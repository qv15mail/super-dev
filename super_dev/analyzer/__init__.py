"""
Super Dev 项目分析器
用于自动检测和分析项目结构
"""

from .analyzer import ArchitectureReport, ProjectAnalyzer
from .detectors import detect_project_type, detect_tech_stack
from .models import (
    ArchitecturePattern,
    Dependency,
    DesignPattern,
    FrameworkType,
    PatternType,
    ProjectCategory,
    ProjectType,
    TechStack,
)

__all__ = [
    "ProjectAnalyzer",
    "ProjectCategory",
    "ProjectType",
    "ArchitectureReport",
    "Dependency",
    "DesignPattern",
    "PatternType",
    "TechStack",
    "FrameworkType",
    "ArchitecturePattern",
    "detect_project_type",
    "detect_tech_stack",
]


