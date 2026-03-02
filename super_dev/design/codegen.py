"""
开发：Excellent（11964948@qq.com）
功能：代码片段生成器
作用：基于设计系统生成多框架的 UI 组件代码片段
创建时间：2025-01-04
最后修改：2025-01-04
"""

import csv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .generator import DesignSystem


class Framework(str, Enum):
    """支持的框架"""
    NEXTJS = "nextjs"
    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    HTML = "html"
    TAILWIND = "tailwind"


class ComponentCategory(str, Enum):
    """组件类别"""
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    MODAL = "modal"
    NAVIGATION = "navigation"
    FORM = "form"
    FEEDBACK = "feedback"
    LAYOUT = "layout"
    TYPOGRAPHY = "typography"
    DATA_DISPLAY = "data_display"


@dataclass
class ComponentSnippet:
    """组件代码片段"""
    name: str
    category: ComponentCategory
    framework: Framework
    code: str
    dependencies: list[str]
    props: dict[str, str]
    preview: str
    description: str


@dataclass
class GeneratedComponent:
    """生成的组件"""
    code: str
    imports: list[str]
    styles: str
    dependencies: list[str]
    description: str
    usage_example: str


class CodeGenerator:
    """代码生成器"""

    def __init__(self, data_dir: Path | None = None):
        """
        初始化代码生成器

        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "design"

        self.data_dir = Path(data_dir)
        self.snippets: list[ComponentSnippet] = []
        self._load_snippets()

    def _load_snippets(self):
        """加载组件片段数据"""
        csv_path = self.data_dir / "components.csv"

        if not csv_path.exists():
            self.snippets = self._get_default_snippets()
            return

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    snippet = ComponentSnippet(
                        name=row["name"],
                        category=ComponentCategory(row["category"]),
                        framework=Framework(row["framework"]),
                        code=row["code"],
                        dependencies=row["dependencies"].split(";"),
                        props=self._parse_props(row["props"]),
                        preview=row.get("preview", ""),
                        description=row.get("description", "")
                    )
                    self.snippets.append(snippet)
                except Exception as e:
                    print(f"Warning: Failed to parse snippet: {e}")

    def _parse_props(self, props_str: str) -> dict[str, str]:
        """解析 props 字符串"""
        props = {}
        for item in props_str.split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                props[key.strip()] = value.strip()
        return props

    def _get_default_snippets(self) -> list[ComponentSnippet]:
        """获取默认组件片段"""
        return [
            ComponentSnippet(
                name="Button",
                category=ComponentCategory.BUTTON,
                framework=Framework.REACT,
                code="import React from 'react'\n\ninterface ButtonProps {\n  children: React.ReactNode\n  onClick?: () => void\n  variant?: 'primary' | 'secondary'\n  size?: 'sm' | 'md' | 'lg'\n}\n\nexport const Button: React.FC<ButtonProps> = ({\n  children,\n  onClick,\n  variant = 'primary',\n  size = 'md'\n}) => {\n  const baseStyles = 'rounded-lg font-medium transition-colors'\n  const variants = {\n    primary: 'bg-blue-500 hover:bg-blue-600 text-white',\n    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800'\n  }\n  const sizes = {\n    sm: 'px-3 py-1.5 text-sm',\n    md: 'px-4 py-2 text-base',\n    lg: 'px-6 py-3 text-lg'\n  }\n\n  return (\n    <button\n      onClick={onClick}\n      className={`${baseStyles} ${variants[variant]} ${sizes[size]}`}\n    >\n      {children}\n    </button>\n  )\n}",
                dependencies=["react"],
                props={"children": "React.ReactNode", "onClick": "() => void", "variant": "'primary' | 'secondary'", "size": "'sm' | 'md' | 'lg'"},
                preview="<Button variant=\"primary\" size=\"md\">Click me</Button>",
                description="A versatile button component with multiple variants and sizes"
            ),
            ComponentSnippet(
                name="Card",
                category=ComponentCategory.CARD,
                framework=Framework.REACT,
                code="import React from 'react'\n\ninterface CardProps {\n  children: React.ReactNode\n  title?: string\n  footer?: React.ReactNode\n}\n\nexport const Card: React.FC<CardProps> = ({ children, title, footer }) => {\n  return (\n    <div className=\"bg-white rounded-lg shadow-md overflow-hidden\">\n      {title && (\n        <div className=\"px-6 py-4 border-b border-gray-200\">\n          <h3 className=\"text-lg font-semibold text-gray-900\">{title}</h3>\n        </div>\n      )}\n      <div className=\"px-6 py-4\">\n        {children}\n      </div>\n      {footer && (\n        <div className=\"px-6 py-4 bg-gray-50 border-t border-gray-200\">\n          {footer}\n        </div>\n      )}\n    </div>\n  )\n}",
                dependencies=["react"],
                props={"children": "React.ReactNode", "title": "string", "footer": "React.ReactNode"},
                preview="<Card title=\"Card Title\">Card content</Card>",
                description="A card component with optional header and footer"
            ),
            ComponentSnippet(
                name="Input",
                category=ComponentCategory.INPUT,
                framework=Framework.REACT,
                code="import React from 'react'\n\ninterface InputProps {\n  type?: 'text' | 'email' | 'password' | 'number'\n  placeholder?: string\n  value: string\n  onChange: (value: string) => void\n  label?: string\n  error?: string\n}\n\nexport const Input: React.FC<InputProps> = ({\n  type = 'text',\n  placeholder,\n  value,\n  onChange,\n  label,\n  error\n}) => {\n  return (\n    <div className=\"w-full\">\n      {label && (\n        <label className=\"block text-sm font-medium text-gray-700 mb-1\">\n          {label}\n        </label>\n      )}\n      <input\n        type={type}\n        placeholder={placeholder}\n        value={value}\n        onChange={(e) => onChange(e.target.value)}\n        className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${\n          error\n            ? 'border-red-500 focus:ring-red-500'\n            : 'border-gray-300 focus:ring-blue-500'\n        }`}\n      />\n      {error && (\n        <p className=\"mt-1 text-sm text-red-600\">{error}</p>\n      )}\n    </div>\n  )\n}",
                dependencies=["react"],
                props={"type": "'text' | 'email' | 'password' | 'number'", "placeholder": "string", "value": "string", "onChange": "(value: string) => void", "label": "string", "error": "string"},
                preview="<Input label=\"Email\" value=\"\" onChange={() => {}} />",
                description="A text input with label and error handling"
            )
        ]

    def search_components(
        self,
        query: str,
        framework: str | None = None,
        category: str | None = None
    ) -> list[ComponentSnippet]:
        """
        搜索组件片段

        Args:
            query: 搜索查询
            framework: 框架过滤
            category: 类别过滤

        Returns:
            组件片段列表
        """
        query_lower = query.lower()
        results = []

        for snippet in self.snippets:
            # 框架过滤
            if framework and snippet.framework.value != framework.lower():
                continue

            # 类别过滤
            if category and snippet.category.value != category.lower():
                continue

            # 搜索匹配
            score = 0
            if query_lower in snippet.name.lower():
                score += 10
            if query_lower in snippet.description.lower():
                score += 5
            if query_lower in snippet.category.value:
                score += 3

            if score > 0:
                results.append((snippet, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results]

    def generate_component(
        self,
        component_name: str,
        framework: Framework,
        design_system: DesignSystem | None = None
    ) -> GeneratedComponent | None:
        """
        生成组件代码

        Args:
            component_name: 组件名称
            framework: 目标框架
            design_system: 设计系统（可选）

        Returns:
            生成的组件
        """
        # 查找组件片段
        snippet = None
        for s in self.snippets:
            if s.name.lower() == component_name.lower() and s.framework == framework:
                snippet = s
                break

        if not snippet:
            return None

        # 如果提供了设计系统，应用设计 tokens
        code = snippet.code
        if design_system:
            code = self._apply_design_tokens(code, design_system, framework)

        return GeneratedComponent(
            code=code,
            imports=self._extract_imports(code, framework),
            styles=self._extract_styles(code, framework),
            dependencies=snippet.dependencies,
            description=snippet.description,
            usage_example=snippet.preview
        )

    def generate_from_design_system(
        self,
        design_system: DesignSystem,
        framework: Framework
    ) -> dict[str, GeneratedComponent]:
        """
        从设计系统生成组件

        Args:
            design_system: 设计系统
            framework: 目标框架

        Returns:
            生成的组件字典
        """
        components = {}

        # 为设计系统生成核心组件
        for category in ComponentCategory:
            # 查找该类别的组件
            category_snippets = [
                s for s in self.snippets
                if s.category == category and s.framework == framework
            ]

            for snippet in category_snippets:
                component = self.generate_component(
                    snippet.name,
                    framework,
                    design_system
                )
                if component:
                    components[snippet.name] = component

        return components

    def _apply_design_tokens(
        self,
        code: str,
        design_system: DesignSystem,
        framework: Framework
    ) -> str:
        """应用设计 tokens 到代码"""
        # 提取颜色值
        colors = design_system.colors
        if colors:
            # 替换颜色值
            primary = colors.get("primary", "#000000")
            secondary = colors.get("secondary", "#666666")

            # 简化示例：实际应该更智能地替换
            if framework == Framework.TAILWIND:
                # 生成 Tailwind 配置建议
                code = f"/* Apply these colors in tailwind.config.js:\n * primary: '{primary}'\n * secondary: '{secondary}'\n */\n\n{code}"
            elif framework in [Framework.REACT, Framework.NEXTJS]:
                # 添加 CSS 变量注释
                code = f"/* Use these CSS variables:\n * --color-primary: {primary}\n * --color-secondary: {secondary}\n */\n\n{code}"

        return code

    def _extract_imports(self, code: str, framework: Framework) -> list[str]:
        """提取 import 语句"""
        imports = []
        for line in code.split('\n'):
            if line.strip().startswith('import '):
                imports.append(line.strip())
        return imports

    def _extract_styles(self, code: str, framework: Framework) -> str:
        """提取样式代码"""
        if framework in [Framework.REACT, Framework.NEXTJS, Framework.TAILWIND]:
            # Tailwind 类名
            import re
            matches = re.findall(r'className="([^"]+)"', code)
            return "\n".join(matches)
        return ""

    def get_available_components(
        self,
        framework: Framework | None = None
    ) -> dict[str, list[str]]:
        """
        获取可用组件列表

        Args:
            framework: 框架过滤

        Returns:
            按类别分组的组件列表
        """
        components: dict[str, list[str]] = {}

        for snippet in self.snippets:
            if framework and snippet.framework != framework:
                continue

            category = snippet.category.value
            if category not in components:
                components[category] = []

            components[category].append(snippet.name)

        return components

    def list_frameworks(self) -> list[str]:
        """列出支持的框架"""
        return [f.value for f in Framework]

    def list_categories(self) -> list[str]:
        """列出组件类别"""
        return [c.value for c in ComponentCategory]


# 便捷函数
def get_code_generator(data_dir: Path | None = None) -> CodeGenerator:
    """获取代码生成器实例"""
    return CodeGenerator(data_dir)


def generate_component_snippet(
    component_name: str,
    framework: str = "react",
    design_system: DesignSystem | None = None
) -> GeneratedComponent | None:
    """
    快捷函数：生成组件片段

    Args:
        component_name: 组件名称
        framework: 框架名称
        design_system: 设计系统

    Returns:
        生成的组件
    """
    generator = get_code_generator()

    try:
        fw_enum = Framework(framework.lower())
    except ValueError:
        return None

    return generator.generate_component(component_name, fw_enum, design_system)
