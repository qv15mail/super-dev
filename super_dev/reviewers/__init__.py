"""
审查模块 - 红队审查、代码审查、质量检查

开发：Excellent（11964948@qq.com）
功能：提供完整的审查流程
创建时间：2025-12-30
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "RedTeamReviewer",
    "CodeReviewGenerator",
    "QualityGateChecker",
    "QualityAdvisor",
    "QualityAdvisorReport",
    "QualityAdvice",
    "UIReviewReviewer",
    "UIReviewReport",
    "ValidationRuleEngine",
    "ValidationRule",
    "ValidationResult",
    "ValidationReport",
    "ExternalReviewCollector",
    "ExternalReviewResult",
]


def __getattr__(name: str) -> Any:
    if name == "RedTeamReviewer":
        return getattr(import_module(".redteam", __name__), name)
    if name == "CodeReviewGenerator":
        return getattr(import_module(".code_review", __name__), name)
    if name in {"UIReviewReviewer", "UIReviewReport"}:
        return getattr(import_module(".ui_review", __name__), name)
    if name == "QualityGateChecker":
        return getattr(import_module(".quality_gate", __name__), name)
    if name in {"ValidationRuleEngine", "ValidationRule", "ValidationResult", "ValidationReport"}:
        return getattr(import_module(".validation_rules", __name__), name)
    if name in {"QualityAdvisor", "QualityAdvisorReport", "QualityAdvice"}:
        return getattr(import_module(".quality_advisor", __name__), name)
    if name in {"ExternalReviewCollector", "ExternalReviewResult"}:
        return getattr(import_module(".external_reviews", __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
