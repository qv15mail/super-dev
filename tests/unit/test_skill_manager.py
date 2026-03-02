"""
Skill 管理测试
"""

from pathlib import Path

import pytest

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

    @pytest.mark.parametrize(
        "target",
        [
            "claude-code",
            "codex-cli",
            "opencode",
            "cursor",
            "qoder",
            "trae",
            "codebuddy",
            "antigravity",
        ],
    )
    def test_install_builtin_skill(self, temp_project_dir: Path, target: str):
        manager = SkillManager(temp_project_dir)
        result = manager.install(source="super-dev", target=target, name="super-dev-core")

        assert result.path.exists()
        assert (result.path / "SKILL.md").exists()
        assert "super-dev-core" in manager.list_installed(target)

        removed = manager.uninstall("super-dev-core", target)
        assert not removed.exists()
