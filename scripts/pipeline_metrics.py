#!/usr/bin/env python3
"""
开发：Excellent（11964948@qq.com）
功能：Pipeline 效能度量 CLI 工具
作用：查看效能趋势、DORA 指标、生成完整报告
创建时间：2026-03-28
最后修改：2026-03-28

用法:
    python scripts/pipeline_metrics.py trend                    # 查看效能趋势
    python scripts/pipeline_metrics.py trend --project myapp    # 查看特定项目趋势
    python scripts/pipeline_metrics.py dora                     # 查看 DORA 指标
    python scripts/pipeline_metrics.py dora --project myapp     # 特定项目 DORA 指标
    python scripts/pipeline_metrics.py report                   # 生成完整报告
    python scripts/pipeline_metrics.py report --project myapp   # 特定项目报告
    python scripts/pipeline_metrics.py report --output FILE     # 报告写入文件
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from project root without install
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from super_dev.metrics.pipeline_metrics import (  # noqa: E402
    PipelineMetricsAnalyzer,
    _format_duration,
)


def cmd_trend(args: argparse.Namespace) -> None:
    """显示效能趋势"""
    analyzer = PipelineMetricsAnalyzer(args.metrics_dir)
    trend = analyzer.get_trend(args.project)

    if not trend["quality_trend"]:
        print("No historical data found.")
        print(f"  Metrics directory: {analyzer.metrics_dir.resolve()}")
        return

    print("=== Pipeline Efficiency Trend ===")
    print()

    print(f"  Quality scores:       {trend['quality_trend']}")
    print(f"  Duration (seconds):   {trend['duration_trend']}")
    print(f"  Knowledge hit rates:  {trend['knowledge_hit_rate_trend']}")
    print(f"  Requirement coverage: {trend['requirement_coverage_trend']}")
    print()
    print(f"  Summary: {trend['improvement_summary']}")


def cmd_dora(args: argparse.Namespace) -> None:
    """显示 DORA 风格指标"""
    analyzer = PipelineMetricsAnalyzer(args.metrics_dir)
    dora = analyzer.get_dora_metrics(args.project)

    if dora["total_runs"] == 0:
        print("No historical data found.")
        print(f"  Metrics directory: {analyzer.metrics_dir.resolve()}")
        return

    print("=== DORA-Style Metrics ===")
    print()
    print(f"  Deployment Frequency:   {dora['deployment_frequency_per_week']:.1f} runs/week")
    print(f"  Lead Time for Changes:  {_format_duration(dora['lead_time_seconds'])}")
    print(f"  Change Failure Rate:    {dora['change_failure_rate']:.1%}")
    print(f"  MTTR:                   {_format_duration(dora['mttr_seconds'])}")
    print()
    print(f"  Period: {dora['period_description']}")


def cmd_report(args: argparse.Namespace) -> None:
    """生成完整 Markdown 报告"""
    analyzer = PipelineMetricsAnalyzer(args.metrics_dir)
    report = analyzer.generate_report(args.project)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Report written to {output_path.resolve()}")
    else:
        print(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline Efficiency Metrics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--metrics-dir",
        default="output/metrics-history",
        help="Path to metrics history directory (default: output/metrics-history)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # trend
    trend_parser = subparsers.add_parser("trend", help="Show efficiency trend")
    trend_parser.add_argument("--project", default=None, help="Filter by project name")

    # dora
    dora_parser = subparsers.add_parser("dora", help="Show DORA-style metrics")
    dora_parser.add_argument("--project", default=None, help="Filter by project name")

    # report
    report_parser = subparsers.add_parser("report", help="Generate full Markdown report")
    report_parser.add_argument("--project", default=None, help="Filter by project name")
    report_parser.add_argument("--output", "-o", default=None, help="Write report to file")

    args = parser.parse_args()

    commands = {
        "trend": cmd_trend,
        "dora": cmd_dora,
        "report": cmd_report,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
