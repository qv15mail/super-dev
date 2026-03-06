"""
商业级 UI Intelligence

作用：
1. 基于产品类型、行业和前端栈推荐更成熟的 UI 方案
2. 为 UI/UX 文档、宿主提示词和设计治理提供统一知识库
3. 约束宿主优先生成现代商业产品，而不是模板化 AI 页面
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LibraryRecommendation:
    """组件生态推荐"""

    name: str
    category: str
    rationale: str
    strengths: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "rationale": self.rationale,
            "strengths": list(self.strengths),
            "notes": list(self.notes),
        }


class UIIntelligenceAdvisor:
    """商业级 UI/UX 推荐引擎"""

    FRONTEND_ALIASES = {
        "next": "react",
        "nextjs": "react",
        "nuxt": "vue",
        "nuxtjs": "vue",
        "react-native": "mobile",
        "flutter": "mobile",
        "swiftui": "mobile",
    }

    PRODUCT_PROFILES: dict[str, dict[str, Any]] = {
        "landing": {
            "surface": "品牌表达 + 价值转化",
            "information_density": "medium",
            "experience_goals": [
                "首屏 5 秒内讲清楚产品价值、差异化和下一步 CTA",
                "用案例、数据、截图、流程示意降低陌生用户的不确定感",
                "页面节奏要强，模块职责清晰，滚动过程中持续推动转化",
            ],
            "page_blueprints": [
                {
                    "page": "首页 / Landing",
                    "sections": [
                        "Hero（价值主张 + 证据 + CTA）",
                        "客户/媒体/合作方信任区",
                        "关键能力模块",
                        "真实使用场景/流程拆解",
                        "案例 / 评价 / 数据证明",
                        "FAQ + 强 CTA + Footer",
                    ],
                    "focus": "建立价值认知、形成转化路径、压缩理解成本",
                },
                {
                    "page": "功能详情页",
                    "sections": [
                        "功能价值开场",
                        "界面截图/交互演示",
                        "适用角色/行业场景",
                        "常见问题与限制说明",
                    ],
                    "focus": "把抽象卖点翻译成具体业务收益",
                },
            ],
            "component_priorities": [
                "Hero / CTA / Social Proof / Pricing / FAQ / Integration Wall / Use-case Cards",
            ],
            "conversion_modules": [
                "首屏强 CTA",
                "案例与客户证明",
                "对比式卖点表达",
                "价格/试用/预约入口",
            ],
            "banned_patterns": [
                "空洞 Hero + 只有一句口号",
                "大面积无意义渐变和玻璃卡片堆砌",
                "没有真实截图或可信证据的营销页",
            ],
        },
        "saas": {
            "surface": "产品介绍 + 工作流演示",
            "information_density": "medium-high",
            "experience_goals": [
                "产品价值、工作流和角色收益要同时可见",
                "把复杂能力拆成清晰的功能模块与任务路径",
                "强调效率、协作、可追踪和商业可信度",
            ],
            "page_blueprints": [
                {
                    "page": "官网 / 产品页",
                    "sections": [
                        "Value Hero + Product Screenshot",
                        "Workflow Explanation",
                        "Role-based Benefits",
                        "Security / Compliance / Cases",
                        "Pricing / CTA / FAQ",
                    ],
                    "focus": "让潜在客户快速理解产品如何落地到团队协作",
                },
                {
                    "page": "应用工作台",
                    "sections": [
                        "Global Header + Command Bar",
                        "Primary Workspace",
                        "Context Sidebar / Inspector",
                        "Recent Activities / Audit / Tasks",
                    ],
                    "focus": "提升日常使用效率与状态可见性",
                },
            ],
            "component_priorities": [
                "Command Bar / Filter Bar / Tabs / Data Cards / Sheets / Activity Timeline / Empty States",
            ],
            "conversion_modules": [
                "产品截图/录屏",
                "角色场景示意",
                "安全与集成说明",
                "试用与预约 CTA",
            ],
            "banned_patterns": [
                "所有模块都像同一层级的卡片墙",
                "信息太空，不能体现软件成熟度",
                "没有截图、没有流程、没有角色收益",
            ],
        },
        "dashboard": {
            "surface": "高密度信息 + 高效率操作",
            "information_density": "high",
            "experience_goals": [
                "高频路径要比视觉装饰更优先",
                "筛选、排序、批量操作、状态反馈必须完整",
                "保证复杂界面仍然具备扫描效率和上下文感",
            ],
            "page_blueprints": [
                {
                    "page": "总览 / Dashboard",
                    "sections": [
                        "KPI Summary Strip",
                        "Filter / Segment Bar",
                        "Chart Grid",
                        "Priority Alerts / Exceptions",
                        "Recent Activity / Tasks",
                    ],
                    "focus": "一屏读懂状态、风险、优先级",
                },
                {
                    "page": "列表 / Table Workspace",
                    "sections": [
                        "Search + Filters + Saved Views",
                        "Dense Data Table",
                        "Bulk Actions",
                        "Detail Drawer / Side Panel",
                    ],
                    "focus": "支持连续操作，而不是看完再跳页",
                },
            ],
            "component_priorities": [
                "KPI Cards / Filters / Data Table / Detail Drawer / Audit Timeline / Status Badges / Bulk Actions",
            ],
            "conversion_modules": [
                "不适用营销转化模块，优先风险提示、最近活动、审计与效率入口",
            ],
            "banned_patterns": [
                "把后台做成营销页",
                "大量空白和 oversized hero 占据工作区",
                "只有图表没有操作路径",
            ],
        },
        "ecommerce": {
            "surface": "购买决策 + 转化推进",
            "information_density": "medium-high",
            "experience_goals": [
                "商品价值、价格、优惠、信任和下一步动作必须就近出现",
                "首要关注商品理解、下单流程和决策辅助",
                "高质量图片、评价、配送与售后信息不可缺失",
            ],
            "page_blueprints": [
                {
                    "page": "首页",
                    "sections": [
                        "Hero / Seasonal Campaign",
                        "Category Entry",
                        "Featured Products",
                        "Reviews / Trust / Guarantees",
                        "Promotional CTA",
                    ],
                    "focus": "引导发现与快速进入购买路径",
                },
                {
                    "page": "商品详情",
                    "sections": [
                        "Gallery + Sticky Summary",
                        "Price / Variant / CTA",
                        "Shipping / Return / Trust",
                        "Review / FAQ / Recommendations",
                    ],
                    "focus": "减少决策犹豫并推进下单",
                },
            ],
            "component_priorities": [
                "Product Gallery / Sticky Summary / Review Cards / Recommendation Rails / Checkout Steps",
            ],
            "conversion_modules": [
                "评价与销量证据",
                "物流与售后承诺",
                "优惠信息与库存提示",
                "支付安全与退换政策",
            ],
            "banned_patterns": [
                "商品详情缺少图片、评价、规格和配送说明",
                "价格和 CTA 被分散到多个区域",
                "复杂花哨但不利于下单的动画",
            ],
        },
        "content": {
            "surface": "阅读效率 + 内容发现",
            "information_density": "medium",
            "experience_goals": [
                "阅读体验和内容结构优先于装饰",
                "列表、目录、相关推荐与订阅/分享路径要自然",
                "排版、字重、段落节奏要有明确的编辑感",
            ],
            "page_blueprints": [
                {
                    "page": "内容首页",
                    "sections": [
                        "Featured Story",
                        "Category Navigation",
                        "Content Feed",
                        "Author / Topic Modules",
                    ],
                    "focus": "建立内容层级与发现效率",
                },
                {
                    "page": "内容详情",
                    "sections": [
                        "Headline / Metadata",
                        "Table of Contents",
                        "Article Body",
                        "Related Content / Subscribe CTA",
                    ],
                    "focus": "高质量阅读与次级转化",
                },
            ],
            "component_priorities": [
                "Editorial Hero / Topic Filters / Table of Contents / Reading Progress / Author Cards",
            ],
            "conversion_modules": [
                "订阅 / 收藏 / 相关推荐 / 专题聚合",
            ],
            "banned_patterns": [
                "阅读页面被过多视觉噪音打断",
                "正文层级和留白失衡",
                "内容站首页像普通 SaaS 营销页",
            ],
        },
        "general": {
            "surface": "价值表达 + 核心流程可演示",
            "information_density": "medium",
            "experience_goals": [
                "先让用户看懂产品，再让用户完成第一步动作",
                "页面结构要能支持未来扩展，不做一次性展示壳子",
                "默认走现代商业产品基线，而不是试验性视觉",
            ],
            "page_blueprints": [
                {
                    "page": "首页",
                    "sections": [
                        "价值主张",
                        "核心功能",
                        "场景说明",
                        "信任证明",
                        "CTA",
                    ],
                    "focus": "建立理解和下一步动作",
                }
            ],
            "component_priorities": [
                "Cards / CTA / Social Proof / Feature Highlights / Empty States",
            ],
            "conversion_modules": [
                "价值说明 + 证据 + CTA",
            ],
            "banned_patterns": [
                "AI 模板式宣传页",
                "缺少信任元素和清晰 CTA",
                "视觉过度但功能主线不清楚",
            ],
        },
    }

    INDUSTRY_TRUST_RULES: dict[str, dict[str, Any]] = {
        "healthcare": {
            "trust_modules": [
                "医生/机构资质与执照信息",
                "预约、流程、费用边界说明",
                "隐私、数据安全和合规提示",
                "紧急/风险场景的可执行下一步",
            ],
            "tone": "专业、克制、低风险感、可读性优先",
            "banned_patterns": [
                "霓虹色和重动效",
                "夸张的 AI 科幻视觉",
                "低对比度和轻飘的卡片堆砌",
            ],
        },
        "fintech": {
            "trust_modules": [
                "费用、收益、风险说明",
                "安全、合规、权限与审计提示",
                "交易状态、到账时间和异常解释",
                "关键数字可追踪且具备来源说明",
            ],
            "tone": "可信、严谨、数字层级清晰、反馈即时",
            "banned_patterns": [
                "过度娱乐化视觉",
                "重要数字弱化或混乱",
                "没有安全与风控表达的金融界面",
            ],
        },
        "education": {
            "trust_modules": [
                "课程/能力路径",
                "阶段进度和成就反馈",
                "老师/机构背书",
                "试学、案例和成果展示",
            ],
            "tone": "清晰、友好、鼓励式反馈",
            "banned_patterns": [
                "术语堆叠、没有引导",
                "只讲功能，不讲学习路径",
            ],
        },
        "general": {
            "trust_modules": [
                "能力边界说明",
                "案例/截图/指标证明",
                "FAQ 与支持入口",
                "状态反馈和错误恢复路径",
            ],
            "tone": "现代、克制、有品牌感",
            "banned_patterns": [
                "只有概念没有证据",
                "所有页面都靠装饰性视觉撑场面",
            ],
        },
    }

    STACK_RECOMMENDATIONS: dict[str, list[LibraryRecommendation]] = {
        "react": [
            LibraryRecommendation(
                name="shadcn/ui + Radix UI + Tailwind CSS",
                category="Primary",
                rationale="适合需要现代品牌感、可定制组件和商业级页面控制力的 React/Next 项目。",
                strengths=[
                    "组件骨架成熟，适合快速搭建高质量产品界面",
                    "与设计 token、主题系统、品牌定制兼容性强",
                    "便于结合 TanStack Table、React Hook Form、Zod 形成完整前端基线",
                ],
                notes=[
                    "必须先定义 token、容器、字重和信息密度，再批量生成组件",
                    "表单建议配合 React Hook Form + Zod",
                ],
            ),
            LibraryRecommendation(
                name="Ant Design",
                category="Alternative",
                rationale="适合 B 端后台、运营系统和高密度表格工作台。",
                strengths=[
                    "表格、表单、数据录入和后台模式成熟",
                    "适合中后台快速交付和复杂管理流程",
                ],
                notes=[
                    "品牌化和高级感需要额外主题定制，避免默认 Ant 风格直出",
                ],
            ),
            LibraryRecommendation(
                name="MUI",
                category="Alternative",
                rationale="适合需要完整组件覆盖和企业级主题系统的 React 项目。",
                strengths=[
                    "组件覆盖全，适合复杂业务表面",
                    "主题系统成熟",
                ],
                notes=[
                    "默认 Material 视觉不应直接作为商业品牌终稿",
                ],
            ),
            LibraryRecommendation(
                name="Mantine",
                category="Alternative",
                rationale="适合偏现代产品化、需要开发效率和一致性的 React 项目。",
                strengths=[
                    "Hooks 与组件生态完整",
                    "适合 SaaS 与工具类产品",
                ],
                notes=[
                    "适合产品工作台，但营销页仍需较强定制",
                ],
            ),
        ],
        "vue": [
            LibraryRecommendation(
                name="Naive UI + Tailwind CSS",
                category="Primary",
                rationale="适合现代 Vue 商业产品，兼顾组件成熟度与品牌化能力。",
                strengths=[
                    "适合 SaaS、工作台和中后台混合场景",
                    "主题覆盖能力较好",
                ],
                notes=[
                    "信息密度和主题层级要先定，不要直接套默认皮肤",
                ],
            ),
            LibraryRecommendation(
                name="Element Plus",
                category="Alternative",
                rationale="适合中文团队和中后台交付效率场景。",
                strengths=[
                    "表单、表格、弹窗、树形控件成熟",
                    "适合高频业务录入流程",
                ],
                notes=[
                    "默认视觉较强，需要定制字体、间距和色彩来避免模板感",
                ],
            ),
            LibraryRecommendation(
                name="Arco Design Vue",
                category="Alternative",
                rationale="适合需要更现代感的中后台与数据工作台。",
                strengths=[
                    "组件层次清晰，视觉更现代",
                    "适合 dashboard 场景",
                ],
                notes=[
                    "仍需针对品牌感与信息密度做定制",
                ],
            ),
        ],
        "angular": [
            LibraryRecommendation(
                name="Angular Material + CDK",
                category="Primary",
                rationale="适合流程型企业应用和可维护性优先的 Angular 项目。",
                strengths=[
                    "无障碍、表单、Overlay 和 CDK 能力成熟",
                    "适合强约束组件体系",
                ],
                notes=[
                    "必须做主题和排版升级，不能直接 Material 默认观感交付",
                ],
            )
        ],
        "svelte": [
            LibraryRecommendation(
                name="shadcn-svelte + Bits UI + Tailwind CSS",
                category="Primary",
                rationale="适合追求现代商业观感和高定制性的 Svelte 项目。",
                strengths=[
                    "组件控制力高，适合品牌型产品界面",
                    "与 token 和 Tailwind 生态配合良好",
                ],
                notes=[
                    "优先建立页面骨架和 token，再补动画与局部质感",
                ],
            ),
            LibraryRecommendation(
                name="Skeleton UI",
                category="Alternative",
                rationale="适合快速起步的 Svelte 产品。",
                strengths=[
                    "上手快，组件较全",
                ],
                notes=[
                    "默认风格需要品牌化重写",
                ],
            ),
        ],
        "mobile": [
            LibraryRecommendation(
                name="平台原生设计系统 + 自定义 Token",
                category="Primary",
                rationale="移动端优先保留原生交互可信度，再叠加品牌 token。",
                strengths=[
                    "符合平台交互预期",
                    "更适合高频任务流和触控体验",
                ],
                notes=[
                    "少做网页式 Hero，多做任务型布局和底部操作结构",
                ],
            )
        ],
        "default": [
            LibraryRecommendation(
                name="Tailwind CSS + Headless Patterns",
                category="Primary",
                rationale="适合未知前端栈时先建立 token、栅格和组件骨架。",
                strengths=[
                    "轻量、灵活",
                    "便于逐步落地品牌化设计系统",
                ],
                notes=[
                    "必须定义组件规范，避免 utility-class 随意散落",
                ],
            )
        ],
    }

    ICON_RECOMMENDATIONS = {
        "default": "Lucide",
        "brand": "Lucide + Simple Icons（仅品牌/合作方标识）",
        "dense": "Lucide / Tabler",
    }

    CHART_RECOMMENDATIONS = {
        "react": {
            "default": "Recharts",
            "dense": "ECharts / Visx",
        },
        "vue": {
            "default": "ECharts",
            "dense": "ECharts / AntV",
        },
        "angular": {
            "default": "ECharts / ngx-charts",
            "dense": "ECharts",
        },
        "svelte": {
            "default": "LayerCake / ECharts",
            "dense": "ECharts",
        },
        "default": {
            "default": "ECharts",
            "dense": "ECharts",
        },
    }

    FORM_STACK = {
        "react": "React Hook Form + Zod",
        "vue": "vee-validate + Zod / Valibot",
        "angular": "Angular Reactive Forms",
        "svelte": "sveltekit-superforms + Zod",
        "default": "Schema-driven validation + typed DTO",
    }

    MOTION_STACK = {
        "react": "Framer Motion（营销/品牌页） + CSS transitions（工作台）",
        "vue": "VueUse Motion / Motion One + CSS transitions",
        "angular": "Angular Animations + CSS transitions",
        "svelte": "Svelte transitions + Motion One",
        "default": "Meaningful CSS transitions only",
    }

    def recommend(
        self,
        *,
        description: str,
        frontend: str,
        product_type: str,
        industry: str,
        style: str,
        ui_library: str | None = None,
    ) -> dict[str, Any]:
        """生成 UI intelligence 推荐"""
        normalized_frontend = self.FRONTEND_ALIASES.get(frontend.lower(), frontend.lower())
        profile = self.PRODUCT_PROFILES.get(product_type, self.PRODUCT_PROFILES["general"])
        industry_rules = self.INDUSTRY_TRUST_RULES.get(industry, self.INDUSTRY_TRUST_RULES["general"])
        library_options = self.STACK_RECOMMENDATIONS.get(
            normalized_frontend, self.STACK_RECOMMENDATIONS["default"]
        )

        primary_library = library_options[0]
        if ui_library:
            primary_library = LibraryRecommendation(
                name=ui_library,
                category="User Selected",
                rationale="用户在项目初始化时显式指定，作为实现基线保留。",
                strengths=[
                    "与项目已有约束保持一致",
                    "避免在中途切换组件生态带来重构成本",
                ],
                notes=[
                    "仍需结合 token、排版和页面骨架进行品牌化重写",
                ],
            )

        density = profile["information_density"]
        chart_key = "dense" if density == "high" else "default"
        chart_library = self.CHART_RECOMMENDATIONS.get(
            normalized_frontend, self.CHART_RECOMMENDATIONS["default"]
        )[chart_key]

        icon_library = self.ICON_RECOMMENDATIONS["dense" if density == "high" else "brand"]

        design_system_priorities = [
            "先冻结颜色、字体、间距、圆角、阴影、边框和动效 token",
            "先定义桌面/平板/移动端栅格与容器宽度，再生成页面",
            "先定义全局组件状态矩阵，再进入页面抛光",
            "优先做页面结构、业务路径和信任表达，再做视觉特效",
        ]

        benchmark_principles = [
            "优先输出完整设计系统和页面骨架，而不是直接铺满页面装饰",
            "页面需要像成熟商业产品，具备截图、案例、信任、状态、流程和数据层级",
            "组件库只负责加速，不负责品牌感，必须做 token 和排版层重写",
            "对营销页、产品页、工作台分别使用不同的信息密度和交互策略",
        ]

        trust_modules = list(industry_rules["trust_modules"]) + list(profile["conversion_modules"])
        banned_patterns = list(profile["banned_patterns"]) + list(industry_rules["banned_patterns"])

        state_requirements = [
            "normal",
            "hover",
            "active",
            "focus-visible",
            "loading",
            "empty",
            "error",
            "disabled",
            "success-feedback",
            "permission-limited",
        ]

        component_stack = {
            "form": self.FORM_STACK.get(normalized_frontend, self.FORM_STACK["default"]),
            "table": self._table_strategy(normalized_frontend, density),
            "chart": chart_library,
            "motion": self.MOTION_STACK.get(normalized_frontend, self.MOTION_STACK["default"]),
            "icons": icon_library,
        }

        style_direction = self._build_style_direction(style=style, product_type=product_type, industry=industry)
        database_keywords = self._knowledge_keywords(
            description=description,
            product_type=product_type,
            industry=industry,
            frontend=normalized_frontend,
        )

        return {
            "normalized_frontend": normalized_frontend,
            "surface": profile["surface"],
            "information_density": density,
            "experience_goals": list(profile["experience_goals"]),
            "page_blueprints": list(profile["page_blueprints"]),
            "component_priorities": list(profile["component_priorities"]),
            "design_system_priorities": design_system_priorities,
            "benchmark_principles": benchmark_principles,
            "trust_modules": trust_modules,
            "banned_patterns": banned_patterns,
            "state_requirements": state_requirements,
            "primary_library": primary_library.to_dict(),
            "alternative_libraries": [item.to_dict() for item in library_options[1:3]],
            "component_stack": component_stack,
            "style_direction": style_direction,
            "industry_tone": industry_rules["tone"],
            "knowledge_keywords": database_keywords,
        }

    def _table_strategy(self, frontend: str, density: str) -> str:
        if density == "high":
            if frontend == "react":
                return "TanStack Table + virtualized rows"
            if frontend == "vue":
                return "Naive UI DataTable / vxe-table（按复杂度选择）"
            if frontend == "angular":
                return "CDK Table / AG Grid（复杂后台）"
            if frontend == "svelte":
                return "TanStack Table core + custom renderers"
        return "Semantic table + lightweight sorting/filtering"

    def _build_style_direction(self, *, style: str, product_type: str, industry: str) -> dict[str, str]:
        mappings = {
            "minimal": {
                "direction": "克制、清晰、减少装饰噪音",
                "materials": "高质量排版、细边框、低饱和背景层",
            },
            "professional": {
                "direction": "可信、稳定、业务优先",
                "materials": "中性色基底 + 单一强调色 + 稳定阴影",
            },
            "playful": {
                "direction": "友好、活跃，但仍保持产品成熟度",
                "materials": "高识别主色 + 更开放的圆角和插图节奏",
            },
            "luxury": {
                "direction": "高级、克制、重材质与排版节奏",
                "materials": "高对比色、精致留白、受控动效",
            },
            "modern": {
                "direction": "现代商业产品基线，品牌感与效率并重",
                "materials": "干净背景、明确层级、局部强调而非全屏特效",
            },
        }
        result = mappings.get(style, mappings["modern"]).copy()
        if product_type == "dashboard":
            result["materials"] += "；在高密度工作台中控制装饰层，优先数据可读性。"
        if industry in {"healthcare", "fintech"}:
            result["direction"] += "，降低风险感和不确定感。"
        return result

    def _knowledge_keywords(
        self,
        *,
        description: str,
        product_type: str,
        industry: str,
        frontend: str,
    ) -> list[str]:
        words = [
            product_type,
            industry,
            frontend,
            "design tokens",
            "component states",
            "commercial ui",
            "trust design",
        ]
        lowered = description.lower()
        if any(token in lowered for token in ["dashboard", "后台", "仪表盘", "workbench", "工作台"]):
            words.extend(["data table", "filter bar", "audit trail", "dense workspace"])
        if any(token in lowered for token in ["landing", "官网", "marketing", "official website", "落地页"]):
            words.extend(["hero", "social proof", "pricing", "conversion"])
        if any(token in lowered for token in ["checkout", "支付", "billing", "order", "cart"]):
            words.extend(["checkout", "trust badges", "payment status"])
        return words
