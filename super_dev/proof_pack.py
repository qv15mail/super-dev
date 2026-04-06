"""
开发：Excellent（11964948@qq.com）
功能：交付证据包构建器
作用：汇总项目交付证据，生成完成度报告和阻塞项分析
创建时间：2025-12-30
最后修改：2026-03-20
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .analyzer import FeatureChecklistBuilder
from .framework_harness import FrameworkHarnessBuilder
from .frameworks import framework_playbook_complete, is_cross_platform_frontend
from .harness_registry import derive_operational_focus
from .hook_harness import HookHarnessBuilder
from .operational_harness import OperationalHarnessBuilder
from .release_readiness import ReleaseReadinessEvaluator
from .review_state import (
    load_architecture_revision,
    load_docs_confirmation,
    load_quality_revision,
    load_ui_revision,
)
from .reviewers.redteam import load_redteam_evidence
from .specs import SpecValidator
from .workflow_harness import WorkflowHarnessBuilder

_logger = logging.getLogger("super_dev.proof_pack")


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

    @property
    def completion_percent(self) -> int:
        if self.total_count <= 0:
            return 0
        return int(round((self.ready_count / self.total_count) * 100))

    @property
    def blockers(self) -> list[ProofPackArtifact]:
        return [artifact for artifact in self.artifacts if artifact.status != "ready"]

    @property
    def key_artifacts(self) -> list[ProofPackArtifact]:
        preferred = {
            "Docs Confirmation",
            "Spec Quality",
            "Scope Coverage",
            "Product Audit",
            "Redteam",
            "Task Execution",
            "UI Contract",
            "UI Contract Alignment",
            "Operational Harness",
            "Framework Harness",
            "Hook Audit Trail",
            "Workflow Continuity",
            "Frontend Runtime",
            "UI Review",
            "Delivery Manifest",
            "Release Readiness",
        }
        prioritized = [artifact for artifact in self.artifacts if artifact.name in preferred]
        return prioritized or self.artifacts[:5]

    @property
    def next_actions(self) -> list[str]:
        actions: list[str] = []
        artifact_names = {artifact.name: artifact for artifact in self.artifacts}
        docs = artifact_names.get("Docs Confirmation")
        if docs and docs.status != "ready":
            actions.append('先执行 `super-dev review docs --status confirmed --comment "三文档已确认"`。')
        spec_quality = artifact_names.get("Spec Quality")
        if spec_quality and spec_quality.status != "ready":
            change_id = str(spec_quality.details.get("change_id", "<change_id>"))
            actions.append(f"先执行 `super-dev spec quality {change_id}` 并补齐 proposal/spec/tasks/validation 的缺口。")
        scope_coverage = artifact_names.get("Scope Coverage")
        if scope_coverage and scope_coverage.status != "ready":
            actions.append("先执行 `super-dev feature-checklist`，补齐高优先级未实现项，或把未落地能力明确降级到后续版本。")
        product_audit = artifact_names.get("Product Audit")
        if product_audit and product_audit.status != "ready":
            actions.append("先执行 `super-dev product-audit`，把产品闭环、首次上手和缺失功能的审查结果纳入交付证据。")
        architecture_revision = artifact_names.get("Architecture Revision State")
        if architecture_revision and architecture_revision.status != "ready":
            actions.append("先完成架构改版闭环：更新 architecture 文档、同步任务与实现，再重新审查。")
        ui_revision = artifact_names.get("UI Revision State")
        if ui_revision and ui_revision.status != "ready":
            actions.append("先完成 UI 改版闭环：更新 UIUX 文档、重做前端、重新执行 frontend runtime 与 UI review。")
        ui_contract = artifact_names.get("UI Contract")
        if ui_contract and ui_contract.status != "ready":
            required_sections = (
                ui_contract.details.get("required_sections", {})
                if isinstance(ui_contract.details, dict)
                else {}
            )
            if isinstance(required_sections, dict) and required_sections.get("framework_playbook") is False:
                actions.append(
                    "先补齐并冻结 output/*-ui-contract.json 中的跨平台框架 playbook，确认 implementation modules、native capabilities、validation surfaces 与 delivery evidence 已写成正式契约。"
                )
            else:
                actions.append("先补齐并冻结 output/*-ui-contract.json，确认 UI 库选择、字体、图标系统和 design tokens 已写成正式契约。")
        ui_contract_alignment = artifact_names.get("UI Contract Alignment")
        if ui_contract_alignment and ui_contract_alignment.status != "ready":
            actions.append("重新执行 `super-dev review ui` 或 quality gate，补齐 output/*-ui-contract-alignment.json，确认源码已接入冻结后的图标、字体、组件生态和 design tokens。")
        framework_harness = artifact_names.get("Framework Harness")
        if framework_harness and framework_harness.status != "ready":
            actions.append("补齐跨平台 framework harness：确认 framework playbook 已冻结，frontend runtime 已证明专项执行完成，并重新生成 framework harness 证据。")
        operational_harness = artifact_names.get("Operational Harness")
        if operational_harness and operational_harness.status != "ready":
            focus = (
                operational_harness.details.get("operational_focus")
                if isinstance(operational_harness.details, dict)
                else {}
            )
            if not isinstance(focus, dict):
                focus = (
                    operational_harness.details.get("focus", {})
                    if isinstance(operational_harness.details, dict)
                    else {}
                )
            focus_action = str(focus.get("recommended_action", "")).strip()
            if focus_action:
                actions.append(focus_action)
            else:
                actions.append("补齐 operational harness：确认 workflow / framework / hook 三类 harness 都已生成并通过，再重新生成 proof-pack。")
        hook_audit = artifact_names.get("Hook Audit Trail")
        if hook_audit and hook_audit.status != "ready":
            actions.append("检查最近 hook 审计历史，修复失败/阻断的 hook 命令后重新执行相关阶段并重新生成 proof-pack。")
        workflow_continuity = artifact_names.get("Workflow Continuity")
        if workflow_continuity and workflow_continuity.status != "ready":
            actions.append("补齐 workflow continuity：确认 .super-dev/workflow-state.json、workflow-history 快照和 workflow-events.jsonl 都已落盘，再重新生成 proof-pack。")
        quality_revision = artifact_names.get("Quality Revision State")
        if quality_revision and quality_revision.status != "ready":
            actions.append("先修复质量返工项并确认 quality review 状态，再重新生成交付证据。")
        redteam = artifact_names.get("Redteam")
        if redteam and redteam.status != "ready":
            actions.append("先补齐红队审查并消除阻断项，再进入质量门禁和发布核验。")
        task_execution = artifact_names.get("Task Execution")
        if task_execution and task_execution.status != "ready":
            actions.append("先补齐 Spec 任务执行报告与交付前自检摘要，确认实现链路已经真实闭环。")
        frontend = artifact_names.get("Frontend Runtime")
        if frontend and frontend.status != "ready":
            actions.append("重新执行前端运行验证，确认前端可真实运行而不是只生成页面文件。")
        quality = artifact_names.get("Quality Gate")
        if quality and quality.status != "ready":
            actions.append("先修复质量或安全问题，再重新执行 quality gate。")
        delivery = artifact_names.get("Delivery Manifest")
        if delivery and delivery.status != "ready":
            actions.append("补齐交付包并确认 delivery manifest 状态为 ready。")
        rehearsal = artifact_names.get("Release Rehearsal")
        if rehearsal and rehearsal.status != "ready":
            actions.append("重新执行发布演练，确认 rehearsal passed。")
        readiness = artifact_names.get("Release Readiness")
        if readiness and readiness.status != "ready":
            actions.append("重新执行 `super-dev release readiness --verify-tests`，确认当前仓库达到发布阈值。")
        if not actions:
            actions.append("当前关键交付证据已经齐全，可以直接对外交付或发布。")
        return actions

    @property
    def governance_artifacts(self) -> list[ProofPackArtifact]:
        governance_names = {
            "Knowledge Reference Report",
            "Pipeline Metrics",
            "Governance Report",
            "Architecture Decisions",
            "Validation Rules Report",
        }
        return [a for a in self.artifacts if a.name in governance_names]

    @property
    def operational_harnesses(self) -> list[ProofPackArtifact]:
        harness_names = {
            "Operational Harness",
            "Framework Harness",
            "Hook Audit Trail",
            "Workflow Continuity",
        }
        return [artifact for artifact in self.artifacts if artifact.name in harness_names]

    @property
    def executive_summary(self) -> str:
        gov = self.governance_artifacts
        gov_text = ""
        if gov:
            gov_text = f"治理证据 {len(gov)} 项已纳入（" + "、".join(a.name for a in gov) + "）。"
        harnesses = self.operational_harnesses
        harness_text = ""
        if harnesses:
            harness_text = (
                f"运行时/恢复类 harness {len(harnesses)} 项已纳入（"
                + "、".join(a.name for a in harnesses)
                + "）。"
            )
        operational_focus_text = ""
        operational_harness = next((a for a in harnesses if a.name == "Operational Harness"), None)
        if operational_harness and isinstance(operational_harness.details, dict):
            focus = operational_harness.details.get("operational_focus")
            if not isinstance(focus, dict):
                focus = operational_harness.details.get("focus", {})
            if isinstance(focus, dict):
                focus_summary = str(focus.get("summary", "")).strip()
                if focus_summary:
                    operational_focus_text = f"当前治理焦点：{focus_summary}。"
        if self.status == "ready":
            return (
                f"当前交付证据包已完成，{self.ready_count}/{self.total_count} 项关键证据就绪，"
                f"可以作为当前 run 的正式交付证明。{gov_text}{harness_text}{operational_focus_text}"
            )
        missing = [artifact.name for artifact in self.blockers[:3]]
        missing_text = "、".join(missing) if missing else "关键交付证据"
        return (
            f"当前交付证据包尚未完成，已就绪 {self.ready_count}/{self.total_count} 项。"
            f"优先补齐：{missing_text}。{gov_text}{harness_text}{operational_focus_text}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "status": self.status,
            "ready_count": self.ready_count,
            "total_count": self.total_count,
            "completion_percent": self.completion_percent,
            "summary": {
                "executive_summary": self.executive_summary,
                "blocking_count": len(self.blockers),
                "key_artifact_count": len(self.key_artifacts),
                "next_actions": list(self.next_actions),
            },
            "blocking_artifacts": [artifact.to_dict() for artifact in self.blockers],
            "key_artifacts": [artifact.to_dict() for artifact in self.key_artifacts],
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
            f"- Completion: {self.completion_percent}%",
            "",
            "## Executive Summary",
            "",
            self.executive_summary,
            "",
            "## Blockers",
            "",
        ]
        if self.blockers:
            for artifact in self.blockers:
                lines.append(f"- **{artifact.name}**: {artifact.summary}")
        else:
            lines.append("- 当前没有阻塞项。")
        lines.extend(
            [
                "",
                "## Next Actions",
                "",
            ]
        )
        for action in self.next_actions:
            lines.append(f"- {action}")
        lines.extend(
            [
                "",
                "## Key Artifacts",
                "",
            ]
        )
        for artifact in self.key_artifacts:
            lines.append(f"- **{artifact.name}**: {artifact.summary} ({artifact.status})")
        harnesses = self.operational_harnesses
        if harnesses:
            lines.extend(
                [
                    "",
                    "## Operational Harnesses",
                    "",
                ]
            )
            for artifact in harnesses:
                lines.append(f"- **{artifact.name}**: {artifact.summary} ({artifact.status})")
            operational_harness = next((a for a in harnesses if a.name == "Operational Harness"), None)
            if operational_harness and isinstance(operational_harness.details, dict):
                focus = operational_harness.details.get("operational_focus")
                if not isinstance(focus, dict):
                    focus = operational_harness.details.get("focus", {})
                if isinstance(focus, dict):
                    focus_summary = str(focus.get("summary", "")).strip()
                    focus_action = str(focus.get("recommended_action", "")).strip()
                    if focus_summary:
                        lines.append(f"- 当前治理焦点: {focus_summary}")
                    if focus_action:
                        lines.append(f"- 建议先做: {focus_action}")
        gov = self.governance_artifacts
        if gov:
            lines.extend(
                [
                    "",
                    "## Governance Evidence",
                    "",
                ]
            )
            for artifact in gov:
                lines.append(f"- **{artifact.name}**: {artifact.summary} ({artifact.status})")
        lines.extend(
            [
                "",
                "## Full Artifact Matrix",
                "",
                "| Artifact | Status | Summary | Path |",
                "|:---|:---:|:---|:---|",
            ]
        )
        for artifact in self.artifacts:
            lines.append(
                f"| {artifact.name} | {artifact.status} | {artifact.summary} | {artifact.path or '-'} |"
            )
        lines.append("")
        return "\n".join(lines)

    def to_executive_markdown(self) -> str:
        artifact_names = {artifact.name: artifact for artifact in self.artifacts}
        lines = [
            "# Delivery Evidence Pack Summary",
            "",
            f"- Project: `{self.project_name}`",
            f"- Generated at (UTC): {self.generated_at}",
            f"- Status: `{self.status}`",
            f"- Completion: {self.completion_percent}%",
            "",
            self.executive_summary,
            "",
            "## Current Blockers",
            "",
        ]
        if self.blockers:
            for artifact in self.blockers:
                lines.append(f"- **{artifact.name}**: {artifact.summary}")
        else:
            lines.append("- None")
        lines.extend(["", "## Recommended Next Actions", ""])
        for action in self.next_actions:
            lines.append(f"- {action}")
        operational_artifacts = [
            artifact_names.get("Operational Harness"),
            artifact_names.get("Workflow Continuity"),
            artifact_names.get("Framework Harness"),
            artifact_names.get("Hook Audit Trail"),
        ]
        visible_operational = [item for item in operational_artifacts if item is not None]
        if visible_operational:
            lines.extend(["", "## Operational Continuity", ""])
            for artifact in visible_operational:
                lines.append(
                    f"- **{artifact.name}**: {artifact.summary} ({artifact.status})"
                )
            operational_harness = artifact_names.get("Operational Harness")
            if operational_harness is not None and isinstance(operational_harness.details, dict):
                focus = operational_harness.details.get("operational_focus")
                if not isinstance(focus, dict):
                    focus = operational_harness.details.get("focus", {})
                if isinstance(focus, dict):
                    focus_summary = str(focus.get("summary", "")).strip()
                    focus_action = str(focus.get("recommended_action", "")).strip()
                    if focus_summary:
                        lines.append(f"- Current operational focus: {focus_summary}")
                    if focus_action:
                        lines.append(f"- Do first: {focus_action}")
            workflow_artifact = artifact_names.get("Workflow Continuity")
            if workflow_artifact is not None:
                details = workflow_artifact.details if isinstance(workflow_artifact.details, dict) else {}
                recent_timeline = details.get("recent_timeline")
                if isinstance(recent_timeline, list) and recent_timeline:
                    lines.extend(["", "## Recent Operational Timeline", ""])
                    for item in recent_timeline[:5]:
                        if not isinstance(item, dict):
                            continue
                        timestamp = str(item.get("timestamp", "")).strip() or "-"
                        title = str(item.get("title", "")).strip() or str(item.get("kind", "")).strip()
                        message = str(item.get("message", "")).strip() or "-"
                        lines.append(f"- {timestamp} · {title} · {message}")
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
                self._architecture_revision_artifact(),
                self._ui_revision_artifact(),
                self._quality_revision_artifact(),
                self._spec_quality_artifact(),
                self._scope_coverage_artifact(),
                self._product_audit_artifact(),
                self._repo_map_artifact(),
                self._dependency_graph_artifact(),
                self._impact_analysis_artifact(),
                self._regression_guard_artifact(),
                self._document_artifact("Research", "*-research.md"),
                self._document_artifact("PRD", "*-prd.md"),
                self._document_artifact("Architecture", "*-architecture.md"),
                self._document_artifact("UI/UX", "*-uiux.md"),
                self._ui_contract_artifact(),
                self._ui_contract_alignment_artifact(),
                self._redteam_artifact(),
                self._task_execution_artifact(),
                self._operational_harness_artifact(),
                self._workflow_continuity_artifact(),
                self._frontend_runtime_artifact(),
                self._ui_review_artifact(),
                self._quality_gate_artifact(),
                self._delivery_manifest_artifact(),
                self._rehearsal_artifact(),
                self._release_readiness_artifact(verify_tests=verify_tests),
            ]
        )
        framework_harness = self._framework_harness_artifact()
        if framework_harness is not None:
            report.artifacts.append(framework_harness)
        hook_audit = self._hook_audit_artifact()
        if hook_audit is not None:
            report.artifacts.append(hook_audit)

        # 新增：治理证据（增量添加，文件不存在则跳过）
        report.artifacts.extend(self._governance_artifacts())

        return report

    def write(self, report: ProofPackReport) -> dict[str, Path]:
        base = self.output_dir / f"{self.project_name}-proof-pack"
        md_path = base.with_suffix(".md")
        json_path = base.with_suffix(".json")
        summary_path = self.output_dir / f"{self.project_name}-proof-pack-summary.md"
        md_path.write_text(report.to_markdown(), encoding="utf-8")
        json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        summary_path.write_text(report.to_executive_markdown(), encoding="utf-8")
        return {"markdown": md_path, "json": json_path, "summary": summary_path}

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

    def _architecture_revision_artifact(self) -> ProofPackArtifact:
        payload = load_architecture_revision(self.project_dir)
        file_path = self.project_dir / ".super-dev" / "review-state" / "architecture-revision.json"
        if not payload:
            return ProofPackArtifact(
                name="Architecture Revision State",
                status="ready",
                summary="no open architecture revision",
                path=str(file_path) if file_path.exists() else "",
            )
        status = str(payload.get("status", "pending_review"))
        if status == "confirmed":
            artifact_status = "ready"
            summary = "architecture revision confirmed"
        elif status == "revision_requested":
            artifact_status = "pending"
            summary = "architecture revision still open"
        else:
            artifact_status = "pending"
            summary = f"status={status}"
        return ProofPackArtifact(
            name="Architecture Revision State",
            status=artifact_status,
            summary=summary,
            path=str(file_path),
            details=payload,
        )

    def _quality_revision_artifact(self) -> ProofPackArtifact:
        payload = load_quality_revision(self.project_dir)
        file_path = self.project_dir / ".super-dev" / "review-state" / "quality-revision.json"
        if not payload:
            return ProofPackArtifact(
                name="Quality Revision State",
                status="ready",
                summary="no open quality revision",
                path=str(file_path) if file_path.exists() else "",
            )
        status = str(payload.get("status", "pending_review"))
        if status == "confirmed":
            artifact_status = "ready"
            summary = "quality revision confirmed"
        elif status == "revision_requested":
            artifact_status = "pending"
            summary = "quality revision still open"
        else:
            artifact_status = "pending"
            summary = f"status={status}"
        return ProofPackArtifact(
            name="Quality Revision State",
            status=artifact_status,
            summary=summary,
            path=str(file_path),
            details=payload,
        )

    def _spec_quality_artifact(self) -> ProofPackArtifact:
        validator = SpecValidator(self.project_dir)
        report = validator.assess_latest_change_quality(exclude_ids={"release-hardening-finalization"})
        if report is None:
            return ProofPackArtifact(
                name="Spec Quality",
                status="ready",
                summary="no active change spec under evaluation",
            )
        change_dir = self.project_dir / ".super-dev" / "changes" / report.change_id
        return ProofPackArtifact(
            name="Spec Quality",
            status="ready" if report.passed else "pending",
            summary=f"change={report.change_id}, score={report.score:.1f}, level={report.level}",
            path=str(change_dir),
            details=report.to_dict(),
        )

    def _repo_map_artifact(self) -> ProofPackArtifact:
        markdown_path = self._latest("*-repo-map.md")
        json_path = self._latest("*-repo-map.json")
        if markdown_path is None and json_path is None:
            return ProofPackArtifact(
                name="Repo Map",
                status="missing",
                summary="repo map has not been generated",
            )
        chosen = markdown_path or json_path
        return ProofPackArtifact(
            name="Repo Map",
            status="ready",
            summary="codebase intelligence artifact available",
            path=str(chosen) if chosen else "",
            details={"json_path": str(json_path) if json_path else ""},
        )

    def _dependency_graph_artifact(self) -> ProofPackArtifact:
        markdown_path = self._latest("*-dependency-graph.md")
        json_path = self._latest("*-dependency-graph.json")
        if markdown_path is None and json_path is None:
            return ProofPackArtifact(
                name="Dependency Graph",
                status="missing",
                summary="dependency graph has not been generated",
            )
        chosen = markdown_path or json_path
        return ProofPackArtifact(
            name="Dependency Graph",
            status="ready",
            summary="dependency graph and critical path artifact available",
            path=str(chosen) if chosen else "",
            details={"json_path": str(json_path) if json_path else ""},
        )

    def _impact_analysis_artifact(self) -> ProofPackArtifact:
        markdown_path = self._latest("*-impact-analysis.md")
        json_path = self._latest("*-impact-analysis.json")
        if markdown_path is None and json_path is None:
            return ProofPackArtifact(
                name="Impact Analysis",
                status="missing",
                summary="impact analysis has not been generated",
            )
        chosen = markdown_path or json_path
        return ProofPackArtifact(
            name="Impact Analysis",
            status="ready",
            summary="change impact analysis artifact available",
            path=str(chosen) if chosen else "",
            details={"json_path": str(json_path) if json_path else ""},
        )

    def _regression_guard_artifact(self) -> ProofPackArtifact:
        markdown_path = self._latest("*-regression-guard.md")
        json_path = self._latest("*-regression-guard.json")
        if markdown_path is None and json_path is None:
            return ProofPackArtifact(
                name="Regression Guard",
                status="missing",
                summary="regression guard has not been generated",
            )
        chosen = markdown_path or json_path
        return ProofPackArtifact(
            name="Regression Guard",
            status="ready",
            summary="regression verification checklist available",
            path=str(chosen) if chosen else "",
            details={"json_path": str(json_path) if json_path else ""},
        )

    def _frontend_runtime_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-frontend-runtime.json")
        if file_path is None:
            return ProofPackArtifact(name="Frontend Runtime", status="missing", summary="frontend runtime report missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.debug(f"Failed to parse frontend runtime JSON: {e}")
            payload = {}
        checks = payload.get("checks", {}) if isinstance(payload, dict) else {}
        passed = bool(payload.get("passed", False)) if isinstance(payload, dict) else False
        contract_aligned = not isinstance(checks, dict) or (
            bool(checks.get("ui_contract_json", False))
            and bool(checks.get("output_frontend_design_tokens", False))
            and bool(checks.get("ui_contract_alignment", False))
            and bool(checks.get("ui_theme_entry", False))
            and bool(checks.get("ui_navigation_shell", False))
            and bool(checks.get("ui_component_imports", False))
            and bool(checks.get("ui_banned_patterns", False))
            and bool(checks.get("ui_framework_playbook", True))
            and bool(checks.get("ui_framework_execution", True))
        )
        return ProofPackArtifact(
            name="Frontend Runtime",
            status="ready" if passed and contract_aligned else "pending",
            summary=(
                "frontend runtime passed and UI contract / framework playbook are wired"
                if passed and contract_aligned
                else "frontend runtime not passed or UI contract / framework evidence is incomplete"
            ),
            path=str(file_path),
            details=payload if isinstance(payload, dict) else {},
        )

    def _ui_contract_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-ui-contract.json")
        if file_path is None:
            return ProofPackArtifact(name="UI Contract", status="missing", summary="UI contract missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.debug(f"Failed to parse UI contract JSON: {e}")
            return ProofPackArtifact(
                name="UI Contract",
                status="pending",
                summary="UI contract is not valid JSON",
                path=str(file_path),
            )
        if not isinstance(payload, dict):
            return ProofPackArtifact(
                name="UI Contract",
                status="pending",
                summary="UI contract must be a JSON object",
                path=str(file_path),
            )
        component_stack = payload.get("component_stack", {}) if isinstance(payload.get("component_stack"), dict) else {}
        emoji_policy = payload.get("emoji_policy") if isinstance(payload.get("emoji_policy"), dict) else {}
        analysis = payload.get("analysis", {}) if isinstance(payload.get("analysis"), dict) else {}
        frontend_value = str(analysis.get("frontend") or "").lower().strip()
        cross_platform_frontend = is_cross_platform_frontend(frontend_value)
        framework_playbook = payload.get("framework_playbook") if isinstance(payload.get("framework_playbook"), dict) else {}
        icon_system = payload.get("icon_system") or component_stack.get("icon") or component_stack.get("icons") or ""
        required_sections = {
            "style_direction": bool(payload.get("style_direction")),
            "typography": (
                (isinstance(payload.get("typography"), dict) and bool(payload.get("typography")))
                or (isinstance(payload.get("typography_preset"), dict) and bool(payload.get("typography_preset")))
            ),
            "icon_system": bool(icon_system),
            "emoji_policy": (
                bool(emoji_policy)
                and emoji_policy.get("allowed_in_ui") is False
                and emoji_policy.get("allowed_as_icon") is False
                and emoji_policy.get("allowed_during_development") is False
            ),
            "ui_library_preference": isinstance(payload.get("ui_library_preference"), dict)
            and bool(payload.get("ui_library_preference")),
            "design_tokens": isinstance(payload.get("design_tokens"), dict) and bool(payload.get("design_tokens")),
        }
        if cross_platform_frontend:
            required_sections["framework_playbook"] = framework_playbook_complete(framework_playbook)
        ready = all(required_sections.values())
        if ready:
            if cross_platform_frontend:
                summary = (
                    f"UI contract frozen with {framework_playbook.get('framework', 'cross-platform')} playbook, style, typography, icon system, emoji policy and design tokens"
                )
            else:
                summary = (
                    "UI contract frozen with style, typography, icon system, emoji policy, library preference and design tokens"
                )
        else:
            missing_sections = [name for name, present in required_sections.items() if not present]
            if cross_platform_frontend and "framework_playbook" in missing_sections:
                summary = (
                    f"UI contract missing {frontend_value or 'cross-platform'} framework playbook sections"
                )
            else:
                summary = "UI contract missing required frozen decision sections"
        return ProofPackArtifact(
            name="UI Contract",
            status="ready" if ready else "pending",
            summary=summary,
            path=str(file_path),
            details={"required_sections": required_sections},
        )

    def _ui_contract_alignment_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-ui-contract-alignment.json")
        if file_path is None:
            return ProofPackArtifact(
                name="UI Contract Alignment",
                status="missing",
                summary="UI contract alignment report missing",
            )
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.debug(f"Failed to parse UI contract alignment JSON: {e}")
            return ProofPackArtifact(
                name="UI Contract Alignment",
                status="pending",
                summary="UI contract alignment report unreadable",
                path=str(file_path),
            )
        if not isinstance(payload, dict):
            return ProofPackArtifact(
                name="UI Contract Alignment",
                status="pending",
                summary="UI contract alignment report must be a JSON object",
                path=str(file_path),
            )
        checks = [value for value in payload.values() if isinstance(value, dict)]
        passed = bool(checks) and all(bool(item.get("passed", False)) for item in checks)
        failed_labels = [str(item.get("label") or key) for key, item in payload.items() if isinstance(item, dict) and not item.get("passed", False)]
        summary = (
            "UI contract alignment verified across icons, typography, ecosystem and design tokens"
            if passed
            else f"UI contract alignment gaps: {', '.join(failed_labels[:4])}"
        )
        return ProofPackArtifact(
            name="UI Contract Alignment",
            status="ready" if passed else "pending",
            summary=summary,
            path=str(file_path),
            details=payload,
        )

    def _framework_harness_artifact(self) -> ProofPackArtifact | None:
        builder = FrameworkHarnessBuilder(self.project_dir)
        report = builder.build()
        if not report.enabled:
            return None
        report_files = builder.write(report)
        summary = (
            f"{report.framework} framework harness verified across playbook, runtime execution and alignment"
            if report.passed
            else (
                f"{report.framework} framework harness gaps: "
                + "；".join(report.blockers[:3])
            )
        )
        return ProofPackArtifact(
            name="Framework Harness",
            status="ready" if report.passed else "pending",
            summary=summary,
            path=str(report_files["json"]),
            details={
                "markdown": str(report_files["markdown"]),
                "checks": report.checks,
                "next_actions": report.next_actions,
                "framework": report.framework,
            },
        )

    def _operational_harness_artifact(self) -> ProofPackArtifact:
        builder = OperationalHarnessBuilder(self.project_dir)
        report = builder.build()
        report_files = builder.write(report)
        focus = derive_operational_focus(self.project_dir)
        summary = (
            f"operational harness verified across {report.passed_count}/{report.enabled_count} enabled harnesses"
            if report.passed
            else str(focus.get("summary", "")).strip()
            or "operational harness contains workflow / framework / hook blockers"
        )
        return ProofPackArtifact(
            name="Operational Harness",
            status="ready" if report.passed else "pending",
            summary=summary,
            path=str(report_files["json"]),
            details={
                "markdown": str(report_files["markdown"]),
                "operational_focus": focus,
                "focus": focus,
                **report.to_dict(),
            },
        )

    def _hook_audit_artifact(self) -> ProofPackArtifact | None:
        builder = HookHarnessBuilder(self.project_dir)
        report = builder.build()
        if not report.enabled:
            return None
        report_files = builder.write(report)
        summary = (
            f"recent hook execution history is clean across {report.total_events} recorded events"
            if report.passed
            else "hook execution history contains failed or blocked events"
        )
        return ProofPackArtifact(
            name="Hook Audit Trail",
            status="ready" if report.passed else "pending",
            summary=summary,
            path=str(report_files["json"]),
            details={
                "markdown": str(report_files["markdown"]),
                **report.to_dict(),
            },
        )

    def _redteam_artifact(self) -> ProofPackArtifact:
        evidence = load_redteam_evidence(self.project_dir, self.project_name)
        if evidence is None:
            return ProofPackArtifact(name="Redteam", status="missing", summary="redteam evidence missing")
        summary = (
            f"score={evidence.total_score}/{evidence.pass_threshold}, "
            f"critical={evidence.critical_count}, passed={evidence.passed}"
        )
        return ProofPackArtifact(
            name="Redteam",
            status="ready" if evidence.passed else "pending",
            summary=summary,
            path=str(evidence.path),
            details={
                "source_format": evidence.source_format,
                "blocking_reasons": evidence.blocking_reasons,
            },
        )

    def _task_execution_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-task-execution.md")
        if file_path is None:
            return ProofPackArtifact(name="Task Execution", status="missing", summary="task execution report missing")
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        has_validation = "## 执行期验证摘要" in text
        has_self_review = "## 宿主补充自检（交付前必做）" in text
        ready = has_validation and has_self_review
        summary = (
            "task execution report includes validation summary and delivery self-review"
            if ready
            else "task execution report missing validation summary or delivery self-review"
        )
        return ProofPackArtifact(
            name="Task Execution",
            status="ready" if ready else "pending",
            summary=summary,
            path=str(file_path),
            details={
                "has_validation_summary": has_validation,
                "has_delivery_self_review": has_self_review,
            },
        )

    def _workflow_continuity_artifact(self) -> ProofPackArtifact:
        builder = WorkflowHarnessBuilder(self.project_dir)
        report = builder.build()
        if not report.enabled:
            return ProofPackArtifact(
                name="Workflow Continuity",
                status="ready",
                summary="no active workflow continuity trail recorded",
                details=report.to_dict(),
            )
        report_files = builder.write(report)
        summary = (
            f"workflow continuity trail captured at {report.updated_at or 'unknown'} · {report.current_step_label or report.workflow_status or 'unknown'}"
            if report.passed
            else "workflow continuity trail is incomplete"
        )
        return ProofPackArtifact(
            name="Workflow Continuity",
            status="ready" if report.passed else "pending",
            summary=summary,
            path=str(report_files["json"]),
            details={
                "markdown": str(report_files["markdown"]),
                **report.to_dict(),
            },
        )

    def _ui_review_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-ui-review.json")
        if file_path is None:
            return ProofPackArtifact(name="UI Review", status="missing", summary="UI review report missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.debug(f"Failed to parse UI review JSON: {e}")
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
        except Exception as e:
            _logger.debug(f"Failed to parse delivery manifest JSON: {e}")
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
        except Exception as e:
            _logger.debug(f"Failed to parse rehearsal report JSON: {e}")
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

    def _scope_coverage_artifact(self) -> ProofPackArtifact:
        builder = FeatureChecklistBuilder(self.project_dir)
        report = builder.build()
        paths = builder.write(report)
        coverage_text = (
            f"{report.coverage_rate:.1f}%"
            if report.coverage_rate is not None
            else "unknown"
        )
        ready = report.status == "ready" or report.high_priority_gap_count == 0
        return ProofPackArtifact(
            name="Scope Coverage",
            status="ready" if ready else "pending",
            summary=(
                f"status={report.status}, coverage={coverage_text}, "
                f"high_priority_gaps={report.high_priority_gap_count}"
            ),
            path=str(paths["json"]),
            details=report.to_dict(),
        )

    def _governance_artifacts(self) -> list[ProofPackArtifact]:
        """Collect governance-related evidence artifacts (knowledge tracking, metrics, ADR, etc.)."""
        artifacts: list[ProofPackArtifact] = []

        # 1. 知识引用报告
        knowledge_report_candidates = [
            self.output_dir / "knowledge-tracking-report.md",
            *sorted(self.output_dir.glob("*-knowledge-tracking.md")),
        ]
        knowledge_report_path = next((path for path in knowledge_report_candidates if path.exists()), None)
        if knowledge_report_path is not None:
            artifacts.append(
                ProofPackArtifact(
                    name="Knowledge Reference Report",
                    status="ready",
                    summary="知识引用追踪报告已生成",
                    path=str(knowledge_report_path),
                )
            )

        # 2. 效能度量数据
        metrics_dir = self.output_dir / "metrics-history"
        if metrics_dir.exists():
            metric_files = list(metrics_dir.glob("*.json"))
            if metric_files:
                latest = sorted(metric_files)[-1]
                artifacts.append(
                    ProofPackArtifact(
                        name="Pipeline Metrics",
                        status="ready",
                        summary=f"效能度量数据 ({len(metric_files)} 次执行记录)",
                        path=str(latest),
                    )
                )

        # 3. 治理报告
        governance_reports = list(self.output_dir.glob("governance-report-*.md"))
        if governance_reports:
            latest_gov = sorted(governance_reports)[-1]
            artifacts.append(
                ProofPackArtifact(
                    name="Governance Report",
                    status="ready",
                    summary="Pipeline 治理总报告",
                    path=str(latest_gov),
                )
            )

        # 4. ADR 决策记录
        adr_dir = self.project_dir / ".super-dev" / "decisions"
        if adr_dir.exists():
            adr_files = list(adr_dir.glob("*.md"))
            if adr_files:
                artifacts.append(
                    ProofPackArtifact(
                        name="Architecture Decisions",
                        status="ready",
                        summary=f"{len(adr_files)} 个架构决策记录",
                        path=str(adr_dir),
                    )
                )

        # 5. 验证规则结果
        validation_results = list(self.output_dir.glob("validation-report-*.md")) + list(
            self.output_dir.glob("*-validation-results*.json")
        ) + list(self.output_dir.glob("*-validation-results*.md"))
        if validation_results:
            artifacts.append(
                ProofPackArtifact(
                    name="Validation Rules Report",
                    status="ready",
                    summary="验证规则检查结果",
                    path=str(sorted(validation_results)[-1]),
                )
            )

        return artifacts

    def _product_audit_artifact(self) -> ProofPackArtifact:
        file_path = self._latest("*-product-audit.json")
        if file_path is None:
            return ProofPackArtifact(name="Product Audit", status="missing", summary="product audit report missing")
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.debug(f"Failed to parse product audit JSON: {e}")
            payload = {}
        score = int(payload.get("score", 0)) if isinstance(payload, dict) else 0
        status = str(payload.get("status", "missing")) if isinstance(payload, dict) else "missing"
        ready = status in {"ready", "attention"}
        return ProofPackArtifact(
            name="Product Audit",
            status="ready" if ready else "pending",
            summary=f"status={status}, score={score}/100",
            path=str(file_path),
            details=payload if isinstance(payload, dict) else {},
        )
