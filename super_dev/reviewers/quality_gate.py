"""
质量门禁检查器 - 确保交付物达到质量标准

开发：Excellent（11964948@qq.com）
功能：多维度质量评分和门禁检查
作用：按场景阈值（或自定义阈值）评估是否通过质量门禁
创建时间：2025-12-30
"""

import json
import re
import shutil
import subprocess  # nosec B404
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, TypedDict

import yaml  # type: ignore[import-untyped]
from defusedxml import ElementTree

from ..config import ConfigManager
from .redteam import RedTeamReport


class CheckStatus(Enum):
    """检查状态"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class QualityCheck:
    """质量检查项"""
    name: str
    category: str  # documentation, security, performance, testing, code_quality
    description: str
    status: CheckStatus
    score: int  # 0-100
    weight: float = 1.0  # 权重，用于计算加权总分
    details: str = ""


@dataclass
class QualityGateResult:
    """质量门禁结果"""
    passed: bool
    total_score: int
    weighted_score: float
    checks: list[QualityCheck] = field(default_factory=list)
    critical_failures: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    scenario: str = "1-N+1"  # 场景类型: "0-1" 或 "1-N+1"

    @property
    def passed_checks(self) -> list[QualityCheck]:
        return [c for c in self.checks if c.status == CheckStatus.PASSED]

    @property
    def failed_checks(self) -> list[QualityCheck]:
        return [c for c in self.checks if c.status == CheckStatus.FAILED]

    @property
    def warning_checks(self) -> list[QualityCheck]:
        return [c for c in self.checks if c.status == CheckStatus.WARNING]

    def to_markdown(self) -> str:
        """生成 Markdown 报告"""
        status_icon = "通过" if self.passed else "未通过"
        status_color = "green" if self.passed else "red"

        lines = [
            "# 质量门禁报告",
            "",
            f"**场景**: {self.scenario} ({'0-1 新建项目' if self.scenario == '0-1' else '1-N+1 增量开发'})",
            f"**状态**: <span style='color:{status_color}'>{status_icon}</span>",
            f"**总分**: {self.total_score}/100",
            f"**加权分**: {self.weighted_score:.1f}/100",
            "",
            "---",
            "",
            "## 检查结果摘要",
            "",
            f"- 通过: {len(self.passed_checks)} 项",
            f"- 警告: {len(self.warning_checks)} 项",
            f"- 失败: {len(self.failed_checks)} 项",
            "",
        ]

        if self.critical_failures:
            lines.extend([
                "## 关键失败项",
                "",
            ])
            for failure in self.critical_failures:
                lines.append(f"- {failure}")
            lines.append("")

        # 按类别分组展示
        categories: dict[str, list[QualityCheck]] = {}
        for check in self.checks:
            if check.category not in categories:
                categories[check.category] = []
            categories[check.category].append(check)

        lines.extend([
            "## 详细检查结果",
            "",
        ])

        for category, checks in categories.items():
            lines.extend([
                f"### {category}",
                "",
                "| 检查项 | 状态 | 得分 | 说明 |",
                "|:---|:---:|:---:|:---|",
            ])

            for check in checks:
                status_icon = "✓" if check.status == CheckStatus.PASSED else "⚠" if check.status == CheckStatus.WARNING else "✗"
                lines.append(
                    f"| {check.name} | {status_icon} | {check.score}/100 | {check.description} |"
                )

            lines.append("")

        # 改进建议
        if self.recommendations:
            lines.extend([
                "## 改进建议",
                "",
            ])
            for idx, rec in enumerate(self.recommendations, 1):
                lines.append(f"{idx}. {rec}")
            lines.append("")

        # 下一步行动
        lines.extend([
            "---",
            "",
            "## 下一步行动",
            "",
        ])

        if self.passed:
            lines.extend([
                "[通过] 质量门禁已通过，可以继续下一步：",
                "",
                "1. 开始编码实现",
                "2. 设置 CI/CD 流水线",
                "3. 部署到测试环境",
                "",
            ])
        else:
            lines.extend([
                "[未通过] 质量门禁未通过，请完成以下操作后重新检查：",
                "",
            ])

            failed_items = [f"- {c.description}" for c in self.failed_checks]
            lines.extend(failed_items)
            lines.extend([
                "",
                "修复后运行: `super-dev quality --type all`",
                "",
            ])

        return "\n".join(lines)


class HostProfileMetrics(TypedDict):
    label: str
    overall_score: float
    ready_hosts: int
    total_hosts: int
    bounded_score: int


class QualityGateChecker:
    """质量门禁检查器"""

    # 质量门禁阈值
    PASS_THRESHOLD = 80
    WARNING_THRESHOLD = 60
    # 0-1 场景与增量场景统一使用 80+ 标准
    PASS_THRESHOLD_ZERO_TO_ONE = 80
    HOST_COMPAT_MIN_SCORE = 80
    HOST_COMPAT_MIN_READY_HOSTS = 1

    # 检查项配置
    CHECKS_CONFIG = {
        "documentation": {
            "weight": 1.0,
            "required": True,
        },
        "security": {
            "weight": 1.5,  # 安全更重要
            "required": True,
        },
        "performance": {
            "weight": 1.2,
            "required": True,
        },
        "testing": {
            "weight": 1.3,
            "required": True,
        },
        "code_quality": {
            "weight": 1.0,
            "required": False,
        },
        "accessibility": {
            "weight": 0.8,
            "required": False,
        },
        "ui_quality": {
            "weight": 1.2,
            "required": True,
        },
    }

    def __init__(
        self,
        project_dir: Path,
        name: str,
        tech_stack: dict,
        scenario_override: str | None = None,
        threshold_override: int | None = None,
        host_compatibility_min_score_override: int | None = None,
        host_compatibility_min_ready_hosts_override: int | None = None,
    ):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack
        self.latest_ui_review_report = None
        self.threshold_override = threshold_override
        config = ConfigManager(self.project_dir).load()
        self.host_profile_targets = [
            item.strip()
            for item in getattr(config, "host_profile_targets", [])
            if isinstance(item, str) and item.strip()
        ]
        self.host_profile_enforce_selected = bool(
            getattr(config, "host_profile_enforce_selected", False)
        )
        self.host_compatibility_min_score = self._coerce_host_compat_score(
            host_compatibility_min_score_override
            if host_compatibility_min_score_override is not None
            else config.host_compatibility_min_score
        )
        self.host_compatibility_min_ready_hosts = self._coerce_host_compat_ready_hosts(
            host_compatibility_min_ready_hosts_override
            if host_compatibility_min_ready_hosts_override is not None
            else config.host_compatibility_min_ready_hosts
        )
        if scenario_override in {"0-1", "1-N+1"}:
            self.is_zero_to_one = scenario_override == "0-1"
        else:
            self.is_zero_to_one = self._detect_zero_to_one_scenario()

    def _coerce_host_compat_score(self, value: object) -> int:
        score = self._coerce_int(value, default=self.HOST_COMPAT_MIN_SCORE)
        return max(0, min(100, score))

    def _coerce_host_compat_ready_hosts(self, value: object) -> int:
        ready_hosts = self._coerce_int(value, default=self.HOST_COMPAT_MIN_READY_HOSTS)
        return max(0, ready_hosts)

    def _coerce_float(self, value: object, default: float) -> float:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return default
            try:
                return float(text)
            except ValueError:
                return default
        return default

    def _coerce_int(self, value: object, default: int) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return default
            try:
                return int(text)
            except ValueError:
                return default
        return default

    def _detect_zero_to_one_scenario(self) -> bool:
        """
        检测是否为 0-1 场景（空项目/新建项目）

        0-1 场景特征：
        - 没有源代码目录（src/, lib/, app/, server/, client/ 等）
        - 没有配置文件（package.json, requirements.txt, go.mod 等）
        - 只有 output/ 目录（刚生成的文档）

        Returns:
            bool: True 表示 0-1 场景，False 表示 1-N+1 场景
        """
        # 检查常见的源代码目录
        source_dirs = [
            "src", "lib", "app", "server", "client",
            "backend", "frontend", "api", "handlers",
            "models", "views", "controllers", "services"
        ]

        has_source_code = any(
            (self.project_dir / d).exists()
            for d in source_dirs
        )

        # 检查是否有项目配置文件（表明这不是空项目）
        config_files = [
            "package.json", "requirements.txt", "go.mod",
            "Cargo.toml", "pom.xml", "build.gradle"
        ]

        has_project_config = any(
            (self.project_dir / f).exists()
            for f in config_files
        )

        # 如果有源代码或有项目配置，说明不是 0-1 场景
        return not (has_source_code or has_project_config)

    def check(self, redteam_report: Optional["RedTeamReport"] = None) -> QualityGateResult:
        """执行质量门禁检查"""
        checks: list[QualityCheck] = []

        # 1. 文档质量检查
        checks.extend(self._check_documentation())

        # 2. 安全检查 (基于红队报告)
        checks.extend(self._check_security(redteam_report))

        # 3. 性能检查 (基于红队报告)
        checks.extend(self._check_performance(redteam_report))

        # 4. 测试检查
        checks.extend(self._check_testing())

        # 5. 代码质量检查
        checks.extend(self._check_code_quality())

        # 5.5 无障碍性检查
        checks.extend(self._check_accessibility())

        # 5.6 性能预算检查
        checks.extend(self._check_performance_budget())

        # 6. UI 审查
        checks.append(self._check_ui_review())

        # 计算总分和加权分
        total_score = self._calculate_total_score(checks)
        weighted_score = self._calculate_weighted_score(checks)

        # 根据场景选择阈值
        threshold = (
            self.threshold_override
            if self.threshold_override is not None
            else (self.PASS_THRESHOLD_ZERO_TO_ONE if self.is_zero_to_one else self.PASS_THRESHOLD)
        )

        # 收集关键失败项
        critical_failures = []
        for check in checks:
            config = self.CHECKS_CONFIG.get(check.category, {})
            if config.get("required", False) and check.status == CheckStatus.FAILED:
                critical_failures.append(f"[{check.category}] {check.description}")

        # 检查是否通过：必须达到阈值，且必检项不能失败
        passed = total_score >= threshold and not critical_failures

        # 生成改进建议
        recommendations = self._generate_recommendations(checks)

        # 确定场景类型
        scenario = "0-1" if self.is_zero_to_one else "1-N+1"

        return QualityGateResult(
            passed=passed,
            total_score=total_score,
            weighted_score=weighted_score,
            checks=checks,
            critical_failures=critical_failures,
            recommendations=recommendations,
            scenario=scenario,
        )

    def _check_documentation(self) -> list[QualityCheck]:
        """检查文档质量"""
        checks = []

        # 检查 PRD 是否存在
        prd_path = self.project_dir / "output" / f"{self.name}-prd.md"
        if prd_path.exists():
            content = prd_path.read_text(encoding="utf-8", errors="ignore")
            # 简单检查文档完整性
            has_vision = "产品愿景" in content or "vision" in content.lower()
            has_features = "功能需求" in content or "features" in content.lower()
            has_acceptance = "验收标准" in content or "acceptance" in content.lower()

            score = 100 if has_vision and has_features and has_acceptance else 70
            status = CheckStatus.PASSED if score >= 80 else CheckStatus.WARNING

            checks.append(QualityCheck(
                name="PRD 文档",
                category="documentation",
                description="产品需求文档完整性",
                status=status,
                score=score,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="包含产品愿景、功能需求和验收标准" if status == CheckStatus.PASSED else "文档内容不完整",
            ))
        else:
            checks.append(QualityCheck(
                name="PRD 文档",
                category="documentation",
                description="产品需求文档存在性",
                status=CheckStatus.FAILED,
                score=0,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="PRD 文档不存在",
            ))

        # 检查架构文档是否存在
        arch_path = self.project_dir / "output" / f"{self.name}-architecture.md"
        if arch_path.exists():
            content = arch_path.read_text(encoding="utf-8", errors="ignore")
            has_tech_stack = "技术栈" in content or "tech stack" in content.lower()
            has_database = "数据库" in content or "database" in content.lower()
            has_api = "API" in content

            score = 100 if has_tech_stack and has_database and has_api else 70
            status = CheckStatus.PASSED if score >= 80 else CheckStatus.WARNING

            checks.append(QualityCheck(
                name="架构文档",
                category="documentation",
                description="架构设计文档完整性",
                status=status,
                score=score,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="包含技术栈、数据库设计和 API 设计" if status == CheckStatus.PASSED else "文档内容不完整",
            ))
        else:
            checks.append(QualityCheck(
                name="架构文档",
                category="documentation",
                description="架构设计文档存在性",
                status=CheckStatus.FAILED,
                score=0,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="架构文档不存在",
            ))

        # 检查 UI/UX 文档是否存在
        uiux_path = self.project_dir / "output" / f"{self.name}-uiux.md"
        if uiux_path.exists():
            checks.append(QualityCheck(
                name="UI/UX 文档",
                category="documentation",
                description="UI/UX 设计文档存在性",
                status=CheckStatus.PASSED,
                score=100,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="UI/UX 文档已创建",
            ))
        else:
            checks.append(QualityCheck(
                name="UI/UX 文档",
                category="documentation",
                description="UI/UX 设计文档存在性",
                status=CheckStatus.FAILED,
                score=0,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="UI/UX 文档不存在（必需）",
            ))

        checks.append(self._check_document_consistency(prd_path=prd_path, arch_path=arch_path, uiux_path=uiux_path))

        return checks

    def _check_document_consistency(self, *, prd_path: Path, arch_path: Path, uiux_path: Path) -> QualityCheck:
        if not (prd_path.exists() and arch_path.exists() and uiux_path.exists()):
            return QualityCheck(
                name="三文档一致性",
                category="documentation",
                description="PRD/Architecture/UIUX 决策与证据闭环",
                status=CheckStatus.WARNING,
                score=60,
                weight=self.CHECKS_CONFIG["documentation"]["weight"],
                details="三文档未全部存在，无法进行一致性检查",
            )

        prd_content = prd_path.read_text(encoding="utf-8", errors="ignore")
        arch_content = arch_path.read_text(encoding="utf-8", errors="ignore")
        uiux_content = uiux_path.read_text(encoding="utf-8", errors="ignore")
        requirements = [
            ("PRD 证据章节", "联网研究证据与方案对比" in prd_content),
            ("PRD 决策账本", "关键决策账本" in prd_content),
            ("PRD 用户统一协议", "用户到专业交付统一协议" in prd_content),
            ("架构证据链", "架构选型取舍与证据链" in arch_content),
            ("架构决策账本", "架构决策账本" in arch_content),
            ("架构全端流水线", "Agent 执行流水线（全端）" in arch_content),
            ("UI 多端策略", "多端适配与平台化设计策略" in uiux_content),
            ("UI 质量门禁", "商业级设计质量门禁" in uiux_content),
            (
                "UI 五端覆盖",
                all(
                    term in uiux_content
                    for term in ("WEB", "H5", "微信小程序", "APP", "桌面端")
                ),
            ),
        ]
        passed_count = sum(1 for _, ok in requirements if ok)
        total = len(requirements)
        missing = [name for name, ok in requirements if not ok]
        score = int((passed_count / total) * 100) if total else 100
        if "UI 五端覆盖" in missing:
            status = CheckStatus.FAILED
            score = min(score, 59)
        elif score >= 85:
            status = CheckStatus.PASSED
        elif score >= 60:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.FAILED
        detail = f"命中 {passed_count}/{total}"
        if missing:
            detail += f"，缺失: {', '.join(missing)}"
        return QualityCheck(
            name="三文档一致性",
            category="documentation",
            description="PRD/Architecture/UIUX 决策与证据闭环",
            status=status,
            score=score,
            weight=self.CHECKS_CONFIG["documentation"]["weight"],
            details=detail,
        )

    def _check_accessibility(self) -> list[QualityCheck]:
        """检查前端无障碍性（A11y / WCAG 2.1）"""
        checks: list[QualityCheck] = []

        # 扫描前端源文件
        source_dirs = ["frontend", "src", "app", "client", "pages", "components"]
        extensions = {".html", ".tsx", ".jsx", ".vue", ".svelte"}
        skip_dirs = {"node_modules", ".git", "dist", "build", "__pycache__", ".next", ".nuxt"}

        files_scanned = 0
        issues: dict[str, int] = {
            "missing_alt": 0,
            "missing_label": 0,
            "click_no_keyboard": 0,
            "div_click_handler": 0,
        }
        has_landmarks = False

        for src_dir_name in source_dirs:
            src_dir = self.project_dir / src_dir_name
            if not src_dir.exists():
                continue
            for file_path in src_dir.rglob("*"):
                if file_path.suffix not in extensions:
                    continue
                if any(skip in file_path.parts for skip in skip_dirs):
                    continue
                files_scanned += 1
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                # 检查图片是否缺少 alt 属性
                img_tags = re.findall(r'<img\b[^>]*>', content, re.IGNORECASE)
                for tag in img_tags:
                    if 'alt=' not in tag.lower() and 'alt =' not in tag.lower():
                        issues["missing_alt"] += 1

                # 检查输入框是否缺少 label 关联
                input_tags = re.findall(r'<input\b[^>]*>', content, re.IGNORECASE)
                for tag in input_tags:
                    tag_lower = tag.lower()
                    if ('aria-label' not in tag_lower
                            and 'aria-labelledby' not in tag_lower
                            and 'id=' not in tag_lower):
                        issues["missing_label"] += 1

                # 检查 onClick 是否缺少键盘事件处理
                onclick_count = len(re.findall(r'onClick\s*[={]', content))
                keyboard_count = len(re.findall(
                    r'on(?:Key(?:Down|Up|Press)|keydown|keyup|keypress)\s*[={]', content,
                ))
                if onclick_count > keyboard_count:
                    issues["click_no_keyboard"] += onclick_count - keyboard_count

                # 检查 div 是否使用了 click handler（应使用 button）
                div_clicks = len(re.findall(r'<div\b[^>]*onClick', content))
                issues["div_click_handler"] += div_clicks

                # 检查 ARIA landmarks 或语义化标签
                if re.search(r'(?:role\s*=|<(?:main|nav|header|footer|aside)\b)', content):
                    has_landmarks = True

        if files_scanned == 0:
            checks.append(QualityCheck(
                name="无障碍性检查",
                category="accessibility",
                description="前端文件无障碍性 (WCAG 2.1)",
                status=CheckStatus.WARNING,
                score=80,
                weight=0.8,
                details="未找到前端源文件，跳过无障碍性检查",
            ))
            return checks

        score = 100
        details_parts: list[str] = []

        if issues["missing_alt"] > 0:
            score -= 15
            details_parts.append(f"发现 {issues['missing_alt']} 个 <img> 缺少 alt 属性")

        if issues["missing_label"] > 0:
            score -= 15
            details_parts.append(f"发现 {issues['missing_label']} 个 <input> 缺少 label/aria-label")

        if issues["click_no_keyboard"] > 0:
            score -= 15
            details_parts.append(f"发现 {issues['click_no_keyboard']} 个 onClick 缺少键盘事件处理")

        if issues["div_click_handler"] > 0:
            score -= 15
            details_parts.append(f"发现 {issues['div_click_handler']} 个 <div> 使用 onClick（应使用 <button>）")

        if not has_landmarks:
            score -= 10
            details_parts.append("未检测到 ARIA landmarks 或语义化标签")

        score = max(0, score)

        if score >= 80:
            status = CheckStatus.PASSED
        elif score >= 60:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.FAILED

        details = "; ".join(details_parts) if details_parts else "无障碍性检查通过"

        checks.append(QualityCheck(
            name="无障碍性检查",
            category="accessibility",
            description="前端文件无障碍性 (WCAG 2.1)",
            status=status,
            score=score,
            weight=0.8,
            details=f"扫描 {files_scanned} 个文件 - {details}",
        ))

        return checks

    def _check_performance_budget(self) -> list[QualityCheck]:
        """检查性能预算（bundle size、依赖数量）"""
        checks: list[QualityCheck] = []
        score = 100
        details_parts: list[str] = []

        # 检查前端 bundle 产物大小
        dist_dirs = ["dist", "build", ".next", ".output", "out"]
        total_bundle_kb = 0
        bundle_dir_found = False

        for dist_name in dist_dirs:
            dist_dir = self.project_dir / "frontend" / dist_name
            if not dist_dir.exists():
                dist_dir = self.project_dir / dist_name
            if not dist_dir.exists():
                continue
            bundle_dir_found = True
            for f in dist_dir.rglob("*"):
                if f.is_file() and f.suffix in {".js", ".css", ".mjs"}:
                    total_bundle_kb += f.stat().st_size / 1024

        if bundle_dir_found:
            if total_bundle_kb > 2048:  # > 2MB
                score -= 25
                details_parts.append(f"前端 bundle 总量 {total_bundle_kb:.0f}KB（超过 2MB 预算）")
            elif total_bundle_kb > 1024:  # > 1MB
                score -= 10
                details_parts.append(f"前端 bundle 总量 {total_bundle_kb:.0f}KB（接近 1MB 预算）")
            else:
                details_parts.append(f"前端 bundle 总量 {total_bundle_kb:.0f}KB（在预算内）")

        # 检查 npm 依赖数量
        pkg_json = self.project_dir / "frontend" / "package.json"
        if not pkg_json.exists():
            pkg_json = self.project_dir / "package.json"

        if pkg_json.exists():
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                dep_count = len(pkg.get("dependencies", {}))

                if dep_count > 40:
                    score -= 15
                    details_parts.append(f"生产依赖 {dep_count} 个（超过 40 个上限）")
                elif dep_count > 25:
                    score -= 5
                    details_parts.append(f"生产依赖 {dep_count} 个（较多）")
                else:
                    details_parts.append(f"生产依赖 {dep_count} 个")
            except (json.JSONDecodeError, OSError):
                pass

        # 检查大文件（潜在性能问题）
        large_files = 0
        for src_dir_name in ["frontend/src", "src", "app"]:
            src_dir = self.project_dir / src_dir_name
            if not src_dir.exists():
                continue
            for f in src_dir.rglob("*"):
                if f.is_file() and f.suffix in {".ts", ".tsx", ".js", ".jsx", ".vue"} and f.stat().st_size > 50 * 1024:
                    large_files += 1

        if large_files > 0:
            score -= min(15, large_files * 5)
            details_parts.append(f"{large_files} 个前端文件超过 50KB（影响代码分割）")

        score = max(0, score)

        if score >= 80:
            status = CheckStatus.PASSED
        elif score >= 60:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.FAILED

        details = "; ".join(details_parts) if details_parts else "未检测到前端构建产物"

        checks.append(QualityCheck(
            name="性能预算检查",
            category="performance",
            description="前端性能预算（bundle size、依赖数量）",
            status=status,
            score=score,
            weight=1.0,
            details=details,
        ))

        return checks

    def _check_ui_review(self) -> QualityCheck:
        """检查商业级 UI 基线和实现一致性"""
        from .ui_review import UIReviewReviewer

        reviewer = UIReviewReviewer(
            project_dir=self.project_dir,
            name=self.name,
            tech_stack=self.tech_stack,
        )
        report = reviewer.review()
        self.latest_ui_review_report = report

        if report.critical_count > 0:
            status = CheckStatus.FAILED
        elif report.high_count > 0 or report.score < 80:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.PASSED

        detail_prefix = (
            f"score={report.score}, critical={report.critical_count}, "
            f"high={report.high_count}, medium={report.medium_count}"
        )
        if report.findings:
            details = f"{detail_prefix}; top issue: {report.findings[0].title}"
        else:
            details = f"{detail_prefix}; 未发现明显 UI 商业级违例"

        from ..design.ui_intelligence import UIIntelligenceAdvisor

        checklist = UIIntelligenceAdvisor.PRE_DELIVERY_CHECKLIST
        details += f" | 交付检查清单 ({len(checklist)} 项): " + "; ".join(checklist[:3]) + "..."

        return QualityCheck(
            name="UI 商业完成度",
            category="ui_quality",
            description="UI 设计基线、实现一致性与反模式扫描",
            status=status,
            score=report.score,
            weight=self.CHECKS_CONFIG["ui_quality"]["weight"],
            details=details,
        )

    def _check_security(self, redteam_report: RedTeamReport | None) -> list[QualityCheck]:
        """检查安全性"""
        checks: list[QualityCheck] = []

        if redteam_report:
            critical_count = sum(1 for i in redteam_report.security_issues if i.severity == "critical")
            high_count = sum(1 for i in redteam_report.security_issues if i.severity == "high")

            if critical_count > 0:
                score = max(0, 100 - critical_count * 30)
                status = CheckStatus.FAILED
            elif high_count > 2:
                score = max(0, 100 - high_count * 15)
                status = CheckStatus.WARNING
            else:
                score = 100
                status = CheckStatus.PASSED

            checks.append(QualityCheck(
                name="安全审查",
                category="security",
                description=f"安全检查 ({critical_count} critical, {high_count} high)",
                status=status,
                score=score,
                weight=self.CHECKS_CONFIG["security"]["weight"],
                details=f"发现 {critical_count} 个严重问题和 {high_count} 个高危问题" if critical_count + high_count > 0 else "未发现严重安全问题",
            ))
        else:
            # 未进行红队审查，给警告
            checks.append(QualityCheck(
                name="安全审查",
                category="security",
                description="安全检查状态",
                status=CheckStatus.WARNING,
                score=50,
                weight=self.CHECKS_CONFIG["security"]["weight"],
                details="未进行红队安全审查",
            ))

        return checks

    def _check_performance(self, redteam_report: RedTeamReport | None) -> list[QualityCheck]:
        """检查性能"""
        checks: list[QualityCheck] = []

        if redteam_report:
            critical_count = sum(1 for i in redteam_report.performance_issues if i.severity == "critical")
            high_count = sum(1 for i in redteam_report.performance_issues if i.severity == "high")

            if critical_count > 0:
                score = max(0, 100 - critical_count * 25)
                status = CheckStatus.FAILED
            elif high_count > 2:
                score = max(0, 100 - high_count * 10)
                status = CheckStatus.WARNING
            else:
                score = 100
                status = CheckStatus.PASSED

            checks.append(QualityCheck(
                name="性能审查",
                category="performance",
                description=f"性能检查 ({critical_count} critical, {high_count} high)",
                status=status,
                score=score,
                weight=self.CHECKS_CONFIG["performance"]["weight"],
                details=f"发现 {critical_count} 个严重问题和 {high_count} 个高危问题" if critical_count + high_count > 0 else "未发现严重性能问题",
            ))
        else:
            checks.append(QualityCheck(
                name="性能审查",
                category="performance",
                description="性能检查状态",
                status=CheckStatus.WARNING,
                score=50,
                weight=self.CHECKS_CONFIG["performance"]["weight"],
                details="未进行红队性能审查",
            ))

        return checks

    def _check_testing(self) -> list[QualityCheck]:
        """检查测试策略"""
        checks: list[QualityCheck] = []

        # 检查是否有测试配置
        has_jest = self._has_js_test_script()
        has_pytest = self._has_pytest_config()

        if has_jest or has_pytest:
            checks.append(QualityCheck(
                name="测试框架",
                category="testing",
                description="测试框架配置",
                status=CheckStatus.PASSED,
                score=100,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details="测试框架已配置",
            ))
        else:
            checks.append(QualityCheck(
                name="测试框架",
                category="testing",
                description="测试框架配置",
                status=CheckStatus.WARNING,
                score=50,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details="测试框架未配置",
            ))

        python_tests = self._discover_python_tests()
        js_test_targets = self._discover_js_test_targets()

        # 真实测试执行检查（优先 Python）
        if python_tests:
            pytest_executable = shutil.which("pytest")
            if pytest_executable:
                result = self._run_command(
                    [pytest_executable, "-q", "--maxfail=1"],
                    timeout=180,
                )
                if result["timed_out"]:
                    checks.append(QualityCheck(
                        name="测试执行",
                        category="testing",
                        description="自动化测试执行结果",
                        status=CheckStatus.WARNING,
                        score=40,
                        weight=self.CHECKS_CONFIG["testing"]["weight"],
                        details="pytest 执行超时，建议拆分测试或优化测试速度",
                    ))
                elif result["returncode"] == 0:
                    summary = self._extract_test_summary(str(result["stdout"]))
                    checks.append(QualityCheck(
                        name="测试执行",
                        category="testing",
                        description="自动化测试执行结果",
                        status=CheckStatus.PASSED,
                        score=100,
                        weight=self.CHECKS_CONFIG["testing"]["weight"],
                        details=summary or "pytest 执行通过",
                    ))
                else:
                    summary = self._extract_test_summary(str(result["stdout"] or result["stderr"]))
                    checks.append(QualityCheck(
                        name="测试执行",
                        category="testing",
                        description="自动化测试执行结果",
                        status=CheckStatus.FAILED,
                        score=20,
                        weight=self.CHECKS_CONFIG["testing"]["weight"],
                        details=summary or "pytest 执行失败",
                    ))
            else:
                checks.append(QualityCheck(
                    name="测试执行",
                    category="testing",
                    description="自动化测试执行结果",
                    status=CheckStatus.WARNING,
                    score=40,
                    weight=self.CHECKS_CONFIG["testing"]["weight"],
                    details="检测到 Python 测试，但未找到 pytest 可执行文件",
                ))
        elif js_test_targets:
            npm_executable = shutil.which("npm")
            if not npm_executable:
                checks.append(QualityCheck(
                    name="测试执行",
                    category="testing",
                    description="自动化测试执行结果",
                    status=CheckStatus.WARNING,
                    score=40,
                    weight=self.CHECKS_CONFIG["testing"]["weight"],
                    details="检测到 JS 测试脚本，但未找到 npm 可执行文件",
                ))
            else:
                timed_out_targets: list[str] = []
                failed_targets: list[str] = []
                passed_targets: list[str] = []
                for target in js_test_targets:
                    rel = "."
                    if target != self.project_dir:
                        rel = str(target.relative_to(self.project_dir))
                    result = self._run_command(
                        [
                            npm_executable,
                            "--prefix",
                            str(target),
                            "run",
                            "test",
                            "--if-present",
                        ],
                        timeout=240,
                    )
                    if result["timed_out"]:
                        timed_out_targets.append(rel)
                    elif result["returncode"] == 0:
                        passed_targets.append(rel)
                    else:
                        failed_targets.append(rel)

                if failed_targets:
                    checks.append(QualityCheck(
                        name="测试执行",
                        category="testing",
                        description="自动化测试执行结果",
                        status=CheckStatus.FAILED,
                        score=20,
                        weight=self.CHECKS_CONFIG["testing"]["weight"],
                        details=f"JS 测试失败: {', '.join(failed_targets)}",
                    ))
                elif timed_out_targets:
                    checks.append(QualityCheck(
                        name="测试执行",
                        category="testing",
                        description="自动化测试执行结果",
                        status=CheckStatus.WARNING,
                        score=40,
                        weight=self.CHECKS_CONFIG["testing"]["weight"],
                        details=f"JS 测试超时: {', '.join(timed_out_targets)}",
                    ))
                else:
                    checks.append(QualityCheck(
                        name="测试执行",
                        category="testing",
                        description="自动化测试执行结果",
                        status=CheckStatus.PASSED,
                        score=100,
                        weight=self.CHECKS_CONFIG["testing"]["weight"],
                        details=f"JS 测试通过: {', '.join(passed_targets)}",
                    ))
        else:
            warning_score = 70 if self.is_zero_to_one else 40
            checks.append(QualityCheck(
                name="测试执行",
                category="testing",
                description="自动化测试执行结果",
                status=CheckStatus.WARNING,
                score=warning_score,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details="未检测到可执行测试用例",
            ))

        checks.append(self._check_spec_task_completion())

        coverage_percent = self._read_coverage_percent()
        if coverage_percent is None:
            warning_score = 70 if self.is_zero_to_one else 50
            checks.append(QualityCheck(
                name="测试覆盖率",
                category="testing",
                description="覆盖率报告",
                status=CheckStatus.WARNING,
                score=warning_score,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details="未检测到 coverage.xml 报告",
            ))
        elif coverage_percent >= 80:
            checks.append(QualityCheck(
                name="测试覆盖率",
                category="testing",
                description="覆盖率报告",
                status=CheckStatus.PASSED,
                score=coverage_percent,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details=f"覆盖率 {coverage_percent}%",
            ))
        elif coverage_percent >= 60:
            checks.append(QualityCheck(
                name="测试覆盖率",
                category="testing",
                description="覆盖率报告",
                status=CheckStatus.WARNING,
                score=coverage_percent,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details=f"覆盖率 {coverage_percent}%（建议提升到 80%+）",
            ))
        else:
            checks.append(QualityCheck(
                name="测试覆盖率",
                category="testing",
                description="覆盖率报告",
                status=CheckStatus.FAILED,
                score=coverage_percent,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details=f"覆盖率 {coverage_percent}%（低于最低建议）",
            ))

        return checks

    def _check_spec_task_completion(self) -> QualityCheck:
        """检查 Spec 任务完成度"""
        task_files = list((self.project_dir / ".super-dev" / "changes").glob("*/tasks.md"))
        if not task_files:
            warning_score = 70 if self.is_zero_to_one else 50
            return QualityCheck(
                name="Spec任务完成度",
                category="testing",
                description="Spec 任务闭环状态",
                status=CheckStatus.WARNING,
                score=warning_score,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details="未发现 .super-dev/changes/*/tasks.md",
            )

        latest_task_file = max(task_files, key=lambda path: path.stat().st_mtime)
        total = 0
        completed = 0
        in_progress = 0
        for line in latest_task_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if not stripped.startswith("- ["):
                continue
            marker = stripped[2:5]
            if not re.match(r"^\[[ x~_]\]$", marker):
                continue
            total += 1
            if marker == "[x]":
                completed += 1
            elif marker == "[~]":
                in_progress += 1

        if total == 0:
            warning_score = 70 if self.is_zero_to_one else 50
            return QualityCheck(
                name="Spec任务完成度",
                category="testing",
                description="Spec 任务闭环状态",
                status=CheckStatus.WARNING,
                score=warning_score,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details="发现 tasks.md 但未解析到任务项",
            )

        pending = total - completed
        completion_rate = int((completed / total) * 100)
        if pending == 0 and in_progress == 0:
            return QualityCheck(
                name="Spec任务完成度",
                category="testing",
                description="Spec 任务闭环状态",
                status=CheckStatus.PASSED,
                score=100,
                weight=self.CHECKS_CONFIG["testing"]["weight"],
                details=f"任务完成 {completed}/{total}（{latest_task_file.parent.name}）",
            )

        score = max(20, completion_rate)
        check_status = CheckStatus.FAILED if completion_rate < 80 else CheckStatus.WARNING
        return QualityCheck(
            name="Spec任务完成度",
            category="testing",
            description="Spec 任务闭环状态",
            status=check_status,
            score=score,
            weight=self.CHECKS_CONFIG["testing"]["weight"],
            details=f"任务完成 {completed}/{total}，未完成 {pending}（{latest_task_file.parent.name}）",
        )

    def _check_code_quality(self) -> list[QualityCheck]:
        """检查代码质量工具"""
        checks: list[QualityCheck] = []

        # 检查 Linter
        has_eslint = (self.project_dir / ".eslintrc.js").exists() or (
            self.project_dir / ".eslintrc.json"
        ).exists()
        has_pylint = (self.project_dir / "pylint.ini").exists()
        try:
            has_black = (self.project_dir / "pyproject.toml").exists() and "black" in (
                self.project_dir / "pyproject.toml"
            ).read_text(encoding='utf-8', errors='ignore')
        except OSError:
            has_black = False

        if has_eslint or has_pylint or has_black:
            checks.append(QualityCheck(
                name="Linter",
                category="code_quality",
                description="代码静态检查工具",
                status=CheckStatus.PASSED,
                score=100,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="Linter 已配置",
            ))
        else:
            checks.append(QualityCheck(
                name="Linter",
                category="code_quality",
                description="代码静态检查工具",
                status=CheckStatus.WARNING,
                score=50,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="Linter 未配置",
            ))

        python_roots = self._discover_python_source_roots()
        if python_roots:
            python_exec = shutil.which("python3") or shutil.which("python")
            if python_exec:
                cmd = [python_exec, "-m", "compileall", "-q", *[str(p) for p in python_roots]]
                result = self._run_command(cmd, timeout=120)
                if result["timed_out"]:
                    checks.append(QualityCheck(
                        name="Python 语法检查",
                        category="code_quality",
                        description="compileall 语法检查",
                        status=CheckStatus.WARNING,
                        score=50,
                        weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                        details="compileall 执行超时",
                    ))
                elif result["returncode"] == 0:
                    checks.append(QualityCheck(
                        name="Python 语法检查",
                        category="code_quality",
                        description="compileall 语法检查",
                        status=CheckStatus.PASSED,
                        score=100,
                        weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                        details="Python 语法检查通过",
                    ))
                else:
                    checks.append(QualityCheck(
                        name="Python 语法检查",
                        category="code_quality",
                        description="compileall 语法检查",
                        status=CheckStatus.FAILED,
                        score=20,
                        weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                        details="Python 语法检查失败",
                    ))
            else:
                checks.append(QualityCheck(
                    name="Python 语法检查",
                    category="code_quality",
                    description="compileall 语法检查",
                    status=CheckStatus.WARNING,
                    score=50,
                    weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                    details="未找到 python 解释器，跳过语法检查",
                ))

        checks.append(self._check_pipeline_observability())
        checks.append(self._check_host_compatibility())
        checks.append(self._check_knowledge_governance())
        checks.append(self._check_launch_rehearsal())
        checks.append(self._check_rehearsal_verification_report())

        return checks

    def _check_pipeline_observability(self) -> QualityCheck:
        output_dir = self.project_dir / "output"
        metric_files = sorted(output_dir.glob("*-pipeline-metrics.json")) if output_dir.exists() else []
        if not metric_files:
            return QualityCheck(
                name="Pipeline 可观测性",
                category="code_quality",
                description="流水线指标报告",
                status=CheckStatus.WARNING,
                score=60 if self.is_zero_to_one else 50,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="未发现 output/*-pipeline-metrics.json",
            )

        latest = max(metric_files, key=lambda path: path.stat().st_mtime)
        try:
            payload = json.loads(latest.read_text(encoding="utf-8"))
        except Exception:
            return QualityCheck(
                name="Pipeline 可观测性",
                category="code_quality",
                description="流水线指标报告",
                status=CheckStatus.FAILED,
                score=30,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=f"指标文件不可解析: {latest.name}",
            )

        success = bool(payload.get("success", False))
        success_rate = float(payload.get("success_rate", 0))
        if success and success_rate >= 90:
            status = CheckStatus.PASSED
            score = 100
        elif success:
            status = CheckStatus.WARNING
            score = 80
        else:
            status = CheckStatus.FAILED
            score = 40

        return QualityCheck(
            name="Pipeline 可观测性",
            category="code_quality",
            description="流水线指标报告",
            status=status,
            score=score,
            weight=self.CHECKS_CONFIG["code_quality"]["weight"],
            details=f"{latest.name} | success_rate={success_rate:.1f}%",
        )

    def _check_host_compatibility(self) -> QualityCheck:
        min_score = float(self.host_compatibility_min_score)
        min_ready_hosts = self.host_compatibility_min_ready_hosts
        warning_threshold = max(40.0, min_score - 20.0)

        output_dir = self.project_dir / "output"
        reports = sorted(output_dir.glob("*-host-compatibility.json")) if output_dir.exists() else []
        if not reports:
            return QualityCheck(
                name="宿主兼容性",
                category="code_quality",
                description="AI Coding 宿主接入兼容性报告",
                status=CheckStatus.WARNING,
                score=70 if self.is_zero_to_one else 60,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=(
                    "未发现 output/*-host-compatibility.json "
                    f"(目标阈值: score>={min_score:.0f}, ready_hosts>={min_ready_hosts})"
                ),
            )

        latest = max(reports, key=lambda path: path.stat().st_mtime)
        try:
            payload = json.loads(latest.read_text(encoding="utf-8"))
        except Exception:
            return QualityCheck(
                name="宿主兼容性",
                category="code_quality",
                description="AI Coding 宿主接入兼容性报告",
                status=CheckStatus.FAILED,
                score=30,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=f"兼容性报告不可解析: {latest.name}",
            )

        compatibility = payload.get("compatibility", {}) if isinstance(payload, dict) else {}
        if not isinstance(compatibility, dict):
            return QualityCheck(
                name="宿主兼容性",
                category="code_quality",
                description="AI Coding 宿主接入兼容性报告",
                status=CheckStatus.FAILED,
                score=30,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=f"兼容性报告结构非法: {latest.name}",
            )

        try:
            overall_score = float(compatibility.get("overall_score", 0))
        except (TypeError, ValueError):
            overall_score = 0.0
        try:
            ready_hosts = int(compatibility.get("ready_hosts", 0))
        except (TypeError, ValueError):
            ready_hosts = 0
        try:
            total_hosts = int(compatibility.get("total_hosts", 0))
        except (TypeError, ValueError):
            total_hosts = 0

        bounded_score = max(0, min(100, int(round(overall_score))))
        details = (
            f"{latest.name} | overall={overall_score:.2f} | "
            f"ready={ready_hosts}/{total_hosts}"
        )

        profile = self._host_profile_metrics(compatibility)
        if profile is not None:
            overall_score = self._coerce_float(profile.get("overall_score"), default=0.0)
            ready_hosts = self._coerce_int(profile.get("ready_hosts"), default=0)
            total_hosts = self._coerce_int(profile.get("total_hosts"), default=0)
            bounded_score = self._coerce_int(profile.get("bounded_score"), default=0)
            details = (
                f"{latest.name} | profile={profile['label']} | overall={overall_score:.2f} | "
                f"ready={ready_hosts}/{total_hosts}"
            )

        if overall_score >= min_score and ready_hosts >= min_ready_hosts:
            return QualityCheck(
                name="宿主兼容性",
                category="code_quality",
                description="AI Coding 宿主接入兼容性报告",
                status=CheckStatus.PASSED,
                score=bounded_score,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=details,
            )

        if overall_score >= warning_threshold:
            return QualityCheck(
                name="宿主兼容性",
                category="code_quality",
                description="AI Coding 宿主接入兼容性报告",
                status=CheckStatus.WARNING,
                score=bounded_score,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=(
                    f"{details}（建议至少 {min_score:.0f} 分且 "
                    f"ready host >= {min_ready_hosts}）"
                ),
            )

        return QualityCheck(
            name="宿主兼容性",
            category="code_quality",
            description="AI Coding 宿主接入兼容性报告",
            status=CheckStatus.FAILED,
            score=max(20, bounded_score),
            weight=self.CHECKS_CONFIG["code_quality"]["weight"],
            details=f"{details}（低于最低建议阈值）",
        )

    def _host_profile_metrics(self, compatibility: dict[str, object]) -> HostProfileMetrics | None:
        if not self.host_profile_enforce_selected or not self.host_profile_targets:
            return None

        hosts_obj = compatibility.get("hosts", {})
        hosts = hosts_obj if isinstance(hosts_obj, dict) else {}
        selected = [item for item in self.host_profile_targets if item in hosts]
        if not selected:
            return {
                "label": ",".join(self.host_profile_targets),
                "overall_score": 0.0,
                "ready_hosts": 0,
                "total_hosts": len(self.host_profile_targets),
                "bounded_score": 0,
            }

        score_values: list[float] = []
        ready_hosts = 0
        for target in selected:
            host_data = hosts.get(target, {})
            if isinstance(host_data, dict):
                try:
                    score_values.append(float(host_data.get("score", 0.0)))
                except (TypeError, ValueError):
                    score_values.append(0.0)
                if bool(host_data.get("ready", False)):
                    ready_hosts += 1
            else:
                score_values.append(0.0)

        overall_score = sum(score_values) / len(score_values) if score_values else 0.0
        bounded_score = max(0, min(100, int(round(overall_score))))
        return {
            "label": ",".join(selected),
            "overall_score": overall_score,
            "ready_hosts": ready_hosts,
            "total_hosts": len(selected),
            "bounded_score": bounded_score,
        }

    def _check_knowledge_governance(self) -> QualityCheck:
        config_file = self.project_dir / "super-dev.yaml"
        config_domains: list[str] = []
        config_ttl = 1800
        if config_file.exists():
            try:
                raw_config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
                if isinstance(raw_config, dict):
                    domains_raw = raw_config.get("knowledge_allowed_domains", [])
                    if isinstance(domains_raw, list):
                        config_domains = [
                            str(item).strip().lower()
                            for item in domains_raw
                            if str(item).strip()
                        ]
                    ttl_raw = raw_config.get("knowledge_cache_ttl_seconds", 1800)
                    if isinstance(ttl_raw, int):
                        config_ttl = ttl_raw
                    elif isinstance(ttl_raw, str) and ttl_raw.strip().isdigit():
                        config_ttl = int(ttl_raw.strip())
            except Exception:
                pass

        cache_dir = self.project_dir / "output" / "knowledge-cache"
        bundles = sorted(cache_dir.glob("*-knowledge-bundle.json")) if cache_dir.exists() else []
        if not bundles:
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.WARNING,
                score=70 if self.is_zero_to_one else 60,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="未发现 output/knowledge-cache/*-knowledge-bundle.json",
            )

        latest = max(bundles, key=lambda path: path.stat().st_mtime)
        try:
            bundle = json.loads(latest.read_text(encoding="utf-8"))
        except Exception:
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.FAILED,
                score=30,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=f"知识缓存不可解析: {latest.name}",
            )
        if not isinstance(bundle, dict):
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.FAILED,
                score=30,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details=f"知识缓存结构非法: {latest.name}",
            )

        signature = str(bundle.get("cache_signature", "")).strip()
        if not signature:
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.FAILED,
                score=30,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="知识缓存缺少 cache_signature",
            )

        ttl_value = bundle.get("cache_ttl_seconds", config_ttl)
        bundle_ttl = ttl_value if isinstance(ttl_value, int) else config_ttl
        metadata = bundle.get("metadata", {})
        metadata_dict = metadata if isinstance(metadata, dict) else {}
        web_enabled = bool(metadata_dict.get("web_enabled", False))
        bundle_domains_raw = metadata_dict.get("allowed_web_domains", [])
        bundle_domains = (
            [
                str(item).strip().lower()
                for item in bundle_domains_raw
                if str(item).strip()
            ]
            if isinstance(bundle_domains_raw, list)
            else []
        )
        web_stats = metadata_dict.get("web_stats", {})
        filtered_out_count = 0
        if isinstance(web_stats, dict):
            raw_filtered = web_stats.get("filtered_out_count", 0)
            if isinstance(raw_filtered, int):
                filtered_out_count = raw_filtered

        if bundle_ttl <= 0:
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.WARNING,
                score=70,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="knowledge_cache_ttl_seconds <= 0，缓存治理策略关闭",
            )

        if web_enabled and not bundle_domains:
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.WARNING,
                score=75,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="联网知识未配置白名单域名",
            )

        config_domain_set = set(config_domains)
        bundle_domain_set = set(bundle_domains)
        if config_domain_set and bundle_domain_set and config_domain_set != bundle_domain_set:
            return QualityCheck(
                name="知识增强治理",
                category="code_quality",
                description="知识来源白名单与缓存可审计性",
                status=CheckStatus.WARNING,
                score=80,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="缓存白名单与项目配置不一致",
            )

        details = (
            f"{latest.name} | ttl={bundle_ttl}s | "
            f"domains={len(bundle_domains)} | filtered_out={filtered_out_count}"
        )
        return QualityCheck(
            name="知识增强治理",
            category="code_quality",
            description="知识来源白名单与缓存可审计性",
            status=CheckStatus.PASSED,
            score=100,
            weight=self.CHECKS_CONFIG["code_quality"]["weight"],
            details=details,
        )

    def _check_launch_rehearsal(self) -> QualityCheck:
        rehearsal_dir = self.project_dir / "output" / "rehearsal"
        required_patterns = [
            "*-launch-rehearsal.md",
            "*-rollback-playbook.md",
            "*-smoke-checklist.md",
        ]
        found = 0
        if rehearsal_dir.exists():
            for pattern in required_patterns:
                if any(rehearsal_dir.glob(pattern)):
                    found += 1

        if found == len(required_patterns):
            return QualityCheck(
                name="发布演练准备",
                category="code_quality",
                description="发布演练与回滚手册",
                status=CheckStatus.PASSED,
                score=100,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="发布演练文档齐全",
            )
        if found == 0:
            return QualityCheck(
                name="发布演练准备",
                category="code_quality",
                description="发布演练与回滚手册",
                status=CheckStatus.WARNING,
                score=60 if self.is_zero_to_one else 50,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="未发现 output/rehearsal/* 发布演练文档",
            )
        return QualityCheck(
            name="发布演练准备",
            category="code_quality",
            description="发布演练与回滚手册",
            status=CheckStatus.WARNING,
            score=75,
            weight=self.CHECKS_CONFIG["code_quality"]["weight"],
            details=f"发布演练文档不完整 ({found}/{len(required_patterns)})",
        )

    def _check_rehearsal_verification_report(self) -> QualityCheck:
        rehearsal_dir = self.project_dir / "output" / "rehearsal"
        if not rehearsal_dir.exists():
            return QualityCheck(
                name="发布演练验证报告",
                category="code_quality",
                description="发布演练验证结果",
                status=CheckStatus.WARNING,
                score=60 if self.is_zero_to_one else 50,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="未发现 output/rehearsal 目录",
            )

        has_md = any(rehearsal_dir.glob("*-rehearsal-report.md"))
        has_json = any(rehearsal_dir.glob("*-rehearsal-report.json"))
        if has_md and has_json:
            return QualityCheck(
                name="发布演练验证报告",
                category="code_quality",
                description="发布演练验证结果",
                status=CheckStatus.PASSED,
                score=100,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="已生成 rehearsal markdown + json 报告",
            )
        if has_md or has_json:
            return QualityCheck(
                name="发布演练验证报告",
                category="code_quality",
                description="发布演练验证结果",
                status=CheckStatus.WARNING,
                score=80,
                weight=self.CHECKS_CONFIG["code_quality"]["weight"],
                details="发布演练报告格式不完整（需同时包含 md 与 json）",
            )
        return QualityCheck(
            name="发布演练验证报告",
            category="code_quality",
            description="发布演练验证结果",
            status=CheckStatus.WARNING,
            score=70 if self.is_zero_to_one else 60,
            weight=self.CHECKS_CONFIG["code_quality"]["weight"],
            details="未发现 output/rehearsal/*-rehearsal-report.(md|json)",
        )

    def _calculate_total_score(self, checks: list[QualityCheck]) -> int:
        """计算总分"""
        if not checks:
            return 0

        return sum(c.score for c in checks) // len(checks)

    def _calculate_weighted_score(self, checks: list[QualityCheck]) -> float:
        """计算加权分"""
        if not checks:
            return 0.0

        total_weight = sum(c.weight for c in checks)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(c.score * c.weight for c in checks)
        return weighted_sum / total_weight

    def _generate_recommendations(self, checks: list[QualityCheck]) -> list[str]:
        """生成改进建议"""
        recommendations: list[str] = []

        fix_command_map = [
            ("PRD 文档", "运行 `super-dev run` 生成文档"),
            ("架构文档", "运行 `super-dev run` 生成文档"),
            ("UI/UX 文档", "运行 `super-dev run` 生成文档"),
            ("安全", "运行 `super-dev quality --type security` 查看详情"),
            ("测试", "运行 `pytest` 执行测试"),
            ("Spec 任务", "运行 `super-dev spec list` 查看任务状态"),
            ("宿主兼容性", "运行 `super-dev doctor --repair` 修复"),
            ("演练", "运行 `super-dev release readiness` 检查"),
            ("UI 质量", "运行 `super-dev review ui` 查看 UI 审查报告"),
        ]

        for check in checks:
            if check.status == CheckStatus.FAILED:
                prefix = "修复"
            elif check.status == CheckStatus.WARNING:
                prefix = "建议"
            else:
                continue

            description = check.description
            fix_hint = ""
            for keyword, command in fix_command_map:
                if keyword in description:
                    fix_hint = f" [修复: {command}]"
                    break

            recommendations.append(f"{prefix}: {description}{fix_hint}")

        return recommendations

    def _discover_python_tests(self) -> list[Path]:
        roots = [self.project_dir / "tests", self.project_dir / "backend" / "tests"]
        files: list[Path] = []
        for tests_dir in roots:
            if not tests_dir.exists():
                continue
            files.extend(list(tests_dir.rglob("test_*.py")))
            files.extend(list(tests_dir.rglob("*_test.py")))
        return files

    def _has_pytest_config(self) -> bool:
        if (self.project_dir / "pytest.ini").exists():
            return True

        setup_cfg = self.project_dir / "setup.cfg"
        if setup_cfg.exists():
            content = setup_cfg.read_text(encoding="utf-8", errors="ignore")
            if "[tool:pytest]" in content:
                return True

        tox_ini = self.project_dir / "tox.ini"
        if tox_ini.exists():
            content = tox_ini.read_text(encoding="utf-8", errors="ignore")
            if "[pytest]" in content:
                return True

        pyproject = self.project_dir / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            if "pytest.ini_options" in content:
                return True

        backend_pyproject = self.project_dir / "backend" / "pyproject.toml"
        if backend_pyproject.exists():
            content = backend_pyproject.read_text(encoding="utf-8", errors="ignore")
            if "pytest.ini_options" in content:
                return True

        return False

    def _discover_python_source_roots(self) -> list[Path]:
        roots: list[Path] = []
        candidates = [
            "super_dev", "src", "app", "backend", "server", "api", "services", "lib"
        ]
        for name in candidates:
            path = self.project_dir / name
            if path.exists() and path.is_dir():
                roots.append(path)

        top_level_py = list(self.project_dir.glob("*.py"))
        roots.extend(top_level_py)

        # 去重并限制数量，避免无界扫描
        unique: list[Path] = []
        seen = set()
        for path in roots:
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            unique.append(path)
        return unique[:8]

    def _discover_js_test_targets(self) -> list[Path]:
        targets: list[Path] = []
        for root in (self.project_dir, self.project_dir / "frontend", self.project_dir / "backend"):
            package_json = root / "package.json"
            if not package_json.exists():
                continue
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
            except Exception:
                continue
            scripts = data.get("scripts", {})
            test_script = str(scripts.get("test", "")).strip()
            if not test_script:
                continue
            if test_script == 'echo "Error: no test specified" && exit 1':
                continue
            targets.append(root)
        return targets

    def _has_js_test_script(self) -> bool:
        return bool(self._discover_js_test_targets())

    def _extract_test_summary(self, output: str) -> str:
        if not output:
            return ""
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        for line in reversed(lines):
            if "passed" in line or "failed" in line or "error" in line:
                return line[:240]
        return lines[-1][:240] if lines else ""

    def _read_coverage_percent(self) -> int | None:
        coverage_candidates = [
            self.project_dir / "coverage.xml",
            self.project_dir / "backend" / "coverage.xml",
            self.project_dir / "frontend" / "coverage.xml",
            self.project_dir / "coverage" / "cobertura-coverage.xml",
            self.project_dir / "frontend" / "coverage" / "cobertura-coverage.xml",
            self.project_dir / "backend" / "coverage" / "cobertura-coverage.xml",
        ]

        parsed_values: list[int] = []
        for coverage_xml in coverage_candidates:
            if not coverage_xml.exists():
                continue
            try:
                root = ElementTree.fromstring(coverage_xml.read_text(encoding="utf-8"))
                line_rate = root.attrib.get("line-rate")
                if line_rate is not None:
                    parsed_values.append(max(0, min(100, int(round(float(line_rate) * 100)))))
                    continue

                lines_covered = root.attrib.get("lines-covered")
                lines_valid = root.attrib.get("lines-valid")
                if lines_covered and lines_valid and float(lines_valid) > 0:
                    percent = (float(lines_covered) / float(lines_valid)) * 100
                    parsed_values.append(max(0, min(100, int(round(percent)))))
            except Exception:
                continue

        if not parsed_values:
            return None
        return max(parsed_values)

    def _run_command(self, cmd: list[str], timeout: int = 120) -> dict[str, object]:
        try:
            completed = subprocess.run(
                cmd,
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )  # nosec B603
            return {
                "returncode": completed.returncode,
                "stdout": completed.stdout or "",
                "stderr": completed.stderr or "",
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as e:
            return {
                "returncode": -1,
                "stdout": (e.stdout or ""),
                "stderr": (e.stderr or ""),
                "timed_out": True,
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "timed_out": False,
            }
