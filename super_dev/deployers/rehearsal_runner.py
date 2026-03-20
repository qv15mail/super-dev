"""
开发：Excellent（11964948@qq.com）
功能：发布演练执行器
作用：验证发布就绪度，执行预发布检查清单
创建时间：2025-12-30
最后修改：2026-03-20
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RehearsalCheck:
    name: str
    passed: bool
    detail: str
    severity: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
            "severity": self.severity,
        }


@dataclass
class RehearsalResult:
    project_name: str
    checks: list[RehearsalCheck] = field(default_factory=list)
    threshold: int = 80
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def failed_checks(self) -> list[RehearsalCheck]:
        return [check for check in self.checks if not check.passed]

    def _weight(self, severity: str) -> int:
        mapping = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return mapping.get(severity, 2)

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        total_weight = sum(self._weight(check.severity) for check in self.checks)
        if total_weight <= 0:
            return 0
        passed_weight = sum(self._weight(check.severity) for check in self.checks if check.passed)
        return int((passed_weight / total_weight) * 100)

    @property
    def passed(self) -> bool:
        has_critical_failure = any((not check.passed and check.severity == "critical") for check in self.checks)
        return self.score >= self.threshold and not has_critical_failure

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "score": self.score,
            "passed": self.passed,
            "threshold": self.threshold,
            "failed_checks": [check.name for check in self.failed_checks],
            "checks": [check.to_dict() for check in self.checks],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Launch Rehearsal Report",
            "",
            f"- Project: `{self.project_name}`",
            f"- Generated at (UTC): {self.generated_at}",
            f"- Score: {self.score}/100",
            f"- Threshold: {self.threshold}",
            f"- Passed: {'yes' if self.passed else 'no'}",
            f"- Failed checks: {len(self.failed_checks)}",
            "",
            "## Checks",
            "",
            "| Check | Result | Severity | Detail |",
            "|:---|:---:|:---:|:---|",
        ]
        for check in self.checks:
            marker = "PASS" if check.passed else "FAIL"
            lines.append(f"| {check.name} | {marker} | {check.severity} | {check.detail} |")
        lines.append("")
        return "\n".join(lines)


class LaunchRehearsalRunner:
    """执行发布演练检查并输出报告"""

    def __init__(self, project_dir: Path, project_name: str, cicd_platform: str):
        self.project_dir = Path(project_dir).resolve()
        self.project_name = project_name
        self.cicd_platform = cicd_platform or "github"

    def run(self) -> RehearsalResult:
        result = RehearsalResult(project_name=self.project_name)
        result.checks.extend(
            [
                self._check_redteam_report(),
                self._check_quality_gate_report(),
                self._check_pipeline_metrics(),
                self._check_delivery_manifest(),
                self._check_rehearsal_documents(),
                self._check_migration_files(),
                self._check_cicd_files(),
            ]
        )
        return result

    def write(self, rehearsal_result: RehearsalResult) -> dict[str, Path]:
        output_dir = self.project_dir / "output" / "rehearsal"
        output_dir.mkdir(parents=True, exist_ok=True)
        md_file = output_dir / f"{self.project_name}-rehearsal-report.md"
        json_file = output_dir / f"{self.project_name}-rehearsal-report.json"
        md_file.write_text(rehearsal_result.to_markdown(), encoding="utf-8")
        json_file.write_text(json.dumps(rehearsal_result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"markdown": md_file, "json": json_file}

    def _check_redteam_report(self) -> RehearsalCheck:
        file_path = self.project_dir / "output" / f"{self.project_name}-redteam.md"
        if not file_path.exists():
            return RehearsalCheck("Redteam Report", False, "missing output/*-redteam.md", severity="critical")

        text = file_path.read_text(encoding="utf-8", errors="ignore")
        if "未通过质量门禁" in text:
            return RehearsalCheck(
                "Redteam Report",
                False,
                "redteam report indicates not passed",
                severity="critical",
            )

        critical_match = re.search(r"Critical 问题\*\*:\s*(\d+)", text)
        if critical_match and int(critical_match.group(1)) > 0:
            return RehearsalCheck(
                "Redteam Report",
                False,
                f"critical_count={critical_match.group(1)}",
                severity="critical",
            )
        return RehearsalCheck("Redteam Report", True, file_path.name)

    def _check_quality_gate_report(self) -> RehearsalCheck:
        file_path = self.project_dir / "output" / f"{self.project_name}-quality-gate.md"
        if not file_path.exists():
            return RehearsalCheck("Quality Gate", False, "missing output/*-quality-gate.md", severity="critical")

        text = file_path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        if "未通过" in text or "failed" in lowered:
            return RehearsalCheck("Quality Gate", False, "quality gate report indicates failed", severity="critical")

        score_match = re.search(r"(总分|Score)\D+(\d{1,3})/100", text, re.IGNORECASE)
        score = int(score_match.group(2)) if score_match else 0

        passed = False
        if "状态" in text and "通过" in text and "未通过" not in text:
            passed = True
        if "Passed" in text and "Failed" not in text:
            passed = True
        if score_match:
            passed = passed and score >= 80

        detail = f"quality score={score}" if score_match else "quality gate report detected"
        return RehearsalCheck("Quality Gate", passed, detail, severity="critical" if not passed else "medium")

    def _check_pipeline_metrics(self) -> RehearsalCheck:
        metrics_file = self.project_dir / "output" / f"{self.project_name}-pipeline-metrics.json"
        if not metrics_file.exists():
            return RehearsalCheck("Pipeline Metrics", False, "missing pipeline metrics json")
        try:
            payload = json.loads(metrics_file.read_text(encoding="utf-8"))
        except Exception:
            return RehearsalCheck("Pipeline Metrics", False, "pipeline metrics parse failed")
        success = bool(payload.get("success"))
        score = payload.get("success_rate", 0)
        return RehearsalCheck(
            "Pipeline Metrics",
            success,
            f"success_rate={score}",
            severity="high" if not success else "low",
        )

    def _check_delivery_manifest(self) -> RehearsalCheck:
        delivery_dir = self.project_dir / "output" / "delivery"
        manifest_candidates = sorted(delivery_dir.glob(f"{self.project_name}-delivery-manifest.json"))
        if not manifest_candidates:
            return RehearsalCheck("Delivery Manifest", False, "missing delivery manifest", severity="critical")
        manifest_file = manifest_candidates[-1]
        try:
            payload = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception:
            return RehearsalCheck("Delivery Manifest", False, "manifest parse failed", severity="high")
        status = str(payload.get("status", "")).lower()
        return RehearsalCheck(
            "Delivery Manifest",
            status == "ready",
            f"status={status or 'unknown'}",
            severity="critical" if status != "ready" else "low",
        )

    def _check_rehearsal_documents(self) -> RehearsalCheck:
        rehearsal_dir = self.project_dir / "output" / "rehearsal"
        required = [
            f"{self.project_name}-launch-rehearsal.md",
            f"{self.project_name}-rollback-playbook.md",
            f"{self.project_name}-smoke-checklist.md",
        ]
        missing = [item for item in required if not (rehearsal_dir / item).exists()]
        if missing:
            return RehearsalCheck(
                "Rehearsal Documents",
                False,
                f"missing: {', '.join(missing)}",
                severity="high",
            )
        return RehearsalCheck("Rehearsal Documents", True, "launch/rollback/smoke docs ready", severity="low")

    def _check_migration_files(self) -> RehearsalCheck:
        backend_migrations = list((self.project_dir / "backend" / "migrations").glob("*.sql"))
        root_migrations = list((self.project_dir / "migrations").glob("*.sql"))
        total = len(backend_migrations) + len(root_migrations)
        return RehearsalCheck(
            "Migration Files",
            total > 0,
            f"{total} migration files",
            severity="high" if total == 0 else "low",
        )

    def _check_cicd_files(self) -> RehearsalCheck:
        cicd_map = {
            "github": [".github/workflows/ci.yml", ".github/workflows/cd.yml"],
            "gitlab": [".gitlab-ci.yml"],
            "jenkins": ["Jenkinsfile"],
            "azure": [".azure-pipelines.yml"],
            "bitbucket": ["bitbucket-pipelines.yml"],
            "all": [
                ".github/workflows/ci.yml",
                ".github/workflows/cd.yml",
                ".gitlab-ci.yml",
                "Jenkinsfile",
                ".azure-pipelines.yml",
                "bitbucket-pipelines.yml",
            ],
        }
        expected = cicd_map.get(self.cicd_platform, cicd_map["github"])
        missing = [item for item in expected if not (self.project_dir / item).exists()]
        if missing:
            return RehearsalCheck(
                "CI/CD Files",
                False,
                f"missing: {', '.join(missing)}",
                severity="high",
            )
        return RehearsalCheck("CI/CD Files", True, f"{len(expected)} files found")
