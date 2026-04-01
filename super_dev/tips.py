"""上下文感知提示系统 — 在合适的时机给用户有用的提示。"""

from __future__ import annotations

import json
import random
from pathlib import Path

# 提示库 — 按触发条件分组
TIPS: list[dict[str, str]] = [
    # 编码前
    {
        "trigger": "pre_code",
        "text": "编码前运行 super-dev enforce validate 检查约束状态",
    },
    {
        "trigger": "pre_code",
        "text": "用 super-dev generate components 生成组件脚手架，避免从零开始",
    },
    {
        "trigger": "pre_code",
        "text": "编码前先读 package.json 确认框架版本，避免用错 API",
    },
    # 编码中
    {
        "trigger": "coding",
        "text": "每完成一个功能后运行 npm run build 确认无报错",
    },
    {
        "trigger": "coding",
        "text": "前端 fetch URL 要和后端 route 完全一致，建议用常量定义 API 路径",
    },
    {
        "trigger": "coding",
        "text": "图标只能用 Lucide/Heroicons/Tabler，不要用 emoji",
    },
    # 审查
    {
        "trigger": "review",
        "text": "用 super-dev review --state ui 做 UI 审查，不要跳过",
    },
    {
        "trigger": "review",
        "text": "用 super-dev quality 运行质量门禁检查",
    },
    # 交付
    {
        "trigger": "delivery",
        "text": "运行 super-dev release proof-pack 生成完整交付证据",
    },
    {
        "trigger": "delivery",
        "text": "运行 super-dev release readiness 确认发布就绪",
    },
    # 通用
    {
        "trigger": "general",
        "text": "用 super-dev status 查看当前 pipeline 状态",
    },
    {
        "trigger": "general",
        "text": "用 super-dev doctor --fix 自动修复安装问题",
    },
    {
        "trigger": "general",
        "text": "用 super-dev memory list 查看项目积累的记忆",
    },
    {
        "trigger": "general",
        "text": "用 super-dev completion bash 生成 shell 自动补全",
    },
    {
        "trigger": "general",
        "text": "在 .super-dev/reminders/ 放 .md 文件可以自定义约束",
    },
    {
        "trigger": "general",
        "text": "用 super-dev experts list 查看所有可用专家",
    },
]


def get_tip(trigger: str = "general") -> str | None:
    """获取一条随机提示。"""
    matching = [t for t in TIPS if t["trigger"] == trigger]
    if not matching:
        matching = [t for t in TIPS if t["trigger"] == "general"]
    if not matching:
        return None
    return random.choice(matching)["text"]  # noqa: S311


def get_tip_for_phase(phase: str) -> str | None:
    """根据当前 pipeline 阶段获取提示。"""
    phase_map = {
        "research": "pre_code",
        "prd": "pre_code",
        "architecture": "pre_code",
        "uiux": "pre_code",
        "spec": "pre_code",
        "frontend": "coding",
        "backend": "coding",
        "quality": "review",
        "delivery": "delivery",
    }
    trigger = phase_map.get(phase, "general")
    return get_tip(trigger)


def should_show_tip(project_dir: Path) -> bool:
    """是否应该显示提示（避免过于频繁）。"""
    state_file = project_dir / ".super-dev" / ".tips-state.json"
    if not state_file.exists():
        return True
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        shown_count = state.get("shown_count", 0)
        # 每 3 次操作显示一次提示
        return shown_count % 3 == 0
    except Exception:
        return True


def mark_tip_shown(project_dir: Path) -> None:
    """记录提示已显示。"""
    state_file = project_dir / ".super-dev" / ".tips-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        state = {}
        if state_file.exists():
            state = json.loads(state_file.read_text(encoding="utf-8"))
        state["shown_count"] = state.get("shown_count", 0) + 1
        state_file.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass
