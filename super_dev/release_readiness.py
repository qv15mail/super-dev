"""
Super Dev 产品发布就绪度评估
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
from .catalogs import HOST_TOOL_IDS
from .integrations import IntegrationManager
from .skills import SkillManager


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
        has_critical_failure = any(not check.passed and check.severity == "critical" for check in self.checks)
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
        return "\n".join(lines)


class ReleaseReadinessEvaluator:
    """评估当前仓库是否达到可发布状态。"""

    REQUIRED_DOCS = {
        "README.md": ["pip install", "uv tool install", "/super-dev", "super-dev:", "super-dev update"],
        "README_EN.md": ["pip install", "uv tool install", "/super-dev", "super-dev:", "super-dev update"],
        "docs/HOST_USAGE_GUIDE.md": ["Smoke", "/super-dev", "super-dev:"],
        "docs/HOST_CAPABILITY_AUDIT.md": ["官方依据", "super-dev integrate smoke"],
        "docs/PRODUCT_AUDIT.md": ["P0", "P1", "P2"],
        "docs/WORKFLOW_GUIDE.md": ["super-dev review docs", "super-dev run --resume"],
        "docs/WORKFLOW_GUIDE_EN.md": ["super-dev review docs", "super-dev run --resume"],
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
        "/.iflow/",
        "/.kimi/",
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
        report.checks.extend(
            [
                self._check_version_alignment(),
                self._check_required_docs(),
                self._check_host_matrix_integrity(),
                self._check_host_coverage_depth(),
                self._check_runtime_boundary_rules(),
                self._check_packaging_entrypoints(),
                self._check_release_spec_exists(),
            ]
        )
        if verify_tests:
            report.checks.append(self._check_test_suite())
        return report

    def write(self, report: ReleaseReadinessReport) -> dict[str, Path]:
        base = self.output_dir / f"{self.project_dir.name}-release-readiness"
        md_path = base.with_suffix(".md")
        json_path = base.with_suffix(".json")
        md_path.write_text(report.to_markdown(), encoding="utf-8")
        json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
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

        versions = [value for value in [pyproject_version, init_version, readme_version, readme_en_version] if value]
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
        all_missing = sum(len(items) for items in gaps.values()) + sum(len(items) for items in skill_gaps.values())
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
            if item.host_protocol_mode in {"official-subagent", "official-skill", "official-steering", "official-context"}
        ]

        passed = (
            len(certified) >= 2
            and len(official_backed) >= max(10, len(HOST_TOOL_IDS) - 3)
            and len(certified) + len(compatible) >= max(8, len(HOST_TOOL_IDS) // 2)
            and not docs_unverified
        )
        detail = (
            f"certified={len(certified)}, compatible={len(compatible)}, official_backed={len(official_backed)}, total={len(profiles)}"
            if passed
            else f"certified={certified}, compatible={compatible}, official_backed={official_backed}, docs_unverified={docs_unverified}"
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
        pyproject_text = pyproject.read_text(encoding="utf-8", errors="ignore") if pyproject.exists() else ""

        checks = [
            install_script.exists(),
            "[project.scripts]" in pyproject_text,
            "super-dev = " in pyproject_text,
            "pip install -U super-dev" in text,
            "uv tool install super-dev" in text,
            "super-dev update" in text,
        ]
        passed = all(checks)
        detail = "installer, entrypoint and pip/uv/update docs are present" if passed else "missing installer or entrypoint/docs markers"
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
        detail = "runtime host surfaces and review-state ignore rules are present" if passed else f"missing ignore rules: {', '.join(missing[:8])}"
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
        missing = [str(path.relative_to(self.project_dir)) for path in required if not path.exists()]
        passed = not missing
        detail = "release change spec present" if passed else f"missing {', '.join(missing)}"
        return ReleaseReadinessCheck(
            name="Release Change Spec",
            passed=passed,
            detail=detail,
            severity="medium" if not passed else "low",
            recommendation="将发布收尾任务沉淀到正式 change spec，避免口头跟踪。",
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
        output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part).strip()
        tail = output.splitlines()[-1] if output else "no output"
        return ReleaseReadinessCheck(
            name="Test Suite",
            passed=result.returncode == 0,
            detail=tail,
            severity="critical" if result.returncode != 0 else "low",
            recommendation="确保全量 pytest 通过后再执行对外发布。",
        )

    def _extract_regex(self, file_path: Path, pattern: str) -> str:
        if not file_path.exists():
            return ""
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""
