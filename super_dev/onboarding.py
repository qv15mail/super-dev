"""
首次使用引导 — 最多显示 4 次，完成后不再提示。

在用户首次运行 ``super-dev``（无子命令）时显示 3 步快速开始，
帮助新用户快速进入工作流。引导状态持久化在 ``.super-dev/onboarding.json``。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from rich.panel import Panel

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class OnboardingGuide:
    """首次使用引导，最多显示 MAX_SHOW_COUNT 次。"""

    MAX_SHOW_COUNT = 4
    _STATE_FILE = ".super-dev/onboarding.json"

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def should_show(self, project_dir: Path) -> bool:
        """判断是否需要显示引导。"""
        state = self._load_state(project_dir)
        if state.get("completed"):
            return False
        if state.get("seen_count", 0) >= self.MAX_SHOW_COUNT:
            return False
        return True

    def show(self, console: Any) -> None:
        """显示 3 步快速引导。"""
        steps = (
            "1. super-dev init <项目名>     — 初始化项目配置\n"
            "2. super-dev detect --auto     — 检测并配置宿主 AI IDE\n"
            "3. 在宿主中输入: /super-dev <需求>  — 启动开发 pipeline"
        )

        if RICH_AVAILABLE and hasattr(console, "print"):
            panel = Panel(
                steps,
                title="[bold cyan]Quick Start[/bold cyan]",
                border_style="cyan",
                expand=False,
            )
            console.print(panel)
            console.print(
                "[dim]提示: 完成以上步骤后此引导将自动消失，"
                "或运行 super-dev --skip-onboarding 跳过[/dim]"
            )
        else:
            print("=== Quick Start ===")  # noqa: T201
            print(steps)  # noqa: T201
            print("提示: 完成以上步骤后此引导将自动消失")  # noqa: T201

    def mark_seen(self, project_dir: Path) -> None:
        """递增已展示计数。"""
        state = self._load_state(project_dir)
        state["seen_count"] = state.get("seen_count", 0) + 1
        self._save_state(project_dir, state)

    def mark_completed(self, project_dir: Path) -> None:
        """标记引导已完成，后续不再显示。"""
        state = self._load_state(project_dir)
        state["completed"] = True
        self._save_state(project_dir, state)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _state_path(self, project_dir: Path) -> Path:
        return project_dir / self._STATE_FILE

    def _load_state(self, project_dir: Path) -> dict:
        path = self._state_path(project_dir)
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_state(self, project_dir: Path, state: dict) -> None:
        path = self._state_path(project_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
