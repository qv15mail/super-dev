from pathlib import Path

from super_dev.release_readiness import ReleaseReadinessEvaluator


def _prepare_release_ready_project(project_dir: Path) -> None:
    (project_dir / "super_dev").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / ".super-dev" / "changes" / "release-hardening-finalization").mkdir(
        parents=True,
        exist_ok=True,
    )
    (project_dir / "pyproject.toml").write_text('[project]\nversion = "2.0.6"\n[project.scripts]\nsuper-dev = "super_dev.cli:main"\n', encoding="utf-8")
    (project_dir / "super_dev" / "__init__.py").write_text('__version__ = "2.0.6"\n', encoding="utf-8")
    (project_dir / "README.md").write_text(
        "当前版本：`2.0.6`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "README_EN.md").write_text(
        "Current version: `2.0.6`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_USAGE_GUIDE.md").write_text(
        "Smoke\n/super-dev\nsuper-dev:\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_CAPABILITY_AUDIT.md").write_text(
        "官方依据\nsuper-dev integrate smoke\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "WORKFLOW_GUIDE.md").write_text(
        "super-dev review docs\nsuper-dev run --resume\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "WORKFLOW_GUIDE_EN.md").write_text(
        "super-dev review docs\nsuper-dev run --resume\n",
        encoding="utf-8",
    )
    (project_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    for name in ("change.yaml", "proposal.md", "tasks.md"):
        (project_dir / ".super-dev" / "changes" / "release-hardening-finalization" / name).write_text(
            "ok\n",
            encoding="utf-8",
        )


def test_release_readiness_detects_missing_docs(temp_project_dir: Path) -> None:
    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    assert report.passed is False
    assert "Documentation Coverage" in report.failed_checks or any(
        check.name == "Documentation Coverage" and not check.passed for check in report.checks
    )


def test_release_readiness_passes_when_required_artifacts_exist(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)
    files = evaluator.write(report)

    assert report.passed is True
    assert report.score == 100
    assert files["markdown"].exists()
    assert files["json"].exists()
