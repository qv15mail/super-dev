"""
平台集成管理测试
"""

from pathlib import Path

import pytest

from super_dev.integrations import IntegrationManager


class TestIntegrationManager:
    @pytest.mark.parametrize(
        "target, expected_file",
        [
            ("claude-code", ".claude/CLAUDE.md"),
            ("codex-cli", ".codex/AGENTS.md"),
            ("opencode", ".opencode/AGENTS.md"),
            ("cursor", ".cursorrules"),
            ("qoder", ".qoder/rules.md"),
            ("trae", ".trae/rules.md"),
            ("codebuddy", ".codebuddy/rules.md"),
            ("antigravity", ".agents/workflows/super-dev.md"),
        ],
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

    def test_antigravity_rules_use_direct_requirement_mode(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("antigravity", force=True)

        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        assert 'super-dev "需求"' in content
        assert 'super-dev pipeline "需求"' in content
