# -*- coding: utf-8 -*-
"""
平台集成管理测试
"""

from pathlib import Path

from super_dev.integrations import IntegrationManager


class TestIntegrationManager:
    def test_setup_single_target(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        files = manager.setup("cursor", force=True)

        assert len(files) == 1
        cursor_rules = temp_project_dir / ".cursorrules"
        assert cursor_rules.exists()
        content = cursor_rules.read_text(encoding="utf-8")
        assert "Super Dev" in content

    def test_setup_all_targets(self, temp_project_dir: Path):
        manager = IntegrationManager(temp_project_dir)
        result = manager.setup_all(force=True)

        assert "claude-code" in result
        assert (temp_project_dir / ".claude" / "CLAUDE.md").exists()
        assert (temp_project_dir / ".codex" / "AGENTS.md").exists()
