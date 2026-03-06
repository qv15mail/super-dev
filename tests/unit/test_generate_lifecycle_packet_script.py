import json
import subprocess
import sys
from pathlib import Path


def _script_path() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts" / "generate_lifecycle_packet.py"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _prepare_templates(project_dir: Path) -> None:
    root = project_dir / "knowledge" / "development" / "15-lifecycle-templates"
    _write(
        root / "template-catalog.yaml",
        "\n".join(
            [
                "template_catalog:",
                "  requirement:",
                "    file: requirement-template.md",
                "  design:",
                "    file: design-handoff-template.md",
                "  architecture:",
                "    file: architecture-adr-template.md",
                "  implementation:",
                "    file: implementation-pr-template.md",
                "  testing:",
                "    file: testing-report-template.md",
                "  security:",
                "    file: security-compliance-template.md",
                "  release:",
                "    file: release-change-template.md",
                "  operations:",
                "    file: operations-runbook-template.md",
                "  incident_learning:",
                "    file: postmortem-template.md",
                "  governance:",
                "    file: lifecycle-review-board-template.md",
            ]
        ),
    )
    files = [
        "requirement-template.md",
        "design-handoff-template.md",
        "architecture-adr-template.md",
        "implementation-pr-template.md",
        "testing-report-template.md",
        "security-compliance-template.md",
        "release-change-template.md",
        "operations-runbook-template.md",
        "postmortem-template.md",
        "lifecycle-review-board-template.md",
    ]
    for name in files:
        _write(root / name, "# 开发：Excellent（11964948@qq.com）\n")


def test_generate_lifecycle_packet_script_generates_manifest(temp_project_dir: Path) -> None:
    _prepare_templates(temp_project_dir)
    output_dir = temp_project_dir / "artifacts" / "lifecycle-packets"
    proc = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--project-dir",
            str(temp_project_dir),
            "--output-dir",
            str(output_dir),
            "--name",
            "demo-packet",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "[PASS]" in proc.stdout
    manifest_path = output_dir / "demo-packet" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "requirement" in manifest["stages"]
    assert "incident_learning" in manifest["stages"]


def test_generate_lifecycle_packet_script_fails_when_template_missing(temp_project_dir: Path) -> None:
    _prepare_templates(temp_project_dir)
    missing = temp_project_dir / "knowledge" / "development" / "15-lifecycle-templates" / "postmortem-template.md"
    missing.unlink()
    proc = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--project-dir",
            str(temp_project_dir),
            "--name",
            "broken-packet",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "[FAIL]" in proc.stdout
