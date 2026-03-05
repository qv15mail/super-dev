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

        assert len(files) == 1
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
        assert codex.slash_command_file.endswith("/super-dev.md")
        assert codex.skill_dir.startswith(".codex/")

        qoder = by_host["qoder"]
        assert qoder.category == "ide"
        assert qoder.adapter_mode == "native-ide-rule-file"
        assert qoder.integration_files[0] == ".qoder/rules.md"
        assert qoder.docs_verified is True

    def test_qoder_rules_generated(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("qoder", force=True)

        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        assert "Super Dev" in content

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
        assert manager.supports_slash("trae") is False
        assert manager.setup_slash_command(target="trae", force=True) is None
        assert manager.setup_global_slash_command(target="trae", force=True) is None
