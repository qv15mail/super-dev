"""
平台集成管理测试
"""

from pathlib import Path

import pytest

from super_dev.integrations import IntegrationManager


class TestIntegrationManager:
    def test_coverage_gaps_are_empty(self):
        gaps = IntegrationManager.coverage_gaps()
        assert gaps["missing_in_targets"] == []
        assert gaps["extra_in_targets"] == []
        assert gaps["missing_in_slash"] == []
        assert gaps["extra_in_slash"] == []
        assert gaps["missing_in_docs_map"] == []
        assert gaps["extra_in_docs_map"] == []
        assert gaps["missing_official_docs_url"] == []
        assert gaps["unverified_docs"] == []

    @pytest.mark.parametrize(
        "target, expected_file",
        [(name, config.files[0]) for name, config in IntegrationManager.TARGETS.items()],
    )
    def test_setup_single_target(self, temp_project_dir: Path, target: str, expected_file: str):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup(target, force=True)

        assert len(files) == len(IntegrationManager.TARGETS[target].files)
        rule_file = temp_project_dir / expected_file
        assert rule_file.exists()
        content = rule_file.read_text(encoding="utf-8")
        assert "Super Dev" in content

    def test_setup_all_targets(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        result = manager.setup_all(force=True)

        assert set(result.keys()) == set(IntegrationManager.TARGETS.keys())
        for target in IntegrationManager.TARGETS.values():
            for file_path in target.files:
                full_path = temp_project_dir / file_path
                assert full_path.exists()
                assert "Super Dev" in full_path.read_text(encoding="utf-8")

    def test_adapter_profiles_cover_all_targets(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        profiles = manager.list_adapter_profiles()
        assert len(profiles) == len(IntegrationManager.TARGETS)
        by_host = {item.host: item for item in profiles}
        assert set(by_host.keys()) == set(IntegrationManager.TARGETS.keys())

        codex = by_host["codex-cli"]
        assert codex.category == "cli"
        assert codex.adapter_mode == "native-cli-session"
        assert codex.terminal_entry_scope.startswith("仅触发本地编排")
        assert codex.slash_command_file == ""
        assert codex.skill_dir.startswith("~/.codex/")
        assert codex.certification_level == "certified"
        assert codex.certification_label == "Certified"
        assert codex.certification_reason
        assert codex.certification_evidence
        assert codex.usage_mode == "agents-and-skill"
        assert codex.requires_restart_after_onboard is True
        assert codex.trigger_command == "super-dev: <需求描述>"
        assert "重启 codex" in codex.usage_location
        assert any("重启 codex" in step for step in codex.post_onboard_steps)
        assert any("不要输入 /super-dev" in note for note in codex.usage_notes)
        assert codex.host_protocol_mode == "official-skill"
        assert codex.host_protocol_summary == "官方 AGENTS.md + 官方 Skills"
        assert "~/.codex/skills/super-dev-core/SKILL.md" in codex.official_user_surfaces
        assert "Skill" in codex.primary_entry or "AGENTS" in codex.notes

        qoder = by_host["qoder"]
        assert qoder.category == "ide"
        assert qoder.adapter_mode == "native-ide-rule-file"
        assert qoder.integration_files[0] == ".qoder/rules.md"
        assert qoder.docs_verified is True
        assert qoder.certification_level == "experimental"
        assert qoder.usage_mode == "native-slash"
        assert qoder.slash_command_file == ".qoder/commands/super-dev.md"
        assert ".qoder/rules.md" in qoder.official_project_surfaces
        assert "~/.qoder/commands/super-dev.md" in qoder.official_user_surfaces
        assert "~/.qoderwork/skills/super-dev-core/SKILL.md" in qoder.official_user_surfaces
        assert ".qoder/skills/super-dev-core/SKILL.md" in qoder.official_project_surfaces

        claude = by_host["claude-code"]
        assert claude.host_protocol_mode == "official-subagent"
        assert claude.host_protocol_summary == "官方 commands + subagents"
        assert ".claude/agents/super-dev-core.md" in claude.official_project_surfaces
        assert "~/.claude/agents/super-dev-core.md" in claude.official_user_surfaces
        assert claude.skill_dir == ""

        gemini = by_host["gemini-cli"]
        assert gemini.host_protocol_mode == "official-context"
        assert gemini.host_protocol_summary == "官方 commands + GEMINI.md"
        assert "GEMINI.md" in gemini.official_project_surfaces
        assert "~/.gemini/GEMINI.md" in gemini.official_user_surfaces

        kimi = by_host["kimi-cli"]
        assert kimi.category == "cli"
        assert kimi.host_protocol_mode == "official-context"
        assert kimi.host_protocol_summary == "官方 AGENTS.md + 文本触发"
        assert kimi.docs_verified is True
        assert kimi.certification_level == "experimental"
        assert kimi.slash_command_file == ""
        assert kimi.skill_dir == "~/.kimi/skills"
        assert kimi.usage_mode == "agents-and-skill"
        assert kimi.trigger_command == "super-dev: <需求描述>"
        assert ".kimi/AGENTS.md" in kimi.integration_files
        assert "~/.kimi/skills/super-dev-core/SKILL.md" in kimi.observed_compatibility_surfaces
        assert "SMOKE_OK" in kimi.smoke_test_prompt
        assert kimi.smoke_test_steps
        assert "SMOKE_OK" in kimi.smoke_success_signal

        kiro_cli = by_host["kiro-cli"]
        assert kiro_cli.host_protocol_mode == "official-context"
        assert kiro_cli.host_protocol_summary == "官方 commands + AGENTS.md"
        assert ".kiro/AGENTS.md" in kiro_cli.official_project_surfaces

        kiro = by_host["kiro"]
        assert kiro.host_protocol_mode == "official-steering"
        assert ".kiro/steering/super-dev.md" in kiro.official_project_surfaces
        assert "~/.kiro/steering/AGENTS.md" in kiro.official_user_surfaces

    def test_qoder_rules_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("qoder", force=True)

        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        assert "Super Dev" in content

    def test_slash_content_requires_host_research_first(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        content = manager._build_slash_command_content("claude-code")

        assert "output/*-research.md" in content
        assert "同类产品" in content
        assert "宿主原生联网" in content or "browse / search" in content
        assert "宿主负责调用自身模型" in content or "编码能力来自当前宿主" in content
        assert "Super Dev 是当前项目里的本地 Python 工具 + 宿主规则/Skill 协议" in content
        assert "output/knowledge-cache/*-knowledge-bundle.json" in content
        assert "首轮响应契约（首次触发必须执行）" in content
        assert "第一轮回复必须明确当前阶段是 `research`" in content
        assert "三份核心文档完成后会暂停并等待用户确认" in content
        assert "未经用户明确确认，不得进入 Spec 或编码" in content
        assert "先按 `tasks.md` 实现并运行前端" in content

    def test_generic_rules_emphasize_host_governance_boundary(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)

        cli_rules = manager._generic_cli_rules("cursor-cli")
        ide_rules = manager._generic_ide_rules("cursor")
        claude_rules = manager._claude_rules()

        assert "The host remains responsible for model execution" in cli_rules
        assert "Treat Super Dev as a local Python CLI plus host-side rules/skills" in cli_rules
        assert "First-Response Contract" in cli_rules
        assert "current phase is `research`" in cli_rules
        assert "stop after the three core documents and wait for approval" in cli_rules
        assert "Read relevant files under `knowledge/` before drafting documents." in cli_rules
        assert "wait for explicit confirmation before creating Spec or coding" in cli_rules
        assert "host remains responsible for actual coding" in ide_rules
        assert "Read relevant files under `knowledge/` before drafting the three core documents." in ide_rules
        assert "Treat Super Dev as the local Python workflow tool plus this host rule file" in ide_rules
        assert "First-Response Contract" in ide_rules
        assert "current phase is `research`" in ide_rules
        assert "Claude Code remains the execution host" in claude_rules
        assert "Read relevant files under `knowledge/` before drafting PRD, architecture, and UIUX." in claude_rules
        assert "First-Response Contract" in claude_rules
        assert "stop after the three core documents and wait for approval" in claude_rules
        assert "wait for explicit confirmation before creating Spec or coding" in claude_rules

    @pytest.mark.parametrize(
        "target, expected_file",
        list(IntegrationManager.SLASH_COMMAND_FILES.items()),
    )
    def test_setup_slash_command(self, temp_project_dir: Path, target: str, expected_file: str):
        manager = IntegrationManager(temp_project_dir)
        command_file = manager.setup_slash_command(target=target, force=True)

        assert command_file is not None
        assert command_file.resolve() == (temp_project_dir / expected_file).resolve()
        assert command_file.exists()
        content = command_file.read_text(encoding="utf-8")
        if command_file.suffix == ".toml":
            assert "{{args}}" in content
            assert "super-dev create" in content
        else:
            assert "/super-dev" in content
            assert "$ARGUMENTS" in content
            assert 'super-dev create "$ARGUMENTS"' in content

    def test_setup_global_slash_command(self, temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))

        manager = IntegrationManager(temp_project_dir)
        command_file = manager.setup_global_slash_command(target="claude-code", force=True)

        assert command_file is not None
        expected = fake_home / ".claude" / "commands" / "super-dev.md"
        assert command_file.resolve() == expected.resolve()
        assert expected.exists()

    def test_setup_global_slash_command_opencode_uses_config_dir(
        self,
        temp_project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))

        manager = IntegrationManager(temp_project_dir)
        command_file = manager.setup_global_slash_command(target="opencode", force=True)

        assert command_file is not None
        expected = fake_home / ".config" / "opencode" / "commands" / "super-dev.md"
        assert command_file.resolve() == expected.resolve()
        assert expected.exists()

    def test_skill_only_target_skips_slash_mapping(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        assert manager.supports_slash("codex-cli") is False
        assert manager.supports_slash("kimi-cli") is False
        assert manager.setup_slash_command(target="codex-cli", force=True) is None
        assert manager.setup_slash_command(target="kimi-cli", force=True) is None
        assert manager.setup_global_slash_command(target="codex-cli", force=True) is None
        assert manager.setup_global_slash_command(target="kimi-cli", force=True) is None
        assert manager.supports_slash("kiro") is False
        assert manager.supports_slash("qoder") is True
        assert manager.supports_slash("trae") is False
        assert manager.requires_skill("kimi-cli") is True
        assert manager.setup_slash_command(target="kiro", force=True) is None
        assert manager.setup_slash_command(target="qoder", force=True) is not None
        assert manager.setup_slash_command(target="trae", force=True) is None
        assert manager.setup_global_slash_command(target="trae", force=True) is None

    @pytest.mark.parametrize(
        ("target", "command_file"),
        [
            ("codebuddy", ".codebuddy/commands/super-dev.md"),
            ("cursor", ".cursor/commands/super-dev.md"),
            ("windsurf", ".windsurf/workflows/super-dev.md"),
            ("gemini-cli", ".gemini/commands/super-dev.md"),
            ("opencode", ".opencode/commands/super-dev.md"),
        ],
    )
    def test_verified_hosts_preserve_native_slash_model(
        self,
        temp_project_dir: Path,
        target: str,
        command_file: str,
    ):
        manager = IntegrationManager(temp_project_dir)
        profile = manager.get_adapter_profile(target)

        assert manager.supports_slash(target) is True
        assert profile.usage_mode == "native-slash"
        assert profile.trigger_command == '/super-dev "<需求描述>"'
        assert profile.slash_command_file == command_file
