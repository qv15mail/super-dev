# -*- coding: utf-8 -*-
"""
红队审查器 - 安全、性能、架构审查

开发：Excellent（11964948@qq.com）
功能：模拟红队视角，全面审查项目安全性、性能和架构
作用：在开发前发现问题，确保质量
创建时间：2025-12-30
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import os
import re


@dataclass
class SecurityIssue:
    """安全问题"""
    severity: str  # critical, high, medium, low
    category: str  # injection, auth, xss, csrf, etc.
    description: str
    recommendation: str
    cwe: Optional[str] = None
    file_path: Optional[str] = None
    line: Optional[int] = None


@dataclass
class PerformanceIssue:
    """性能问题"""
    severity: str  # critical, high, medium, low
    category: str  # database, api, frontend, infrastructure
    description: str
    recommendation: str
    impact: str = ""
    file_path: Optional[str] = None
    line: Optional[int] = None


@dataclass
class ArchitectureIssue:
    """架构问题"""
    severity: str  # critical, high, medium, low
    category: str  # scalability, maintainability, reliability
    description: str
    recommendation: str
    adr_needed: bool = False
    file_path: Optional[str] = None
    line: Optional[int] = None


@dataclass
class RedTeamReport:
    """红队审查报告"""
    project_name: str
    security_issues: list[SecurityIssue] = field(default_factory=list)
    performance_issues: list[PerformanceIssue] = field(default_factory=list)
    architecture_issues: list[ArchitectureIssue] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return (
            sum(1 for i in self.security_issues if i.severity == "critical") +
            sum(1 for i in self.performance_issues if i.severity == "critical") +
            sum(1 for i in self.architecture_issues if i.severity == "critical")
        )

    @property
    def high_count(self) -> int:
        return (
            sum(1 for i in self.security_issues if i.severity == "high") +
            sum(1 for i in self.performance_issues if i.severity == "high") +
            sum(1 for i in self.architecture_issues if i.severity == "high")
        )

    @property
    def total_score(self) -> int:
        """计算总分 (0-100)"""
        base_score = 100

        # 扣分标准
        for issue in self.security_issues:
            if issue.severity == "critical":
                base_score -= 20
            elif issue.severity == "high":
                base_score -= 10
            elif issue.severity == "medium":
                base_score -= 5
            else:
                base_score -= 2

        for issue in self.performance_issues:
            if issue.severity == "critical":
                base_score -= 15
            elif issue.severity == "high":
                base_score -= 8
            elif issue.severity == "medium":
                base_score -= 4
            else:
                base_score -= 1

        for issue in self.architecture_issues:
            if issue.severity == "critical":
                base_score -= 15
            elif issue.severity == "high":
                base_score -= 8
            elif issue.severity == "medium":
                base_score -= 4
            else:
                base_score -= 1

        return max(0, base_score)

    def to_markdown(self) -> str:
        """生成 Markdown 报告"""
        lines = [
            f"# {self.project_name} - 红队审查报告",
            "",
            f"> **审查时间**: 自动生成",
            f"> **总分**: {self.total_score}/100",
            "",
            "---",
            "",
            "## 执行摘要",
            "",
            f"- **Critical 问题**: {self.critical_count}",
            f"- **High 问题**: {self.high_count}",
            f"- **总分**: {self.total_score}/100",
            "",
        ]

        if self.total_score < 60:
            lines.append("**状态**: 未通过质量门禁 - 需要修复关键问题后重新审查")
        elif self.total_score < 80:
            lines.append("**状态**: 有条件通过 - 建议修复 High 级别问题")
        else:
            lines.append("**状态**: 通过 - 质量良好")

        lines.extend(["", "---", ""])

        # 安全审查
        lines.extend([
            "## 1. 安全审查",
            "",
        ])

        if not self.security_issues:
            lines.append("未发现明显的安全问题。")
        else:
            lines.append("| 严重性 | 类别 | 描述 | 建议 |")
            lines.append("|:---|:---|:---|:---|")
            for issue in self.security_issues:
                cwe_ref = f" ({issue.cwe})" if issue.cwe else ""
                lines.append(
                    f"| {issue.severity} | {issue.category}{cwe_ref} | {issue.description} | {issue.recommendation} |"
                )

        lines.extend(["", "---", ""])

        # 性能审查
        lines.extend([
            "## 2. 性能审查",
            "",
        ])

        if not self.performance_issues:
            lines.append("未发现明显的性能问题。")
        else:
            lines.append("| 严重性 | 类别 | 描述 | 影响 | 建议 |")
            lines.append("|:---|:---|:---|:---|:---|")
            for issue in self.performance_issues:
                lines.append(
                    f"| {issue.severity} | {issue.category} | {issue.description} | {issue.impact} | {issue.recommendation} |"
                )

        lines.extend(["", "---", ""])

        # 架构审查
        lines.extend([
            "## 3. 架构审查",
            "",
        ])

        if not self.architecture_issues:
            lines.append("未发现明显的架构问题。")
        else:
            lines.append("| 严重性 | 类别 | 描述 | 需要 ADR | 建议 |")
            lines.append("|:---|:---|:---|:---:|:---|")
            for issue in self.architecture_issues:
                adr = "是" if issue.adr_needed else "否"
                lines.append(
                    f"| {issue.severity} | {issue.category} | {issue.description} | {adr} | {issue.recommendation} |"
                )

        lines.extend(["", "---", ""])

        # 改进建议
        lines.extend([
            "## 4. 改进建议",
            "",
            "### 优先级 P0 (立即修复)",
            "",
        ])

        p0_issues = [
            i for i in self.security_issues + self.performance_issues + self.architecture_issues
            if i.severity in ("critical", "high")
        ]

        if not p0_issues:
            lines.append("无 P0 级别问题。")
        else:
            for idx, issue in enumerate(p0_issues, 1):
                issue_type = "安全" if issue in self.security_issues else "性能" if issue in self.performance_issues else "架构"
                lines.append(f"{idx}. [{issue_type}] {issue.description}")
                lines.append(f"   - 建议: {issue.recommendation}")
                lines.append("")

        lines.extend([
            "### 优先级 P1 (尽快修复)",
            "",
        ])

        p1_issues = [
            i for i in self.security_issues + self.performance_issues + self.architecture_issues
            if i.severity == "medium"
        ]

        if not p1_issues:
            lines.append("无 P1 级别问题。")
        else:
            for idx, issue in enumerate(p1_issues, 1):
                issue_type = "安全" if issue in self.security_issues else "性能" if issue in self.performance_issues else "架构"
                lines.append(f"{idx}. [{issue_type}] {issue.description}")
                lines.append(f"   - 建议: {issue.recommendation}")
                lines.append("")

        return "\n".join(lines)


class RedTeamReviewer:
    """红队审查器"""

    _CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".sql"}
    _SKIP_DIRS = {
        ".git", ".idea", ".vscode", "node_modules", "__pycache__", ".pytest_cache",
        ".mypy_cache", ".ruff_cache", "dist", "build", "output", ".super-dev", "logs",
        ".venv", "venv", ".tox", ".cache", "coverage", "htmlcov", ".next", ".nuxt",
    }
    _PREFERRED_SCAN_DIRS = (
        "backend", "frontend", "src", "app", "server", "api", "services", "lib", "super_dev"
    )
    _MAX_SCAN_FILES = 220
    _MAX_FILE_SIZE = 300_000

    def __init__(self, project_dir: Path, name: str, tech_stack: dict):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack
        self.platform = tech_stack.get("platform", "web")
        self.frontend = tech_stack.get("frontend", "react")
        self.backend = tech_stack.get("backend", "node")
        self.domain = tech_stack.get("domain", "")
        self._source_file_cache: Optional[list[tuple[Path, str]]] = None

    def review(self) -> RedTeamReport:
        """执行完整红队审查"""
        report = RedTeamReport(project_name=self.name)

        # 安全审查
        report.security_issues = self._review_security()

        # 性能审查
        report.performance_issues = self._review_performance()

        # 架构审查
        report.architecture_issues = self._review_architecture()

        return report

    def _review_security(self) -> list[SecurityIssue]:
        """安全审查"""
        issues: list[SecurityIssue] = []
        issue_keys: set[tuple[str, str]] = set()

        # 1) 扫描代码中的高风险模式（真实信号）
        secret_pattern = re.compile(
            r'(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*["\']([^"\']{6,})["\']'
        )
        dangerous_rules = [
            ("命令执行", re.compile(r"\bsubprocess\.(run|call|Popen)\([^)]*shell\s*=\s*True"), "CWE-78",
             "避免 shell=True，改为参数数组执行并进行输入白名单校验"),
            ("动态执行", re.compile(r"\b(eval|exec)\s*\("), "CWE-95",
             "避免 eval/exec，使用安全解析器或受限表达式引擎"),
            ("动态命令", re.compile(r"child_process\.exec\s*\("), "CWE-78",
             "改用 execFile/spawn 并限定允许命令集合"),
            ("SQL 注入", re.compile(r'(?i)(select|insert|update|delete)[^\n]{0,120}\+'), "CWE-89",
             "避免字符串拼接 SQL，统一使用参数化查询/ORM"),
        ]

        for file_path, content in self._iter_source_files_with_content():
            if self._is_yaml_file(file_path):
                # 对配置文件只做轻量提示，不做高危判定
                continue

            # 硬编码凭据
            for match in secret_pattern.finditer(content):
                value = match.group(2).strip()
                if self._looks_like_placeholder(value):
                    continue
                line_no = self._line_number_from_offset(content, match.start())
                issue_key = (str(file_path), "硬编码凭据")
                if issue_key in issue_keys:
                    continue
                issue_keys.add(issue_key)
                issues.append(SecurityIssue(
                    severity="high",
                    category="硬编码凭据",
                    description=f"检测到疑似硬编码敏感信息: {file_path.name}:{line_no}",
                    recommendation="将密钥迁移到环境变量或密钥管理服务（Vault/KMS）",
                    cwe="CWE-798",
                    file_path=str(file_path),
                    line=line_no,
                ))
                break

            for category, pattern, cwe, recommendation in dangerous_rules:
                match = pattern.search(content)
                if not match:
                    continue
                issue_key = (str(file_path), category)
                if issue_key in issue_keys:
                    continue
                issue_keys.add(issue_key)
                line_no = self._line_number_from_offset(content, match.start())
                issues.append(SecurityIssue(
                    severity="high",
                    category=category,
                    description=f"检测到高风险代码模式: {file_path.name}:{line_no}",
                    recommendation=recommendation,
                    cwe=cwe,
                    file_path=str(file_path),
                    line=line_no,
                ))

        # 2) 框架级最低安全基线（中低风险建议）
        if self.backend != "none":
            issues.append(SecurityIssue(
                severity="medium",
                category="认证",
                description="建议统一鉴权中间件并对关键接口做细粒度权限控制",
                recommendation="采用 JWT/Session + RBAC/ABAC，补充关键操作审计日志",
                cwe="CWE-287",
            ))
            issues.append(SecurityIssue(
                severity="medium",
                category="速率限制",
                description="建议对登录、注册、重置密码等敏感接口启用限流",
                recommendation="采用令牌桶/滑动窗口算法并记录触发日志",
                cwe="CWE-770",
            ))

        # 领域特定安全
        if self.domain == "fintech":
            issues.extend([
                SecurityIssue(
                    severity="high",
                    category="PCI-DSS",
                    description="金融场景需完成支付数据合规评估与密钥分级管理",
                    recommendation="补充 PCI-DSS 控制项自检并输出合规矩阵",
                    cwe="CWE-320"
                ),
                SecurityIssue(
                    severity="high",
                    category="审计",
                    description="金融核心流程建议实施不可篡改审计链路",
                    recommendation="关键交易日志上链或做 WORM 存储并定期核验",
                    cwe="CWE-778"
                ),
            ])
        elif self.domain == "medical":
            issues.extend([
                SecurityIssue(
                    severity="high",
                    category="HIPAA",
                    description="医疗数据必须符合 HIPAA 标准",
                    recommendation="实施数据加密、访问控制、审计日志",
                    cwe="CWE-200"
                ),
            ])

        return issues

    def _review_performance(self) -> list[PerformanceIssue]:
        """性能审查"""
        issues: list[PerformanceIssue] = []
        issue_keys: set[tuple[str, str]] = set()

        async_requests_pattern = re.compile(r"async\s+def[\s\S]{0,300}requests\.(get|post|put|delete)\(")
        n_plus_one_pattern = re.compile(r"for\s+.+:\s*[\r\n]+\s*.+\.(find|get|query|select)\(")

        for file_path, content in self._iter_source_files_with_content():
            line_count = content.count("\n") + 1

            async_match = async_requests_pattern.search(content)
            if async_match and (str(file_path), "API") not in issue_keys:
                issue_keys.add((str(file_path), "API"))
                line_no = self._line_number_from_offset(content, async_match.start())
                issues.append(PerformanceIssue(
                    severity="high",
                    category="API",
                    description=f"异步上下文中检测到同步 HTTP 调用: {file_path.name}:{line_no}",
                    recommendation="在 async 流程中使用异步 HTTP 客户端（httpx.AsyncClient/aiohttp）",
                    impact="阻塞事件循环，增加高并发下请求延迟",
                    file_path=str(file_path),
                    line=line_no,
                ))

            n_plus_one_match = n_plus_one_pattern.search(content)
            if n_plus_one_match and (str(file_path), "数据库") not in issue_keys:
                issue_keys.add((str(file_path), "数据库"))
                line_no = self._line_number_from_offset(content, n_plus_one_match.start())
                issues.append(PerformanceIssue(
                    severity="medium",
                    category="数据库",
                    description=f"疑似 N+1 查询模式: {file_path.name}:{line_no}",
                    recommendation="批量查询或预加载关联数据，减少循环内 DB 调用",
                    impact="高数据量场景响应时间线性恶化",
                    file_path=str(file_path),
                    line=line_no,
                ))

            if line_count > 1200:
                issues.append(PerformanceIssue(
                    severity="medium",
                    category="代码结构",
                    description=f"超大文件可能影响维护与性能优化: {file_path.name} ({line_count} 行)",
                    recommendation="拆分模块并隔离热点路径，便于单点性能调优",
                    impact="性能问题定位与重构成本升高",
                ))

        # 基线建议
        if self.backend != "none":
            issues.append(PerformanceIssue(
                severity="medium",
                category="数据库",
                description="建议关键查询路径补齐索引与慢查询观测",
                recommendation="建立慢查询阈值与索引基线，持续回归",
                impact="降低接口尾延迟并提升吞吐稳定性",
            ))
        if self.frontend != "none":
            issues.append(PerformanceIssue(
                severity="medium",
                category="前端",
                description="建议实施代码分割与静态资源缓存策略",
                recommendation="按路由拆包并配置长期缓存 + 指纹文件名",
                impact="首屏加载与重复访问体验提升",
            ))

        return issues

    def _review_architecture(self) -> list[ArchitectureIssue]:
        """架构审查"""
        issues: list[ArchitectureIssue] = []
        source_files = self._iter_source_files_with_content()

        tests_dir = self.project_dir / "tests"
        if not tests_dir.exists():
            issues.append(ArchitectureIssue(
                severity="high",
                category="可维护性",
                description="未检测到 tests 目录，回归保障不足",
                recommendation="建立单元/集成测试目录并纳入 CI 必跑策略",
                adr_needed=False,
            ))

        has_health_endpoint = False
        for _file_path, content in source_files:
            if re.search(r"/health|health_check|healthcheck", content, re.IGNORECASE):
                has_health_endpoint = True
                break

        if self.backend != "none" and not has_health_endpoint:
            issues.append(ArchitectureIssue(
                severity="medium",
                category="可靠性",
                description="未检测到健康检查端点标记",
                recommendation="增加 /health 与 /ready 端点并接入部署探针",
                adr_needed=False,
            ))

        ci_files = [
            self.project_dir / ".github" / "workflows" / "ci.yml",
            self.project_dir / ".gitlab-ci.yml",
            self.project_dir / "Jenkinsfile",
            self.project_dir / ".azure-pipelines.yml",
            self.project_dir / "bitbucket-pipelines.yml",
        ]
        if not any(p.exists() for p in ci_files):
            issues.append(ArchitectureIssue(
                severity="medium",
                category="工程化",
                description="未检测到 CI/CD 主流程配置",
                recommendation="补齐至少一套 CI 流水线并将质量门禁前置",
                adr_needed=True,
            ))

        largest_file = None
        largest_lines = 0
        for file_path, content in source_files:
            line_count = content.count("\n") + 1
            if line_count > largest_lines:
                largest_file = file_path
                largest_lines = line_count
        if largest_file and largest_lines > 2000:
            issues.append(ArchitectureIssue(
                severity="high",
                category="可维护性",
                description=f"检测到超大单体文件: {largest_file.name} ({largest_lines} 行)",
                recommendation="按业务边界拆分模块并定义明确接口契约",
                adr_needed=True,
                file_path=str(largest_file),
                line=1,
            ))
        elif largest_file and largest_lines > 1200:
            issues.append(ArchitectureIssue(
                severity="medium",
                category="可维护性",
                description=f"检测到大文件: {largest_file.name} ({largest_lines} 行)",
                recommendation="逐步拆分高复杂度模块并补充针对性测试",
                adr_needed=True,
                file_path=str(largest_file),
                line=1,
            ))

        return issues

    def _iter_source_files_with_content(self) -> list[tuple[Path, str]]:
        if self._source_file_cache is not None:
            return self._source_file_cache

        files: list[tuple[Path, str]] = []
        seen: set[Path] = set()

        # 优先扫描常见源码目录，保证信噪比
        for root_name in self._PREFERRED_SCAN_DIRS:
            root = self.project_dir / root_name
            if not root.exists() or not root.is_dir():
                continue
            self._collect_scannable_files(root, files, seen)
            if len(files) >= self._MAX_SCAN_FILES:
                self._source_file_cache = files
                return files

        # 回退到全项目扫描，避免目录命名不标准导致漏检
        if len(files) < self._MAX_SCAN_FILES:
            self._collect_scannable_files(self.project_dir, files, seen)

        self._source_file_cache = files
        return files

    def _collect_scannable_files(
        self, root: Path, files: list[tuple[Path, str]], seen: set[Path]
    ) -> None:
        for dirpath, dirnames, filenames in os.walk(root):
            # 预剪枝，避免进入大型依赖目录
            dirnames[:] = [d for d in dirnames if not self._should_skip_dir(d)]

            for filename in filenames:
                if len(files) >= self._MAX_SCAN_FILES:
                    return

                path = Path(dirpath) / filename
                if not self._is_scannable_file(path):
                    continue

                try:
                    resolved = path.resolve()
                except Exception:
                    continue
                if resolved in seen:
                    continue
                seen.add(resolved)

                try:
                    if path.stat().st_size > self._MAX_FILE_SIZE:
                        continue
                except OSError:
                    continue

                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                files.append((path, content))

    def _should_skip_dir(self, dirname: str) -> bool:
        if dirname in self._SKIP_DIRS:
            return True
        return dirname.startswith(".") and dirname not in {".github"}

    def _is_scannable_file(self, path: Path) -> bool:
        suffix = path.suffix.lower()
        return suffix in self._CODE_EXTENSIONS or self._is_yaml_file(path)

    def _is_yaml_file(self, path: Path) -> bool:
        return path.suffix.lower() in {".yml", ".yaml"}

    def _looks_like_placeholder(self, value: str) -> bool:
        lowered = value.lower()
        placeholder_markers = (
            "your-", "example", "placeholder", "changeme", "<value>", "*****", "dummy"
        )
        if any(marker in lowered for marker in placeholder_markers):
            return True
        if lowered in {"password", "secret", "token", "api_key"}:
            return True
        return False

    def _line_number_from_offset(self, content: str, start: int) -> int:
        return content.count("\n", 0, start) + 1
