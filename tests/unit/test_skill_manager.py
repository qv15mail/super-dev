# -*- coding: utf-8 -*-
"""
Skill 管理测试
"""

from pathlib import Path

from super_dev.skills import SkillManager


class TestSkillManager:
    def test_install_from_directory_and_uninstall(self, temp_project_dir: Path):
        source_skill = temp_project_dir / "my-skill"
        source_skill.mkdir(parents=True, exist_ok=True)
        (source_skill / "SKILL.md").write_text("# My Skill", encoding="utf-8")

        manager = SkillManager(temp_project_dir)
        result = manager.install(
            source=str(source_skill),
            target="codex-cli",
            name="my-skill",
        )

        assert result.path.exists()
        assert "my-skill" in manager.list_installed("codex-cli")

        removed = manager.uninstall("my-skill", "codex-cli")
        assert not removed.exists()

    def test_install_builtin_skill(self, temp_project_dir: Path):
        manager = SkillManager(temp_project_dir)
        result = manager.install(source="super-dev", target="claude-code", name="super-dev-core")

        assert result.path.exists()
        assert (result.path / "SKILL.md").exists()
        assert "super-dev-core" in manager.list_installed("claude-code")
