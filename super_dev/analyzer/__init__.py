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
from .repo_map import RepoMapBuilder, RepoMapItem, RepoMapReport
from .impact import ImpactAnalyzer, ImpactAnalysisReport, ImpactItem
from .regression_guard import RegressionCheck, RegressionGuardBuilder, RegressionGuardReport
from .dependency_graph import CriticalPath, DependencyEdge, DependencyGraphBuilder, DependencyGraphReport, DependencyNode

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
