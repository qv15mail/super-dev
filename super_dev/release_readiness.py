"""
开发：Excellent（11964948@qq.com）
功能：发布就绪度评估器
作用：评估版本对齐、文档覆盖、宿主兼容性等发布条件
创建时间：2025-12-30
最后修改：2026-03-20
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .analyzer import FeatureChecklistBuilder
from .catalogs import HOST_TOOL_IDS
from .framework_harness import FrameworkHarnessBuilder
from .frameworks import framework_playbook_complete, is_cross_platform_frontend
from .harness_registry import derive_operational_focus
from .hooks.manager import HookManager
from .integrations import IntegrationManager
from .operational_harness import OperationalHarnessBuilder
from .review_state import (
    load_recent_operational_timeline,
    load_recent_workflow_events,
    load_recent_workflow_snapshots,
    load_workflow_state,
)
from .reviewers.redteam import load_redteam_evidence
from .skills import SkillManager
from .specs import SpecValidator


@dataclass
class ReleaseReadinessCheck:
    name: str
    passed: bool
    detail: str
    severity: str = "medium"
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
            "severity": self.severity,
            "recommendation": self.recommendation,
        }


@dataclass
class ReleaseReadinessReport:
    project_name: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    threshold: int = 85
    checks: list[ReleaseReadinessCheck] = field(default_factory=list)
    recent_timeline: list[dict[str, Any]] = field(default_factory=list)
    operational_focus: dict[str, Any] = field(default_factory=dict)

    def _weight(self, severity: str) -> int:
        mapping = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return mapping.get(severity, 2)

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        total_weight = sum(self._weight(check.severity) for check in self.checks)
        passed_weight = sum(self._weight(check.severity) for check in self.checks if check.passed)
        return int((passed_weight / total_weight) * 100) if total_weight else 0

    @property
    def failed_checks(self) -> list[ReleaseReadinessCheck]:
        return [check for check in self.checks if not check.passed]

    @property
    def passed(self) -> bool:
        has_critical_failure = any(
            not check.passed and check.severity == "critical" for check in self.checks
        )
        return self.score >= self.threshold and not has_critical_failure

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "score": self.score,
            "passed": self.passed,
            "threshold": self.threshold,
            "failed_checks": [item.name for item in self.failed_checks],
            "checks": [item.to_dict() for item in self.checks],
            "recent_timeline": list(self.recent_timeline),
            "operational_focus": dict(self.operational_focus),
        }

    def to_markdown(self) -> str:
        lines = [
            "# Release Readiness Report",
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
            "| Check | Result | Severity | Detail | Recommendation |",
            "|:---|:---:|:---:|:---|:---|",
        ]
        for check in self.checks:
            marker = "PASS" if check.passed else "FAIL"
            lines.append(
                f"| {check.name} | {marker} | {check.severity} | {check.detail} | {check.recommendation or '-'} |"
            )
        lines.append("")

        # 治理就绪度章节
        governance_checks = [c for c in self.checks if c.name.startswith("Governance:")]
        if governance_checks:
            lines.append("## Governance Readiness")
            lines.append("")
            gov_passed = sum(1 for c in governance_checks if c.passed)
            gov_total = len(governance_checks)
            lines.append(f"- Governance checks: {gov_passed}/{gov_total} passed")
            lines.append("")
            lines.append("| Check | Result | Detail |")
            lines.append("|:---|:---:|:---|")
            for gc in governance_checks:
                marker = "PASS" if gc.passed else "FAIL"
                lines.append(f"| {gc.name} | {marker} | {gc.detail} |")
            lines.append("")

        operational_checks = [
            c
            for c in self.checks
            if c.name
            in {
                "Workflow Recovery Trail",
                "Framework Harness Trail",
                "Hook Audit Trail",
                "Operational Harness Trail",
            }
        ]
        if operational_checks:
            lines.append("## Operational Continuity")
            lines.append("")
            lines.append("| Check | Result | Detail |")
            lines.append("|:---|:---:|:---|")
            for oc in operational_checks:
                marker = "PASS" if oc.passed else "FAIL"
                lines.append(f"| {oc.name} | {marker} | {oc.detail} |")
            lines.append("")
        focus_summary = str(self.operational_focus.get("summary", "")).strip()
        focus_action = str(self.operational_focus.get("recommended_action", "")).strip()
        if focus_summary:
            lines.append("## Current Governance Focus")
            lines.append("")
            lines.append(f"- {focus_summary}")
            if focus_action:
                lines.append(f"- 建议先做: {focus_action}")
            lines.append("")
        if self.recent_timeline:
            lines.append("## Recent Operational Timeline")
            lines.append("")
            for item in self.recent_timeline:
                timestamp = str(item.get("timestamp", "")).strip() or "-"
                title = str(item.get("title", "")).strip() or str(item.get("kind", "")).strip()
                message = str(item.get("message", "")).strip() or "-"
                lines.append(f"- {timestamp} · {title} · {message}")
            lines.append("")

        return "\n".join(lines)


class ReleaseReadinessEvaluator:
    """评估当前仓库是否达到可发布状态。"""

    REQUIRED_DOCS = {
        "README.md": [
            "pip install",
            "uv tool install",
            "/super-dev",
            "super-dev:",
            "super-dev update",
        ],
        "README_EN.md": [
            "pip install",
            "uv tool install",
            "/super-dev",
            "super-dev:",
            "super-dev update",
        ],
        "docs/README.md": ["用户文档", "维护者文档"],
        "docs/HOST_USAGE_GUIDE.md": ["Smoke", "/super-dev", "super-dev:"],
        "docs/HOST_CAPABILITY_AUDIT.md": ["官方依据", "super-dev integrate smoke"],
        "docs/HOST_RUNTIME_VALIDATION.md": [
            "host runtime validation",
            "research",
            "super-dev review docs",
        ],
        "docs/HOST_INSTALL_SURFACES.md": [
            "Codex CLI",
            "super-dev:",
            "super-dev integrate audit --auto",
        ],
        "docs/WORKFLOW_GUIDE.md": ["super-dev review docs", "super-dev run --resume"],
        "docs/WORKFLOW_GUIDE_EN.md": ["super-dev review docs", "super-dev run --resume"],
        "docs/PRODUCT_AUDIT.md": ["super-dev product-audit", "proof-pack", "release readiness"],
    }

    REQUIRED_RUNTIME_IGNORE_RULES = [
        "output/",
        "artifacts/",
        ".super-dev/runs/",
        ".super-dev/review-state/",
        "/.agent/",
        "/.claude/",
        "/.codebuddy/",
        "/.cursor/",
        "/.gemini/",
        "/.kiro/",
        "/.opencode/",
        "/.qoder/",
        "/.trae/",
        "/.windsurf/",
        "/GEMINI.md",
    ]

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        self.output_dir = self.project_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def evaluate(self, verify_tests: bool = False) -> ReleaseReadinessReport:
        report = ReleaseReadinessReport(project_name=self.project_dir.name)
        report.recent_timeline = load_recent_operational_timeline(self.project_dir, limit=5)
        report.operational_focus = derive_operational_focus(self.project_dir)
        report.checks.extend(
            [
                self._check_version_alignment(),
                self._check_required_docs(),
                self._check_host_matrix_integrity(),
                self._check_host_coverage_depth(),
                self._check_runtime_boundary_rules(),
                self._check_packaging_entrypoints(),
                self._check_release_spec_exists(),
                self._check_spec_quality(),
                self._check_scope_coverage(),
                self._check_delivery_closure(),
                self._check_workflow_recovery_trail(),
                self._check_framework_harness_trail(),
                self._check_hook_audit_trail(),
                self._check_operational_harness_trail(),
            ]
        )
        # 治理能力检查（增量添加，不影响现有逻辑）
        report.checks.extend(self._check_governance_artifacts())
        if verify_tests:
            report.checks.append(self._check_test_suite())
        return report

    def write(self, report: ReleaseReadinessReport) -> dict[str, Path]:
        base = self.output_dir / f"{self.project_dir.name}-release-readiness"
        md_path = base.with_suffix(".md")
        json_path = base.with_suffix(".json")
        md_path.write_text(report.to_markdown(), encoding="utf-8")
        json_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return {"markdown": md_path, "json": json_path}

    def _check_version_alignment(self) -> ReleaseReadinessCheck:
        pyproject = self.project_dir / "pyproject.toml"
        init_file = self.project_dir / "super_dev" / "__init__.py"
        readme = self.project_dir / "README.md"
        readme_en = self.project_dir / "README_EN.md"

        pyproject_version = self._extract_regex(pyproject, r'version\s*=\s*"([^"]+)"')
        init_version = self._extract_regex(init_file, r'__version__\s*=\s*"([^"]+)"')
        readme_version = self._extract_regex(readme, r"当前版本：`([^`]+)`")
        readme_en_version = self._extract_regex(readme_en, r"Current version: `([^`]+)`")

        versions = [
            value
            for value in [pyproject_version, init_version, readme_version, readme_en_version]
            if value
        ]
        unique_versions = sorted(set(versions))
        passed = len(unique_versions) == 1 and unique_versions[0] == __version__
        detail = f"versions={unique_versions or ['missing']}"
        return ReleaseReadinessCheck(
            name="Version Alignment",
            passed=passed,
            detail=detail,
            severity="critical" if not passed else "low",
            recommendation="同步 pyproject、super_dev/__init__.py、README 与 README_EN 中的版本号。",
        )

    def _check_required_docs(self) -> ReleaseReadinessCheck:
        missing: list[str] = []
        for relative_path, markers in self.REQUIRED_DOCS.items():
            file_path = self.project_dir / relative_path
            if not file_path.exists():
                missing.append(f"{relative_path} (missing)")
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for marker in markers:
                if marker not in text:
                    missing.append(f"{relative_path} -> {marker}")
        passed = not missing
        detail = "all required docs and markers present" if passed else "; ".join(missing[:8])
        return ReleaseReadinessCheck(
            name="Documentation Coverage",
            passed=passed,
            detail=detail,
            severity="high" if not passed else "low",
            recommendation="补齐发布、宿主使用、Smoke 验收与恢复流程文档。",
        )

    def _check_host_matrix_integrity(self) -> ReleaseReadinessCheck:
        gaps = IntegrationManager.coverage_gaps()
        skill_gaps = SkillManager.coverage_gaps()
        all_missing = sum(len(items) for items in gaps.values()) + sum(
            len(items) for items in skill_gaps.values()
        )
        passed = all_missing == 0
        detail = (
            "host targets, slash map, docs map and skill targets are aligned"
            if passed
            else f"integration_gaps={gaps}, skill_gaps={skill_gaps}"
        )
        return ReleaseReadinessCheck(
            name="Host Matrix Integrity",
            passed=passed,
            detail=detail,
            severity="critical" if not passed else "low",
            recommendation="确保宿主目录、slash/skill 覆盖、官方文档映射保持一致。",
        )

    def _check_host_coverage_depth(self) -> ReleaseReadinessCheck:
        manager = IntegrationManager(self.project_dir)
        profiles = manager.list_adapter_profiles()
        certified = [item.host for item in profiles if item.certification_level == "certified"]
        compatible = [item.host for item in profiles if item.certification_level == "compatible"]
        docs_unverified = [item.host for item in profiles if not item.docs_verified]
        official_backed = [
            item.host
            for item in profiles
            if item.host_protocol_mode
            in {"official-subagent", "official-skill", "official-steering", "official-context"}
        ]

        stable_hosts = len(certified) + len(compatible)
        passed = (
            len(certified) >= 2
            and len(official_backed) >= max(10, len(HOST_TOOL_IDS) - 3)
            and stable_hosts >= 8
            and not docs_unverified
        )
        detail = (
            f"certified={len(certified)}, compatible={len(compatible)}, stable={stable_hosts}, official_backed={len(official_backed)}, total={len(profiles)}"
            if passed
            else f"certified={certified}, compatible={compatible}, stable={stable_hosts}, official_backed={official_backed}, docs_unverified={docs_unverified}"
        )
        return ReleaseReadinessCheck(
            name="Host Coverage Depth",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation="继续提升关键宿主的稳定等级，并确保官方依据已核验。",
        )

    def _check_packaging_entrypoints(self) -> ReleaseReadinessCheck:
        install_script = self.project_dir / "install.sh"
        pyproject = self.project_dir / "pyproject.toml"
        readme = self.project_dir / "README.md"
        text = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else ""
        pyproject_text = (
            pyproject.read_text(encoding="utf-8", errors="ignore") if pyproject.exists() else ""
        )

        checks = [
            install_script.exists(),
            "[project.scripts]" in pyproject_text,
            "super-dev = " in pyproject_text,
            "pip install -U super-dev" in text,
            "uv tool install super-dev" in text,
            "super-dev update" in text,
        ]
        passed = all(checks)
        detail = (
            "installer, entrypoint and pip/uv/update docs are present"
            if passed
            else "missing installer or entrypoint/docs markers"
        )
        return ReleaseReadinessCheck(
            name="Packaging Entrypoints",
            passed=passed,
            detail=detail,
            severity="high" if not passed else "low",
            recommendation="确保 pip/uv 安装、入口脚本和 update 命令文档一致。",
        )

    def _check_runtime_boundary_rules(self) -> ReleaseReadinessCheck:
        gitignore = self.project_dir / ".gitignore"
        text = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""
        missing = [rule for rule in self.REQUIRED_RUNTIME_IGNORE_RULES if rule not in text]
        passed = not missing
        detail = (
            "runtime host surfaces and review-state ignore rules are present"
            if passed
            else f"missing ignore rules: {', '.join(missing[:8])}"
        )
        return ReleaseReadinessCheck(
            name="Runtime Boundary Rules",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation="明确忽略宿主运行时目录、review-state 与项目级宿主接入产物，避免本机生成文件混入仓库。",
        )

    def _check_release_spec_exists(self) -> ReleaseReadinessCheck:
        change_dir = self.project_dir / ".super-dev" / "changes" / "release-hardening-finalization"
        required = [
            change_dir / "change.yaml",
            change_dir / "proposal.md",
            change_dir / "tasks.md",
        ]
        missing = [
            str(path.relative_to(self.project_dir)) for path in required if not path.exists()
        ]
        passed = not missing
        detail = "release change spec present" if passed else f"missing {', '.join(missing)}"
        return ReleaseReadinessCheck(
            name="Release Change Spec",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation="将发布收尾任务沉淀到正式 change spec，避免口头跟踪。",
        )

    def _check_spec_quality(self) -> ReleaseReadinessCheck:
        validator = SpecValidator(self.project_dir)
        report = validator.assess_latest_change_quality(
            exclude_ids={"release-hardening-finalization"}
        )
        if report is None:
            return ReleaseReadinessCheck(
                name="Spec Quality",
                passed=True,
                detail="no active change spec under evaluation",
                severity="low",
                recommendation="如当前发布包含新需求或修复变更，先执行 `super-dev spec quality <change_id>`。",
            )

        passed = report.passed
        detail = f"change={report.change_id}, score={report.score:.1f}, level={report.level}, blockers={len(report.blockers)}"
        recommendation = (
            report.action_plan[0].get("command", "")
            if report.action_plan
            else f"执行 `super-dev spec quality {report.change_id}` 查看完整整改计划。"
        )
        return ReleaseReadinessCheck(
            name="Spec Quality",
            passed=passed,
            detail=detail,
            severity="high" if not passed else "low",
            recommendation=recommendation,
        )

    def _check_scope_coverage(self) -> ReleaseReadinessCheck:
        builder = FeatureChecklistBuilder(self.project_dir)
        report = builder.build()
        builder.write(report)

        coverage_text = (
            f"{report.coverage_rate:.1f}%" if report.coverage_rate is not None else "unknown"
        )
        detail = (
            f"status={report.status}, coverage={coverage_text}, "
            f"high_priority_gaps={report.high_priority_gap_count}, missing={report.missing_count}, unknown={report.unknown_count}"
        )

        if report.status == "unknown":
            return ReleaseReadinessCheck(
                name="Scope Coverage",
                passed=True,
                detail=detail,
                severity="low",
                recommendation="如需确认 PRD 全量覆盖率，先执行 `super-dev feature-checklist` 生成范围完成度报告。",
            )

        passed = report.high_priority_gap_count == 0 and report.missing_count == 0
        recommendation = (
            "先补齐 P0/P1 缺口或把未实现能力明确降级为后续版本，再重新执行 `super-dev feature-checklist`。"
            if not passed
            else "当前范围覆盖率未发现高优先级缺口。"
        )
        return ReleaseReadinessCheck(
            name="Scope Coverage",
            passed=passed,
            detail=detail,
            severity="high" if not passed else "low",
            recommendation=recommendation,
        )

    def _check_test_suite(self) -> ReleaseReadinessCheck:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            return ReleaseReadinessCheck(
                name="Test Suite",
                passed=False,
                detail=f"pytest execution failed: {exc}",
                severity="critical",
                recommendation="修复测试环境后重新执行 `super-dev release readiness --verify-tests`。",
            )
        output = "\n".join(
            part for part in [result.stdout.strip(), result.stderr.strip()] if part
        ).strip()
        tail = output.splitlines()[-1] if output else "no output"
        return ReleaseReadinessCheck(
            name="Test Suite",
            passed=result.returncode == 0,
            detail=tail,
            severity="critical" if result.returncode != 0 else "low",
            recommendation="确保全量 pytest 通过后再执行对外发布。",
        )

    def _check_delivery_closure(self) -> ReleaseReadinessCheck:
        redteam = load_redteam_evidence(self.project_dir, self.project_dir.name)
        quality_gate_file = self.output_dir / f"{self.project_dir.name}-quality-gate.md"
        task_execution_file = self.output_dir / f"{self.project_dir.name}-task-execution.md"
        product_audit_file = self.output_dir / f"{self.project_dir.name}-product-audit.json"
        ui_contract_file = self.output_dir / f"{self.project_dir.name}-ui-contract.json"
        frontend_runtime_file = self.output_dir / f"{self.project_dir.name}-frontend-runtime.json"
        design_tokens_file = self.output_dir / "frontend" / "design-tokens.css"

        blockers: list[str] = []

        if redteam is None:
            blockers.append("redteam missing")
        elif not redteam.passed:
            blockers.append(
                f"redteam failed ({'; '.join(redteam.blocking_reasons) or redteam.path.name})"
            )

        if not quality_gate_file.exists():
            blockers.append("quality gate missing")
        else:
            quality_text = quality_gate_file.read_text(encoding="utf-8", errors="ignore").lower()
            if "未通过" in quality_text or "failed" in quality_text:
                blockers.append("quality gate failed")

        if not task_execution_file.exists():
            blockers.append("task execution missing")
        else:
            task_text = task_execution_file.read_text(encoding="utf-8", errors="ignore")
            if (
                "## 执行期验证摘要" not in task_text
                or "## 宿主补充自检（交付前必做）" not in task_text
            ):
                blockers.append("task execution self-review incomplete")

        if not product_audit_file.exists():
            blockers.append("product audit missing")
        else:
            try:
                product_payload = json.loads(product_audit_file.read_text(encoding="utf-8"))
            except Exception:
                blockers.append("product audit unreadable")
            else:
                product_status = str(product_payload.get("status", "missing"))
                if product_status == "revision_required":
                    blockers.append("product audit requires revision")

        if not ui_contract_file.exists():
            blockers.append("ui contract missing")
        else:
            try:
                ui_contract_payload = json.loads(ui_contract_file.read_text(encoding="utf-8"))
            except Exception:
                blockers.append("ui contract unreadable")
            else:
                if not isinstance(ui_contract_payload, dict):
                    blockers.append("ui contract invalid")
                else:
                    component_stack = (
                        ui_contract_payload.get("component_stack", {})
                        if isinstance(ui_contract_payload.get("component_stack"), dict)
                        else {}
                    )
                    emoji_policy = (
                        ui_contract_payload.get("emoji_policy")
                        if isinstance(ui_contract_payload.get("emoji_policy"), dict)
                        else {}
                    )
                    analysis = (
                        ui_contract_payload.get("analysis", {})
                        if isinstance(ui_contract_payload.get("analysis"), dict)
                        else {}
                    )
                    frontend_value = str(analysis.get("frontend") or "").lower().strip()
                    cross_platform_frontend = is_cross_platform_frontend(frontend_value)
                    framework_playbook = (
                        ui_contract_payload.get("framework_playbook")
                        if isinstance(ui_contract_payload.get("framework_playbook"), dict)
                        else {}
                    )
                    icon_system = (
                        ui_contract_payload.get("icon_system")
                        or component_stack.get("icon")
                        or component_stack.get("icons")
                    )
                    required_sections = (
                        bool(ui_contract_payload.get("style_direction")),
                        (
                            (
                                isinstance(ui_contract_payload.get("typography"), dict)
                                and bool(ui_contract_payload.get("typography"))
                            )
                            or (
                                isinstance(ui_contract_payload.get("typography_preset"), dict)
                                and bool(ui_contract_payload.get("typography_preset"))
                            )
                        ),
                        bool(icon_system),
                        (
                            bool(emoji_policy)
                            and emoji_policy.get("allowed_in_ui") is False
                            and emoji_policy.get("allowed_as_icon") is False
                            and emoji_policy.get("allowed_during_development") is False
                        ),
                        isinstance(ui_contract_payload.get("ui_library_preference"), dict)
                        and bool(ui_contract_payload.get("ui_library_preference")),
                        isinstance(ui_contract_payload.get("design_tokens"), dict)
                        and bool(ui_contract_payload.get("design_tokens")),
                    )
                    if cross_platform_frontend:
                        framework_name = str(
                            framework_playbook.get("framework")
                            or frontend_value
                            or "cross-platform"
                        ).strip()
                        required_sections = (
                            *required_sections,
                            framework_playbook_complete(framework_playbook),
                        )
                    if not all(required_sections):
                        if cross_platform_frontend:
                            blockers.append(f"{framework_name} ui contract playbook incomplete")
                        else:
                            blockers.append("ui contract incomplete")

        if not design_tokens_file.exists():
            blockers.append("design tokens missing")

        if not frontend_runtime_file.exists():
            blockers.append("frontend runtime missing")
        else:
            try:
                frontend_runtime_payload = json.loads(
                    frontend_runtime_file.read_text(encoding="utf-8")
                )
            except Exception:
                blockers.append("frontend runtime unreadable")
            else:
                checks = (
                    frontend_runtime_payload.get("checks", {})
                    if isinstance(frontend_runtime_payload, dict)
                    else {}
                )
                key_ui_checks = (
                    "ui_contract_alignment",
                    "ui_theme_entry",
                    "ui_navigation_shell",
                    "ui_component_imports",
                    "ui_banned_patterns",
                    "ui_framework_playbook",
                    "ui_framework_execution",
                )
                runtime_ready = (
                    isinstance(frontend_runtime_payload, dict)
                    and bool(frontend_runtime_payload.get("passed", False))
                    and isinstance(checks, dict)
                    and bool(checks.get("ui_contract_json", False))
                    and bool(checks.get("output_frontend_design_tokens", False))
                    and all(bool(checks.get(name, True)) for name in key_ui_checks)
                )
                if not runtime_ready:
                    if cross_platform_frontend:
                        framework_name = str(
                            framework_playbook.get("framework")
                            or frontend_value
                            or "cross-platform"
                        ).strip()
                        blockers.append(
                            f"{framework_name} frontend runtime framework execution missing"
                        )
                    else:
                        blockers.append("frontend runtime ui contract alignment missing")

        passed = not blockers
        detail = "delivery closure evidence aligned" if passed else "; ".join(blockers)
        return ReleaseReadinessCheck(
            name="Delivery Closure",
            passed=passed,
            detail=detail,
            severity="critical" if not passed else "low",
            recommendation=(
                "先补齐 redteam / quality gate / task execution / product audit / ui contract / frontend runtime 证据，并确保它们指向同一轮交付。"
            ),
        )

    def _check_workflow_recovery_trail(self) -> ReleaseReadinessCheck:
        state_payload = load_workflow_state(self.project_dir)
        recent_snapshots = load_recent_workflow_snapshots(self.project_dir, limit=3)
        recent_events = load_recent_workflow_events(self.project_dir, limit=5)

        if state_payload is None and not recent_snapshots:
            return ReleaseReadinessCheck(
                name="Workflow Recovery Trail",
                passed=True,
                detail="no active workflow recovery trail recorded",
                severity="low",
                recommendation="如当前发布来自活跃 Super Dev 流程，建议补齐 workflow-state、history snapshots 与 workflow events。",
            )

        status = str(
            (state_payload or {}).get("status", "")
            or (state_payload or {}).get("workflow_status", "")
        ).strip()
        current_step = str((state_payload or {}).get("current_step_label", "")).strip()
        passed = state_payload is not None and bool(recent_snapshots) and bool(recent_events)
        detail = (
            f"status={status or 'unknown'}, step={current_step or 'unknown'}, snapshots={len(recent_snapshots)}, events={len(recent_events)}"
            if passed
            else f"workflow recovery trail incomplete: state={'yes' if state_payload is not None else 'no'}, snapshots={len(recent_snapshots)}, events={len(recent_events)}"
        )
        return ReleaseReadinessCheck(
            name="Workflow Recovery Trail",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation="补齐 .super-dev/workflow-state.json、workflow-history 快照和 workflow-events.jsonl，确保关窗、断开和次日恢复有正式证据。",
        )

    def _check_hook_audit_trail(self) -> ReleaseReadinessCheck:
        history = HookManager.load_recent_history(self.project_dir, limit=20)
        if not history:
            return ReleaseReadinessCheck(
                name="Hook Audit Trail",
                passed=True,
                detail="no hook execution history recorded",
                severity="low",
                recommendation="如项目启用了 hooks，建议在关键阶段执行后保留 hook 审计历史。",
            )

        blocked = [item for item in history if item.blocked]
        failed = [item for item in history if not item.success]
        passed = not blocked and not failed
        if passed:
            detail = f"recent hook history clean across {len(history)} events"
        elif blocked:
            detail = f"recent hook history contains {len(blocked)} blocked events"
        else:
            detail = f"recent hook history contains {len(failed)} failed events"
        return ReleaseReadinessCheck(
            name="Hook Audit Trail",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation="检查 .super-dev/hook-history.jsonl 中最近的失败或阻断 hook，修复命令或放宽 blocking 策略后再重试。",
        )

    def _check_framework_harness_trail(self) -> ReleaseReadinessCheck:
        harness = FrameworkHarnessBuilder(self.project_dir).build()
        if not harness.enabled:
            return ReleaseReadinessCheck(
                name="Framework Harness Trail",
                passed=True,
                detail="no cross-platform framework harness required",
                severity="low",
                recommendation="如项目属于 uni-app / Taro / RN / Flutter / Desktop Shell，建议保留 framework harness 证据。",
            )

        passed = harness.passed
        blocker_count = len(harness.blockers)
        detail = (
            f"{harness.framework or 'framework'} harness clean"
            if passed
            else f"{harness.framework or 'framework'} harness has {blocker_count} blockers"
        )
        recommendation = (
            harness.next_actions[0]
            if harness.next_actions
            else "补齐 framework playbook、alignment 与 frontend runtime 的专项执行证据。"
        )
        return ReleaseReadinessCheck(
            name="Framework Harness Trail",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation=recommendation,
        )

    def _check_operational_harness_trail(self) -> ReleaseReadinessCheck:
        harness = OperationalHarnessBuilder(self.project_dir).build()
        focus = derive_operational_focus(self.project_dir)
        if not harness.enabled:
            return ReleaseReadinessCheck(
                name="Operational Harness Trail",
                passed=True,
                detail="no operational harness evidence required",
                severity="low",
                recommendation="如当前 run 依赖 workflow / framework / hook harness，建议保留统一 operational harness 证据。",
            )

        passed = harness.passed
        detail = (
            f"operational harness clean across {harness.passed_count}/{harness.enabled_count} enabled harnesses"
            if passed
            else str(focus.get("summary", "")).strip()
            or f"operational harness has {len(harness.blockers)} blockers across {harness.enabled_count} enabled harnesses"
        )
        recommendation = str(focus.get("recommended_action", "")).strip() or (
            harness.next_actions[0]
            if harness.next_actions
            else "补齐 workflow / framework / hook harness 后重新生成 operational harness。"
        )
        return ReleaseReadinessCheck(
            name="Operational Harness Trail",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation=recommendation,
        )

    def _check_governance_artifacts(self) -> list[ReleaseReadinessCheck]:
        """检查治理相关产物是否就绪（增量检查，不影响现有逻辑）。"""
        checks: list[ReleaseReadinessCheck] = []

        # 1. 治理报告
        governance_reports = list(self.output_dir.glob("governance-report-*.md"))
        if governance_reports:
            checks.append(
                ReleaseReadinessCheck(
                    name="Governance: Report",
                    passed=True,
                    detail=f"治理报告已生成 ({len(governance_reports)} 份)",
                    severity="medium",
                )
            )
        else:
            checks.append(
                ReleaseReadinessCheck(
                    name="Governance: Report",
                    passed=False,
                    detail="未找到治理报告 (output/governance-report-*.md)",
                    severity="low",
                    recommendation="执行治理流程生成 governance-report 后重新评估。",
                )
            )

        # 2. 知识引用报告
        knowledge_refs = list(self.output_dir.glob("*-knowledge-references*.md")) + list(
            self.output_dir.glob("*-knowledge-references*.json")
        )
        knowledge_cache = (
            list((self.output_dir / "knowledge-cache").glob("*-knowledge-bundle.json"))
            if (self.output_dir / "knowledge-cache").is_dir()
            else []
        )
        has_knowledge = bool(knowledge_refs or knowledge_cache)
        checks.append(
            ReleaseReadinessCheck(
                name="Governance: Knowledge References",
                passed=has_knowledge,
                detail=(
                    f"知识引用报告 {len(knowledge_refs)} 份, 知识缓存 {len(knowledge_cache)} 份"
                    if has_knowledge
                    else "未找到知识引用报告或知识缓存"
                ),
                severity="low",
                recommendation=(
                    "" if has_knowledge else "建议在文档阶段启用知识库引用，确保决策有据可查。"
                ),
            )
        )

        # 3. 效能度量数据
        metrics_files = (
            list(self.output_dir.glob("*-metrics*.json"))
            + list(self.output_dir.glob("*-pipeline-metrics.json"))
            + list(self.output_dir.glob("*-pipeline-metrics.md"))
            + (
                list((self.output_dir / "metrics-history").glob("*.json"))
                if (self.output_dir / "metrics-history").is_dir()
                else []
            )
            + list(self.output_dir.glob("*-performance-metrics*.md"))
        )
        has_metrics = bool(metrics_files)
        checks.append(
            ReleaseReadinessCheck(
                name="Governance: Performance Metrics",
                passed=has_metrics,
                detail=(
                    f"效能度量文件 {len(metrics_files)} 份" if has_metrics else "未找到效能度量数据"
                ),
                severity="low",
                recommendation="" if has_metrics else "建议生成效能度量报告以量化交付质量。",
            )
        )

        # 4. ADR 决策记录
        adr_dir = self.project_dir / "docs" / "adr"
        adr_files = list(adr_dir.glob("*.md")) if adr_dir.is_dir() else []
        # 也检查 output 目录中的 ADR
        adr_output = list(self.output_dir.glob("*-adr-*.md"))
        all_adrs = adr_files + adr_output
        has_adrs = bool(all_adrs)
        checks.append(
            ReleaseReadinessCheck(
                name="Governance: ADR Records",
                passed=has_adrs,
                detail=f"ADR 决策记录 {len(all_adrs)} 份" if has_adrs else "未找到 ADR 决策记录",
                severity="low",
                recommendation="" if has_adrs else "建议为重要架构决策创建 ADR 记录 (docs/adr/)。",
            )
        )

        # 5. 验证规则结果
        validation_files = list(self.output_dir.glob("*-validation-results*.json")) + list(
            self.output_dir.glob("*-validation-results*.md")
        )
        has_validation = bool(validation_files)
        checks.append(
            ReleaseReadinessCheck(
                name="Governance: Validation Results",
                passed=has_validation,
                detail=(
                    f"验证规则结果 {len(validation_files)} 份"
                    if has_validation
                    else "未找到验证规则结果"
                ),
                severity="low",
                recommendation="" if has_validation else "执行验证规则引擎生成结果后重新评估。",
            )
        )

        return checks

    def _extract_regex(self, file_path: Path, pattern: str) -> str:
        if not file_path.exists():
            return ""
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""
