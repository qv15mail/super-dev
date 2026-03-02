"""
开发：Excellent（11964948@qq.com）
功能：图表类型推荐引擎
作用：根据数据类型和可视化需求推荐最佳图表类型
创建时间：2025-01-04
最后修改：2025-01-04
"""

import csv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ChartCategory(str, Enum):
    """图表类别"""
    TIME_SERIES = "Time Series"
    CATEGORICAL = "Categorical"
    PROPORTION = "Proportion"
    CORRELATION = "Correlation"
    DISTRIBUTION = "Distribution"
    HIERARCHICAL = "Hierarchical"
    GEOGRAPHIC = "Geographic"
    FINANCIAL = "Financial"
    FLOW = "Flow"
    MULTIVARIATE = "Multivariate"
    STATISTICAL = "Statistical"


class DataType(str, Enum):
    """数据类型"""
    CONTINUOUS = "Continuous"
    DISCRETE = "Discrete"
    PART_TO_WHOLE = "Part-to-whale"
    TWO_DIMENSIONAL = "Two-dimensional"
    THREE_DIMENSIONAL = "Three-dimensional"
    SEQUENTIAL = "Sequential"
    SPATIAL = "Spatial"
    SINGLE_VALUE = "Single-value"
    DIRECTIONAL = "Directional"


@dataclass
class ChartType:
    """图表类型"""
    name: str
    category: ChartCategory
    data_type: DataType
    description: str
    best_libraries: list[str]  # Chart.js, Recharts, D3.js, etc.
    accessibility_notes: str
    use_cases: list[str]
    limitations: list[str]
    keywords: list[str]


@dataclass
class ChartRecommendation:
    """图表推荐"""
    chart_type: ChartType
    confidence: float  # 0-1
    reasoning: str
    alternatives: list[ChartType]
    library_recommendation: str
    accessibility_considerations: list[str]


class ChartRecommender:
    """图表类型推荐引擎"""

    # 推荐的图表库
    RECOMMENDED_LIBRARIES = {
        "react": ["Recharts", "Chart.js", "Nivo"],
        "vue": ["Chart.js", "ECharts", "ApexCharts"],
        "svelte": ["Chart.js", "Plotly"],
        "vanilla": ["Chart.js", "Plotly", "D3.js", "ECharts"],
        "angular": ["Chart.js", "Ngx-Chart", "ECharts"],
        "next": ["Recharts", "Chart.js", "Nivo", "Tremor"],
    }

    def __init__(self, data_dir: Path | None = None):
        """
        初始化推荐引擎

        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "design"

        self.data_dir = Path(data_dir)
        self.chart_types: list[ChartType] = []
        self._load_chart_types()

    def _load_chart_types(self):
        """从 CSV 加载图表类型数据"""
        csv_path = self.data_dir / "chart_types.csv"

        if not csv_path.exists():
            self.chart_types = self._get_default_chart_types()
            return

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    chart_type = ChartType(
                        name=row["name"],
                        category=ChartCategory(row["category"]),
                        data_type=DataType(row["data_type"]),
                        description=row["description"],
                        best_libraries=row["best_libraries"].split(","),
                        accessibility_notes=row["accessibility_notes"],
                        use_cases=row["use_cases"].split(","),
                        limitations=row["limitations"].split(",") if row.get("limitations") else [],
                        keywords=row["keywords"].split(",") if row.get("keywords") else []
                    )
                    self.chart_types.append(chart_type)
                except Exception as e:
                    print(f"Warning: Failed to parse chart type: {e}")

    def _get_default_chart_types(self) -> list[ChartType]:
        """获取默认图表类型（当 CSV 不存在时）"""
        return [
            ChartType(
                name="Line Chart",
                category=ChartCategory.TIME_SERIES,
                data_type=DataType.CONTINUOUS,
                description="Trends over time",
                best_libraries=["Chart.js", "Recharts", "Highcharts"],
                accessibility_notes="Provide data table as fallback",
                use_cases=["Stock prices", "Weather", "Temperature"],
                limitations=["Not for categorical data"],
                keywords=["line", "trend", "time", "series"]
            ),
            ChartType(
                name="Bar Chart",
                category=ChartCategory.CATEGORICAL,
                data_type=DataType.DISCRETE,
                description="Comparing categories",
                best_libraries=["Chart.js", "Recharts", "ECharts"],
                accessibility_notes="Use sufficient color contrast",
                use_cases=["Sales by region", "Survey results", "Population"],
                limitations=["Not for many categories"],
                keywords=["bar", "column", "compare", "categorical"]
            ),
            ChartType(
                name="Pie Chart",
                category=ChartCategory.PROPORTION,
                data_type=DataType.PART_TO_WHOLE,
                description="Showing proportions",
                best_libraries=["Chart.js", "ECharts", "D3.js"],
                accessibility_notes="Provide legend and percentages",
                use_cases=["Market share", "Budget allocation", "Demographics"],
                limitations=["Not for more than 5-7 categories"],
                keywords=["pie", "proportion", "percentage"]
            )
        ]

    def recommend(
        self,
        data_description: str,
        framework: str = "react",
        max_results: int = 3
    ) -> list[ChartRecommendation]:
        """
        推荐图表类型

        Args:
            data_description: 数据描述（如 "time series sales data"）
            framework: 前端框架
            max_results: 最大结果数

        Returns:
            推荐列表
        """
        desc_lower = data_description.lower()

        # 分析数据描述
        analysis = self._analyze_description(data_description)

        # 评分和排序
        scored_charts = []
        for chart_type in self.chart_types:
            score = 0
            reasons = []

            # 数据类型匹配
            if chart_type.data_type.value.lower() in desc_lower:
                score += 10
                reasons.append(f"Matches {chart_type.data_type.value} data type")

            # 类别匹配
            if chart_type.category.value.lower() in desc_lower:
                score += 8
                reasons.append(f"Matches {chart_type.category.value} category")

            # 关键词匹配
            for keyword in chart_type.keywords:
                if keyword.lower() in desc_lower:
                    score += 5
                    reasons.append(f"Keyword '{keyword}' matched")

            # 用例匹配
            for use_case in chart_type.use_cases:
                if use_case.lower() in desc_lower:
                    score += 7
                    reasons.append(f"Use case '{use_case}' matched")

            # 基于分析的其他匹配
            if analysis.get("has_time_component") and chart_type.category == ChartCategory.TIME_SERIES:
                score += 10
                reasons.append("Time series data detected")

            if analysis.get("has_comparison") and chart_type.category == ChartCategory.CATEGORICAL:
                score += 8
                reasons.append("Comparison data detected")

            if analysis.get("has_proportions") and chart_type.category == ChartCategory.PROPORTION:
                score += 8
                reasons.append("Proportion data detected")

            if score > 0:
                # 计算置信度 (0-1)
                confidence = min(score / 30, 1.0)

                # 获取替代方案
                alternatives = self._get_alternatives(chart_type, framework)

                # 推荐库
                lib_rec = self._recommend_library(chart_type, framework)

                # 无障碍考虑
                a11y_considerations = self._get_accessibility_considerations(chart_type)

                scored_charts.append(ChartRecommendation(
                    chart_type=chart_type,
                    confidence=confidence,
                    reasoning="; ".join(reasons),
                    alternatives=alternatives[:2],
                    library_recommendation=lib_rec,
                    accessibility_considerations=a11y_considerations
                ))

        # 按置信度排序
        scored_charts.sort(key=lambda x: x.confidence, reverse=True)

        return scored_charts[:max_results]

    def _analyze_description(self, description: str) -> dict[str, bool]:
        """分析数据描述"""
        desc_lower = description.lower()

        return {
            "has_time_component": any(word in desc_lower for word in [
                "time", "date", "month", "year", "trend", "over time", "series"
            ]),
            "has_comparison": any(word in desc_lower for word in [
                "compare", "vs", "versus", "between", "across", "by region", "by category"
            ]),
            "has_proportions": any(word in desc_lower for word in [
                "percentage", "proportion", "share", "of total", "breakdown", "part of"
            ]),
            "has_correlation": any(word in desc_lower for word in [
                "relationship", "correlation", "vs", "relationship between"
            ]),
            "has_distribution": any(word in desc_lower for word in [
                "distribution", "frequency", "histogram", "spread", "range"
            ]),
            "has_geography": any(word in desc_lower for word in [
                "map", "region", "country", "state", "location", "geographic"
            ])
        }

    def _get_alternatives(self, chart_type: ChartType, framework: str) -> list[ChartType]:
        """获取替代图表类型"""
        alternatives = []

        # 基于类别找替代方案
        for other_chart in self.chart_types:
            if other_chart.name == chart_type.name:
                continue

            # 同类别但不同类型
            if other_chart.category == chart_type.category and other_chart.data_type != chart_type.data_type:
                alternatives.append(other_chart)

            # 相似的用例
            if any(use_case in chart_type.use_cases for use_case in other_chart.use_cases):
                alternatives.append(other_chart)

        return alternatives[:5]

    def _recommend_library(self, chart_type: ChartType, framework: str) -> str:
        """推荐图表库"""
        # 获取框架特定的推荐
        framework_libs = self.RECOMMENDED_LIBRARIES.get(framework.lower(), self.RECOMMENDED_LIBRARIES["vanilla"])

        # 找到图表类型支持的库
        for lib in framework_libs:
            if lib in chart_type.best_libraries:
                return lib

        # 如果没有完美匹配，返回第一个推荐的库
        return chart_type.best_libraries[0] if chart_type.best_libraries else "Chart.js"

    def _get_accessibility_considerations(self, chart_type: ChartType) -> list[str]:
        """获取无障碍考虑事项"""
        considerations = [chart_type.accessibility_notes]

        # 基于类别的额外考虑
        if chart_type.category == ChartCategory.TIME_SERIES:
            considerations.append("Ensure color differences are distinguishable by all users")
            considerations.append("Provide data table for screen reader users")

        elif chart_type.category == ChartCategory.CATEGORICAL:
            considerations.append("Use distinct colors or patterns for each category")
            considerations.append("Ensure labels are readable")

        elif chart_type.category == ChartCategory.PROPORTION:
            considerations.append("Order segments consistently")
            considerations.append("Include percentages in labels")

        return considerations

    def search(self, query: str, max_results: int = 5) -> list[ChartType]:
        """
        搜索图表类型

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            匹配的图表类型列表
        """
        query_lower = query.lower()
        scored_charts = []

        for chart_type in self.chart_types:
            score = 0

            # 名称匹配
            if query_lower in chart_type.name.lower():
                score += 10

            # 类别匹配
            if query_lower in chart_type.category.value.lower():
                score += 8

            # 关键词匹配
            for keyword in chart_type.keywords:
                if query_lower in keyword.lower():
                    score += 5

            # 用例匹配
            for use_case in chart_type.use_cases:
                if query_lower in use_case.lower():
                    score += 5

            if score > 0:
                scored_charts.append((chart_type, score))

        # 按分数排序
        scored_charts.sort(key=lambda x: x[1], reverse=True)

        return [chart for chart, _ in scored_charts[:max_results]]

    def get_chart_type(self, name: str) -> ChartType | None:
        """
        获取指定名称的图表类型

        Args:
            name: 图表类型名称

        Returns:
            图表类型对象或 None
        """
        for chart_type in self.chart_types:
            if chart_type.name.lower() == name.lower():
                return chart_type
        return None

    def list_categories(self) -> list[str]:
        """列出所有类别"""
        return list(set(c.category.value for c in self.chart_types))

    def list_chart_types(self) -> list[str]:
        """列出所有图表类型"""
        return [c.name for c in self.chart_types]


# 便捷函数
def get_chart_recommender(data_dir: Path | None = None) -> ChartRecommender:
    """获取图表推荐引擎实例"""
    return ChartRecommender(data_dir)
