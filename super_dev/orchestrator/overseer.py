"""
Super Dev Overseer Agent

功能：独立质量监督者 — 对流水线各阶段和步骤进行检查点审查，追踪偏差，生成报告。
创建时间：2026-04-10
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    """返回 UTC ISO 8601 时间戳。"""
    return datetime.now(timezone.utc).isoformat()


def _escape_markdown_cell(value: str) -> str:
    """转义 Markdown 表格单元格中的特殊字符。"""
    return value.replace("|", "\\|").replace("\n", "<br/>")


class DeviationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CheckpointVerdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    HOLD = "HOLD"
    FAIL = "FAIL"


@dataclass
class Deviation:
    id: int
    severity: DeviationSeverity
    category: str
    description: str
    expected: str
    actual: str
    recommendation: str
    phase: str
    step_id: str
    resolved: bool = False
    resolution: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "category": self.category,
            "description": self.description,
            "expected": self.expected,
            "actual": self.actual,
            "recommendation": self.recommendation,
            "phase": self.phase,
            "step_id": self.step_id,
            "resolved": self.resolved,
            "resolution": self.resolution,
        }


@dataclass
class CheckpointReport:
    checkpoint_id: str
    phase: str
    step_id: str
    verdict: CheckpointVerdict
    timestamp: str
    deviations: list[Deviation] = field(default_factory=list)
    quality_score: float = 0.0
    codex_review_processed: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "phase": self.phase,
            "step_id": self.step_id,
            "verdict": self.verdict.value,
            "timestamp": self.timestamp,
            "deviations": [deviation.to_dict() for deviation in self.deviations],
            "quality_score": self.quality_score,
            "codex_review_processed": self.codex_review_processed,
            "notes": self.notes,
        }


@dataclass
class OverseerReport:
    project_name: str
    report_id: str
    created_at: str
    checkpoints: list[CheckpointReport] = field(default_factory=list)
    total_deviations: int = 0
    critical_count: int = 0
    high_count: int = 0
    warning_count: int = 0
    overall_verdict: CheckpointVerdict = CheckpointVerdict.PASS
    pipeline_halted: bool = False
    halt_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "report_id": self.report_id,
            "created_at": self.created_at,
            "checkpoints": [checkpoint.to_dict() for checkpoint in self.checkpoints],
            "total_deviations": self.total_deviations,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "warning_count": self.warning_count,
            "overall_verdict": self.overall_verdict.value,
            "pipeline_halted": self.pipeline_halted,
            "halt_reason": self.halt_reason,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Super Dev Overseer Report",
            "",
            f"- 项目名: `{self.project_name}`",
            f"- 报告 ID: `{self.report_id}`",
            f"- 创建时间: {self.created_at}",
            "",
            "## 总览",
            "",
            "| 指标 | 值 |",
            "|---|---|",
            f"| 总偏差数 | {self.total_deviations} |",
            f"| Critical 数 | {self.critical_count} |",
            f"| High 数 | {self.high_count} |",
            f"| Warning 数 | {self.warning_count} |",
            f"| Overall Verdict | {self.overall_verdict.value} |",
            f"| Pipeline Halted | {'Yes' if self.pipeline_halted else 'No'} |",
        ]

        if self.halt_reason:
            lines.append(f"| Halt Reason | {_escape_markdown_cell(self.halt_reason)} |")

        for checkpoint in self.checkpoints:
            lines.extend(
                [
                    "",
                    f"## Checkpoint `{checkpoint.checkpoint_id}`",
                    "",
                    f"- Phase: `{checkpoint.phase}`",
                    f"- Step ID: `{checkpoint.step_id or '-'}`",
                    f"- Verdict: `{checkpoint.verdict.value}`",
                    f"- Quality Score: `{checkpoint.quality_score:.2f}`",
                    f"- Timestamp: {checkpoint.timestamp}",
                    f"- Codex Review Processed: {'Yes' if checkpoint.codex_review_processed else 'No'}",
                ]
            )

            if checkpoint.notes:
                lines.append(f"- Notes: {checkpoint.notes}")

            lines.extend(
                [
                    "",
                    "| ID | Severity | Category | Description | Resolved |",
                    "|---|---|---|---|---|",
                ]
            )

            if checkpoint.deviations:
                for deviation in checkpoint.deviations:
                    lines.append(
                        "| "
                        f"{deviation.id} | "
                        f"{deviation.severity.value} | "
                        f"{_escape_markdown_cell(deviation.category)} | "
                        f"{_escape_markdown_cell(deviation.description)} | "
                        f"{'Yes' if deviation.resolved else 'No'} |"
                    )
            else:
                lines.append("| - | - | - | No deviations | - |")

        lines.extend(
            [
                "",
                "---",
                "Generated by Super Dev Overseer.",
            ]
        )
        return "\n".join(lines)


class Overseer:
    """独立质量监督者，负责阶段与步骤级检查点审查。"""

    def __init__(
        self,
        project_dir: str | Path,
        project_name: str,
        quality_threshold: float = 80.0,
        halt_on_critical: bool = True,
    ) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.project_name = project_name
        self.quality_threshold = quality_threshold
        self.halt_on_critical = halt_on_critical
        self.overseer_dir = self.project_dir / ".super-dev" / "overseer"
        self.overseer_dir.mkdir(parents=True, exist_ok=True)
        self._deviation_counter = 0
        self._report = OverseerReport(
            project_name=project_name,
            report_id=uuid4().hex,
            created_at=_now_iso(),
        )

    def checkpoint_phase(
        self,
        phase: str,
        plan_data: dict[str, Any] | None = None,
        actual_output: dict[str, Any] | None = None,
        quality_score: float = 0.0,
        codex_reviews: list[dict[str, Any]] | None = None,
    ) -> CheckpointReport:
        report = CheckpointReport(
            checkpoint_id=f"phase-{phase}",
            phase=phase,
            step_id="",
            verdict=CheckpointVerdict.PASS,
            timestamp=_now_iso(),
            quality_score=quality_score,
        )

        if quality_score < self.quality_threshold:
            gap = self.quality_threshold - quality_score
            severity = (
                DeviationSeverity.HIGH if gap >= 20 else DeviationSeverity.WARNING
            )
            report.deviations.append(
                self._create_deviation(
                    severity=severity,
                    category="quality-drop",
                    description=f"Quality score fell below threshold in phase {phase}.",
                    expected=f"Quality score >= {self.quality_threshold:.2f}",
                    actual=f"Quality score = {quality_score:.2f}",
                    recommendation="Improve output quality and rerun the checkpoint.",
                    phase=phase,
                    step_id="",
                )
            )

        if plan_data and actual_output:
            self._check_plan_alignment(report, phase, plan_data, actual_output)

        for review in (codex_reviews or []):
            severity_label = str(review.get("severity", "")).strip().lower()
            issue = str(review.get("issue", "")).strip() or "Unspecified Codex review issue."
            if severity_label == "critical":
                severity = DeviationSeverity.CRITICAL
            elif severity_label == "high":
                severity = DeviationSeverity.HIGH
            else:
                continue
            report.deviations.append(
                self._create_deviation(
                    severity=severity,
                    category="codex-unresolved",
                    description=issue,
                    expected="No unresolved high-severity Codex review issues.",
                    actual=issue,
                    recommendation="Resolve the review issue before advancing the pipeline.",
                    phase=phase,
                    step_id="",
                )
            )

        report.codex_review_processed = True
        self._determine_verdict(report)
        if report.verdict == CheckpointVerdict.FAIL and self.halt_on_critical:
            self._report.pipeline_halted = True
            self._report.halt_reason = f"Critical deviation in phase {phase}"

            # Webhook notification on overseer halt
            try:
                from ..webhooks import send_webhook

                send_webhook(
                    "overseer_halt",
                    {
                        "phase": phase,
                        "halt_reason": self._report.halt_reason,
                        "verdict": report.verdict.value,
                        "quality_score": report.quality_score,
                        "deviations": [
                            d.to_dict() for d in report.deviations
                        ],
                        "project": self.project_name,
                    },
                )
            except Exception:
                pass

        self._report.checkpoints.append(report)
        self._update_report_summary()
        self._save_report()
        return report

    def checkpoint_step(
        self,
        phase: str,
        step_id: str,
        step_label: str,
        expected_output: dict[str, Any] | None = None,
        actual_output: dict[str, Any] | None = None,
        verify_results: list[dict[str, Any]] | None = None,
        codex_review: dict[str, Any] | None = None,
    ) -> CheckpointReport:
        report = CheckpointReport(
            checkpoint_id=f"step-{phase}-{step_id}",
            phase=phase,
            step_id=step_id,
            verdict=CheckpointVerdict.PASS,
            timestamp=_now_iso(),
        )

        for result in (verify_results or []):
            if result.get("required") and not result.get("passed"):
                gate_name = str(result.get("gate", "unknown"))
                report.deviations.append(
                    self._create_deviation(
                        severity=DeviationSeverity.HIGH,
                        category="behavior-anomaly",
                        description=f"Required verification gate failed: {gate_name}",
                        expected=f"Required gate {gate_name} should pass.",
                        actual=f"Gate {gate_name} did not pass.",
                        recommendation="Fix the failing gate condition and rerun verification.",
                        phase=phase,
                        step_id=step_id,
                    )
                )

        if actual_output is None or actual_output == {}:
            report.deviations.append(
                self._create_deviation(
                    severity=DeviationSeverity.WARNING,
                    category="data-gap",
                    description=f"Step output is missing for {step_label}.",
                    expected=step_label,
                    actual="No step output was produced.",
                    recommendation="Generate the expected step output before proceeding.",
                    phase=phase,
                    step_id=step_id,
                )
            )

        if codex_review is not None:
            severity_label = str(codex_review.get("severity", "")).strip().lower()
            issue = (
                str(codex_review.get("issue", "")).strip()
                or "Unspecified Codex review issue."
            )
            if severity_label == "critical":
                severity = DeviationSeverity.CRITICAL
            elif severity_label == "high":
                severity = DeviationSeverity.HIGH
            else:
                severity = None

            if severity is not None:
                report.deviations.append(
                    self._create_deviation(
                        severity=severity,
                        category="codex-unresolved",
                        description=issue,
                        expected="No unresolved high-severity Codex review issues.",
                        actual=issue,
                        recommendation="Resolve the review issue before advancing the step.",
                        phase=phase,
                        step_id=step_id,
                    )
                )

        report.codex_review_processed = codex_review is not None
        self._determine_verdict(report)
        self._report.checkpoints.append(report)
        self._update_report_summary()
        self._save_report()
        return report

    def should_halt(self) -> bool:
        return self._report.pipeline_halted

    def get_report(self) -> OverseerReport:
        return self._report

    def finalize(self) -> OverseerReport:
        self._update_report_summary()
        self._save_report()
        markdown_path = self.overseer_dir / "report.md"
        markdown_path.write_text(self._report.to_markdown(), encoding="utf-8")
        return self._report

    def mark_deviation_resolved(self, deviation_id: int, resolution: str) -> bool:
        for checkpoint in self._report.checkpoints:
            for deviation in checkpoint.deviations:
                if deviation.id == deviation_id:
                    deviation.resolved = True
                    deviation.resolution = resolution
                    self._save_report()
                    return True
        return False

    def _create_deviation(self, **kwargs: Any) -> Deviation:
        self._deviation_counter += 1
        return Deviation(id=self._deviation_counter, **kwargs)

    def _check_plan_alignment(
        self,
        report: CheckpointReport,
        phase: str,
        plan_data: dict[str, Any],
        actual_output: dict[str, Any] | None,
    ) -> None:
        for file_path in plan_data.get("expected_outputs", []):
            expected_path = Path(file_path)
            if not expected_path.exists():
                report.deviations.append(
                    self._create_deviation(
                        severity=DeviationSeverity.WARNING,
                        category="spec-drift",
                        description=f"Planned output file is missing: {file_path}",
                        expected=file_path,
                        actual="File not found.",
                        recommendation="Create the planned output artifact to realign with the plan.",
                        phase=phase,
                        step_id="",
                    )
                )

        actual_data = actual_output if isinstance(actual_output, dict) else {}
        for required_key in plan_data.get("required_keys", []):
            if required_key not in actual_data:
                report.deviations.append(
                    self._create_deviation(
                        severity=DeviationSeverity.HIGH,
                        category="spec-drift",
                        description=f"Required output key is missing: {required_key}",
                        expected=f"Output contains key `{required_key}`",
                        actual="Key not present in actual output.",
                        recommendation="Populate the missing key in the actual output payload.",
                        phase=phase,
                        step_id="",
                    )
                )

    def _determine_verdict(self, report: CheckpointReport) -> CheckpointVerdict:
        severities = {deviation.severity for deviation in report.deviations}
        if DeviationSeverity.CRITICAL in severities:
            report.verdict = CheckpointVerdict.FAIL
        elif DeviationSeverity.HIGH in severities:
            report.verdict = CheckpointVerdict.HOLD
        elif DeviationSeverity.WARNING in severities:
            report.verdict = CheckpointVerdict.WARN
        else:
            report.verdict = CheckpointVerdict.PASS
        return report.verdict

    def _update_report_summary(self) -> None:
        deviations = [
            deviation
            for checkpoint in self._report.checkpoints
            for deviation in checkpoint.deviations
        ]
        self._report.total_deviations = len(deviations)
        self._report.critical_count = sum(
            1 for deviation in deviations if deviation.severity == DeviationSeverity.CRITICAL
        )
        self._report.high_count = sum(
            1 for deviation in deviations if deviation.severity == DeviationSeverity.HIGH
        )
        self._report.warning_count = sum(
            1 for deviation in deviations if deviation.severity == DeviationSeverity.WARNING
        )

        verdicts = {checkpoint.verdict for checkpoint in self._report.checkpoints}
        if CheckpointVerdict.FAIL in verdicts:
            self._report.overall_verdict = CheckpointVerdict.FAIL
        elif CheckpointVerdict.HOLD in verdicts:
            self._report.overall_verdict = CheckpointVerdict.HOLD
        elif CheckpointVerdict.WARN in verdicts:
            self._report.overall_verdict = CheckpointVerdict.WARN
        else:
            self._report.overall_verdict = CheckpointVerdict.PASS

        if self._report.pipeline_halted and self._report.overall_verdict != CheckpointVerdict.FAIL:
            self._report.overall_verdict = CheckpointVerdict.FAIL

    def _save_report(self) -> None:
        report_path = self.overseer_dir / "report.json"
        report_path.write_text(
            json.dumps(self._report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
