"""
Spec-Driven Development 验证器

开发：Excellent（11964948@qq.com）
功能：验证规格格式和结构
作用：检查 spec.md 和 change 的格式是否符合规范标准
创建时间：2025-12-30
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationError:
    """验证错误"""
    file: str                  # 文件路径
    line: int = 0              # 行号
    column: int = 0            # 列号
    message: str = ""          # 错误消息
    severity: str = "error"    # 严重程度: error, warning, info


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    info: list[ValidationError] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        """总问题数"""
        return len(self.errors) + len(self.warnings)

    def to_summary(self) -> str:
        """生成摘要报告"""
        lines = []
        if self.is_valid:
            lines.append("[通过] 规格格式验证通过")
        else:
            lines.append(f"[失败] 发现 {len(self.errors)} 个错误")

        if self.warnings:
            lines.append(f"[警告] {len(self.warnings)} 个警告")

        return "\n".join(lines)


class SpecValidator:
    """规格验证器"""

    # 规范需求关键词
    REQUIREMENT_KEYWORDS = ["SHALL", "MUST", "SHOULD", "MAY"]

    # Delta 类型
    DELTA_TYPES = ["ADDED", "MODIFIED", "REMOVED"]

    def __init__(self, project_dir: Path | str):
        """初始化验证器"""
        self.project_dir = Path(project_dir).resolve()
        self.specs_dir = self.project_dir / ".super-dev" / "specs"
        self.changes_dir = self.project_dir / ".super-dev" / "changes"

    def validate_change(self, change_id: str) -> ValidationResult:
        """验证变更"""
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        info: list[ValidationError] = []

        change_dir = self.changes_dir / change_id
        if not change_dir.exists():
            errors.append(ValidationError(
                file=str(change_dir),
                message=f"变更目录不存在: {change_id}"
            ))
            return ValidationResult(is_valid=False, errors=errors)

        # 验证 proposal.md
        proposal_file = change_dir / "proposal.md"
        if proposal_file.exists():
            result = self._validate_proposal(proposal_file)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
            info.extend(result.info)
        else:
            warnings.append(ValidationError(
                file=str(proposal_file),
                message="缺少 proposal.md"
            ))

        # 验证 tasks.md
        tasks_file = change_dir / "tasks.md"
        if tasks_file.exists():
            result = self._validate_tasks(tasks_file)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
            info.extend(result.info)
        else:
            warnings.append(ValidationError(
                file=str(tasks_file),
                message="缺少 tasks.md"
            ))

        # 验证 design.md (可选)
        design_file = change_dir / "design.md"
        if design_file.exists():
            result = self._validate_design(design_file)
            errors.extend(result.errors)
            warnings.extend(result.warnings)

        # 验证 specs/ 目录
        specs_dir = change_dir / "specs"
        if specs_dir.exists():
            for spec_file in specs_dir.rglob("spec.md"):
                result = self._validate_spec_delta(spec_file)
                errors.extend(result.errors)
                warnings.extend(result.warnings)
                info.extend(result.info)
        else:
            warnings.append(ValidationError(
                file=str(specs_dir),
                message="缺少 specs/ 目录"
            ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info
        )

    def validate_spec(self, spec_name: str) -> ValidationResult:
        """验证规范"""
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        spec_file = self.specs_dir / spec_name / "spec.md"
        if not spec_file.exists():
            errors.append(ValidationError(
                file=str(spec_file),
                message=f"规范文件不存在: {spec_name}"
            ))
            return ValidationResult(is_valid=False, errors=errors)

        content = spec_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # 检查标题
        has_title = False
        has_purpose = False
        has_requirements = False
        has_req_keyword = False

        for i, line in enumerate(lines, 1):
            # 检查一级标题
            if line.startswith("# ") and not has_title:
                has_title = True
                if not line[2:].strip():
                    errors.append(ValidationError(
                        file=str(spec_file),
                        line=i,
                        message="标题不能为空"
                    ))

            # 检查 Purpose 部分
            if line.startswith("## Purpose"):
                has_purpose = True

            # 检查 Requirements 部分
            if line.startswith("## Requirements"):
                has_requirements = True

            # 检查需求格式
            if line.startswith("### Requirement:"):
                has_req_keyword = True
                if not line[16:].strip():
                    errors.append(ValidationError(
                        file=str(spec_file),
                        line=i,
                        message="需求名称不能为空"
                    ))

            # 检查需求关键词
            if any(kw in line for kw in self.REQUIREMENT_KEYWORDS):
                has_req_keyword = True

            # 检查场景格式
            if line.startswith("#### Scenario:"):
                if not line[14:].strip():
                    warnings.append(ValidationError(
                        file=str(spec_file),
                        line=i,
                        severity="warning",
                        message="场景描述为空"
                    ))

        # 验证结果
        if not has_title:
            errors.append(ValidationError(
                file=str(spec_file),
                message="缺少一级标题"
            ))

        if not has_purpose:
            warnings.append(ValidationError(
                file=str(spec_file),
                severity="warning",
                message="缺少 Purpose 部分"
            ))

        if not has_requirements:
            warnings.append(ValidationError(
                file=str(spec_file),
                severity="warning",
                message="缺少 Requirements 部分"
            ))

        if not has_req_keyword:
            warnings.append(ValidationError(
                file=str(spec_file),
                severity="info",
                message="建议使用 SHALL/MUST/SHOULD/MAY 关键词"
            ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_proposal(self, proposal_file: Path) -> ValidationResult:
        """验证提案文件"""
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        content = proposal_file.read_text(encoding="utf-8")

        # 检查必需的章节
        has_title = False
        has_description = False

        for line in content.split("\n"):
            if re.match(r"^##\s+", line):
                if "description" in line.lower():
                    has_description = True
                elif "title" in line.lower() or line.startswith("# "):
                    has_title = True

        if not has_title:
            warnings.append(ValidationError(
                file=str(proposal_file),
                severity="warning",
                message="提案缺少标题"
            ))

        if not has_description:
            warnings.append(ValidationError(
                file=str(proposal_file),
                severity="warning",
                message="提案缺少描述"
            ))

        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings
        )

    def _validate_tasks(self, tasks_file: Path) -> ValidationResult:
        """验证任务文件"""
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        content = tasks_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        task_pattern = re.compile(r'^-\s*\[([ x~_])\]\s*\*\*([\d.]+):\s*([^*]+)\*\*')

        task_ids = []
        for i, line in enumerate(lines, 1):
            match = task_pattern.match(line)
            if match:
                status_char, task_id, title = match.groups()
                task_ids.append(task_id)

                # 检查任务标题
                if not title.strip():
                    errors.append(ValidationError(
                        file=str(tasks_file),
                        line=i,
                        message="任务标题不能为空"
                    ))

        # 检查任务ID格式
        for task_id in task_ids:
            if not re.match(r"^\d+\.\d+$", task_id):
                warnings.append(ValidationError(
                    file=str(tasks_file),
                    severity="warning",
                    message=f"任务ID格式建议为 '数字.数字' 格式: {task_id}"
                ))

        if not task_ids:
            warnings.append(ValidationError(
                file=str(tasks_file),
                severity="warning",
                message="没有找到任何任务"
            ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_design(self, design_file: Path) -> ValidationResult:
        """验证设计文件"""
        # design.md 是可选的，只做基本检查
        content = design_file.read_text(encoding="utf-8")
        if len(content) < 10:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    file=str(design_file),
                    message="设计文件内容过少"
                )]
            )
        return ValidationResult(is_valid=True)

    def _validate_spec_delta(self, spec_file: Path) -> ValidationResult:
        """验证规范增量文件"""
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        content = spec_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        has_delta_header = False
        current_delta_type = None
        has_requirements = False

        for i, line in enumerate(lines, 1):
            # 检查 Delta 类型标题
            if line.startswith("## "):
                for delta_type in self.DELTA_TYPES:
                    if delta_type in line.upper():
                        has_delta_header = True
                        current_delta_type = delta_type
                        break

            # 检查需求格式
            if line.startswith("### Requirement:"):
                if not current_delta_type:
                    errors.append(ValidationError(
                        file=str(spec_file),
                        line=i,
                        message="需求必须在 Delta 类型 (ADDED/MODIFIED/REMOVED) 下"
                    ))

                has_requirements = True

                if not line[16:].strip():
                    errors.append(ValidationError(
                        file=str(spec_file),
                        line=i,
                        message="需求名称不能为空"
                    ))

        if not has_delta_header:
            errors.append(ValidationError(
                file=str(spec_file),
                message="缺少 Delta 类型标题 (ADDED/MODIFIED/REMOVED)"
            ))

        if not has_requirements:
            warnings.append(ValidationError(
                file=str(spec_file),
                severity="warning",
                message="没有找到任何需求"
            ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_all(self) -> ValidationResult:
        """验证所有变更"""
        all_errors: list[ValidationError] = []
        all_warnings: list[ValidationError] = []

        if not self.changes_dir.exists():
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    file=str(self.changes_dir),
                    message="changes 目录不存在，请先运行 'super-dev spec init'"
                )]
            )

        for change_dir in self.changes_dir.iterdir():
            if change_dir.is_dir() and not change_dir.name.startswith("."):
                result = self.validate_change(change_dir.name)
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )
