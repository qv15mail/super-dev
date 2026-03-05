from pathlib import Path

from super_dev.orchestrator.telemetry import PipelineTelemetryReport


def test_pipeline_telemetry_report_write_and_rate(temp_project_dir: Path) -> None:
    report = PipelineTelemetryReport(project_name="demo-project")
    report.record_stage("0", "需求增强", True, 1.25, {"local_knowledge_count": 3})
    report.record_stage("1", "文档生成", False, 0.75, {"error": "doc generation failed"})
    report.finalize(success=False, total_duration_seconds=2.1, failure_reason="stage 1 failed")

    output_dir = temp_project_dir / "output"
    files = report.write(output_dir)

    assert files["json"].exists()
    assert files["markdown"].exists()
    assert files["history_json"].exists()
    assert files["history_markdown"].exists()
    payload = files["json"].read_text(encoding="utf-8")
    assert '"project_name": "demo-project"' in payload
    assert '"success_rate": 50.0' in payload
    markdown = files["markdown"].read_text(encoding="utf-8")
    assert "Pipeline Metrics" in markdown
    assert "需求增强" in markdown
