from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .release_readiness import ReleaseReadinessEvaluator
from .review_state import load_docs_confirmation, load_ui_revision


@dataclass
class ProofPackArtifact:
    name: str
    status: str
    summary: str
    path: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "summary": self.summary,
            "path": self.path,
            "details": self.details,
        }


@dataclass
class ProofPackReport:
    project_name: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    artifacts: list[ProofPackArtifact] = field(default_factory=list)

    @property
    def ready_count(self) -> int:
        return sum(1 for artifact in self.artifacts if artifact.status == "ready")

    @property
    def total_count(self) -> int:
        return len(self.artifacts)

    @property
    def status(self) -> str:
        return "ready" if self.ready_count == self.total_count and self.total_count > 0 else "incomplete"

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "status": self.status,
            "ready_count": self.ready_count,
            "total_count": self.total_count,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Proof Pack",
            "",
            f"- Project: `{self.project_name}`",
            f"- Generated at (UTC): {self.generated_at}",
            f"- Status: `{self.status}`",
            f"- Ready artifacts: {self.ready_count}/{self.total_count}",
            "",
            "| Artifact | Status | Summary | Path |",
            "|:---|:---:|:---|:---|",
        ]
        for artifact in self.artifacts:
            lines.append(
                f"| {artifact.name} | {artifact.status} | {artifact.summary} | {artifact.path or '-'} |"
            )
        lines.append("")
        return "\n".join(lines)


class ProofPackBuilder:
    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        self.output_dir = self.project_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.project_name = self.project_dir.name

    def build(self, verify_tests: bool = False) -> ProofPackReport:
        report = ProofPackReport(project_name=self.project_name)
        report.artifacts.extend(
            [
                self._docs_confirmation_artifact(),
                self._ui_revision_artifact(),
                self._document_artifact("Research", "*-research.md"),
                self._document_artifact("PRD", "*-prd.md"),
                self._document_artifact("Architecture", "*-architecture.md"),
                self._document_artifact("UI/UX", "*-uiux.md"),
                self._frontend_runtime_artifact(),
                self._ui_review_artifact(),
                self._quality_gate_artifact(),
                self._delivery_manifest_artifact(),
                self._rehearsal_artifact(),
                self._release_readiness_artifact(verify_tests=verify_tests),
            ]
        )
        return report

    def write(self, report: ProofPackReport) -> dict[str, Path]:
        base = self.output_dir / f"{self.project_name}-proof-pack"
        md_path = base.with_suffix(".md")
        json_path = base.with_suffix(".json")
        md_path.write_text(report.to_markdown(), encoding="utf-8")
        json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"markdown": md_path, "json": json_path}

    def _latest(self, pattern: str, base_dir: Path | None = None) -> Path | None:
        directory = base_dir or self.output_dir
        candidates = [path for path in directory.glob(pattern) if path.is_file()]
        if not candidates:
            return None
        return max(candidates, key=lambda item: item.stat().st_mtime)

    def _document_artifact(self, name: str, pattern: str) -> ProofPackArtifact:
        file_path = self._latest(pattern)
        if file_path is None:
            return ProofPackArtifact(name=name, status="missing", summary=f"missing {pattern}")
        return ProofPackArtifact(
            name=name,
            status="ready",
            summary="document generated",
            path=str(file_path),
        )

    def _docs_confirmation_artifact(self) -> ProofPackArtifact:
        payload = load_docs_confirmation(self.project_dir)
        file_path = self.project_dir / ".super-dev" / "review-state" / "document-confirmation.json"
        if not payload:
            return ProofPackArtifact(
                name="Docs Confirmation",
                status="missing",
                summary="document confirmation state not recorded",
                path=str(file_path) if file_path.exists() else "",
            )
        status = str(payload.get("status", "pending_review"))
        ready = status == "confirmed"
        summary = "core documents confirmed" if ready else f"status={status}"
        return ProofPackArtifact(
            name="Docs Confirmation",
            status="ready" if ready else "pending",
            summary=summary,
            path=str(file_path),
            details=payload,
        )

    def _ui_revision_artifact(self) -> ProofPackArtifact:
        payload = load_ui_revision(self.project_dir)
        file_path = self.project_dir / ".super-dev" / "review-state" / "ui-revision.json"
        if not payload:
            return ProofPackArtifact(
                name="UI Revision State",
                status="ready",
                summary="no open UI revision",
                path=str(file_path) if file_path.exists() else "",
            )
        status = str(payload.get("status", "pending_review"))
        if status == "confirmed":
            artifact_status = "ready"
            summary = "UI revision confirmed"
        elif status == "revision_requested":
            artifact_status = "pending"
            summary = "UI revision still open"
        else:
            artifact_status = "pending"
            summary = f"status={status}"
        return ProofPackArtifact(
            name="UI Revision State",
            status=artifact_status,
            summary=summary,
            path=str(file_path),
            details=payload,
        )

    def _frontend_runtime_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-frontend-runtime.json")
        if file_path is None:
            return ProofPackArtifact(name="Frontend Runtime", status="missing", summary="frontend runtime report missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        passed = bool(payload.get("passed", False)) if isinstance(payload, dict) else False
        return ProofPackArtifact(
            name="Frontend Runtime",
            status="ready" if passed else "pending",
            summary="frontend runtime passed" if passed else "frontend runtime not passed",
            path=str(file_path),
            details=payload if isinstance(payload, dict) else {},
        )

    def _ui_review_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-ui-review.json")
        if file_path is None:
            return ProofPackArtifact(name="UI Review", status="missing", summary="UI review report missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        score = payload.get("score") if isinstance(payload, dict) else None
        critical = int(payload.get("critical_count", 0)) if isinstance(payload, dict) else 0
        ready = critical == 0
        summary = f"score={score}, critical={critical}" if score is not None else f"critical={critical}"
        return ProofPackArtifact(
            name="UI Review",
            status="ready" if ready else "pending",
            summary=summary,
            path=str(file_path),
            details=payload if isinstance(payload, dict) else {},
        )

    def _quality_gate_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-quality-gate.md")
        if file_path is None:
            return ProofPackArtifact(name="Quality Gate", status="missing", summary="quality gate report missing")
        text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
        if "fail" in text or "未通过" in text:
            status = "pending"
            summary = "quality gate indicates unresolved issues"
        else:
            status = "ready"
            summary = "quality gate report generated"
        return ProofPackArtifact(name="Quality Gate", status=status, summary=summary, path=str(file_path))

    def _delivery_manifest_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-delivery-manifest.json", self.output_dir / "delivery")
        if file_path is None:
            return ProofPackArtifact(name="Delivery Manifest", status="missing", summary="delivery manifest missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        ready = isinstance(payload, dict) and payload.get("status") == "ready"
        summary = f"status={payload.get('status', 'unknown')}" if isinstance(payload, dict) else "manifest unreadable"
        return ProofPackArtifact(
            name="Delivery Manifest",
            status="ready" if ready else "pending",
            summary=summary,
            path=str(file_path),
            details=payload if isinstance(payload, dict) else {},
        )

    def _rehearsal_artifact(self) -> ProofPackArtifact:
        rehearsal_dir = self.output_dir / "rehearsal"
        file_path = self._latest("*-rehearsal-report.json", rehearsal_dir)
        if file_path is None:
            return ProofPackArtifact(name="Release Rehearsal", status="missing", summary="rehearsal report missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        passed = bool(payload.get("passed", False)) if isinstance(payload, dict) else False
        summary = f"score={payload.get('score', 'unknown')}, passed={passed}" if isinstance(payload, dict) else "report unreadable"
        return ProofPackArtifact(
            name="Release Rehearsal",
            status="ready" if passed else "pending",
            summary=summary,
            path=str(file_path),
            details=payload if isinstance(payload, dict) else {},
        )

    def _release_readiness_artifact(self, verify_tests: bool) -> ProofPackArtifact:
        evaluator = ReleaseReadinessEvaluator(self.project_dir)
        report = evaluator.evaluate(verify_tests=verify_tests)
        files = evaluator.write(report)
        return ProofPackArtifact(
            name="Release Readiness",
            status="ready" if report.passed else "pending",
            summary=f"score={report.score}/100, passed={report.passed}",
            path=str(files["json"]),
            details=report.to_dict(),
        )
