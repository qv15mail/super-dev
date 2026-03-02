"""
开发：Excellent（11964948@qq.com）
功能：UX 指南数据库引擎
作用：提供 UX 最佳实践和反模式查询
创建时间：2025-01-04
最后修改：2025-01-04
"""

import csv
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class UXDomain(str, Enum):
    """UX 领域"""
    ANIMATION = "Animation"
    A11Y = "A11y"  # Accessibility
    PERFORMANCE = "Performance"
    RESPONSIVE = "Responsive"
    FORMS = "Forms"
    NAVIGATION = "Navigation"
    LOADING = "Loading"
    ERROR = "Error"
    DARK_MODE = "Dark Mode"
    I18N = "I18n"  # Internationalization


@dataclass
class UXGuideline:
    """UX 指南"""
    domain: UXDomain
    topic: str
    best_practice: str
    anti_pattern: str
    example: str
    impact: str
    complexity: str  # low, medium, high


@dataclass
class UXRecommendation:
    """UX 推荐建议"""
    guideline: UXGuideline
    priority: str  # critical, high, medium, low
    implementation_effort: str  # low, medium, high
    user_impact: str  # high, medium, low
    resources: list[str]  # 相关资源链接


class UXGuideEngine:
    """UX 指南引擎"""

    def __init__(self, data_dir: Path | None = None):
        """
        初始化引擎

        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "design"

        self.data_dir = Path(data_dir)
        self.guidelines: list[UXGuideline] = []
        self._load_guidelines()

    def _load_guidelines(self):
        """从 CSV 加载指南数据"""
        csv_path = self.data_dir / "ux_guidelines.csv"

        if not csv_path.exists():
            self.guidelines = self._get_default_guidelines()
            return

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    guideline = UXGuideline(
                        domain=UXDomain(row["domain"]),
                        topic=row["topic"],
                        best_practice=row["best_practice"],
                        anti_pattern=row["anti_pattern"],
                        example=row["example"],
                        impact=row["impact"],
                        complexity=row["complexity"]
                    )
                    self.guidelines.append(guideline)
                except Exception as e:
                    print(f"Warning: Failed to parse UX guideline: {e}")

    def _get_default_guidelines(self) -> list[UXGuideline]:
        """获取默认指南（当 CSV 不存在时）"""
        return [
            UXGuideline(
                domain=UXDomain.ANIMATION,
                topic="Loading",
                best_practice="Use skeleton screens for content loading",
                anti_pattern="Use spinners for all loading states",
                example="Skeleton while profile data loads",
                impact="Reduced perceived wait time",
                complexity="medium"
            ),
            UXGuideline(
                domain=UXDomain.A11Y,
                topic="Color",
                best_practice="Use 4.5:1 contrast ratio for text",
                anti_pattern="Light gray text on white background",
                example="Dark text on light background",
                impact="Readable by all users",
                complexity="low"
            ),
            UXGuideline(
                domain=UXDomain.PERFORMANCE,
                topic="Images",
                best_practice="Use WebP format with fallbacks",
                anti_pattern="Unoptimized 5MB PNGs",
                example="WebP with JPEG fallback",
                impact="Faster page load",
                complexity="low"
            )
        ]

    def search(
        self,
        query: str,
        domain: str | None = None,
        max_results: int = 5
    ) -> list[UXRecommendation]:
        """
        搜索 UX 指南

        Args:
            query: 搜索查询
            domain: 领域过滤
            max_results: 最大结果数

        Returns:
            推荐建议列表
        """
        query_lower = query.lower()

        # 筛选和评分
        scored_guidelines = []
        for guideline in self.guidelines:
            # 领域过滤
            if domain and guideline.domain.value.lower() != domain.lower():
                continue

            score = 0

            # 主题匹配
            if query_lower in guideline.topic.lower():
                score += 10

            # 最佳实践匹配
            if query_lower in guideline.best_practice.lower():
                score += 8

            # 反模式匹配
            if query_lower in guideline.anti_pattern.lower():
                score += 8

            # 关键词匹配（从影响描述中提取）
            words = query_lower.split()
            for word in words:
                if word in guideline.impact.lower():
                    score += 3

            if score > 0:
                # 确定优先级
                priority = self._determine_priority(guideline)

                # 确定实现难度
                effort = guideline.complexity

                # 确定用户影响
                user_impact = self._determine_user_impact(guideline)

                scored_guidelines.append((guideline, score, priority, effort, user_impact))

        # 按分数排序
        scored_guidelines.sort(key=lambda x: x[1], reverse=True)

        # 构建推荐列表
        recommendations = []
        for guideline, score, priority, effort, user_impact in scored_guidelines[:max_results]:
            recommendations.append(UXRecommendation(
                guideline=guideline,
                priority=priority,
                implementation_effort=effort,
                user_impact=user_impact,
                resources=self._get_resources(guideline)
            ))

        return recommendations

    def _determine_priority(self, guideline: UXGuideline) -> str:
        """确定优先级"""
        # 无障碍性通常是关键优先级
        if guideline.domain == UXDomain.A11Y:
            return "critical"

        # 性能影响通常是高优先级
        if guideline.domain == UXDomain.PERFORMANCE:
            return "high"

        # 基于复杂度确定优先级
        if guideline.complexity == "low":
            return "high"  # 容易实现的优先级高

        return "medium"

    def _determine_user_impact(self, guideline: UXGuideline) -> str:
        """确定用户影响"""
        # 从影响描述中推断
        impact_lower = guideline.impact.lower()

        if any(word in impact_lower for word in ["all users", "everyone", "critical", "essential"]):
            return "high"

        if any(word in impact_lower for word in ["some users", "improved", "better"]):
            return "medium"

        return "low"

    def _get_resources(self, guideline: UXGuideline) -> list[str]:
        """获取相关资源"""
        resources = []

        # 基于领域添加资源
        domain_resources = {
            UXDomain.A11Y: [
                "WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/",
                "WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/"
            ],
            UXDomain.PERFORMANCE: [
                "Web.dev Performance: https://web.dev/performance/",
                "Google Lighthouse: https://developers.google.com/web/tools/lighthouse"
            ],
            UXDomain.RESPONSIVE: [
                "MDN Responsive Design: https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design"
            ],
            UXDomain.ANIMATION: [
                "Motion Design Guidelines: https://material.io/design/motion"
            ]
        }

        resources.extend(domain_resources.get(guideline.domain, []))

        return resources

    def get_guidelines_by_domain(self, domain: str) -> list[UXGuideline]:
        """
        按领域获取指南

        Args:
            domain: 领域名称

        Returns:
            该领域的所有指南
        """
        domain_lower = domain.lower()
        return [
            g for g in self.guidelines
            if g.domain.value.lower() == domain_lower
        ]

    def get_quick_wins(self, max_results: int = 5) -> list[UXRecommendation]:
        """
        获取快速见效的改进（低复杂度、高影响）

        Args:
            max_results: 最大结果数

        Returns:
            快速见效的建议列表
        """
        quick_wins = []

        for guideline in self.guidelines:
            # 低复杂度
            if guideline.complexity == "low":
                user_impact = self._determine_user_impact(guideline)

                # 高或中等影响
                if user_impact in ["high", "medium"]:
                    quick_wins.append(UXRecommendation(
                        guideline=guideline,
                        priority="high",
                        implementation_effort="low",
                        user_impact=user_impact,
                        resources=self._get_resources(guideline)
                    ))

        # 按领域分组，避免同一领域的建议过多
        from collections import defaultdict
        domain_groups = defaultdict(list)
        for rec in quick_wins:
            domain_groups[rec.guideline.domain].append(rec)

        # 从每个领域选择最好的
        result: list[UXRecommendation] = []
        domains = list(domain_groups.keys())
        random.shuffle(domains)

        while len(result) < max_results and domains:
            domain = domains.pop(0)
            if domain_groups[domain]:
                result.append(domain_groups[domain].pop(0))

        return result

    def get_checklist(self, domains: list[str] | None = None) -> dict[str, list[str]]:
        """
        获取 UX 检查清单

        Args:
            domains: 要包含的领域列表，None 表示全部

        Returns:
            按领域分组的检查清单
        """
        checklist: dict[str, list[str]] = {}

        for guideline in self.guidelines:
            domain = guideline.domain.value

            # 领域过滤
            if domains and domain not in domains:
                continue

            if domain not in checklist:
                checklist[domain] = []

            checklist[domain].append(
                f"[ ] {guideline.best_practice}"
            )

        return checklist

    def get_anti_patterns(self) -> dict[str, list[dict[str, str]]]:
        """
        获取所有反模式

        Returns:
            按领域分组的反模式
        """
        anti_patterns: dict[str, list[dict[str, str]]] = {}

        for guideline in self.guidelines:
            domain = guideline.domain.value

            if domain not in anti_patterns:
                anti_patterns[domain] = []

            anti_patterns[domain].append({
                "anti_pattern": guideline.anti_pattern,
                "best_practice": guideline.best_practice,
                "impact": guideline.impact
            })

        return anti_patterns

    def list_domains(self) -> list[str]:
        """列出所有领域"""
        return list(set(g.domain.value for g in self.guidelines))

    def list_topics(self, domain: str | None = None) -> list[str]:
        """
        列出所有主题

        Args:
            domain: 可选的领域过滤

        Returns:
            主题列表
        """
        if domain:
            guidelines = self.get_guidelines_by_domain(domain)
            return list(set(g.topic for g in guidelines))

        return list(set(g.topic for g in self.guidelines))


# 便捷函数
def get_ux_guide(data_dir: Path | None = None) -> UXGuideEngine:
    """获取 UX 指南引擎实例"""
    return UXGuideEngine(data_dir)
