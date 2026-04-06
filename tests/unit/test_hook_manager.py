from pathlib import Path

from super_dev.hooks.manager import HookManager
from super_dev.review_state import save_docs_confirmation


def test_workflow_event_hook_dispatches_from_review_state(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo"
    project_dir.mkdir(parents=True, exist_ok=True)
    marker = project_dir / "workflow-hook.txt"
    (project_dir / "super-dev.yaml").write_text(
        "\n".join(
            [
                "hooks:",
                "  WorkflowEvent:",
                '    - matcher: "docs_confirmation_saved"',
                "      type: command",
                f"      command: \"python3 -c \\\"from pathlib import Path; import os; Path(r'{marker}').write_text(os.environ.get('SUPER_DEV_PHASE', ''), encoding='utf-8')\\\"\"",
                "      blocking: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    save_docs_confirmation(
        project_dir,
        {
            "status": "confirmed",
            "current_step_label": "三文档已确认",
        },
    )

    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "docs_confirmation_saved"

    history = HookManager.load_recent_history(project_dir, limit=5)
    assert history
    latest = history[0]
    assert latest.event == "WorkflowEvent"
    assert latest.phase == "docs_confirmation_saved"
    assert latest.source == "config"
    assert latest.success is True
