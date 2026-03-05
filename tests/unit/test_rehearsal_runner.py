from pathlib import Path

from super_dev.deployers.rehearsal_runner import LaunchRehearsalRunner


def _prepare_common_artifacts(temp_project_dir: Path, project_name: str) -> None:
    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / f"{project_name}-redteam.md").write_text(
        (
            "# demo-redteam\n\n"
            "- **Critical 问题**: 0\n"
            "- **总分**: 90/100\n"
            "**状态**: 通过 - 质量良好\n"
        ),
        encoding="utf-8",
    )
    (output_dir / f"{project_name}-quality-gate.md").write_text(
        (
            "# 质量门禁报告\n\n"
            "**状态**: <span style='color:green'>通过</span>\n"
            "**总分**: 88/100\n"
        ),
        encoding="utf-8",
    )
    (output_dir / f"{project_name}-pipeline-metrics.json").write_text(
        (
            "{\n"
            '  "project_name": "demo",\n'
            '  "success": true,\n'
            '  "success_rate": 100,\n'
            '  "total_duration_seconds": 11.4,\n'
            '  "stages": []\n'
            "}\n"
        ),
        encoding="utf-8",
    )

    delivery_dir = output_dir / "delivery"
    delivery_dir.mkdir(parents=True, exist_ok=True)
    (delivery_dir / f"{project_name}-delivery-manifest.json").write_text(
        (
            "{\n"
            '  "project_name": "demo",\n'
            '  "status": "ready"\n'
            "}\n"
        ),
        encoding="utf-8",
    )

    rehearsal_dir = output_dir / "rehearsal"
    rehearsal_dir.mkdir(parents=True, exist_ok=True)
    (rehearsal_dir / f"{project_name}-launch-rehearsal.md").write_text("# Launch", encoding="utf-8")
    (rehearsal_dir / f"{project_name}-rollback-playbook.md").write_text("# Rollback", encoding="utf-8")
    (rehearsal_dir / f"{project_name}-smoke-checklist.md").write_text("# Smoke", encoding="utf-8")

    (temp_project_dir / "backend" / "migrations").mkdir(parents=True, exist_ok=True)
    (temp_project_dir / "backend" / "migrations" / "001_init.sql").write_text(
        "-- migration",
        encoding="utf-8",
    )

    (temp_project_dir / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (temp_project_dir / ".github" / "workflows" / "ci.yml").write_text("name: ci", encoding="utf-8")
    (temp_project_dir / ".github" / "workflows" / "cd.yml").write_text("name: cd", encoding="utf-8")


def test_rehearsal_runner_passes_when_all_artifacts_ready(temp_project_dir: Path) -> None:
    project_name = "demo"
    _prepare_common_artifacts(temp_project_dir, project_name=project_name)

    runner = LaunchRehearsalRunner(
        project_dir=temp_project_dir,
        project_name=project_name,
        cicd_platform="github",
    )
    result = runner.run()

    assert result.passed is True
    assert result.score >= 80
    files = runner.write(result)
    assert files["markdown"].exists()
    assert files["json"].exists()


def test_rehearsal_runner_detects_quality_gate_failed_text(temp_project_dir: Path) -> None:
    project_name = "demo"
    _prepare_common_artifacts(temp_project_dir, project_name=project_name)

    # 覆盖为“未通过”，验证不会被“通过”子串误判。
    (temp_project_dir / "output" / f"{project_name}-quality-gate.md").write_text(
        (
            "# 质量门禁报告\n\n"
            "**状态**: <span style='color:red'>未通过</span>\n"
            "**总分**: 78/100\n"
        ),
        encoding="utf-8",
    )

    runner = LaunchRehearsalRunner(
        project_dir=temp_project_dir,
        project_name=project_name,
        cicd_platform="github",
    )
    result = runner.run()
    quality_checks = [item for item in result.checks if item.name == "Quality Gate"]

    assert quality_checks
    assert quality_checks[0].passed is False
    assert result.passed is False
