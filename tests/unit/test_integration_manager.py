"""
平台集成管理测试
"""

from pathlib import Path
from urllib import error as urllib_error

import pytest

from super_dev.catalogs import PRIMARY_HOST_TOOL_IDS
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

        assert len(files) >= len(IntegrationManager.TARGETS[target].files)
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
        project_skill = temp_project_dir / ".agents" / "skills" / "super-dev" / "SKILL.md"

        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("codex-cli", force=True)

        plugin_marketplace = temp_project_dir / ".agents" / "plugins" / "marketplace.json"
        plugin_manifest = (
            temp_project_dir / "plugins" / "super-dev-codex" / ".codex-plugin" / "plugin.json"
        )
        plugin_skill = temp_project_dir / "plugins" / "super-dev-codex" / "skills" / "super-dev" / "SKILL.md"
        assert {agents.resolve(), project_skill.resolve(), plugin_marketplace.resolve(), plugin_manifest.resolve(), plugin_skill.resolve()} <= {
            item.resolve() for item in files
        }
        content = agents.read_text(encoding="utf-8")
        assert "# Existing Project Rules" in content
        assert "BEGIN SUPER DEV CODEX" in content
        assert "super-dev:" in content
        assert "super-dev：" in content
        assert "output/*-prd.md" in content
        assert "actual project files" in content or "repository workspace" in content
        assert "Do not spend a turn saying you will read the skill first" in content
        assert project_skill.exists()

    def test_codex_setup_global_protocol_writes_global_codex_agents(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))

        manager = IntegrationManager(temp_project_dir)
        global_file = manager.setup_global_protocol("codex-cli", force=True)

        expected = fake_home / ".codex" / "AGENTS.md"
        assert global_file == expected
        assert expected.exists()
        content = expected.read_text(encoding="utf-8")
        assert "BEGIN SUPER DEV CODEX" in content
        assert "super-dev:" in content
        assert "$super-dev" in content
        assert "/` list" in content or "`/` list" in content

    def test_codex_global_protocol_and_skill_paths_follow_codex_home(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        codex_home = temp_project_dir / "custom-codex-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        codex_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        monkeypatch.setenv("CODEX_HOME", str(codex_home))

        manager = IntegrationManager(temp_project_dir)

        assert manager.resolve_global_protocol_path("codex-cli") == codex_home / "AGENTS.md"
        paths = manager.expected_skill_paths("codex-cli")
        normalized = {path.as_posix() for path in paths}
        assert any(item.endswith("/.agents/skills/super-dev/SKILL.md") for item in normalized)
        assert any(item.endswith("/custom-codex-home/skills/super-dev/SKILL.md") for item in normalized)
        assert any(item.endswith("/custom-codex-home/skills/super-dev-core/SKILL.md") for item in normalized)

    def test_codex_expected_skill_paths_include_compatibility_mirror(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        paths = manager.expected_skill_paths("codex-cli")
        normalized = {path.as_posix() for path in paths}
        assert any(item.endswith("/.agents/skills/super-dev/SKILL.md") for item in normalized)
        assert any(item.endswith("/.agents/skills/super-dev-core/SKILL.md") for item in normalized)
        assert any(item.endswith("/.codex/skills/super-dev/SKILL.md") for item in normalized)
        assert any(item.endswith("/.codex/skills/super-dev-core/SKILL.md") for item in normalized)

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
        assert antigravity.host_protocol_summary == "官方 commands + workflows + skills"
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
        assert codex.skill_dir.startswith("~/.agents/")
        assert codex.certification_level == "certified"
        assert codex.certification_label == "Certified"
        assert codex.certification_reason
        assert codex.certification_evidence
        assert codex.usage_mode == "agents-and-skill"
        assert codex.requires_restart_after_onboard is True
        assert codex.trigger_command == "super-dev: <需求描述>"
        assert codex.entry_variants
        assert codex.entry_variants[0]["entry"] == "/super-dev"
        assert any(item["entry"] == "$super-dev" for item in codex.entry_variants)
        assert "重启 codex" in codex.usage_location
        assert any("重启 codex" in step for step in codex.post_onboard_steps)
        assert any("Codex 官方不走自定义项目 slash" in note for note in codex.usage_notes)
        assert codex.host_protocol_mode == "official-skill"
        assert codex.host_protocol_summary == "官方 AGENTS.md + 官方 Skills + optional repo plugin enhancement"
        assert codex.capability_labels["slash"] == "skill-list"
        assert ".agents/skills/super-dev/SKILL.md" in codex.official_project_surfaces
        assert ".agents/plugins/marketplace.json" in codex.official_project_surfaces
        assert "plugins/super-dev-codex/.codex-plugin/plugin.json" in codex.official_project_surfaces
        assert "~/.codex/AGENTS.md" in codex.official_user_surfaces
        assert "~/.agents/skills/super-dev/SKILL.md" in codex.official_user_surfaces
        assert "~/.agents/skills/super-dev-core/SKILL.md" in codex.observed_compatibility_surfaces
        assert "~/.codex/skills/super-dev/SKILL.md" in codex.observed_compatibility_surfaces
        assert "~/.codex/skills/super-dev-core/SKILL.md" in codex.observed_compatibility_surfaces
        assert "/` 列表选择 `super-dev`" in codex.primary_entry
        assert "$super-dev" in codex.primary_entry
        assert "从 `/` 列表选择 `super-dev`" in codex.usage_notes[0]

        qoder = by_host["qoder"]
        assert qoder.category == "ide"
        assert qoder.adapter_mode == "native-ide-rule-file"
        assert qoder.integration_files[0] == ".qoder/rules/super-dev.md"
        assert qoder.docs_verified is True
        assert qoder.certification_level == "experimental"
        assert qoder.usage_mode == "native-slash"
        assert qoder.slash_command_file == ".qoder/commands/super-dev.md"
        assert ".qoder/rules/super-dev.md" in qoder.official_project_surfaces
        assert "~/.qoder/commands/super-dev.md" in qoder.official_user_surfaces
        assert "~/.qoder/skills/super-dev-core/SKILL.md" in qoder.official_user_surfaces
        assert ".qoder/skills/super-dev-core/SKILL.md" in qoder.official_project_surfaces
        assert "AGENTS.md" in qoder.observed_compatibility_surfaces

        codebuddy = by_host["codebuddy"]
        assert codebuddy.host_protocol_mode == "official-subagent"
        assert codebuddy.host_protocol_summary == "官方 commands + agents + skills"
        assert ".codebuddy/agents/super-dev-core.md" in codebuddy.integration_files
        assert ".codebuddy/agents/super-dev-core.md" in codebuddy.official_project_surfaces
        assert "~/.codebuddy/agents/super-dev-core.md" in codebuddy.official_user_surfaces
        assert "~/.codebuddy/skills/super-dev-core/SKILL.md" in codebuddy.official_user_surfaces
        assert ".codebuddy/rules.md" in codebuddy.observed_compatibility_surfaces

        codebuddy_cli = by_host["codebuddy-cli"]
        assert codebuddy_cli.host_protocol_summary == "官方 commands + skills + AGENTS.md compatibility"
        assert ".codebuddy/skills/super-dev-core/SKILL.md" in codebuddy_cli.integration_files
        assert ".codebuddy/skills/super-dev-core/SKILL.md" in codebuddy_cli.official_project_surfaces
        assert ".codebuddy/AGENTS.md" in codebuddy_cli.observed_compatibility_surfaces

        claude = by_host["claude-code"]
        assert claude.host_protocol_mode == "official-skill"
        assert claude.host_protocol_summary == "官方 CLAUDE.md + Skills + optional repo plugin enhancement"
        assert "CLAUDE.md" in claude.official_project_surfaces
        assert ".claude/CLAUDE.md" in claude.official_project_surfaces
        assert ".claude/skills/super-dev/SKILL.md" in claude.official_project_surfaces
        assert ".claude/agents/super-dev-core.md" in claude.official_project_surfaces
        assert ".claude/commands/super-dev.md" in claude.official_project_surfaces
        assert ".claude-plugin/marketplace.json" in claude.official_project_surfaces
        assert "plugins/super-dev-claude/.claude-plugin/plugin.json" in claude.official_project_surfaces
        assert "~/.claude/CLAUDE.md" in claude.official_user_surfaces
        assert "~/.claude/skills/super-dev/SKILL.md" in claude.official_user_surfaces
        assert "~/.claude/commands/super-dev.md" in claude.official_user_surfaces
        assert "~/.claude/skills/super-dev-core/SKILL.md" in claude.observed_compatibility_surfaces
        assert "~/.claude/agents/super-dev-core.md" in claude.observed_compatibility_surfaces
        assert claude.skill_dir.startswith("~/.claude/skills")

        gemini = by_host["gemini-cli"]
        assert gemini.host_protocol_mode == "official-context"
        assert gemini.host_protocol_summary == "官方 commands + GEMINI.md"
        assert "GEMINI.md" in gemini.official_project_surfaces
        assert "~/.gemini/GEMINI.md" in gemini.official_user_surfaces
        assert "~/.gemini/commands/super-dev.md" in gemini.official_user_surfaces

        assert codex.precondition_status == "session-restart-required"
        assert any("重开宿主会话" in item["label"] for item in codex.precondition_items)
        assert any(item["status"] == "project-context-required" for item in codex.precondition_items)
        assert any("目标项目目录" in item for item in codex.precondition_guidance)

        cursor = by_host["cursor"]
        assert cursor.precondition_status == "project-context-required"
        assert cursor.precondition_items
        assert any("目标项目" in item for item in cursor.precondition_guidance)
        assert cursor.host_protocol_summary == "官方 commands + rules + AGENTS.md compatibility"
        assert "AGENTS.md" in cursor.observed_compatibility_surfaces

        kiro_cli = by_host["kiro-cli"]
        assert kiro_cli.host_protocol_mode == "official-steering"
        assert kiro_cli.host_protocol_summary == "官方 steering + skills"
        assert ".kiro/steering/super-dev.md" in kiro_cli.official_project_surfaces
        assert ".kiro/skills/super-dev-core/SKILL.md" in kiro_cli.official_project_surfaces
        assert "~/.kiro/skills/super-dev-core/SKILL.md" in kiro_cli.official_user_surfaces

        kiro = by_host["kiro"]
        assert kiro.host_protocol_mode == "official-steering"
        assert ".kiro/steering/super-dev.md" in kiro.official_project_surfaces
        assert "~/.kiro/steering/AGENTS.md" in kiro.official_user_surfaces
        assert "~/.kiro/skills/super-dev-core/SKILL.md" in kiro.official_user_surfaces

        roo = by_host["roo-code"]
        assert roo.host_protocol_mode == "official-skill"
        assert roo.capability_labels["slash"] == "native"
        assert roo.slash_command_file == ".roo/commands/super-dev.md"
        assert roo.host_protocol_summary == "官方 commands + rules"
        assert ".roo/rules/super-dev.md" in roo.official_project_surfaces

        cline = by_host["cline"]
        assert cline.host_protocol_mode == "official-context"
        assert cline.host_protocol_summary == "官方 .clinerules + skills + AGENTS.md compatibility"
        assert ".clinerules/super-dev.md" in cline.official_project_surfaces
        assert ".cline/skills/super-dev-core/SKILL.md" in cline.official_project_surfaces
        assert "~/.cline/skills/super-dev-core/SKILL.md" in cline.official_user_surfaces
        assert "AGENTS.md" in cline.observed_compatibility_surfaces

        copilot = by_host["vscode-copilot"]
        assert copilot.host_protocol_mode == "official-context"
        assert copilot.capability_labels["slash"] == "none"
        assert copilot.trigger_command == "super-dev: <需求描述>"
        assert ".github/copilot-instructions.md" in copilot.official_project_surfaces
        assert "AGENTS.md" in copilot.observed_compatibility_surfaces

        copilot_cli = by_host["copilot-cli"]
        assert copilot_cli.host_protocol_summary == "官方 copilot-instructions + skills + AGENTS.md compatibility"
        assert ".github/skills/super-dev-core/SKILL.md" in copilot_cli.integration_files
        assert ".github/skills/super-dev-core/SKILL.md" in copilot_cli.official_project_surfaces
        assert "~/.copilot/skills/super-dev-core/SKILL.md" in copilot_cli.official_user_surfaces
        assert "AGENTS.md" in copilot_cli.observed_compatibility_surfaces

    def test_adapter_profile_contains_docs_references_and_capability_labels(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        claude = manager.get_adapter_profile("claude-code")
        codex = manager.get_adapter_profile("codex-cli")

        assert len(claude.official_docs_references) >= 2
        assert claude.capability_labels["slash"] == "native"
        assert claude.capability_labels["skills"] == "official"
        assert claude.capability_labels["trigger"] == "slash"

        assert codex.capability_labels["slash"] == "skill-list"
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

        assert len(files) == 2
        rules_content = (temp_project_dir / ".qoder" / "rules" / "super-dev.md").read_text(encoding="utf-8")
        skill_content = (temp_project_dir / ".qoder" / "skills" / "super-dev-core" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "Super Dev" in rules_content
        assert "super-dev：" in skill_content

    def test_cline_rules_and_project_skill_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("cline", force=True)

        assert len(files) == 2
        rules_content = (temp_project_dir / ".clinerules" / "super-dev.md").read_text(encoding="utf-8")
        skill_content = (temp_project_dir / ".cline" / "skills" / "super-dev-core" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "Super Dev" in rules_content
        assert "super-dev：" in skill_content

    def test_antigravity_context_and_workflow_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("antigravity", force=True)
        slash_file = manager.setup_slash_command(target="antigravity", force=True)

        assert len(files) == 2
        context_content = (temp_project_dir / "GEMINI.md").read_text(encoding="utf-8")
        workflow_content = (temp_project_dir / ".agent" / "workflows" / "super-dev.md").read_text(encoding="utf-8")
        assert slash_file is not None
        command_content = slash_file.read_text(encoding="utf-8")
        assert "Super Dev" in context_content
        assert "/super-dev" in command_content
        assert "必须暂停等待用户确认" in workflow_content

    def test_trae_project_and_compatibility_rules_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("trae", force=True)

        assert len(files) == 2
        project_rules = (temp_project_dir / ".trae" / "project_rules.md").read_text(encoding="utf-8")
        compatibility_rules = (temp_project_dir / ".trae" / "rules.md").read_text(encoding="utf-8")
        assert "super-dev：" in project_rules
        assert "continue Super Dev" in project_rules
        assert project_rules == compatibility_rules

    def test_roo_code_rules_and_slash_command_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("roo-code", force=True)
        slash_file = manager.setup_slash_command(target="roo-code", force=True)

        assert len(files) == 1
        rules_content = (temp_project_dir / ".roo" / "rules" / "super-dev.md").read_text(encoding="utf-8")
        assert slash_file is not None
        command_content = slash_file.read_text(encoding="utf-8")
        assert "Super Dev" in rules_content
        assert "/super-dev" in command_content

    def test_kilo_code_rules_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("kilo-code", force=True)

        assert len(files) == 1
        rules_content = (temp_project_dir / ".kilocode" / "rules" / "super-dev.md").read_text(encoding="utf-8")
        assert "Super Dev" in rules_content
        assert "super-dev：" in rules_content

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
        assert "first natural-language requirement in a new session must also continue Super Dev" in content
        assert "project workspace" in content
        assert "instead of only replying in chat" in content
        assert "treat the step as incomplete" in content

    def test_embedded_skill_and_host_specific_surfaces_require_written_artifacts(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)

        embedded = manager._build_embedded_skill_content(
            "codex-cli", ".agents/skills/super-dev/SKILL.md"
        )
        antigravity = manager._build_antigravity_context_content()
        claude_agent = manager._build_claude_agent_content()
        codebuddy_agent = manager._build_codebuddy_agent_content()
        workflow = manager._antigravity_workflow_rules()

        assert "super-dev:" in embedded or "super-dev：" in embedded
        assert "必须真实写入项目文件" in embedded
        assert "继续当前流程" in embedded
        assert "SESSION_BRIEF" in embedded
        assert "Chat-only summaries do not count" in antigravity
        assert "write them as project files" in antigravity
        assert "workspace files" in claude_agent
        assert "chat-only summaries" in claude_agent
        assert "first natural-language requirement" in claude_agent
        assert "continue Super Dev" in claude_agent
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
        assert "the first natural-language requirement in a new host session must also default to continuing Super Dev" in cli_rules
        assert "current phase is `research`" in cli_rules
        assert "stop after the three core documents and wait for approval" in cli_rules
        assert "Read relevant files under `knowledge/` before drafting documents." in cli_rules
        assert "wait for explicit confirmation before creating Spec or coding" in cli_rules
        assert ".super-dev/SESSION_BRIEF.md" in cli_rules
        assert "Do not silently exit Super Dev mode" in cli_rules
        assert "host remains responsible for actual coding" in ide_rules
        assert "Read relevant files under `knowledge/` before drafting the three core documents." in ide_rules
        assert "Treat Super Dev as the local Python workflow tool plus this host rule file" in ide_rules
        assert "First-Response Contract" in ide_rules
        assert "the first natural-language requirement in a new host session must also default to continuing Super Dev" in ide_rules
        assert "current phase is `research`" in ide_rules
        assert ".super-dev/SESSION_BRIEF.md" in ide_rules
        assert "Claude Code remains the execution host" in claude_rules
        assert "Read relevant files under `knowledge/` before drafting PRD, architecture, and UIUX." in claude_rules
        assert "First-Response Contract" in claude_rules
        assert "first natural-language requirement" in claude_rules
        assert "continuing Super Dev" in claude_rules
        assert "stop after the three core documents and wait for approval" in claude_rules
        assert "wait for explicit confirmation before creating Spec or coding" in claude_rules
        assert ".super-dev/SESSION_BRIEF.md" in claude_rules

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

    def test_opencode_setup_uses_root_agents_and_global_agents(
        self,
        temp_project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))

        manager = IntegrationManager(temp_project_dir)
        written = manager.setup("opencode", force=True)
        global_file = manager.setup_global_protocol(target="opencode", force=True)

        root_agents = temp_project_dir / "AGENTS.md"
        assert root_agents.resolve() in [item.resolve() for item in written]
        assert (temp_project_dir / ".opencode" / "skills" / "super-dev-core" / "SKILL.md").resolve() in [
            item.resolve() for item in written
        ]
        assert root_agents.exists()
        root_content = root_agents.read_text(encoding="utf-8")
        assert "BEGIN SUPER DEV OPENCODE" in root_content
        assert '/super-dev "<需求描述>"' in root_content

        assert global_file is not None
        expected_global = fake_home / ".config" / "opencode" / "AGENTS.md"
        assert global_file.resolve() == expected_global.resolve()
        assert expected_global.exists()

    def test_windsurf_rules_and_project_skill_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("windsurf", force=True)
        workflow_file = manager.setup_slash_command(target="windsurf", force=True)

        assert len(files) == 2
        rules_content = (temp_project_dir / ".windsurf" / "rules" / "super-dev.md").read_text(encoding="utf-8")
        skill_content = (temp_project_dir / ".windsurf" / "skills" / "super-dev-core" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert workflow_file is not None
        workflow_content = workflow_file.read_text(encoding="utf-8")
        assert "Super Dev" in rules_content
        assert "super-dev：" in skill_content
        assert "/super-dev" in workflow_content

    def test_remove_opencode_preserves_codex_agents_block(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        manager.setup("codex-cli", force=True)
        manager.setup("opencode", force=True)

        agents = temp_project_dir / "AGENTS.md"
        content_before = agents.read_text(encoding="utf-8")
        assert "BEGIN SUPER DEV CODEX" in content_before
        assert "BEGIN SUPER DEV OPENCODE" in content_before

        manager.remove("opencode")

        content_after = agents.read_text(encoding="utf-8")
        assert "BEGIN SUPER DEV CODEX" in content_after
        assert "BEGIN SUPER DEV OPENCODE" not in content_after

    def test_skill_only_target_skips_slash_mapping(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        assert manager.supports_slash("codex-cli") is False
        assert manager.supports_slash("kiro-cli") is False
        assert manager.setup_slash_command(target="codex-cli", force=True) is None
        assert manager.setup_slash_command(target="kiro-cli", force=True) is None
        assert manager.setup_global_slash_command(target="codex-cli", force=True) is None
        assert manager.setup_global_slash_command(target="kiro-cli", force=True) is None
        assert manager.supports_slash("kiro") is False
        assert manager.supports_slash("qoder") is True
        assert manager.supports_slash("trae") is False
        assert manager.supports_slash("antigravity") is True
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

    @pytest.mark.parametrize("target", ["codex-cli", "opencode", "claude-code", "cursor"])
    def test_host_rules_embed_ui_governance_constraints(self, temp_project_dir: Path, target: str):
        manager = IntegrationManager(temp_project_dir)
        written = manager.setup(target, force=True)
        assert written

        merged = "\n".join(path.read_text(encoding="utf-8") for path in written if path.exists())
        assert "emoji" in merged.lower()
        assert "图标库" in merged or "icon" in merged.lower()
        assert "output/*-uiux.md" in merged
        assert "Claude / ChatGPT" in merged or "claude / chatgpt" in merged.lower()
        assert "design token" in merged.lower() or "design tokens" in merged.lower()

    @pytest.mark.parametrize("target", PRIMARY_HOST_TOOL_IDS)
    def test_primary_hosts_always_embed_uiux_and_continuity_contracts(self, temp_project_dir: Path, target: str):
        manager = IntegrationManager(temp_project_dir)
        written = manager.setup(target, force=True)

        merged = "\n".join(path.read_text(encoding="utf-8") for path in written if path.exists())
        lowered = merged.lower()
        assert "output/*-uiux.md" in merged
        assert ".super-dev/SESSION_BRIEF.md" in merged
        assert "emoji" in lowered
        assert "design token" in lowered

    def test_codex_rules_require_ui_contract_before_implementation(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        manager.setup("codex-cli", force=True)

        agents = temp_project_dir / "AGENTS.md"
        content = agents.read_text(encoding="utf-8")
        assert "开始任何 UI 实现前" in content
        assert "图标库" in content
        assert "output/*-uiux.md" in content
        assert "emoji" in content.lower()
