"""
专家建议服务测试
"""

from pathlib import Path

from super_dev.experts import (
    has_expert,
    list_expert_advice_history,
    list_experts,
    read_expert_advice,
    render_expert_advice_markdown,
    save_expert_advice,
)


class TestExpertService:
    def test_list_experts_contains_rca(self):
        experts = list_experts()
        ids = {item["id"] for item in experts}
        assert "PM" in ids
        assert "RCA" in ids

    def test_render_advice_markdown(self):
        content = render_expert_advice_markdown("PM", "规划认证模块")
        assert "# PM 专家建议" in content
        assert "建议清单" in content
        assert "规划认证模块" in content

    def test_save_expert_advice(self, temp_project_dir: Path):
        path, content = save_expert_advice(temp_project_dir, "QA", "补测试策略")
        assert path.exists()
        assert "QA 专家建议" in content
        assert "补测试策略" in content
        assert path.read_text(encoding="utf-8") == content

    def test_has_expert(self):
        assert has_expert("PM") is True
        assert has_expert("UNKNOWN") is False

    def test_history_and_read(self, temp_project_dir: Path):
        path, _ = save_expert_advice(temp_project_dir, "PM", "测试")
        history = list_expert_advice_history(temp_project_dir, limit=10)
        assert any(item["file_name"] == path.name for item in history)

        file_path, content = read_expert_advice(temp_project_dir, path.name)
        assert file_path.name == path.name
        assert "PM 专家建议" in content

    def test_read_expert_advice_rejects_invalid_name(self, temp_project_dir: Path):
        try:
            read_expert_advice(temp_project_dir, "../bad.md")
            assert False, "should raise ValueError"
        except ValueError:
            assert True
