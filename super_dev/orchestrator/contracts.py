"""
Pipeline contract report.

记录流水线阶段的输入输出工件，便于审计和复盘。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StageContract:
    stage: str
    title: str
    success: bool
    duration_seconds: float
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "title": self.title,
            "success": self.success,
            "duration_seconds": round(self.duration_seconds, 3),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "notes": self.notes,
        }


@dataclass
class PipelineContractReport:
    project_name: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str = ""
    success: bool = True
    failure_reason: str = ""
    stages: list[StageContract] = field(default_factory=list)

    def record_stage(
        self,
        *,
        stage: str,
        title: str,
        success: bool,
        duration_seconds: float,
        inputs: list[str] | None = None,
        outputs: list[str] | None = None,
        notes: list[str] | None = None,
    ) -> None:
        self.stages.append(
            StageContract(
                stage=stage,
                title=title,
                success=success,
                duration_seconds=duration_seconds,
                inputs=inputs or [],
                outputs=outputs or [],
                notes=notes or [],
            )
        )

    def finalize(self, success: bool, failure_reason: str = "") -> None:
        self.success = success
        self.failure_reason = failure_reason
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "stages": [stage.to_dict() for stage in self.stages],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Pipeline Contract",
            "",
            f"- Project: `{self.project_name}`",
            f"- Started at (UTC): {self.started_at}",
            f"- Finished at (UTC): {self.finished_at or '(running)'}",
            f"- Success: {'yes' if self.success else 'no'}",
        ]
        if self.failure_reason:
            lines.append(f"- Failure reason: {self.failure_reason}")
        lines.extend(["", "## Stage Evidence", ""])
        lines.extend(
            ["| Stage | Name | Status | Inputs | Outputs |", "|:---|:---|:---:|:---|:---|"]
        )
        for stage in self.stages:
            status = "PASS" if stage.success else "FAIL"
            input_text = "<br/>".join(stage.inputs) if stage.inputs else "-"
            output_text = "<br/>".join(stage.outputs) if stage.outputs else "-"
            lines.append(
                f"| {stage.stage} | {stage.title} | {status} | {input_text} | {output_text} |"
            )
        lines.append("")
        return "\n".join(lines)

    def write(self, output_dir: Path) -> dict[str, Path]:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / f"{self.project_name}-pipeline-contract.json"
        md_file = output_dir / f"{self.project_name}-pipeline-contract.md"
        json_file.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        md_file.write_text(self.to_markdown(), encoding="utf-8")
        return {"json": json_file, "markdown": md_file}
