from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SEEAI_FIRST_RESPONSE_TEMPLATE: tuple[str, ...] = (
    "作品类型",
    "评委 wow 点",
    "P0 主路径",
    "主动放弃项",
    "关键假设",
)

SEEAI_TIMEBOX_BREAKDOWN: tuple[str, ...] = (
    "0-4 分钟：fast research",
    "4-8 分钟：compact 文档",
    "8-10 分钟：docs confirm",
    "10-12 分钟：compact spec",
    "12-27 分钟：full-stack sprint",
    "27-30 分钟：polish/handoff",
)

SEEAI_SCOPE_RULE = "先保主路径，再做 wow 点，最后才补额外工程深度。"
SEEAI_DEGRADE_RULE = "后端或外部集成拖慢节奏时，优先 mock / 本地数据 / 高保真演示流。"

SEEAI_ARCHETYPE_DETECTION_HINTS: tuple[str, ...] = (
    "品牌、官网、落地页、活动宣传、首屏 -> 官网类",
    "玩法、得分、胜负、闯关、点击反馈 -> 小游戏类",
    "生成、分析、查询、输入输出、结果页、效率提升 -> 工具类",
)

SEEAI_COMPACT_DOC_SECTIONS: dict[str, tuple[str, ...]] = {
    "research": ("题目理解", "参考风格", "Wow 点", "主动放弃项"),
    "prd": ("作品目标", "P0 主路径", "P1 Wow 点", "P2 可选项", "非目标"),
    "architecture": ("主循环", "技术栈", "数据流", "最小后端", "降级方案"),
    "uiux": ("视觉方向", "首屏/主界面", "关键交互", "动效重点", "设计 Token"),
    "spec": ("P0", "P1", "Polish"),
}

SEEAI_QUALITY_FLOOR: tuple[str, ...] = (
    "3 秒内必须让评委看懂主题和亮点，首屏不能有普通模板感。",
    "30 秒内必须能完整走完一条主演示路径，不允许关键步骤断掉。",
    "至少保住一个 wow 点，而且 wow 点必须真实可见，不是只写在文案里。",
    "时间不够时优先删功能，不要删完成度、动效记忆点和演示闭环。",
    "必须能在比赛现场直接讲解与演示，结果页或结束态要有完成感。",
)

SEEAI_JUDGE_CHECKLIST: tuple[str, ...] = (
    "3 秒第一印象够不够强，是否一眼看懂主题。",
    "30 秒主演示路径是否闭环，评委不用猜下一步。",
    "wow 点是否真实出现，而不是停留在计划里。",
    "是否还残留默认组件、默认配色、占位文案或丑的细节。",
    "还能不能再砍一个次要功能，换更强的完成度和视觉统一性。",
)

SEEAI_EXECUTION_GUARDRAILS: tuple[str, ...] = (
    "先选最稳的已知技术栈，不为了炫技引入初始化重、配置重、调试重的方案。",
    "默认优先零配置或成熟脚手架，依赖数量越少越好，能不用就不用。",
    "12 分钟内必须跑出第一个可见、可点击、可截图的运行界面，不能一直停留在初始化。",
    "先打通主路径，再补 wow 点；主路径没跑通前，不做长尾功能和高级工程化。",
    "外部 API、数据库、鉴权、支付、上传不是评审主轴时，一律降级为 mock 或本地状态。",
)

SEEAI_FAILURE_PROTOCOL: tuple[str, ...] = (
    "初始化失败一次后，立刻切到更轻的备选栈，不在原栈上死磕。",
    "如果构建链卡住，优先回退到 Vite、CDN、Canvas 或静态数据方案，先把作品跑起来。",
    "任何功能连续两次调试不过，就立刻降级复杂度，保住演示闭环。",
    "最后 5 分钟只允许修阻断演示的问题，不再新增功能。",
)

SEEAI_MODULE_TRUTH_RULES: tuple[str, ...] = (
    "比赛模式默认只保留 1 到 3 个真正参与演示的核心模块，模块越少越容易做实。",
    "每个保留下来的模块都必须真实启动、真实渲染、真实可交互，并进入主演示路径。",
    "禁止保留只有壳子、点不开、没有数据、没有调用链的假模块或占位模块。",
    "20 分钟前仍未接入主路径的模块，默认降级或删除，不允许拖到最后阶段。",
    "结果页、结束态、弹窗、排行榜、设置页这类附加模块，只有真实服务主路径时才保留。",
)

SEEAI_COMPLEXITY_REDUCTION_RULES: tuple[str, ...] = (
    "如果需求像完整操作系统、完整社交平台、完整电商、完整游戏宇宙，先压成 1 个可讲解的主演示切片，不做全量复刻。",
    "如果用户要复刻老系统或大产品，先做最有记忆点的 1 个主界面 + 1 到 2 个真实可交互核心动作。",
    "如果需求天然跨前端、后端、数据、AI、多终端，先收成单终端单主流程，再决定是否补最小后端。",
    "比赛模式默认做 demo slice，不做 production scope；范围大的题必须主动写出放弃项。",
)

SEEAI_COMPLEXITY_PATTERNS: tuple[dict[str, str], ...] = (
    {
        "pattern": "系统/桌面/操作系统/IDE/复杂软件复刻",
        "rewrite_strategy": "压成一个高辨识主界面 + 1 到 2 个真实可交互核心动作 + 一个结束态或彩蛋。",
        "reason": "这类题初始化和状态管理过重，比赛里只能做最有记忆点的交互切片。",
    },
    {
        "pattern": "平台/社区/电商/门户型大产品",
        "rewrite_strategy": "压成一个最核心的用户主路径 + 一个互动亮点 + 一个可信结果页/详情页。",
        "reason": "这类题页面和角色太多，比赛里要优先保住最值钱的一段用户旅程。",
    },
    {
        "pattern": "3D/开放世界/重模拟/多系统游戏",
        "rewrite_strategy": "压成一个单场景 demo：进入场景、一个核心交互、一个结算/彩蛋/反馈高潮。",
        "reason": "这类题内容量和初始化成本都过大，必须收成单场景体验。",
    },
    {
        "pattern": "多角色协作/多 Agent/全链路企业系统",
        "rewrite_strategy": "压成一个主角色主流程，只保留 1 个关键协作点做演示，不做全角色全权限。",
        "reason": "角色、权限、后端链路过长，比赛里应该只展示最有说服力的主流程。",
    },
)

SEEAI_RESEARCH_PRIORITIES: tuple[str, ...] = (
    "先判断题型和复杂度，不先讨论实现细节。",
    "联网搜索优先找 3 类信息：视觉参考、交互参考、技术风险参考。",
    "研究结论必须收敛到 wow 点、P0 主路径、主动放弃项、回退栈四个决策。",
    "不做长竞品报告；研究的目标是帮助 10 分钟内定方向，而不是堆资料。",
)

SEEAI_SEARCH_QUERIES: tuple[str, ...] = (
    "同类题目的高完成度展示案例",
    "当前题型最容易打动评委的首屏/核心交互",
    "目标技术栈在 30 分钟内最常见的初始化或运行风险",
)


@dataclass(frozen=True, slots=True)
class SeeAIDesignPack:
    key: str
    label: str
    fit_for: str
    typography: str
    color_story: str
    motion_signature: str
    component_direction: str
    guardrail: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "label": self.label,
            "fit_for": self.fit_for,
            "typography": self.typography,
            "color_story": self.color_story,
            "motion_signature": self.motion_signature,
            "component_direction": self.component_direction,
            "guardrail": self.guardrail,
        }


@dataclass(frozen=True, slots=True)
class SeeAIArchetypePlaybook:
    key: str
    label: str
    default_stack: str
    sprint_plan: tuple[str, ...]
    focus: str
    preferred_design_packs: tuple[str, ...]
    hero_strategy: str
    wow_pattern: str
    runtime_checkpoint: str
    fallback_stack: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "default_stack": self.default_stack,
            "sprint_plan": list(self.sprint_plan),
            "focus": self.focus,
            "preferred_design_packs": list(self.preferred_design_packs),
            "hero_strategy": self.hero_strategy,
            "wow_pattern": self.wow_pattern,
            "runtime_checkpoint": self.runtime_checkpoint,
            "fallback_stack": self.fallback_stack,
        }


SEEAI_DESIGN_PACKS: tuple[SeeAIDesignPack, ...] = (
    SeeAIDesignPack(
        key="arena_neon",
        label="Arena Neon",
        fit_for="比赛海报气质、强科技展示页、海洋/竞技题、抓眼 Hero",
        typography="Rajdhani + Manrope，标题高对比、正文紧凑，避免默认系统字。",
        color_story="黑底 + 深海绿 + 电光青 + 少量热红点缀，不用紫粉渐变。",
        motion_signature="强入场光束、数字跳变、重点 hover glow，控制在 2-3 个记忆点。",
        component_direction="大 Hero、硬朗卡片、数据 HUD、发光 CTA、清晰分区层级。",
        guardrail="不要把整页都做成霓虹夜店风，只允许 Hero 和关键模块承担高强度效果。",
    ),
    SeeAIDesignPack(
        key="clean_product",
        label="Clean Product",
        fit_for="工具类、企业官网、效率产品、评委需要快速读懂价值的场景",
        typography="Space Grotesk + Inter，标题简洁，正文强调秩序和可读性。",
        color_story="暖白/浅灰底 + 碳黑文本 + 冷蓝或湖青强调，干净但不寡淡。",
        motion_signature="短位移动画、数字递进、结果区 reveal，少而准。",
        component_direction="强网格、留白、结果卡、对比模块、主 CTA 和证据信任区。",
        guardrail="不能退化成普通 SaaS 模板，必须保留一个高辨识 Hero 或结果展示。",
    ),
    SeeAIDesignPack(
        key="playful_motion",
        label="Playful Motion",
        fit_for="小游戏、互动作品、轻娱乐 demo、带反馈的趣味工具",
        typography="Sora + DM Sans，标题圆润，正文轻快，适合高反馈界面。",
        color_story="墨黑或奶油底 + 青绿/橙黄对比，强调可玩反馈，不用粉紫套路。",
        motion_signature="弹性反馈、粒子/积分飞字、胜负动画、按钮按压回弹。",
        component_direction="大按钮、状态 HUD、胜负态、反馈层和复玩入口要清楚。",
        guardrail="动效不能喧宾夺主，主循环必须先稳，再补趣味反馈。",
    ),
)

SEEAI_ARCHETYPE_PLAYBOOKS: tuple[SeeAIArchetypePlaybook, ...] = (
    SeeAIArchetypePlaybook(
        key="landing_page",
        label="官网类",
        default_stack="React/Vite 或 Next.js + Tailwind + Framer Motion",
        sprint_plan=("Hero/首屏", "亮点区/品牌叙事", "CTA/滚动动效", "最终 polish"),
        focus="主视觉、信息密度、滚动节奏、首屏转化",
        preferred_design_packs=("arena_neon", "clean_product"),
        hero_strategy="首屏必须在 3 秒内说清作品主题、价值和主亮点，优先做强主 KV。",
        wow_pattern="一个高记忆点 Hero + 一段能被截图传播的中段亮点模块。",
        runtime_checkpoint="12 分钟内至少跑出可滚动 Hero、一个亮点模块和 CTA。",
        fallback_stack="HTML + Tailwind CDN + GSAP，先做单页强展示，再决定是否补框架。",
    ),
    SeeAIArchetypePlaybook(
        key="mini_game",
        label="小游戏类",
        default_stack="HTML Canvas + Vanilla JS；复杂玩法再上 Phaser",
        sprint_plan=("主循环可玩", "积分/胜负反馈", "特效/音效", "复玩和 polish"),
        focus="玩法闭环、反馈感、积分胜负、再次游玩",
        preferred_design_packs=("playful_motion", "arena_neon"),
        hero_strategy="开场 1 步就能进入玩法，开始态和结束态都要能截图。",
        wow_pattern="一处强反馈动作或结算画面，让评委记住玩法节奏。",
        runtime_checkpoint="12 分钟内至少跑出开始态、主循环和结束态，能玩一局。",
        fallback_stack="HTML Canvas + Vanilla JS，先保住玩法闭环，再考虑 Phaser。",
    ),
    SeeAIArchetypePlaybook(
        key="tool",
        label="工具类",
        default_stack="React + Vite + Tailwind；必要时补最小 Express/Fastify 后端",
        sprint_plan=("输入页/主流程", "结果页", "分享/导出", "最终 polish"),
        focus="高价值主流程、输入输出清晰、结果页直观",
        preferred_design_packs=("clean_product", "arena_neon"),
        hero_strategy="首屏必须让评委立刻理解输入什么、得到什么、为什么值得看。",
        wow_pattern="一个可信且有质感的结果页，结果比输入页更需要打磨。",
        runtime_checkpoint="12 分钟内至少跑出输入页到结果页的一条闭环。",
        fallback_stack="React + Vite + 本地状态 + mock 数据，后端只在主轴依赖时才加。",
    ),
)


def get_seeai_design_packs() -> tuple[SeeAIDesignPack, ...]:
    return SEEAI_DESIGN_PACKS


def get_seeai_design_pack_map() -> dict[str, dict[str, str]]:
    return {pack.key: pack.to_dict() for pack in SEEAI_DESIGN_PACKS}


def get_seeai_archetype_playbooks() -> tuple[SeeAIArchetypePlaybook, ...]:
    return SEEAI_ARCHETYPE_PLAYBOOKS


def get_seeai_archetype_playbook_map() -> dict[str, dict[str, Any]]:
    return {playbook.key: playbook.to_dict() for playbook in SEEAI_ARCHETYPE_PLAYBOOKS}


__all__ = [
    "SEEAI_ARCHETYPE_DETECTION_HINTS",
    "SEEAI_ARCHETYPE_PLAYBOOKS",
    "SEEAI_COMPACT_DOC_SECTIONS",
    "SEEAI_COMPLEXITY_REDUCTION_RULES",
    "SEEAI_COMPLEXITY_PATTERNS",
    "SEEAI_DEGRADE_RULE",
    "SEEAI_DESIGN_PACKS",
    "SEEAI_EXECUTION_GUARDRAILS",
    "SEEAI_FAILURE_PROTOCOL",
    "SEEAI_FIRST_RESPONSE_TEMPLATE",
    "SEEAI_JUDGE_CHECKLIST",
    "SEEAI_MODULE_TRUTH_RULES",
    "SEEAI_QUALITY_FLOOR",
    "SEEAI_RESEARCH_PRIORITIES",
    "SEEAI_SEARCH_QUERIES",
    "SEEAI_SCOPE_RULE",
    "SEEAI_TIMEBOX_BREAKDOWN",
    "SeeAIArchetypePlaybook",
    "SeeAIDesignPack",
    "get_seeai_archetype_playbook_map",
    "get_seeai_archetype_playbooks",
    "get_seeai_design_pack_map",
    "get_seeai_design_packs",
]
