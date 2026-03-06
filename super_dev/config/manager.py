"""
开发：Excellent（11964948@qq.com）
功能：配置管理器 - 管理项目配置
作用：读取、验证、持久化 super-dev.yaml 配置
创建时间：2025-12-30
最后修改：2025-12-30
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from super_dev.catalogs import (
    FULL_FRONTEND_TEMPLATE_IDS,
    HOST_TOOL_IDS,
    PIPELINE_BACKEND_IDS,
    PLATFORM_IDS,
)


@dataclass
class ProjectConfig:
    """项目配置"""

    name: str
    description: str = ""
    version: str = "2.0.7"
    author: str = ""
    license: str = "MIT"

    # 技术栈
    platform: str = "web"  # web, mobile, wechat, desktop
    frontend: str = "next"  # 扩展支持：next, remix, react-vite, gatsby, nuxt, vue-vite, angular, sveltekit, astro, solid, qwik
    backend: str = "node"  # node, python, go, java, rust, php, ruby, csharp, kotlin, swift, elixir, scala, dart
    database: str = "postgresql"  # postgresql, mysql, mongodb, redis

    # 前端配置 (扩展)
    ui_library: str | None = None  # UI 组件库
    style_solution: str | None = None  # 样式方案
    state_management: list[str] = field(default_factory=list)  # 状态管理
    testing_frameworks: list[str] = field(default_factory=list)  # 测试框架

    # 领域知识
    domain: str = ""  # fintech, ecommerce, medical, social, iot, education
    language_preferences: list[str] = field(default_factory=list)  # 语言偏好（用于文档/实现建议）
    knowledge_allowed_domains: list[str] = field(default_factory=list)  # 联网知识白名单域名
    knowledge_cache_ttl_seconds: int = 1800  # 知识缓存 TTL（秒）

    # 工作流配置
    phases: list[str] = field(default_factory=lambda: [
        "discovery", "intelligence", "drafting",
        "redteam", "qa", "delivery", "deployment"
    ])

    # 专家配置
    experts: list[str] = field(default_factory=lambda: [
        "PM", "ARCHITECT", "UI", "UX", "SECURITY", "CODE"
    ])

    # 质量门禁
    quality_gate: int = 80
    host_compatibility_min_score: int = 80
    host_compatibility_min_ready_hosts: int = 1
    host_profile_targets: list[str] = field(default_factory=list)  # 目标宿主画像（用于质量门禁和运营看板）
    host_profile_enforce_selected: bool = False  # 仅按 host_profile_targets 计算宿主兼容性

    # 输出目录
    output_dir: str = "output"

    # CLI 设置
    cli: dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """配置管理器"""

    CONFIG_FILENAME = "super-dev.yaml"
    DEFAULT_CONFIG: dict[str, Any] = {
        "name": "my-project",
        "description": "A Super Dev project",
        "version": "2.0.7",
        "platform": "web",
        "frontend": "next",  # 默认使用 Next.js
        "backend": "node",
        "database": "postgresql",
        "domain": "",
        "language_preferences": [],
        "knowledge_allowed_domains": [],
        "knowledge_cache_ttl_seconds": 1800,
        "quality_gate": 80,
        "host_compatibility_min_score": 80,
        "host_compatibility_min_ready_hosts": 1,
        "host_profile_targets": [],
        "host_profile_enforce_selected": False,
        "output_dir": "output",
        # 前端配置
        "ui_library": None,
        "style_solution": None,
        "state_management": [],
        "testing_frameworks": [],
    }

    def __init__(self, project_dir: Path | None = None):
        """
        初始化配置管理器

        Args:
            project_dir: 项目目录，默认为当前目录
        """
        self.project_dir = Path.cwd() if project_dir is None else project_dir
        self.config_path = self.project_dir / self.CONFIG_FILENAME
        self._config: ProjectConfig | None = None

    @property
    def config(self) -> ProjectConfig:
        """获取配置（延迟加载）"""
        if self._config is None:
            self._config = self.load()
        return self._config

    def exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_path.exists()

    def load(self) -> ProjectConfig:
        """
        加载配置文件

        Returns:
            ProjectConfig: 项目配置对象
        """
        if not self.exists():
            # 返回默认配置
            return ProjectConfig(**cast(dict[str, Any], self.DEFAULT_CONFIG.copy()))

        with open(self.config_path, encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        data = loaded if isinstance(loaded, dict) else {}

        # 合并默认配置
        config_data: dict[str, Any] = {**self.DEFAULT_CONFIG, **data}

        return ProjectConfig(**cast(dict[str, Any], config_data))

    def save(self, config: ProjectConfig | None = None) -> None:
        """
        保存配置文件

        Args:
            config: 要保存的配置，默认使用当前配置
        """
        config_to_save = config or self._config
        if config_to_save is None:
            raise ValueError("No config to save")

        # 转换为字典（排除 None 值）
        data = {
            k: v for k, v in config_to_save.__dict__.items()
            if v is not None and not k.startswith("_")
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        self._config = config_to_save

    def create(self, **kwargs: Any) -> ProjectConfig:
        """
        创建新配置

        Args:
            **kwargs: 配置参数

        Returns:
            ProjectConfig: 新创建的配置对象
        """
        config_data: dict[str, Any] = {**self.DEFAULT_CONFIG, **kwargs}
        candidate = ProjectConfig(**cast(dict[str, Any], config_data))
        errors = self._collect_validation_errors(candidate)
        if errors:
            raise ValueError(f"配置验证失败: {'; '.join(errors)}")
        self._config = candidate
        self.save()
        return candidate

    def update(self, **kwargs: Any) -> ProjectConfig:
        """
        更新配置

        Args:
            **kwargs: 要更新的配置参数

        Returns:
            ProjectConfig: 更新后的配置对象
        """
        if not self.exists():
            return self.create(**kwargs)

        # 类型转换映射
        type_converters: dict[str, type[int]] = {
            "quality_gate": int,  # 质量门禁必须是整数
            "knowledge_cache_ttl_seconds": int,
            "host_compatibility_min_score": int,
            "host_compatibility_min_ready_hosts": int,
        }

        # 转换类型
        converted_kwargs: dict[str, Any] = {}
        for key, value in kwargs.items():
            if key == "knowledge_allowed_domains" and isinstance(value, str):
                converted_kwargs[key] = [
                    item.strip() for item in value.split(",") if item.strip()
                ]
                continue
            if key == "language_preferences" and isinstance(value, str):
                converted_kwargs[key] = [
                    item.strip() for item in value.split(",") if item.strip()
                ]
                continue
            if key == "host_profile_targets" and isinstance(value, str):
                converted_kwargs[key] = [
                    item.strip() for item in value.split(",") if item.strip()
                ]
                continue
            if key == "host_profile_enforce_selected" and isinstance(value, str):
                lowered = value.strip().lower()
                converted_kwargs[key] = lowered in {"1", "true", "yes", "y", "on"}
                continue
            if key in type_converters and isinstance(value, str):
                try:
                    converted_kwargs[key] = type_converters[key](value)
                except (ValueError, TypeError):
                    converted_kwargs[key] = value
            else:
                converted_kwargs[key] = value

        # 合并现有配置
        current_data: dict[str, Any] = dict(self.config.__dict__)
        updated_data: dict[str, Any] = {**current_data, **converted_kwargs}

        candidate = ProjectConfig(**cast(dict[str, Any], updated_data))
        errors = self._collect_validation_errors(candidate)
        if errors:
            raise ValueError(f"配置验证失败: {'; '.join(errors)}")
        self._config = candidate
        self.save()
        return candidate

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键（支持点号分隔的嵌套键）
            default: 默认值

        Returns:
            配置值
        """
        value = self.config
        for part in key.split("."):
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        return value

    def validate(self) -> tuple[bool, list[str]]:
        """
        验证配置

        Returns:
            (是否有效, 错误列表)
        """
        errors = self._collect_validation_errors(self.config)
        return len(errors) == 0, errors

    def _collect_validation_errors(self, config: ProjectConfig) -> list[str]:
        """收集配置错误列表"""
        errors: list[str] = []

        # 验证必需字段
        if not config.name:
            errors.append("项目名称不能为空")

        # 验证平台
        valid_platforms = list(PLATFORM_IDS)
        if config.platform not in valid_platforms:
            errors.append(f"平台必须是: {', '.join(valid_platforms)}")

        # 验证前端框架
        valid_frontends = list(FULL_FRONTEND_TEMPLATE_IDS)
        if config.frontend not in valid_frontends:
            errors.append(f"前端框架必须是: {', '.join(valid_frontends)}")

        # 验证后端框架
        valid_backends = list(PIPELINE_BACKEND_IDS)
        if config.backend not in valid_backends:
            errors.append(f"后端框架必须是: {', '.join(valid_backends)}")

        # 验证质量门禁
        if not 0 <= config.quality_gate <= 100:
            errors.append("质量门禁必须在 0-100 之间")
        if not 0 <= config.host_compatibility_min_score <= 100:
            errors.append("host_compatibility_min_score 必须在 0-100 之间")
        if config.host_compatibility_min_ready_hosts < 0:
            errors.append("host_compatibility_min_ready_hosts 不能小于 0")
        if not isinstance(config.host_profile_enforce_selected, bool):
            errors.append("host_profile_enforce_selected 必须是布尔值")
        if not isinstance(config.host_profile_targets, list):
            errors.append("host_profile_targets 必须是字符串列表")
        else:
            invalid_targets = [
                item for item in config.host_profile_targets
                if not isinstance(item, str) or not item.strip()
            ]
            if invalid_targets:
                errors.append("host_profile_targets 包含非法项")
            unsupported_targets = [
                item for item in config.host_profile_targets
                if isinstance(item, str) and item.strip() and item not in HOST_TOOL_IDS
            ]
            if unsupported_targets:
                errors.append(
                    "host_profile_targets 包含不支持的宿主: "
                    + ", ".join(sorted(set(unsupported_targets)))
                )

        # 验证知识增强配置
        if config.knowledge_cache_ttl_seconds < 0:
            errors.append("knowledge_cache_ttl_seconds 不能小于 0")
        if not isinstance(config.language_preferences, list):
            errors.append("language_preferences 必须是字符串列表")
        else:
            invalid_language_items = [
                item for item in config.language_preferences
                if not isinstance(item, str) or not item.strip()
            ]
            if invalid_language_items:
                errors.append("language_preferences 包含非法项")
        if not isinstance(config.knowledge_allowed_domains, list):
            errors.append("knowledge_allowed_domains 必须是字符串列表")
        else:
            invalid_items = [
                item for item in config.knowledge_allowed_domains
                if not isinstance(item, str) or not item.strip()
            ]
            if invalid_items:
                errors.append("knowledge_allowed_domains 包含非法项")

        return errors


# 全局配置管理器缓存（按项目目录隔离）
_global_config_managers: dict[Path, ConfigManager] = {}


def get_config_manager(project_dir: Path | None = None) -> ConfigManager:
    """
    获取全局配置管理器实例

    Args:
        project_dir: 项目目录

    Returns:
        ConfigManager: 配置管理器实例
    """
    project_root = (Path.cwd() if project_dir is None else Path(project_dir)).resolve()
    manager = _global_config_managers.get(project_root)
    if manager is None:
        manager = ConfigManager(project_root)
        _global_config_managers[project_root] = manager
    return manager
