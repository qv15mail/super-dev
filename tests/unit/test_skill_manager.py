"""
Skill 管理测试
"""

from pathlib import Path

import pytest

from super_dev.skills import SkillManager


class TestSkillManager:
    def test_coverage_gaps_are_empty(self):
        gaps = SkillManager.coverage_gaps()
        assert gaps["missing_in_skill_targets"] == []
        assert gaps["extra_in_skill_targets"] == []

    def test_target_path_kind_distinguishes_official_and_observed(self):
        assert SkillManager.target_path_kind("antigravity") == "official-user-surface"
        assert SkillManager.target_path_kind("qoder-cli") == "official-user-surface"
        assert SkillManager.target_path_kind("trae") == "observed-compatibility-surface"
        assert SkillManager.TARGET_PATHS["antigravity"] == "~/.gemini/skills"
        assert SkillManager.TARGET_PATHS["qoder"] == "~/.qoderwork/skills"
        assert SkillManager.TARGET_PATHS["windsurf"] == "~/.codeium/windsurf/skills"
        assert SkillManager.TARGET_PATHS["opencode"] == "~/.config/opencode/skills"

    def test_install_from_directory_and_uninstall(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
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
        list(SkillManager.TARGET_PATHS.keys()),
    )
    def test_install_builtin_skill(self, temp_project_dir: Path, target: str, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        manager = SkillManager(temp_project_dir)
        result = manager.install(source="super-dev", target=target, name="super-dev-core")

        assert result.path.exists()
        assert (result.path / "SKILL.md").exists()
        skill_content = (result.path / "SKILL.md").read_text(encoding="utf-8")
        assert skill_content.startswith("---\nname: super-dev-core\n")
        assert "当前宿主负责调用模型、工具、终端与实际代码修改" in skill_content
        assert "Super Dev 不是大模型平台" in skill_content
        assert "Runtime Contract（强制）" in skill_content
        assert "首轮响应契约（强制）" in skill_content
        assert "第一轮回复必须明确说明当前阶段是 `research`" in skill_content
        assert "三份核心文档完成后会暂停等待用户确认" in skill_content
        assert "本地知识库契约（强制）" in skill_content
        assert "output/knowledge-cache/*-knowledge-bundle.json" in skill_content
        assert "未经用户明确确认，禁止创建 `.super-dev/changes/*`" in skill_content
        assert "super-dev：" in skill_content
        assert "super-dev-core" in manager.list_installed(target)

        removed = manager.uninstall("super-dev-core", target)
        assert not removed.exists()
