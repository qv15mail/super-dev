"""
统一错误处理 — 所有 CLI 命令的错误都经过这里。

将 Python 异常转换为用户友好的错误信息，隐藏 traceback。
支持通过 i18n 模块进行中英双语切换。
"""

from __future__ import annotations

import json
import logging

from .i18n import t

logger = logging.getLogger("super_dev.error_handler")

# Exit codes
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_INTERRUPTED = 130


def handle_cli_error(error: Exception, command: str = "") -> int:
    """将 Python 异常转换为用户友好的错误信息。

    绝不向终端用户显示 Python traceback。错误信息使用中文，
    保持与 CLI 其余部分一致的风格。

    Args:
        error: 捕获到的异常
        command: 触发异常的 CLI 命令名（可选，用于日志）

    Returns:
        退出码 — 1 表示运行时错误，2 表示使用错误，130 表示用户中断
    """
    from .terminal import create_console

    console = create_console()

    # ── 用户中断 ──────────────────────────────────────────────
    if isinstance(error, KeyboardInterrupt):
        console.print(f"[yellow]{t('error:user_interrupted')}[/yellow]")
        return EXIT_INTERRUPTED

    # ── 已知的 Super Dev 异常 ─────────────────────────────────
    from .exceptions import SuperDevError

    if isinstance(error, SuperDevError):
        console.print(f"[red]错误: {error.message}[/red]")
        if error.details:
            logger.warning("命令执行失败: %s — %s", error.code, error.details)
        return EXIT_ERROR

    # ── 文件系统 ──────────────────────────────────────────────
    if isinstance(error, FileNotFoundError):
        path = getattr(error, "filename", None) or str(error)
        console.print(f"[red]{t('error:file_not_found', path=path)}[/red]")
        return EXIT_ERROR

    if isinstance(error, PermissionError):
        path = getattr(error, "filename", None) or str(error)
        console.print(f"[red]{t('error:permission_denied', path=path)}[/red]")
        return EXIT_ERROR

    if isinstance(error, IsADirectoryError):
        path = getattr(error, "filename", None) or str(error)
        console.print(f"[red]路径是目录而非文件: {path}[/red]")
        return EXIT_ERROR

    # ── 配置解析 ──────────────────────────────────────────────
    if isinstance(error, json.JSONDecodeError):
        console.print(
            f"[red]{t('error:config_format', msg=f'{error.msg}, 行 {error.lineno}')}[/red]"
        )
        return EXIT_ERROR

    try:
        import yaml

        if isinstance(error, yaml.YAMLError):
            console.print("[red]YAML 配置格式错误[/red]")
            if hasattr(error, "problem_mark") and error.problem_mark is not None:
                mark = error.problem_mark
                console.print(f"  位置: 行 {mark.line + 1}, 列 {mark.column + 1}")
            return EXIT_ERROR
    except ImportError:
        pass

    # ── 网络 ──────────────────────────────────────────────────
    if isinstance(error, ConnectionError):
        console.print(f"[red]{t('error:network_failure')}[/red]")
        return EXIT_ERROR

    if isinstance(error, TimeoutError):
        console.print(f"[red]{t('error:timeout')}[/red]")
        return EXIT_ERROR

    # ── 使用错误 ──────────────────────────────────────────────
    if isinstance(error, ValueError | TypeError):
        console.print(f"[red]{t('error:invalid_args', detail=error)}[/red]")
        return EXIT_USAGE

    # ── 兜底 ──────────────────────────────────────────────────
    console.print(f"[red]{t('error:unknown', detail=error)}[/red]")
    logger.error(
        "CLI 命令异常: %s — %s: %s",
        command,
        type(error).__name__,
        error,
        exc_info=True,  # full traceback in log, not on screen
    )
    return EXIT_ERROR
