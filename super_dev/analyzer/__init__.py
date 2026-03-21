"""
Super Dev 项目分析器
用于自动检测和分析项目结构
"""

from .analyzer import ArchitectureReport, ProjectAnalyzer
from .dependency_graph import (
    CriticalPath,
    DependencyEdge,
    DependencyGraphBuilder,
    DependencyGraphReport,
    DependencyNode,
)
from .detectors import detect_project_type, detect_tech_stack
from .impact import ImpactAnalysisReport, ImpactAnalyzer, ImpactItem
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
from .regression_guard import RegressionCheck, RegressionGuardBuilder, RegressionGuardReport
from .repo_map import RepoMapBuilder, RepoMapItem, RepoMapReport

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
    "RepoMapBuilder",
    "RepoMapItem",
    "RepoMapReport",
    "ImpactAnalyzer",
    "ImpactAnalysisReport",
    "ImpactItem",
    "RegressionCheck",
    "RegressionGuardBuilder",
    "RegressionGuardReport",
    "DependencyEdge",
    "DependencyNode",
    "CriticalPath",
    "DependencyGraphBuilder",
    "DependencyGraphReport",
    "detect_project_type",
    "detect_tech_stack",
]
