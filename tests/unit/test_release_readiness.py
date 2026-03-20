from pathlib import Path

from super_dev.release_readiness import ReleaseReadinessEvaluator
from super_dev.specs.generator import SpecGenerator


def _prepare_release_ready_project(project_dir: Path) -> None:
    (project_dir / "super_dev").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / ".super-dev" / "changes" / "release-hardening-finalization").mkdir(
        parents=True,
        exist_ok=True,
    )
    (project_dir / "pyproject.toml").write_text('[project]\nversion = "2.0.11"\n[project.scripts]\nsuper-dev = "super_dev.cli:main"\n', encoding="utf-8")
    (project_dir / ".gitignore").write_text(
        "\n".join(
            [
                "output/",
                "artifacts/",
                ".super-dev/runs/",
                ".super-dev/review-state/",
                "/.agent/",
                "/.claude/",
                "/.codebuddy/",
                "/.cursor/",
                "/.gemini/",
                "/.iflow/",
                "/.kimi/",
                "/.kiro/",
                "/.opencode/",
                "/.qoder/",
                "/.trae/",
                "/.windsurf/",
                "/GEMINI.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (project_dir / "super_dev" / "__init__.py").write_text('__version__ = "2.0.11"\n', encoding="utf-8")
    (project_dir / "README.md").write_text(
        "当前版本：`2.0.11`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "README_EN.md").write_text(
        "Current version: `2.0.11`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
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
    (project_dir / "docs" / "README.md").write_text("用户文档\n维护者文档\n", encoding="utf-8")
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


def _prepare_spec_quality_change(project_dir: Path, change_id: str = "add-proof-ready") -> None:
    generator = SpecGenerator(project_dir)
    generator.init_sdd()
    change = generator.create_change(
        change_id=change_id,
        title="Add Proof Ready",
        description="用于发布前 spec 质量验证",
    )
    generator.scaffold_change_artifacts(change.id)


def test_release_readiness_detects_missing_docs(temp_project_dir: Path) -> None:
    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    assert report.passed is False
    assert "Documentation Coverage" in report.failed_checks or any(
        check.name == "Documentation Coverage" and not check.passed for check in report.checks
    )


def test_release_readiness_passes_when_required_artifacts_exist(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    _prepare_spec_quality_change(temp_project_dir)

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)
    files = evaluator.write(report)

    assert report.passed is True
    assert report.score == 100
    assert files["markdown"].exists()
    assert files["json"].exists()


def test_release_readiness_fails_when_latest_spec_quality_is_weak(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    generator = SpecGenerator(temp_project_dir)
    generator.init_sdd()
    change = generator.create_change(
        change_id="weak-change",
        title="Weak Change",
        description="弱规格",
    )
    change_dir = temp_project_dir / ".super-dev" / "changes" / change.id
    (change_dir / "tasks.md").write_text("# Tasks\n\n", encoding="utf-8")

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    spec_check = next(check for check in report.checks if check.name == "Spec Quality")
    assert spec_check.passed is False
    assert "weak-change" in spec_check.detail


def test_release_readiness_fails_when_latest_spec_contains_tbd_placeholders(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    _prepare_spec_quality_change(temp_project_dir, change_id="placeholder-change")

    spec_file = next((temp_project_dir / ".super-dev" / "changes" / "placeholder-change" / "specs").rglob("spec.md"))
    spec_file.write_text(
        "# Placeholder Change\n\n## Requirements\n\n### Requirement: Example\n\nSHALL keep placeholder\n\n#### Scenario 1: TBD\n- DETAIL REQUIRED\n",
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    spec_check = next(check for check in report.checks if check.name == "Spec Quality")
    assert spec_check.passed is False
    assert "placeholder-change" in spec_check.detail
