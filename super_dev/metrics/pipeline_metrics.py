"""
开发：Excellent（11964948@qq.com）
功能：Pipeline 效能度量系统
作用：追踪每次 pipeline 执行的效率和质量数据，生成趋势报告。
      追踪 DORA 指标和 pipeline 执行效率。
创建时间：2026-03-28
最后修改：2026-03-28
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_logger = logging.getLogger("super_dev.metrics.pipeline_metrics")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class PipelineRunMetrics:
    """单次 pipeline 执行度量"""

    run_id: str
    project_name: str
    timestamp: str

    # 时间度量
    total_duration_seconds: float = 0.0
    phase_durations: dict[str, float] = field(default_factory=dict)

    # 质量度量
    quality_gate_score: int = 0
    quality_gate_passed: bool = False
    redteam_issues_count: int = 0
    redteam_critical_count: int = 0

    # 知识度量
    knowledge_files_referenced: int = 0
    knowledge_hit_rate: float = 0.0

    # 交付度量
    spec_requirements_count: int = 0
    spec_requirements_covered: int = 0
    deliverables_count: int = 0
    proof_pack_completion: float = 0.0

    # 验证规则度量
    validation_rules_total: int = 0
    validation_rules_passed: int = 0
    validation_critical_failures: int = 0

    # 返工度量 (DORA 2025 Rework Rate)
    rework_count: int = 0  # 返工次数（质量门禁失败后重试）
    rework_phases: list[str] = field(default_factory=list)  # 返工的阶段

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------

    @property
    def requirement_coverage(self) -> float:
        """需求覆盖率 (0-1)"""
        if self.spec_requirements_count == 0:
            return 0.0
        return self.spec_requirements_covered / self.spec_requirements_count

    @property
    def validation_pass_rate(self) -> float:
        """验证规则通过率 (0-1)"""
        if self.validation_rules_total == 0:
            return 0.0
        return self.validation_rules_passed / self.validation_rules_total

    def to_dict(self) -> dict:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> PipelineRunMetrics:
        """从字典反序列化"""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)


# ---------------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------------


class PipelineMetricsCollector:
    """Pipeline 度量收集器

    典型用法::

        collector = PipelineMetricsCollector()
        collector.start_run("my-project")
        collector.record_phase_start("research")
        # ... 执行 research 阶段 ...
        collector.record_phase_end("research")
        collector.record_quality_score(92, True)
        metrics = collector.finish_run()
    """

    def __init__(self, metrics_dir: str = "output/metrics-history") -> None:
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.current_run: PipelineRunMetrics | None = None
        self._run_start_time: float = 0.0
        self._phase_start_times: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_run(self, project_name: str) -> str:
        """开始一次 pipeline 执行度量，返回 run_id"""
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
        self.current_run = PipelineRunMetrics(
            run_id=run_id,
            project_name=project_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._run_start_time = time.monotonic()
        self._phase_start_times = {}
        _logger.info("Pipeline metrics run started: %s (project=%s)", run_id, project_name)
        return run_id

    def finish_run(self) -> PipelineRunMetrics:
        """结束本次执行，保存度量数据并返回"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")

        self.current_run.total_duration_seconds = round(time.monotonic() - self._run_start_time, 2)

        # 结束仍在计时的阶段
        for phase in list(self._phase_start_times):
            self.record_phase_end(phase)

        metrics = self.current_run
        self.save_metrics(metrics)
        _logger.info(
            "Pipeline metrics run finished: %s (duration=%.1fs, quality=%d)",
            metrics.run_id,
            metrics.total_duration_seconds,
            metrics.quality_gate_score,
        )
        self.current_run = None
        return metrics

    # ------------------------------------------------------------------
    # Phase tracking
    # ------------------------------------------------------------------

    def record_phase_start(self, phase: str) -> None:
        """记录阶段开始"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self._phase_start_times[phase] = time.monotonic()
        _logger.debug("Phase started: %s", phase)

    def record_phase_end(self, phase: str) -> None:
        """记录阶段结束，计算该阶段耗时"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        start = self._phase_start_times.pop(phase, None)
        if start is None:
            _logger.warning("record_phase_end called for '%s' without matching start", phase)
            return
        duration = round(time.monotonic() - start, 2)
        self.current_run.phase_durations[phase] = duration
        _logger.debug("Phase ended: %s (%.2fs)", phase, duration)

    # ------------------------------------------------------------------
    # Quality & knowledge recording
    # ------------------------------------------------------------------

    def record_quality_score(self, score: int, passed: bool) -> None:
        """记录质量门禁结果"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.quality_gate_score = score
        self.current_run.quality_gate_passed = passed

    def record_redteam_results(self, issues_count: int, critical_count: int) -> None:
        """记录红队审查结果"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.redteam_issues_count = issues_count
        self.current_run.redteam_critical_count = critical_count

    def record_knowledge_usage(self, files_referenced: int, hit_rate: float) -> None:
        """记录知识使用情况"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.knowledge_files_referenced = files_referenced
        self.current_run.knowledge_hit_rate = round(hit_rate, 4)

    def record_spec_coverage(
        self,
        requirements_count: int,
        requirements_covered: int,
    ) -> None:
        """记录需求覆盖情况"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.spec_requirements_count = requirements_count
        self.current_run.spec_requirements_covered = requirements_covered

    def record_deliverables(self, count: int, proof_pack_completion: float) -> None:
        """记录交付物情况"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.deliverables_count = count
        self.current_run.proof_pack_completion = round(proof_pack_completion, 4)

    def record_validation_results(
        self,
        rules_total: int,
        rules_passed: int,
        critical_failures: int,
    ) -> None:
        """记录验证规则结果"""
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.validation_rules_total = rules_total
        self.current_run.validation_rules_passed = rules_passed
        self.current_run.validation_critical_failures = critical_failures

    def record_rework(self, phase: str) -> None:
        """记录一次返工（质量门禁失败后重试）

        每当某阶段因质量门禁失败而需要重新执行时调用。
        DORA 2025 报告指出 AI 辅助开发会提升吞吐量但可能增加返工率，
        此指标用于追踪交付稳定性。

        Args:
            phase: 发生返工的阶段名称
        """
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")
        self.current_run.rework_count += 1
        self.current_run.rework_phases.append(phase)
        _logger.info(
            "Rework recorded for phase '%s' (total reworks: %d)",
            phase,
            self.current_run.rework_count,
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_metrics(self, metrics: PipelineRunMetrics) -> Path:
        """保存度量数据到 JSON 文件

        文件名: output/metrics-history/{project}_{run_id}.json
        """
        safe_name = metrics.project_name.replace("/", "_").replace(" ", "_")
        filename = f"{safe_name}_{metrics.run_id}.json"
        filepath = self.metrics_dir / filename
        filepath.write_text(
            json.dumps(metrics.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        _logger.info("Metrics saved to %s", filepath)
        return filepath


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class PipelineMetricsAnalyzer:
    """Pipeline 度量分析器 - 趋势分析与 DORA 风格指标"""

    def __init__(self, metrics_dir: str = "output/metrics-history") -> None:
        self.metrics_dir = Path(metrics_dir)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_history(
        self,
        project_name: str | None = None,
        limit: int = 50,
    ) -> list[PipelineRunMetrics]:
        """加载历史度量数据

        Args:
            project_name: 项目名过滤，为 None 时加载全部项目
            limit: 最多返回的记录数（按时间倒序截取）

        Returns:
            按 timestamp 升序排列的度量列表
        """
        if not self.metrics_dir.exists():
            return []

        results: list[PipelineRunMetrics] = []
        for path in sorted(self.metrics_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                metrics = PipelineRunMetrics.from_dict(data)
                if project_name is None or metrics.project_name == project_name:
                    results.append(metrics)
            except (json.JSONDecodeError, TypeError, KeyError) as exc:
                _logger.warning("Skipping malformed metrics file %s: %s", path, exc)

        # 按 timestamp 升序，取最近 limit 条
        results.sort(key=lambda m: m.timestamp)
        return results[-limit:]

    # ------------------------------------------------------------------
    # Trend analysis
    # ------------------------------------------------------------------

    def get_trend(self, project_name: str | None = None) -> dict:
        """获取效能趋势

        Returns:
            包含质量趋势、耗时趋势、知识命中率趋势及改善摘要的字典
        """
        history = self.load_history(project_name)
        if not history:
            return {
                "quality_trend": [],
                "duration_trend": [],
                "knowledge_hit_rate_trend": [],
                "requirement_coverage_trend": [],
                "improvement_summary": "No historical data available.",
            }

        quality_trend = [m.quality_gate_score for m in history]
        duration_trend = [m.total_duration_seconds for m in history]
        knowledge_trend = [m.knowledge_hit_rate for m in history]
        coverage_trend = [m.requirement_coverage for m in history]

        summary_parts: list[str] = []
        if len(history) >= 2:
            first, last = history[0], history[-1]

            # Quality improvement
            q_delta = last.quality_gate_score - first.quality_gate_score
            if first.quality_gate_score > 0:
                q_pct = abs(q_delta) / first.quality_gate_score * 100
                direction = "improved" if q_delta > 0 else "declined"
                summary_parts.append(
                    f"Quality score {direction} by {q_pct:.0f}% ({first.quality_gate_score} -> {last.quality_gate_score})"
                )

            # Duration improvement
            if first.total_duration_seconds > 0:
                d_delta = first.total_duration_seconds - last.total_duration_seconds
                d_pct = abs(d_delta) / first.total_duration_seconds * 100
                direction = "reduced" if d_delta > 0 else "increased"
                summary_parts.append(
                    f"Duration {direction} by {d_pct:.0f}% ({first.total_duration_seconds:.0f}s -> {last.total_duration_seconds:.0f}s)"
                )

            # Knowledge hit rate
            if first.knowledge_hit_rate > 0:
                k_delta = last.knowledge_hit_rate - first.knowledge_hit_rate
                k_pct = abs(k_delta) / first.knowledge_hit_rate * 100
                direction = "improved" if k_delta > 0 else "declined"
                summary_parts.append(
                    f"Knowledge hit rate {direction} by {k_pct:.0f}% ({first.knowledge_hit_rate:.2f} -> {last.knowledge_hit_rate:.2f})"
                )

        return {
            "quality_trend": quality_trend,
            "duration_trend": duration_trend,
            "knowledge_hit_rate_trend": knowledge_trend,
            "requirement_coverage_trend": coverage_trend,
            "improvement_summary": (
                "; ".join(summary_parts) if summary_parts else "Not enough data for comparison."
            ),
        }

    # ------------------------------------------------------------------
    # DORA-style metrics
    # ------------------------------------------------------------------

    def get_dora_metrics(self, project_name: str | None = None) -> dict:
        """计算类 DORA 指标

        - Deployment Frequency: pipeline 执行频率 (runs/week)
        - Lead Time for Changes: 平均 pipeline 耗时 (seconds)
        - Change Failure Rate: 质量门禁失败率 (0-1)
        - MTTR: 从失败到下次通过的平均恢复时间 (seconds)

        Returns:
            包含四项 DORA 指标的字典
        """
        history = self.load_history(project_name)
        if not history:
            return {
                "deployment_frequency_per_week": 0.0,
                "lead_time_seconds": 0.0,
                "change_failure_rate": 0.0,
                "mttr_seconds": 0.0,
                "rework_rate": 0.0,
                "total_runs": 0,
                "period_description": "No data",
            }

        total_runs = len(history)

        # --- Deployment Frequency ---
        if total_runs >= 2:
            first_ts = datetime.fromisoformat(history[0].timestamp)
            last_ts = datetime.fromisoformat(history[-1].timestamp)
            span_seconds = max((last_ts - first_ts).total_seconds(), 1)
            span_weeks = span_seconds / (7 * 24 * 3600)
            deployment_freq = total_runs / max(span_weeks, 0.01)
        else:
            deployment_freq = float(total_runs)
            span_weeks = 0.0

        # --- Lead Time ---
        avg_duration = sum(m.total_duration_seconds for m in history) / total_runs

        # --- Change Failure Rate ---
        failures = sum(1 for m in history if not m.quality_gate_passed)
        failure_rate = failures / total_runs

        # --- MTTR ---
        recovery_times: list[float] = []
        i = 0
        while i < total_runs:
            if not history[i].quality_gate_passed:
                fail_ts = datetime.fromisoformat(history[i].timestamp)
                # 向后查找第一次通过
                j = i + 1
                while j < total_runs and not history[j].quality_gate_passed:
                    j += 1
                if j < total_runs:
                    pass_ts = datetime.fromisoformat(history[j].timestamp)
                    recovery_times.append((pass_ts - fail_ts).total_seconds())
                i = j + 1
            else:
                i += 1
        mttr = sum(recovery_times) / len(recovery_times) if recovery_times else 0.0

        # --- Rework Rate (DORA 2025) ---
        # 返工率 = 有返工的 run 数 / 总 run 数
        # DORA 2025 发现 AI 提升吞吐量但增加返工率，此指标追踪交付稳定性
        runs_with_rework = sum(1 for m in history if m.rework_count > 0)
        rework_rate = runs_with_rework / total_runs
        total_rework_count = sum(m.rework_count for m in history)
        # 统计最常返工的阶段
        rework_phase_counts: dict[str, int] = {}
        for m in history:
            for phase in m.rework_phases:
                rework_phase_counts[phase] = rework_phase_counts.get(phase, 0) + 1
        top_rework_phases = sorted(rework_phase_counts.items(), key=lambda x: -x[1])[:3]

        period_desc = f"{total_runs} runs"
        if total_runs >= 2:
            period_desc += f" over {span_weeks:.1f} weeks"

        return {
            "deployment_frequency_per_week": round(deployment_freq, 2),
            "lead_time_seconds": round(avg_duration, 2),
            "change_failure_rate": round(failure_rate, 4),
            "mttr_seconds": round(mttr, 2),
            "rework_rate": round(rework_rate, 4),
            "total_rework_count": total_rework_count,
            "top_rework_phases": top_rework_phases,
            "total_runs": total_runs,
            "period_description": period_desc,
        }

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(self, project_name: str | None = None) -> str:
        """生成效能趋势 Markdown 报告

        包含: 概览、DORA 指标、质量趋势图(ASCII)、阶段耗时分析、知识使用分析、改善建议
        """
        history = self.load_history(project_name)
        trend = self.get_trend(project_name)
        dora = self.get_dora_metrics(project_name)

        title_suffix = f" - {project_name}" if project_name else ""
        lines: list[str] = []
        lines.append(f"# Pipeline Efficiency Report{title_suffix}")
        lines.append("")
        lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"Data points: {len(history)}")
        lines.append("")

        # --- Summary ---
        lines.append("## Summary")
        lines.append("")
        lines.append(trend["improvement_summary"])
        lines.append("")

        # --- DORA Metrics ---
        dora_levels = _classify_dora_levels(dora)
        overall_level = _overall_dora_level(dora_levels)

        lines.append("## DORA-Style Metrics")
        lines.append("")
        lines.append(f"**Overall DORA Level: {overall_level}**")
        lines.append("")
        lines.append("| Metric | Value | Level | Benchmark |")
        lines.append("|--------|-------|-------|-----------|")
        lines.append(
            f"| Deployment Frequency | {dora['deployment_frequency_per_week']:.1f} runs/week "
            f"| {dora_levels['deployment_frequency']} "
            f"| {DORA_BENCHMARKS['deployment_frequency'][dora_levels['deployment_frequency'].lower()]} |"
        )
        lines.append(
            f"| Lead Time for Changes | {_format_duration(dora['lead_time_seconds'])} "
            f"| {dora_levels['lead_time']} "
            f"| {DORA_BENCHMARKS['lead_time'][dora_levels['lead_time'].lower()]} |"
        )
        lines.append(
            f"| Change Failure Rate | {dora['change_failure_rate']:.1%} "
            f"| {dora_levels['change_failure_rate']} "
            f"| {DORA_BENCHMARKS['change_failure_rate'][dora_levels['change_failure_rate'].lower()]} |"
        )
        lines.append(
            f"| MTTR | {_format_duration(dora['mttr_seconds'])} "
            f"| {dora_levels['mttr']} "
            f"| {DORA_BENCHMARKS['mttr'][dora_levels['mttr'].lower()]} |"
        )
        lines.append(
            f"| Rework Rate (DORA 2025) | {dora['rework_rate']:.1%} "
            f"| {dora_levels['rework_rate']} "
            f"| {DORA_BENCHMARKS['rework_rate'][dora_levels['rework_rate'].lower()]} |"
        )
        lines.append(f"| Period | {dora['period_description']} | - | - |")
        lines.append("")

        if not history:
            lines.append("*No historical data available.*")
            return "\n".join(lines)

        # --- Quality Trend (ASCII chart) ---
        lines.append("## Quality Score Trend")
        lines.append("")
        lines.append("```")
        lines.extend(_ascii_bar_chart(trend["quality_trend"], max_val=100, width=40, label="Q"))
        lines.append("```")
        lines.append("")

        # --- Duration Trend ---
        lines.append("## Duration Trend")
        lines.append("")
        lines.append("```")
        max_dur = max(trend["duration_trend"]) if trend["duration_trend"] else 1
        lines.extend(
            _ascii_bar_chart(trend["duration_trend"], max_val=max_dur, width=40, label="T")
        )
        lines.append("```")
        lines.append("")

        # --- Phase Duration Breakdown (latest run) ---
        latest = history[-1]
        if latest.phase_durations:
            lines.append("## Phase Duration Breakdown (Latest Run)")
            lines.append("")
            lines.append("| Phase | Duration |")
            lines.append("|-------|----------|")
            for phase, dur in sorted(latest.phase_durations.items(), key=lambda x: -x[1]):
                lines.append(f"| {phase} | {_format_duration(dur)} |")
            lines.append("")

        # --- Knowledge Usage ---
        lines.append("## Knowledge Usage Trend")
        lines.append("")
        lines.append("```")
        lines.extend(
            _ascii_bar_chart(
                [round(v * 100) for v in trend["knowledge_hit_rate_trend"]],
                max_val=100,
                width=40,
                label="K%",
            )
        )
        lines.append("```")
        lines.append("")

        # --- Improvement Suggestions ---
        lines.append("## Improvement Suggestions")
        lines.append("")
        suggestions = self._generate_suggestions(history, dora)
        for s in suggestions:
            lines.append(f"- {s}")
        lines.append("")

        # --- Super Dev Governance Value ---
        lines.extend(self._generate_governance_value(history, dora, dora_levels))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Governance value
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_governance_value(
        history: list[PipelineRunMetrics],
        dora: dict,
        dora_levels: dict[str, str],
    ) -> list[str]:
        """生成 Super Dev 治理价值证明章节"""
        lines: list[str] = [
            "## Super Dev Governance Value",
            "",
        ]

        if not history:
            lines.append("*Not enough data to calculate governance value.*")
            lines.append("")
            return lines

        # 通过质量门禁拦截的问题数
        total_redteam = sum(m.redteam_issues_count for m in history)
        total_critical = sum(m.redteam_critical_count for m in history)
        total_validation_failures = sum(
            m.validation_rules_total - m.validation_rules_passed for m in history
        )

        lines.append(
            f"- Quality gate intercepted **{total_redteam}** red-team issues "
            f"(**{total_critical}** critical) across {len(history)} runs"
        )
        lines.append(f"- Validation rules discovered **{total_validation_failures}** risks")

        # 知识库命中率趋势
        runs_with_knowledge = [m for m in history if m.knowledge_hit_rate > 0]
        if len(runs_with_knowledge) >= 2:
            first_rate = runs_with_knowledge[0].knowledge_hit_rate * 100
            last_rate = runs_with_knowledge[-1].knowledge_hit_rate * 100
            lines.append(f"- Knowledge hit rate: {first_rate:.0f}% -> {last_rate:.0f}%")

        # DORA 等级变化
        if len(history) >= 2:
            first_half = history[: len(history) // 2]
            # 简单估算早期 DORA 等级
            early_failures = sum(1 for m in first_half if not m.quality_gate_passed)
            early_rate = early_failures / max(len(first_half), 1)
            early_level = _classify_failure_rate_level(early_rate)
            current_level = dora_levels.get("change_failure_rate", "Medium")
            if early_level != current_level:
                lines.append(f"- DORA failure-rate level: [{early_level}] -> [{current_level}]")
            overall = _overall_dora_level(dora_levels)
            lines.append(f"- Current overall DORA level: **{overall}**")

        lines.append("")
        return lines

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_suggestions(
        history: list[PipelineRunMetrics],
        dora: dict,
    ) -> list[str]:
        """根据度量数据生成改善建议"""
        suggestions: list[str] = []

        if not history:
            return ["Collect more pipeline runs to generate actionable suggestions."]

        latest = history[-1]

        # Quality suggestions
        if latest.quality_gate_score < 80:
            suggestions.append(
                f"Quality score is {latest.quality_gate_score}/100. "
                "Focus on resolving red-team critical issues and improving test coverage."
            )

        # Failure rate
        if dora["change_failure_rate"] > 0.2:
            suggestions.append(
                f"Change failure rate is {dora['change_failure_rate']:.0%}. "
                "Review recurring failure patterns and strengthen pre-commit validation."
            )

        # Knowledge usage
        if latest.knowledge_hit_rate < 0.3:
            suggestions.append(
                f"Knowledge hit rate is {latest.knowledge_hit_rate:.0%}. "
                "Expand the knowledge base with domain-specific standards and playbooks."
            )

        # Duration
        if dora["lead_time_seconds"] > 600:
            suggestions.append(
                f"Average lead time is {_format_duration(dora['lead_time_seconds'])}. "
                "Consider parallelizing independent phases or caching research results."
            )

        # MTTR
        if dora["mttr_seconds"] > 3600:
            suggestions.append(
                f"MTTR is {_format_duration(dora['mttr_seconds'])}. "
                "Set up faster feedback loops and automate common fix patterns."
            )

        # Requirement coverage
        if latest.requirement_coverage < 0.8 and latest.spec_requirements_count > 0:
            suggestions.append(
                f"Requirement coverage is {latest.requirement_coverage:.0%}. "
                "Ensure all SHALL/MUST requirements are addressed before delivery."
            )

        # Rework rate (DORA 2025)
        if dora.get("rework_rate", 0) > 0.3:
            top_phases = dora.get("top_rework_phases", [])
            phase_hint = ""
            if top_phases:
                phase_hint = f" Top rework phases: {', '.join(p for p, _ in top_phases)}."
            suggestions.append(
                f"Rework rate is {dora['rework_rate']:.0%}. "
                "AI-assisted delivery may increase throughput but also instability. "
                f"Strengthen pre-phase validation to reduce rework.{phase_hint}"
            )

        # Redteam critical issues
        if latest.redteam_critical_count > 0:
            suggestions.append(
                f"{latest.redteam_critical_count} critical red-team issue(s) remain. "
                "These must be resolved before production deployment."
            )

        if not suggestions:
            suggestions.append("All metrics look healthy. Keep up the good work!")

        return suggestions


# ---------------------------------------------------------------------------
# DORA benchmarks & classification
# ---------------------------------------------------------------------------

DORA_BENCHMARKS: dict[str, dict[str, str]] = {
    "deployment_frequency": {
        "elite": "On-demand (multiple/day)",
        "high": "1/day - 1/week",
        "medium": "1/week - 1/month",
        "low": "< 1/month",
    },
    "lead_time": {
        "elite": "< 1 hour",
        "high": "< 1 day",
        "medium": "< 1 week",
        "low": "> 1 week",
    },
    "change_failure_rate": {
        "elite": "< 5%",
        "high": "< 10%",
        "medium": "< 15%",
        "low": "> 15%",
    },
    "mttr": {
        "elite": "< 1 hour",
        "high": "< 1 day",
        "medium": "< 1 week",
        "low": "> 1 week",
    },
    "rework_rate": {
        "elite": "< 10%",
        "high": "< 20%",
        "medium": "< 30%",
        "low": "> 30%",
    },
}


def _classify_failure_rate_level(rate: float) -> str:
    """Classify change failure rate into a DORA level."""
    if rate < 0.05:
        return "Elite"
    if rate < 0.10:
        return "High"
    if rate < 0.15:
        return "Medium"
    return "Low"


def _classify_dora_levels(dora: dict) -> dict[str, str]:
    """Classify each DORA metric into Elite/High/Medium/Low."""
    levels: dict[str, str] = {}

    # Deployment Frequency (runs/week)
    freq = dora.get("deployment_frequency_per_week", 0)
    if freq >= 7:
        levels["deployment_frequency"] = "Elite"
    elif freq >= 1:
        levels["deployment_frequency"] = "High"
    elif freq >= 0.25:
        levels["deployment_frequency"] = "Medium"
    else:
        levels["deployment_frequency"] = "Low"

    # Lead Time (seconds)
    lt = dora.get("lead_time_seconds", 0)
    if lt <= 0:
        levels["lead_time"] = "Medium"
    elif lt < 3600:
        levels["lead_time"] = "Elite"
    elif lt < 86400:
        levels["lead_time"] = "High"
    elif lt < 604800:
        levels["lead_time"] = "Medium"
    else:
        levels["lead_time"] = "Low"

    # Change Failure Rate
    levels["change_failure_rate"] = _classify_failure_rate_level(dora.get("change_failure_rate", 0))

    # MTTR (seconds)
    mttr = dora.get("mttr_seconds", 0)
    if mttr <= 0:
        levels["mttr"] = "Elite"
    elif mttr < 3600:
        levels["mttr"] = "Elite"
    elif mttr < 86400:
        levels["mttr"] = "High"
    elif mttr < 604800:
        levels["mttr"] = "Medium"
    else:
        levels["mttr"] = "Low"

    # Rework Rate
    rr = dora.get("rework_rate", 0)
    if rr < 0.10:
        levels["rework_rate"] = "Elite"
    elif rr < 0.20:
        levels["rework_rate"] = "High"
    elif rr < 0.30:
        levels["rework_rate"] = "Medium"
    else:
        levels["rework_rate"] = "Low"

    return levels


def _overall_dora_level(levels: dict[str, str]) -> str:
    """Determine overall DORA level from individual metric levels."""
    rank = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
    if not levels:
        return "Medium"
    avg = sum(rank.get(v, 2) for v in levels.values()) / len(levels)
    if avg >= 3.5:
        return "Elite"
    if avg >= 2.5:
        return "High"
    if avg >= 1.5:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Module-level utilities
# ---------------------------------------------------------------------------


def _format_duration(seconds: float) -> str:
    """将秒数格式化为可读时间字符串"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    hours = seconds / 3600
    return f"{hours:.1f}h"


def _ascii_bar_chart(
    values: list[float | int],
    max_val: float = 100,
    width: int = 40,
    label: str = "",
) -> list[str]:
    """生成简单的 ASCII 横向柱状图

    Args:
        values: 数值列表
        max_val: 最大值（用于缩放）
        width: 柱状图最大宽度（字符数）
        label: 每行前缀标签

    Returns:
        字符串行列表
    """
    if not values:
        return ["  (no data)"]

    lines: list[str] = []
    safe_max = max(max_val, 1)
    for i, v in enumerate(values):
        bar_len = int(round(v / safe_max * width))
        bar_len = max(bar_len, 0)
        bar = "#" * bar_len
        idx_label = f"{label}{i + 1:>3}"
        val_str = f"{v:>6.1f}" if isinstance(v, float) else f"{v:>6}"
        lines.append(f"  {idx_label} | {bar:<{width}} | {val_str}")
    return lines
