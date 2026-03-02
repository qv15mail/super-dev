"""
Spec-Driven Development 生成器

开发：Excellent（11964948@qq.com）
功能：从需求或 PRD 自动生成规范和变更提案
作用：辅助用户快速创建 SDD 文档
创建时间：2025-12-30
"""

from pathlib import Path

from .manager import ChangeManager, SpecManager
from .models import (
    Change,
    ChangeStatus,
    DeltaType,
    Proposal,
    Requirement,
    Scenario,
    SpecDelta,
    Task,
    TaskStatus,
)


class SpecGenerator:
    """规范生成器 - 从需求自动生成规范"""

    def __init__(self, project_dir: Path | str):
        """初始化生成器"""
        self.project_dir = Path(project_dir).resolve()
        self.spec_manager = SpecManager(self.project_dir)
        self.change_manager = ChangeManager(self.project_dir)

    def create_change(
        self,
        change_id: str,
        title: str,
        description: str,
        motivation: str = "",
        impact: str = ""
    ) -> Change:
        """创建新变更提案"""
        change = Change(
            id=change_id,
            title=title,
            status=ChangeStatus.PROPOSED,
            proposal=Proposal(
                title=title,
                description=description,
                motivation=motivation,
                impact=impact
            )
        )
        self.change_manager.save_change(change)
        return change

    def add_requirement_to_change(
        self,
        change_id: str,
        spec_name: str,
        requirement_name: str,
        description: str,
        scenarios: list[dict] | None = None,
        delta_type: DeltaType = DeltaType.ADDED
    ) -> SpecDelta:
        """向变更添加需求"""
        change = self.change_manager.load_change(change_id)
        if not change:
            raise FileNotFoundError(f"变更不存在: {change_id}")

        # 创建场景
        req_scenarios = []
        if scenarios:
            for s in scenarios:
                req_scenarios.append(Scenario(
                    given=s.get("given", ""),
                    when=s.get("when", ""),
                    then=s.get("then", "")
                ))

        requirement = Requirement(
            name=requirement_name,
            description=description,
            keyword="SHALL"
        )
        requirement.scenarios = req_scenarios

        # 查找或创建增量
        for delta in change.spec_deltas:
            if delta.spec_name == spec_name:
                delta.requirements.append(requirement)
                break
        else:
            delta = SpecDelta(
                spec_name=spec_name,
                delta_type=delta_type,
                requirements=[requirement]
            )
            change.spec_deltas.append(delta)

        self.change_manager.save_change(change)
        return delta

    def generate_tasks_from_requirements(
        self,
        change_id: str,
        tech_stack: dict | None = None
    ) -> list[Task]:
        """从需求自动生成任务"""
        change = self.change_manager.load_change(change_id)
        if not change:
            raise FileNotFoundError(f"变更不存在: {change_id}")

        tasks = []
        task_id = [1, 1]  # [major, minor]

        # 根据规范增量生成任务
        for delta in change.spec_deltas:
            for req in delta.requirements:
                # 为每个需求生成实现任务
                task_id[1] += 1
                task = Task(
                    id=f"{task_id[0]}.{task_id[1]}",
                    title=f"Implement: {req.name}",
                    description=req.description,
                    status=TaskStatus.PENDING,
                    spec_refs=[f"{delta.spec_name}::{req.name}"]
                )
                tasks.append(task)

        # 添加测试任务
        task_id[0] += 1
        task_id[1] = 0
        for delta in change.spec_deltas:
            task_id[1] += 1
            task = Task(
                id=f"{task_id[0]}.{task_id[1]}",
                title=f"Test: {delta.spec_name} requirements",
                description=f"Verify all scenarios for {delta.spec_name}",
                status=TaskStatus.PENDING,
                spec_refs=[delta.spec_name]
            )
            tasks.append(task)

        # 更新变更
        change.tasks = tasks
        self.change_manager.save_change(change)

        return tasks

    def propose_from_prd(self, prd_content: str) -> Change:
        """从 PRD 内容生成变更提案 (简化版)"""
        # 解析 PRD 提取关键信息
        lines = prd_content.split("\n")

        title = "Feature from PRD"
        description = ""
        features = []

        current_section = None
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## 概述") or line.startswith("## Overview"):
                current_section = "overview"
            elif line.startswith("## 功能需求") or line.startswith("## Features"):
                current_section = "features"
            elif line.startswith("- ") or line.startswith("* "):
                if current_section == "features":
                    features.append(line[2:].strip())
            elif current_section == "overview" and line.strip():
                description += line.strip() + "\n"

        # 创建变更 ID
        change_id = title.lower().replace(" ", "-").replace("/", "-")[:50]

        change = self.create_change(
            change_id=change_id,
            title=title,
            description=description.strip(),
            motivation="Derived from PRD",
            impact=", ".join(features[:3])
        )

        return change

    def init_sdd(self):
        """初始化 SDD 目录结构"""
        self.spec_manager.init()
        self.change_manager.init()

        # 创建 AGENTS.md 文件
        agents_path = self.project_dir / ".super-dev" / "AGENTS.md"
        if not agents_path.exists():
            agents_content = """# Super Dev Spec-Driven Development

This project uses Super Dev's Spec-Driven Development (SDD) workflow.

## Workflow

1. **Propose**: Create a change proposal with `super-dev spec propose <id>`
2. **Review**: Review the generated specs and tasks
3. **Implement**: Work through the tasks with AI assistance
4. **Archive**: Archive the change with `super-dev spec archive <id>`

## Directory Structure

```
.super-dev/
├── specs/          # Current specifications (source of truth)
├── changes/        # Proposed changes (proposals + tasks + deltas)
└── archive/        # Archived changes
```

## Commands

- `super-dev spec list` - List all changes
- `super-dev spec show <id>` - Show change details
- `super-dev spec propose <id>` - Create new change proposal
- `super-dev spec apply <id>` - Start implementing a change
- `super-dev spec archive <id>` - Archive completed change

## AI Integration

When working with AI coding assistants, reference the change:

"Please help me implement change `add-user-auth`. The tasks are in `.super-dev/changes/add-user-auth/tasks.md` and the specs are in `.super-dev/changes/add-user-auth/specs/`."
"""
            agents_path.write_text(agents_content, encoding="utf-8")

        # 创建 project.md 模板
        project_path = self.project_dir / ".super-dev" / "project.md"
        if not project_path.exists():
            project_content = """# Project Context

## Purpose
_What is this project about?_

## Tech Stack
- **Language**: _e.g., Python, JavaScript, Go_
- **Framework**: _e.g., FastAPI, Express, Gin_
- **Database**: _e.g., PostgreSQL, MongoDB_
- **Frontend**: _e.g., React, Vue, None_

## Conventions
### Code Style
- _e.g., PEP 8 for Python, ESLint + Prettier for JS_

### Git Flow
- _e.g., main for production, develop for integration_

### Testing
- _e.g., pytest with >80% coverage required_

## Architecture Notes
_Add architectural patterns and decisions here_

## Domain Knowledge
_Add domain-specific information here_
"""
            project_path.write_text(project_content, encoding="utf-8")

        return agents_path, project_path
