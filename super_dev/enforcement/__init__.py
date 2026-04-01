"""
宿主侧执行机制 — 自动配置 AI coding host 的 hooks 和验证规则。

Super Dev 治理模式升级：从 Advisory（建议）到 Enforcement（执行）。
不再只是生成文档和规则，而是在宿主侧配置实际的执行机制。
"""

from .host_hooks import HostHooksConfigurator
from .pre_code_gate import PreCodeGate
from .validation import ValidationScriptGenerator

__all__ = [
    "HostHooksConfigurator",
    "PreCodeGate",
    "ValidationScriptGenerator",
]
