"""
开发：Excellent（11964948@qq.com）
功能：设计系统生成器 - 完整的设计交付
作用：生成完整的设计系统、组件、文档
创建时间：2025-12-30
最后修改：2025-12-30
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .aesthetics import AestheticDirection, AestheticDirectionType, AestheticEngine
from .engine import DesignIntelligenceEngine
from .tokens import TokenGenerator


@dataclass
class DesignSystem:
    """设计系统配置"""
    name: str
    description: str

    # 色彩
    colors: dict[str, str] = field(default_factory=dict)

    # 字体
    typography: dict[str, str] = field(default_factory=dict)

    # 间距
    spacing: dict[str, str] = field(default_factory=dict)

    # 阴影
    shadows: dict[str, str] = field(default_factory=dict)

    # 圆角
    radius: dict[str, str] = field(default_factory=dict)

    # 动画
    animations: dict[str, str] = field(default_factory=dict)

    # 组件样式
    components: dict[str, dict] = field(default_factory=dict)

    # 美学方向
    aesthetic: AestheticDirection | None = None

    def to_css_variables(self) -> str:
        """生成 CSS 变量"""
        lines = [":root {"]
        lines.append("  /* Colors */")

        for name, value in self.colors.items():
            lines.append(f"  --color-{name}: {value};")

        lines.append("")
        lines.append("  /* Typography */")

        for name, value in self.typography.items():
            lines.append(f"  --font-{name}: {value};")

        lines.append("")
        lines.append("  /* Spacing */")

        for name, value in self.spacing.items():
            lines.append(f"  --space-{name}: {value};")

        lines.append("")
        lines.append("  /* Shadows */")

        for name, value in self.shadows.items():
            lines.append(f"  --shadow-{name}: {value};")

        lines.append("")
        lines.append("  /* Border Radius */")

        for name, value in self.radius.items():
            lines.append(f"  --radius-{name}: {value};")

        lines.append("")
        lines.append("  /* Animations */")

        for name, value in self.animations.items():
            lines.append(f"  --animate-{name}: {value};")

        lines.append("}")

        return "\n".join(lines)

    def to_tailwind_config(self) -> dict[str, Any]:
        """生成 Tailwind 配置"""
        return {
            "theme": {
                "extend": {
                    "colors": self.colors,
                    "fontFamily": self.typography,
                    "spacing": self.spacing,
                    "boxShadow": self.shadows,
                    "borderRadius": self.radius,
                    "animation": self.animations,
                }
            }
        }


class DesignSystemGenerator:
    """
    设计系统生成器

    整合所有设计能力：
    1. 智能推荐
    2. 美学生成
    3. Token 生成
    4. 组件样式
    5. 文档生成
    """

    def __init__(self):
        """初始化设计系统生成器"""
        self.engine = DesignIntelligenceEngine()
        self.aesthetic_engine = AestheticEngine()
        self.token_generator = TokenGenerator()

    def generate(
        self,
        product_type: str,
        industry: str,
        keywords: list[str],
        platform: str = "web",
        aesthetic: str | None = None,
    ) -> DesignSystem:
        """
        生成完整的设计系统

        Args:
            product_type: 产品类型
            industry: 行业
            keywords: 关键词
            platform: 平台
            aesthetic: 美学方向（可选）

        Returns:
            完整的设计系统
        """
        # 获取智能推荐
        recommendation = self.engine.recommend_design_system(
            product_type=product_type,
            industry=industry,
            keywords=keywords,
            platform=platform,
        )

        # 生成或使用指定的美学方向
        if aesthetic:
            direction = AestheticDirectionType[aesthetic.upper()]
            aesthetic_config = self.aesthetic_engine.generate_direction(direction)
        else:
            aesthetic_config = self.aesthetic_engine.generate_direction()

        # 创建设计系统
        design_system = DesignSystem(
            name=f"{product_type} {industry} Design System",
            description=f"Complete design system for {product_type} in {industry} industry",
            aesthetic=aesthetic_config,
        )

        # 配色方案
        color_palette = recommendation.get("color_palette", {})
        design_system.colors = {
            "primary": color_palette.get("primary", "#3B82F6"),
            "secondary": color_palette.get("secondary", "#8B5CF6"),
            "accent": color_palette.get("accent", "#EC4899"),
            "background": color_palette.get("background", "#FFFFFF"),
            "surface": color_palette.get("surface", "#F9FAFB"),
            "text": color_palette.get("text", "#111827"),
            "text-muted": color_palette.get("text_muted", "#6B7280"),
            "border": color_palette.get("border", "#E5E7EB"),
        }

        # 字体
        typography_config = recommendation.get("typography", {})
        design_system.typography = {
            "heading": typography_config.get("heading_font", "Inter"),
            "body": typography_config.get("body_font", "Inter"),
            "accent": typography_config.get("accent_font", ""),
        }

        # 间距（8pt 栅格）
        design_system.spacing = {
            "xs": "0.25rem",   # 4px
            "sm": "0.5rem",    # 8px
            "md": "1rem",      # 16px
            "lg": "1.5rem",    # 24px
            "xl": "2rem",      # 32px
            "2xl": "3rem",     # 48px
            "3xl": "4rem",     # 64px
        }

        # 阴影
        design_system.shadows = {
            "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "md": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
            "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1)",
        }

        # 圆角
        design_system.radius = {
            "sm": "0.25rem",
            "md": "0.5rem",
            "lg": "1rem",
            "xl": "1.5rem",
            "full": "9999px",
        }

        # 动画
        design_system.animations = {
            "fade-in": "fade-in 0.3s ease-out",
            "slide-up": "slide-up 0.4s ease-out",
            "scale-in": "scale-in 0.2s ease-out",
        }

        # 组件样式
        design_system.components = self._generate_component_styles(design_system)

        return design_system

    def _generate_component_styles(self, design_system: DesignSystem) -> dict[str, dict]:
        """生成组件样式"""
        return {
            "button": {
                "primary": {
                    "background": "var(--color-primary)",
                    "color": "var(--color-background)",
                    "padding": "var(--space-sm) var(--space-lg)",
                    "border-radius": "var(--radius-md)",
                    "font-weight": "600",
                    "transition": "all 0.2s",
                },
                "secondary": {
                    "background": "var(--color-secondary)",
                    "color": "var(--color-background)",
                    "padding": "var(--space-sm) var(--space-lg)",
                    "border-radius": "var(--radius-md)",
                    "font-weight": "600",
                },
            },
            "card": {
                "background": "var(--color-surface)",
                "border": "1px solid var(--color-border)",
                "border-radius": "var(--radius-lg)",
                "padding": "var(--space-lg)",
                "shadow": "var(--shadow-md)",
            },
            "input": {
                "background": "var(--color-background)",
                "border": "1px solid var(--color-border)",
                "border-radius": "var(--radius-md)",
                "padding": "var(--space-sm) var(--space-md)",
                "color": "var(--color-text)",
            },
        }

    def generate_documentation(
        self,
        design_system: DesignSystem,
        output_dir: Path,
    ) -> list[Path]:
        """
        生成设计系统文档

        Args:
            design_system: 设计系统
            output_dir: 输出目录

        Returns:
            生成的文件列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        generated_files = []

        # 1. CSS Variables
        css_file = output_dir / "design-tokens.css"
        css_file.write_text(design_system.to_css_variables(), encoding="utf-8")
        generated_files.append(css_file)

        # 2. Tailwind Config
        tailwind_file = output_dir / "tailwind.config.json"
        tailwind_file.write_text(
            json.dumps(design_system.to_tailwind_config(), indent=2),
            encoding="utf-8"
        )
        generated_files.append(tailwind_file)

        # 3. Design System Documentation
        docs_file = output_dir / "DESIGN_SYSTEM.md"
        docs_content = self._generate_docs_content(design_system)
        docs_file.write_text(docs_content, encoding="utf-8")
        generated_files.append(docs_file)

        return generated_files

    def _generate_docs_content(self, design_system: DesignSystem) -> str:
        """生成文档内容"""
        lines = [
            f"# {design_system.name}",
            "",
            f"{design_system.description}",
            "",
            "## Design Tokens",
            "",
            "### Colors",
            "",
            "| Token | Value | Usage |",
            "|-------|-------|-------|",
        ]

        for name, value in design_system.colors.items():
            lines.append(f"| `--color-{name}` | `{value}` | {self._get_color_usage(name)} |")

        lines.extend([
            "",
            "### Typography",
            "",
            "| Token | Value | Usage |",
            "|-------|-------|-------|",
        ])

        for name, value in design_system.typography.items():
            if value:
                lines.append(f"| `--font-{name}` | `{value}` | {name.capitalize()} text |")

        if design_system.aesthetic:
            lines.extend([
                "",
                "## Aesthetic Direction",
                "",
                f"**Style**: {design_system.aesthetic.name}",
                f"**Description**: {design_system.aesthetic.description}",
                f"**Key Differentiator**: {design_system.aesthetic.differentiation}",
                "",
                "### Typography",
                "",
                f"- **Display**: {design_system.aesthetic.typography.display}",
                f"- **Body**: {design_system.aesthetic.typography.body}",
            ])

        return "\n".join(lines)

    def _get_color_usage(self, color_name: str) -> str:
        """获取颜色用途"""
        usages = {
            "primary": "Primary actions, links, highlights",
            "secondary": "Secondary actions, accents",
            "accent": "Emphasis, call-to-actions",
            "background": "Page background",
            "surface": "Card, panel backgrounds",
            "text": "Primary text",
            "text-muted": "Secondary text",
            "border": "Borders, dividers",
        }
        return usages.get(color_name, "General use")

    def export_to_sketch(
        self,
        design_system: DesignSystem,
        output_path: Path,
    ):
        """
        导出为 Sketch 格式（未来实现）

        Args:
            design_system: 设计系统
            output_path: 输出路径
        """
        # TODO: 实现 Sketch 导出
        pass

    def export_to_figma(
        self,
        design_system: DesignSystem,
        output_path: Path,
    ):
        """
        导出为 Figma 格式（未来实现）

        Args:
            design_system: 设计系统
            output_path: 输出路径
        """
        # TODO: 实现 Figma 导出
        pass
