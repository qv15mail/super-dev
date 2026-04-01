"""Auto-memory system — 从 pipeline 执行结果中自动提取和管理记忆。"""

from __future__ import annotations

from .consolidator import ConsolidationConfig, ConsolidationResult, MemoryConsolidator
from .extractor import MemoryExtractor
from .store import MemoryEntry, MemoryStore

__all__ = [
    "ConsolidationConfig",
    "ConsolidationResult",
    "MemoryConsolidator",
    "MemoryEntry",
    "MemoryExtractor",
    "MemoryStore",
]
