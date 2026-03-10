"""
Super Dev 项目分析器核心模块
"""

import ast
import os
from pathlib import Path

from .detectors import (
    detect_architecture_pattern,
    detect_project_type,
    detect_tech_stack,
)
from .models import (
    ArchitectureReport,
    Dependency,
    DesignPattern,
    PatternType,
    ProjectCategory,
)

# 类型别名，向后兼容
ProjectType = ProjectCategory


class ProjectAnalyzer:
    """
    项目分析器

    用于分析现有项目的结构、技术栈、架构模式和设计模式
    """

    def __init__(self, project_path: str | Path):
        """
        初始化分析器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise FileNotFoundError(f"项目不存在: {self.project_path}")

        self._report: ArchitectureReport | None = None
        self._ignored_dir_names = {
            "node_modules",
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "env",
            ".env",
            "dist",
            "build",
            "target",
            "bin",
            "obj",
            ".next",
            ".nuxt",
            "coverage",
            ".pytest_cache",
            "site-packages",
            "dist-packages",
        }

    def analyze(self) -> ArchitectureReport:
        """
        执行完整分析

        Returns:
            ArchitectureReport: 架构分析报告
        """
        # 检测项目类型
        category = detect_project_type(self.project_path)

        # 检测技术栈
        tech_stack = detect_tech_stack(self.project_path)

        # 检测架构模式
        architecture_pattern = detect_architecture_pattern(self.project_path)

        # 分析目录结构
        directory_structure = self._analyze_directory_structure()

        # 统计文件和代码行数
        file_count, total_lines, languages_used = self._count_files_and_lines()

        # 检测设计模式
        design_patterns = self._detect_design_patterns()

        self._report = ArchitectureReport(
            project_path=self.project_path,
            category=category,
            tech_stack=tech_stack,
            architecture_pattern=architecture_pattern,
            design_patterns=design_patterns,
            directory_structure=directory_structure,
            file_count=file_count,
            total_lines=total_lines,
            languages_used=languages_used,
        )

        return self._report

    def _analyze_directory_structure(self, max_depth: int = 3) -> dict:
        """
        分析目录结构

        Args:
            max_depth: 最大递归深度

        Returns:
            dict: 目录结构树
        """
        result = {}

        def _build_tree(path: Path, depth: int) -> dict | None:
            if depth > max_depth:
                return None

            tree: dict[str, dict | None] = {}
            try:
                for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                    if self._should_ignore_path(item):
                        continue

                    if item.is_dir():
                        subtree = _build_tree(item, depth + 1)
                        if subtree:
                            tree[item.name] = subtree
                    else:
                        # 只包含代码文件
                        if item.suffix in [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java"]:
                            tree[item.name] = None
            except PermissionError:
                pass

            return tree if tree else None

        top_tree = _build_tree(self.project_path, 0)
        if top_tree:
            result = top_tree

        return result

    def _count_files_and_lines(
        self,
    ) -> tuple[int, int, dict[str, int]]:
        """
        统计文件数量和代码行数

        Returns:
            tuple: (文件数量, 总行数, 各语言行数)
        """
        file_count = 0
        total_lines = 0
        languages_used: dict[str, int] = {}

        # 语言扩展名映射
        lang_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".jsx": "JavaScript",
            ".go": "Go",
            ".java": "Java",
            ".kt": "Kotlin",
            ".swift": "Swift",
            ".rb": "Ruby",
            ".php": "PHP",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".vue": "Vue",
            ".svelte": "Svelte",
        }

        for root, dirs, files in os.walk(self.project_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if not self._should_ignore_dir_name(d)]

            for file in files:
                suffix = Path(file).suffix

                if suffix not in lang_map:
                    continue

                file_path = Path(root) / file
                if self._should_ignore_path(file_path):
                    continue
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1

                        lang = lang_map[suffix]
                        languages_used[lang] = languages_used.get(lang, 0) + lines
                except (OSError, UnicodeDecodeError):
                    pass

        return file_count, total_lines, languages_used

    def _detect_design_patterns(self) -> list[DesignPattern]:
        """
        检测设计模式

        Returns:
            list[DesignPattern]: 检测到的设计模式列表
        """
        patterns: list[DesignPattern] = []

        # 根据语言选择检测策略
        if self.project_path.joinpath("package.json").exists():
            patterns.extend(self._detect_js_patterns())
        elif (
            self.project_path.joinpath("requirements.txt").exists()
            or self.project_path.joinpath("pyproject.toml").exists()
        ):
            patterns.extend(self._detect_python_patterns())

        return patterns

    def _detect_js_patterns(self) -> list[DesignPattern]:
        """检测 JavaScript/TypeScript 设计模式"""
        patterns: list[DesignPattern] = []

        src_dir = self.project_path / "src"
        if not src_dir.exists():
            src_dir = self.project_path

        # 遍历源文件
        for js_file in src_dir.rglob("*.js"):
            self._check_file_for_patterns(js_file, patterns, "javascript")

        for ts_file in src_dir.rglob("*.ts"):
            self._check_file_for_patterns(ts_file, patterns, "typescript")

        for tsx_file in src_dir.rglob("*.tsx"):
            self._check_file_for_patterns(tsx_file, patterns, "typescript")

        return patterns

    def _detect_python_patterns(self) -> list[DesignPattern]:
        """检测 Python 设计模式"""
        patterns: list[DesignPattern] = []

        for py_file in self.project_path.rglob("*.py"):
            if self._should_ignore_path(py_file):
                continue
            self._check_file_for_patterns(py_file, patterns, "python")

        return patterns

    def _should_ignore_dir_name(self, name: str) -> bool:
        return name in self._ignored_dir_names

    def _should_ignore_path(self, path: Path) -> bool:
        try:
            relative = path.resolve().relative_to(self.project_path)
            parts = relative.parts
        except Exception:
            parts = path.parts

        return any(
            part.startswith(".") or part in self._ignored_dir_names
            for part in parts
        )

    def _check_file_for_patterns(
        self, file_path: Path, patterns: list[DesignPattern], language: str
    ) -> None:
        """
        检查文件中的设计模式

        Args:
            file_path: 文件路径
            patterns: 模式列表（输出参数）
            language: 编程语言
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            if language == "python":
                self._detect_python_ast_patterns(file_path, patterns)
            else:
                self._detect_text_based_patterns(file_path, content, patterns)

        except (OSError, UnicodeDecodeError):
            pass

    def _detect_python_ast_patterns(
        self, file_path: Path, patterns: list[DesignPattern]
    ) -> None:
        """使用 AST 检测 Python 设计模式"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                # 检测 Singleton 模式
                if isinstance(node, ast.ClassDef):
                    self._check_singleton_class(node, file_path, patterns)

                # 检测 Observer 模式
                if isinstance(node, ast.FunctionDef):
                    self._check_observer_methods(node, file_path, patterns)

        except (OSError, SyntaxError):
            pass

    def _check_singleton_class(
        self, class_node: ast.ClassDef, file_path: Path, patterns: list[DesignPattern]
    ) -> None:
        """检查 Singleton 模式"""
        # 查找 _instance 属性
        has_instance = False
        has_get_instance = False

        for item in class_node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    if item.target.id == "_instance":
                        has_instance = True

            if isinstance(item, ast.FunctionDef):
                if item.name in ["__new__", "get_instance", "instance"]:
                    has_get_instance = True

        if has_instance or has_get_instance:
            patterns.append(
                DesignPattern(
                    name=PatternType.SINGLETON,
                    location=file_path,
                    description=f"类 {class_node.name} 实现了单例模式",
                )
            )

    def _check_observer_methods(
        self, func_node: ast.FunctionDef, file_path: Path, patterns: list[DesignPattern]
    ) -> None:
        """检查 Observer 模式相关方法"""
        observer_methods = ["attach", "detach", "notify", "subscribe", "unsubscribe"]

        if func_node.name in observer_methods:
            patterns.append(
                DesignPattern(
                    name=PatternType.OBSERVER,
                    location=file_path,
                    description=f"方法 {func_node.name} 可能是观察者模式的一部分",
                    confidence=0.7,
                )
            )

    def _detect_text_based_patterns(
        self, file_path: Path, content: str, patterns: list[DesignPattern]
    ) -> None:
        """基于文本检测设计模式（适用于 JS/TS 等）"""

        # Singleton 检测
        if "getInstance" in content or ("instance" in content and "private" in content):
            patterns.append(
                DesignPattern(
                    name=PatternType.SINGLETON,
                    location=file_path,
                    description="检测到单例模式相关代码",
                    confidence=0.6,
                )
            )

        # Factory 检测
        if "create" in content and ("Factory" in content or "factory" in content):
            patterns.append(
                DesignPattern(
                    name=PatternType.FACTORY,
                    location=file_path,
                    description="检测到工厂模式相关代码",
                    confidence=0.7,
                )
            )

        # Observer 检测
        observer_keywords = ["subscribe", "unsubscribe", "notify", "emit", "addEventListener"]
        if any(keyword in content for keyword in observer_keywords):
            patterns.append(
                DesignPattern(
                    name=PatternType.OBSERVER,
                    location=file_path,
                    description="检测到观察者模式相关代码",
                    confidence=0.6,
                )
            )

        # Strategy 检测
        if "Strategy" in content or ("execute" in content and "context" in content):
            patterns.append(
                DesignPattern(
                    name=PatternType.STRATEGY,
                    location=file_path,
                    description="检测到策略模式相关代码",
                    confidence=0.6,
                )
            )

    def get_summary(self) -> str:
        """
        获取项目摘要

        Returns:
            str: 项目摘要文本
        """
        if self._report is None:
            self.analyze()

        if self._report is None:
            raise RuntimeError("analyze() did not produce a report")

        lines = [
            f"项目类型: {self._report.category.value}",
            f"编程语言: {self._report.tech_stack.language}",
            f"框架: {self._report.tech_stack.framework.value if hasattr(self._report.tech_stack.framework, 'value') else self._report.tech_stack.framework}",
            f"文件数量: {self._report.file_count}",
            f"代码行数: {self._report.total_lines:,}",
        ]

        if self._report.architecture_pattern:
            lines.append(f"架构模式: {self._report.architecture_pattern.value}")

        return "\n".join(lines)

    def get_dependencies(self) -> list[Dependency]:
        """
        获取项目依赖列表

        Returns:
            list[Dependency]: 依赖列表
        """
        if self._report is None:
            self.analyze()

        if self._report is None:
            raise RuntimeError("analyze() did not produce a report")
        return self._report.tech_stack.dependencies

    def get_language_distribution(self) -> dict[str, float]:
        """
        获取语言分布百分比

        Returns:
            dict[str, float]: 语言 -> 百分比
        """
        if self._report is None:
            self.analyze()

        if self._report is None:
            raise RuntimeError("analyze() did not produce a report")

        total = self._report.total_lines
        if total == 0:
            return {}

        return {
            lang: (count / total) * 100
            for lang, count in self._report.languages_used.items()
        }
