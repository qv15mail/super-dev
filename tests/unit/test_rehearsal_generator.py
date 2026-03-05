from pathlib import Path

from super_dev.deployers.rehearsal import LaunchRehearsalGenerator


def test_rehearsal_generator_outputs_markdown_files(temp_project_dir: Path) -> None:
    generator = LaunchRehearsalGenerator(
        project_dir=temp_project_dir,
        name="demo-app",
        tech_stack={"platform": "web", "frontend": "react", "backend": "python", "domain": "saas"},
    )

    files = generator.generate(cicd_platform="github")

    assert "output/rehearsal/demo-app-launch-rehearsal.md" in files
    assert "output/rehearsal/demo-app-rollback-playbook.md" in files
    assert "output/rehearsal/demo-app-smoke-checklist.md" in files
    assert "Launch Rehearsal" in files["output/rehearsal/demo-app-launch-rehearsal.md"]
    assert "Rollback Playbook" in files["output/rehearsal/demo-app-rollback-playbook.md"]
