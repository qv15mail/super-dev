from __future__ import annotations

from typing import Any

SEEAI_SMOKE_SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "id": "system_retro_shell",
        "label": "复杂系统复刻切片",
        "prompt": "复刻一个经典桌面系统，但只做半小时内最有记忆点的演示切片。",
        "expected_slice": "1 个高辨识主界面 + 1 到 2 个真实可交互核心动作 + 1 个结束态/彩蛋。",
        "must_prove": (
            "宿主会主动压缩范围，而不是按完整系统做。",
            "12 分钟内先跑出可见桌面或主界面。",
            "开始菜单/窗口/主交互里至少有 1 到 2 个真实可点动作。",
        ),
    },
    {
        "id": "showcase_landing",
        "label": "强视觉官网展示",
        "prompt": "做一个比赛级官网或展示页，要求首屏抓眼、30 秒内可讲完主价值。",
        "expected_slice": "1 个强 Hero + 1 个亮点区 + 1 个 CTA/结果区，不追求多页。",
        "must_prove": (
            "宿主先锁设计包和题型，再开做。",
            "首屏、亮点区、CTA 都真实可见可滚动。",
            "文案和主视觉不是默认模板感。",
        ),
    },
    {
        "id": "mini_game_loop",
        "label": "小游戏主循环",
        "prompt": "做一个 30 分钟内能完整玩一局的小游戏。",
        "expected_slice": "开始态 + 主循环 + 结算态 + 再来一次入口。",
        "must_prove": (
            "宿主不会一开始就上重框架或复杂地图系统。",
            "12 分钟内至少能进入一局可玩的主循环。",
            "积分/胜负/结算其中至少一项是真实触发的。",
        ),
    },
    {
        "id": "tool_result_path",
        "label": "工具型结果闭环",
        "prompt": "做一个高价值工具 demo，要求输入到结果的主流程清晰且可演示。",
        "expected_slice": "输入页 + 结果页 + 1 个可信结果表现，不强求完整后端。",
        "must_prove": (
            "宿主会优先保住输入到结果的主路径。",
            "结果页是真实生成或真实渲染的，不是空占位。",
            "外部依赖起不来时会主动改用 mock 或本地数据。",
        ),
    },
)

SEEAI_ACCEPTANCE_GATES: tuple[str, ...] = (
    "复杂题是否被主动压缩成可讲解的 demo slice，而不是照原题全量展开。",
    "12 分钟内是否出现第一个可见、可点击、可截图的运行界面。",
    "保留下来的模块是否都真实启动、真实渲染、真实进入主演示路径。",
    "初始化或构建失败时，是否立即切到轻量回退栈而不是死磕。",
    "最终作品是否能在 30 秒到 60 秒内完整演示一遍主路径。",
)


def get_seeai_smoke_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "label": item["label"],
            "prompt": item["prompt"],
            "expected_slice": item["expected_slice"],
            "must_prove": list(item["must_prove"]),
        }
        for item in SEEAI_SMOKE_SCENARIOS
    ]


def get_seeai_acceptance_gates() -> list[str]:
    return list(SEEAI_ACCEPTANCE_GATES)


def build_seeai_smoke_suite(trigger_command: str) -> list[dict[str, Any]]:
    suite: list[dict[str, Any]] = []
    for item in SEEAI_SMOKE_SCENARIOS:
        suite.append(
            {
                "id": item["id"],
                "label": item["label"],
                "trigger": (
                    f'{trigger_command} "{item["prompt"]}"'
                    if trigger_command.startswith(("/", "$"))
                    else f"{trigger_command} {item['prompt']}"
                ),
                "prompt": item["prompt"],
                "expected_slice": item["expected_slice"],
                "must_prove": list(item["must_prove"]),
            }
        )
    return suite


def build_seeai_evidence_template() -> dict[str, Any]:
    return {
        "first_response": {
            "required": ["作品类型", "评委 wow 点", "P0 主路径", "主动放弃项"],
            "note": "首轮必须明确压缩后的 demo slice，而不是直接开编码。",
        },
        "runtime_checkpoint": {
            "required": [
                "12 分钟内首个可见界面",
                "主路径首个可点击动作",
                "至少一个真实启动模块",
            ],
            "note": "至少要证明作品不是停留在初始化或静态壳子阶段。",
        },
        "fallback_decision": {
            "required": ["失败点", "回退栈", "为什么这样降级"],
            "note": "如果初始化或构建失败，必须记录回退选择，而不是空说修好了。",
        },
        "demo_path": {
            "required": ["30-60 秒主演示路径", "结果页/结束态", "可截图 wow 点"],
            "note": "最后必须证明评委能在短时间内完整看完一遍主流程。",
        },
    }


__all__ = [
    "SEEAI_ACCEPTANCE_GATES",
    "SEEAI_SMOKE_SCENARIOS",
    "build_seeai_smoke_suite",
    "build_seeai_evidence_template",
    "get_seeai_acceptance_gates",
    "get_seeai_smoke_scenarios",
]
