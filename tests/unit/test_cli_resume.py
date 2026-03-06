from super_dev.cli import SuperDevCLI


def test_resume_stage_resolution_matrix() -> None:
    cli = SuperDevCLI()

    assert cli._resolve_resume_start_stage(None, skip_redteam=False) is None
    assert cli._resolve_resume_start_stage(4, skip_redteam=False) is None
    assert cli._resolve_resume_start_stage(5, skip_redteam=False) == 5
    assert cli._resolve_resume_start_stage(6, skip_redteam=False) == 5
    assert cli._resolve_resume_start_stage(6, skip_redteam=True) == 6
    assert cli._resolve_resume_start_stage(7, skip_redteam=False) == 7
    assert cli._resolve_resume_start_stage(8, skip_redteam=False) == 8
    assert cli._resolve_resume_start_stage(9, skip_redteam=False) == 9
    assert cli._resolve_resume_start_stage(12, skip_redteam=False) == 9


def test_extract_resume_context_prefers_state_and_backfills_from_metrics() -> None:
    cli = SuperDevCLI()
    run_state = {
        "context": {
            "scenario": "0-1",
            "enriched_description": "state-enriched",
        }
    }
    metrics_payload = {
        "stages": [
            {"stage": "1", "details": {"scenario": "1-N+1"}},
            {"stage": "3", "details": {"change_id": "change-from-metrics"}},
        ]
    }

    context = cli._extract_resume_context(run_state=run_state, metrics_payload=metrics_payload)

    assert context["scenario"] == "0-1"
    assert context["enriched_description"] == "state-enriched"
    assert context["change_id"] == "change-from-metrics"


def test_detect_failed_stage_from_metrics_payload() -> None:
    cli = SuperDevCLI()
    payload = {
        "success": False,
        "stages": [
            {"stage": "0", "success": True},
            {"stage": "6", "success": False},
            {"stage": "7", "success": False},
        ],
    }

    assert cli._detect_failed_stage_from_metrics_payload(payload) == 6


def test_adjust_resume_stage_falls_back_when_docs_missing(temp_project_dir) -> None:
    cli = SuperDevCLI()
    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    adjusted, reasons = cli._adjust_resume_stage_for_artifacts(
        project_dir=temp_project_dir,
        output_dir=output_dir,
        project_name="resume-demo",
        resume_from_stage=7,
    )

    assert adjusted == 1
    assert reasons


def test_adjust_resume_stage_keeps_stage_when_docs_complete(temp_project_dir) -> None:
    cli = SuperDevCLI()
    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    required = cli._stage_one_artifact_paths(output_dir=output_dir, project_name="resume-demo")
    for path in required.values():
        path.write_text("ok", encoding="utf-8")
    (output_dir / "resume-demo-frontend-runtime.json").write_text('{"passed": true}', encoding="utf-8")
    change_dir = temp_project_dir / ".super-dev" / "changes" / "resume-change"
    change_dir.mkdir(parents=True, exist_ok=True)
    (change_dir / "proposal.md").write_text("# proposal", encoding="utf-8")
    (change_dir / "tasks.md").write_text("# tasks", encoding="utf-8")

    adjusted, reasons = cli._adjust_resume_stage_for_artifacts(
        project_dir=temp_project_dir,
        output_dir=output_dir,
        project_name="resume-demo",
        resume_from_stage=7,
    )

    assert adjusted == 7
    assert reasons == []


def test_write_resume_audit_outputs_json_and_markdown(temp_project_dir) -> None:
    cli = SuperDevCLI()
    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "project_name": "resume-demo",
        "status": "running",
        "run_state_status": "failed",
        "detected_failed_stage": 7,
        "initial_resume_stage": 7,
        "final_resume_stage": 1,
        "planned_skipped_stages": [0],
        "fallback_reasons": ["缺少前置文档产物: prd"],
        "started_at": "2026-03-04T00:00:00+00:00",
        "finished_at": "",
    }

    files = cli._write_resume_audit(
        output_dir=output_dir,
        project_name="resume-demo",
        payload=payload,
    )

    assert files["json"].exists()
    assert files["markdown"].exists()
    markdown = files["markdown"].read_text(encoding="utf-8")
    assert "Resume Audit" in markdown
    assert "fallback" in markdown.lower()
