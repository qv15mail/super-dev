"""
Pipeline Hook 管理器 — 注册、匹配、执行 hook。

Pipeline hook 系统架构:
- 10 种 hook 事件
- 事件匹配模式 (阶段名 / 通配符)
- Shell 命令执行 + 超时控制
- 执行结果记录和日志

开发：Super Dev Team
创建时间：2026-03-31
"""

from __future__ import annotations

import fnmatch
import subprocess  # nosec B404
import time
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils import get_logger
from .models import HookConfig, HookDefinition, HookResult, HookType

logger = get_logger("hooks")


class HookEvent(str, Enum):
    """Pipeline hook 事件类型

    Super Dev pipeline 适用的 8 种 hook 事件类型。
    """

    PRE_PHASE = "PrePhase"  # 阶段执行前
    POST_PHASE = "PostPhase"  # 阶段执行后
    PRE_DOCUMENT = "PreDocument"  # 文档生成前
    POST_DOCUMENT = "PostDocument"  # 文档生成后
    PRE_QUALITY_GATE = "PreQualityGate"  # 质量门禁前
    POST_QUALITY_GATE = "PostQualityGate"  # 质量门禁后
    ON_ERROR = "OnError"  # 错误发生时
    SESSION_START = "SessionStart"  # 会话开始


class HookManager:
    """Pipeline Hook 管理器"""

    def __init__(
        self,
        config: HookConfig | None = None,
        project_dir: Path | None = None,
    ):
        self.config = config or HookConfig()
        self.project_dir = project_dir or Path.cwd()
        self._results: list[HookResult] = []
        self._callbacks: dict[str, list] = {}  # Python callback hooks

    @classmethod
    def from_yaml_config(cls, yaml_config: dict[str, Any], project_dir: Path | None = None):
        """从 super-dev.yaml 的 hooks 段创建管理器"""
        config = HookConfig.from_dict(yaml_config.get("hooks"))
        return cls(config=config, project_dir=project_dir)

    def register_callback(
        self,
        event: HookEvent | str,
        callback,
        matcher: str = "*",
    ) -> None:
        """注册 Python 回调 hook"""
        event_name = event.value if isinstance(event, HookEvent) else event
        if event_name not in self._callbacks:
            self._callbacks[event_name] = []
        self._callbacks[event_name].append({"callback": callback, "matcher": matcher})

    def execute(
        self,
        event: HookEvent | str,
        context: dict[str, Any] | None = None,
        phase: str = "",
    ) -> list[HookResult]:
        """执行指定事件的所有匹配 hook。

        Args:
            event: hook 事件类型
            context: 上下文数据 (传递给 hook 命令的环境变量)
            phase: 当前阶段名 (用于 matcher 匹配)

        Returns:
            HookResult 列表
        """
        event_name = event.value if isinstance(event, HookEvent) else event
        results: list[HookResult] = []

        # 1. 执行配置文件中的 hook
        definitions = self.config.get_definitions(event_name)
        for defn in definitions:
            if not self._matches(defn.matcher, phase):
                continue
            result = self._execute_definition(defn, event_name, context or {})
            results.append(result)
            self._results.append(result)

            if result.blocked:
                logger.warning(f"Hook 阻止了 pipeline 继续: {event_name} ({defn.command})")
                break

        # 2. 执行 Python 回调 hook
        for cb_entry in self._callbacks.get(event_name, []):
            if not self._matches(cb_entry["matcher"], phase):
                continue
            result = self._execute_callback(cb_entry["callback"], event_name, context or {})
            results.append(result)
            self._results.append(result)

        return results

    def has_blocking_result(self, results: list[HookResult]) -> bool:
        """检查结果中是否有阻塞性失败"""
        return any(r.blocked for r in results)

    def get_history(self) -> list[HookResult]:
        """获取所有执行历史"""
        return list(self._results)

    def clear_history(self) -> None:
        """清除执行历史"""
        self._results.clear()

    def list_configured_hooks(self) -> dict[str, list[dict[str, Any]]]:
        """列出所有配置的 hook (用于 CLI 展示)"""
        result: dict[str, list[dict[str, Any]]] = {}
        for event_name, definitions in self.config.hooks.items():
            result[event_name] = definitions
        return result

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _matches(self, matcher: str, phase: str) -> bool:
        """检查 matcher 是否匹配当前阶段"""
        if matcher == "*":
            return True
        if not phase:
            return True
        return fnmatch.fnmatch(phase.lower(), matcher.lower())

    def _execute_definition(
        self,
        defn: HookDefinition,
        event_name: str,
        context: dict[str, Any],
    ) -> HookResult:
        """执行单个 hook 定义"""
        if defn.type == HookType.LOG:
            return self._execute_log_hook(defn, event_name)
        if defn.type == HookType.COMMAND:
            return self._execute_command_hook(defn, event_name, context)
        return HookResult(
            hook_name=defn.command or defn.description,
            event=event_name,
            success=False,
            error=f"不支持的 hook 类型: {defn.type}",
        )

    def _execute_command_hook(
        self,
        defn: HookDefinition,
        event_name: str,
        context: dict[str, Any],
    ) -> HookResult:
        """执行 shell 命令 hook"""
        if not defn.command:
            return HookResult(
                hook_name="(empty)",
                event=event_name,
                success=False,
                error="Hook command 为空",
            )

        env = {
            "SUPER_DEV_EVENT": event_name,
            "SUPER_DEV_PHASE": context.get("phase", ""),
            "SUPER_DEV_PROJECT": str(self.project_dir),
        }
        # 添加上下文环境变量 (只取字符串值)
        for key, val in context.items():
            if isinstance(val, str):
                env[f"SUPER_DEV_{key.upper()}"] = val

        start = time.monotonic()
        try:
            result = subprocess.run(
                defn.command,
                shell=True,  # nosec B602
                capture_output=True,
                text=True,
                timeout=defn.timeout,
                cwd=str(self.project_dir),
                env={**dict(__import__("os").environ), **env},
            )
            duration_ms = (time.monotonic() - start) * 1000

            blocked = defn.blocking and result.returncode == 2
            return HookResult(
                hook_name=defn.command,
                event=event_name,
                success=result.returncode == 0,
                output=result.stdout[:2000] if result.stdout else "",
                error=result.stderr[:1000] if result.stderr else "",
                duration_ms=duration_ms,
                blocked=blocked,
            )
        except subprocess.TimeoutExpired:
            duration_ms = (time.monotonic() - start) * 1000
            return HookResult(
                hook_name=defn.command,
                event=event_name,
                success=False,
                error=f"Hook 执行超时 ({defn.timeout}s)",
                duration_ms=duration_ms,
                blocked=defn.blocking,
            )
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            return HookResult(
                hook_name=defn.command,
                event=event_name,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )

    def _execute_log_hook(
        self,
        defn: HookDefinition,
        event_name: str,
    ) -> HookResult:
        """执行日志 hook (仅记录)"""
        msg = defn.description or f"Hook event: {event_name}"
        logger.info(f"[Hook] {msg}")
        return HookResult(
            hook_name=defn.description or "(log)",
            event=event_name,
            success=True,
            output=msg,
        )

    def _execute_callback(
        self,
        callback,
        event_name: str,
        context: dict[str, Any],
    ) -> HookResult:
        """执行 Python 回调 hook"""
        start = time.monotonic()
        try:
            result = callback(context)
            duration_ms = (time.monotonic() - start) * 1000
            blocked = result is False  # 回调返回 False 表示阻塞
            return HookResult(
                hook_name=getattr(callback, "__name__", str(callback)),
                event=event_name,
                success=not blocked,
                output=str(result) if result and result is not True else "",
                duration_ms=duration_ms,
                blocked=blocked,
            )
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            return HookResult(
                hook_name=getattr(callback, "__name__", str(callback)),
                event=event_name,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )
