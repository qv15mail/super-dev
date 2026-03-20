"""
Spec-Driven Development 数据模型

开发：Excellent（11964948@qq.com）
功能：定义 SDD 的核心数据结构
作用：Spec、Change、Proposal、Task 等模型
创建时间：2025-12-30
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChangeStatus(Enum):
    """变更状态"""
    DRAFT = "draft"           # 草稿
    PROPOSED = "proposed"     # 已提议
    APPROVED = "approved"     # 已批准
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    ARCHIVED = "archived"     # 已归档


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"       # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    SKIPPED = "skipped"       # 已跳过


class DeltaType(Enum):
    """增量类型"""
    ADDED = "added"           # 新增
    MODIFIED = "modified"     # 修改
    REMOVED = "removed"       # 删除


@dataclass
class Scenario:
    """场景 - 需求的具体场景"""
    given: str = ""           # 前置条件
    when: str = ""            # 触发事件
    then: str = ""            # 预期结果

    def to_markdown(self) -> str:
        """转换为 Markdown"""
        lines = []
        if self.given:
            lines.append(f"- GIVEN {self.given}")
        if self.when:
            lines.append(f"- WHEN {self.when}")
        if self.then:
            lines.append(f"- THEN {self.then}")
        return "\n".join(lines) if lines else "- DETAIL REQUIRED"


@dataclass
class Requirement:
    """需求 - 功能需求"""
    name: str                 # 需求名称
    description: str = ""     # 需求描述
    keyword: str = "SHALL"    # 关键词 (SHALL/MUST/SHOULD/MAY)
    scenarios: list[Scenario] = field(default_factory=list)

    def to_markdown(self, level: int = 3) -> str:
        """转换为 Markdown"""
        lines = [
            f"{'#' * level} Requirement: {self.name}",
            ""
        ]
        if self.description:
            lines.append(f"{self.keyword} {self.description}")
            lines.append("")

        if self.scenarios:
            for i, scenario in enumerate(self.scenarios, 1):
                scenario_title = scenario.when.strip() if scenario.when.strip() else f"Scenario {i}"
                lines.append(f"#### Scenario {i}: {scenario_title}")
                lines.append(scenario.to_markdown())
                lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "keyword": self.keyword,
            "scenarios": [
                {"given": s.given, "when": s.when, "then": s.then}
                for s in self.scenarios
            ],
        }


@dataclass
class Spec:
    """规范 - 功能规范文档"""
    name: str                 # 规范名称 (如 "auth", "user-profile")
    title: str = ""           # 规范标题
    purpose: str = ""         # 规范目的
    requirements: list[Requirement] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def slug(self) -> str:
        """获取 URL 友好的名称"""
        return self.name.lower().replace("_", "-").replace(" ", "-")

    def to_markdown(self) -> str:
        """转换为 Markdown"""
        lines = [
            f"# {self.title or self.name.title()}",
            ""
        ]

        if self.purpose:
            lines.extend([
                "## Purpose",
                self.purpose,
                ""
            ])

        if self.requirements:
            lines.append("## Requirements")
            lines.append("")
            for req in self.requirements:
                lines.append(req.to_markdown())

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "title": self.title,
            "purpose": self.purpose,
            "requirements": [
                {
                    "name": r.name,
                    "description": r.description,
                    "keyword": r.keyword,
                    "scenarios": [
                        {
                            "given": s.given,
                            "when": s.when,
                            "then": s.then
                        }
                        for s in r.scenarios
                    ]
                }
                for r in self.requirements
            ],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Task:
    """任务 - 实现任务"""
    id: str                   # 任务 ID (如 "1.1", "2.3")
    title: str                # 任务标题
    description: str = ""     # 任务描述
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str = ""     # 分配给谁
    dependencies: list[str] = field(default_factory=list)  # 依赖的任务 ID
    spec_refs: list[str] = field(default_factory=list)    # 引用的规范

    def to_markdown(self) -> str:
        """转换为 Markdown"""
        checkbox = {
            TaskStatus.PENDING: "[ ]",
            TaskStatus.IN_PROGRESS: "[~]",
            TaskStatus.COMPLETED: "[x]",
            TaskStatus.SKIPPED: "[_]"
        }.get(self.status, "[ ]")

        lines = [
            f"- {checkbox} **{self.id}: {self.title}**"
        ]

        if self.description:
            lines.append(f"  - {self.description}")

        if self.assigned_to:
            lines.append(f"  - Assigned to: {self.assigned_to}")

        if self.spec_refs:
            lines.append(f"  - Refs: {', '.join(f'`{r}`' for r in self.spec_refs)}")

        if self.dependencies:
            lines.append(f"  - Depends on: {', '.join(self.dependencies)}")

        return "\n".join(lines)


@dataclass
class SpecDelta:
    """规范增量 - 规范的变更"""
    spec_name: str            # 规范名称
    delta_type: DeltaType     # 增量类型
    requirements: list[Requirement] = field(default_factory=list)
    description: str = ""     # 变更说明

    def to_markdown(self) -> str:
        """转换为 Markdown"""
        lines = [
            f"## {self.delta_type.value.upper()} Requirements",
            ""
        ]

        if self.description:
            lines.extend([
                f"> {self.description}",
                ""
            ])

        for req in self.requirements:
            lines.append(req.to_markdown())

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "spec_name": self.spec_name,
            "delta_type": self.delta_type.value,
            "description": self.description,
            "requirements": [r.to_dict() for r in self.requirements]
        }


@dataclass
class Proposal:
    """提案 - 变更提案"""
    title: str                # 提案标题
    description: str          # 提案描述
    motivation: str = ""      # 动机/背景
    impact: str = ""          # 影响范围

    def to_markdown(self) -> str:
        """转换为 Markdown"""
        lines = [
            "# Proposal",
            ""
        ]

        if self.title:
            lines.extend([
                f"## {self.title}",
                ""
            ])

        if self.description:
            lines.extend([
                "## Description",
                self.description,
                ""
            ])

        if self.motivation:
            lines.extend([
                "## Motivation",
                self.motivation,
                ""
            ])

        if self.impact:
            lines.extend([
                "## Impact",
                self.impact,
                ""
            ])

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "title": self.title,
            "description": self.description,
            "motivation": self.motivation,
            "impact": self.impact
        }


@dataclass
class Change:
    """变更 - 功能变更"""
    id: str                   # 变更 ID (目录名，如 "add-user-auth")
    title: str                # 变更标题
    status: ChangeStatus = ChangeStatus.DRAFT
    proposal: Proposal | None = None
    tasks: list[Task] = field(default_factory=list)
    spec_deltas: list[SpecDelta] = field(default_factory=list)
    design_notes: str = ""    # 设计笔记 (可选)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def is_completed(self) -> bool:
        """是否所有任务都已完成"""
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)

    @property
    def completion_rate(self) -> float:
        """完成率 (0-100)"""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(self.tasks)) * 100

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "status": t.status.value,
                    "assigned_to": t.assigned_to,
                    "dependencies": t.dependencies,
                    "spec_refs": t.spec_refs
                }
                for t in self.tasks
            ],
            "spec_deltas": [d.to_dict() for d in self.spec_deltas],
            "design_notes": self.design_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_completed": self.is_completed,
            "completion_rate": self.completion_rate
        }

    def get_task_by_id(self, task_id: str) -> Task | None:
        """根据 ID 获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
