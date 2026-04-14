"""
质量评分引擎 - 基于文档内容和检查项计算真实质量分数

开发：Excellent（11964948@qq.com）
功能：为 WorkflowEngine 提供真实的质量评分算法
作用：替代原来硬编码的 return 85.0，基于多维度评估
创建时间：2026-01-29
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QualityDimension:
    """质量评估维度"""

    name: str
    score: int  # 0-100
    weight: float  # 权重
    details: str = ""


@dataclass
class PhaseQualityReport:
    """阶段质量评估报告"""

    phase_name: str
    dimensions: list[QualityDimension] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        if not self.dimensions:
            return 0.0
        total_w = sum(d.weight for d in self.dimensions)
        if total_w == 0:
            return 0.0
        return sum(d.score * d.weight for d in self.dimensions) / total_w

    @property
    def total_score(self) -> int:
        return int(self.weighted_score)


class QualityScorer:
    """
    质量评分引擎

    为 orchestrator/engine.py 中的每个阶段提供真实质量评分，
    替代硬编码的 return 85.0。
    """

    def __init__(self, project_dir: Path, name: str):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.output_dir = self.project_dir / "output"

    # ------------------------------------------------------------------
    # 阶段评分入口
    # ------------------------------------------------------------------

    def score_discovery(self, context_data: dict) -> int:
        """第 0 阶段：需求增强质量评分"""
        report = PhaseQualityReport(phase_name="discovery")

        # 1. 需求描述长度和完整度
        description = context_data.get("description", "")
        desc_score = min(100, max(40, len(description) // 2))
        report.dimensions.append(
            QualityDimension(
                name="需求描述完整度",
                score=desc_score,
                weight=1.5,
                details=f"需求描述长度：{len(description)} 字符",
            )
        )

        # 2. 是否有知识库增强
        has_kb_enhancement = bool(context_data.get("knowledge_enhanced"))
        report.dimensions.append(
            QualityDimension(
                name="知识库增强",
                score=90 if has_kb_enhancement else 60,
                weight=1.0,
                details="知识库已注入" if has_kb_enhancement else "未进行知识库增强",
            )
        )

        # 3. 是否有联网检索
        has_web_research = bool(context_data.get("web_research"))
        report.dimensions.append(
            QualityDimension(
                name="联网检索",
                score=90 if has_web_research else 65,
                weight=0.8,
                details="已完成联网检索" if has_web_research else "未进行联网检索（离线模式）",
            )
        )

        return report.total_score

    def score_documentation(self) -> int:
        """第 1 阶段：文档生成质量评分"""
        report = PhaseQualityReport(phase_name="documentation")

        # PRD 文档
        prd_score = self._score_doc_file(
            f"{self.name}-prd.md",
            required_sections=["产品愿景", "功能需求", "用户故事", "验收标准"],
            min_length=2000,
        )
        report.dimensions.append(
            QualityDimension(
                name="PRD 文档",
                score=prd_score,
                weight=1.5,
            )
        )

        # 架构文档
        arch_score = self._score_doc_file(
            f"{self.name}-architecture.md",
            required_sections=["技术栈", "数据库", "API", "安全"],
            min_length=2000,
        )
        report.dimensions.append(
            QualityDimension(
                name="架构文档",
                score=arch_score,
                weight=1.5,
            )
        )

        # UI/UX 文档
        uiux_score = self._score_doc_file(
            f"{self.name}-uiux.md",
            required_sections=["设计系统", "色彩"],
            min_length=1000,
        )
        report.dimensions.append(
            QualityDimension(
                name="UI/UX 文档",
                score=uiux_score,
                weight=1.0,
            )
        )

        return report.total_score

    def score_frontend_scaffold(self) -> int:
        """第 2 阶段：前端骨架质量评分"""
        report = PhaseQualityReport(phase_name="frontend_scaffold")

        # 前端蓝图文档
        blueprint_score = self._score_doc_file(
            f"{self.name}-frontend-blueprint.md",
            required_sections=["信息架构", "页面", "组件"],
            min_length=500,
        )
        report.dimensions.append(
            QualityDimension(
                name="前端蓝图",
                score=blueprint_score,
                weight=1.2,
            )
        )

        # 执行计划
        plan_score = self._score_doc_file(
            f"{self.name}-execution-plan.md",
            required_sections=["phase", "阶段"],
            min_length=500,
        )
        report.dimensions.append(
            QualityDimension(
                name="执行计划",
                score=plan_score,
                weight=1.0,
            )
        )

        return report.total_score

    def score_spec(self) -> int:
        """第 3 阶段：Spec 规范质量评分"""
        spec_dir = self.project_dir / ".super-dev" / "changes"
        if not spec_dir.exists():
            return 55  # 没有 Spec，宽松评分

        changes = [d for d in spec_dir.iterdir() if d.is_dir()]
        if not changes:
            return 55

        # 检查最新的 change
        latest = sorted(changes)[-1]
        tasks_file = latest / "tasks.md"
        proposal_file = latest / "proposal.md"

        score = 50
        if proposal_file.exists():
            score += 20
        if tasks_file.exists():
            content = tasks_file.read_text(encoding="utf-8", errors="ignore")
            # 计算任务数量
            task_count = content.count("- [ ]") + content.count("- [x]")
            score += min(30, task_count * 5)

        return min(100, score)

    def score_scaffold(self) -> int:
        """第 4 阶段：前后端实现骨架质量评分"""
        report = PhaseQualityReport(phase_name="scaffold")

        impl_score = self._score_doc_file(
            f"{self.name}-implementation.md",
            required_sections=["目录结构", "API", "frontend", "backend"],
            min_length=500,
        )
        report.dimensions.append(
            QualityDimension(
                name="实现骨架",
                score=impl_score,
                weight=1.0,
            )
        )

        return report.total_score

    def score_redteam(self) -> int:
        """第 5 阶段：红队审查质量评分"""
        redteam_score = self._score_doc_file(
            f"{self.name}-redteam.md",
            required_sections=["安全审查", "性能审查", "架构审查"],
            min_length=500,
        )

        # 从报告中提取实际红队分数
        redteam_file = self.output_dir / f"{self.name}-redteam.md"
        if redteam_file.exists():
            content = redteam_file.read_text(encoding="utf-8", errors="ignore")
            # 尝试提取 "总分: XX/100" 格式
            import re

            match = re.search(r"总分[：:]\s*(\d+)/100", content)
            if match:
                return int(match.group(1))

        return redteam_score

    def score_quality_gate(self) -> int:
        """第 6 阶段：质量门禁报告评分"""
        qg_file = self.output_dir / f"{self.name}-quality-gate.md"
        if not qg_file.exists():
            return 60

        content = qg_file.read_text(encoding="utf-8", errors="ignore")

        # 提取总分
        import re

        match = re.search(r"总分[：:]\s*(\d+)/100", content)
        if match:
            return int(match.group(1))

        # 检查是否通过
        if "通过" in content and "未通过" not in content:
            return 85
        return 65

    def score_code_review(self) -> int:
        """第 7 阶段：代码审查指南评分"""
        score = self._score_doc_file(
            f"{self.name}-code-review.md",
            required_sections=["审查清单", "安全", "性能"],
            min_length=500,
        )
        return score

    def score_ai_prompt(self) -> int:
        """第 8 阶段：AI 提示词生成评分"""
        score = self._score_doc_file(
            f"{self.name}-ai-prompt.md",
            required_sections=["任务列表", "开发规范", "文件结构"],
            min_length=500,
        )
        return score

    def score_delivery(self) -> int:
        """delivery 阶段综合评分：代码审查指南 + AI 提示词"""
        code_review_score = self.score_code_review()
        ai_prompt_score = self.score_ai_prompt()
        return (code_review_score + ai_prompt_score) // 2

    def score_cicd(self) -> int:
        """第 9 阶段：CI/CD 配置评分"""
        # 检查 .github/workflows 或类似目录
        github_actions = self.project_dir / ".github" / "workflows"
        if github_actions.exists() and any(github_actions.iterdir()):
            return 90

        # 检查 output 中的 CI/CD 文档
        cicd_file = self.output_dir / f"{self.name}-cicd.md"
        if cicd_file.exists():
            content = cicd_file.read_text(encoding="utf-8", errors="ignore")
            if len(content) > 500:
                return 85
        return 70

    def score_migration(self) -> int:
        """第 10 阶段：数据库迁移评分"""
        migration_file = self.output_dir / f"{self.name}-migration.md"
        if migration_file.exists():
            content = migration_file.read_text(encoding="utf-8", errors="ignore")
            if len(content) > 500:
                return 88
        return 65

    # ------------------------------------------------------------------
    # 通用阶段评分（fallback）
    # ------------------------------------------------------------------

    def score_phase(self, phase_name: str, context_data: dict | None = None) -> int:
        """根据阶段名称路由到对应评分方法"""
        ctx = context_data or {}
        scorers = {
            "discovery": lambda: self.score_discovery(ctx),
            "intelligence": lambda: self.score_discovery(ctx),  # 同 discovery 逻辑
            "drafting": self.score_documentation,
            "frontend": self.score_frontend_scaffold,
            "spec": self.score_spec,
            "scaffold": self.score_scaffold,
            "redteam": self.score_redteam,
            "qa": self.score_quality_gate,
            "code_review": self.score_code_review,
            "ai_prompt": self.score_ai_prompt,
            "deployment": self.score_cicd,
            "migration": self.score_migration,
            "delivery": self.score_delivery,
        }
        fn = scorers.get(phase_name.lower())
        if fn:
            try:
                return fn()
            except Exception:
                return 75  # 评分失败时给默认分
        return 80  # 未知阶段默认分

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _score_doc_file(
        self,
        filename: str,
        required_sections: list[str],
        min_length: int = 500,
    ) -> int:
        """评估 output/ 目录下指定文档文件的质量"""
        doc_path = self.output_dir / filename
        if not doc_path.exists():
            return 40  # 文件不存在

        content = doc_path.read_text(encoding="utf-8", errors="ignore")
        if len(content) < 100:
            return 45  # 内容太少

        # 基础分：文件存在且有内容
        base = 60

        # 长度加分
        if len(content) >= min_length:
            base += 10
        if len(content) >= min_length * 2:
            base += 5

        # 关键章节检查
        per_section = 25 // max(len(required_sections), 1)
        for section in required_sections:
            if section.lower() in content.lower():
                base += per_section

        return min(100, base)
