"""
平台集成管理测试
"""

from pathlib import Path
from urllib import error as urllib_error

import pytest

from super_dev.integrations import IntegrationManager
from super_dev.skills import SkillManager


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

    def test_codex_setup_upserts_root_agents_without_clobbering_existing_content(self, temp_project_dir: Path):
        agents = temp_project_dir / "AGENTS.md"
        agents.write_text("# Existing Project Rules\n\n- Keep current behavior.\n", encoding="utf-8")

        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("codex-cli", force=True)

        assert [item.resolve() for item in files] == [agents.resolve()]
        content = agents.read_text(encoding="utf-8")
        assert "# Existing Project Rules" in content
        assert "BEGIN SUPER DEV CODEX" in content
        assert "super-dev:" in content
        assert "super-dev：" in content
        assert "output/*-prd.md" in content
        assert "actual project files" in content or "repository workspace" in content

    def test_adapter_profiles_cover_all_targets(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        profiles = manager.list_adapter_profiles()
        assert len(profiles) == len(IntegrationManager.TARGETS)
        by_host = {item.host: item for item in profiles}
        assert set(by_host.keys()) == set(IntegrationManager.TARGETS.keys())

        antigravity = by_host["antigravity"]
        assert antigravity.category == "ide"
        assert antigravity.usage_mode == "native-slash"
        assert antigravity.trigger_command == '/super-dev "<需求描述>"'
        assert antigravity.host_protocol_mode == "official-workflow"
        assert antigravity.host_protocol_summary == "GEMINI.md + commands + workflows + skills"
        assert "GEMINI.md" in antigravity.integration_files
        assert ".agent/workflows/super-dev.md" in antigravity.integration_files
        assert ".gemini/commands/super-dev.md" in antigravity.official_project_surfaces
        assert "~/.gemini/GEMINI.md" in antigravity.official_user_surfaces
        assert "~/.gemini/skills/super-dev-core/SKILL.md" in antigravity.official_user_surfaces
        assert antigravity.requires_restart_after_onboard is True

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

        codebuddy = by_host["codebuddy"]
        assert codebuddy.host_protocol_mode == "official-subagent"
        assert codebuddy.host_protocol_summary == "官方 commands + agents + skills"
        assert ".codebuddy/agents/super-dev-core.md" in codebuddy.integration_files
        assert ".codebuddy/agents/super-dev-core.md" in codebuddy.official_project_surfaces
        assert "~/.codebuddy/agents/super-dev-core.md" in codebuddy.official_user_surfaces
        assert "~/.codebuddy/skills/super-dev-core/SKILL.md" in codebuddy.official_user_surfaces

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

        iflow = by_host["iflow"]
        assert iflow.precondition_status == "host-auth-required"
        assert iflow.precondition_guidance
        assert any("/auth" in item for item in iflow.precondition_guidance)
        assert iflow.precondition_label in {"需宿主鉴权", "已检测到鉴权配置"}
        assert any(item["status"] == "project-context-required" for item in iflow.precondition_items)
        assert any(item["status"] == "host-auth-required" for item in iflow.precondition_items)

        assert codex.precondition_status == "session-restart-required"
        assert any("重开宿主会话" in item["label"] for item in codex.precondition_items)
        assert any(item["status"] == "project-context-required" for item in codex.precondition_items)
        assert any("目标项目目录" in item for item in codex.precondition_guidance)

        cursor = by_host["cursor"]
        assert cursor.precondition_status == "project-context-required"
        assert cursor.precondition_items
        assert any("目标项目" in item for item in cursor.precondition_guidance)

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

        roo = by_host["roo-code"]
        assert roo.host_protocol_mode == "official-skill"
        assert roo.capability_labels["slash"] == "native"
        assert roo.slash_command_file == ".roo/commands/super-dev.md"
        assert ".roo/rules/super-dev.md" in roo.official_project_surfaces

        copilot = by_host["vscode-copilot"]
        assert copilot.host_protocol_mode == "official-context"
        assert copilot.capability_labels["slash"] == "none"
        assert copilot.trigger_command == "super-dev: <需求描述>"
        assert ".github/copilot-instructions.md" in copilot.official_project_surfaces

        aider = by_host["aider"]
        assert aider.category == "cli"
        assert aider.capability_labels["slash"] == "none"
        assert aider.capability_labels["skills"] == "none"
        assert "aider.chat/docs" in aider.official_docs_url

    def test_adapter_profile_contains_docs_references_and_capability_labels(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        claude = manager.get_adapter_profile("claude-code")
        codex = manager.get_adapter_profile("codex-cli")

        assert len(claude.official_docs_references) >= 2
        assert claude.capability_labels["slash"] == "native"
        assert claude.capability_labels["skills"] == "none"
        assert claude.capability_labels["trigger"] == "slash"

        assert codex.capability_labels["slash"] == "none"
        assert codex.capability_labels["trigger"] == "text"
        assert codex.capability_labels["skills"] == "official"

    def test_verify_official_docs_reports_reachability(self, temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch):
        manager = IntegrationManager(temp_project_dir)

        class _Resp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def _fake_urlopen(req, timeout=0):
            return _Resp()

        monkeypatch.setattr("super_dev.integrations.manager.urllib_request.urlopen", _fake_urlopen)

        result = manager.verify_official_docs("claude-code")
        assert result["status"] == "verified"
        assert result["reachable"] == result["checked"]
        assert result["checked"] >= 2

    def test_host_hardening_blueprint_contains_steps(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        codex = manager.host_hardening_blueprint("codex-cli")
        claude = manager.host_hardening_blueprint("claude-code")

        assert codex["trigger_mode"] == "text"
        assert any("install skill" in step for step in codex["required_steps"])
        assert claude["trigger_mode"] == "slash"
        assert any("setup project slash command" in step for step in claude["required_steps"])

    def test_compare_official_capabilities_reports_alignment(self, temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch):
        manager = IntegrationManager(temp_project_dir)

        class _Resp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self, size=-1):
                return b"slash commands rules skills sub-agents instructions"

        def _fake_urlopen(req, timeout=0):
            return _Resp()

        monkeypatch.setattr("super_dev.integrations.manager.urllib_request.urlopen", _fake_urlopen)

        result = manager.compare_official_capabilities("claude-code")
        assert result["status"] == "passed"
        assert result["reachable_urls"] >= 1
        checks = result["checks"]
        assert checks["slash"]["ok"] is True
        assert checks["rules"]["ok"] is True

    def test_verify_official_docs_fallbacks_head_to_get(self, temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch):
        manager = IntegrationManager(temp_project_dir)

        class _Resp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def _fake_urlopen(req, timeout=0, context=None):
            method = req.get_method()
            if method == "HEAD":
                raise urllib_error.HTTPError(req.full_url, 405, "Method Not Allowed", {}, None)
            return _Resp()

        monkeypatch.setattr("super_dev.integrations.manager.urllib_request.urlopen", _fake_urlopen)

        result = manager.verify_official_docs("claude-code")
        assert result["status"] == "verified"
        assert result["reachable"] == result["checked"]
        assert all(item.get("method") == "GET" for item in result["details"])

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

    def test_trae_rules_require_workspace_artifacts_and_fullwidth_trigger(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        content = manager._trae_rules()

        assert "super-dev：" in content
        assert "project workspace" in content
        assert "instead of only replying in chat" in content
        assert "treat the step as incomplete" in content

    def test_embedded_skill_and_host_specific_surfaces_require_written_artifacts(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)

        embedded = manager._build_embedded_skill_content()
        antigravity = manager._build_antigravity_context_content()
        claude_agent = manager._build_claude_agent_content()
        codebuddy_agent = manager._build_codebuddy_agent_content()
        workflow = manager._antigravity_workflow_rules()

        assert "super-dev：" in embedded
        assert "必须真实写入项目文件" in embedded
        assert "Chat-only summaries do not count" in antigravity
        assert "write them as project files" in antigravity
        assert "workspace files" in claude_agent
        assert "chat-only summaries" in claude_agent
        assert "workspace files" in codebuddy_agent
        assert "chat-only explanations" in codebuddy_agent
        assert "只在聊天里总结不算完成" in workflow
        assert "必须暂停等待用户确认" in workflow

    def test_managed_surfaces_all_pass_contract_audit(self, temp_project_dir: Path, monkeypatch: pytest.MonkeyPatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))

        manager = IntegrationManager(temp_project_dir)
        skill_manager = SkillManager(temp_project_dir)

        for target in IntegrationManager.TARGETS:
            manager.setup(target, force=True)
            manager.setup_global_protocol(target, force=True)
            if manager.supports_slash(target):
                manager.setup_slash_command(target, force=True)
                manager.setup_global_slash_command(target, force=True)
            if IntegrationManager.requires_skill(target):
                skill_root = skill_manager._target_dir(target)
                if skill_manager.target_path_kind(target) == "observed-compatibility-surface":
                    skill_root.mkdir(parents=True, exist_ok=True)
                if skill_manager.skill_surface_available(target):
                    skill_manager.install("super-dev", target=target, name="super-dev-core", force=True)

            surfaces = manager.collect_managed_surface_paths(target)
            for _, path in surfaces.items():
                if not path.exists():
                    continue
                content = path.read_text(encoding="utf-8")
                missing = manager.audit_surface_contract(target, _, path, content)
                assert missing == [], f"{target} surface {path} missing contract markers: {missing}"

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

    def test_setup_injects_system_flow_contract_marker(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("qoder", force=True)
        assert files
        content = files[0].read_text(encoding="utf-8")
        assert "SUPER_DEV_FLOW_CONTRACT_V1" in content
        assert "PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery" in content

    def test_iflow_toml_slash_command_injects_flow_contract_comment(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        command_file = manager.setup_slash_command(target="iflow", force=True)
        assert command_file is not None
        assert command_file.suffix == ".toml"
        content = command_file.read_text(encoding="utf-8")
        assert "# SUPER_DEV_FLOW_CONTRACT_V1" in content
        assert "# DOC_CONFIRM_GATE: required" in content

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
        assert manager.supports_slash("antigravity") is True
        assert manager.requires_skill("kimi-cli") is True
        assert manager.requires_skill("codebuddy") is True
        assert manager.setup_slash_command(target="kiro", force=True) is None
        assert manager.setup_slash_command(target="qoder", force=True) is not None
        assert manager.setup_slash_command(target="antigravity", force=True) is not None
        assert manager.setup_slash_command(target="trae", force=True) is None
        assert manager.setup_global_slash_command(target="trae", force=True) is None

    @pytest.mark.parametrize(
        ("target", "command_file"),
        [
            ("antigravity", ".gemini/commands/super-dev.md"),
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
