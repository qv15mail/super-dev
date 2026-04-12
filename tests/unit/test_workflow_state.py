from __future__ import annotations

import json
from pathlib import Path

from super_dev.workflow_state import (
    build_host_entry_prompts,
    build_host_flow_probe,
    detect_pipeline_summary,
)


def test_build_host_entry_prompts_supports_seeai_codex():
    payload = build_host_entry_prompts(
        target="codex-cli",
        instruction="继续当前比赛项目",
        supports_slash=False,
        flow_variant="seeai",
    )

    prompts = payload["entry_prompts"]
    assert prompts["app_desktop"].startswith('/super-dev-seeai "')
    assert prompts["cli"].startswith('$super-dev-seeai "')
    assert prompts["fallback"].startswith("super-dev-seeai:")


def test_build_host_flow_probe_uses_adapter_for_codebuddy_and_openclaw():
    codebuddy_probe = build_host_flow_probe("codebuddy-cli")
    openclaw_probe = build_host_flow_probe("openclaw")

    assert codebuddy_probe["enabled"] is True
    assert "CodeBuddy" in codebuddy_probe["title"]
    assert any("super-dev-seeai" in step for step in codebuddy_probe["steps"])
    assert "SEEAI" in codebuddy_probe["success_signal"]

    assert openclaw_probe["enabled"] is True
    assert "OpenClaw" in openclaw_probe["title"]
    assert any("super-dev-seeai" in step for step in openclaw_probe["steps"])
    assert "SEEAI" in openclaw_probe["success_signal"]


def test_build_host_flow_probe_preserves_codex_special_probe():
    codex_probe = build_host_flow_probe("codex-cli")

    assert codex_probe["enabled"] is True
    assert codex_probe["title"] == "Codex 三入口同流程验收"
    assert any("App/Desktop" in step for step in codex_probe["steps"])


def test_detect_pipeline_summary_seeai_skips_preview_gate(temp_project_dir: Path):
    superdev_dir = temp_project_dir / ".super-dev"
    review_state_dir = superdev_dir / "review-state"
    output_dir = temp_project_dir / "output"
    changes_dir = superdev_dir / "changes" / "demo-change"
    review_state_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    changes_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / f"{temp_project_dir.name}-research.md").write_text("research", encoding="utf-8")
    (output_dir / f"{temp_project_dir.name}-prd.md").write_text("prd", encoding="utf-8")
    (output_dir / f"{temp_project_dir.name}-architecture.md").write_text(
        "architecture", encoding="utf-8"
    )
    (output_dir / f"{temp_project_dir.name}-uiux.md").write_text("uiux", encoding="utf-8")
    (changes_dir / "proposal.md").write_text("proposal", encoding="utf-8")
    (changes_dir / "tasks.md").write_text("tasks", encoding="utf-8")
    (output_dir / f"{temp_project_dir.name}-frontend-runtime.json").write_text(
        json.dumps({"passed": True}),
        encoding="utf-8",
    )
    (superdev_dir / "workflow-state.json").write_text(
        json.dumps({"flow_variant": "seeai"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = detect_pipeline_summary(temp_project_dir)

    assert summary["flow_variant"] == "seeai"
    assert summary["workflow_status"] == "missing_backend"
    assert "SEEAI" in summary["recommended_command"]
