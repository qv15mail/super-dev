"""
Spec-Driven Development 管理器

开发：Excellent（11964948@qq.com）
功能：管理规范和变更的文件读写
作用：处理 specs/ 和 changes/ 目录的文件操作
创建时间：2025-12-30
"""

import re
from datetime import datetime, timezone
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from .models import (
    Change,
    ChangeStatus,
    DeltaType,
    Proposal,
    Requirement,
    Scenario,
    Spec,
    SpecDelta,
    Task,
    TaskStatus,
)


class SpecManager:
    """规范管理器 - 管理当前规范 (specs/)"""

    def __init__(self, project_dir: Path | str):
        """初始化规范管理器"""
        self.project_dir = Path(project_dir).resolve()
        self.specs_dir = self.project_dir / ".super-dev" / "specs"

    def init(self):
        """初始化规范目录"""
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        (self.specs_dir / ".gitkeep").touch()

    def get_spec_path(self, spec_name: str) -> Path:
        """获取规范文件路径"""
        resolved = (self.specs_dir / spec_name / "spec.md").resolve()
        if not str(resolved).startswith(str(self.specs_dir.resolve())):
            raise ValueError(f"Invalid spec name: {spec_name}")
        return self.specs_dir / spec_name / "spec.md"

    def load_spec(self, spec_name: str) -> Spec | None:
        """加载规范"""
        spec_path = self.get_spec_path(spec_name)
        if not spec_path.exists():
            return None

        content = spec_path.read_text(encoding="utf-8")
        return self._parse_spec(spec_name, content)

    def save_spec(self, spec: Spec):
        """保存规范"""
        spec_path = self.get_spec_path(spec.name)
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec.updated_at = datetime.now(timezone.utc)
        spec_path.write_text(spec.to_markdown(), encoding="utf-8")

    def list_specs(self) -> list[str]:
        """列出所有规范"""
        if not self.specs_dir.exists():
            return []
        return [
            d.name for d in self.specs_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    def delete_spec(self, spec_name: str):
        """删除规范"""
        import shutil
        spec_path = self.get_spec_path(spec_name)
        if spec_path.exists():
            shutil.rmtree(spec_path.parent)

    def _parse_spec(self, spec_name: str, content: str) -> Spec:
        """从 Markdown 解析规范"""
        lines = content.split("\n")

        spec = Spec(name=spec_name)
        current_section = None
        current_req = None

        for line in lines:
            # 解析标题
            if line.startswith("# "):
                spec.title = line[2:].strip()
            elif line.startswith("## Purpose"):
                current_section = "purpose"
            elif line.startswith("## Requirements"):
                current_section = "requirements"
            elif line.startswith("### Requirement:"):
                if current_req:
                    spec.requirements.append(current_req)
                current_req = Requirement(name=line[16:].strip())
                current_section = "requirement"
            elif line.startswith("#### Scenario"):
                if current_req:
                    scenario = Scenario(when=line.split(":", 1)[-1].strip() if ":" in line else "")
                    current_req.scenarios.append(scenario)
            elif current_section == "purpose" and line.strip():
                spec.purpose += line.strip() + "\n"
            elif current_section == "requirement" and current_req:
                if line.strip().startswith(("SHALL", "MUST", "SHOULD", "MAY")):
                    parts = line.strip().split(" ", 1)
                    current_req.keyword = parts[0]
                    current_req.description = parts[1] if len(parts) > 1 else ""
                elif line.startswith("- GIVEN"):
                    if current_req.scenarios:
                        current_req.scenarios[-1].given = line[7:].strip()
                elif line.startswith("- WHEN"):
                    if current_req.scenarios:
                        current_req.scenarios[-1].when = line[6:].strip()
                elif line.startswith("- THEN"):
                    if current_req.scenarios:
                        current_req.scenarios[-1].then = line[6:].strip()

        if current_req:
            spec.requirements.append(current_req)

        spec.purpose = spec.purpose.strip()
        return spec


class ChangeManager:
    """变更管理器 - 管理变更提案 (changes/)"""

    def __init__(self, project_dir: Path | str):
        """初始化变更管理器"""
        self.project_dir = Path(project_dir).resolve()
        self.changes_dir = self.project_dir / ".super-dev" / "changes"

    def init(self):
        """初始化变更目录"""
        self.changes_dir.mkdir(parents=True, exist_ok=True)
        (self.changes_dir / ".gitkeep").touch()

    def get_change_path(self, change_id: str) -> Path:
        """获取变更目录路径"""
        resolved = (self.changes_dir / change_id).resolve()
        if not str(resolved).startswith(str(self.changes_dir.resolve())):
            raise ValueError(f"Invalid change ID: {change_id}")
        return self.changes_dir / change_id

    def load_change(self, change_id: str) -> Change | None:
        """加载变更"""
        change_path = self.get_change_path(change_id)
        if not change_path.exists():
            return None

        change = Change(id=change_id, title=change_id.replace("-", " ").title())

        # 加载元数据
        meta_path = change_path / "change.yaml"
        if meta_path.exists():
            with open(meta_path, encoding="utf-8") as f:
                metadata = yaml.safe_load(f) or {}
            title = metadata.get("title")
            if isinstance(title, str) and title.strip():
                change.title = title.strip()

            raw_status = str(metadata.get("status", "")).strip().lower()
            for status in ChangeStatus:
                if status.value == raw_status:
                    change.status = status
                    break

            created_at = metadata.get("created_at")
            if isinstance(created_at, str):
                try:
                    change.created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    pass
            updated_at = metadata.get("updated_at")
            if isinstance(updated_at, str):
                try:
                    change.updated_at = datetime.fromisoformat(updated_at)
                except ValueError:
                    pass

        # 加载提案
        proposal_path = change_path / "proposal.md"
        if proposal_path.exists():
            change.proposal = self._parse_proposal(proposal_path.read_text(encoding="utf-8"))

        # 加载任务
        tasks_path = change_path / "tasks.md"
        if tasks_path.exists():
            change.tasks = self._parse_tasks(tasks_path.read_text(encoding="utf-8"))

        # 加载设计笔记
        design_path = change_path / "design.md"
        if design_path.exists():
            change.design_notes = design_path.read_text(encoding="utf-8")

        # 加载规范增量
        specs_deltas_dir = change_path / "specs"
        if specs_deltas_dir.exists():
            change.spec_deltas = self._parse_spec_deltas(specs_deltas_dir)

        return change

    def save_change(self, change: Change):
        """保存变更"""
        change_path = self.get_change_path(change.id)
        change_path.mkdir(parents=True, exist_ok=True)
        change.updated_at = datetime.now(timezone.utc)

        # 保存提案
        if change.proposal:
            proposal_path = change_path / "proposal.md"
            proposal_path.write_text(change.proposal.to_markdown(), encoding="utf-8")

        # 保存任务
        tasks_path = change_path / "tasks.md"
        tasks_path.write_text(self._format_tasks(change.tasks), encoding="utf-8")

        # 保存设计笔记
        if change.design_notes:
            design_path = change_path / "design.md"
            design_path.write_text(change.design_notes, encoding="utf-8")

        # 保存规范增量
        if change.spec_deltas:
            for delta in change.spec_deltas:
                delta_path = change_path / "specs" / delta.spec_name / "spec.md"
                delta_path.parent.mkdir(parents=True, exist_ok=True)
                delta_path.write_text(delta.to_markdown(), encoding="utf-8")

        # 保存元数据
        meta_path = change_path / "change.yaml"
        with open(meta_path, "w", encoding="utf-8") as f:
            yaml.dump({
                "id": change.id,
                "title": change.title,
                "status": change.status.value,
                "created_at": change.created_at.isoformat(),
                "updated_at": change.updated_at.isoformat()
            }, f, allow_unicode=True)

    def list_changes(self, status: ChangeStatus | None = None) -> list[Change]:
        """列出所有变更"""
        if not self.changes_dir.exists():
            return []

        changes = []
        for d in self.changes_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                change = self.load_change(d.name)
                if change and (status is None or change.status == status):
                    changes.append(change)

        return sorted(changes, key=lambda c: self._normalize_datetime(c.created_at), reverse=True)

    def delete_change(self, change_id: str):
        """删除变更"""
        change_path = self.get_change_path(change_id)
        if change_path.exists():
            import shutil
            shutil.rmtree(change_path)

    def archive_change(self, change_id: str, spec_manager: SpecManager):
        """归档变更 - 将规范增量合并到主规范"""
        change = self.load_change(change_id)
        if not change:
            raise FileNotFoundError(f"变更不存在: {change_id}")

        # 合并规范增量
        for delta in change.spec_deltas:
            spec = spec_manager.load_spec(delta.spec_name)
            if not spec:
                spec = Spec(name=delta.spec_name, title=delta.spec_name.replace("-", " ").title())

            if delta.delta_type == DeltaType.ADDED:
                spec.requirements.extend(delta.requirements)
            elif delta.delta_type == DeltaType.MODIFIED:
                # 替换同名需求
                for new_req in delta.requirements:
                    for i, existing_req in enumerate(spec.requirements):
                        if existing_req.name == new_req.name:
                            spec.requirements[i] = new_req
                            break
                    else:
                        spec.requirements.append(new_req)
            elif delta.delta_type == DeltaType.REMOVED:
                # 移除指定需求
                spec.requirements = [
                    r for r in spec.requirements
                    if r.name not in {req.name for req in delta.requirements}
                ]

            spec_manager.save_spec(spec)

        # 更新状态并保存，然后移动到归档
        change.status = ChangeStatus.ARCHIVED
        self.save_change(change)

        archive_dir = self.changes_dir.parent / "archive" / change_id
        archive_dir.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.move(str(self.get_change_path(change_id)), str(archive_dir))

        return change

    def _parse_proposal(self, content: str) -> Proposal:
        """解析提案"""
        lines = content.split("\n")
        proposal = Proposal(title="", description="")

        current_section = None
        for line in lines:
            if line.startswith("## "):
                current_section = line[3:].lower()
            elif current_section == "description" and line.strip():
                proposal.description += line.strip() + "\n"
            elif current_section == "motivation" and line.strip():
                proposal.motivation += line.strip() + "\n"
            elif current_section == "impact" and line.strip():
                proposal.impact += line.strip() + "\n"
            elif line.startswith("# ") and not proposal.title:
                proposal.title = line[2:].strip()

        proposal.description = proposal.description.strip()
        proposal.motivation = proposal.motivation.strip()
        proposal.impact = proposal.impact.strip()
        return proposal


    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _parse_tasks(self, content: str) -> list[Task]:
        """解析任务"""
        tasks: list[Task] = []
        current_task: Task | None = None
        task_pattern = re.compile(
            r"^-\s*\[(?P<marker>[ xX~_])\]\s+\*\*(?P<id>[^:]+):\s*(?P<title>.*?)\*\*\s*$"
        )
        fallback_pattern = re.compile(
            r"^-\s*\[(?P<marker>[ xX~_])\]\s+(?P<id>\d+(?:\.\d+)*)\s*:?\s*(?P<title>.+)$"
        )

        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            task_match = task_pattern.match(stripped) or fallback_pattern.match(stripped)
            if task_match:
                if current_task:
                    tasks.append(current_task)
                marker = task_match.group("marker")
                status = {
                    " ": TaskStatus.PENDING,
                    "~": TaskStatus.IN_PROGRESS,
                    "x": TaskStatus.COMPLETED,
                    "X": TaskStatus.COMPLETED,
                    "_": TaskStatus.SKIPPED,
                }.get(marker, TaskStatus.PENDING)
                current_task = Task(
                    id=task_match.group("id").strip(),
                    title=task_match.group("title").strip(),
                    status=status,
                )
                continue

            if current_task is None or not stripped.startswith("-"):
                continue

            detail = stripped[1:].strip()
            detail_lower = detail.lower()
            if detail_lower.startswith("refs:"):
                refs_part = detail.split(":", 1)[1].strip() if ":" in detail else ""
                refs = [
                    token.strip().strip("`")
                    for token in refs_part.split(",")
                    if token.strip().strip("`")
                ]
                current_task.spec_refs = refs
                continue

            if detail_lower.startswith("depends on:"):
                depends_part = detail.split(":", 1)[1].strip() if ":" in detail else ""
                dependencies = [token.strip() for token in depends_part.split(",") if token.strip()]
                current_task.dependencies = dependencies
                continue

            if detail_lower.startswith("assigned to:"):
                current_task.assigned_to = detail.split(":", 1)[1].strip() if ":" in detail else ""
                continue

            if current_task.description:
                current_task.description = f"{current_task.description}\n{detail}"
            else:
                current_task.description = detail

        if current_task:
            tasks.append(current_task)

        return tasks

    def _format_tasks(self, tasks: list[Task]) -> str:
        """格式化任务为 Markdown"""
        lines = ["# Tasks", ""]
        groups: dict[str, list[Task]] = {}
        for task in tasks:
            group = task.id.split(".")[0]
            if group not in groups:
                groups[group] = []
            groups[group].append(task)

        def _group_sort_key(value: str) -> tuple[int, int | str]:
            if value.isdigit():
                return (0, int(value))
            return (1, value)

        for group in sorted(groups.keys(), key=_group_sort_key):
            group_name = {
                "1": "1. Planning",
                "2": "2. Frontend",
                "3": "3. Backend",
                "4": "4. Integration & Quality",
                "5": "5. Testing",
                "6": "6. Documentation",
            }.get(group, f"{group}. Other")
            lines.append(f"## {group_name}")
            lines.append("")
            for task in groups[group]:
                lines.append(task.to_markdown())
            lines.append("")

        return "\n".join(lines)

    def _parse_spec_deltas(self, specs_dir: Path) -> list[SpecDelta]:
        """解析规范增量"""
        deltas = []
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir():
                spec_path = spec_dir / "spec.md"
                if spec_path.exists():
                    content = spec_path.read_text(encoding="utf-8")
                    # 解析增量类型
                    delta_type = DeltaType.ADDED
                    for line in content.split("\n"):
                        if line.startswith("## ADDED"):
                            delta_type = DeltaType.ADDED
                            break
                        elif line.startswith("## MODIFIED"):
                            delta_type = DeltaType.MODIFIED
                            break
                        elif line.startswith("## REMOVED"):
                            delta_type = DeltaType.REMOVED
                            break

                    requirements: list[Requirement] = []
                    current_req: Requirement | None = None
                    current_scenario: Scenario | None = None

                    for raw_line in content.split("\n"):
                        line = raw_line.strip()
                        if line.startswith("### Requirement:"):
                            if current_req:
                                requirements.append(current_req)
                            req_name = line[len("### Requirement:"):].strip()
                            current_req = Requirement(name=req_name)
                            current_scenario = None
                            continue

                        if current_req is None:
                            continue

                        if line.startswith(("SHALL ", "MUST ", "SHOULD ", "MAY ")):
                            parts = line.split(" ", 1)
                            current_req.keyword = parts[0]
                            current_req.description = parts[1] if len(parts) > 1 else ""
                            continue

                        if line.startswith("#### Scenario"):
                            current_scenario = Scenario()
                            current_req.scenarios.append(current_scenario)
                            continue

                        if line.startswith("- GIVEN"):
                            if current_scenario is None:
                                current_scenario = Scenario()
                                current_req.scenarios.append(current_scenario)
                            current_scenario.given = line[len("- GIVEN"):].strip()
                            continue

                        if line.startswith("- WHEN"):
                            if current_scenario is None:
                                current_scenario = Scenario()
                                current_req.scenarios.append(current_scenario)
                            current_scenario.when = line[len("- WHEN"):].strip()
                            continue

                        if line.startswith("- THEN"):
                            if current_scenario is None:
                                current_scenario = Scenario()
                                current_req.scenarios.append(current_scenario)
                            current_scenario.then = line[len("- THEN"):].strip()
                            continue

                    if current_req:
                        requirements.append(current_req)

                    deltas.append(SpecDelta(
                        spec_name=spec_dir.name,
                        delta_type=delta_type,
                        description="",
                        requirements=requirements
                    ))

        return deltas
