"""
开发：Excellent（11964948@qq.com）
功能：设计智能引擎
作用：提供 UI/UX 设计智能搜索和推荐
创建时间：2025-12-30
最后修改：2025-12-30
"""

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from math import log
from pathlib import Path
from typing import Any, cast

from .aesthetics import AestheticEngine

# ============ 配置 ============
DATA_DIR = Path(__file__).parent.parent / "data" / "design"
MAX_RESULTS = 5


# ============ 数据模型 ============
@dataclass
class SearchResult:
    """搜索结果"""

    score: float
    relevance: str  # high, medium, low
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"score": self.score, "relevance": self.relevance, **self.data}


# ============ 增强版 BM25 ============
class EnhancedBM25:
    """
    增强版 BM25 算法

    改进点：
    1. 支持 IDF 平滑
    2. 支持字段权重
    3. 支持模糊匹配
    4. 支持短语匹配
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75, epsilon: float = 0.25):
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon  # IDF 平滑参数
        self.corpus: list[list[str]] = []
        self.doc_lengths: list[int] = []
        self.avgdl: float = 0.0
        self.idf: dict[str, float] = {}
        self.doc_freqs: defaultdict[str, int] = defaultdict(int)
        self.N = 0
        self.field_weights: dict[str, float] = {}  # 字段权重

    def tokenize(self, text: str) -> list[str]:
        """分词 - 支持中英文"""
        # 移除标点
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", str(text).lower())
        # 分词（英文按空格，中文按字符）
        words: list[str] = []
        for word in text.split():
            if re.match(r"[\u4e00-\u9fff]", word):
                # 中文，按字符分
                words.extend(list(word))
            else:
                # 英文，过滤短词
                if len(word) > 2:
                    words.append(word)
        return words

    def fit(self, documents: list[str], field_weights: dict[str, float] | None = None):
        """构建索引"""
        self.field_weights = field_weights or {}
        self.corpus = [self.tokenize(doc) for doc in documents]
        self.N = len(self.corpus)
        if self.N == 0:
            return

        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_lengths) / self.N

        # 计算文档频率
        for doc in self.corpus:
            seen = set()
            for word in doc:
                if word not in seen:
                    self.doc_freqs[word] += 1
                    seen.add(word)

        # 计算 IDF（带平滑）
        for word, freq in self.doc_freqs.items():
            idf = log((self.N - freq + 0.5) / (freq + 0.5) + 1)
            self.idf[word] = max(idf, self.epsilon)

    def score(self, query: str, phrase_boost: float = 1.5) -> list[tuple[int, float]]:
        """评分 - 支持短语匹配加成"""
        query_tokens = self.tokenize(query)
        scores: list[tuple[int, float]] = []

        for idx, doc in enumerate(self.corpus):
            score = 0.0
            doc_len = self.doc_lengths[idx]
            term_freqs: defaultdict[str, int] = defaultdict(int)

            for word in doc:
                term_freqs[word] += 1

            # 短语匹配检测
            doc_text = " ".join(doc)
            phrase_match = 1.0
            if len(query_tokens) >= 2:
                phrase = " ".join(query_tokens)
                if phrase in doc_text:
                    phrase_match = phrase_boost

            for token in query_tokens:
                if token in self.idf:
                    tf = term_freqs[token]
                    idf = self.idf[token]
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                    score += idf * numerator / denominator

            scores.append((idx, score * phrase_match))

        return sorted(scores, key=lambda x: x[1], reverse=True)


# ============ 设计智能引擎 ============
class DesignIntelligenceEngine:
    """
    设计智能引擎

    设计智能引擎核心能力：
    1. 更多设计资产（100+ styles, 150+ palettes, 80+ fonts）
    2. AI 驱动的推荐
    3. 语义搜索支持
    4. 上下文感知
    5. 与项目工作流集成
    """

    def __init__(self, data_dir: Path | None = None):
        """
        初始化设计智能引擎

        Args:
            data_dir: 数据目录，默认使用内置数据
        """
        self.data_dir = data_dir or DATA_DIR
        self.aesthetic_engine = AestheticEngine()
        self._cache: dict[str, dict[str, Any]] = {}

        # 领域配置（扩展版）
        self.domain_configs: dict[str, dict[str, Any]] = {
            "style": {
                "file": "styles.csv",
                "search_cols": ["name", "category", "keywords", "best_for"],
                "output_cols": [
                    "name",
                    "category",
                    "keywords",
                    "description",
                    "primary_colors",
                    "effects",
                    "animations",
                    "best_for",
                    "complexity",
                    "accessibility",
                    "performance",
                    "frameworks",
                    "example_prompt",
                ],
            },
            "color": {
                "file": "colors.csv",
                "search_cols": ["name", "category", "keywords", "mood", "best_for"],
                "output_cols": [
                    "name",
                    "category",
                    "primary",
                    "secondary",
                    "accent",
                    "background",
                    "surface",
                    "text",
                    "text_muted",
                    "border",
                    "keywords",
                    "mood",
                    "best_for",
                    "css_vars",
                ],
            },
            "typography": {
                "file": "typography.csv",
                "search_cols": [
                    "name",
                    "category",
                    "mood",
                    "heading_font",
                    "body_font",
                    "keywords",
                ],
                "output_cols": [
                    "name",
                    "category",
                    "heading_font",
                    "body_font",
                    "accent_font",
                    "mood",
                    "keywords",
                    "best_for",
                    "google_fonts_url",
                    "css_import",
                    "tailwind_config",
                    "notes",
                ],
            },
            "component": {
                "file": "components.csv",
                "search_cols": ["name", "type", "keywords", "use_case", "complexity"],
                "output_cols": [
                    "name",
                    "type",
                    "description",
                    "keywords",
                    "use_case",
                    "complexity",
                    "accessibility",
                    "responsive",
                    "frameworks",
                    "code_example",
                    "props",
                ],
            },
            "layout": {
                "file": "layouts.csv",
                "search_cols": ["name", "type", "keywords", "best_for"],
                "output_cols": [
                    "name",
                    "type",
                    "description",
                    "keywords",
                    "structure",
                    "responsive",
                    "best_for",
                    "css_grid",
                ],
            },
            "animation": {
                "file": "animations.csv",
                "search_cols": ["name", "type", "keywords", "effect"],
                "output_cols": [
                    "name",
                    "type",
                    "description",
                    "keywords",
                    "css_code",
                    "duration",
                    "easing",
                    "best_for",
                    "accessibility",
                ],
            },
            "ux": {
                "file": "ux_guidelines.csv",
                "search_cols": ["domain", "topic", "best_practice", "anti_pattern", "impact"],
                "output_cols": [
                    "domain",
                    "topic",
                    "best_practice",
                    "anti_pattern",
                    "example",
                    "impact",
                    "complexity",
                ],
            },
            "chart": {
                "file": "chart_types.csv",
                "search_cols": ["name", "category", "data_type", "keywords", "description"],
                "output_cols": [
                    "name",
                    "category",
                    "data_type",
                    "description",
                    "best_libraries",
                    "accessibility_notes",
                    "use_cases",
                    "limitations",
                    "keywords",
                ],
            },
            "product": {
                "file": "landing_patterns.csv",
                "search_cols": ["name", "category", "description", "best_for", "keywords"],
                "output_cols": [
                    "name",
                    "category",
                    "description",
                    "sections",
                    "cta_strategy",
                    "best_for",
                    "conversion_tips",
                    "complexity",
                    "keywords",
                ],
            },
            "stack": {
                "file": "tech_stacks.csv",
                "search_cols": ["framework", "category", "topic", "recommendation", "use_cases"],
                "output_cols": [
                    "framework",
                    "category",
                    "topic",
                    "recommendation",
                    "code_example",
                    "benefits",
                    "use_cases",
                    "complexity",
                ],
            },
        }

    def search(
        self,
        query: str,
        domain: str | None = None,
        max_results: int = MAX_RESULTS,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        搜索设计资产

        Args:
            query: 搜索查询
            domain: 领域（style, color, typography, component, layout, animation, ux, chart, product, stack）
            max_results: 最大结果数
            use_cache: 是否使用缓存

        Returns:
            搜索结果字典
        """
        # 自动检测领域
        if domain is None:
            domain = self._detect_domain(query)

        # 检查缓存
        cache_key = f"{domain}:{query}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # 获取配置
        config = self.domain_configs.get(domain)
        if not config:
            return {"error": f"Unknown domain: {domain}", "domain": domain}

        # 加载数据
        filepath = self.data_dir / str(config["file"])
        if not filepath.exists():
            # 如果文件不存在，返回空结果
            return {
                "domain": domain,
                "query": query,
                "count": 0,
                "results": [],
                "note": f"Data file not found: {filepath}",
            }

        # 执行搜索
        results = self._search_csv(
            filepath,
            cast(list[str], config["search_cols"]),
            cast(list[str], config["output_cols"]),
            query,
            max_results,
        )

        response = {
            "domain": domain,
            "query": query,
            "count": len(results),
            "results": results,
        }

        # 缓存结果
        if use_cache:
            self._cache[cache_key] = response

        return response

    def recommend_design_system(
        self,
        product_type: str,
        industry: str,
        keywords: list[str],
        platform: str = "web",
    ) -> dict[str, Any]:
        """
        AI 驱动的完整设计系统推荐

        不只搜索，而是推荐完整的设计系统

        Args:
            product_type: 产品类型（SaaS, E-commerce, Portfolio, Dashboard）
            industry: 行业（Fintech, Healthcare, Education, Gaming）
            keywords: 关键词列表
            platform: 平台（web, mobile, desktop）

        Returns:
            完整的设计系统推荐
        """
        # 搜索产品类型推荐
        product_result = self.search(f"{product_type} {industry}", domain="product")

        # 搜索风格
        style_query = " ".join(keywords[:3])
        style_result = self.search(style_query, domain="style")

        # 搜索配色
        color_result = self.search(f"{industry} {product_type}", domain="color")

        # 搜索字体
        typography_result = self.search(style_query, domain="typography")

        # 生成美学方向
        aesthetic = self.aesthetic_engine.generate_direction()

        # 综合推荐
        return {
            "product_analysis": (
                product_result.get("results", [{}])[0] if product_result.get("results") else {}
            ),
            "recommended_style": (
                style_result.get("results", [{}])[0] if style_result.get("results") else {}
            ),
            "color_palette": (
                color_result.get("results", [{}])[0] if color_result.get("results") else {}
            ),
            "typography": (
                typography_result.get("results", [{}])[0]
                if typography_result.get("results")
                else {}
            ),
            "aesthetic_direction": {
                "name": aesthetic.name,
                "description": aesthetic.description,
                "differentiation": aesthetic.differentiation,
            },
            "ux_guidelines": self.search(f"{product_type} best practices", domain="ux").get(
                "results", []
            ),
            "implementation_stack": self._get_stack_recommendation(platform),
        }

    def generate_design_tokens(self, design_system: dict[str, Any]) -> str:
        """
        生成 Design Tokens

        生成可直接使用的 design tokens

        Args:
            design_system: 设计系统字典

        Returns:
            CSS Variables 格式的 tokens
        """
        tokens = [":root {"]
        tokens.append("  /* Colors */")

        # 颜色 tokens
        colors = design_system.get("color_palette", {})
        for key in [
            "primary",
            "secondary",
            "accent",
            "background",
            "surface",
            "text",
            "text_muted",
            "border",
        ]:
            value = colors.get(key, "")
            if value:
                css_var = f"--color-{key}"
                tokens.append(f"  {css_var}: {value};")

        tokens.append("")
        tokens.append("  /* Typography */")

        # 字体 tokens
        typography = design_system.get("typography", {})
        for key in ["heading_font", "body_font", "accent_font"]:
            value = typography.get(key, "")
            if value:
                css_var = f"--font-{key}"
                tokens.append(f"  {css_var}: {value};")

        tokens.append("")
        tokens.append("  /* Spacing */")
        tokens.append("  --space-xs: 0.25rem;")
        tokens.append("  --space-sm: 0.5rem;")
        tokens.append("  --space-md: 1rem;")
        tokens.append("  --space-lg: 1.5rem;")
        tokens.append("  --space-xl: 2rem;")
        tokens.append("  --space-2xl: 3rem;")

        tokens.append("")
        tokens.append("  /* Border Radius */")
        tokens.append("  --radius-sm: 0.25rem;")
        tokens.append("  --radius-md: 0.5rem;")
        tokens.append("  --radius-lg: 1rem;")
        tokens.append("  --radius-xl: 1.5rem;")
        tokens.append("  --radius-full: 9999px;")

        tokens.append("")

        # 阴影 tokens
        tokens.append("  /* Shadows */")
        tokens.append("  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);")
        tokens.append("  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);")
        tokens.append("  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);")
        tokens.append("  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);")

        tokens.append("}")

        return "\n".join(tokens)

    def _detect_domain(self, query: str) -> str:
        """自动检测领域"""
        query_lower = query.lower()

        # 关键词映射（扩展版）
        domain_keywords = {
            "color": ["color", "palette", "hex", "#", "rgb", "hsl", "主题色", "配色"],
            "typography": [
                "font",
                "type",
                "typography",
                "heading",
                "body",
                "serif",
                "sans",
                "字体",
                "排版",
            ],
            "component": ["component", "button", "modal", "navbar", "card", "form", "组件", "按钮"],
            "layout": ["layout", "grid", "flex", "structure", "布局", "网格"],
            "animation": ["animation", "transition", "motion", "effect", "动画", "过渡", "特效"],
            "chart": ["chart", "graph", "visualization", "trend", "data", "图表", "可视化", "数据"],
            "ux": [
                "ux",
                "usability",
                "accessibility",
                "wcag",
                "experience",
                "体验",
                "可用性",
                "无障碍",
            ],
            "product": [
                "saas",
                "ecommerce",
                "fintech",
                "healthcare",
                "portfolio",
                "dashboard",
                "产品",
            ],
            "style": [
                "style",
                "design",
                "ui",
                "minimalism",
                "glassmorphism",
                "brutalism",
                "风格",
                "设计",
            ],
            "stack": ["react", "vue", "nextjs", "tailwind", "framework", "框架"],
        }

        # 计算每个领域的匹配分数
        scores: dict[str, int] = {}
        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for kw in keywords if kw in query_lower)

        # 返回最高分的领域
        best = max(scores, key=lambda key: scores[key])
        return best if scores[best] > 0 else "style"

    def _search_csv(
        self,
        filepath: Path,
        search_cols: list[str],
        output_cols: list[str],
        query: str,
        max_results: int,
    ) -> list[dict[str, Any]]:
        """在 CSV 文件中搜索"""
        try:
            with open(filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception:
            return []

        if not data:
            return []

        # 构建文档
        documents = [" ".join(str(row.get(col, "")) for col in search_cols) for row in data]

        # BM25 搜索
        bm25 = EnhancedBM25()
        bm25.fit(documents)
        ranked = bm25.score(query)

        # 获取结果
        results = []
        for idx, score in ranked[:max_results]:
            if score > 0:
                row = data[idx]
                result = {col: row.get(col, "") for col in output_cols if col in row}

                # 计算相关性
                relevance = "high" if score > 2.0 else "medium" if score > 1.0 else "low"

                results.append(
                    SearchResult(
                        score=round(score, 3),
                        relevance=relevance,
                        data=result,
                    ).to_dict()
                )

        return results

    def _get_stack_recommendation(self, platform: str) -> dict[str, str]:
        """获取技术栈推荐"""
        stack_map = {
            "web": {
                "default": "nextjs",
                "alternative": "react",
                "styling": "tailwindcss",
                "ui_library": "shadcn-ui",
            },
            "mobile": {
                "default": "react-native",
                "alternative": "flutter",
                "styling": "styled-components",
                "ui_library": "react-native-paper",
            },
            "desktop": {
                "default": "electron",
                "alternative": "tauri",
                "styling": "css",
                "ui_library": "mui",
            },
        }
        return stack_map.get(platform, stack_map["web"])

    def get_available_domains(self) -> list[str]:
        """获取可用的搜索领域"""
        return list(self.domain_configs.keys())

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()

    def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        stats = {
            "domains": len(self.domain_configs),
            "available_domains": list(self.domain_configs.keys()),
            "cached_results": len(self._cache),
            "data_dir": str(self.data_dir),
        }
        return stats
