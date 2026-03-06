"""
开发：Excellent（11964948@qq.com）
功能：设计系统模块 - 企业级设计智能能力
作用：生成完整的设计系统、美学方向、design tokens、Landing 模式、图表推荐、UX 指南、技术栈最佳实践、代码生成
创建时间：2025-12-30
最后修改：2025-01-04
"""

from .aesthetics import AestheticDirection, AestheticDirectionType, AestheticEngine
from .charts import ChartRecommendation, ChartRecommender, ChartType, get_chart_recommender
from .codegen import (
    CodeGenerator,
    ComponentCategory,
    ComponentSnippet,
    Framework,
    GeneratedComponent,
    generate_component_snippet,
    get_code_generator,
)
from .engine import DesignIntelligenceEngine, EnhancedBM25
from .generator import DesignSystem, DesignSystemGenerator
from .landing import CTAStrategy, LandingPattern, LandingPatternGenerator, get_landing_generator
from .tech_stack import (
    PerformanceTip,
    PracticeCategory,
    StackRecommendation,
    TechBestPractice,
    TechPattern,
    TechStack,
    TechStackEngine,
    get_tech_stack_engine,
)
from .tokens import TokenGenerator
from .ui_intelligence import LibraryRecommendation, UIIntelligenceAdvisor
from .ux_guide import UXGuideEngine, UXGuideline, UXRecommendation, get_ux_guide

__all__ = [
    "DesignIntelligenceEngine",
    "EnhancedBM25",
    "DesignSystemGenerator",
    "DesignSystem",
    "AestheticEngine",
    "AestheticDirection",
    "AestheticDirectionType",
    "TokenGenerator",
    "UIIntelligenceAdvisor",
    "LibraryRecommendation",
    "LandingPatternGenerator",
    "LandingPattern",
    "CTAStrategy",
    "get_landing_generator",
    "ChartRecommender",
    "ChartType",
    "ChartRecommendation",
    "get_chart_recommender",
    "UXGuideEngine",
    "UXGuideline",
    "UXRecommendation",
    "get_ux_guide",
    # Tech Stack
    "TechStackEngine",
    "TechStack",
    "PracticeCategory",
    "TechBestPractice",
    "TechPattern",
    "PerformanceTip",
    "StackRecommendation",
    "get_tech_stack_engine",
    # Code Generator
    "CodeGenerator",
    "Framework",
    "ComponentCategory",
    "ComponentSnippet",
    "GeneratedComponent",
    "get_code_generator",
    "generate_component_snippet",
]
