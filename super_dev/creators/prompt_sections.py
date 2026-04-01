"""
Prompt Section Registry — 分层式提示词构建引擎

开发：Excellent（11964948@qq.com）
功能：将提示词拆分为独立可注册的段落，支持缓存与优先级排序
注册制 prompt section 管理。
创建时间：2026-03-31
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class PromptSection:
    """A single prompt section that can be registered in a PromptBuilder.

    Attributes:
        name: Unique section identifier.
        content_fn: Lazy content generator; receives ``**context`` and returns
            a string (or ``None`` to skip).
        cacheable: Whether the resolved content can be cached across invocations.
        priority: Lower values appear earlier in the final output.
    """

    name: str
    content_fn: Callable[..., str | None]
    cacheable: bool = True
    priority: int = 100


class PromptBuilder:
    """Registry-based prompt construction engine.

    Sections are registered with :meth:`register`, then resolved together via
    :meth:`resolve`.  Cacheable sections store their result after the first
    resolve so that repeated calls are cheaper.
    """

    def __init__(self) -> None:
        self._sections: dict[str, PromptSection] = {}
        self._cache: dict[str, str | None] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, section: PromptSection) -> None:
        """Register (or replace) a prompt section."""
        self._sections[section.name] = section
        # Invalidate cache for this section when re-registered.
        self._cache.pop(section.name, None)

    def resolve(self, **context: Any) -> str:
        """Resolve all registered sections and join them into a single string.

        Sections are sorted by *priority* (ascending).  Sections whose
        ``content_fn`` returns ``None`` or an empty string are silently
        skipped.
        """
        ordered = sorted(self._sections.values(), key=lambda s: s.priority)
        parts: list[str] = []
        for section in ordered:
            content = self._resolve_section(section, **context)
            if content:
                parts.append(content)
        return "\n".join(parts)

    def get_section(self, name: str, **context: Any) -> str | None:
        """Resolve and return a single section by *name*.

        Returns ``None`` if the section is not registered or its
        ``content_fn`` returns ``None``.
        """
        section = self._sections.get(name)
        if section is None:
            return None
        return self._resolve_section(section, **context)

    def clear_cache(self) -> None:
        """Drop all cached section outputs."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_section(self, section: PromptSection, **context: Any) -> str | None:
        if section.cacheable and section.name in self._cache:
            return self._cache[section.name]

        content = section.content_fn(**context)

        if section.cacheable:
            self._cache[section.name] = content
        return content
