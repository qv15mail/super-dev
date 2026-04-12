"""
Super Dev 国际化 (i18n) 基础模块。

提供中英双语支持，通过统一接口实现运行时多语言切换。

用法::

    from super_dev.i18n import t, set_locale, get_locale

    set_locale("en")
    t("error:file_not_found", path="/tmp/missing.txt")
    # => "File not found: /tmp/missing.txt"

环境变量:
    SUPER_DEV_LANG: 指定默认语言 (\"zh\" 或 \"en\")，未设置时默认 \"zh\"。
"""

from __future__ import annotations

import os
from typing import Any

# ---------------------------------------------------------------------------
# Locale state
# ---------------------------------------------------------------------------

_DEFAULT_LOCALE: str = "zh"
_current_locale: str = os.environ.get("SUPER_DEV_LANG", _DEFAULT_LOCALE)

# ---------------------------------------------------------------------------
# Translation catalog  (key -> {locale -> template})
# ---------------------------------------------------------------------------

_TRANSLATIONS: dict[str, dict[str, str]] = {
    # -- 错误消息 / Error messages ------------------------------------------
    "error:user_interrupted": {
        "zh": "已取消",
        "en": "Cancelled",
    },
    "error:file_not_found": {
        "zh": "文件不存在: {path}",
        "en": "File not found: {path}",
    },
    "error:permission_denied": {
        "zh": "权限不足: {path}",
        "en": "Permission denied: {path}",
    },
    "error:network_failure": {
        "zh": "网络连接失败",
        "en": "Network connection failed",
    },
    "error:timeout": {
        "zh": "操作超时",
        "en": "Operation timed out",
    },
    "error:config_format": {
        "zh": "配置文件格式错误 (JSON): {msg}",
        "en": "Config format error (JSON): {msg}",
    },
    "error:invalid_args": {
        "zh": "参数错误: {detail}",
        "en": "Invalid arguments: {detail}",
    },
    "error:unknown": {
        "zh": "发生错误: {detail}",
        "en": "An error occurred: {detail}",
    },
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_locale() -> str:
    """返回当前激活的语言代码。"""
    return _current_locale


def set_locale(locale: str) -> None:
    """设置当前语言。

    Args:
        locale: 语言代码，目前支持 ``"zh"`` 和 ``"en"``。

    Raises:
        ValueError: 当传入不支持的语言代码时抛出。
    """
    global _current_locale
    supported = {_DEFAULT_LOCALE, "en"}
    if locale not in supported:
        raise ValueError(f"Unsupported locale '{locale}'. Supported: {sorted(supported)}")
    _current_locale = locale


def t(key: str, **kwargs: Any) -> str:
    """根据当前语言查找翻译模板并用 *kwargs* 插值后返回。

    如果 *key* 在翻译目录中不存在，则直接返回 *key* 本身作为回退。

    Args:
        key: 翻译键，例如 ``"error:file_not_found"``。
        **kwargs: 用于模板插值的关键字参数。

    Returns:
        插值后的本地化字符串。
    """
    entry = _TRANSLATIONS.get(key)
    if entry is None:
        return key

    template = entry.get(_current_locale) or entry.get(_DEFAULT_LOCALE) or key
    try:
        return template.format(**kwargs) if kwargs else template
    except (KeyError, ValueError, IndexError):
        # Missing placeholder, malformed braces, or bad index — return uninterpolated
        return template
