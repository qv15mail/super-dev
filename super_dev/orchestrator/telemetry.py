"""
Pipeline 可观测性报告

记录每个阶段耗时、状态与关键指标，并输出 JSON + Markdown。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StageTelemetry:
    stage: str
    title: str
    success: bool
    duration_seconds: float
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "title": self.title,
            "success": self.success,
            "duration_seconds": round(self.duration_seconds, 3),
            "details": self.details,
        }


@dataclass
class PipelineTelemetryReport:
    project_name: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str = ""
    success: bool = True
    failure_reason: str = ""
    stages: list[StageTelemetry] = field(default_factory=list)
    total_duration_seconds: float = 0.0

    def record_stage(
        self,
        stage: str,
        title: str,
        success: bool,
        duration_seconds: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.stages.append(
            StageTelemetry(
                stage=stage,
                title=title,
                success=success,
                duration_seconds=duration_seconds,
                details=details or {},
            )
        )

    def finalize(self, success: bool, total_duration_seconds: float, failure_reason: str = "") -> None:
        self.success = success
        self.total_duration_seconds = max(0.0, total_duration_seconds)
        self.failure_reason = failure_reason
        self.finished_at = datetime.now(timezone.utc).isoformat()

    @property
    def success_rate(self) -> float:
        if not self.stages:
            return 0.0
        passed = sum(1 for stage in self.stages if stage.success)
        return (passed / len(self.stages)) * 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "total_duration_seconds": round(self.total_duration_seconds, 3),
            "success_rate": round(self.success_rate, 2),
            "stages": [stage.to_dict() for stage in self.stages],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Pipeline Metrics",
            "",
            f"- Project: `{self.project_name}`",
            f"- Success: {'yes' if self.success else 'no'}",
            f"- Success rate: {self.success_rate:.1f}%",
            f"- Total duration: {self.total_duration_seconds:.2f}s",
            f"- Started at (UTC): {self.started_at}",
            f"- Finished at (UTC): {self.finished_at or '(running)'}",
        ]
        if self.failure_reason:
            lines.append(f"- Failure reason: {self.failure_reason}")
        lines.extend(["", "## Stages", "", "| Stage | Name | Status | Duration(s) |", "|:---|:---|:---:|---:|"])
        for stage in self.stages:
            status = "PASS" if stage.success else "FAIL"
            lines.append(
                f"| {stage.stage} | {stage.title} | {status} | {stage.duration_seconds:.2f} |"
            )
        lines.append("")
        return "\n".join(lines)

    def write(self, output_dir: Path) -> dict[str, Path]:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / f"{self.project_name}-pipeline-metrics.json"
        md_file = output_dir / f"{self.project_name}-pipeline-metrics.md"
        json_file.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        md_file.write_text(self.to_markdown(), encoding="utf-8")

        history_dir = output_dir / "metrics-history"
        history_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        history_json_file = history_dir / f"{self.project_name}-pipeline-metrics-{stamp}.json"
        history_md_file = history_dir / f"{self.project_name}-pipeline-metrics-{stamp}.md"
        history_json_file.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        history_md_file.write_text(self.to_markdown(), encoding="utf-8")
        return {
            "json": json_file,
            "markdown": md_file,
            "history_json": history_json_file,
            "history_markdown": history_md_file,
        }
