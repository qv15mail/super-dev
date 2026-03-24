"""
开发：Excellent（11964948@qq.com）
功能：Landing 页面模式生成器
作用：生成转化优化的 Landing 页面布局
创建时间：2025-01-04
最后修改：2025-01-04
"""

import csv
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class LandingCategory(str, Enum):
    """Landing 页面类别"""
    CLASSIC = "classic"
    VIDEO = "video"
    PRICING = "pricing"
    PRODUCT = "product"
    SOCIAL = "social"
    COMPARISON = "comparison"
    FAQ = "faq"
    LAYOUT = "layout"
    MINIMAL = "minimal"
    CONVERSION = "conversion"
    INTERACTIVE = "interactive"
    NARRATIVE = "narrative"
    DATA = "data"
    TRUST = "trust"
    THEME = "theme"


@dataclass
class LandingSection:
    """页面区块"""
    name: str
    type: str  # hero, features, pricing, testimonial, cta, etc.
    content_hint: str
    required: bool = False
    order: int = 0


@dataclass
class CTAStrategy:
    """CTA 策略"""
    primary_placement: str  # where the main CTA goes
    secondary_placements: list[str] = field(default_factory=list)
    style: str = "button"  # button, link, text
    urgency: str = "medium"  # low, medium, high
    text_variations: list[str] = field(default_factory=list)


@dataclass
class LandingPattern:
    """Landing 页面模式"""
    name: str
    category: LandingCategory
    description: str
    sections: list[LandingSection]
    cta_strategy: CTAStrategy
    best_for: list[str]  # SaaS, Marketing, E-commerce, etc.
    conversion_tips: list[str]
    complexity: str  # low, medium, high
    keywords: list[str]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "sections": [
                {
                    "name": s.name,
                    "type": s.type,
                    "content_hint": s.content_hint,
                    "required": s.required,
                    "order": s.order
                }
                for s in self.sections
            ],
            "cta_strategy": {
                "primary_placement": self.cta_strategy.primary_placement,
                "secondary_placements": self.cta_strategy.secondary_placements,
                "style": self.cta_strategy.style,
                "urgency": self.cta_strategy.urgency,
                "text_variations": self.cta_strategy.text_variations
            },
            "best_for": self.best_for,
            "conversion_tips": self.conversion_tips,
            "complexity": self.complexity,
            "keywords": self.keywords
        }


class LandingPatternGenerator:
    """Landing 页面模式生成器"""

    def __init__(self, data_dir: Path | None = None):
        """
        初始化生成器

        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "design"

        self.data_dir = Path(data_dir)
        self.patterns: list[LandingPattern] = []
        self._load_patterns()

    def _load_patterns(self):
        """从 CSV 加载模式数据"""
        csv_path = self.data_dir / "landing_patterns.csv"

        if not csv_path.exists():
            # 使用默认模式
            self.patterns = self._get_default_patterns()
            return

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pattern = self._parse_pattern(row)
                if pattern:
                    self.patterns.append(pattern)

    def _parse_pattern(self, row: dict[str, str]) -> LandingPattern | None:
        """解析 CSV 行为模式对象"""
        try:
            # 解析 sections
            sections_raw = row.get("sections", "")
            section_names = [s.strip() for s in sections_raw.split(",")]

            sections = []
            for i, name in enumerate(section_names):
                section_type = self._infer_section_type(name)
                sections.append(LandingSection(
                    name=name.replace("_", " ").title(),
                    type=section_type,
                    content_hint=self._get_content_hint(section_type),
                    required=(i == 0),  # 第一部分通常是必需的
                    order=i
                ))

            # 解析 CTA 策略
            cta_strategy = CTAStrategy(
                primary_placement=section_names[0] if section_names else "hero",
                style="button",
                urgency="medium",
                text_variations=self._get_cta_variations(row.get("best_for", ""))
            )

            return LandingPattern(
                name=row["name"],
                category=LandingCategory(row.get("category", "classic")),
                description=row["description"],
                sections=sections,
                cta_strategy=cta_strategy,
                best_for=row.get("best_for", "").split(","),
                conversion_tips=row.get("conversion_tips", "").split(",") if row.get("conversion_tips") else [],
                complexity=row.get("complexity", "medium"),
                keywords=row.get("keywords", "").split(",") if row.get("keywords") else []
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to parse pattern: {e}")
            return None

    def _infer_section_type(self, name: str) -> str:
        """推断区块类型"""
        name_lower = name.lower()
        type_map = {
            "hero": ["hero", "video_hero", "split_hero", "dark_hero", "single_cta"],
            "features": ["features", "zigzag_features", "dark_features", "feature"],
            "pricing": ["pricing_plans", "pricing", "plans"],
            "testimonials": ["testimonials", "social_proof", "reviews"],
            "comparison": ["comparison_table", "comparison"],
            "faq": ["faq", "faq_categories", "questions"],
            "demo": ["interactive_demo", "video_hero", "product_gallery"],
            "stats": ["stats_dashboard", "trust_badges", "stats"],
            "cta": ["cta", "contact_cta", "repeating_ctas"],
            "story": ["story_sections", "timeline", "narrative"],
        }
        for type_name, patterns in type_map.items():
            if any(pattern in name_lower for pattern in patterns):
                return type_name
        return "content"

    def _get_content_hint(self, section_type: str) -> str:
        """获取内容提示"""
        hints = {
            "hero": "Compelling headline, subheadline, primary CTA, hero image/video",
            "features": "3-6 key features with icons, titles, descriptions",
            "pricing": "2-4 pricing tiers, highlight recommended plan",
            "testimonials": "3-5 customer quotes with photos and titles",
            "comparison": "Side-by-side feature comparison table",
            "faq": "5-10 common questions with clear answers",
            "demo": "Interactive or video demonstration",
            "stats": "Key metrics, social proof numbers",
            "cta": "Clear call-to-action with benefit statement",
            "content": "Relevant content for this section",
        }
        return hints.get(section_type, "Content for this section")

    def _get_cta_variations(self, best_for: str) -> list[str]:
        """获取 CTA 文本变体"""
        base_ctas = {
            "SaaS": ["Start Free Trial", "Get Started", "Request Demo", "Start Now"],
            "E-commerce": ["Shop Now", "Browse Collection", "Add to Cart", "Buy Now"],
            "Marketing": ["Learn More", "Get Started", "Contact Us", "Sign Up"],
            "B2B": ["Request Demo", "Contact Sales", "Enterprise Plans", "Book a Call"],
            "Freemium": ["Start Free", "Upgrade Now", "Get Pro", "Unlock Features"],
            "Mobile": ["Download App", "Get on iOS", "Get on Android", "Install Now"],
            "Default": ["Get Started", "Learn More", "Contact Us", "Sign Up"]
        }

        for key, cta_list in base_ctas.items():
            if key.lower() in best_for.lower():
                return cta_list

        return base_ctas["Default"]

    def _get_default_patterns(self) -> list[LandingPattern]:
        """获取默认模式（当 CSV 不存在时）"""
        return [
            LandingPattern(
                name="Hero + Features",
                category=LandingCategory.CLASSIC,
                description="Classic landing page with hero section and feature showcase",
                sections=[
                    LandingSection("Hero", "hero", "Compelling headline and primary CTA", True, 0),
                    LandingSection("Features", "features", "3-6 key features with icons", False, 1),
                    LandingSection("Social Proof", "testimonials", "Customer testimonials", False, 2),
                    LandingSection("CTA", "cta", "Final call-to-action", False, 3),
                ],
                cta_strategy=CTAStrategy(
                    primary_placement="hero",
                    secondary_placements=["features", "cta"],
                    style="button",
                    urgency="medium",
                    text_variations=["Get Started", "Learn More", "Start Free Trial"]
                ),
                best_for=["SaaS", "Marketing", "Product"],
                conversion_tips=["Place primary CTA in hero section", "Use contrasting color for CTA"],
                complexity="medium",
                keywords=["hero", "features", "classic", "landing"]
            ),
            LandingPattern(
                name="Minimal Single CTA",
                category=LandingCategory.MINIMAL,
                description="Ultra-minimalist page with single focused action",
                sections=[
                    LandingSection("Single CTA", "hero", "One clear headline and one button", True, 0),
                ],
                cta_strategy=CTAStrategy(
                    primary_placement="hero",
                    style="button",
                    urgency="high",
                    text_variations=["Sign Up", "Get Started", "Join Now"]
                ),
                best_for=["Newsletter", "Signup", "Waitlist"],
                conversion_tips=["Remove all distractions", "Use plenty of whitespace"],
                complexity="low",
                keywords=["minimal", "simple", "focused", "single"]
            )
        ]

    def search(self, query: str, max_results: int = 5) -> list[LandingPattern]:
        """
        搜索 Landing 页面模式

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            匹配的模式列表
        """
        query_lower = query.lower()

        # 简单的关键词匹配
        scored_patterns = []
        for pattern in self.patterns:
            score = 0

            # 名称匹配
            if query_lower in pattern.name.lower():
                score += 10

            # 类别匹配
            if query_lower in pattern.category.value:
                score += 5

            # 关键词匹配
            for keyword in pattern.keywords:
                if query_lower in keyword.lower():
                    score += 3

            # 最佳用途匹配
            for use_case in pattern.best_for:
                if query_lower in use_case.lower():
                    score += 2

            if score > 0:
                scored_patterns.append((pattern, score))

        # 按分数排序
        scored_patterns.sort(key=lambda x: x[1], reverse=True)

        return [p for p, _ in scored_patterns[:max_results]]

    def get_pattern(self, name: str) -> LandingPattern | None:
        """
        获取指定名称的模式

        Args:
            name: 模式名称

        Returns:
            模式对象或 None
        """
        for pattern in self.patterns:
            if pattern.name.lower() == name.lower():
                return pattern
        return None

    def recommend(self, product_type: str, goal: str, audience: str) -> LandingPattern | None:
        """
        推荐最适合的模式

        Args:
            product_type: 产品类型 (SaaS, E-commerce, Mobile, etc.)
            goal: 目标 (signup, purchase, demo, etc.)
            audience: 受众 (B2B, B2C, Enterprise, etc.)

        Returns:
            推荐的模式
        """
        # 基于目标和产品类型的推荐逻辑
        goal_lower = goal.lower()
        product_lower = product_type.lower()

        if goal_lower in ["signup", "register", "newsletter"]:
            # 注册类目标：推荐简单聚焦的模式
            return self.get_pattern("Minimal Single CTA") or self.get_pattern("Hero + Features")

        elif goal_lower in ["purchase", "buy", "order"]:
            # 购买类目标：推荐产品展示模式
            return self.get_pattern("Product Showcase") or self.get_pattern("Hero + Features")

        elif goal_lower in ["demo", "trial"]:
            # 演示类目标：推荐交互演示
            return self.get_pattern("Interactive Demo") or self.get_pattern("Video-First")

        elif "pricing" in goal_lower:
            # 价格相关：推荐价格预览
            return self.get_pattern("Pricing Preview")

        elif product_lower in ["b2b", "enterprise", "saas"]:
            # B2B/SaaS：推荐对比或信任导向
            return self.get_pattern("Comparison Table") or self.get_pattern("Trust Badges")

        else:
            # 默认推荐经典模式
            return self.get_pattern("Hero + Features")

    def generate_structure(self, pattern: LandingPattern) -> dict[str, Any]:
        """
        生成页面结构

        Args:
            pattern: 模式对象

        Returns:
            页面结构字典
        """
        return {
            "pattern": pattern.name,
            "description": pattern.description,
            "sections": [
                {
                    "name": section.name,
                    "type": section.type,
                    "content_hint": section.content_hint,
                    "order": section.order
                }
                for section in pattern.sections
            ],
            "cta_strategy": {
                "primary": {
                    "placement": pattern.cta_strategy.primary_placement,
                    "style": pattern.cta_strategy.style,
                    "texts": pattern.cta_strategy.text_variations[:3]
                },
                "secondary": [
                    {
                        "placement": placement,
                        "style": pattern.cta_strategy.style
                    }
                    for placement in pattern.cta_strategy.secondary_placements
                ]
            },
            "conversion_tips": pattern.conversion_tips,
            "complexity": pattern.complexity
        }

    def list_patterns(self) -> list[str]:
        """列出所有可用模式"""
        return [p.name for p in self.patterns]

    def list_categories(self) -> list[str]:
        """列出所有类别"""
        return list(set(p.category.value for p in self.patterns))


# 便捷函数
def get_landing_generator(data_dir: Path | None = None) -> LandingPatternGenerator:
    """获取 Landing 页面生成器实例"""
    return LandingPatternGenerator(data_dir)
