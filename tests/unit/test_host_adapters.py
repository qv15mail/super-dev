from super_dev.host_adapters import (
    SpecialAdapterContext,
    build_special_usage_profile,
    get_adapter_mode_override,
    get_competition_smoke_extra_steps,
    get_pass_criteria,
    get_resume_checklist,
    get_runtime_checklist,
    get_special_install_surfaces,
    render_manual_install_guidance,
)


def test_workbuddy_special_adapter_builds_manual_usage_profile():
    profile = build_special_usage_profile(
        SpecialAdapterContext(
            target="workbuddy",
            category="ide",
            usage_location="WorkBuddy 当前任务会话",
            usage_notes=("note-a",),
        )
    )

    assert profile is not None
    assert profile["usage_mode"] == "manual-workbench-skill"
    assert profile["trigger_context"] == "WorkBuddy 当前任务/对话会话"
    assert profile["entry_variants"][1]["entry"] == "super-dev-seeai: <需求描述>"
    assert "WorkBuddy" in profile["notes"]


def test_openclaw_manual_install_guidance_renders_docs_and_doctor_hint():
    payload = render_manual_install_guidance(
        host_id="openclaw",
        command_name="setup",
        docs=["https://docs.openclaw.ai/plugins/building-plugins"],
    )

    assert payload is not None
    assert payload["title"] == "OpenClaw 手动安装"
    assert any("@super-dev/openclaw-plugin" in line for line in payload["lines"])
    assert any("super-dev doctor --host openclaw" in line for line in payload["lines"])
    assert any("官方文档:" == line for line in payload["lines"])


def test_codebuddy_special_adapter_exposes_competition_steps_and_surfaces():
    steps = get_competition_smoke_extra_steps("codebuddy")
    surfaces = get_special_install_surfaces("codebuddy")

    assert any("P0/P1/P2" in step for step in steps)
    assert surfaces is not None
    assert ".codebuddy/commands/super-dev-seeai.md" in surfaces["official_project_surfaces"]
    assert "~/.codebuddy/skills/super-dev-seeai/SKILL.md" in surfaces["official_user_surfaces"]


def test_workbuddy_adapter_mode_override_is_manual_workbench_skill():
    assert get_adapter_mode_override("workbuddy") == "manual-workbench-skill"
    assert get_adapter_mode_override("claude-code") == ""


def test_runtime_validation_helpers_expose_structured_metadata():
    for host_id in ("codebuddy-cli", "codebuddy", "openclaw", "workbuddy"):
        runtime_checklist = get_runtime_checklist(host_id)
        pass_criteria = get_pass_criteria(host_id)
        resume_checklist = get_resume_checklist(host_id)

        assert runtime_checklist
        assert pass_criteria
        assert resume_checklist
        assert all(isinstance(item, str) for item in runtime_checklist)
        assert all(isinstance(item, str) for item in pass_criteria)
        assert all(isinstance(item, str) for item in resume_checklist)


def test_runtime_validation_payload_is_present_in_usage_profiles():
    profile = build_special_usage_profile(
        SpecialAdapterContext(
            target="openclaw",
            category="plugin",
            usage_location="OpenClaw Agent 会话",
            usage_notes=("note-a",),
        )
    )

    assert profile is not None
    runtime_validation = profile["runtime_validation"]
    assert runtime_validation["runtime_checklist"]
    assert runtime_validation["pass_criteria"]
    assert runtime_validation["resume_checklist"]
