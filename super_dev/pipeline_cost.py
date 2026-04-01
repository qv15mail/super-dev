"""
Pipeline 执行成本追踪 — 记录每个阶段的耗时和资源消耗。

用于在 pipeline 执行过程中收集各阶段的性能指标，
包括耗时、文件读写数、命令执行数等，并支持持久化到 .super-dev/metrics/。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class PhaseCost:
    """单阶段成本记录。"""

    phase: str
    duration_seconds: float = 0.0
    files_read: int = 0
    files_written: int = 0
    commands_executed: int = 0
    started_at: str = ""
    completed_at: str = ""


@dataclass
class PipelineCost:
    """整条 pipeline 的成本汇总。"""

    phases: dict[str, PhaseCost] = field(default_factory=dict)
    total_duration: float = 0.0
    started_at: str = ""
    completed_at: str = ""


class PipelineCostTracker:
    """Pipeline 执行成本追踪器。

    调用 ``start_phase`` / ``end_phase`` 包裹每个阶段的执行，
    最后通过 ``get_summary`` 获取汇总或 ``save`` 持久化。
    """

    def __init__(self) -> None:
        self._phases: dict[str, PhaseCost] = {}
        self._pipeline_started_at: str = ""
        self._active_starts: dict[str, datetime] = {}

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def start_pipeline(self) -> None:
        """标记 pipeline 执行开始。"""
        self._pipeline_started_at = datetime.now(timezone.utc).isoformat()

    def start_phase(self, phase: str) -> None:
        """记录某阶段开始。"""
        now = datetime.now(timezone.utc)
        self._active_starts[phase] = now
        if phase not in self._phases:
            self._phases[phase] = PhaseCost(phase=phase, started_at=now.isoformat())
        else:
            self._phases[phase].started_at = now.isoformat()

    def end_phase(
        self,
        phase: str,
        *,
        files_read: int = 0,
        files_written: int = 0,
        commands_executed: int = 0,
    ) -> None:
        """记录某阶段结束，附带可选指标。"""
        now = datetime.now(timezone.utc)
        start = self._active_starts.pop(phase, None)
        duration = (now - start).total_seconds() if start else 0.0

        if phase not in self._phases:
            self._phases[phase] = PhaseCost(phase=phase)

        cost = self._phases[phase]
        cost.duration_seconds = duration
        cost.completed_at = now.isoformat()
        cost.files_read = files_read
        cost.files_written = files_written
        cost.commands_executed = commands_executed

    def get_summary(self) -> PipelineCost:
        """返回当前汇总。"""
        total = sum(c.duration_seconds for c in self._phases.values())
        completed_at = ""
        if self._phases:
            last_completed = max(
                (c.completed_at for c in self._phases.values() if c.completed_at),
                default="",
            )
            completed_at = last_completed
        return PipelineCost(
            phases=dict(self._phases),
            total_duration=total,
            started_at=self._pipeline_started_at,
            completed_at=completed_at,
        )

    def save(self, project_dir: Path) -> Path:
        """持久化到 .super-dev/metrics/pipeline-cost.json，返回文件路径。"""
        metrics_dir = project_dir / ".super-dev" / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        out_path = metrics_dir / "pipeline-cost.json"

        summary = self.get_summary()
        payload = {
            "started_at": summary.started_at,
            "completed_at": summary.completed_at,
            "total_duration": round(summary.total_duration, 3),
            "phases": {name: asdict(cost) for name, cost in summary.phases.items()},
        }
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return out_path

    def load(self, project_dir: Path) -> PipelineCost | None:
        """从 .super-dev/metrics/pipeline-cost.json 加载，不存在则返回 None。"""
        path = project_dir / ".super-dev" / "metrics" / "pipeline-cost.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        phases: dict[str, PhaseCost] = {}
        for name, raw in data.get("phases", {}).items():
            phases[name] = PhaseCost(
                phase=raw.get("phase", name),
                duration_seconds=float(raw.get("duration_seconds", 0)),
                files_read=int(raw.get("files_read", 0)),
                files_written=int(raw.get("files_written", 0)),
                commands_executed=int(raw.get("commands_executed", 0)),
                started_at=raw.get("started_at", ""),
                completed_at=raw.get("completed_at", ""),
            )

        return PipelineCost(
            phases=phases,
            total_duration=float(data.get("total_duration", 0)),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
        )
