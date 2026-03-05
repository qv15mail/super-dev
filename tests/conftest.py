"""
Super Dev 测试配置
"""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from super_dev.config import ConfigManager, ProjectConfig
from super_dev.orchestrator import WorkflowContext, WorkflowEngine


@pytest.fixture(autouse=True)
def reset_global_config_manager():
    """重置全局配置管理器（每个测试前）"""
    from super_dev.config import manager
    manager._global_config_manager = None
    yield
    manager._global_config_manager = None


@pytest.fixture(autouse=True)
def allow_pipeline_without_host_in_tests(monkeypatch):
    """测试默认关闭宿主硬门禁，避免依赖本机宿主安装状态。"""
    monkeypatch.setenv("SUPER_DEV_ALLOW_NO_HOST", "1")


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """临时项目目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config(temp_project_dir: Path) -> ProjectConfig:
    """示例配置"""
    return ProjectConfig(
        name="test-project",
        description="Test project",
        platform="web",
        frontend="react",
        backend="node",
        domain="ecommerce"
    )


@pytest.fixture
def config_manager(temp_project_dir: Path, sample_config: ProjectConfig) -> ConfigManager:
    """配置管理器"""
    manager = ConfigManager(temp_project_dir)
    manager._config = sample_config
    return manager


@pytest.fixture
def workflow_engine(temp_project_dir: Path) -> WorkflowEngine:
    """工作流引擎"""
    return WorkflowEngine(temp_project_dir)


@pytest.fixture
def workflow_context(temp_project_dir: Path, config_manager: ConfigManager) -> WorkflowContext:
    """工作流上下文"""
    return WorkflowContext(
        project_dir=temp_project_dir,
        config=config_manager
    )
