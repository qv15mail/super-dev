"""
开发：Excellent（11964948@qq.com）
功能：Design Token 生成器
作用：生成可复用的设计 tokens
创建时间：2025-12-30
最后修改：2025-12-30
"""



class TokenGenerator:
    """
    Design Token 生成器

    支持生成：
    1. Color Tokens
    2. Typography Tokens
    3. Spacing Tokens
    4. Shadow Tokens
    5. Animation Tokens
    """

    def generate_color_tokens(
        self,
        primary: str,
        palette_type: str = "monochromatic",
    ) -> dict[str, str]:
        """
        生成色彩 tokens

        Args:
            primary: 主色（hex）
            palette_type: 调色板类型（monochromatic, analogous, complementary, triadic）

        Returns:
            色彩 token 字典
        """
        base_color = self._hex_to_hsl(primary)

        if palette_type == "monochromatic":
            return self._generate_monochromatic_palette(base_color)
        elif palette_type == "analogous":
            return self._generate_analogous_palette(base_color)
        elif palette_type == "complementary":
            return self._generate_complementary_palette(base_color)
        elif palette_type == "triadic":
            return self._generate_triadic_palette(base_color)
        else:
            return self._generate_monochromatic_palette(base_color)

    def _generate_monochromatic_palette(self, base_hsl: tuple) -> dict[str, str]:
        """生成单色调色板"""
        h, s, lightness = base_hsl

        return {
            "50": self._hsl_to_hex(h, s, min(lightness + 45, 100)),
            "100": self._hsl_to_hex(h, s, min(lightness + 40, 100)),
            "200": self._hsl_to_hex(h, s, min(lightness + 30, 100)),
            "300": self._hsl_to_hex(h, s, min(lightness + 20, 100)),
            "400": self._hsl_to_hex(h, s, min(lightness + 10, 100)),
            "500": self._hsl_to_hex(h, s, lightness),
            "600": self._hsl_to_hex(h, s, max(lightness - 10, 0)),
            "700": self._hsl_to_hex(h, s, max(lightness - 20, 0)),
            "800": self._hsl_to_hex(h, s, max(lightness - 30, 0)),
            "900": self._hsl_to_hex(h, s, max(lightness - 40, 0)),
            "950": self._hsl_to_hex(h, s, max(lightness - 45, 0)),
        }

    def _generate_analogous_palette(self, base_hsl: tuple) -> dict[str, str]:
        """生成类比调色板"""
        h, s, lightness = base_hsl

        return {
            "primary": self._hsl_to_hex(h, s, lightness),
            "secondary": self._hsl_to_hex((h + 30) % 360, s, lightness),
            "accent": self._hsl_to_hex((h - 30) % 360, s, lightness),
            "muted": self._hsl_to_hex(h, s * 0.5, lightness * 1.1),
        }

    def _generate_complementary_palette(self, base_hsl: tuple) -> dict[str, str]:
        """生成互补调色板"""
        h, s, lightness = base_hsl

        return {
            "primary": self._hsl_to_hex(h, s, lightness),
            "secondary": self._hsl_to_hex((h + 180) % 360, s, lightness),
            "accent": self._hsl_to_hex((h + 90) % 360, s, lightness),
            "muted": self._hsl_to_hex(h, s * 0.6, lightness * 1.1),
        }

    def _generate_triadic_palette(self, base_hsl: tuple) -> dict[str, str]:
        """生成三元调色板"""
        h, s, lightness = base_hsl

        return {
            "primary": self._hsl_to_hex(h, s, lightness),
            "secondary": self._hsl_to_hex((h + 120) % 360, s, lightness),
            "tertiary": self._hsl_to_hex((h + 240) % 360, s, lightness),
            "accent": self._hsl_to_hex((h + 60) % 360, s, lightness),
        }

    def generate_spacing_tokens(self, base_unit: int = 8) -> dict[str, str]:
        """
        生成间距 tokens（8pt 栅格）

        Args:
            base_unit: 基础单位（像素）

        Returns:
            间距 token 字典
        """
        return {
            "0": "0",
            "px": f"{base_unit * 0.5}px",
            "0.5": f"{base_unit * 0.5}px",
            "1": f"{base_unit}px",
            "1.5": f"{base_unit * 1.5}px",
            "2": f"{base_unit * 2}px",
            "2.5": f"{base_unit * 2.5}px",
            "3": f"{base_unit * 3}px",
            "3.5": f"{base_unit * 3.5}px",
            "4": f"{base_unit * 4}px",
            "5": f"{base_unit * 5}px",
            "6": f"{base_unit * 6}px",
            "7": f"{base_unit * 7}px",
            "8": f"{base_unit * 8}px",
            "9": f"{base_unit * 9}px",
            "10": f"{base_unit * 10}px",
            "12": f"{base_unit * 12}px",
            "16": f"{base_unit * 16}px",
            "20": f"{base_unit * 20}px",
            "24": f"{base_unit * 24}px",
            "32": f"{base_unit * 32}px",
            "40": f"{base_unit * 40}px",
            "48": f"{base_unit * 48}px",
            "56": f"{base_unit * 56}px",
            "64": f"{base_unit * 64}px",
        }

    def generate_shadow_tokens(self, elevation: int = 3) -> dict[str, str]:
        """
        生成阴影 tokens（Material Design 风格）

        Args:
            elevation: 最大级别

        Returns:
            阴影 token 字典
        """
        shadows = {}

        for i in range(elevation + 1):
            opacity = 0.1 + (i * 0.05)
            blur = 2 + (i * 4)
            y_offset = 1 + (i * 2)

            shadows[str(i)] = f"0 {y_offset}px {blur}px 0 rgb(0 0 0 / {opacity:.2f})"

        return shadows

    def generate_animation_tokens(self) -> dict[str, str]:
        """
        生成动画 tokens

        Returns:
            动画 token 字典
        """
        return {
            "duration-fast": "150ms",
            "duration-base": "200ms",
            "duration-slow": "300ms",
            "duration-slower": "500ms",
            "easing-default": "cubic-bezier(0.4, 0, 0.2, 1)",
            "easing-in": "cubic-bezier(0.4, 0, 1, 1)",
            "easing-out": "cubic-bezier(0, 0, 0.2, 1)",
            "easing-in-out": "cubic-bezier(0.4, 0, 0.6, 1)",
            "easing-bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        }

    def _hex_to_hsl(self, hex_color: str) -> tuple[int, int, int]:
        """Hex 转 HSL"""
        hex_color = hex_color.lstrip("#")

        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255

        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val

        # Hue
        h: float = 0.0
        if delta == 0:
            h = 0
        elif max_val == r:
            h = 60 * (((g - b) / delta) % 6)
        elif max_val == g:
            h = 60 * (((b - r) / delta) + 2)
        elif max_val == b:
            h = 60 * (((r - g) / delta) + 4)

        # Saturation
        s: float = 0.0
        if max_val == 0:
            s = 0
        else:
            s = (delta / max_val) * 100

        # Lightness
        lightness: float = ((max_val + min_val) / 2) * 100

        return (round(h), round(s), round(lightness))

    def _hsl_to_hex(self, h: float, s: float, lightness: float) -> str:
        """HSL 转 Hex"""
        s /= 100
        lightness /= 100

        c = (1 - abs(2 * lightness - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = lightness - c / 2

        r: float
        g: float
        b: float
        if 0 <= h < 60:
            r, g, b = c, x, 0.0
        elif 60 <= h < 120:
            r, g, b = x, c, 0.0
        elif 120 <= h < 180:
            r, g, b = 0.0, c, x
        elif 180 <= h < 240:
            r, g, b = 0.0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0.0, c
        else:
            r, g, b = c, 0.0, x

        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)

        return f"#{r:02x}{g:02x}{b:02x}"

    def generate_all_tokens(
        self,
        primary_color: str,
        palette_type: str = "monochromatic",
    ) -> dict[str, dict[str, str]]:
        """
        生成所有 tokens

        Args:
            primary_color: 主色
            palette_type: 调色板类型

        Returns:
            所有 tokens 字典
        """
        return {
            "colors": self.generate_color_tokens(primary_color, palette_type),
            "spacing": self.generate_spacing_tokens(),
            "shadows": self.generate_shadow_tokens(),
            "animations": self.generate_animation_tokens(),
        }
