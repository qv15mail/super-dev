"""
开发：Excellent（11964948@qq.com）
功能：美学引擎 - 生成独特的设计美学方向
作用：避免通用 AI 美学，生成独特、令人难忘的设计方向
创建时间：2025-12-30
最后修改：2025-12-30
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import cast


class AestheticDirectionType(str, Enum):
    """美学方向类型"""

    # 极简方向
    BRUTALIST_MINIMAL = "brutalist_minimal"
    JAPANESE_ZEN = "japanese_zen"
    SCANDINAVIAN = "scandinavian"
    SWISS_INTERNATIONAL = "swiss_international"

    # 极繁方向
    MAXIMALIST_CHAOS = "maximalist_chaos"
    MEMPHIS_GROUP = "memphis_group"
    POP_ART = "pop_art"
    VAPORWAVE = "vaporwave"

    # 复古未来
    RETRO_FUTURISM = "retro_futurism"
    CYBERPUNK = "cyberpunk"
    ART_DECO = "art_deco"
    STEAMPUNK = "steampunk"

    # 自然有机
    ORGANIC_NATURAL = "organic_natural"
    BIOPHILIC = "biophilic"
    EARTHY = "earthy"
    BOTANICAL = "botanical"

    # 奢华精致
    LUXURY_REFINED = "luxury_refined"
    FRENCH_ELEGANCE = "french_elegance"
    ITALIAN_SOPHISTICATION = "italian_sophistication"
    ARTISANAL = "artisanal"

    # 俏皮趣味
    PLAYFUL_TOY = "playful_toy"
    KAWAII = "kawaii"
    WHIMSICAL = "whimsical"
    NEON_POP = "neon_pop"

    # 编辑杂志
    EDITORIAL_MAGAZINE = "editorial_magazine"
    TYPOGRAPHY_CENTRIC = "typography_centric"
    GRID_BREAKING = "grid_breaking"

    # 原始工业
    RAW_INDUSTRIAL = "raw_industrial"
    UTILITARIAN = "utilitarian"
    GRUNGE = "grunge"
    POST_APOCALYPTIC = "post_apocalyptic"

    # 柔和梦幻
    SOFT_PASTEL = "soft_pastel"
    DREAMY = "dreamy"
    ETHEREAL = "ethereal"
    GLASS_MORPHISM = "glass_morphism"


@dataclass
class Typography:
    """字体配置"""
    display: str  # 标题字体
    body: str  # 正文字体
    accent: str | None = None  # 强调字体
    mono: str | None = None  # 等宽字体

    def get_css_imports(self) -> list[str]:
        """获取 Google Fonts 导入"""
        fonts = [self.display, self.body]
        if self.accent:
            fonts.append(self.accent)
        if self.mono:
            fonts.append(self.mono)
        return list(set(fonts))


@dataclass
class ColorPalette:
    """色彩配置"""
    primary: str  # 主色
    secondary: str  # 次要色
    accent: str  # 强调色
    background: str  # 背景色
    surface: str  # 表面色
    text: str  # 文本色
    text_secondary: str  # 次要文本色

    # 可选的高级色彩
    gradient_start: str | None = None
    gradient_end: str | None = None
    noise_texture: str | None = None

    def get_css_variables(self) -> dict[str, str]:
        """获取 CSS 变量"""
        vars = {
            "--color-primary": self.primary,
            "--color-secondary": self.secondary,
            "--color-accent": self.accent,
            "--color-background": self.background,
            "--color-surface": self.surface,
            "--color-text": self.text,
            "--color-text-secondary": self.text_secondary,
        }
        if self.gradient_start:
            vars["--color-gradient-start"] = self.gradient_start
        if self.gradient_end:
            vars["--color-gradient-end"] = self.gradient_end
        return vars


@dataclass
class AnimationStyle:
    """动画风格"""
    easing: str  # 缓动函数
    duration: str  # 默认时长
    stagger: bool = True  # 是否使用交错
    micro_interactions: bool = True  # 是否有微交互
    scroll_trigger: bool = False  # 是否有滚动触发

    # 特殊效果
    parallax: bool = False
    morphing: bool = False
    particle_effects: bool = False


@dataclass
class LayoutPrinciples:
    """布局原则"""
    grid_system: str  # 栅格系统
    asymmetry: bool = False  # 不对称
    overlap: bool = False  # 重叠元素
    diagonal_flow: bool = False  # 对角线流动
    generous_spacing: bool = True  # 宽松间距
    density: str = "balanced"  # 密度：sparse, balanced, dense


@dataclass
class VisualDetails:
    """视觉细节"""
    shadows: str  # 阴影风格
    borders: str  # 边框风格
    corner_radius: str  # 圆角
    textures: list[str]  # 纹理列表

    # 特效
    grain_overlay: bool = False
    gradient_mesh: bool = False
    decorative_borders: bool = False
    custom_cursor: bool = False


@dataclass
class AestheticDirection:
    """完整的美学方向"""
    name: str
    description: str
    typography: Typography
    colors: ColorPalette
    animation: AnimationStyle
    layout: LayoutPrinciples
    details: VisualDetails
    differentiation: str  # 令人难忘的独特元素

    def to_css(self) -> str:
        """生成 CSS 变量"""
        css = [":root {"]
        css.extend([f"  {k}: {v};" for k, v in self.colors.get_css_variables().items()])
        css.append("}")
        return "\n".join(css)


class AestheticEngine:
    """美学引擎 - 生成独特的设计方向"""

    # 独特的字体库（避免 Inter, Roboto, Arial）
    DISPLAY_FONTS = [
        "Space Grotesk", "Syne", "Clash Display", "General Sans",
        "Fraunces", "Bebas Neue", "Right Grotesk", "PP Neue Montreal",
        "DM Sans", "Outfit", "Sora", "Chillax",
        "Monument Extended", "Bodon", "Playfair Display", "Cormorant",
        "IBM Plex Sans", "Syncopate", "Russo One", "Lexend",
    ]

    BODY_FONTS = [
        "Plus Jakarta Sans", "Inter", "Satoshi", "Geist",
        "Neue Haas Grotesk", "SF Pro Display", "Source Sans Pro",
        "Work Sans", "Space Grotesk", "DM Sans", "Outfit",
        "EB Garamond", "Crimson Pro", "Lora", "Merriweather",
    ]

    ACCENT_FONTS = [
        "Playfair Display", "Cormorant", "Fraunces", "Bebas Neue",
        "Syncopate", "Russo One", "Monument Extended",
    ]

    MONO_FONTS = [
        "JetBrains Mono", "Fira Code", "IBM Plex Mono", "Source Code Pro",
        "Space Mono", "Roboto Mono", "DM Mono",
    ]

    # 预设美学方向
    AESTHETIC_PRESETS: dict[AestheticDirectionType, dict] = {
        AestheticDirectionType.BRUTALIST_MINIMAL: {
            "description": "原始极简主义 - 粗糙、直接、无装饰",
            "typography": {
                "display": "Space Grotesk",
                "body": "Plus Jakarta Sans",
            },
            "colors": {
                "primary": "#000000",
                "secondary": "#FFFFFF",
                "accent": "#FF0000",
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "text": "#000000",
                "text_secondary": "#666666",
            },
            "animation": {
                "easing": "steps(4)",
                "duration": "0.2s",
                "stagger": False,
                "micro_interactions": False,
            },
        },

        AestheticDirectionType.MAXIMALIST_CHAOS: {
            "description": "极繁混乱 - 最大化视觉冲击力",
            "typography": {
                "display": "Clash Display",
                "body": "Satoshi",
                "accent": "Bebas Neue",
            },
            "colors": {
                "primary": "#FF6B6B",
                "secondary": "#4ECDC4",
                "accent": "#FFE66D",
                "background": "#1A1A2E",
                "surface": "#16213E",
                "text": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "gradient_start": "#FF6B6B",
                "gradient_end": "#4ECDC4",
            },
            "animation": {
                "easing": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
                "duration": "0.6s",
                "stagger": True,
                "micro_interactions": True,
                "scroll_trigger": True,
            },
        },

        AestheticDirectionType.CYBERPUNK: {
            "description": "赛博朋克 - 高科技低生活",
            "typography": {
                "display": "Syncopate",
                "body": "Rajdhani",
                "mono": "Orbitron",
            },
            "colors": {
                "primary": "#00FF41",
                "secondary": "#FF00FF",
                "accent": "#00FFFF",
                "background": "#0D0D0D",
                "surface": "#1A1A1A",
                "text": "#00FF41",
                "text_secondary": "#B0B0B0",
                "gradient_start": "#00FF41",
                "gradient_end": "#FF00FF",
                "noise_texture": "url(#noise)",
            },
            "animation": {
                "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
                "duration": "0.3s",
                "stagger": True,
                "micro_interactions": True,
                "scroll_trigger": True,
                "parallax": True,
            },
        },

        AestheticDirectionType.SOFT_PASTEL: {
            "description": "柔和梦幻 - 粉彩与柔和",
            "typography": {
                "display": "Fraunces",
                "body": "Sora",
            },
            "colors": {
                "primary": "#FFB3BA",
                "secondary": "#BAFFC9",
                "accent": "#BAE1FF",
                "background": "#FFFDF5",
                "surface": "#FFFFFF",
                "text": "#4A4A4A",
                "text_secondary": "#8A8A8A",
            },
            "animation": {
                "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
                "duration": "0.5s",
                "stagger": True,
                "micro_interactions": True,
            },
        },

        AestheticDirectionType.LUXURY_REFINED: {
            "description": "奢华精致 - 优雅与品质",
            "typography": {
                "display": "Playfair Display",
                "body": "Cormorant",
                "accent": "Bodoni",
            },
            "colors": {
                "primary": "#1C1C1C",
                "secondary": "#C9A962",
                "accent": "#8B7355",
                "background": "#FAFAFA",
                "surface": "#FFFFFF",
                "text": "#1C1C1C",
                "text_secondary": "#666666",
            },
            "animation": {
                "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
                "duration": "0.6s",
                "stagger": True,
                "micro_interactions": True,
            },
        },

        AestheticDirectionType.VAPORWAVE: {
            "description": "蒸汽波 - 复古数字美学",
            "typography": {
                "display": "Right Grotesk",
                "body": "Space Grotesk",
            },
            "colors": {
                "primary": "#FF71CE",
                "secondary": "#01CDFE",
                "accent": "#B967FF",
                "background": "#2D1B4E",
                "surface": "#1A0B2E",
                "text": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "gradient_start": "#FF71CE",
                "gradient_end": "#01CDFE",
            },
            "animation": {
                "easing": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
                "duration": "0.4s",
                "stagger": True,
                "micro_interactions": True,
            },
        },
    }

    def __init__(self, seed: int | None = None):
        """
        初始化美学引擎

        Args:
            seed: 随机种子，用于可重现的结果
        """
        self._rng: random.Random | random.SystemRandom
        if seed is not None:
            self._rng = random.Random(seed)  # nosec B311
        else:
            self._rng = random.SystemRandom()

    def generate_direction(
        self,
        direction: AestheticDirectionType | None = None,
        custom_context: str | None = None,
    ) -> AestheticDirection:
        """
        生成美学方向

        Args:
            direction: 指定的美学方向，None 则随机
            custom_context: 自定义上下文，用于 AI 生成定制方向

        Returns:
            完整的美学方向配置
        """
        if direction is None:
            direction = self._rng.choice(list(AestheticDirectionType))

        preset = self.AESTHETIC_PRESETS.get(direction)
        if not preset:
            # 如果没有预设，生成基础配置
            return self._generate_custom_direction(direction)

        return self._build_from_preset(direction, preset)

    def _generate_custom_direction(
        self, direction: AestheticDirectionType
    ) -> AestheticDirection:
        """生成自定义美学方向"""
        return AestheticDirection(
            name=direction.value,
            description=f"Custom {direction.value} aesthetic",
            typography=Typography(
                display=self._rng.choice(self.DISPLAY_FONTS),
                body=self._rng.choice(self.BODY_FONTS),
                accent=self._rng.choice(self.ACCENT_FONTS) if self._rng.random() > 0.5 else None,
                mono=self._rng.choice(self.MONO_FONTS),
            ),
            colors=ColorPalette(
                primary=self._random_color(),
                secondary=self._random_color(),
                accent=self._random_color(),
                background=self._random_color(light=True),
                surface=self._random_color(light=True),
                text="#000000" if self._rng.random() > 0.5 else "#FFFFFF",
                text_secondary="#666666",
            ),
            animation=AnimationStyle(
                easing=self._rng.choice([
                    "ease", "ease-in", "ease-out", "ease-in-out",
                    "cubic-bezier(0.4, 0, 0.2, 1)",
                    "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
                ]),
                duration=f"{self._rng.uniform(0.2, 0.8):.1f}s",
                stagger=self._rng.random() > 0.3,
                micro_interactions=self._rng.random() > 0.2,
                scroll_trigger=self._rng.random() > 0.5,
            ),
            layout=LayoutPrinciples(
                grid_system=self._rng.choice(["8pt", "12pt", "baseline"]),
                asymmetry=self._rng.random() > 0.5,
                overlap=self._rng.random() > 0.7,
                diagonal_flow=self._rng.random() > 0.8,
            ),
            details=VisualDetails(
                shadows=self._rng.choice(["none", "subtle", "medium", "dramatic"]),
                borders=self._rng.choice(["none", "thin", "medium", "thick"]),
                corner_radius=self._rng.choice(["0", "4px", "8px", "16px", "pill"]),
                textures=[],
            ),
            differentiation="Unique custom aesthetic",
        )

    def _build_from_preset(
        self, direction: AestheticDirectionType, preset: dict
    ) -> AestheticDirection:
        """从预设构建美学方向"""
        typo_cfg = preset["typography"]
        color_cfg = preset["colors"]
        anim_cfg = preset["animation"]

        return AestheticDirection(
            name=direction.value,
            description=preset["description"],
            typography=Typography(
                display=typo_cfg.get("display", self._rng.choice(self.DISPLAY_FONTS)),
                body=typo_cfg.get("body", self._rng.choice(self.BODY_FONTS)),
                accent=typo_cfg.get("accent"),
                mono=typo_cfg.get("mono", self._rng.choice(self.MONO_FONTS)),
            ),
            colors=ColorPalette(**color_cfg),
            animation=AnimationStyle(**anim_cfg),
            layout=LayoutPrinciples(
                grid_system="8pt",
                asymmetry=direction in [
                    AestheticDirectionType.MAXIMALIST_CHAOS,
                    AestheticDirectionType.GRID_BREAKING,
                ],
                overlap=direction in [
                    AestheticDirectionType.MAXIMALIST_CHAOS,
                    AestheticDirectionType.MEMPHIS_GROUP,
                ],
            ),
            details=VisualDetails(
                shadows="dramatic" if direction in [
                    AestheticDirectionType.CYBERPUNK,
                    AestheticDirectionType.VAPORWAVE,
                ] else "subtle",
                borders="thin",
                corner_radius="0" if direction in [
                    AestheticDirectionType.BRUTALIST_MINIMAL,
                    AestheticDirectionType.RAW_INDUSTRIAL,
                ] else "8px",
                textures=["noise"] if direction == AestheticDirectionType.CYBERPUNK else [],
            ),
            differentiation=self._get_differentiation(direction),
        )

    def _get_differentiation(self, direction: AestheticDirectionType) -> str:
        """获取令人难忘的独特元素"""
        differentiations = {
            AestheticDirectionType.BRUTALIST_MINIMAL: "粗体排版、单色对比、极简装饰",
            AestheticDirectionType.MAXIMALIST_CHAOS: "饱和色彩、大胆碰撞、最大视觉密度",
            AestheticDirectionType.CYBERPUNK: "霓虹发光、故障效果、数字纹理",
            AestheticDirectionType.SOFT_PASTEL: "柔和粉彩、圆润形状、梦幻氛围",
            AestheticDirectionType.LUXURY_REFINED: "金色点缀、精致衬线、充足留白",
            AestheticDirectionType.VAPORWAVE: "紫粉渐变、复古网格、雕塑效果",
            AestheticDirectionType.RETRO_FUTURISM: "原子图案、流线型形状、复古科技",
            AestheticDirectionType.ORGANIC_NATURAL: "有机曲线、大地色调、自然纹理",
            AestheticDirectionType.PLAYFUL_TOY: "明亮色彩、圆润形状、趣味图标",
            AestheticDirectionType.EDITORIAL_MAGAZINE: "大胆排版、不对称布局、编辑感",
        }
        return differentiations.get(
            direction, "独特的视觉识别，令人难忘的设计语言"
        )

    def _random_color(self, light: bool = False) -> str:
        """生成随机颜色"""
        if light:
            return f"#{self._rng.randint(200, 255):02x}{self._rng.randint(200, 255):02x}{self._rng.randint(200, 255):02x}"
        return f"#{self._rng.randint(0, 255):02x}{self._rng.randint(0, 255):02x}{self._rng.randint(0, 255):02x}"

    def list_directions(self) -> list[str]:
        """列出所有可用的美学方向"""
        return [d.value for d in AestheticDirectionType]

    def get_direction_description(self, direction: AestheticDirectionType) -> str:
        """获取美学方向的描述"""
        preset = self.AESTHETIC_PRESETS.get(direction, {})
        return cast(str, preset.get("description", direction.value))
