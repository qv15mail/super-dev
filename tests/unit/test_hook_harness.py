import json
from pathlib import Path

from super_dev.hook_harness import HookHarnessBuilder
from super_dev.hooks.manager import HookManager


def test_hook_harness_disabled_without_history(tmp_path: Path) -> None:
    report = HookHarnessBuilder(tmp_path / "demo").build()
    assert report.enabled is False
    assert report.passed is False


def test_hook_harness_reports_blocked_history(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo"
    history_file = HookManager.hook_history_file(project_dir)
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "hook_name": "python3 scripts/check.py",
                        "event": "WorkflowEvent",
                        "success": True,
                        "output": "",
                        "error": "",
                        "duration_ms": 10.0,
                        "blocked": False,
                        "phase": "docs_confirmation_saved",
                        "source": "config",
                        "timestamp": "2026-04-06T01:02:03+00:00",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "hook_name": "python3 scripts/guard.py",
                        "event": "WorkflowEvent",
                        "success": False,
                        "output": "",
                        "error": "blocked by policy",
                        "duration_ms": 9.0,
                        "blocked": True,
                        "phase": "quality_revision_saved",
                        "source": "config",
                        "timestamp": "2026-04-06T01:03:03+00:00",
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = HookHarnessBuilder(project_dir).build()
    assert report.enabled is True
    assert report.total_events == 2
    assert report.blocked_count == 1
    assert report.failed_count == 1
    assert report.passed is False
    assert report.blockers
