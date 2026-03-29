"""
开发：Excellent（11964948@qq.com）
功能：商业级 UI Intelligence 推荐引擎
作用：基于产品类型、行业和前端栈推荐 UI 方案，提供配色、字体、组件库和设计治理知识库
创建时间：2025-12-30
最后修改：2026-03-21
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
        "react-native": "react-native",
        "flutter": "flutter",
        "swiftui": "swiftui",
        "taro": "miniapp",
        "uniapp": "miniapp",
        "uni-app": "miniapp",
        "wechat-miniprogram": "miniapp",
        "miniprogram": "miniapp",
        "miniapp": "miniapp",
        "mp-weixin": "miniapp",
        "weapp": "miniapp",
        "electron": "desktop",
        "tauri": "desktop",
        "desktop": "desktop",
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
        "legal": {
            "trust_modules": [
                "律师资质与执照展示",
                "案件成功率与客户评价",
                "隐私保护与数据安全声明",
                "咨询流程与费用透明说明",
            ],
            "tone": "权威、严谨、专业、可信",
            "banned_patterns": [
                "过度活泼或娱乐化的视觉",
                "缺少资质证明的专业页面",
            ],
        },
        "beauty": {
            "trust_modules": [
                "技师资质与服务项目",
                "真实案例与效果对比",
                "预约流程与退改政策",
                "产品安全认证与成分说明",
            ],
            "tone": "精致、温暖、品牌感、女性友好",
            "banned_patterns": [
                "粗糙的排版和低质量图片",
                "缺少真人案例的纯装饰页面",
            ],
        },
        "restaurant": {
            "trust_modules": [
                "菜品实拍与价格展示",
                "营业时间与位置导航",
                "食品安全认证",
                "用户评价与推荐菜品",
            ],
            "tone": "温暖、食欲感、本地化、便捷",
            "banned_patterns": [
                "使用库存图片替代实际菜品",
                "菜单信息不完整或过时",
            ],
        },
        "travel": {
            "trust_modules": [
                "目的地实景图片与评价",
                "价格透明与退改政策",
                "安全提示与保险说明",
                "行程定制与客服支持",
            ],
            "tone": "向往感、安全感、便捷、值得信赖",
            "banned_patterns": [
                "过度修图导致期望落差",
                "隐藏费用和不透明的定价",
            ],
        },
        "real-estate": {
            "trust_modules": [
                "房源实景与户型图",
                "价格趋势与区域分析",
                "经纪人资质与评价",
                "交易流程与法律说明",
            ],
            "tone": "专业、值得信赖、数据驱动",
            "banned_patterns": [
                "过度美化的效果图替代实景",
                "关键信息（价格、面积）不突出",
            ],
        },
    }

    PRODUCT_COLOR_PALETTES: dict[str, dict[str, str]] = {
        # SaaS & Software
        "saas": {"primary": "#2563EB", "secondary": "#3B82F6", "accent": "#EA580C", "background": "#F8FAFC", "text": "#1E293B", "card": "#FFFFFF", "muted": "#E9EFF8", "border": "#E2E8F0", "name": "Trust Blue"},
        "micro-saas": {"primary": "#6366F1", "secondary": "#818CF8", "accent": "#059669", "background": "#F5F3FF", "text": "#1E1B4B", "card": "#FFFFFF", "muted": "#EBEFF9", "border": "#E0E7FF", "name": "Indigo Focus"},
        "b2b": {"primary": "#0F172A", "secondary": "#334155", "accent": "#0369A1", "background": "#F8FAFC", "text": "#020617", "card": "#FFFFFF", "muted": "#E8ECF1", "border": "#E2E8F0", "name": "Enterprise Navy"},
        "productivity": {"primary": "#0D9488", "secondary": "#14B8A6", "accent": "#EA580C", "background": "#F0FDFA", "text": "#134E4A", "card": "#FFFFFF", "muted": "#E8F1F4", "border": "#99F6E4", "name": "Teal Efficiency"},
        "collaboration": {"primary": "#7C3AED", "secondary": "#8B5CF6", "accent": "#059669", "background": "#F5F3FF", "text": "#312E81", "card": "#FFFFFF", "muted": "#EBEFF9", "border": "#E0E7FF", "name": "Team Indigo"},
        "ai-platform": {"primary": "#A83AED", "secondary": "#A78BFA", "accent": "#0891B2", "background": "#FAF5FF", "text": "#1E1B4B", "card": "#FFFFFF", "muted": "#ECEEF9", "border": "#DDD6FE", "name": "AI Violet"},
        "design-tool": {"primary": "#4F46E5", "secondary": "#6366F1", "accent": "#EA580C", "background": "#EEF2FF", "text": "#312E81", "card": "#FFFFFF", "muted": "#EBEEF8", "border": "#C7D2FE", "name": "Creative Indigo"},
        "knowledge-base": {"primary": "#475569", "secondary": "#64748B", "accent": "#2563EB", "background": "#F8FAFC", "text": "#1E293B", "card": "#FFFFFF", "muted": "#EAEFF3", "border": "#E2E8F0", "name": "Slate Knowledge"},
        # E-commerce & Marketplace
        "ecommerce": {"primary": "#059669", "secondary": "#10B981", "accent": "#EA580C", "background": "#ECFDF5", "text": "#064E3B", "card": "#FFFFFF", "muted": "#E8F1F3", "border": "#A7F3D0", "name": "Commerce Green"},
        "ecommerce-luxury": {"primary": "#1C1917", "secondary": "#44403C", "accent": "#A16207", "background": "#FAFAF9", "text": "#0C0A09", "card": "#FFFFFF", "muted": "#E8ECF0", "border": "#D6D3D1", "name": "Luxury Noir"},
        "marketplace": {"primary": "#4F3AED", "secondary": "#A78BFA", "accent": "#16A34A", "background": "#FAF5FF", "text": "#4C1D95", "card": "#FFFFFF", "muted": "#ECEEF9", "border": "#DDD6FE", "name": "Market Purple"},
        "subscription-box": {"primary": "#D946EF", "secondary": "#E879F9", "accent": "#EA580C", "background": "#FDF4FF", "text": "#86198F", "card": "#FFFFFF", "muted": "#F0EEF9", "border": "#F5D0FE", "name": "Unbox Magenta"},
        # Finance & Fintech
        "fintech": {"primary": "#F59E0B", "secondary": "#FBBF24", "accent": "#8B5CF6", "background": "#0F172A", "text": "#F8FAFC", "card": "#222735", "muted": "#272F42", "border": "#334155", "name": "Crypto Gold"},
        "banking": {"primary": "#0E102A", "secondary": "#1E3A8A", "accent": "#A16207", "background": "#F8FAFC", "text": "#020617", "card": "#FFFFFF", "muted": "#E8ECF1", "border": "#E2E8F0", "name": "Bank Navy"},
        "insurance": {"primary": "#0369A1", "secondary": "#0EA5E9", "accent": "#16A34A", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E7EFF5", "border": "#BAE6FD", "name": "Trust Sky"},
        "financial-dashboard": {"primary": "#0E1D2A", "secondary": "#1E293B", "accent": "#22C55E", "background": "#020617", "text": "#F8FAFC", "card": "#0E1223", "muted": "#1A1E2F", "border": "#334155", "name": "Dark Finance"},
        "analytics": {"primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#D97706", "background": "#F8FAFC", "text": "#1E3A8A", "card": "#FFFFFF", "muted": "#E9EEF6", "border": "#DBEAFE", "name": "Data Blue"},
        # Healthcare & Wellness
        "healthcare": {"primary": "#0891B2", "secondary": "#22D3EE", "accent": "#059669", "background": "#ECFEFF", "text": "#164E63", "card": "#FFFFFF", "muted": "#E8F1F6", "border": "#A5F3FC", "name": "Medical Cyan"},
        "mental-health": {"primary": "#8B5CF6", "secondary": "#C4B5FD", "accent": "#059669", "background": "#FAF5FF", "text": "#4C1D95", "card": "#FFFFFF", "muted": "#EDEFF9", "border": "#EDE9FE", "name": "Calm Violet"},
        "fitness": {"primary": "#F97316", "secondary": "#FB923C", "accent": "#22C55E", "background": "#1F2937", "text": "#F8FAFC", "card": "#313742", "muted": "#37414F", "border": "#374151", "name": "Energy Orange"},
        "beauty-spa": {"primary": "#EC4899", "secondary": "#F9A8D4", "accent": "#8B5CF6", "background": "#FDF2F8", "text": "#831843", "card": "#FFFFFF", "muted": "#F1EEF5", "border": "#FBCFE8", "name": "Blush Pink"},
        # Education & Learning
        "education": {"primary": "#4F46E5", "secondary": "#818CF8", "accent": "#EA580C", "background": "#EEF2FF", "text": "#1E1B4B", "card": "#FFFFFF", "muted": "#EBEEF8", "border": "#C7D2FE", "name": "Learn Indigo"},
        "e-learning": {"primary": "#0F766E", "secondary": "#14B8A6", "accent": "#EA580C", "background": "#F0FDFA", "text": "#134E4A", "card": "#FFFFFF", "muted": "#E8F1F4", "border": "#5EEAD4", "name": "Edu Teal"},
        # Media & Entertainment
        "social-media": {"primary": "#E11D48", "secondary": "#FB7185", "accent": "#2563EB", "background": "#FFF1F2", "text": "#881337", "card": "#FFFFFF", "muted": "#F0ECF2", "border": "#FECDD3", "name": "Social Rose"},
        "gaming": {"primary": "#D53AED", "secondary": "#A78BFA", "accent": "#F43F5E", "background": "#0F0F23", "text": "#E2E8F0", "card": "#1E1C35", "muted": "#27273B", "border": "#4C1D95", "name": "Game Violet"},
        "music": {"primary": "#1E1B4B", "secondary": "#4338CA", "accent": "#22C55E", "background": "#0F0F23", "text": "#F8FAFC", "card": "#1B1B30", "muted": "#27273B", "border": "#312E81", "name": "Sound Dark"},
        "video-streaming": {"primary": "#0F0F23", "secondary": "#1E1B4B", "accent": "#E11D48", "background": "#000000", "text": "#F8FAFC", "card": "#0C0C0D", "muted": "#181818", "border": "#312E81", "name": "Stream Black"},
        "podcast": {"primary": "#1E1B4B", "secondary": "#312E81", "accent": "#F97316", "background": "#0F0F23", "text": "#F8FAFC", "card": "#1B1B30", "muted": "#27273B", "border": "#4338CA", "name": "Voice Dark"},
        "content": {"primary": "#475569", "secondary": "#94A3B8", "accent": "#2563EB", "background": "#FFFFFF", "text": "#1E293B", "card": "#F8FAFC", "muted": "#F1F5F9", "border": "#E2E8F0", "name": "Reader Slate"},
        "creative-agency": {"primary": "#EC4899", "secondary": "#F472B6", "accent": "#0891B2", "background": "#FDF2F8", "text": "#831843", "card": "#FFFFFF", "muted": "#F1EEF5", "border": "#FBCFE8", "name": "Agency Pink"},
        "creator-economy": {"primary": "#EC4899", "secondary": "#F472B6", "accent": "#EA580C", "background": "#FDF2F8", "text": "#831843", "card": "#FFFFFF", "muted": "#F1EEF5", "border": "#FBCFE8", "name": "Creator Pink"},
        # Professional Services
        "legal": {"primary": "#1E3A8A", "secondary": "#1E40AF", "accent": "#B45309", "background": "#F8FAFC", "text": "#0F172A", "card": "#FFFFFF", "muted": "#E9EEF5", "border": "#CBD5E1", "name": "Legal Blue"},
        "government": {"primary": "#140E2A", "secondary": "#334155", "accent": "#0369A1", "background": "#F8FAFC", "text": "#020617", "card": "#FFFFFF", "muted": "#E8ECF1", "border": "#E2E8F0", "name": "Gov Navy"},
        "nonprofit": {"primary": "#0891B2", "secondary": "#22D3EE", "accent": "#EA580C", "background": "#ECFEFF", "text": "#164E63", "card": "#FFFFFF", "muted": "#E8F1F6", "border": "#A5F3FC", "name": "Impact Cyan"},
        "consulting": {"primary": "#0E242A", "secondary": "#1E293B", "accent": "#2563EB", "background": "#F8FAFC", "text": "#020617", "card": "#FFFFFF", "muted": "#E8ECF1", "border": "#E2E8F0", "name": "Consult Navy"},
        # Real Estate & Hospitality
        "real-estate": {"primary": "#0F766E", "secondary": "#14B8A6", "accent": "#0369A1", "background": "#F0FDFA", "text": "#134E4A", "card": "#FFFFFF", "muted": "#E8F0F3", "border": "#99F6E4", "name": "Property Teal"},
        "hotel": {"primary": "#1E3A8A", "secondary": "#3B82F6", "accent": "#A16207", "background": "#F8FAFC", "text": "#1E40AF", "card": "#FFFFFF", "muted": "#E9EEF5", "border": "#BFDBFE", "name": "Hotel Royal"},
        "travel": {"primary": "#0EA5E9", "secondary": "#38BDF8", "accent": "#EA580C", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E8F2F8", "border": "#BAE6FD", "name": "Travel Sky"},
        "restaurant": {"primary": "#DC2626", "secondary": "#F87171", "accent": "#A16207", "background": "#FEF2F2", "text": "#450A0A", "card": "#FFFFFF", "muted": "#F0EDF1", "border": "#FECACA", "name": "Dining Red"},
        # Technology & IOT
        "smart-home": {"primary": "#1E293B", "secondary": "#334155", "accent": "#22C55E", "background": "#0F172A", "text": "#F8FAFC", "card": "#1B2336", "muted": "#272F42", "border": "#475569", "name": "IoT Dark"},
        "ev-charging": {"primary": "#0891B2", "secondary": "#22D3EE", "accent": "#16A34A", "background": "#ECFEFF", "text": "#164E63", "card": "#FFFFFF", "muted": "#E8F1F6", "border": "#A5F3FC", "name": "EV Cyan"},
        "web3": {"primary": "#8B5CF6", "secondary": "#A78BFA", "accent": "#FBBF24", "background": "#0F0F23", "text": "#F8FAFC", "card": "#1E1D35", "muted": "#27273B", "border": "#4C1D95", "name": "Web3 Purple"},
        "logistics": {"primary": "#2563EB", "secondary": "#3B82F6", "accent": "#EA580C", "background": "#EFF6FF", "text": "#1E40AF", "card": "#FFFFFF", "muted": "#E9EFF8", "border": "#BFDBFE", "name": "Logistics Blue"},
        "agriculture": {"primary": "#15803D", "secondary": "#22C55E", "accent": "#A16207", "background": "#F0FDF4", "text": "#14532D", "card": "#FFFFFF", "muted": "#E8F0F1", "border": "#BBF7D0", "name": "Farm Green"},
        # Lifestyle & Events
        "dating": {"primary": "#E11D48", "secondary": "#FB7185", "accent": "#EA580C", "background": "#FFF1F2", "text": "#881337", "card": "#FFFFFF", "muted": "#F0ECF2", "border": "#FECDD3", "name": "Love Rose"},
        "wedding": {"primary": "#DB2777", "secondary": "#F472B6", "accent": "#A16207", "background": "#FDF2F8", "text": "#831843", "card": "#FFFFFF", "muted": "#F0EDF4", "border": "#FBCFE8", "name": "Wedding Fuchsia"},
        "pet-tech": {"primary": "#F97316", "secondary": "#FB923C", "accent": "#2563EB", "background": "#FFF7ED", "text": "#9A3412", "card": "#FFFFFF", "muted": "#F1F0F0", "border": "#FED7AA", "name": "Pet Orange"},
        # Portfolio & Personal
        "portfolio": {"primary": "#18181B", "secondary": "#3F3F46", "accent": "#2563EB", "background": "#FAFAFA", "text": "#09090B", "card": "#FFFFFF", "muted": "#E8ECF0", "border": "#E4E4E7", "name": "Mono Zinc"},
        "luxury-brand": {"primary": "#1C1917", "secondary": "#44403C", "accent": "#A16207", "background": "#FAFAF9", "text": "#0C0A09", "card": "#FFFFFF", "muted": "#E8ECF0", "border": "#D6D3D1", "name": "Luxury Stone"},
        # Job & HR
        "job-board": {"primary": "#0241A1", "secondary": "#0EA5E9", "accent": "#16A34A", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E7EFF5", "border": "#BAE6FD", "name": "Career Sky"},
        # Dashboard variants
        "dashboard": {"primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#D97706", "background": "#F8FAFC", "text": "#1E3A8A", "card": "#FFFFFF", "muted": "#E9EEF6", "border": "#DBEAFE", "name": "Dashboard Blue"},
        "admin": {"primary": "#1B0E2A", "secondary": "#334155", "accent": "#2563EB", "background": "#F8FAFC", "text": "#020617", "card": "#FFFFFF", "muted": "#E8ECF1", "border": "#E2E8F0", "name": "Admin Slate"},
        # Landing & General
        "landing": {"primary": "#1D4ED8", "secondary": "#2563EB", "accent": "#EA580C", "background": "#FFFFFF", "text": "#111827", "card": "#F8FAFC", "muted": "#F1F5F9", "border": "#E5E7EB", "name": "Brand Blue"},
        "general": {"primary": "#3B82F6", "secondary": "#60A5FA", "accent": "#EA580C", "background": "#FFFFFF", "text": "#111827", "card": "#F8FAFC", "muted": "#F1F5F9", "border": "#E5E7EB", "name": "Professional Blue"},
        # Construction & Automotive
        "construction": {"primary": "#64748B", "secondary": "#94A3B8", "accent": "#EA580C", "background": "#F8FAFC", "text": "#334155", "card": "#FFFFFF", "muted": "#EBF0F5", "border": "#E2E8F0", "name": "Build Slate"},
        "automotive": {"primary": "#1E293B", "secondary": "#334155", "accent": "#DC2626", "background": "#F8FAFC", "text": "#0F172A", "card": "#FFFFFF", "muted": "#E9EDF1", "border": "#E2E8F0", "name": "Auto Dark"},
        # Photography & Creative
        "photography": {"primary": "#18181B", "secondary": "#27272A", "accent": "#F8FAFC", "background": "#000000", "text": "#FAFAFA", "card": "#0C0C0C", "muted": "#181818", "border": "#3F3F46", "name": "Photo Noir"},
        # Coworking & Services
        "coworking": {"primary": "#F59E0B", "secondary": "#FBBF24", "accent": "#2563EB", "background": "#FFFBEB", "text": "#78350F", "card": "#FFFFFF", "muted": "#F1F2EF", "border": "#FDE68A", "name": "Space Amber"},
        "home-services": {"primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#EA580C", "background": "#EFF6FF", "text": "#1E3A8A", "card": "#FFFFFF", "muted": "#E9EEF6", "border": "#BFDBFE", "name": "Service Blue"},
        # Childcare & Senior Care
        "childcare": {"primary": "#F472B6", "secondary": "#FBCFE8", "accent": "#16A34A", "background": "#FDF2F8", "text": "#9D174D", "card": "#FFFFFF", "muted": "#F1F0F6", "border": "#FCE7F3", "name": "Care Pink"},
        "senior-care": {"primary": "#0290A1", "secondary": "#38BDF8", "accent": "#16A34A", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E7EFF5", "border": "#E0F2FE", "name": "Elder Sky"},
        # Medical & Health Services
        "medical-clinic": {"primary": "#0891B2", "secondary": "#22D3EE", "accent": "#16A34A", "background": "#F0FDFA", "text": "#134E4A", "card": "#FFFFFF", "muted": "#E8F1F6", "border": "#CCFBF1", "name": "Clinic Teal"},
        "pharmacy": {"primary": "#15803D", "secondary": "#22C55E", "accent": "#0369A1", "background": "#F0FDF4", "text": "#14532D", "card": "#FFFFFF", "muted": "#E8F0F1", "border": "#BBF7D0", "name": "Pharma Green"},
        "dental": {"primary": "#0EA5E9", "secondary": "#38BDF8", "accent": "#059669", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E8F2F8", "border": "#BAE6FD", "name": "Dental Sky"},
        "veterinary": {"primary": "#115E59", "secondary": "#0D9488", "accent": "#EA580C", "background": "#F0FDFA", "text": "#134E4A", "card": "#FFFFFF", "muted": "#E8F1F4", "border": "#99F6E4", "name": "Vet Teal"},
        # Food & Beverage
        "florist": {"primary": "#15803D", "secondary": "#22C55E", "accent": "#EC4899", "background": "#F0FDF4", "text": "#14532D", "card": "#FFFFFF", "muted": "#E8F0F1", "border": "#BBF7D0", "name": "Bloom Green"},
        "bakery-cafe": {"primary": "#92400E", "secondary": "#B45309", "accent": "#DC2626", "background": "#FEF3C7", "text": "#78350F", "card": "#FFFFFF", "muted": "#EDEEF0", "border": "#FDE68A", "name": "Bake Amber"},
        "brewery": {"primary": "#7C2D12", "secondary": "#B91C1C", "accent": "#A16207", "background": "#FEF2F2", "text": "#450A0A", "card": "#FFFFFF", "muted": "#ECEDF0", "border": "#FECACA", "name": "Brew Red"},
        # Transport & Media
        "airline": {"primary": "#1E3A8A", "secondary": "#3B82F6", "accent": "#EA580C", "background": "#EFF6FF", "text": "#1E40AF", "card": "#FFFFFF", "muted": "#E9EEF5", "border": "#BFDBFE", "name": "Sky Royal"},
        "news-media": {"primary": "#DC2626", "secondary": "#EF4444", "accent": "#1E40AF", "background": "#FEF2F2", "text": "#450A0A", "card": "#FFFFFF", "muted": "#F0EDF1", "border": "#FECACA", "name": "News Red"},
        "magazine": {"primary": "#18181B", "secondary": "#3F3F46", "accent": "#EC4899", "background": "#FAFAFA", "text": "#09090B", "card": "#FFFFFF", "muted": "#E8ECF0", "border": "#E4E4E7", "name": "Editorial Mono"},
        # Freelancer & Agency
        "freelancer": {"primary": "#4338CA", "secondary": "#6366F1", "accent": "#16A34A", "background": "#EEF2FF", "text": "#312E81", "card": "#FFFFFF", "muted": "#EBEFF9", "border": "#C7D2FE", "name": "Freelance Indigo"},
        "marketing-agency": {"primary": "#EC4899", "secondary": "#F472B6", "accent": "#0891B2", "background": "#FDF2F8", "text": "#831843", "card": "#FFFFFF", "muted": "#F1EEF5", "border": "#FBCFE8", "name": "Marketing Pink"},
        "event-management": {"primary": "#3A51ED", "secondary": "#A78BFA", "accent": "#EA580C", "background": "#FAF5FF", "text": "#4C1D95", "card": "#FFFFFF", "muted": "#ECEEF9", "border": "#DDD6FE", "name": "Event Purple"},
        # Community & Membership
        "membership": {"primary": "#ED3AD7", "secondary": "#A78BFA", "accent": "#16A34A", "background": "#FAF5FF", "text": "#4C1D95", "card": "#FFFFFF", "muted": "#ECEEF9", "border": "#DDD6FE", "name": "Community Purple"},
        "newsletter": {"primary": "#0219A1", "secondary": "#0EA5E9", "accent": "#EA580C", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E7EFF5", "border": "#BAE6FD", "name": "Newsletter Sky"},
        "digital-products": {"primary": "#4F46E5", "secondary": "#6366F1", "accent": "#16A34A", "background": "#EEF2FF", "text": "#312E81", "card": "#FFFFFF", "muted": "#EBEFF9", "border": "#C7D2FE", "name": "Digital Indigo"},
        "church": {"primary": "#ED3A51", "secondary": "#A78BFA", "accent": "#A16207", "background": "#FAF5FF", "text": "#4C1D95", "card": "#FFFFFF", "muted": "#ECEEF9", "border": "#DDD6FE", "name": "Faith Purple"},
        # Web3 & Digital
        "nft-web3": {"primary": "#8B5CF6", "secondary": "#A78BFA", "accent": "#FBBF24", "background": "#0F0F23", "text": "#F8FAFC", "card": "#1E1D35", "muted": "#27273B", "border": "#4C1D95", "name": "Web3 Violet"},
        "remote-work": {"primary": "#5B21B6", "secondary": "#7C3AED", "accent": "#059669", "background": "#F5F3FF", "text": "#312E81", "card": "#FFFFFF", "muted": "#EBEFF9", "border": "#E0E7FF", "name": "Remote Indigo"},
        # Streaming & Music
        "music-streaming": {"primary": "#1E1B4B", "secondary": "#4338CA", "accent": "#22C55E", "background": "#0F0F23", "text": "#F8FAFC", "card": "#1B1B30", "muted": "#27273B", "border": "#312E81", "name": "Sound Indigo"},
        # Recruitment & Local
        "recruitment": {"primary": "#02A18A", "secondary": "#0EA5E9", "accent": "#16A34A", "background": "#F0F9FF", "text": "#0C4A6E", "card": "#FFFFFF", "muted": "#E7EFF5", "border": "#BAE6FD", "name": "Career Sky"},
        "hyperlocal": {"primary": "#059669", "secondary": "#10B981", "accent": "#EA580C", "background": "#ECFDF5", "text": "#064E3B", "card": "#FFFFFF", "muted": "#E8F1F3", "border": "#A7F3D0", "name": "Local Green"},
        "online-course": {"primary": "#0D9488", "secondary": "#2DD4BF", "accent": "#EA580C", "background": "#F0FDFA", "text": "#134E4A", "card": "#FFFFFF", "muted": "#E8F1F4", "border": "#5EEAD4", "name": "Course Teal"},
    }

    PRODUCT_TYPOGRAPHY_PRESETS: dict[str, dict[str, str]] = {
        "saas": {"heading": "Manrope", "body": "Source Sans 3", "mood": "professional, clear, product-focused", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Manrope:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600&display=swap');"},
        "ecommerce": {"heading": "DM Sans", "body": "Inter", "mood": "friendly, approachable, trustworthy", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=DM+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');"},
        "ecommerce-luxury": {"heading": "Cormorant Garamond", "body": "Montserrat", "mood": "elegant, luxury, sophisticated", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');"},
        "fintech": {"heading": "Space Grotesk", "body": "IBM Plex Sans", "mood": "technical, trustworthy, precise", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');"},
        "healthcare": {"heading": "Plus Jakarta Sans", "body": "Nunito Sans", "mood": "calming, professional, accessible", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Nunito+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');"},
        "education": {"heading": "Outfit", "body": "Source Sans 3", "mood": "clear, friendly, encouraging", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Outfit:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');"},
        "gaming": {"heading": "Rajdhani", "body": "Exo 2", "mood": "bold, energetic, futuristic", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Exo+2:wght@400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');"},
        "beauty-spa": {"heading": "Cormorant Garamond", "body": "Montserrat", "mood": "elegant, calming, sophisticated", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');"},
        "content": {"heading": "Merriweather", "body": "Source Sans 3", "mood": "readable, editorial, classic", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Merriweather:wght@400;700&family=Source+Sans+3:wght@400;500;600&display=swap');"},
        "dashboard": {"heading": "IBM Plex Sans", "body": "Public Sans", "mood": "dense, operational, precise", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=IBM+Plex+Sans:wght@500;600;700&family=Public+Sans:wght@400;500;600&display=swap');"},
        "portfolio": {"heading": "Space Grotesk", "body": "Inter", "mood": "creative, distinctive, modern", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');"},
        "landing": {"heading": "Space Grotesk", "body": "DM Sans", "mood": "confident, distinctive, conversion-focused", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=DM+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');"},
        "social-media": {"heading": "Poppins", "body": "Open Sans", "mood": "modern, friendly, social", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Open+Sans:wght@400;500;600&family=Poppins:wght@400;500;600;700&display=swap');"},
        "restaurant": {"heading": "Playfair Display", "body": "Lato", "mood": "warm, appetizing, inviting", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Lato:wght@400;700&family=Playfair+Display:wght@400;500;600;700&display=swap');"},
        "real-estate": {"heading": "DM Serif Display", "body": "DM Sans", "mood": "premium, trustworthy, established", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');"},
        "legal": {"heading": "EB Garamond", "body": "Source Sans 3", "mood": "authoritative, traditional, trustworthy", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=EB+Garamond:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');"},
        "general": {"heading": "Manrope", "body": "Source Sans 3", "mood": "modern, professional, adaptable", "css_import": "@import url('https://fonts.googleapis.cn/css2?family=Manrope:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600&display=swap');"},
    }

    PRE_DELIVERY_CHECKLIST: list[str] = [
        "SVG 图标替代所有 emoji（使用 Lucide/Heroicons/Tabler）",
        "所有可点击元素具有 cursor-pointer",
        "hover 状态使用 150-300ms 平滑过渡",
        "浅色模式文字对比度至少 4.5:1（WCAG AA）",
        "focus 状态对键盘导航可见",
        "尊重 prefers-reduced-motion 偏好设置",
        "响应式断点覆盖：375px / 768px / 1024px / 1440px",
        "深色模式文字对比度至少 4.5:1（如适用）",
        "按钮和输入框高度一致（40px 基线）",
        "卡片圆角统一（8-12px）",
        "loading/empty/error/disabled 状态完整",
        "品牌字体已加载，无系统字体回退直出",
    ]

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
                    "可与 Aceternity UI / Magic UI 的视觉模块组合，提升品牌差异化表现",
                ],
                notes=[
                    "必须先定义 token、容器、字重和信息密度，再批量生成组件",
                    "表单建议配合 React Hook Form + Zod",
                    "视觉特效组件仅用于首屏叙事与反馈，避免影响可读性和性能",
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
                name="DaisyUI + Tailwind CSS",
                category="Alternative",
                rationale="适合多主题业务和快速产出高一致性视觉。",
                strengths=[
                    "主题切换能力强，适合白标与多品牌场景",
                    "与 Tailwind 兼容，开发效率高",
                ],
                notes=[
                    "需要补充高级组件与版式体系，避免默认主题观感",
                ],
            ),
            LibraryRecommendation(
                name="Aceternity UI / Magic UI",
                category="Alternative",
                rationale="适合官网、品牌页和叙事型 landing，增强视觉张力。",
                strengths=[
                    "高质量视觉模块与动效资源丰富",
                    "可快速构建有辨识度的商业首屏",
                ],
                notes=[
                    "必须设置性能预算并搭配可读性审查，避免炫技化",
                ],
            ),
            LibraryRecommendation(
                name="NextUI + Tailwind CSS",
                category="Alternative",
                rationale="适合需要现代感与动效且开发效率优先的 React/Next 项目。",
                strengths=[
                    "内置 Framer Motion 动效，开箱即用的过渡与微交互",
                    "组件视觉精美，深色模式支持优秀",
                    "与 Tailwind CSS 深度集成，定制灵活",
                ],
                notes=[
                    "组件库仍在快速迭代中，注意版本兼容",
                    "大型表格和复杂表单场景需要补充 TanStack Table 等",
                ],
            ),
            LibraryRecommendation(
                name="MUI (Material UI)",
                category="Alternative",
                rationale="适合大型企业应用和需要完整组件覆盖的 React 项目。",
                strengths=[
                    "组件覆盖最全（60+），文档完善，社区庞大",
                    "Material Design 3 主题系统成熟，token 化能力强",
                    "Data Grid、Date Picker 等高级组件企业级可用",
                ],
                notes=[
                    "包体较大，需要 tree-shaking 优化",
                    "默认 Material 风格强烈，品牌化需要大量主题覆盖",
                ],
            ),
            LibraryRecommendation(
                name="Mantine",
                category="Alternative",
                rationale="适合全栈 React 项目和需要丰富 hooks 与工具库的场景。",
                strengths=[
                    "100+ 组件 + 50+ hooks，功能覆盖极广",
                    "内置表单管理、通知系统、富文本编辑器",
                    "深色模式和主题定制体验优秀",
                ],
                notes=[
                    "样式方案与 Tailwind 并行使用时需要协调",
                    "更新频率高，大版本升级需关注 breaking changes",
                ],
            ),
            LibraryRecommendation(
                name="Chakra UI",
                category="Alternative",
                rationale="适合重视可访问性和开发体验的 React 项目。",
                strengths=[
                    "无障碍性（A11y）开箱即用，符合 WAI-ARIA",
                    "Style Props 系统直观，开发效率高",
                    "主题系统灵活，支持语义化 token",
                ],
                notes=[
                    "运行时 CSS-in-JS 有性能开销，SSR 场景需注意",
                    "组件视觉相对朴素，品牌化需要额外设计投入",
                ],
            ),
            LibraryRecommendation(
                name="Headless UI + Tailwind CSS",
                category="Alternative",
                rationale="适合对视觉完全自主控制、不想受组件库风格限制的项目。",
                strengths=[
                    "完全无样式的交互组件，视觉 100% 由开发者定义",
                    "由 Tailwind Labs 官方维护，与 Tailwind 完美集成",
                    "无障碍性内置，键盘导航和 ARIA 支持完善",
                ],
                notes=[
                    "组件数量有限（~15 个），复杂场景需要自建组件",
                    "适合有设计能力的团队，纯开发团队上手成本较高",
                ],
            ),
            LibraryRecommendation(
                name="Tremor + Tailwind CSS",
                category="Alternative",
                rationale="适合数据仪表板和 KPI 展示型产品，开箱即用的图表与指标组件。",
                strengths=[
                    "专为 Dashboard 设计，KPI 卡片/图表/列表组件即开即用",
                    "与 Recharts 深度集成，数据可视化能力强",
                    "Tailwind 原生，主题定制简单",
                ],
                notes=[
                    "仅适合数据展示场景，不适合通用 UI",
                    "组件数量有限，营销页和表单场景需要搭配其他库",
                ],
            ),
            LibraryRecommendation(
                name="Park UI + Ark UI",
                category="Alternative",
                rationale="适合需要跨框架一致性（React/Vue/Solid）的设计系统项目。",
                strengths=[
                    "基于 Ark UI 的 headless 层，支持 React/Vue/Solid 三框架",
                    "预设主题精美，视觉质量高",
                    "Panda CSS 集成，token 化设计系统",
                ],
                notes=[
                    "生态相对新，社区资源不如 shadcn/MUI 丰富",
                    "需要了解 Panda CSS 的工作方式",
                ],
            ),
            LibraryRecommendation(
                name="Arco Design React",
                category="Alternative",
                rationale="适合追求现代感中后台的 React 项目，字节跳动出品。",
                strengths=[
                    "60+ 组件覆盖，视觉比 Ant Design 更现代精致",
                    "暗色模式和主题定制开箱即用",
                    "IconBox 和插画资源丰富",
                ],
                notes=[
                    "社区不如 Ant Design 庞大，但组件质量高",
                ],
            ),
            LibraryRecommendation(
                name="Ant Design Mobile",
                category="Alternative",
                rationale="适合 H5 移动端和混合 APP 的 React 项目。",
                strengths=[
                    "移动端交互模式成熟（下拉刷新、滑动、手势）",
                    "与 Ant Design 桌面版设计语言统一",
                    "高性能虚拟列表和懒加载内置",
                ],
                notes=[
                    "仅适合移动端/H5，不适合桌面端",
                ],
            ),
            LibraryRecommendation(
                name="Semi Design",
                category="Alternative",
                rationale="适合追求设计工程化和主题定制的 React 项目，抖音出品。",
                strengths=[
                    "DSM（Design to Code）设计工程化能力强",
                    "2800+ Design Token，主题定制粒度极细",
                    "A11y 优先，WAI-ARIA 支持完善",
                ],
                notes=[
                    "国际化社区较小，中文生态为主",
                ],
            ),
            LibraryRecommendation(
                name="TDesign React",
                category="Alternative",
                rationale="适合遵循腾讯设计规范的 React 项目。",
                strengths=[
                    "腾讯官方设计系统，组件覆盖完整",
                    "与 TDesign 小程序版设计语言统一，适合跨端一致性",
                    "Starter Kit 开箱即用",
                ],
                notes=[
                    "主要面向腾讯生态，外部社区较小",
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
                name="Ant Design Vue",
                category="Alternative",
                rationale="适合中后台系统和中文团队的 Vue 项目，Ant Design 生态的 Vue 实现。",
                strengths=[
                    "与 Ant Design React 版保持一致的设计语言和组件覆盖",
                    "表格、表单、树形、日期选择等 B 端核心组件成熟",
                    "中文文档完善，国内社区活跃",
                ],
                notes=[
                    "默认 Ant 风格强烈，品牌化需要通过 ConfigProvider 做主题覆盖",
                    "包体较大，建议按需引入",
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
            LibraryRecommendation(
                name="Vuetify 3",
                category="Alternative",
                rationale="适合遵循 Material Design 3 规范的 Vue 项目。",
                strengths=[
                    "Material Design 3 官方级实现，组件覆盖 70+",
                    "内置网格系统、主题引擎和无障碍支持",
                    "企业级组件（Data Table、Treeview）成熟",
                ],
                notes=[
                    "包体较大，需要按需引入优化",
                    "视觉强绑定 Material，品牌化需要大量 token 覆盖",
                ],
            ),
            LibraryRecommendation(
                name="PrimeVue",
                category="Alternative",
                rationale="适合需要完整组件覆盖和多主题支持的 Vue 企业项目。",
                strengths=[
                    "90+ 组件覆盖，含 DataTable、Chart、Editor 等高级组件",
                    "多种预设主题（Lara/Aura/Nora），无障碍优先设计",
                    "支持 unstyled 模式，可完全自定义视觉",
                ],
                notes=[
                    "预设主题风格独特，品牌化需要主题定制",
                ],
            ),
            LibraryRecommendation(
                name="Radix Vue + Tailwind CSS",
                category="Alternative",
                rationale="适合追求 Vue 版 shadcn 级别控制力的项目。",
                strengths=[
                    "headless 组件，视觉完全由 Tailwind 控制",
                    "无障碍内置，与 shadcn-vue 配合使用",
                ],
                notes=[
                    "生态较新，需要自建部分业务组件",
                ],
            ),
            LibraryRecommendation(
                name="TDesign Vue Next",
                category="Alternative",
                rationale="适合遵循腾讯设计规范的 Vue 3 项目，与小程序端保持统一。",
                strengths=[
                    "腾讯官方 Vue 3 组件库，与 TDesign 小程序设计语言统一",
                    "适合需要 Web + 小程序跨端一致性的项目",
                    "Starter Kit 和模板项目开箱即用",
                ],
                notes=[
                    "主要面向腾讯生态，外部社区相对较小",
                ],
            ),
            LibraryRecommendation(
                name="Vant 4",
                category="Alternative",
                rationale="适合 H5 移动端的 Vue 3 项目，有赞出品。",
                strengths=[
                    "70+ 移动端组件，触控交互和手势支持成熟",
                    "轻量高性能，按需引入后包体小",
                    "多语言和多主题支持",
                ],
                notes=[
                    "仅适合移动端/H5，不适合桌面端中后台",
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
            ),
            LibraryRecommendation(
                name="PrimeNG",
                category="Alternative",
                rationale="适合需要丰富组件和企业级功能的 Angular 项目。",
                strengths=[
                    "80+ 组件覆盖，含 TreeTable、Schedule、Editor 等高级组件",
                    "多主题预设（Lara/Aura），支持深色模式",
                    "社区活跃，商业支持可用",
                ],
                notes=[
                    "默认主题风格偏传统，品牌化需定制",
                ],
            ),
            LibraryRecommendation(
                name="NG-ZORRO (Ant Design of Angular)",
                category="Alternative",
                rationale="适合中后台和中文团队的 Angular 项目。",
                strengths=[
                    "Ant Design 规范的 Angular 实现，组件覆盖完整",
                    "中文文档完善，国内社区活跃",
                    "表格、表单、树形等 B 端核心组件成熟",
                ],
                notes=[
                    "与 Ant Design React 版保持视觉一致，品牌化需额外投入",
                ],
            ),
            LibraryRecommendation(
                name="Spartan UI + Tailwind CSS",
                category="Alternative",
                rationale="适合追求 Angular 版 shadcn 体验的项目。",
                strengths=[
                    "shadcn/ui 的 Angular 移植版，headless + Tailwind 组合",
                    "完全可定制，品牌控制力强",
                ],
                notes=[
                    "生态较新，组件数量持续增长中",
                ],
            ),
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
        "desktop": [
            LibraryRecommendation(
                name="Electron / Tauri + React/Vue + Tailwind + 桌面组件库",
                category="Primary",
                rationale="适合跨平台桌面应用，兼顾 Web 技术效率与桌面系统能力。",
                strengths=[
                    "可复用现有 Web 组件体系与设计 token",
                    "便于集成文件系统、托盘、通知、离线缓存等桌面能力",
                ],
                notes=[
                    "窗口布局、快捷键、菜单栏、深色模式需按桌面范式设计",
                    "避免把桌面端做成纯网页壳，需补齐本地能力交互",
                ],
            ),
            LibraryRecommendation(
                name="Wails / Tauri + 原生壳层",
                category="Alternative",
                rationale="适合更轻量、资源占用更低的桌面客户端。",
                strengths=[
                    "包体更轻，启动性能更好",
                ],
                notes=[
                    "需要明确前后端通信契约与本地权限边界",
                ],
            ),
        ],
        "react-native": [
            LibraryRecommendation(
                name="React Native + NativeWind + Tamagui / React Native Paper",
                category="Primary",
                rationale="适合 AI Coding 场景快速落地跨端 APP，同时保持可控品牌系统。",
                strengths=[
                    "跨平台组件复用效率高",
                    "可通过 token 保持与 Web/H5 品牌一致",
                ],
                notes=[
                    "导航、手势、系统权限优先按原生范式设计",
                    "避免直接照搬 Web 布局和交互节奏",
                ],
            )
        ],
        "flutter": [
            LibraryRecommendation(
                name="Flutter + Material 3 / Cupertino + FlexColorScheme",
                category="Primary",
                rationale="适合高性能跨端 APP 与复杂动画场景。",
                strengths=[
                    "渲染一致性高，组件体系完整",
                    "动画和复杂交互实现能力强",
                ],
                notes=[
                    "必须先定义主题和组件状态映射，避免默认 Material 风格直出",
                ],
            )
        ],
        "swiftui": [
            LibraryRecommendation(
                name="SwiftUI + Design Tokens + SF Symbols",
                category="Primary",
                rationale="适合 iOS 原生体验优先的商业 APP。",
                strengths=[
                    "原生体验、动效和无障碍能力优秀",
                    "便于与 iOS 设计规范对齐",
                ],
                notes=[
                    "遵循 Human Interface Guidelines，避免网页式信息堆叠",
                ],
            )
        ],
        "miniapp": [
            LibraryRecommendation(
                name="TDesign 小程序 + Taro / UniApp + Tailwind(TW 适配)",
                category="Primary",
                rationale="适合微信小程序商业场景，兼顾腾讯生态组件规范与跨端复用。",
                strengths=[
                    "符合微信生态交互习惯，组件成熟",
                    "支持表单、弹层、列表、导航等高频业务组件快速搭建",
                ],
                notes=[
                    "小程序端优先使用 TDesign 组件与交互模式",
                    "触控区域、性能包体、分包策略需前置约束",
                ],
            ),
            LibraryRecommendation(
                name="Vant Weapp / NutUI(小程序)",
                category="Alternative",
                rationale="适合轻量业务与已有技术栈迁移。",
                strengths=[
                    "上手成本低，社区资料丰富",
                ],
                notes=[
                    "需要额外做品牌 token 重写，避免默认风格模板化",
                ],
            ),
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

    # 向后兼容：旧测试和外部调用仍可能使用 COMPONENT_LIBRARIES 这个名字。
    COMPONENT_LIBRARIES = STACK_RECOMMENDATIONS

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
        "miniapp": {
            "default": "F2 / ECharts 小程序版",
            "dense": "F2 + 自定义业务图层",
        },
        "react-native": {
            "default": "Victory Native / React Native Skia Charts",
            "dense": "Skia-based custom charts",
        },
        "flutter": {
            "default": "fl_chart / Syncfusion Flutter Charts",
            "dense": "Syncfusion / CustomPainter charts",
        },
        "swiftui": {
            "default": "Swift Charts",
            "dense": "Swift Charts + custom marks",
        },
        "desktop": {
            "default": "ECharts / Plotly（桌面高密度分析）",
            "dense": "ECharts + AG Grid integrated charts",
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
        "miniapp": "TDesign Form + 小程序原生校验",
        "react-native": "React Hook Form + Zod + controlled inputs",
        "flutter": "Form + Validator + Riverpod/BLoC",
        "swiftui": "SwiftUI Form + Observable validation",
        "desktop": "Schema Form + local persistence + shortcut actions",
        "default": "Schema-driven validation + typed DTO",
    }

    MOTION_STACK = {
        "react": "Framer Motion（营销/品牌页） + CSS transitions（工作台）",
        "vue": "VueUse Motion / Motion One + CSS transitions",
        "angular": "Angular Animations + CSS transitions",
        "svelte": "Svelte transitions + Motion One",
        "miniapp": "小程序原生动画 + 轻量过渡（避免重动画）",
        "react-native": "Reanimated / Moti + native transitions",
        "flutter": "Implicit animations + Motion spec",
        "swiftui": "SwiftUI animation + spring transitions",
        "desktop": "Micro-interaction transitions + window state animations",
        "default": "Meaningful CSS transitions only",
    }

    @staticmethod
    def generate_dark_variant(palette: dict[str, str]) -> dict[str, str]:
        """从浅色配色方案自动生成暗色变体"""
        bg = palette.get("background", "#FFFFFF")

        # If already dark (background is dark), return as-is
        bg_hex = bg.lstrip("#")
        if len(bg_hex) == 6:
            r, g, b = int(bg_hex[:2], 16), int(bg_hex[2:4], 16), int(bg_hex[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            if luminance < 0.4:
                return dict(palette)  # Already dark

        # Generate dark variant
        return {
            "primary": palette.get("primary", "#2563EB"),
            "secondary": palette.get("secondary", "#3B82F6"),
            "accent": palette.get("accent", "#EA580C"),
            "background": "#0F172A",
            "text": "#F8FAFC",
            "card": "#1E293B",
            "muted": "#334155",
            "border": "#475569",
            "name": palette.get("name", "Dark") + " Dark",
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
            "同一产品在 Web/H5/小程序/APP 需保持品牌一致，同时保留平台原生交互习惯",
        ]

        trust_modules = list(industry_rules["trust_modules"]) + list(profile["conversion_modules"])
        banned_patterns = list(profile["banned_patterns"]) + list(industry_rules["banned_patterns"]) + [
            "emoji 充当功能图标或临时占位图标",
            "Claude / ChatGPT 同款侧栏聊天骨架与窄中栏对话壳层",
            "以灰黑中性色为主、几乎无品牌辨识度的聊天式产品外壳",
        ]

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
        ui_library_matrix = [
            {"scene": "Web 工作台", "libraries": "shadcn/ui + Radix + Tailwind", "focus": "高密度任务与状态可见性"},
            {"scene": "品牌官网/H5", "libraries": "Tailwind + Aceternity UI / Magic UI", "focus": "叙事转化与视觉识别"},
            {"scene": "多主题业务", "libraries": "Tailwind + DaisyUI", "focus": "主题系统与快速迭代"},
            {"scene": "微信小程序", "libraries": "TDesign 小程序 + Taro / UniApp", "focus": "腾讯生态规范、触控效率与性能包体"},
            {"scene": "APP", "libraries": "React Native / Flutter / SwiftUI", "focus": "手势、反馈、导航与原生体验一致性"},
            {"scene": "桌面端", "libraries": "Electron / Tauri + React/Vue + Tailwind", "focus": "窗口范式、快捷键与本地能力集成"},
        ]
        quality_checklist = [
            "必须提供 token（color/typography/spacing/radius/shadow/motion）并可复用",
            "必须覆盖关键状态（loading/empty/error/success/permission）",
            "必须具备商业信任模块（案例、指标、定价、FAQ、合规）",
            "必须通过可访问性检查（对比度、键盘、focus、reduced motion）",
            "必须通过品牌差异化检查（字体层级、配色节奏、图形语言）",
        ]

        style_direction = self._build_style_direction(style=style, product_type=product_type, industry=industry)
        database_keywords = self._knowledge_keywords(
            description=description,
            product_type=product_type,
            industry=industry,
            frontend=normalized_frontend,
        )

        # Find matching palette
        palette_key = product_type
        if palette_key not in self.PRODUCT_COLOR_PALETTES:
            # Try industry match
            palette_key = industry if industry in self.PRODUCT_COLOR_PALETTES else "general"
        color_palette = self.PRODUCT_COLOR_PALETTES.get(palette_key, self.PRODUCT_COLOR_PALETTES["general"])

        # Find matching typography
        typo_key = product_type
        if typo_key not in self.PRODUCT_TYPOGRAPHY_PRESETS:
            typo_key = industry if industry in self.PRODUCT_TYPOGRAPHY_PRESETS else "general"
        typography_preset = self.PRODUCT_TYPOGRAPHY_PRESETS.get(typo_key, self.PRODUCT_TYPOGRAPHY_PRESETS["general"])

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
            "ui_library_matrix": ui_library_matrix,
            "quality_checklist": quality_checklist,
            "color_palette": color_palette,
            "color_palette_dark": self.generate_dark_variant(color_palette),
            "typography_preset": typography_preset,
            "pre_delivery_checklist": list(self.PRE_DELIVERY_CHECKLIST),
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
            if frontend == "miniapp":
                return "TDesign Table / 虚拟列表 + 分页筛选"
            if frontend in {"react-native", "flutter", "swiftui"}:
                return "Virtualized List + Filter Chips + Sticky Header"
            if frontend == "desktop":
                return "AG Grid / Naive DataTable + Split View + Local Index"
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

    # ------------------------------------------------------------------
    # Responsive Design Validation
    # ------------------------------------------------------------------

    def _check_responsive_design(self, css_content: str, html_content: str = "") -> dict[str, Any]:
        """
        检查响应式设计实现质量。

        分析 CSS 中的媒体查询、响应式单位使用情况，以及是否存在不推荐的固定像素宽度。

        Args:
            css_content: CSS 文件内容
            html_content: 可选的 HTML 内容，用于检查 viewport meta

        Returns:
            包含响应式设计评估结果的字典
        """
        import re

        issues: list[dict[str, str]] = []
        suggestions: list[str] = []
        score = 100

        # 1. Check for media queries
        media_queries = re.findall(r"@media\s*\([^)]+\)", css_content)
        media_breakpoints: list[str] = []
        for mq in media_queries:
            bp_match = re.search(r"(\d+)px", mq)
            if bp_match:
                media_breakpoints.append(bp_match.group(1))

        standard_breakpoints = {"375", "480", "640", "768", "1024", "1280", "1440"}
        covered_breakpoints = set(media_breakpoints) & standard_breakpoints
        missing_breakpoints = standard_breakpoints - set(media_breakpoints)

        if not media_queries:
            issues.append({
                "severity": "high",
                "message": "CSS 中未发现任何媒体查询（@media），页面可能无法在不同屏幕尺寸下正常显示",
                "fix": "添加至少 3 个断点的媒体查询：768px（平板）、1024px（小桌面）、1440px（大桌面）",
            })
            score -= 30
        elif len(media_queries) < 3:
            issues.append({
                "severity": "medium",
                "message": f"仅发现 {len(media_queries)} 个媒体查询，建议覆盖更多断点",
                "fix": "建议至少覆盖 375px / 768px / 1024px / 1440px 四个常用断点",
            })
            score -= 15

        # 2. Check for responsive units usage
        responsive_units = {
            "rem": len(re.findall(r"[\d.]+rem", css_content)),
            "em": len(re.findall(r"[\d.]+em(?!s)", css_content)),
            "%": len(re.findall(r"[\d.]+%", css_content)),
            "vw": len(re.findall(r"[\d.]+vw", css_content)),
            "vh": len(re.findall(r"[\d.]+vh", css_content)),
            "vmin": len(re.findall(r"[\d.]+vmin", css_content)),
            "vmax": len(re.findall(r"[\d.]+vmax", css_content)),
            "clamp": len(re.findall(r"clamp\(", css_content)),
            "min()": len(re.findall(r"min\(", css_content)),
            "max()": len(re.findall(r"max\(", css_content)),
        }
        total_responsive_units = sum(responsive_units.values())
        total_px_units = len(re.findall(r"[\d.]+px", css_content))

        if total_responsive_units == 0:
            issues.append({
                "severity": "high",
                "message": "未使用任何响应式单位（rem/em/%/vw/vh/clamp），全部使用固定像素",
                "fix": "字体建议使用 rem，容器宽度建议使用 % 或 max-width，间距建议使用 rem 或 em",
            })
            score -= 25
        elif total_px_units > 0 and total_responsive_units / (total_px_units + total_responsive_units) < 0.3:
            issues.append({
                "severity": "medium",
                "message": f"响应式单位占比偏低（{total_responsive_units}/{total_px_units + total_responsive_units}），大量使用固定像素",
                "fix": "建议将字体、间距和容器尺寸逐步迁移到 rem/% 等响应式单位",
            })
            score -= 10

        # 3. Check for hardcoded pixel widths (anti-pattern)
        hardcoded_width_pattern = re.compile(
            r"(?:^|\s|;)width\s*:\s*(\d+)px", re.MULTILINE
        )
        hardcoded_widths = hardcoded_width_pattern.findall(css_content)
        problematic_widths = [w for w in hardcoded_widths if int(w) > 320]

        if problematic_widths:
            issues.append({
                "severity": "medium",
                "message": f"发现 {len(problematic_widths)} 个硬编码的大像素宽度值：{', '.join(problematic_widths[:5])}px",
                "fix": "使用 max-width 代替 width，或使用百分比和 min()/max()/clamp() 函数",
            })
            score -= min(len(problematic_widths) * 3, 15)

        # 4. Check for hardcoded pixel heights on containers
        hardcoded_height_pattern = re.compile(
            r"(?:^|\s|;)height\s*:\s*(\d+)px", re.MULTILINE
        )
        hardcoded_heights = hardcoded_height_pattern.findall(css_content)
        large_fixed_heights = [h for h in hardcoded_heights if int(h) > 200]
        if large_fixed_heights:
            issues.append({
                "severity": "low",
                "message": f"发现 {len(large_fixed_heights)} 个大的固定高度值，可能导致内容溢出",
                "fix": "考虑使用 min-height 代替 height，或使用 auto/fit-content",
            })
            score -= 5

        # 5. Check for flexible layout usage
        flexbox_count = len(re.findall(r"display\s*:\s*flex", css_content))
        grid_count = len(re.findall(r"display\s*:\s*grid", css_content))
        if flexbox_count == 0 and grid_count == 0:
            issues.append({
                "severity": "high",
                "message": "未使用 Flexbox 或 Grid 布局，可能依赖过时的浮动或定位布局",
                "fix": "优先使用 CSS Grid 进行页面布局，Flexbox 进行组件内部布局",
            })
            score -= 20

        # 6. Check viewport meta in HTML
        has_viewport_meta = False
        if html_content:
            has_viewport_meta = "viewport" in html_content and "width=device-width" in html_content
            if not has_viewport_meta:
                issues.append({
                    "severity": "high",
                    "message": "HTML 缺少正确的 viewport meta 标签",
                    "fix": '添加 <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
                })
                score -= 15

        # 7. Check for container queries (modern CSS)
        container_queries = len(re.findall(r"@container", css_content))

        # 8. Check for overflow handling
        overflow_hidden_count = len(re.findall(r"overflow\s*:\s*hidden", css_content))
        overflow_auto_count = len(re.findall(r"overflow(?:-[xy])?\s*:\s*(?:auto|scroll)", css_content))
        text_overflow_count = len(re.findall(r"text-overflow\s*:\s*ellipsis", css_content))

        # Generate suggestions
        if not container_queries:
            suggestions.append("考虑使用 @container 查询实现组件级响应式设计（现代浏览器已广泛支持）")
        if responsive_units.get("clamp", 0) == 0:
            suggestions.append("建议使用 clamp() 实现流畅的字体和间距缩放，例如 font-size: clamp(1rem, 2.5vw, 2rem)")
        if not text_overflow_count:
            suggestions.append("建议为文本内容添加 text-overflow: ellipsis 处理溢出场景")
        if len(covered_breakpoints) < 3:
            suggestions.append(f"建议补充以下断点的媒体查询：{', '.join(sorted(missing_breakpoints)[:3])}px")

        score = max(0, min(100, score))

        return {
            "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
            "media_queries": {
                "count": len(media_queries),
                "breakpoints_found": sorted(set(media_breakpoints)),
                "standard_covered": sorted(covered_breakpoints),
                "standard_missing": sorted(missing_breakpoints),
            },
            "unit_usage": {
                "responsive_units": {k: v for k, v in responsive_units.items() if v > 0},
                "fixed_px_count": total_px_units,
                "responsive_ratio": round(
                    total_responsive_units / max(total_px_units + total_responsive_units, 1), 2
                ),
            },
            "layout": {
                "flexbox_usage": flexbox_count,
                "grid_usage": grid_count,
                "container_queries": container_queries,
            },
            "overflow_handling": {
                "overflow_hidden": overflow_hidden_count,
                "overflow_auto_scroll": overflow_auto_count,
                "text_overflow_ellipsis": text_overflow_count,
            },
            "hardcoded_widths": [f"{w}px" for w in problematic_widths[:10]],
            "has_viewport_meta": has_viewport_meta if html_content else "N/A",
            "issues": issues,
            "suggestions": suggestions,
        }

    # ------------------------------------------------------------------
    # Accessibility Depth Check
    # ------------------------------------------------------------------

    def _check_accessibility_depth(self, html_content: str, css_content: str = "") -> dict[str, Any]:
        """
        深度检查无障碍（A11y）合规性。

        覆盖图片 alt 属性、表单 label 关联、颜色对比度、skip navigation、
        ARIA 属性和键盘导航支持等。

        Args:
            html_content: HTML 文件内容
            css_content: CSS 文件内容（可选，用于提取颜色变量计算对比度）

        Returns:
            包含无障碍评估结果的字典
        """
        import re

        issues: list[dict[str, str]] = []
        passes: list[str] = []
        score = 100

        # 1. Check images for alt attributes
        img_tags = re.findall(r"<img\b[^>]*>", html_content, re.IGNORECASE)
        imgs_without_alt: list[str] = []
        imgs_with_empty_alt = 0
        imgs_with_alt = 0

        for img in img_tags:
            if 'alt=' not in img.lower():
                src_match = re.search(r'src\s*=\s*["\']([^"\']*)', img)
                imgs_without_alt.append(src_match.group(1) if src_match else "(unknown)")
            elif re.search(r'alt\s*=\s*["\'][\s]*["\']', img):
                imgs_with_empty_alt += 1
            else:
                imgs_with_alt += 1

        if imgs_without_alt:
            issues.append({
                "severity": "high",
                "message": f"{len(imgs_without_alt)} 个图片缺少 alt 属性：{', '.join(imgs_without_alt[:5])}",
                "fix": "为所有 <img> 标签添加描述性 alt 属性。纯装饰图片使用 alt=\"\"",
                "wcag": "WCAG 2.1 SC 1.1.1 Non-text Content (Level A)",
            })
            score -= min(len(imgs_without_alt) * 5, 20)
        else:
            passes.append("所有图片均包含 alt 属性")

        # 2. Check forms for label associations
        input_tags = re.findall(
            r"<(?:input|select|textarea)\b[^>]*>", html_content, re.IGNORECASE
        )
        inputs_without_label: list[str] = []
        label_for_ids = set(re.findall(r'<label\b[^>]*for\s*=\s*["\']([^"\']+)', html_content, re.IGNORECASE))
        aria_labelled_ids = set()

        for inp in input_tags:
            # Skip hidden inputs and submit buttons
            if re.search(r'type\s*=\s*["\'](?:hidden|submit|button)["\']', inp, re.IGNORECASE):
                continue
            inp_id_match = re.search(r'id\s*=\s*["\']([^"\']+)', inp)
            has_aria_label = 'aria-label=' in inp.lower() or 'aria-labelledby=' in inp.lower()
            if inp_id_match:
                inp_id = inp_id_match.group(1)
                if inp_id in label_for_ids or has_aria_label:
                    aria_labelled_ids.add(inp_id)
                    continue

            if not has_aria_label:
                name_match = re.search(r'name\s*=\s*["\']([^"\']+)', inp)
                inputs_without_label.append(name_match.group(1) if name_match else "(unnamed)")

        if inputs_without_label:
            issues.append({
                "severity": "high",
                "message": f"{len(inputs_without_label)} 个表单元素缺少关联的 <label> 或 aria-label",
                "fix": "使用 <label for=\"id\"> 或 aria-label / aria-labelledby 关联表单控件",
                "wcag": "WCAG 2.1 SC 1.3.1 Info and Relationships (Level A)",
            })
            score -= min(len(inputs_without_label) * 5, 20)
        elif input_tags:
            passes.append("所有表单元素均有正确的 label 关联")

        # 3. Color contrast check (extract CSS variables and calculate)
        color_contrast_issues: list[dict[str, str]] = []
        if css_content:
            # Extract CSS custom properties (color values)
            color_vars: dict[str, str] = {}
            var_pattern = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*(#[0-9a-fA-F]{3,8}|rgb[a]?\([^)]+\))")
            for match in var_pattern.finditer(css_content):
                color_vars[match.group(1)] = match.group(2)

            # Check text/background contrast pairs
            text_keys = [k for k in color_vars if any(t in k.lower() for t in ["text", "foreground", "fg"])]
            bg_keys = [k for k in color_vars if any(t in k.lower() for t in ["background", "bg", "surface"])]

            for text_key in text_keys:
                for bg_key in bg_keys:
                    text_color = color_vars[text_key]
                    bg_color = color_vars[bg_key]
                    contrast = self._calculate_contrast_ratio(text_color, bg_color)
                    if contrast is not None and contrast < 4.5:
                        color_contrast_issues.append({
                            "text_var": f"--{text_key}",
                            "bg_var": f"--{bg_key}",
                            "text_color": text_color,
                            "bg_color": bg_color,
                            "ratio": f"{contrast:.2f}:1",
                            "required": "4.5:1 (WCAG AA)",
                        })

            if color_contrast_issues:
                issues.append({
                    "severity": "high",
                    "message": f"{len(color_contrast_issues)} 对文字/背景色对比度不满足 WCAG AA (4.5:1)",
                    "fix": "调整颜色变量确保文字与背景的对比度至少为 4.5:1（大文字至少 3:1）",
                    "wcag": "WCAG 2.1 SC 1.4.3 Contrast (Minimum) (Level AA)",
                })
                score -= min(len(color_contrast_issues) * 5, 20)
            elif color_vars:
                passes.append("CSS 变量中的颜色对比度满足 WCAG AA 标准")

        # 4. Check for skip navigation link
        has_skip_nav = bool(re.search(
            r'<a\b[^>]*href\s*=\s*["\']#(?:main|content|maincontent)["\'][^>]*>',
            html_content, re.IGNORECASE,
        ))
        skip_nav_class = bool(re.search(
            r'(?:skip[-_]?nav|skip[-_]?to[-_]?(?:main|content))',
            html_content, re.IGNORECASE,
        ))

        if not has_skip_nav and not skip_nav_class:
            issues.append({
                "severity": "medium",
                "message": "未发现 Skip Navigation 链接",
                "fix": "在页面顶部添加 <a href=\"#main\" class=\"skip-nav\">跳到主内容</a>",
                "wcag": "WCAG 2.1 SC 2.4.1 Bypass Blocks (Level A)",
            })
            score -= 10
        else:
            passes.append("页面包含 Skip Navigation 链接")

        # 5. Check ARIA landmarks
        has_main = bool(re.search(r'<main\b|role\s*=\s*["\']main["\']', html_content, re.IGNORECASE))
        has_nav = bool(re.search(r'<nav\b|role\s*=\s*["\']navigation["\']', html_content, re.IGNORECASE))
        has_banner = bool(re.search(r'<header\b|role\s*=\s*["\']banner["\']', html_content, re.IGNORECASE))

        landmark_coverage = sum([has_main, has_nav, has_banner])
        if not has_main:
            issues.append({
                "severity": "medium",
                "message": "缺少 <main> 元素或 role=\"main\" 标记",
                "fix": "使用 <main> 语义元素包裹页面主要内容区域",
                "wcag": "WCAG 2.1 SC 1.3.1 Info and Relationships (Level A)",
            })
            score -= 8

        # 6. Check for focus styles
        has_focus_visible = bool(re.search(r":focus-visible", css_content or ""))
        has_focus = bool(re.search(r":focus(?!-)", css_content or ""))
        has_outline_none = bool(re.search(r"outline\s*:\s*(?:none|0)", css_content or ""))

        if has_outline_none and not has_focus_visible and not has_focus:
            issues.append({
                "severity": "high",
                "message": "移除了 outline 但未提供替代的 focus 样式",
                "fix": "如果移除 outline，必须使用 :focus-visible 提供替代的焦点指示器",
                "wcag": "WCAG 2.1 SC 2.4.7 Focus Visible (Level AA)",
            })
            score -= 15

        if has_focus_visible:
            passes.append("使用了 :focus-visible 伪类提供键盘焦点样式")

        # 7. Check for reduced motion preference
        has_reduced_motion = bool(re.search(
            r"prefers-reduced-motion", css_content or "",
        ))
        if not has_reduced_motion and css_content and (
            "animation" in css_content or "transition" in css_content
        ):
            issues.append({
                "severity": "medium",
                "message": "页面包含动画/过渡效果但未处理 prefers-reduced-motion 偏好",
                "fix": "添加 @media (prefers-reduced-motion: reduce) { * { animation-duration: 0s; transition-duration: 0s; } }",
                "wcag": "WCAG 2.1 SC 2.3.3 Animation from Interactions (Level AAA)",
            })
            score -= 8
        elif has_reduced_motion:
            passes.append("尊重 prefers-reduced-motion 用户偏好设置")

        # 8. Check heading hierarchy
        headings = re.findall(r"<h([1-6])\b", html_content, re.IGNORECASE)
        heading_levels = [int(h) for h in headings]
        heading_issues: list[str] = []

        if heading_levels:
            if heading_levels[0] != 1:
                heading_issues.append(f"页面首个标题是 h{heading_levels[0]}，应该从 h1 开始")
            for i in range(1, len(heading_levels)):
                if heading_levels[i] > heading_levels[i - 1] + 1:
                    heading_issues.append(
                        f"标题层级从 h{heading_levels[i-1]} 跳到 h{heading_levels[i]}，跳过了中间层级"
                    )
                    break

        if heading_issues:
            issues.append({
                "severity": "medium",
                "message": "标题层级结构不正确：" + "；".join(heading_issues),
                "fix": "确保标题层级从 h1 开始且不跳级（h1 > h2 > h3 ...）",
                "wcag": "WCAG 2.1 SC 1.3.1 Info and Relationships (Level A)",
            })
            score -= 8

        # 9. Check lang attribute
        has_lang = bool(re.search(r'<html\b[^>]*\blang\s*=\s*["\'][^"\']+["\']', html_content, re.IGNORECASE))
        if not has_lang:
            issues.append({
                "severity": "medium",
                "message": "HTML 标签缺少 lang 属性",
                "fix": '在 <html> 标签添加 lang 属性，如 <html lang="zh-CN">',
                "wcag": "WCAG 2.1 SC 3.1.1 Language of Page (Level A)",
            })
            score -= 5
        else:
            passes.append("HTML 标签包含 lang 属性")

        # 10. Check for button accessibility
        buttons_without_text = re.findall(
            r"<button\b[^>]*>\s*<(?:img|svg|i|span)\b[^>]*/?>\s*</button>",
            html_content, re.IGNORECASE,
        )
        icon_buttons_without_label = [
            btn for btn in buttons_without_text
            if "aria-label" not in btn.lower() and "title" not in btn.lower()
        ]
        if icon_buttons_without_label:
            issues.append({
                "severity": "medium",
                "message": f"{len(icon_buttons_without_label)} 个图标按钮缺少 aria-label 或 title",
                "fix": "为仅包含图标的按钮添加 aria-label 描述其功能",
                "wcag": "WCAG 2.1 SC 4.1.2 Name, Role, Value (Level A)",
            })
            score -= min(len(icon_buttons_without_label) * 3, 10)

        score = max(0, min(100, score))

        return {
            "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
            "wcag_level": "AA" if score >= 75 else "A" if score >= 50 else "Fail",
            "images": {
                "total": len(img_tags),
                "with_alt": imgs_with_alt,
                "with_empty_alt": imgs_with_empty_alt,
                "missing_alt": imgs_without_alt[:10],
            },
            "forms": {
                "total_inputs": len(input_tags),
                "properly_labelled": len(aria_labelled_ids),
                "missing_labels": inputs_without_label[:10],
            },
            "color_contrast": {
                "issues_found": len(color_contrast_issues),
                "details": color_contrast_issues[:5],
            },
            "navigation": {
                "has_skip_nav": has_skip_nav or skip_nav_class,
                "landmarks": {
                    "main": has_main,
                    "nav": has_nav,
                    "banner": has_banner,
                    "coverage": f"{landmark_coverage}/3",
                },
            },
            "focus": {
                "has_focus_visible": has_focus_visible,
                "has_focus_styles": has_focus,
                "outline_removed": has_outline_none,
            },
            "motion": {
                "respects_reduced_motion": has_reduced_motion,
            },
            "heading_hierarchy": {
                "levels_found": heading_levels,
                "issues": heading_issues,
            },
            "has_lang_attribute": has_lang,
            "issues": issues,
            "passes": passes,
        }

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float | None:
        """
        计算两个颜色之间的对比度比率（WCAG 2.1 算法）。

        Args:
            color1: 第一个颜色值（#hex 或 rgb()/rgba()）
            color2: 第二个颜色值（#hex 或 rgb()/rgba()）

        Returns:
            对比度比率，如果无法解析颜色则返回 None
        """
        import re

        def hex_to_rgb(hex_str: str) -> tuple[int, int, int] | None:
            hex_str = hex_str.lstrip("#")
            if len(hex_str) == 3:
                hex_str = "".join(c * 2 for c in hex_str)
            if len(hex_str) == 6:
                return (
                    int(hex_str[0:2], 16),
                    int(hex_str[2:4], 16),
                    int(hex_str[4:6], 16),
                )
            if len(hex_str) == 8:
                return (
                    int(hex_str[0:2], 16),
                    int(hex_str[2:4], 16),
                    int(hex_str[4:6], 16),
                )
            return None

        def parse_rgb(color_str: str) -> tuple[int, int, int] | None:
            match = re.match(
                r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)",
                color_str,
            )
            if match:
                return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
            return None

        def parse_color(color_str: str) -> tuple[int, int, int] | None:
            color_str = color_str.strip()
            if color_str.startswith("#"):
                return hex_to_rgb(color_str)
            if color_str.startswith("rgb"):
                return parse_rgb(color_str)
            return None

        def relative_luminance(r: int, g: int, b: int) -> float:
            def srgb(c: int) -> float:
                s = c / 255.0
                return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
            return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)

        rgb1 = parse_color(color1)
        rgb2 = parse_color(color2)
        if rgb1 is None or rgb2 is None:
            return None

        l1 = relative_luminance(*rgb1)
        l2 = relative_luminance(*rgb2)
        lighter = max(l1, l2)
        darker = min(l1, l2)

        return round((lighter + 0.05) / (darker + 0.05), 2)

    # ------------------------------------------------------------------
    # Design Token Consistency Check
    # ------------------------------------------------------------------

    def _check_token_consistency(
        self,
        css_content: str,
        source_files: list[str] | None = None,
        tailwind_config: str = "",
    ) -> dict[str, Any]:
        """
        检查设计 Token 一致性：从 CSS 变量和 Tailwind 配置中提取 Token 定义，
        然后检查源代码中是否存在未使用 Token 的硬编码值。

        Args:
            css_content: CSS 文件内容（包含 :root 变量定义）
            source_files: 源文件内容列表（HTML/JSX/TSX/Vue 等）
            tailwind_config: tailwind.config.js/ts 文件内容（可选）

        Returns:
            包含 Token 一致性分析结果的字典
        """
        import re

        source_files = source_files or []
        issues: list[dict[str, str]] = []
        suggestions: list[str] = []

        # 1. Extract CSS custom property tokens
        css_tokens: dict[str, dict[str, str]] = {}
        var_pattern = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);")
        for match in var_pattern.finditer(css_content):
            name = match.group(1).strip()
            value = match.group(2).strip()
            category = self._categorize_token(name, value)
            css_tokens[name] = {"value": value, "category": category}

        # Categorize tokens
        color_tokens = {k: v for k, v in css_tokens.items() if v["category"] == "color"}
        spacing_tokens = {k: v for k, v in css_tokens.items() if v["category"] == "spacing"}
        typography_tokens = {k: v for k, v in css_tokens.items() if v["category"] == "typography"}
        radius_tokens = {k: v for k, v in css_tokens.items() if v["category"] == "radius"}
        shadow_tokens = {k: v for k, v in css_tokens.items() if v["category"] == "shadow"}
        other_tokens = {k: v for k, v in css_tokens.items() if v["category"] == "other"}

        # 2. Extract Tailwind config tokens
        tailwind_tokens: dict[str, list[str]] = {
            "colors": [],
            "spacing": [],
            "fontSize": [],
            "borderRadius": [],
            "boxShadow": [],
        }
        if tailwind_config:
            for category in tailwind_tokens:
                # Simple extraction from JS/TS config
                cat_pattern = re.compile(
                    rf"{category}\s*:\s*\{{([^}}]+)\}}", re.DOTALL,
                )
                cat_match = cat_pattern.search(tailwind_config)
                if cat_match:
                    block = cat_match.group(1)
                    keys = re.findall(r"['\"]?([a-zA-Z0-9_-]+)['\"]?\s*:", block)
                    tailwind_tokens[category] = keys

        # 3. Check for hardcoded values in source files
        hardcoded_colors: list[dict[str, str]] = []
        hardcoded_fonts: list[dict[str, str]] = []
        hardcoded_spacing: list[dict[str, str]] = []
        hardcoded_radius: list[dict[str, str]] = []

        all_source = "\n".join(source_files)

        if all_source:
            # Check for inline hex colors not using tokens
            inline_hex = re.findall(r'(?:color|background|border|fill|stroke)\s*[:=]\s*["\']?(#[0-9a-fA-F]{3,8})', all_source)
            token_color_values = {v["value"].lower() for v in color_tokens.values()}
            for hex_val in inline_hex:
                if hex_val.lower() not in token_color_values:
                    hardcoded_colors.append({
                        "value": hex_val,
                        "suggestion": self._find_closest_token(hex_val, color_tokens),
                    })

            # Check for inline font-family not using tokens
            inline_fonts = re.findall(
                r'font-?[Ff]amily\s*[:=]\s*["\']([^"\']+)', all_source,
            )
            for font in inline_fonts:
                if "var(--" not in font:
                    hardcoded_fonts.append({"value": font})

            # Check for inline pixel spacing not using tokens
            inline_spacing = re.findall(
                r'(?:margin|padding|gap)\s*[:=]\s*["\']?(\d+px)', all_source,
            )
            for sp in inline_spacing:
                hardcoded_spacing.append({"value": sp})

            # Check for inline border-radius
            inline_radius = re.findall(
                r'border-?[Rr]adius\s*[:=]\s*["\']?(\d+px)', all_source,
            )
            for rd in inline_radius:
                hardcoded_radius.append({"value": rd})

        if hardcoded_colors:
            issues.append({
                "severity": "medium",
                "message": f"发现 {len(hardcoded_colors)} 个硬编码颜色值未使用 Token",
                "fix": "将硬编码颜色替换为 var(--token-name) 或 Tailwind 语义类",
            })
        if hardcoded_fonts:
            issues.append({
                "severity": "medium",
                "message": f"发现 {len(hardcoded_fonts)} 个硬编码字体声明未使用 Token",
                "fix": "将字体声明统一使用 var(--font-heading) / var(--font-body) Token",
            })
        if hardcoded_spacing and spacing_tokens:
            issues.append({
                "severity": "low",
                "message": f"发现 {len(hardcoded_spacing)} 个硬编码间距值，建议使用 Token 或 Tailwind 预设类",
                "fix": "定义间距 Token 并统一引用",
            })

        # 4. Token coverage analysis
        total_token_count = len(css_tokens)
        total_hardcoded = len(hardcoded_colors) + len(hardcoded_fonts) + len(hardcoded_spacing) + len(hardcoded_radius)
        token_usage_count = len(re.findall(r"var\(--[a-zA-Z0-9_-]+\)", all_source)) if all_source else 0
        coverage_ratio = round(
            token_usage_count / max(token_usage_count + total_hardcoded, 1), 2,
        )

        # 5. Check token naming convention
        naming_issues: list[str] = []
        for token_name in css_tokens:
            # Check for semantic naming
            if re.match(r"^(color|bg|text|border|font|spacing|radius|shadow)-", token_name):
                continue  # Good semantic prefix
            if re.match(r"^(primary|secondary|accent|muted|surface|foreground|background|card|destructive|ring|input|chart)-?", token_name):
                continue  # Good semantic name
            if re.match(r"^(--)?[a-z]+-\d+$", token_name):
                naming_issues.append(f"--{token_name} 使用了数字后缀命名，建议使用语义化名称")

        if naming_issues:
            suggestions.append(
                f"发现 {len(naming_issues)} 个 Token 使用了非语义化命名，"
                "建议使用如 --color-primary、--spacing-lg 等语义前缀"
            )

        # 6. Check required token categories
        required_categories = {
            "color": "颜色 Token（primary/secondary/accent/background/text）",
            "typography": "字体 Token（font-family/font-size/font-weight/line-height）",
            "spacing": "间距 Token（spacing/gap/padding/margin 系列）",
            "radius": "圆角 Token（border-radius 系列）",
            "shadow": "阴影 Token（box-shadow 系列）",
        }
        missing_categories: list[str] = []
        for cat, desc in required_categories.items():
            count = len([v for v in css_tokens.values() if v["category"] == cat])
            if count == 0:
                missing_categories.append(desc)

        if missing_categories:
            issues.append({
                "severity": "medium",
                "message": f"缺少以下类别的 Token 定义：{'、'.join(missing_categories)}",
                "fix": "补充完整的设计 Token 体系，确保颜色、字体、间距、圆角、阴影全部覆盖",
            })

        score = 100
        score -= min(len(hardcoded_colors) * 2, 20)
        score -= min(len(hardcoded_fonts) * 3, 15)
        score -= min(len(missing_categories) * 8, 24)
        score -= min(len(naming_issues) * 1, 10)
        score = max(0, min(100, score))

        return {
            "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
            "token_inventory": {
                "total": total_token_count,
                "by_category": {
                    "color": len(color_tokens),
                    "typography": len(typography_tokens),
                    "spacing": len(spacing_tokens),
                    "radius": len(radius_tokens),
                    "shadow": len(shadow_tokens),
                    "other": len(other_tokens),
                },
            },
            "tailwind_tokens": {k: len(v) for k, v in tailwind_tokens.items() if v},
            "coverage": {
                "token_usage_count": token_usage_count,
                "hardcoded_value_count": total_hardcoded,
                "coverage_ratio": coverage_ratio,
            },
            "hardcoded_values": {
                "colors": hardcoded_colors[:10],
                "fonts": hardcoded_fonts[:10],
                "spacing": hardcoded_spacing[:10],
                "radius": hardcoded_radius[:10],
            },
            "missing_categories": missing_categories,
            "naming_issues": naming_issues[:10],
            "issues": issues,
            "suggestions": suggestions,
        }

    def _categorize_token(self, name: str, value: str) -> str:
        """根据 Token 名称和值推断其类别"""
        name_lower = name.lower()
        value_lower = value.lower().strip()

        # Color detection
        if any(kw in name_lower for kw in [
            "color", "primary", "secondary", "accent", "background", "bg",
            "foreground", "fg", "text", "muted", "border", "surface", "card",
            "destructive", "ring", "input", "chart", "stroke", "fill",
        ]):
            return "color"
        if value_lower.startswith("#") or value_lower.startswith("rgb") or value_lower.startswith("hsl"):
            return "color"

        # Typography detection
        if any(kw in name_lower for kw in ["font", "text-size", "line-height", "letter-spacing", "heading", "body"]):
            return "typography"

        # Spacing detection
        if any(kw in name_lower for kw in ["spacing", "gap", "padding", "margin", "space", "inset"]):
            return "spacing"

        # Radius detection
        if any(kw in name_lower for kw in ["radius", "rounded", "corner"]):
            return "radius"

        # Shadow detection
        if any(kw in name_lower for kw in ["shadow", "elevation"]):
            return "shadow"

        return "other"

    def _find_closest_token(self, hex_color: str, color_tokens: dict[str, dict[str, str]]) -> str:
        """查找最接近的颜色 Token"""
        hex_color = hex_color.lstrip("#").lower()
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        if len(hex_color) != 6:
            return "(无法匹配)"

        r1, g1, b1 = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        best_name = ""
        best_distance = float("inf")

        for name, info in color_tokens.items():
            val = info["value"].lstrip("#").lower()
            if len(val) == 3:
                val = "".join(c * 2 for c in val)
            if len(val) != 6:
                continue
            r2, g2, b2 = int(val[:2], 16), int(val[2:4], 16), int(val[4:6], 16)
            distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
            if distance < best_distance:
                best_distance = distance
                best_name = name

        if best_name and best_distance < 80:
            return f"建议使用 var(--{best_name})"
        return "(无匹配 Token，请新建)"
