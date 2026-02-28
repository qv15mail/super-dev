# -*- coding: utf-8 -*-
"""
专家系统调度器 - 协调 10 位专家协作生成文档

开发：Excellent（11964948@qq.com）
功能：调度专家角色，生成高质量项目文档
作用：将工作路由到正确的专家处理器
创建时间：2025-12-30
最后修改：2026-01-29
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ExpertRole(Enum):
    """专家角色枚举"""
    PM = "PM"                       # 产品经理
    ARCHITECT = "ARCHITECT"         # 架构师
    UI = "UI"                       # UI 设计师
    UX = "UX"                       # UX 设计师
    SECURITY = "SECURITY"           # 安全专家
    CODE = "CODE"                   # 代码专家
    DBA = "DBA"                     # 数据库专家
    QA = "QA"                       # 质量保证专家
    DEVOPS = "DEVOPS"               # DevOps 工程师
    RCA = "RCA"                     # 根因分析专家


EXPERT_DESCRIPTIONS: dict[ExpertRole, str] = {
    ExpertRole.PM: "需求分析、PRD 编写、用户故事、业务规则",
    ExpertRole.ARCHITECT: "系统设计、技术选型、架构文档、API 设计",
    ExpertRole.UI: "视觉设计、设计规范、组件库、品牌一致性",
    ExpertRole.UX: "交互设计、用户体验、信息架构、可用性测试",
    ExpertRole.SECURITY: "安全审查、漏洞检测、威胁建模、合规",
    ExpertRole.CODE: "代码实现、最佳实践、代码审查、性能优化",
    ExpertRole.DBA: "数据库设计、SQL 优化、数据建模、迁移策略",
    ExpertRole.QA: "质量保证、测试策略、自动化测试、质量门禁",
    ExpertRole.DEVOPS: "部署、CI/CD、容器化、监控告警",
    ExpertRole.RCA: "根因分析、故障复盘、风险识别、改进建议",
}


@dataclass
class ExpertOutput:
    """专家输出"""
    role: ExpertRole
    document_type: str          # prd | architecture | uiux | redteam | quality-gate | ...
    content: str
    quality_score: int = 85      # 0-100
    metadata: dict = field(default_factory=dict)


@dataclass
class ExpertTeamResult:
    """专家团队协作结果"""
    outputs: list[ExpertOutput] = field(default_factory=list)
    total_score: float = 0.0
    summary: str = ""

    def get_output(self, doc_type: str) -> Optional[ExpertOutput]:
        for out in self.outputs:
            if out.document_type == doc_type:
                return out
        return None


class ExpertDispatcher:
    """
    专家调度器

    根据任务类型将工作路由到正确的专家处理器，
    并协调多专家协作完成文档生成任务。
    """

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def dispatch_document_generation(
        self,
        name: str,
        description: str,
        platform: str = "web",
        frontend: str = "react",
        backend: str = "node",
        domain: str = "",
        **kwargs,
    ) -> ExpertTeamResult:
        """
        调度多专家协作生成完整项目文档集

        调用顺序：PM → ARCHITECT → UI/UX → SECURITY → DBA → QA → DEVOPS
        """
        from ..creators.document_generator import DocumentGenerator

        gen = DocumentGenerator(
            name=name,
            description=description,
            platform=platform,
            frontend=frontend,
            backend=backend,
            domain=domain,
            **kwargs,
        )

        result = ExpertTeamResult()

        # 1. PM 专家：生成 PRD
        prd_content = gen.generate_prd()
        result.outputs.append(ExpertOutput(
            role=ExpertRole.PM,
            document_type="prd",
            content=prd_content,
            quality_score=self._score_document(prd_content, ["产品愿景", "功能需求", "验收标准"]),
            metadata={"name": name, "platform": platform},
        ))

        # 2. ARCHITECT 专家：生成架构文档
        arch_content = gen.generate_architecture()
        result.outputs.append(ExpertOutput(
            role=ExpertRole.ARCHITECT,
            document_type="architecture",
            content=arch_content,
            quality_score=self._score_document(arch_content, ["技术栈", "数据库", "API", "安全"]),
            metadata={"frontend": frontend, "backend": backend},
        ))

        # 3. UI/UX 专家：生成 UI/UX 文档
        uiux_content = gen.generate_uiux()
        result.outputs.append(ExpertOutput(
            role=ExpertRole.UI,
            document_type="uiux",
            content=uiux_content,
            quality_score=self._score_document(uiux_content, ["设计系统", "色彩", "组件"]),
            metadata={"platform": platform},
        ))

        # 4. 计算团队总分
        scores = [o.quality_score for o in result.outputs]
        result.total_score = sum(scores) / len(scores) if scores else 0.0
        result.summary = (
            f"专家团队协作完成：生成 {len(result.outputs)} 份文档，"
            f"平均质量分 {result.total_score:.0f}/100"
        )

        return result

    def dispatch_redteam_review(
        self,
        name: str,
        tech_stack: dict,
    ) -> ExpertOutput:
        """SECURITY 专家：调度红队审查"""
        from ..reviewers.redteam import RedTeamReviewer

        reviewer = RedTeamReviewer(
            project_dir=self.project_dir,
            name=name,
            tech_stack=tech_stack,
        )
        report = reviewer.review()
        content = report.to_markdown()

        return ExpertOutput(
            role=ExpertRole.SECURITY,
            document_type="redteam",
            content=content,
            quality_score=report.total_score,
            metadata={
                "critical_count": report.critical_count,
                "high_count": report.high_count,
                "security_issues": [self._serialize_security_issue(i) for i in report.security_issues],
                "performance_issues": [self._serialize_performance_issue(i) for i in report.performance_issues],
                "architecture_issues": [self._serialize_architecture_issue(i) for i in report.architecture_issues],
            },
        )

    def dispatch_quality_gate(
        self,
        name: str,
        tech_stack: dict,
        redteam_report=None,
        threshold_override: Optional[int] = None,
    ) -> ExpertOutput:
        """QA 专家：调度质量门禁检查"""
        from ..reviewers.quality_gate import QualityGateChecker

        checker = QualityGateChecker(
            project_dir=self.project_dir,
            name=name,
            tech_stack=tech_stack,
            threshold_override=threshold_override,
        )
        result = checker.check(redteam_report=redteam_report)
        content = result.to_markdown()

        return ExpertOutput(
            role=ExpertRole.QA,
            document_type="quality-gate",
            content=content,
            quality_score=result.total_score,
            metadata={
                "passed": result.passed,
                "scenario": result.scenario,
                "weighted_score": result.weighted_score,
            },
        )

    def dispatch_code_review(
        self,
        name: str,
        tech_stack: dict,
    ) -> ExpertOutput:
        """CODE 专家：调度代码审查"""
        from ..reviewers.code_review import CodeReviewGuideGenerator

        generator = CodeReviewGuideGenerator(
            project_dir=self.project_dir,
            name=name,
            tech_stack=tech_stack,
        )
        content = generator.generate()

        return ExpertOutput(
            role=ExpertRole.CODE,
            document_type="code-review",
            content=content,
            quality_score=85,
            metadata={"tech_stack": tech_stack},
        )

    def dispatch_ai_prompt(self, name: str) -> ExpertOutput:
        """CODE 专家：生成 AI 提示词"""
        from ..creators.prompt_generator import AIPromptGenerator

        generator = AIPromptGenerator(
            project_dir=self.project_dir,
            name=name,
        )
        content = generator.generate()

        return ExpertOutput(
            role=ExpertRole.CODE,
            document_type="ai-prompt",
            content=content,
            quality_score=90,
            metadata={"name": name},
        )

    def dispatch_cicd(
        self,
        name: str,
        tech_stack: dict,
        cicd_platform: str = "github",
    ) -> ExpertOutput:
        """DEVOPS 专家：生成 CI/CD 配置"""
        from ..deployers.cicd import CICDGenerator

        generator = CICDGenerator(
            project_dir=self.project_dir,
            name=name,
            tech_stack=tech_stack,
        )
        content = generator.generate(platform=cicd_platform)

        return ExpertOutput(
            role=ExpertRole.DEVOPS,
            document_type="cicd",
            content=content,
            quality_score=88,
            metadata={"platform": cicd_platform},
        )

    def dispatch_migration(
        self,
        name: str,
        tech_stack: dict,
        orm: str = "prisma",
    ) -> ExpertOutput:
        """DBA 专家：生成数据库迁移脚本"""
        from ..deployers.migration import MigrationGenerator

        generator = MigrationGenerator(
            project_dir=self.project_dir,
            name=name,
            tech_stack=tech_stack,
        )
        content = generator.generate(orm=orm)

        return ExpertOutput(
            role=ExpertRole.DBA,
            document_type="migration",
            content=content,
            quality_score=87,
            metadata={"orm": orm},
        )

    def list_experts(self) -> list[dict]:
        """列出所有专家信息"""
        return [
            {
                "role": role.value,
                "description": desc,
            }
            for role, desc in EXPERT_DESCRIPTIONS.items()
        ]

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _score_document(self, content: str, required_keywords: list[str]) -> int:
        """基于关键词检测评估文档质量分"""
        if not content:
            return 0
        base = 70
        per_keyword = 10
        for kw in required_keywords:
            if kw in content:
                base += per_keyword
        # 长度加分（越详细越好，上限 100）
        length_bonus = min(10, len(content) // 2000)
        return min(100, base + length_bonus)

    def _serialize_security_issue(self, issue) -> dict:
        return {
            "severity": issue.severity,
            "category": issue.category,
            "description": issue.description,
            "recommendation": issue.recommendation,
            "cwe": issue.cwe,
            "file_path": issue.file_path,
            "line": issue.line,
        }

    def _serialize_performance_issue(self, issue) -> dict:
        return {
            "severity": issue.severity,
            "category": issue.category,
            "description": issue.description,
            "recommendation": issue.recommendation,
            "impact": issue.impact,
            "file_path": issue.file_path,
            "line": issue.line,
        }

    def _serialize_architecture_issue(self, issue) -> dict:
        return {
            "severity": issue.severity,
            "category": issue.category,
            "description": issue.description,
            "recommendation": issue.recommendation,
            "adr_needed": issue.adr_needed,
            "file_path": issue.file_path,
            "line": issue.line,
        }
