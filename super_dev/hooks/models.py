"""Hook 数据模型 — 定义 hook 事件、配置和执行结果。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HookType(str, Enum):
    """Hook 执行类型"""

    COMMAND = "command"  # Shell 命令
    PYTHON = "python"  # Python callable
    LOG = "log"  # 仅记录日志


@dataclass
class HookDefinition:
    """单个 hook 定义"""

    type: HookType = HookType.COMMAND
    command: str = ""  # Shell 命令或 Python 模块路径
    timeout: int = 30  # 超时秒数
    matcher: str = "*"  # 事件匹配模式 (阶段名 或 * 通配符)
    description: str = ""
    blocking: bool = True  # 是否阻塞 pipeline


@dataclass
class HookResult:
    """Hook 执行结果"""

    hook_name: str
    event: str
    success: bool
    output: str = ""
    error: str = ""
    duration_ms: float = 0.0
    blocked: bool = False  # 是否阻止了 pipeline 继续
    phase: str = ""
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize hook result for JSON/API/history logs."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HookResult:
        """Restore hook result from persisted JSON data."""
        return cls(
            hook_name=str(data.get("hook_name", "")),
            event=str(data.get("event", "")),
            success=bool(data.get("success", False)),
            output=str(data.get("output", "")),
            error=str(data.get("error", "")),
            duration_ms=float(data.get("duration_ms", 0.0) or 0.0),
            blocked=bool(data.get("blocked", False)),
            phase=str(data.get("phase", "")),
            source=str(data.get("source", "")),
            timestamp=str(data.get("timestamp", "")) or datetime.now(timezone.utc).isoformat(),
        )


@dataclass
class HookConfig:
    """Hook 配置（从 super-dev.yaml 的 hooks 段加载）

    YAML 格式:
    ```yaml
    hooks:
      PrePhase:
        - matcher: "drafting"
          type: command
          command: "python scripts/pre-draft.py"
          timeout: 30
      PostPhase:
        - matcher: "*"
          type: command
          command: "echo 'Phase completed'"
      PostQualityGate:
        - matcher: "*"
          type: log
          description: "Log quality gate results"
    ```
    """

    hooks: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> HookConfig:
        """从字典创建配置"""
        if not data or not isinstance(data, dict):
            return cls()
        return cls(hooks=data)

    def get_definitions(self, event: str) -> list[HookDefinition]:
        """获取指定事件的 hook 定义列表"""
        raw_list = self.hooks.get(event, [])
        definitions: list[HookDefinition] = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            try:
                hook_type = HookType(item.get("type", "command"))
            except ValueError:
                hook_type = HookType.COMMAND
            definitions.append(
                HookDefinition(
                    type=hook_type,
                    command=str(item.get("command", "")),
                    timeout=int(item.get("timeout", 30)),
                    matcher=str(item.get("matcher", "*")),
                    description=str(item.get("description", "")),
                    blocking=bool(item.get("blocking", True)),
                )
            )
        return definitions
