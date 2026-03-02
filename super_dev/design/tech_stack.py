"""
开发：Excellent（11964948@qq.com）
功能：技术栈最佳实践引擎
作用：提供各技术栈的最佳实践、性能优化和常见模式
创建时间：2025-01-04
最后修改：2025-01-04
"""

import csv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TechStack(str, Enum):
    """技术栈枚举"""
    NEXTJS = "Next.js"
    REMIX = "Remix"
    REACT = "React"
    VUE = "Vue"
    SVELTEKIT = "SvelteKit"
    ANGULAR = "Angular"
    ASTRO = "Astro"
    SOLIDJS = "SolidJS"
    QWIK = "Qwik"
    SWIFTUI = "SwiftUI"
    REACT_NATIVE = "React Native"
    FLUTTER = "Flutter"


class PracticeCategory(str, Enum):
    """实践类别"""
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    STATE_MANAGEMENT = "state_management"
    STYLING = "styling"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"


@dataclass
class TechBestPractice:
    """技术栈最佳实践"""
    stack: TechStack
    category: PracticeCategory
    topic: str
    practice: str
    anti_pattern: str
    code_example: str
    benefits: str
    complexity: str  # low, medium, high


@dataclass
class TechPattern:
    """设计模式"""
    stack: TechStack
    name: str
    description: str
    use_case: str
    implementation: str
    pros: list[str]
    cons: list[str]


@dataclass
class PerformanceTip:
    """性能优化建议"""
    stack: TechStack
    topic: str
    technique: str
    impact: str  # high, medium, low
    effort: str  # low, medium, high
    description: str
    code_snippet: str


@dataclass
class StackRecommendation:
    """技术栈推荐"""
    practice: TechBestPractice
    priority: str  # critical, high, medium, low
    context: str
    alternatives: list[str]
    resources: list[str]


class TechStackEngine:
    """技术栈引擎"""

    def __init__(self, data_dir: Path | None = None):
        """
        初始化引擎

        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "design"

        self.data_dir = Path(data_dir)
        self.practices: list[TechBestPractice] = []
        self.patterns: list[TechPattern] = []
        self.performance_tips: list[PerformanceTip] = []
        self._load_data()

    def _load_data(self):
        """从 CSV 加载数据"""
        # 加载最佳实践
        practices_path = self.data_dir / "tech_practices.csv"
        if practices_path.exists():
            self._load_practices(practices_path)
        else:
            self.practices = self._get_default_practices()

        # 加载设计模式
        patterns_path = self.data_dir / "tech_patterns.csv"
        if patterns_path.exists():
            self._load_patterns(patterns_path)
        else:
            self.patterns = self._get_default_patterns()

        # 加载性能建议
        performance_path = self.data_dir / "tech_performance.csv"
        if performance_path.exists():
            self._load_performance(performance_path)
        else:
            self.performance_tips = self._get_default_performance()

    def _load_practices(self, csv_path: Path):
        """加载最佳实践数据"""
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    practice = TechBestPractice(
                        stack=TechStack(row["stack"]),
                        category=PracticeCategory(row["category"]),
                        topic=row["topic"],
                        practice=row["practice"],
                        anti_pattern=row["anti_pattern"],
                        code_example=row["code_example"],
                        benefits=row["benefits"],
                        complexity=row["complexity"]
                    )
                    self.practices.append(practice)
                except Exception as e:
                    print(f"Warning: Failed to parse practice: {e}")

    def _load_patterns(self, csv_path: Path):
        """加载设计模式数据"""
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    pattern = TechPattern(
                        stack=TechStack(row["stack"]),
                        name=row["name"],
                        description=row["description"],
                        use_case=row["use_case"],
                        implementation=row["implementation"],
                        pros=row["pros"].split(";"),
                        cons=row["cons"].split(";")
                    )
                    self.patterns.append(pattern)
                except Exception as e:
                    print(f"Warning: Failed to parse pattern: {e}")

    def _load_performance(self, csv_path: Path):
        """加载性能建议数据"""
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    tip = PerformanceTip(
                        stack=TechStack(row["stack"]),
                        topic=row["topic"],
                        technique=row["technique"],
                        impact=row["impact"],
                        effort=row["effort"],
                        description=row["description"],
                        code_snippet=row["code_snippet"]
                    )
                    self.performance_tips.append(tip)
                except Exception as e:
                    print(f"Warning: Failed to parse performance tip: {e}")

    def _get_default_practices(self) -> list[TechBestPractice]:
        """获取默认最佳实践"""
        return [
            TechBestPractice(
                stack=TechStack.NEXTJS,
                category=PracticeCategory.ARCHITECTURE,
                topic="Server Components",
                practice="Use Server Components by default, Client Components only when needed",
                anti_pattern="Mark all components with 'use client'",
                code_example="// Server Component (default)\nexport default function Profile() {\n  return <div>{user.name}</div>\n}\n\n// Client Component\n'use client'\nexport function Button() { return <button>Click</button> }",
                benefits="Reduced bundle size, improved performance, simpler data fetching",
                complexity="low"
            ),
            TechBestPractice(
                stack=TechStack.REACT,
                category=PracticeCategory.PERFORMANCE,
                topic="Code Splitting",
                practice="Use React.lazy and Suspense for route-based code splitting",
                anti_pattern="Load entire application bundle upfront",
                code_example="const Dashboard = React.lazy(() => import('./Dashboard'));\n\n<Suspense fallback={<Loading />}>\n  <Dashboard />\n</Suspense>",
                benefits="Faster initial load, better user experience",
                complexity="medium"
            ),
            TechBestPractice(
                stack=TechStack.VUE,
                category=PracticeCategory.STATE_MANAGEMENT,
                topic="Composition API",
                practice="Use Composition API with <script setup> syntax",
                anti_pattern="Mix Options API and Composition API",
                code_example="<script setup>\nimport { ref, computed } from 'vue'\nconst count = ref(0)\nconst doubled = computed(() => count.value * 2)\n</script>",
                benefits="Better type inference, code organization, tree-shaking",
                complexity="low"
            )
        ]

    def _get_default_patterns(self) -> list[TechPattern]:
        """获取默认设计模式"""
        return [
            TechPattern(
                stack=TechStack.NEXTJS,
                name="Parallel Routes",
                description="Render multiple sections of a page in parallel",
                use_case="Dashboard with independent sections",
                implementation="// app/dashboard/layout.tsx\nexport default function Layout({\n  children,\n  analytics,\n  users\n}: {\n  children: React.ReactNode\n  analytics: React.ReactNode\n  users: React.ReactNode\n}) {\n  return (\n    <div>\n      {children}\n      {analytics}\n      {users}\n    </div>\n  )\n}",
                pros=["Independent loading states", "Parallel rendering", "Better UX"],
                cons=["More complex routing", "Not suitable for all layouts"]
            ),
            TechPattern(
                stack=TechStack.REACT,
                name="Compound Components",
                description="Build components that share state implicitly",
                use_case="Modals, Dropdowns, Tabs",
                implementation="const Tabs = ({ children }) => {\n  const [active, setActive] = useState(0)\n  return (\n    <TabsContext value={{ active, setActive }}>\n      {children}\n    </TabsContext>\n  )\n}",
                pros=["Flexible API", "Less prop drilling", "Intuitive usage"],
                cons=["Harder to understand", "Requires context"]
            )
        ]

    def _get_default_performance(self) -> list[PerformanceTip]:
        """获取默认性能建议"""
        return [
            PerformanceTip(
                stack=TechStack.NEXTJS,
                topic="Image Optimization",
                technique="Use next/image for all images",
                impact="high",
                effort="low",
                description="Automatic optimization, lazy loading, and responsive images",
                code_snippet="import Image from 'next/image'\n\n<Image\n  src='/hero.jpg'\n  alt='Hero'\n  width={1200}\n  height={600}\n  priority\n/>"
            ),
            PerformanceTip(
                stack=TechStack.REACT,
                topic="Memoization",
                technique="Use useMemo and useCallback sparingly",
                impact="medium",
                effort="medium",
                description="Memoize expensive computations and callbacks",
                code_snippet="const memoizedValue = useMemo(() => {\n  return computeExpensiveValue(a, b)\n}, [a, b])"
            )
        ]

    def search_practices(
        self,
        stack: str,
        query: str | None = None,
        category: str | None = None,
        max_results: int = 5
    ) -> list[StackRecommendation]:
        """
        搜索最佳实践

        Args:
            stack: 技术栈名称
            query: 搜索查询
            category: 类别过滤
            max_results: 最大结果数

        Returns:
            推荐建议列表
        """
        stack_lower = stack.lower()

        # 筛选最佳实践
        filtered_practices = []
        for practice in self.practices:
            # 技术栈过滤
            if practice.stack.value.lower() != stack_lower:
                continue

            # 类别过滤
            if category and practice.category.value.lower() != category.lower():
                continue

            # 查询评分
            if query:
                query_lower = query.lower()
                score = 0

                if query_lower in practice.topic.lower():
                    score += 10
                if query_lower in practice.practice.lower():
                    score += 8
                if query_lower in practice.benefits.lower():
                    score += 5

                if score == 0:
                    continue

            filtered_practices.append(practice)

        # 构建推荐
        recommendations = []
        for practice in filtered_practices[:max_results]:
            priority = self._determine_priority(practice)
            context = self._get_context(practice)
            alternatives = self._get_alternatives(practice)
            resources = self._get_resources(practice)

            recommendations.append(StackRecommendation(
                practice=practice,
                priority=priority,
                context=context,
                alternatives=alternatives,
                resources=resources
            ))

        return recommendations

    def get_patterns(self, stack: str) -> list[TechPattern]:
        """
        获取设计模式

        Args:
            stack: 技术栈名称

        Returns:
            设计模式列表
        """
        stack_lower = stack.lower()
        return [
            p for p in self.patterns
            if p.stack.value.lower() == stack_lower
        ]

    def get_performance_tips(
        self,
        stack: str,
        impact: str | None = None,
        effort: str | None = None
    ) -> list[PerformanceTip]:
        """
        获取性能优化建议

        Args:
            stack: 技术栈名称
            impact: 影响程度过滤
            effort: 实施难度过滤

        Returns:
            性能建议列表
        """
        stack_lower = stack.lower()
        tips = []

        for tip in self.performance_tips:
            if tip.stack.value.lower() != stack_lower:
                continue

            if impact and tip.impact.lower() != impact.lower():
                continue

            if effort and tip.effort.lower() != effort.lower():
                continue

            tips.append(tip)

        # 按影响程度排序
        impact_order = {"high": 0, "medium": 1, "low": 2}
        tips.sort(key=lambda t: impact_order.get(t.impact.lower(), 3))

        return tips

    def get_quick_wins(self, stack: str) -> list[PerformanceTip]:
        """
        获取快速见效的性能优化

        Args:
            stack: 技术栈名称

        Returns:
            高影响、低难度的优化建议
        """
        tips = self.get_performance_tips(stack)

        return [
            tip for tip in tips
            if tip.impact.lower() == "high" and tip.effort.lower() == "low"
        ]

    def get_migration_guide(
        self,
        from_stack: str,
        to_stack: str
    ) -> dict[str, str]:
        """
        获取技术栈迁移指南

        Args:
            from_stack: 源技术栈
            to_stack: 目标技术栈

        Returns:
            迁移指南
        """
        # 简化版迁移指南
        # 实际应用中可以扩展为更详细的文档
        guides = {
            "react->nextjs": {
                "routing": "Replace react-router with Next.js App Router file-based routing",
                "data_fetching": "Move from useEffect to Server Components and async/await",
                "styling": "Keep existing CSS solutions, they work with Next.js",
                "deployment": "Deploy to Vercel for zero-config hosting"
            },
            "vue->nuxt": {
                "routing": "Replace vue-router with file-based routing in pages/",
                "data_fetching": "Use useAsyncData and useFetch composables",
                "styling": "Vue SFC styles work the same way",
                "deployment": "Deploy to Vercel, Netlify, or Node.js server"
            }
        }

        key = f"{from_stack.lower()}->{to_stack.lower()}"
        return guides.get(key, {})

    def _determine_priority(self, practice: TechBestPractice) -> str:
        """确定优先级"""
        if practice.category == PracticeCategory.SECURITY:
            return "critical"

        if practice.category == PracticeCategory.PERFORMANCE:
            return "high"

        if practice.complexity == "low":
            return "high"

        return "medium"

    def _get_context(self, practice: TechBestPractice) -> str:
        """获取上下文说明"""
        contexts = {
            PracticeCategory.ARCHITECTURE: "架构层面的最佳实践，影响整体代码组织",
            PracticeCategory.PERFORMANCE: "性能优化建议，提升用户体验",
            PracticeCategory.STATE_MANAGEMENT: "状态管理模式，确保数据流清晰",
            PracticeCategory.STYLING: "样式方案，保持视觉一致性",
            PracticeCategory.TESTING: "测试策略，确保代码质量",
            PracticeCategory.DEPLOYMENT: "部署方案，简化发布流程",
            PracticeCategory.SECURITY: "安全实践，保护应用和用户",
            PracticeCategory.ACCESSIBILITY: "无障碍性，确保所有用户可用"
        }

        return contexts.get(practice.category, "通用最佳实践")

    def _get_alternatives(self, practice: TechBestPractice) -> list[str]:
        """获取替代方案"""
        # 简化版，可以扩展为更详细的映射
        return ["See documentation for alternatives"]

    def _get_resources(self, practice: TechBestPractice) -> list[str]:
        """获取相关资源"""
        resources = {
            TechStack.NEXTJS: [
                "Next.js Documentation: https://nextjs.org/docs",
                "Next.js Learn: https://nextjs.org/learn"
            ],
            TechStack.REACT: [
                "React Documentation: https://react.dev",
                "React Patterns: https://reactpatterns.com"
            ],
            TechStack.VUE: [
                "Vue Documentation: https://vuejs.org/guide/",
                "Vue Style Guide: https://vuejs.org/style-guide/"
            ],
            TechStack.SVELTEKIT: [
                "SvelteKit Docs: https://kit.svelte.dev/docs",
                "Svelte Docs: https://svelte.dev/docs"
            ]
        }

        return resources.get(practice.stack, [])

    def list_stacks(self) -> list[str]:
        """列出所有支持的技术栈"""
        return list(set(p.stack.value for p in self.practices))

    def list_categories(self, stack: str | None = None) -> list[str]:
        """
        列出所有类别

        Args:
            stack: 可选的技术栈过滤

        Returns:
            类别列表
        """
        if stack:
            practices = [p for p in self.practices if p.stack.value.lower() == stack.lower()]
            return list(set(p.category.value for p in practices))

        return list(set(p.category.value for p in self.practices))


# 便捷函数
def get_tech_stack_engine(data_dir: Path | None = None) -> TechStackEngine:
    """获取技术栈引擎实例"""
    return TechStackEngine(data_dir)
