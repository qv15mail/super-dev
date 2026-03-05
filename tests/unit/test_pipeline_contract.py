from __future__ import annotations

import json
from pathlib import Path

from super_dev.orchestrator import PipelineContractReport


def test_pipeline_contract_write_outputs(temp_project_dir: Path) -> None:
    report = PipelineContractReport(project_name="demo")
    report.record_stage(
        stage="4",
        title="实现骨架",
        success=True,
        duration_seconds=1.234,
        inputs=["output/demo-prd.md"],
        outputs=["backend/src/app.js"],
        notes=["生成基础 API 模块"],
    )
    report.finalize(success=True)

    files = report.write(temp_project_dir / "output")
    assert files["json"].exists()
    assert files["markdown"].exists()

    payload = json.loads(files["json"].read_text(encoding="utf-8"))
    assert payload["project_name"] == "demo"
    assert payload["success"] is True
    assert len(payload["stages"]) == 1
    assert payload["stages"][0]["title"] == "实现骨架"


def test_pipeline_contract_markdown_contains_stage_table(temp_project_dir: Path) -> None:
    report = PipelineContractReport(project_name="shop")
    report.record_stage(
        stage="6",
        title="质量门禁",
        success=False,
        duration_seconds=0.42,
        inputs=["output/shop-redteam.md"],
        outputs=["output/shop-quality-gate.md"],
    )
    report.finalize(success=False, failure_reason="quality_gate_failed")
    files = report.write(temp_project_dir / "output")

    markdown = files["markdown"].read_text(encoding="utf-8")
    assert "Pipeline Contract" in markdown
    assert "quality_gate_failed" in markdown
    assert "| 6 | 质量门禁 | FAIL |" in markdown
