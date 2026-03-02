"""
Spec 管理器测试
"""

from pathlib import Path

from super_dev.specs.generator import SpecGenerator
from super_dev.specs.manager import ChangeManager


class TestSpecManager:
    def test_change_spec_requirements_persist_after_reload_and_save(self, temp_project_dir: Path):
        generator = SpecGenerator(temp_project_dir)
        generator.init_sdd()

        change = generator.create_change(
            change_id="add-auth-flow",
            title="Add Auth Flow",
            description="认证流程",
        )
        generator.add_requirement_to_change(
            change_id=change.id,
            spec_name="auth",
            requirement_name="secure-authentication",
            description="系统 SHALL 支持安全认证与会话管理。",
            scenarios=[{"given": "用户未登录", "when": "提交凭据", "then": "建立会话"}],
        )
        generator.add_requirement_to_change(
            change_id=change.id,
            spec_name="auth",
            requirement_name="password-reset",
            description="系统 SHALL 支持密码重置。",
        )

        manager = ChangeManager(temp_project_dir)
        loaded = manager.load_change(change.id)
        assert loaded is not None
        assert loaded.spec_deltas
        assert loaded.spec_deltas[0].requirements
        assert any(req.name == "secure-authentication" for req in loaded.spec_deltas[0].requirements)

        # 模拟后续任务更新再次保存，需求不应丢失
        manager.save_change(loaded)
        reloaded = manager.load_change(change.id)
        assert reloaded is not None
        assert reloaded.spec_deltas
        assert reloaded.spec_deltas[0].requirements
        assert any(req.name == "password-reset" for req in reloaded.spec_deltas[0].requirements)
