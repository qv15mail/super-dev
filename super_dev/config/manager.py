# -*- coding: utf-8 -*-
"""
开发：Excellent（11964948@qq.com）
功能：配置管理器 - 管理项目配置
作用：读取、验证、持久化 super-dev.yaml 配置
创建时间：2025-12-30
最后修改：2025-12-30
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """项目配置"""

    name: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    license: str = "MIT"

    # 技术栈
    platform: str = "web"  # web, mobile, wechat, desktop
    frontend: str = "next"  # 扩展支持：next, remix, react-vite, gatsby, nuxt, vue-vite, angular, sveltekit, astro, solid, qwik
    backend: str = "node"  # node, python, go, java
    database: str = "postgresql"  # postgresql, mysql, mongodb, redis

    # 前端配置 (扩展)
    ui_library: Optional[str] = None  # UI 组件库
    style_solution: Optional[str] = None  # 样式方案
    state_management: List[str] = field(default_factory=list)  # 状态管理
    testing_frameworks: List[str] = field(default_factory=list)  # 测试框架

    # 领域知识
    domain: str = ""  # fintech, ecommerce, medical, social, iot, education

    # 工作流配置
    phases: list = field(default_factory=lambda: [
        "discovery", "intelligence", "drafting",
        "redteam", "qa", "delivery", "deployment"
    ])

    # 专家配置
    experts: list = field(default_factory=lambda: [
        "PM", "ARCHITECT", "UI", "UX", "SECURITY", "CODE"
    ])

    # 质量门禁
    quality_gate: int = 80

    # 输出目录
    output_dir: str = "output"

    # CLI 设置
    cli: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """配置管理器"""

    CONFIG_FILENAME = "super-dev.yaml"
    DEFAULT_CONFIG = {
        "name": "my-project",
        "description": "A Super Dev project",
        "version": "1.0.0",
        "platform": "web",
        "frontend": "next",  # 默认使用 Next.js
        "backend": "node",
        "database": "postgresql",
        "domain": "",
        "quality_gate": 80,
        "output_dir": "output",
        # 前端配置
        "ui_library": None,
        "style_solution": None,
        "state_management": [],
        "testing_frameworks": [],
    }

    def __init__(self, project_dir: Optional[Path] = None):
        """
        初始化配置管理器

        Args:
            project_dir: 项目目录，默认为当前目录
        """
        self.project_dir = Path.cwd() if project_dir is None else project_dir
        self.config_path = self.project_dir / self.CONFIG_FILENAME
        self._config: Optional[ProjectConfig] = None

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
            return ProjectConfig(**self.DEFAULT_CONFIG)

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # 合并默认配置
        config_data = {**self.DEFAULT_CONFIG, **data}

        return ProjectConfig(**config_data)

    def save(self, config: Optional[ProjectConfig] = None) -> None:
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

    def create(self, **kwargs) -> ProjectConfig:
        """
        创建新配置

        Args:
            **kwargs: 配置参数

        Returns:
            ProjectConfig: 新创建的配置对象
        """
        config_data = {**self.DEFAULT_CONFIG, **kwargs}
        self._config = ProjectConfig(**config_data)
        self.save()
        return self._config

    def update(self, **kwargs) -> ProjectConfig:
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
        type_converters = {
            "quality_gate": int,  # 质量门禁必须是整数
        }

        # 转换类型
        converted_kwargs = {}
        for key, value in kwargs.items():
            if key in type_converters and isinstance(value, str):
                try:
                    converted_kwargs[key] = type_converters[key](value)
                except (ValueError, TypeError):
                    converted_kwargs[key] = value
            else:
                converted_kwargs[key] = value

        # 合并现有配置
        current_data = self.config.__dict__
        updated_data = {**current_data, **converted_kwargs}

        self._config = ProjectConfig(**updated_data)
        self.save()
        return self._config

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
        errors = []

        # 验证必需字段
        if not self.config.name:
            errors.append("项目名称不能为空")

        # 验证平台
        valid_platforms = ["web", "mobile", "wechat", "desktop"]
        if self.config.platform not in valid_platforms:
            errors.append(f"平台必须是: {', '.join(valid_platforms)}")

        # 验证前端框架
        valid_frontends = [
            "next", "remix", "react-vite", "gatsby",
            "nuxt", "vue-vite",
            "angular",
            "sveltekit",
            "astro", "solid", "qwik",
            "react", "vue", "svelte",
            "none",
        ]
        if self.config.frontend not in valid_frontends:
            errors.append(f"前端框架必须是: {', '.join(valid_frontends)}")

        # 验证后端框架
        valid_backends = ["node", "python", "go", "java", "none"]
        if self.config.backend not in valid_backends:
            errors.append(f"后端框架必须是: {', '.join(valid_backends)}")

        # 验证质量门禁
        if not 0 <= self.config.quality_gate <= 100:
            errors.append("质量门禁必须在 0-100 之间")

        return len(errors) == 0, errors


# 全局配置管理器实例
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager(project_dir: Optional[Path] = None) -> ConfigManager:
    """
    获取全局配置管理器实例

    Args:
        project_dir: 项目目录

    Returns:
        ConfigManager: 配置管理器实例
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager(project_dir)
    return _global_config_manager
