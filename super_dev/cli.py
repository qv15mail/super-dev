"""
开发：Excellent（11964948@qq.com）
功能：Super Dev CLI 主入口
作用：提供命令行界面，统一访问所有功能
创建时间：2025-12-30
最后修改：2025-01-29
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, cast

try:
    import fcntl
except ImportError:
    fcntl = None

try:
    import requests
    from rich.console import Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from . import __description__, __version__
from .catalogs import (
    CICD_PLATFORM_IDS,
    DOMAIN_IDS,
    FULL_FRONTEND_TEMPLATE_IDS,
    HOST_COMMAND_CANDIDATES,
    HOST_TOOL_IDS,
    PIPELINE_BACKEND_IDS,
    PIPELINE_FRONTEND_TEMPLATE_IDS,
    PLATFORM_IDS,
    PRIMARY_HOST_TOOL_IDS,
    host_path_candidates,
)
from .config import ConfigManager, ProjectConfig, get_config_manager
from .exceptions import SuperDevError
from .orchestrator import Phase, WorkflowContext, WorkflowEngine
from .proof_pack import ProofPackBuilder
from .release_readiness import ReleaseReadinessEvaluator
from .review_state import (
    architecture_revision_file,
    docs_confirmation_file,
    host_runtime_validation_file,
    load_architecture_revision,
    load_docs_confirmation,
    load_host_runtime_validation,
    load_quality_revision,
    load_ui_revision,
    quality_revision_file,
    save_architecture_revision,
    save_docs_confirmation,
    save_host_runtime_validation,
    save_quality_revision,
    save_ui_revision,
    ui_revision_file,
)
from .terminal import (
    create_console,
    normalize_terminal_text,
    output_mode_label,
    output_mode_reason,
    symbol,
)
from .utils import get_logger

CICDPlatform = Literal["github", "gitlab", "jenkins", "azure", "bitbucket", "all"]

SUPPORTED_PLATFORMS = list(PLATFORM_IDS)
SUPPORTED_PIPELINE_FRONTENDS = list(PIPELINE_FRONTEND_TEMPLATE_IDS)
SUPPORTED_INIT_FRONTENDS = list(FULL_FRONTEND_TEMPLATE_IDS)
SUPPORTED_PIPELINE_BACKENDS = list(PIPELINE_BACKEND_IDS)
SUPPORTED_DOMAINS = list(DOMAIN_IDS)
SUPPORTED_CICD = list(CICD_PLATFORM_IDS)
SUPPORTED_HOST_TOOLS = list(HOST_TOOL_IDS)
PRIMARY_SUPPORTED_HOST_TOOLS = list(PRIMARY_HOST_TOOL_IDS)


class SuperDevCLI:
    """Super Dev 命令行接口"""

    def __init__(self):
        self.console = create_console() if RICH_AVAILABLE else None
        self.parser = self._create_parser()
        self.logger = get_logger('cli', level='WARNING')  # CLI只记录WARNING及以上级别

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog="super-dev",
            description=__description__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  super-dev init my-project        初始化新项目
  super-dev analyze [path]         分析现有项目
  super-dev workflow               运行完整工作流
  super-dev expert PM              调用产品经理专家
  super-dev quality                运行质量检查
  super-dev preview                生成原型预览
  super-dev deploy                 生成部署配置
            """
        )

        parser.add_argument(
            "-v", "--version",
            action="version",
            version=f"%(prog)s {__version__}"
        )

        # 子命令
        subparsers = parser.add_subparsers(
            dest="command",
            title="可用命令",
            description="使用 'super-dev <command> -h' 查看帮助"
        )

        # init 命令
        init_parser = subparsers.add_parser(
            "init",
            help="初始化新项目",
            description="创建一个新的 Super Dev 项目"
        )
        init_parser.add_argument(
            "name",
            help="项目名称"
        )
        init_parser.add_argument(
            "-d", "--description",
            default="",
            help="项目描述"
        )
        init_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            default="web",
            help="目标平台"
        )
        init_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_INIT_FRONTENDS,
            default="next",
            help="前端框架"
        )
        init_parser.add_argument(
            "--ui-library",
            choices=[
                "mui", "ant-design", "chakra-ui", "mantine", "shadcn-ui", "radix-ui",
                "element-plus", "naive-ui", "vuetify", "primevue", "arco-design",
                "angular-material", "primeng",
                "skeleton-ui", "svelte-material-ui",
                "tailwind", "daisyui"
            ],
            help="UI 组件库"
        )
        init_parser.add_argument(
            "--style",
            choices=["tailwind", "css-modules", "styled-components", "emotion", "scss", "less", "unocss"],
            help="样式方案"
        )
        init_parser.add_argument(
            "--state",
            choices=["react-query", "swr", "zustand", "redux-toolkit", "jotai", "pinia", "xstate"],
            action="append",
            help="状态管理方案 (可多选)"
        )
        init_parser.add_argument(
            "--testing",
            choices=["vitest", "jest", "playwright", "cypress", "testing-library"],
            action="append",
            help="测试框架 (可多选)"
        )
        init_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            default="node",
            help="后端框架"
        )
        init_parser.add_argument(
            "--domain",
            choices=SUPPORTED_DOMAINS,
            default="",
            help="业务领域"
        )
        bootstrap_parser = subparsers.add_parser(
            "bootstrap",
            help="显式初始化 Super Dev 工作流契约",
            description="创建项目配置、SDD 目录、工作流契约和 bootstrap 摘要，让初始化规范可见"
        )
        bootstrap_parser.add_argument(
            "--name",
            help="项目名称；默认使用当前目录名"
        )
        bootstrap_parser.add_argument(
            "-d", "--description",
            default="",
            help="项目描述"
        )
        bootstrap_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            default="web",
            help="目标平台"
        )
        bootstrap_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_INIT_FRONTENDS,
            default="next",
            help="前端框架"
        )
        bootstrap_parser.add_argument(
            "--ui-library",
            choices=[
                "mui", "ant-design", "chakra-ui", "mantine", "shadcn-ui", "radix-ui",
                "element-plus", "naive-ui", "vuetify", "primevue", "arco-design",
                "angular-material", "primeng",
                "skeleton-ui", "svelte-material-ui",
                "tailwind", "daisyui"
            ],
            help="UI 组件库"
        )
        bootstrap_parser.add_argument(
            "--style",
            choices=["tailwind", "css-modules", "styled-components", "emotion", "scss", "less", "unocss"],
            help="样式方案"
        )
        bootstrap_parser.add_argument(
            "--state",
            choices=["react-query", "swr", "zustand", "redux-toolkit", "jotai", "pinia", "xstate"],
            action="append",
            help="状态管理方案 (可多选)"
        )
        bootstrap_parser.add_argument(
            "--testing",
            choices=["vitest", "jest", "playwright", "cypress", "testing-library"],
            action="append",
            help="测试框架 (可多选)"
        )
        bootstrap_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            default="node",
            help="后端框架"
        )
        bootstrap_parser.add_argument(
            "--domain",
            choices=SUPPORTED_DOMAINS,
            default="",
            help="业务领域"
        )

        # analyze 命令
        analyze_parser = subparsers.add_parser(
            "analyze",
            help="分析现有项目",
            description="自动检测和分析现有项目的结构、技术栈和架构模式"
        )
        analyze_parser.add_argument(
            "path",
            nargs="?",
            default=".",
                       help="项目路径 (默认为当前目录)"
        )
        analyze_parser.add_argument(
            "-o", "--output",
            help="输出报告文件路径 (Markdown 格式)"
        )
        analyze_parser.add_argument(
            "-f", "--format",
            choices=["json", "markdown", "text"],
            default="text",
            help="输出格式"
        )
        analyze_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出"
        )

        repo_map_parser = subparsers.add_parser(
            "repo-map",
            help="生成代码库地图",
            description="输出项目级代码库地图，帮助宿主和开发者先理解代码结构再进入实现",
        )
        repo_map_parser.add_argument(
            "path",
            nargs="?",
            default=".",
            help="项目路径 (默认为当前目录)",
        )
        repo_map_parser.add_argument(
            "-o", "--output",
            help="输出报告路径（默认为 output/<project>-repo-map.md 或 .json）",
        )
        repo_map_parser.add_argument(
            "-f", "--format",
            choices=["json", "markdown", "text"],
            default="text",
            help="输出格式",
        )
        repo_map_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出",
        )

        impact_parser = subparsers.add_parser(
            "impact",
            help="分析变更影响范围",
            description="基于 Repo Map 推断变更会影响的模块、入口、集成面和回归重点",
        )
        impact_parser.add_argument(
            "description",
            nargs="?",
            default="",
            help="变更描述，例如“修改登录流程”",
        )
        impact_parser.add_argument(
            "--files",
            nargs="*",
            default=[],
            help="已知会修改的文件列表，用于提升影响分析准确度",
        )
        impact_parser.add_argument(
            "--path",
            default=".",
            help="项目路径 (默认为当前目录)",
        )
        impact_parser.add_argument(
            "-o", "--output",
            help="输出报告路径（默认为 output/<project>-impact-analysis.md 或 .json）",
        )
        impact_parser.add_argument(
            "-f", "--format",
            choices=["json", "markdown", "text"],
            default="text",
            help="输出格式",
        )
        impact_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出",
        )

        regression_guard_parser = subparsers.add_parser(
            "regression-guard",
            help="生成回归检查清单",
            description="基于 Impact Analysis 输出可执行的回归检查清单，减少修复或重构带来的连带回退。",
        )
        regression_guard_parser.add_argument(
            "description",
            nargs="?",
            default="",
            help="变更描述，例如“修改登录流程”",
        )
        regression_guard_parser.add_argument(
            "--files",
            nargs="*",
            default=[],
            help="已知会修改的文件列表，用于提升回归清单准确度",
        )
        regression_guard_parser.add_argument(
            "--path",
            default=".",
            help="项目路径 (默认为当前目录)",
        )
        regression_guard_parser.add_argument(
            "-o", "--output",
            help="输出报告路径（默认为 output/<project>-regression-guard.md 或 .json）",
        )
        regression_guard_parser.add_argument(
            "-f", "--format",
            choices=["json", "markdown", "text"],
            default="text",
            help="输出格式",
        )
        regression_guard_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出",
        )

        dependency_graph_parser = subparsers.add_parser(
            "dependency-graph",
            help="生成依赖图与关键路径",
            description="输出内部依赖图、关键节点和关键路径，帮助宿主在改动前理解 blast radius。",
        )
        dependency_graph_parser.add_argument(
            "path",
            nargs="?",
            default=".",
            help="项目路径 (默认为当前目录)",
        )
        dependency_graph_parser.add_argument(
            "-o", "--output",
            help="输出报告路径（默认为 output/<project>-dependency-graph.md 或 .json）",
        )
        dependency_graph_parser.add_argument(
            "-f", "--format",
            choices=["json", "markdown", "text"],
            default="text",
            help="输出格式",
        )
        dependency_graph_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出",
        )

        # workflow 命令
        workflow_parser = subparsers.add_parser(
            "workflow",
            help="运行工作流",
            description="执行 Super Dev 7 阶段工作流"
        )
        workflow_parser.add_argument(
            "--phase",
            choices=["discovery", "intelligence", "drafting", "redteam", "qa", "delivery", "deployment"],
            nargs="*",
            help="指定要执行的阶段"
        )
        workflow_parser.add_argument(
            "-q", "--quality-gate",
            type=int,
            help="质量门禁阈值 (0-100)"
        )

        # studio 命令
        studio_parser = subparsers.add_parser(
            "studio",
            help="启动交互工作台",
            description="启动 Super Dev Web 工作台 API 服务"
        )
        studio_parser.add_argument(
            "--host",
            default="127.0.0.1",
            help="监听地址 (默认: 127.0.0.1)"
        )
        studio_parser.add_argument(
            "--port",
            type=int,
            default=8765,
            help="监听端口 (默认: 8765)"
        )
        studio_parser.add_argument(
            "--reload",
            action="store_true",
            help="启用热重载 (开发模式)"
        )

        # expert 命令
        expert_parser = subparsers.add_parser(
            "expert",
            help="调用专家",
            description="直接调用特定专家"
        )
        expert_parser.add_argument(
            "--list",
            action="store_true",
            help="列出所有可用专家"
        )
        expert_parser.add_argument(
            "expert_name",
            nargs="?",
            choices=["PM", "ARCHITECT", "UI", "UX", "SECURITY", "CODE", "DBA", "QA", "DEVOPS", "RCA"],
            help="专家名称"
        )
        expert_parser.add_argument(
            "prompt",
            nargs="*",
            help="提示词"
        )

        # quality 命令
        quality_parser = subparsers.add_parser(
            "quality",
            help="质量检查",
            description="运行质量检查脚本"
        )
        quality_parser.add_argument(
            "-t", "--type",
            choices=["prd", "architecture", "ui", "ux", "ui-review", "code", "all"],
            default="all",
            help="检查类型"
        )

        # metrics 命令
        metrics_parser = subparsers.add_parser(
            "metrics",
            help="流水线指标",
            description="查看最近一次 pipeline 指标报告"
        )
        metrics_parser.add_argument(
            "--project",
            help="项目名（可选，默认自动匹配最近文件）",
        )
        metrics_parser.add_argument(
            "--history",
            action="store_true",
            help="显示多次流水线历史趋势",
        )
        metrics_parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="历史记录条数（默认 10）",
        )

        # preview 命令
        preview_parser = subparsers.add_parser(
            "preview",
            help="生成原型",
            description="从 UI 设计生成可交互的原型"
        )
        preview_parser.add_argument(
            "-o", "--output",
            default="preview.html",
            help="输出文件路径"
        )

        # deploy 命令
        deploy_parser = subparsers.add_parser(
            "deploy",
            help="生成部署配置",
            description="生成 Dockerfile 和 CI/CD 配置"
        )
        deploy_parser.add_argument(
            "--docker",
            action="store_true",
            help="生成 Dockerfile"
        )
        deploy_parser.add_argument(
            "--cicd",
            choices=SUPPORTED_CICD,
            help="生成 CI/CD 配置"
        )
        deploy_parser.add_argument(
            "--rehearsal",
            action="store_true",
            help="生成发布演练清单与回滚手册",
        )
        deploy_parser.add_argument(
            "--rehearsal-verify",
            action="store_true",
            help="执行发布演练验证并生成评分报告",
        )

        # config 命令
        config_parser = subparsers.add_parser(
            "config",
            help="配置管理",
            description="查看和修改项目配置"
        )
        config_parser.add_argument(
            "action",
            choices=["get", "set", "list"],
            help="操作"
        )
        config_parser.add_argument(
            "key",
            nargs="?",
            help="配置键"
        )
        config_parser.add_argument(
            "value",
            nargs="?",
            help="配置值"
        )

        # skill 命令 - 多平台 Skill 安装/管理
        skill_parser = subparsers.add_parser(
            "skill",
            help="Skill 管理",
            description="安装、列出、卸载跨平台 AI Coding Skills"
        )
        skill_parser.add_argument(
            "action",
            choices=["list", "install", "uninstall", "targets"],
            help="操作类型"
        )
        skill_parser.add_argument(
            "source_or_name",
            nargs="?",
            help="install 时为来源（目录/git/super-dev），uninstall 时为 skill 名称"
        )
        skill_parser.add_argument(
            "-t", "--target",
            choices=SUPPORTED_HOST_TOOLS,
            default="claude-code",
            help="目标平台 (默认: claude-code)"
        )
        skill_parser.add_argument(
            "--name",
            help="安装后的 skill 名称（可选）"
        )
        skill_parser.add_argument(
            "--force",
            action="store_true",
            help="覆盖已存在的 skill"
        )

        # integrate 命令 - 多平台适配配置
        integrate_parser = subparsers.add_parser(
            "integrate",
            help="平台集成配置",
            description="为 CLI/IDE AI Coding 工具生成集成配置文件"
        )
        integrate_parser.add_argument(
            "action",
            choices=["list", "setup", "harden", "matrix", "smoke", "audit", "validate"],
            help="操作类型"
        )
        integrate_parser.add_argument(
            "-t", "--target",
            choices=SUPPORTED_HOST_TOOLS,
            help="目标平台"
        )
        integrate_parser.add_argument(
            "--all",
            action="store_true",
            help="对所有平台执行 setup"
        )
        integrate_parser.add_argument(
            "--auto",
            action="store_true",
            help="自动探测本机已安装宿主，仅对检测到的宿主执行审计"
        )
        integrate_parser.add_argument(
            "--force",
            action="store_true",
            help="覆盖已存在的配置文件"
        )
        integrate_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 输出集成矩阵（用于自动化）"
        )
        integrate_parser.add_argument(
            "--repair",
            action="store_true",
            help="审计时自动重装缺失或过期的宿主接入面"
        )
        integrate_parser.add_argument(
            "--no-save",
            action="store_true",
            help="不将审计结果写入 output 报告"
        )
        integrate_parser.add_argument(
            "--status",
            choices=["pending", "passed", "failed"],
            help="用于 validate：写入某个宿主的真人运行时验收状态"
        )
        integrate_parser.add_argument(
            "--comment",
            help="用于 validate：补充真人运行时验收备注"
        )
        integrate_parser.add_argument(
            "--actor",
            default="user",
            help="用于 validate：记录操作者（默认: user）"
        )
        integrate_parser.add_argument(
            "--verify-docs",
            action="store_true",
            help="对宿主官方文档链接执行在线可达性核验（matrix/audit）",
        )
        integrate_parser.add_argument(
            "--official-compare",
            action="store_true",
            help="对照官方文档内容校验 slash/rules/skills 能力声明（matrix/audit/harden）",
        )
        integrate_parser.add_argument(
            "--parity-threshold",
            type=float,
            default=95.0,
            help="宿主一致性总分门槛（默认: 95.0）",
        )

        # onboard 命令 - 首次安装向导（宿主选择 + 集成 + skill + slash）
        onboard_parser = subparsers.add_parser(
            "onboard",
            help="首次接入向导",
            description="选择宿主 AI Coding 工具并自动完成集成、Skill 安装与 /super-dev 命令映射"
        )
        onboard_parser.add_argument(
            "--host",
            choices=SUPPORTED_HOST_TOOLS,
            help="宿主工具（不填则进入选择模式）"
        )
        onboard_parser.add_argument(
            "--all",
            action="store_true",
            help="对所有宿主工具执行接入"
        )
        onboard_parser.add_argument(
            "--auto",
            action="store_true",
            help="自动探测本机已安装宿主，仅对检测到的宿主执行接入"
        )
        onboard_parser.add_argument(
            "--skill-name",
            default="super-dev-core",
            help="安装后的 Skill 名称（默认: super-dev-core）"
        )
        onboard_parser.add_argument(
            "--skip-integrate",
            action="store_true",
            help="跳过规则文件集成"
        )
        onboard_parser.add_argument(
            "--skip-skill",
            action="store_true",
            help="跳过内置 Skill 安装"
        )
        onboard_parser.add_argument(
            "--skip-slash",
            action="store_true",
            help="跳过 /super-dev 命令映射文件生成"
        )
        onboard_parser.add_argument(
            "--yes",
            action="store_true",
            help="非交互模式（未指定 --host 时默认等价 --all）"
        )
        onboard_parser.add_argument(
            "--force",
            action="store_true",
            help="覆盖已存在文件并重装 Skill"
        )
        onboard_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="预览将要写入的文件，不实际执行"
        )
        onboard_parser.add_argument(
            "--stable-only",
            action="store_true",
            help="仅安装 Certified 和 Compatible 级别的宿主"
        )

        # doctor 命令 - 宿主接入诊断
        doctor_parser = subparsers.add_parser(
            "doctor",
            help="接入状态诊断",
            description="诊断当前项目在各宿主 AI Coding 工具中的集成、Skill、/super-dev 命令映射状态"
        )
        doctor_parser.add_argument(
            "--host",
            choices=SUPPORTED_HOST_TOOLS,
            help="仅诊断指定宿主（默认诊断全部）"
        )
        doctor_parser.add_argument(
            "--all",
            action="store_true",
            help="诊断全部宿主工具"
        )
        doctor_parser.add_argument(
            "--auto",
            action="store_true",
            help="自动探测本机已安装宿主，仅诊断检测到的宿主"
        )
        doctor_parser.add_argument(
            "--skill-name",
            default="super-dev-core",
            help="需要校验的 Skill 名称（默认: super-dev-core）"
        )
        doctor_parser.add_argument(
            "--skip-integrate",
            action="store_true",
            help="跳过集成规则文件检查"
        )
        doctor_parser.add_argument(
            "--skip-skill",
            action="store_true",
            help="跳过 Skill 检查"
        )
        doctor_parser.add_argument(
            "--skip-slash",
            action="store_true",
            help="跳过 /super-dev 命令映射检查"
        )
        doctor_parser.add_argument(
            "--json",
            action="store_true",
            help="输出 JSON 诊断结果"
        )
        doctor_parser.add_argument(
            "--repair",
            action="store_true",
            help="自动修复缺失项（集成规则 / Skill / slash 映射）"
        )
        doctor_parser.add_argument(
            "--force",
            action="store_true",
            help="修复时覆盖已有文件并重装 Skill"
        )

        # setup 命令 - 非技术用户一步接入
        setup_parser = subparsers.add_parser(
            "setup",
            help="一步接入安装",
            description="一步完成宿主接入（规则 + Skill + /super-dev）并执行诊断"
        )
        setup_parser.add_argument(
            "--host",
            choices=SUPPORTED_HOST_TOOLS,
            help="宿主工具（不填默认全部）"
        )
        setup_parser.add_argument(
            "--all",
            action="store_true",
            help="接入全部宿主工具"
        )
        setup_parser.add_argument(
            "--auto",
            action="store_true",
            help="自动探测本机已安装宿主，仅对检测到的宿主执行接入"
        )
        setup_parser.add_argument(
            "--skill-name",
            default="super-dev-core",
            help="安装后的 Skill 名称（默认: super-dev-core）"
        )
        setup_parser.add_argument(
            "--skip-integrate",
            action="store_true",
            help="跳过规则文件集成"
        )
        setup_parser.add_argument(
            "--skip-skill",
            action="store_true",
            help="跳过内置 Skill 安装"
        )
        setup_parser.add_argument(
            "--skip-slash",
            action="store_true",
            help="跳过 /super-dev 命令映射文件生成"
        )
        setup_parser.add_argument(
            "--skip-doctor",
            action="store_true",
            help="跳过接入诊断"
        )
        setup_parser.add_argument(
            "--force",
            action="store_true",
            help="覆盖已存在文件并重装 Skill"
        )
        setup_parser.add_argument(
            "--yes",
            action="store_true",
            help="非交互模式（未指定 --host 时默认等价 --all）"
        )

        # install 命令 - 面向 PyPI 用户的一键安装入口
        install_parser = subparsers.add_parser(
            "install",
            help="安装向导（宿主多选）",
            description="在终端内选择要接入的 AI Coding 宿主并完成接入安装"
        )
        install_parser.add_argument(
            "--host",
            choices=SUPPORTED_HOST_TOOLS,
            help="宿主工具（指定后只安装该宿主）"
        )
        install_parser.add_argument(
            "--all",
            action="store_true",
            help="安装全部宿主工具"
        )
        install_parser.add_argument(
            "--auto",
            action="store_true",
            help="自动探测本机已安装宿主并安装"
        )
        install_parser.add_argument(
            "--skill-name",
            default="super-dev-core",
            help="安装后的 Skill 名称（默认: super-dev-core）"
        )
        install_parser.add_argument(
            "--no-skill",
            action="store_true",
            help="只安装规则与 /super-dev 映射，不安装 skill"
        )
        install_parser.add_argument(
            "--skip-integrate",
            action="store_true",
            help="跳过规则文件集成"
        )
        install_parser.add_argument(
            "--skip-slash",
            action="store_true",
            help="跳过 /super-dev 命令映射文件生成"
        )
        install_parser.add_argument(
            "--skip-doctor",
            action="store_true",
            help="跳过安装后诊断"
        )
        install_parser.add_argument(
            "--force",
            action="store_true",
            help="覆盖已存在文件并重装 Skill"
        )
        install_parser.add_argument(
            "--yes",
            action="store_true",
            help="非交互模式（未指定 --host 时默认等价 --all）"
        )

        start_parser = subparsers.add_parser(
            "start",
            help="非技术用户起步入口",
            description="自动选择合适宿主、完成接入，并输出可直接复制的试用步骤"
        )
        start_parser.add_argument(
            "--idea",
            help="你的需求描述（可选，提供后会生成宿主内可直接使用的触发语句）"
        )
        start_parser.add_argument(
            "--host",
            choices=SUPPORTED_HOST_TOOLS,
            help="指定宿主；默认自动检测并选择最合适的宿主"
        )
        start_parser.add_argument(
            "--skip-onboard",
            action="store_true",
            help="只输出起步步骤，不自动写入规则、Skill 与命令映射"
        )
        start_parser.add_argument(
            "--no-save-profile",
            action="store_true",
            help="不写入 super-dev.yaml 的宿主画像"
        )
        start_parser.add_argument(
            "--force",
            action="store_true",
            help="覆盖已存在的规则、Skill 或命令映射"
        )
        start_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 输出起步说明"
        )

        # detect 命令 - 宿主自动探测与兼容性报告
        detect_parser = subparsers.add_parser(
            "detect",
            help="宿主探测与兼容性报告",
            description="自动探测本机可用宿主并输出接入兼容性评分"
        )
        detect_parser.add_argument(
            "--host",
            choices=SUPPORTED_HOST_TOOLS,
            help="仅分析指定宿主"
        )
        detect_parser.add_argument(
            "--all",
            action="store_true",
            help="分析全部宿主（默认仅分析自动探测到的宿主）"
        )
        detect_parser.add_argument(
            "--auto",
            action="store_true",
            help="显式启用自动探测模式（默认行为）"
        )
        detect_parser.add_argument(
            "--skill-name",
            default="super-dev-core",
            help="用于兼容性评分的 Skill 名称（默认: super-dev-core）"
        )
        detect_parser.add_argument(
            "--skip-integrate",
            action="store_true",
            help="评分时跳过集成规则文件检查"
        )
        detect_parser.add_argument(
            "--skip-skill",
            action="store_true",
            help="评分时跳过 Skill 检查"
        )
        detect_parser.add_argument(
            "--skip-slash",
            action="store_true",
            help="评分时跳过 /super-dev 命令映射检查"
        )
        detect_parser.add_argument(
            "--json",
            action="store_true",
            help="输出 JSON 结果"
        )
        detect_parser.add_argument(
            "--no-save",
            action="store_true",
            help="不写入 output/host-compatibility 报告文件"
        )
        detect_parser.add_argument(
            "--save-profile",
            action="store_true",
            help="将本次 selected_targets 保存到 super-dev.yaml 的 host_profile_targets，并启用 host_profile_enforce_selected"
        )

        update_parser = subparsers.add_parser(
            "update",
            help="升级到最新版本",
            description="检查 PyPI 最新版本并使用 pip 或 uv 升级当前 super-dev"
        )
        update_parser.add_argument(
            "--check",
            action="store_true",
            help="只检查最新版本，不执行升级"
        )
        update_parser.add_argument(
            "--method",
            choices=["auto", "pip", "uv"],
            default="auto",
            help="升级方式（默认: auto）"
        )

        review_parser = subparsers.add_parser(
            "review",
            help="管理文档确认等评审状态",
            description="记录或查看三文档确认状态"
        )
        review_subparsers = review_parser.add_subparsers(dest="review_command")

        review_docs_parser = review_subparsers.add_parser(
            "docs",
            help="查看或更新三文档确认状态"
        )
        review_docs_parser.add_argument(
            "--status",
            choices=["pending_review", "revision_requested", "confirmed"],
            help="要写入的三文档确认状态；不传则仅查看当前状态"
        )
        review_docs_parser.add_argument(
            "--comment",
            default="",
            help="确认意见或修改要求"
        )
        review_docs_parser.add_argument(
            "--run-id",
            default="",
            help="关联的运行 ID（可选）"
        )
        review_docs_parser.add_argument(
            "--actor",
            default="user",
            help="记录操作者（默认: user）"
        )
        review_docs_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出"
        )

        review_ui_parser = review_subparsers.add_parser(
            "ui",
            help="查看或更新 UI 改版状态"
        )
        review_ui_parser.add_argument(
            "--status",
            choices=["pending_review", "revision_requested", "confirmed"],
            help="要写入的 UI 改版状态；不传则仅查看当前状态"
        )
        review_ui_parser.add_argument(
            "--comment",
            default="",
            help="UI 改版意见或确认说明"
        )
        review_ui_parser.add_argument(
            "--run-id",
            default="",
            help="关联的运行 ID（可选）"
        )
        review_ui_parser.add_argument(
            "--actor",
            default="user",
            help="记录操作者（默认: user）"
        )
        review_ui_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出"
        )

        review_architecture_parser = review_subparsers.add_parser(
            "architecture",
            help="查看或更新架构返工状态"
        )
        review_architecture_parser.add_argument(
            "--status",
            choices=["pending_review", "revision_requested", "confirmed"],
            help="要写入的架构返工状态；不传则仅查看当前状态"
        )
        review_architecture_parser.add_argument(
            "--comment",
            default="",
            help="架构返工意见或确认说明"
        )
        review_architecture_parser.add_argument(
            "--run-id",
            default="",
            help="关联的运行 ID（可选）"
        )
        review_architecture_parser.add_argument(
            "--actor",
            default="user",
            help="记录操作者（默认: user）"
        )
        review_architecture_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出"
        )

        review_quality_parser = review_subparsers.add_parser(
            "quality",
            help="查看或更新质量返工状态"
        )
        review_quality_parser.add_argument(
            "--status",
            choices=["pending_review", "revision_requested", "confirmed"],
            help="要写入的质量返工状态；不传则仅查看当前状态"
        )
        review_quality_parser.add_argument(
            "--comment",
            default="",
            help="质量返工意见或确认说明"
        )
        review_quality_parser.add_argument(
            "--run-id",
            default="",
            help="关联的运行 ID（可选）"
        )
        review_quality_parser.add_argument(
            "--actor",
            default="user",
            help="记录操作者（默认: user）"
        )
        review_quality_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出"
        )

        release_parser = subparsers.add_parser(
            "release",
            help="发布收尾与就绪度检查",
            description="检查当前仓库距离对外发布还剩哪些关键缺口"
        )
        release_subparsers = release_parser.add_subparsers(dest="release_command")

        release_readiness_parser = release_subparsers.add_parser(
            "readiness",
            help="发布就绪度评估"
        )
        release_readiness_parser.add_argument(
            "--verify-tests",
            action="store_true",
            help="执行 pytest -q，并把测试结果纳入发布就绪度评分"
        )
        release_readiness_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 输出结果"
        )
        release_proof_pack_parser = release_subparsers.add_parser(
            "proof-pack",
            help="生成交付证据包摘要"
        )
        release_proof_pack_parser.add_argument(
            "--verify-tests",
            action="store_true",
            help="执行 release readiness 时纳入 pytest -q 结果"
        )
        release_proof_pack_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 输出结果"
        )

        # create 命令 - 一键创建项目
        create_parser = subparsers.add_parser(
            "create",
            help="一键创建项目 (从想法到规范)",
            description="从一句话描述自动生成 PRD、架构、UI/UX 文档并创建 Spec"
        )
        create_parser.add_argument(
            "description",
            help="功能描述 (如 '用户认证系统')"
        )
        create_parser.add_argument(
            "--mode",
            choices=["feature", "bugfix"],
            default="feature",
            help="请求模式（默认 feature；bugfix 会生成轻量补丁文档）",
        )
        create_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            default="web",
            help="目标平台"
        )
        create_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_PIPELINE_FRONTENDS,
            default="react",
            help="前端框架"
        )
        create_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            default="node",
            help="后端框架"
        )
        create_parser.add_argument(
            "-d", "--domain",
            choices=SUPPORTED_DOMAINS,
            default="",
            help="业务领域"
        )
        create_parser.add_argument(
            "--name",
            help="项目名称 (默认根据描述生成)"
        )
        create_parser.add_argument(
            "--skip-docs",
            action="store_true",
            help="跳过文档生成，只创建 Spec"
        )

        # wizard 命令 - 零门槛向导
        wizard_parser = subparsers.add_parser(
            "wizard",
            help="零门槛向导模式",
            description="通过向导收集业务需求并自动执行完整流水线"
        )
        wizard_parser.add_argument(
            "--idea",
            help="需求描述（提供后跳过交互输入）"
        )
        wizard_parser.add_argument(
            "--name",
            help="项目名称 (可选)"
        )
        wizard_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            help="目标平台（可选）"
        )
        wizard_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_PIPELINE_FRONTENDS,
            help="前端框架（可选）"
        )
        wizard_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            help="后端框架（可选）"
        )
        wizard_parser.add_argument(
            "-d", "--domain",
            choices=SUPPORTED_DOMAINS,
            help="业务领域（可选）"
        )
        wizard_parser.add_argument(
            "--cicd",
            choices=SUPPORTED_CICD,
            help="CI/CD 平台（可选）"
        )
        wizard_parser.add_argument(
            "--offline",
            action="store_true",
            help="离线模式（禁用联网检索）"
        )
        wizard_parser.add_argument(
            "--quick",
            action="store_true",
            help="快速模式：使用默认值（需配合 --idea）"
        )

        # design 命令 - 设计智能引擎
        design_parser = subparsers.add_parser(
            "design",
            help="设计智能引擎",
            description="搜索设计资产、生成设计系统、创建 design tokens"
        )
        design_subparsers = design_parser.add_subparsers(
            dest="design_command",
            title="设计命令",
            description="使用 'super-dev design <command> -h' 查看帮助"
        )

        # design search
        design_search_parser = design_subparsers.add_parser(
            "search",
            help="搜索设计资产",
            description="搜索 UI 风格、配色、字体、组件等设计资产"
        )
        design_search_parser.add_argument(
            "query",
            help="搜索关键词"
        )
        design_search_parser.add_argument(
            "-d", "--domain",
            choices=["style", "color", "typography", "component", "layout", "animation", "ux", "chart", "product"],
            help="搜索领域 (默认自动检测)"
        )
        design_search_parser.add_argument(
            "-n", "--max-results",
            type=int,
            default=5,
            help="最大结果数 (默认: 5)"
        )

        # design generate
        design_generate_parser = design_subparsers.add_parser(
            "generate",
            help="生成完整设计系统",
            description="基于产品类型和行业生成完整的设计系统"
        )
        design_generate_parser.add_argument(
            "--product",
            required=True,
            help="产品类型 (SaaS, E-commerce, Portfolio, Dashboard)"
        )
        design_generate_parser.add_argument(
            "--industry",
            required=True,
            help="行业 (Fintech, Healthcare, Education, Gaming)"
        )
        design_generate_parser.add_argument(
            "--keywords",
            nargs="+",
            help="关键词列表"
        )
        design_generate_parser.add_argument(
            "-p", "--platform",
            choices=["web", "mobile", "desktop"],
            default="web",
            help="目标平台 (默认: web)"
        )
        design_generate_parser.add_argument(
            "-a", "--aesthetic",
            help="美学方向 (可选)"
        )
        design_generate_parser.add_argument(
            "-o", "--output",
            default="output/design",
            help="输出目录 (默认: output/design)"
        )

        # design tokens
        design_tokens_parser = design_subparsers.add_parser(
            "tokens",
            help="生成 design tokens",
            description="生成 CSS 变量、Tailwind 配置等 design tokens"
        )
        design_tokens_parser.add_argument(
            "--primary",
            required=True,
            help="主色 (hex 值，如 #3B82F6)"
        )
        design_tokens_parser.add_argument(
            "--type",
            choices=["monochromatic", "analogous", "complementary", "triadic"],
            default="monochromatic",
            help="调色板类型 (默认: monochromatic)"
        )
        design_tokens_parser.add_argument(
            "--format",
            choices=["css", "json", "tailwind"],
            default="css",
            help="输出格式 (默认: css)"
        )
        design_tokens_parser.add_argument(
            "-o", "--output",
            help="输出文件路径"
        )

        # design landing - Landing 页面模式
        design_landing_parser = design_subparsers.add_parser(
            "landing",
            help="Landing 页面模式生成",
            description="搜索和推荐 Landing 页面布局模式"
        )
        design_landing_parser.add_argument(
            "query",
            nargs="?",
            help="搜索关键词（可选）"
        )
        design_landing_parser.add_argument(
            "--product-type",
            help="产品类型 (SaaS, E-commerce, Mobile, etc.)"
        )
        design_landing_parser.add_argument(
            "--goal",
            help="目标 (signup, purchase, demo, etc.)"
        )
        design_landing_parser.add_argument(
            "--audience",
            help="受众 (B2B, B2C, Enterprise, etc.)"
        )
        design_landing_parser.add_argument(
            "-n", "--max-results",
            type=int,
            default=5,
            help="最大结果数 (默认: 5)"
        )
        design_landing_parser.add_argument(
            "--list",
            action="store_true",
            help="列出所有可用模式"
        )

        # design chart - 图表类型推荐
        design_chart_parser = design_subparsers.add_parser(
            "chart",
            help="图表类型推荐",
            description="根据数据类型推荐最佳图表类型"
        )
        design_chart_parser.add_argument(
            "data_description",
            help="数据描述（如 'time series sales data'）"
        )
        design_chart_parser.add_argument(
            "-f", "--framework",
            choices=["react", "vue", "svelte", "angular", "next", "vanilla"],
            default="react",
            help="前端框架 (默认: react)"
        )
        design_chart_parser.add_argument(
            "-n", "--max-results",
            type=int,
            default=3,
            help="最大结果数 (默认: 3)"
        )
        design_chart_parser.add_argument(
            "--list",
            action="store_true",
            help="列出所有图表类型"
        )

        # design ux - UX 指南查询
        design_ux_parser = design_subparsers.add_parser(
            "ux",
            help="UX 指南查询",
            description="查询 UX 最佳实践和反模式"
        )
        design_ux_parser.add_argument(
            "query",
            help="搜索查询"
        )
        design_ux_parser.add_argument(
            "-d", "--domain",
            help="领域过滤 (Animation, A11y, Performance, etc.)"
        )
        design_ux_parser.add_argument(
            "-n", "--max-results",
            type=int,
            default=5,
            help="最大结果数 (默认: 5)"
        )
        design_ux_parser.add_argument(
            "--quick-wins",
            action="store_true",
            help="显示快速见效的改进建议"
        )
        design_ux_parser.add_argument(
            "--checklist",
            action="store_true",
            help="显示 UX 检查清单"
        )
        design_ux_parser.add_argument(
            "--list-domains",
            action="store_true",
            help="列出所有领域"
        )

        # design stack - 技术栈最佳实践
        design_stack_parser = design_subparsers.add_parser(
            "stack",
            help="技术栈最佳实践",
            description="查询技术栈最佳实践、性能优化和设计模式"
        )
        design_stack_parser.add_argument(
            "stack",
            help="技术栈名称 (Next.js, React, Vue, SvelteKit, etc.)"
        )
        design_stack_parser.add_argument(
            "query",
            nargs="?",
            help="搜索查询（可选）"
        )
        design_stack_parser.add_argument(
            "-c", "--category",
            help="类别过滤 (architecture, performance, state_management, etc.)"
        )
        design_stack_parser.add_argument(
            "--patterns",
            action="store_true",
            help="显示设计模式"
        )
        design_stack_parser.add_argument(
            "--performance",
            action="store_true",
            help="显示性能优化建议"
        )
        design_stack_parser.add_argument(
            "--quick-wins",
            action="store_true",
            help="显示快速见效的性能优化"
        )
        design_stack_parser.add_argument(
            "-n", "--max-results",
            type=int,
            default=5,
            help="最大结果数 (默认: 5)"
        )
        design_stack_parser.add_argument(
            "--list",
            action="store_true",
            help="列出所有支持的技术栈"
        )

        # design codegen - 代码片段生成
        design_codegen_parser = design_subparsers.add_parser(
            "codegen",
            help="代码片段生成",
            description="生成多框架的 UI 组件代码片段"
        )
        design_codegen_parser.add_argument(
            "component",
            help="组件名称 (button, card, input, etc.)"
        )
        design_codegen_parser.add_argument(
            "-f", "--framework",
            choices=["react", "nextjs", "vue", "svelte", "html", "tailwind"],
            default="react",
            help="目标框架 (默认: react)"
        )
        design_codegen_parser.add_argument(
            "-o", "--output",
            help="输出文件路径"
        )
        design_codegen_parser.add_argument(
            "--list",
            action="store_true",
            help="列出所有可用组件"
        )
        design_codegen_parser.add_argument(
            "--search",
            help="搜索组件"
        )

        # spec 命令 - Spec-Driven Development
        spec_parser = subparsers.add_parser(
            "spec",
            help="规范驱动开发 (SDD)",
            description="管理规范和变更提案"
        )
        spec_subparsers = spec_parser.add_subparsers(
            dest="spec_action",
            title="SDD 命令",
            description="使用 'super-dev spec <command> -h' 查看帮助"
        )

        # spec init
        spec_subparsers.add_parser(
            "init",
            help="初始化 SDD 目录结构"
        )

        # spec list
        spec_list_parser = spec_subparsers.add_parser(
            "list",
            help="列出所有变更"
        )
        spec_list_parser.add_argument(
            "--status",
            choices=["draft", "proposed", "approved", "in_progress", "completed", "archived"],
            help="按状态过滤"
        )

        # spec show
        spec_show_parser = spec_subparsers.add_parser(
            "show",
            help="显示变更详情"
        )
        spec_show_parser.add_argument(
            "change_id",
            help="变更 ID"
        )

        # spec propose
        spec_propose_parser = spec_subparsers.add_parser(
            "propose",
            help="创建变更提案"
        )
        spec_propose_parser.add_argument(
            "change_id",
            help="变更 ID (如 add-user-auth)"
        )
        spec_propose_parser.add_argument(
            "--title",
            required=True,
            help="变更标题"
        )
        spec_propose_parser.add_argument(
            "--description",
            required=True,
            help="变更描述"
        )
        spec_propose_parser.add_argument(
            "--motivation",
            help="变更动机/背景"
        )
        spec_propose_parser.add_argument(
            "--impact",
            help="影响范围"
        )
        spec_propose_parser.add_argument(
            "--no-scaffold",
            action="store_true",
            help="仅创建 proposal，不生成 spec/plan/tasks/checklist 模板"
        )

        # spec add-req
        spec_add_req_parser = spec_subparsers.add_parser(
            "add-req",
            help="向变更添加需求"
        )
        spec_add_req_parser.add_argument(
            "change_id",
            help="变更 ID"
        )
        spec_add_req_parser.add_argument(
            "spec_name",
            help="规范名称 (如 auth, user-profile)"
        )
        spec_add_req_parser.add_argument(
            "req_name",
            help="需求名称"
        )
        spec_add_req_parser.add_argument(
            "description",
            help="需求描述"
        )

        spec_scaffold_parser = spec_subparsers.add_parser(
            "scaffold",
            help="为变更生成 spec/plan/tasks/checklist 四件套"
        )
        spec_scaffold_parser.add_argument(
            "change_id",
            help="变更 ID"
        )
        spec_scaffold_parser.add_argument(
            "--force",
            action="store_true",
            help="强制覆盖已存在文件"
        )

        spec_quality_parser = spec_subparsers.add_parser(
            "quality",
            help="评估 Spec 完整度与质量分"
        )
        spec_quality_parser.add_argument(
            "change_id",
            help="变更 ID"
        )
        spec_quality_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出"
        )

        # spec archive
        spec_archive_parser = spec_subparsers.add_parser(
            "archive",
            help="归档已完成的变更"
        )
        spec_archive_parser.add_argument(
            "change_id",
            help="变更 ID"
        )
        spec_archive_parser.add_argument(
            "-y", "--yes",
            action="store_true",
            help="跳过确认"
        )

        # spec validate
        spec_validate_parser = spec_subparsers.add_parser(
            "validate",
            help="验证规格格式和结构"
        )
        spec_validate_parser.add_argument(
            "change_id",
            nargs="?",
            help="变更 ID (留空则验证所有变更)"
        )
        spec_validate_parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="显示详细信息"
        )

        # spec view
        spec_view_parser = spec_subparsers.add_parser(
            "view",
            help="交互式仪表板 - 显示所有规范和变更"
        )
        spec_view_parser.add_argument(
            "--refresh",
            action="store_true",
            help="强制刷新数据"
        )

        # task 命令 - 独立执行/查看 Spec 任务闭环
        task_parser = subparsers.add_parser(
            "task",
            help="Spec 任务闭环执行",
            description="执行或查看 `.super-dev/changes/*/tasks.md` 的任务状态"
        )
        task_parser.add_argument(
            "action",
            choices=["run", "status", "list"],
            help="任务操作类型"
        )
        task_parser.add_argument(
            "change_id",
            nargs="?",
            help="变更 ID（run/status 必填）"
        )
        task_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            help="目标平台（可选，默认取项目配置）"
        )
        task_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_PIPELINE_FRONTENDS,
            help="前端框架（可选，默认取项目配置）"
        )
        task_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            help="后端框架（可选，默认取项目配置）"
        )
        task_parser.add_argument(
            "-d", "--domain",
            choices=SUPPORTED_DOMAINS,
            help="业务领域（可选，默认取项目配置）"
        )
        task_parser.add_argument(
            "--project-name",
            help="任务执行报告中的项目名（默认取配置名或 change_id）"
        )
        task_parser.add_argument(
            "--max-retries",
            type=int,
            default=1,
            help="失败自动修复重试次数（默认: 1）"
        )

        # pipeline 命令 - 完整流水线
        pipeline_parser = subparsers.add_parser(
            "pipeline",
            help="运行完整流水线 (从想法到部署)",
            description="执行完整开发流水线：需求增强 → 文档 → 前端骨架 → Spec → 实现骨架 → 审查与门禁 → 交付配置"
        )
        pipeline_parser.add_argument(
            "description",
            help="功能描述 (如 '用户认证系统')"
        )
        pipeline_parser.add_argument(
            "--mode",
            choices=["feature", "bugfix"],
            default="feature",
            help="请求模式（默认 feature；bugfix 会启用轻量缺陷修复路径）",
        )
        pipeline_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            default="web",
            help="目标平台"
        )
        pipeline_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_PIPELINE_FRONTENDS,
            default="react",
            help="前端框架"
        )
        pipeline_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            default="node",
            help="后端框架"
        )
        pipeline_parser.add_argument(
            "-d", "--domain",
            choices=SUPPORTED_DOMAINS,
            default="",
            help="业务领域"
        )
        pipeline_parser.add_argument(
            "--name",
            help="项目名称 (默认根据描述生成)"
        )
        pipeline_parser.add_argument(
            "--cicd",
            choices=SUPPORTED_CICD,
            default="all",
            help="CI/CD 平台"
        )
        pipeline_parser.add_argument(
            "--skip-redteam",
            action="store_true",
            help="跳过红队审查"
        )
        pipeline_parser.add_argument(
            "--skip-scaffold",
            action="store_true",
            help="跳过前后端实现骨架生成"
        )
        pipeline_parser.add_argument(
            "--skip-quality-gate",
            action="store_true",
            help="跳过质量门禁检查"
        )
        pipeline_parser.add_argument(
            "--offline",
            action="store_true",
            help="离线模式（禁用联网检索）"
        )
        pipeline_parser.add_argument(
            "--quality-threshold",
            type=int,
            default=None,
            help="质量门禁阈值（可选；默认按场景自动判定）"
        )
        pipeline_parser.add_argument(
            "--skip-rehearsal-verify",
            action="store_true",
            help="跳过发布演练验证（默认执行）",
        )
        pipeline_parser.add_argument(
            "--resume",
            action="store_true",
            help="恢复模式：优先复用上次已完成阶段产物（含自动降级与审计报告）",
        )

        fix_parser = subparsers.add_parser(
            "fix",
            help="显式缺陷修复模式",
            description="以轻量 bugfix 路径执行问题复现、补丁文档、修复与回归验证",
        )
        fix_parser.add_argument(
            "description",
            help="缺陷描述 (如 '修复登录接口 500 并补充回归验证')",
        )
        fix_parser.add_argument(
            "-p", "--platform",
            choices=SUPPORTED_PLATFORMS,
            default="web",
            help="目标平台"
        )
        fix_parser.add_argument(
            "-f", "--frontend",
            choices=SUPPORTED_PIPELINE_FRONTENDS,
            default="react",
            help="前端框架"
        )
        fix_parser.add_argument(
            "-b", "--backend",
            choices=SUPPORTED_PIPELINE_BACKENDS,
            default="node",
            help="后端框架"
        )
        fix_parser.add_argument(
            "-d", "--domain",
            choices=SUPPORTED_DOMAINS,
            default="",
            help="业务领域"
        )
        fix_parser.add_argument(
            "--name",
            help="项目名称 (默认根据描述生成)"
        )
        fix_parser.add_argument(
            "--cicd",
            choices=SUPPORTED_CICD,
            default="all",
            help="CI/CD 平台"
        )
        fix_parser.add_argument(
            "--skip-redteam",
            action="store_true",
            help="跳过红队审查"
        )
        fix_parser.add_argument(
            "--skip-scaffold",
            action="store_true",
            help="跳过前后端实现骨架生成"
        )
        fix_parser.add_argument(
            "--skip-quality-gate",
            action="store_true",
            help="跳过质量门禁检查"
        )
        fix_parser.add_argument(
            "--offline",
            action="store_true",
            help="离线模式（禁用联网检索）"
        )
        fix_parser.add_argument(
            "--quality-threshold",
            type=int,
            default=None,
            help="质量门禁阈值（可选；默认按场景自动判定）"
        )
        fix_parser.add_argument(
            "--skip-rehearsal-verify",
            action="store_true",
            help="跳过发布演练验证（默认执行）",
        )

        # run 命令 - 运行控制（如失败恢复）
        run_parser = subparsers.add_parser(
            "run",
            help="运行控制",
            description="运行控制命令（恢复、状态、阶段回跳、阶段确认）"
        )
        run_parser.add_argument(
            "stage_selector",
            nargs="?",
            help="快捷阶段入口（如 research/prd/architecture/uiux/frontend/backend/quality）",
        )
        run_parser.add_argument(
            "--resume",
            action="store_true",
            help="恢复最近一次失败的 pipeline 运行",
        )
        run_parser.add_argument(
            "--status",
            action="store_true",
            help="查看当前流程状态、阶段确认与推荐下一步",
        )
        run_parser.add_argument(
            "--phase",
            help="从指定阶段继续执行（如 docs/spec/frontend/backend/quality/delivery）",
        )
        run_parser.add_argument(
            "--jump",
            help="跳转到指定阶段并继续执行（会先展示影响面）",
        )
        run_parser.add_argument(
            "--confirm",
            dest="confirm_phase",
            help="确认指定阶段（docs/ui/architecture/quality/frontend/backend/delivery）",
        )
        run_parser.add_argument(
            "--comment",
            default="",
            help="阶段确认备注",
        )
        run_parser.add_argument(
            "--actor",
            default="cli-user",
            help="阶段确认操作者",
        )
        run_parser.add_argument(
            "--json",
            action="store_true",
            help="状态输出使用 JSON 格式",
        )

        status_parser = subparsers.add_parser(
            "status",
            help="查看当前流程状态",
            description="快捷别名，等同于 super-dev run --status",
        )
        status_parser.add_argument(
            "--json",
            action="store_true",
            help="状态输出使用 JSON 格式",
        )

        jump_parser = subparsers.add_parser(
            "jump",
            help="跳转到指定阶段",
            description="快捷别名，等同于 super-dev run --jump <stage>",
        )
        jump_parser.add_argument(
            "stage",
            help="目标阶段（如 docs/frontend/backend/quality）",
        )

        confirm_parser = subparsers.add_parser(
            "confirm",
            help="确认指定阶段",
            description="快捷别名，等同于 super-dev run --confirm <phase>",
        )
        confirm_parser.add_argument(
            "phase",
            help="需要确认的阶段（如 docs/preview/frontend/backend/quality）",
        )
        confirm_parser.add_argument(
            "--comment",
            default="",
            help="阶段确认备注",
        )
        confirm_parser.add_argument(
            "--actor",
            default="cli-user",
            help="阶段确认操作者",
        )

        policy_parser = subparsers.add_parser(
            "policy",
            help="流水线治理策略",
            description="管理 Super Dev 的流水线策略（Policy DSL）"
        )
        policy_subparsers = policy_parser.add_subparsers(dest="action")
        policy_subparsers.add_parser("show", help="显示当前策略")
        policy_subparsers.add_parser("presets", help="显示可用策略预设")
        policy_init_parser = policy_subparsers.add_parser("init", help="生成策略文件")
        policy_init_parser.add_argument(
            "--preset",
            choices=["default", "balanced", "enterprise"],
            default="default",
            help="策略预设（默认 default）",
        )
        policy_init_parser.add_argument(
            "--force",
            action="store_true",
            help="强制覆盖已有策略文件",
        )

        return parser

    def _public_host_targets(self, *, integration_manager) -> list[str]:
        available_targets = [item.name for item in integration_manager.list_targets()]
        public_targets = [target for target in PRIMARY_SUPPORTED_HOST_TOOLS if target in available_targets]
        return public_targets or available_targets

    def run(self, args: list | None = None) -> int:
        """
        运行 CLI

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        argv = list(args) if args is not None else sys.argv[1:]

        # 兼容 `super-dev help` / `super-dev version` 这类用户习惯输入
        if len(argv) == 1 and argv[0] == "help":
            self._print_banner()
            self.parser.print_help()
            return 0
        if len(argv) == 1 and argv[0] == "version":
            self.console.print(f"super-dev {__version__}")
            return 0

        # 直达入口：`super-dev <需求描述>`
        if self._is_direct_requirement_input(argv):
            try:
                description, direct_overrides = self._parse_direct_requirement_args(argv)
            except ValueError as exc:
                self.console.print(f"[red]{exc}[/red]")
                return 2
            return self._run_direct_requirement(description, direct_overrides)

        parsed_args = self.parser.parse_args(argv)

        if parsed_args.command is None:
            install_args = argparse.Namespace(
                host=None,
                all=False,
                auto=False,
                skill_name="super-dev-core",
                no_skill=False,
                skip_integrate=False,
                skip_slash=False,
                skip_doctor=False,
                force=False,
                yes=False,
            )
            return self._cmd_install(install_args)

        # 路由到对应命令
        command_name = str(parsed_args.command).replace("-", "_")
        command_handler = getattr(self, f"_cmd_{command_name}", None)
        if command_handler is None or not callable(command_handler):
            self.console.print(f"[red]未知命令: {parsed_args.command}[/red]")
            return 1

        try:
            handler = cast(Callable[[Any], int], command_handler)
            return int(handler(parsed_args))

        except SuperDevError as e:
            # 已知异常 - 显示友好错误信息
            self.console.print(f"[red]错误: {e.message}[/red]")
            if e.details:
                self.logger.warning(f"命令执行失败: {e.code}", extra={'details': e.details})
            return 1

        except KeyboardInterrupt:
            # 用户中断
            self.console.print("\n[yellow]操作已取消[/yellow]")
            return 130

        except Exception as e:
            # 未知异常 - 显示详细错误信息
            self.console.print(f"[red]未预期的错误: {str(e)}[/red]")

            # 记录完整错误栈
            self.logger.error(
                f"CLI命令异常: {parsed_args.command}",
                extra={
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc()
                }
            )

            # 在调试模式下显示traceback
            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())

            return 1

    # ==================== 命令处理器 ====================

    def _cmd_init(self, args) -> int:
        """初始化项目"""
        config_manager = get_config_manager()

        # 检查是否已初始化
        if config_manager.exists():
            self.console.print("[yellow]项目已初始化，使用 'super-dev config set' 修改配置[/yellow]")
            return 0

        # 创建配置
        config = config_manager.create(
            name=args.name,
            description=args.description,
            platform=args.platform,
            frontend=args.frontend,
            backend=args.backend,
            domain=args.domain,
            ui_library=getattr(args, 'ui_library', None),
            style_solution=getattr(args, 'style', None),
            state_management=getattr(args, 'state', []) or [],
            testing_frameworks=getattr(args, 'testing', []) or [],
        )

        # 创建输出目录
        output_dir = Path.cwd() / config.output_dir
        output_dir.mkdir(exist_ok=True)
        workflow_file, summary_file = self._bootstrap_project_contract(
            project_dir=Path.cwd(),
            config=config,
        )

        self.console.print(f"[green]✓[/green] 项目已初始化: {config.name}")
        self.console.print(f"  平台: {config.platform}")
        self.console.print(f"  前端框架: {config.frontend}")
        if config.ui_library:
            self.console.print(f"  UI 组件库: {config.ui_library}")
        if config.style_solution:
            self.console.print(f"  样式方案: {config.style_solution}")
        if config.state_management:
            self.console.print(f"  状态管理: {', '.join(config.state_management)}")
        if config.testing_frameworks:
            self.console.print(f"  测试框架: {', '.join(config.testing_frameworks)}")
        self.console.print(f"  后端: {config.backend}")
        if config.domain:
            self.console.print(f"  领域: {config.domain}")
        self.console.print(f"  工作流契约: {workflow_file}")
        self.console.print(f"  Bootstrap 摘要: {summary_file}")

        self.console.print("\n[dim]下一步:[/dim]")
        self.console.print("  1. 查看 output/*-bootstrap.md 确认初始化结果")
        self.console.print("  2. 运行 'super-dev start --idea \"你的需求\"' 或在宿主中触发 /super-dev")
        self.console.print("  3. 如需手动管理 SDD，可运行 'super-dev spec init'")

        return 0

    def _cmd_bootstrap(self, args) -> int:
        """显式初始化 bootstrap 契约。"""
        project_dir = Path.cwd()
        config_manager = get_config_manager()

        if config_manager.exists():
            config = config_manager.config
        else:
            config = config_manager.create(
                name=args.name or project_dir.name,
                description=args.description,
                platform=args.platform,
                frontend=args.frontend,
                backend=args.backend,
                domain=args.domain,
                ui_library=getattr(args, "ui_library", None),
                style_solution=getattr(args, "style", None),
                state_management=getattr(args, "state", []) or [],
                testing_frameworks=getattr(args, "testing", []) or [],
            )

        workflow_file, summary_file = self._bootstrap_project_contract(
            project_dir=project_dir,
            config=config,
        )
        self.console.print("[green]✓[/green] Bootstrap 已完成")
        self.console.print(f"  项目配置: {config_manager.config_path}")
        self.console.print(f"  工作流契约: {workflow_file}")
        self.console.print(f"  Bootstrap 摘要: {summary_file}")
        self.console.print("")
        self.console.print("[cyan]下一步:[/cyan]")
        self.console.print("  1. 运行 super-dev start --idea \"你的需求\"")
        self.console.print("  2. 或直接在已接入宿主中触发 /super-dev / super-dev:")
        return 0

    def _bootstrap_project_contract(self, project_dir: Path, config) -> tuple[Path, Path]:
        """创建显式 bootstrap 工作流契约与摘要。"""
        from .specs import SpecGenerator

        output_dir = project_dir / config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        generator = SpecGenerator(project_dir)
        generator.init_sdd()

        workflow_file = project_dir / ".super-dev" / "WORKFLOW.md"
        workflow_file.write_text(
            self._render_workflow_contract_markdown(config=config, project_dir=project_dir),
            encoding="utf-8",
        )

        summary_file = output_dir / f"{config.name}-bootstrap.md"
        summary_file.write_text(
            self._render_bootstrap_summary_markdown(config=config, project_dir=project_dir),
            encoding="utf-8",
        )
        return workflow_file, summary_file

    def _render_workflow_contract_markdown(self, config, project_dir: Path) -> str:
        timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        return f"""# Super Dev Workflow Contract

> Generated by `super-dev bootstrap`
> Updated: {timestamp}

## Project

- Name: {config.name}
- Description: {config.description or "待补充"}
- Platform: {config.platform}
- Frontend: {config.frontend}
- Backend: {config.backend}
- Domain: {config.domain or "未指定"}

## Bootstrap Outcome

This repository has been explicitly bootstrapped for Super Dev.

The following surfaces are now the project bootstrap contract:

- `super-dev.yaml`
- `.super-dev/WORKFLOW.md`
- `.super-dev/project.md`
- `.super-dev/AGENTS.md`
- `.super-dev/specs/`
- `.super-dev/changes/`
- `output/{config.name}-bootstrap.md`

## Required Pipeline Order

1. research
2. PRD / Architecture / UIUX
3. wait for user confirmation
4. Spec / tasks
5. frontend first + runtime validation
6. backend / integration / tests
7. quality gate
8. delivery ready + rehearsal passed

## Trigger Rules

- Slash hosts: `/super-dev <需求描述>`
- Text-trigger hosts: `super-dev: <需求描述>` or `super-dev：<需求描述>`

## Bootstrap Guidance

Use `super-dev start --idea "<需求描述>"` for the shortest guided path.

If the repository already has a host onboarded, trigger Super Dev directly inside the host.

## Project Context File

Fill `.super-dev/project.md` with domain constraints, architecture notes, delivery expectations, and team conventions.
"""

    def _render_bootstrap_summary_markdown(self, config, project_dir: Path) -> str:
        timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        return f"""# {config.name} Bootstrap Summary

> Generated by `super-dev bootstrap`
> Updated: {timestamp}

## Result

Super Dev has explicitly initialized this repository.

Generated bootstrap assets:

- `super-dev.yaml`
- `.super-dev/WORKFLOW.md`
- `.super-dev/project.md`
- `.super-dev/AGENTS.md`
- `.super-dev/specs/`
- `.super-dev/changes/`

## Current Stack

- Platform: `{config.platform}`
- Frontend: `{config.frontend}`
- Backend: `{config.backend}`
- Domain: `{config.domain or "未指定"}`

## How To Start

### Option 1. Guided bootstrap

```bash
super-dev start --idea "你的需求"
```

### Option 2. Host trigger

- Slash hosts: `/super-dev 你的需求`
- Text-trigger hosts: `super-dev: 你的需求` or `super-dev：你的需求`

## What Happens Next

1. Super Dev enforces `research` first.
2. The host writes:
   - `output/*-research.md`
   - `output/*-prd.md`
   - `output/*-architecture.md`
   - `output/*-uiux.md`
3. The workflow pauses for user confirmation.
4. Only then can Spec / tasks and implementation continue.

## Notes

- This bootstrap summary is the visible initialization artifact for repository operators.
- `.super-dev/WORKFLOW.md` is the repository workflow contract for hosts and maintainers.
- `super-dev spec init` can be used later to reinitialize SDD directories if needed.
"""

    def _cmd_analyze(self, args) -> int:
        """分析现有项目"""
        from .analyzer import ProjectAnalyzer

        project_path = Path(args.path).resolve()

        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        try:
            analyzer = ProjectAnalyzer(project_path)
            report = analyzer.analyze()

            # 根据格式输出
            output_format = "json" if args.json else args.format

            if output_format == "json":
                import json
                output = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)

                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                else:
                    sys.stdout.write(output + "\n")
                return 0

            self.console.print(f"[cyan]正在分析项目: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()

                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]报告已保存到: {args.output}[/green]")
                else:
                    self.console.print(output)

            else:  # text
                framework_value = (
                    report.tech_stack.framework.value
                    if hasattr(report.tech_stack.framework, "value")
                    else str(report.tech_stack.framework)
                )
                self.console.print("[cyan]项目分析报告[/cyan]")
                self.console.print(f"  路径: {report.project_path}")
                self.console.print(f"  类型: {report.category.value}")
                self.console.print(f"  语言: {report.tech_stack.language}")
                self.console.print(f"  框架: {framework_value}")
                if report.tech_stack.ui_library:
                    self.console.print(f"  UI 库: {report.tech_stack.ui_library}")
                if report.tech_stack.state_management:
                    self.console.print(f"  状态管理: {report.tech_stack.state_management}")
                self.console.print(f"  文件数: {report.file_count}")
                self.console.print(f"  代码行数: {report.total_lines:,}")
                self.console.print(f"  依赖数: {len(report.tech_stack.dependencies)}")

                if args.output:
                    Path(args.output).write_text(report.to_markdown(), encoding="utf-8")
                    self.console.print(f"[green]报告已保存到: {args.output}[/green]")

            return 0

        except FileNotFoundError as e:
            self.console.print(f"[red]路径不存在: {e}[/red]")
            self.logger.error("分析失败: 文件不存在", extra={'path': str(e)})
            return 1

        except PermissionError as e:
            self.console.print(f"[red]权限不足: {e}[/red]")
            self.logger.error("分析失败: 权限错误", extra={'path': str(e)})
            return 1

        except Exception as e:
            self.console.print(f"[red]分析失败: {e}[/red]")
            self.logger.error(
                f"分析异常: {type(e).__name__}",
                extra={
                    'error_message': str(e),
                    'traceback': traceback.format_exc()
                }
            )

            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())

            return 1

    def _cmd_repo_map(self, args) -> int:
        """生成代码库地图。"""
        from .analyzer import RepoMapBuilder

        project_path = Path(args.path).resolve()
        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        try:
            builder = RepoMapBuilder(project_path)
            report = builder.build()
            output_format = "json" if args.json else args.format

            if output_format == "json":
                output = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                else:
                    builder.write(report)
                    sys.stdout.write(output + "\n")
                return 0

            self.console.print(f"[cyan]正在生成 Repo Map: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]Repo Map 已保存到: {args.output}[/green]")
                else:
                    paths = builder.write(report)
                    self.console.print("[green]Repo Map 已生成[/green]")
                    self.console.print(f"  Markdown: {paths['markdown']}")
                    self.console.print(f"  JSON: {paths['json']}")
                return 0

            paths = builder.write(report)
            self.console.print("[green]Repo Map 已生成[/green]")
            self.console.print(f"  项目: {report.project_name}")
            self.console.print(f"  Markdown: {paths['markdown']}")
            self.console.print(f"  JSON: {paths['json']}")
            self.console.print(f"  入口文件: {len(report.entry_points)}")
            self.console.print(f"  核心模块: {len(report.top_modules)}")
            self.console.print(f"  集成面: {len(report.integration_surfaces)}")
            self.console.print(f"  风险点: {len(report.risk_points)}")
            self.console.print("")
            self.console.print("[cyan]建议阅读顺序:[/cyan]")
            for item in report.recommended_reading_order[:5]:
                self.console.print(f"  - {item.path}: {item.summary}")
            return 0

        except Exception as e:
            self.console.print(f"[red]生成 Repo Map 失败: {e}[/red]")
            self.logger.error(
                "Repo Map 生成失败",
                extra={"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()},
            )
            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())
            return 1

    def _cmd_impact(self, args) -> int:
        """分析变更影响范围。"""
        from .analyzer import ImpactAnalyzer

        project_path = Path(args.path).resolve()
        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        if not args.description and not args.files:
            self.console.print("[yellow]请提供变更描述或 --files 列表，例如 `super-dev impact \"修改登录流程\" --files services/auth.py`[/yellow]")
            return 1

        try:
            analyzer = ImpactAnalyzer(project_path)
            report = analyzer.build(description=args.description, files=list(args.files or []))
            output_format = "json" if args.json else args.format

            if output_format == "json":
                output = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                else:
                    analyzer.write(report)
                    sys.stdout.write(output + "\n")
                return 0

            self.console.print(f"[cyan]正在分析变更影响范围: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]Impact Analysis 已保存到: {args.output}[/green]")
                else:
                    paths = analyzer.write(report)
                    self.console.print("[green]Impact Analysis 已生成[/green]")
                    self.console.print(f"  Markdown: {paths['markdown']}")
                    self.console.print(f"  JSON: {paths['json']}")
                return 0

            paths = analyzer.write(report)
            self.console.print("[green]Impact Analysis 已生成[/green]")
            self.console.print(f"  项目: {report.project_name}")
            self.console.print(f"  风险等级: {report.risk_level}")
            self.console.print(f"  Markdown: {paths['markdown']}")
            self.console.print(f"  JSON: {paths['json']}")
            self.console.print(f"  受影响模块: {len(report.affected_modules)}")
            self.console.print(f"  受影响入口: {len(report.affected_entry_points)}")
            self.console.print(f"  受影响集成面: {len(report.affected_integration_surfaces)}")
            self.console.print("")
            self.console.print(f"[cyan]{report.summary}[/cyan]")
            self.console.print("")
            self.console.print("[cyan]回归重点:[/cyan]")
            for item in report.regression_focus:
                self.console.print(f"  - {item}")
            self.console.print("")
            self.console.print("[cyan]建议动作:[/cyan]")
            for item in report.recommended_steps:
                self.console.print(f"  - {item}")
            return 0

        except Exception as e:
            self.console.print(f"[red]Impact Analysis 生成失败: {e}[/red]")
            self.logger.error(
                "Impact Analysis 生成失败",
                extra={"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()},
            )
            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())
            return 1

    def _cmd_regression_guard(self, args) -> int:
        """生成回归检查清单。"""
        from .analyzer import RegressionGuardBuilder

        project_path = Path(args.path).resolve()
        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        if not args.description and not args.files:
            self.console.print(
                "[yellow]请提供变更描述或 --files 列表，例如 `super-dev regression-guard \"修改登录流程\" --files services/auth.py`[/yellow]"
            )
            return 1

        try:
            builder = RegressionGuardBuilder(project_path)
            report = builder.build(description=args.description, files=list(args.files or []))
            output_format = "json" if args.json else args.format

            if output_format == "json":
                output = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                else:
                    builder.write(report)
                    sys.stdout.write(output + "\n")
                return 0

            self.console.print(f"[cyan]正在生成 Regression Guard: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]Regression Guard 已保存到: {args.output}[/green]")
                else:
                    paths = builder.write(report)
                    self.console.print("[green]Regression Guard 已生成[/green]")
                    self.console.print(f"  Markdown: {paths['markdown']}")
                    self.console.print(f"  JSON: {paths['json']}")
                return 0

            paths = builder.write(report)
            self.console.print("[green]Regression Guard 已生成[/green]")
            self.console.print(f"  项目: {report.project_name}")
            self.console.print(f"  风险等级: {report.risk_level}")
            self.console.print(f"  Markdown: {paths['markdown']}")
            self.console.print(f"  JSON: {paths['json']}")
            self.console.print(f"  高优先级检查: {len(report.high_priority_checks)}")
            self.console.print(f"  中优先级检查: {len(report.medium_priority_checks)}")
            self.console.print(f"  支撑性检查: {len(report.supporting_checks)}")
            self.console.print("")
            self.console.print(f"[cyan]{report.summary}[/cyan]")
            self.console.print("")
            self.console.print("[cyan]推荐命令:[/cyan]")
            for item in report.recommended_commands:
                self.console.print(f"  - {item}")
            return 0

        except Exception as e:
            self.console.print(f"[red]Regression Guard 生成失败: {e}[/red]")
            self.logger.error(
                "Regression Guard 生成失败",
                extra={"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()},
            )
            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())
            return 1

    def _cmd_dependency_graph(self, args) -> int:
        """生成依赖图与关键路径。"""
        from .analyzer import DependencyGraphBuilder

        project_path = Path(args.path).resolve()
        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        try:
            builder = DependencyGraphBuilder(project_path)
            report = builder.build()
            output_format = "json" if args.json else args.format

            if output_format == "json":
                output = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                else:
                    builder.write(report)
                    sys.stdout.write(output + "\n")
                return 0

            self.console.print(f"[cyan]正在生成 Dependency Graph: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]Dependency Graph 已保存到: {args.output}[/green]")
                else:
                    paths = builder.write(report)
                    self.console.print("[green]Dependency Graph 已生成[/green]")
                    self.console.print(f"  Markdown: {paths['markdown']}")
                    self.console.print(f"  JSON: {paths['json']}")
                return 0

            paths = builder.write(report)
            self.console.print("[green]Dependency Graph 已生成[/green]")
            self.console.print(f"  项目: {report.project_name}")
            self.console.print(f"  Markdown: {paths['markdown']}")
            self.console.print(f"  JSON: {paths['json']}")
            self.console.print(f"  节点数: {report.node_count}")
            self.console.print(f"  边数: {report.edge_count}")
            self.console.print(f"  关键节点: {len(report.critical_nodes)}")
            self.console.print(f"  关键路径: {len(report.critical_paths)}")
            self.console.print("")
            self.console.print(f"[cyan]{report.summary}[/cyan]")
            return 0

        except Exception as e:
            self.console.print(f"[red]Dependency Graph 生成失败: {e}[/red]")
            self.logger.error(
                "Dependency Graph 生成失败",
                extra={"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()},
            )
            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())
            return 1

    def _cmd_workflow(self, args) -> int:
        """运行工作流"""
        project_dir = Path.cwd()
        config_manager = ConfigManager(project_dir)

        if not config_manager.exists():
            self.console.print("[red]未找到项目配置，请先运行 'super-dev init'[/red]")
            return 1

        # 更新质量门禁
        if args.quality_gate is not None:
            config_manager.update(quality_gate=args.quality_gate)

        # 确定要执行的阶段
        phases = None
        if args.phase:
            phase_map = {
                "discovery": Phase.DISCOVERY,
                "intelligence": Phase.INTELLIGENCE,
                "drafting": Phase.DRAFTING,
                "redteam": Phase.REDTEAM,
                "qa": Phase.QA,
                "delivery": Phase.DELIVERY,
                "deployment": Phase.DEPLOYMENT,
            }
            phases = [phase_map[p] for p in args.phase]

        # 运行工作流
        import asyncio
        config = config_manager.config
        context = WorkflowContext(
            project_dir=project_dir,
            config=config_manager,
            user_input={
                "name": config.name or project_dir.name,
                "description": config.description,
                "platform": config.platform,
                "frontend": config.frontend,
                "backend": config.backend,
                "domain": config.domain,
                "language_preferences": config.language_preferences,
                "quality_threshold": args.quality_gate,
            },
        )
        engine = WorkflowEngine(project_dir)
        results = asyncio.run(engine.run(phases=phases, context=context))

        # 检查是否全部成功
        all_success = bool(results) and all(r.success and not r.errors for r in results.values())

        return 0 if all_success else 1

    def _cmd_review(self, args) -> int:
        """查看或更新评审状态"""
        review_specs = {
            "docs": {
                "title": "三文档确认状态",
                "load": load_docs_confirmation,
                "save": save_docs_confirmation,
                "file": docs_confirmation_file,
                "type": "docs",
            },
            "ui": {
                "title": "UI 改版状态",
                "load": load_ui_revision,
                "save": save_ui_revision,
                "file": ui_revision_file,
                "type": "ui",
            },
            "architecture": {
                "title": "架构返工状态",
                "load": load_architecture_revision,
                "save": save_architecture_revision,
                "file": architecture_revision_file,
                "type": "architecture",
            },
            "quality": {
                "title": "质量返工状态",
                "load": load_quality_revision,
                "save": save_quality_revision,
                "file": quality_revision_file,
                "type": "quality",
            },
        }
        if args.review_command not in review_specs:
            self.console.print(
                "[yellow]请指定 review 子命令，例如 `super-dev review docs`、`super-dev review ui`、`super-dev review architecture` 或 `super-dev review quality`[/yellow]"
            )
            return 1

        project_dir = Path.cwd()
        spec = review_specs[args.review_command]
        review_type = str(spec["type"])
        current = cast(Callable[[Path], dict[str, Any] | None], spec["load"])(project_dir) or {}
        state_file = cast(Callable[[Path], Path], spec["file"])(project_dir)
        title = str(spec["title"])

        if not args.status:
            payload = {
                "status": str(current.get("status", "")).strip() or "pending_review",
                "comment": str(current.get("comment", "")).strip(),
                "actor": str(current.get("actor", "")).strip(),
                "run_id": str(current.get("run_id", "")).strip(),
                "updated_at": str(current.get("updated_at", "")).strip(),
                "exists": bool(current),
                "file_path": str(state_file),
            }
            if args.json:
                self.console.print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                self.console.print(f"[cyan]{title}[/cyan]")
                self.console.print(f"  状态: {self._review_status_label(payload['status'], review_type=review_type)}")
                self.console.print(f"  备注: {payload['comment'] or '-'}")
                self.console.print(f"  操作者: {payload['actor'] or '-'}")
                self.console.print(f"  关联 Run: {payload['run_id'] or '-'}")
                self.console.print(f"  更新时间: {payload['updated_at'] or '-'}")
                self.console.print(f"  文件: {payload['file_path']}")
            return 0

        save_fn = cast(Callable[[Path, dict[str, Any]], Path], spec["save"])
        load_fn = cast(Callable[[Path], dict[str, Any] | None], spec["load"])
        file_path = save_fn(
            project_dir,
            {
                "status": args.status,
                "comment": args.comment.strip(),
                "actor": args.actor.strip() or "user",
                "run_id": args.run_id.strip(),
            },
        )
        payload = load_fn(project_dir) or {}
        if args.json:
            self.console.print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            if review_type == "ui":
                action = "已确认 UI 改版通过" if args.status == "confirmed" else ("已记录 UI 改版请求" if args.status == "revision_requested" else "已重置为待确认")
            elif review_type == "architecture":
                action = "已确认架构返工通过" if args.status == "confirmed" else ("已记录架构返工请求" if args.status == "revision_requested" else "已重置为待确认")
            elif review_type == "quality":
                action = "已确认质量返工通过" if args.status == "confirmed" else ("已记录质量返工请求" if args.status == "revision_requested" else "已重置为待确认")
            else:
                action = "已确认三文档" if args.status == "confirmed" else ("已记录文档修改要求" if args.status == "revision_requested" else "已重置为待确认")
            self.console.print(f"[green]✓[/green] {action}")
            self.console.print(f"  状态: {self._review_status_label(args.status, review_type=review_type)}")
            self.console.print(f"  备注: {payload.get('comment', '') or '-'}")
            self.console.print(f"  操作者: {payload.get('actor', '') or '-'}")
            self.console.print(f"  关联 Run: {payload.get('run_id', '') or '-'}")
            self.console.print(f"  文件: {file_path}")
            if review_type == "ui" and args.status == "revision_requested":
                self.console.print("[dim]下一步: 先更新 output/*-uiux.md，再重做前端，并重新执行 frontend runtime 与 UI review[/dim]")
            elif review_type == "architecture" and args.status == "revision_requested":
                self.console.print("[dim]下一步: 先更新 output/*-architecture.md，再调整技术方案与实现，并重新通过相关质量门禁[/dim]")
            elif review_type == "quality" and args.status == "revision_requested":
                self.console.print("[dim]下一步: 先修复质量/安全问题，重新执行 quality gate 与 release proof-pack，再继续后续动作[/dim]")
        return 0

    def _cmd_release(self, args) -> int:
        """发布就绪度检查"""
        if args.release_command == "proof-pack":
            project_dir = Path.cwd()
            builder = ProofPackBuilder(project_dir)
            report = builder.build(verify_tests=bool(args.verify_tests))
            files = builder.write(report)
            payload = report.to_dict()
            payload["report_file"] = str(files["markdown"])
            payload["json_file"] = str(files["json"])
            payload["summary_file"] = str(files["summary"])

            if args.json:
                self.console.print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 0 if report.status == "ready" else 1

            status = "[green]ready[/green]" if report.status == "ready" else "[yellow]incomplete[/yellow]"
            self.console.print(f"[cyan]Proof Pack[/cyan] {status} 证据就绪: {report.ready_count}/{report.total_count}")
            self.console.print(f"  [green]✓[/green] Markdown: {files['markdown']}")
            self.console.print(f"  [green]✓[/green] JSON: {files['json']}")
            self.console.print(f"  [green]✓[/green] Summary: {files['summary']}")
            self.console.print(f"  [dim]{report.executive_summary}[/dim]")
            if report.blockers:
                self.console.print("  [yellow]待补齐项:[/yellow]")
                for artifact in report.blockers[:8]:
                    self.console.print(f"    - {artifact.name}: {artifact.summary}")
                self.console.print("  [cyan]推荐动作:[/cyan]")
                for action in report.next_actions[:5]:
                    self.console.print(f"    - {action}")
            else:
                self.console.print("  [green]所有关键交付证据均已就绪。[/green]")
            return 0 if report.status == "ready" else 1

        if args.release_command != "readiness":
            self.console.print("[yellow]请指定 release 子命令，例如 `super-dev release readiness` 或 `super-dev release proof-pack`[/yellow]")
            return 1

        project_dir = Path.cwd()
        evaluator = ReleaseReadinessEvaluator(project_dir)
        report = evaluator.evaluate(verify_tests=bool(args.verify_tests))
        files = evaluator.write(report)
        payload = report.to_dict()
        payload["report_file"] = str(files["markdown"])
        payload["json_file"] = str(files["json"])

        if args.json:
            self.console.print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if report.passed else 1

        status = "[green]通过[/green]" if report.passed else "[yellow]未完成[/yellow]"
        self.console.print(f"[cyan]发布就绪度[/cyan] {status} 分数: {report.score}/100")
        self.console.print(f"  [green]✓[/green] Markdown: {files['markdown']}")
        self.console.print(f"  [green]✓[/green] JSON: {files['json']}")

        if report.failed_checks:
            self.console.print("  [yellow]待收尾项:[/yellow]")
            for check in report.failed_checks[:8]:
                recommendation = f" | 建议: {check.recommendation}" if check.recommendation else ""
                self.console.print(f"    - {check.name}: {check.detail}{recommendation}")
        else:
            self.console.print("  [green]所有关键发布项均已满足。[/green]")

        return 0 if report.passed else 1

    def _cmd_studio(self, args) -> int:
        """启动交互工作台 API"""
        try:
            import uvicorn
        except ImportError:
            self.console.print("[red]缺少依赖: uvicorn[/red]")
            self.console.print("[dim]请安装: pip install fastapi uvicorn[/dim]")
            return 1

        self.console.print(f"[cyan]启动 Super Dev Studio: http://{args.host}:{args.port}[/cyan]")
        uvicorn.run(
            "super_dev.web.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )
        return 0

    def _cmd_expert(self, args) -> int:
        """调用专家"""
        from .experts import has_expert, list_experts, save_expert_advice

        # 处理 --list 选项
        if args.list:
            self.console.print("[cyan]可用专家列表:[/cyan]")
            for expert in list_experts():
                self.console.print(f"  [green]{expert['id']:<10}[/green] {expert['name']} - {expert['description']}")
            return 0

        # 如果没有提供专家名称，显示帮助
        if not args.expert_name:
            self.console.print("[yellow]请提供专家名称或使用 --list 查看可用专家[/yellow]")
            return 1

        prompt = " ".join(args.prompt) if args.prompt else ""
        self.console.print(f"[cyan]调用专家: {args.expert_name}[/cyan]")
        self.console.print(f"[dim]提示词: {prompt or '(无)'}[/dim]")
        if not has_expert(args.expert_name):
            self.console.print(f"[red]未知专家: {args.expert_name}[/red]")
            return 1

        report_file, _ = save_expert_advice(
            project_dir=Path.cwd(),
            expert_id=args.expert_name,
            prompt=prompt,
        )
        self.console.print(f"[green]✓[/green] 专家建议已生成: {report_file}")
        return 0

    def _cmd_quality(self, args) -> int:
        """质量检查"""
        from .reviewers import QualityGateChecker, UIReviewReviewer

        project_dir = Path.cwd()
        output_dir = project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        config_manager = ConfigManager(project_dir)
        config = config_manager.load()

        project_name = self._sanitize_project_name(config.name or project_dir.name)
        tech_stack = {
            "platform": config.platform,
            "frontend": self._normalize_pipeline_frontend(config.frontend),
            "backend": config.backend,
            "domain": config.domain,
        }

        self.console.print(f"[cyan]运行质量检查: {args.type}[/cyan]")

        if args.type == "ui-review":
            reviewer = UIReviewReviewer(
                project_dir=project_dir,
                name=project_name,
                tech_stack=tech_stack,
            )
            report = reviewer.review()
            review_file = output_dir / f"{project_name}-ui-review.md"
            review_json_file = output_dir / f"{project_name}-ui-review.json"
            review_file.write_text(report.to_markdown(), encoding="utf-8")
            review_json_file.write_text(
                json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            status = "[green]通过[/green]" if report.passed else "[yellow]需修正[/yellow]"
            self.console.print(f"  {status} 总分: {report.score}/100")
            self.console.print(f"  [green]✓[/green] 报告: {review_file}")
            self.console.print(f"  [green]✓[/green] JSON: {review_json_file}")
            if report.findings:
                self.console.print("[yellow]主要问题:[/yellow]")
                for finding in report.findings[:5]:
                    self.console.print(f"  - [{finding.level}] {finding.title}")
            return 0 if report.passed else 1

        # 轻量文档检查
        if args.type in {"prd", "architecture", "ui", "ux"}:
            pattern_map = {
                "prd": "*-prd.md",
                "architecture": "*-architecture.md",
                "ui": "*-uiux.md",
                "ux": "*-uiux.md",
            }
            expected_pattern = pattern_map[args.type]
            matched = sorted(output_dir.glob(expected_pattern))
            if matched:
                self.console.print(f"[green]✓[/green] 检测到 {len(matched)} 个文档: {expected_pattern}")
                for file_path in matched[:5]:
                    self.console.print(f"  - {file_path}")
                return 0

            self.console.print(f"[red]未找到文档: output/{expected_pattern}[/red]")
            return 1

        # 代码或全量检查走质量门禁评估
        gate_checker = QualityGateChecker(
            project_dir=project_dir,
            name=project_name,
            tech_stack=tech_stack,
            host_compatibility_min_score_override=config.host_compatibility_min_score,
            host_compatibility_min_ready_hosts_override=config.host_compatibility_min_ready_hosts,
        )
        gate_result = gate_checker.check(redteam_report=None)

        gate_file = output_dir / f"{project_name}-quality-gate.md"
        gate_file.write_text(gate_result.to_markdown(), encoding="utf-8")
        if gate_checker.latest_ui_review_report is not None:
            ui_review_file = output_dir / f"{project_name}-ui-review.md"
            ui_review_json_file = output_dir / f"{project_name}-ui-review.json"
            ui_review_file.write_text(
                gate_checker.latest_ui_review_report.to_markdown(),
                encoding="utf-8",
            )
            ui_review_json_file.write_text(
                json.dumps(
                    gate_checker.latest_ui_review_report.to_dict(),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        scenario_label = "0-1 新建项目" if gate_result.scenario == "0-1" else "1-N+1 增量开发"
        status = "[green]通过[/green]" if gate_result.passed else "[red]未通过[/red]"

        self.console.print(f"  [dim]场景: {scenario_label}[/dim]")
        self.console.print(f"  {status} 总分: {gate_result.total_score}/100")
        self.console.print(f"  [green]✓[/green] 报告: {gate_file}")
        if gate_checker.latest_ui_review_report is not None:
            self.console.print(
                f"  [green]✓[/green] UI 审查: {output_dir / f'{project_name}-ui-review.md'}"
            )
            self.console.print(
                f"  [green]✓[/green] UI 审查 JSON: {output_dir / f'{project_name}-ui-review.json'}"
            )

        if not gate_result.passed and gate_result.critical_failures:
            self.console.print("[yellow]关键失败项:[/yellow]")
            for failure in gate_result.critical_failures:
                self.console.print(f"  - {failure}")

        return 0 if gate_result.passed else 1

    def _cmd_metrics(self, args) -> int:
        """查看最近一次流水线指标"""
        output_dir = Path.cwd() / "output"
        if not output_dir.exists():
            self.console.print("[yellow]未找到 output 目录，请先执行流水线[/yellow]")
            return 1

        if args.history:
            limit = max(1, int(args.limit))
            history_dir = output_dir / "metrics-history"
            candidates: list[Path] = []
            if history_dir.exists():
                candidates.extend(history_dir.glob("*-pipeline-metrics-*.json"))
            if not candidates:
                candidates.extend(output_dir.glob("*-pipeline-metrics.json"))
            if args.project:
                prefix = f"{self._sanitize_project_name(args.project)}-pipeline-metrics"
                candidates = [item for item in candidates if item.name.startswith(prefix)]
            candidates = sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
            if not candidates:
                self.console.print("[yellow]未找到 pipeline 历史指标文件[/yellow]")
                return 1

            items: list[dict[str, Any]] = []
            for file_path in candidates:
                try:
                    payload = json.loads(file_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                items.append(
                    {
                        "file": file_path.name,
                        "project": payload.get("project_name", ""),
                        "success": bool(payload.get("success", False)),
                        "success_rate": float(payload.get("success_rate", 0)),
                        "duration": float(payload.get("total_duration_seconds", 0)),
                        "started_at": str(payload.get("started_at", "")),
                    }
                )

            if not items:
                self.console.print("[yellow]指标文件存在但无法解析[/yellow]")
                return 1

            run_count = len(items)
            success_count = sum(1 for item in items if item["success"])
            avg_duration = sum(item["duration"] for item in items) / run_count
            avg_success_rate = sum(item["success_rate"] for item in items) / run_count
            self.console.print("[cyan]Pipeline 历史趋势[/cyan]")
            self.console.print(f"  记录数: {run_count}")
            self.console.print(f"  成功次数: {success_count}/{run_count}")
            self.console.print(f"  平均成功率: {avg_success_rate:.1f}%")
            self.console.print(f"  平均耗时: {avg_duration:.2f}s")
            self.console.print("  最近记录:")
            for item in items:
                marker = "✓" if item["success"] else "✗"
                started_at = item["started_at"] or "-"
                self.console.print(
                    f"    {marker} {item['file']} | {item['project']} | "
                    f"success_rate={item['success_rate']:.1f}% | duration={item['duration']:.2f}s | start={started_at}"
                )
            return 0

        if args.project:
            metrics_file = output_dir / f"{self._sanitize_project_name(args.project)}-pipeline-metrics.json"
            if not metrics_file.exists():
                self.console.print(f"[red]未找到指标文件: {metrics_file.name}[/red]")
                return 1
        else:
            candidates = sorted(
                output_dir.glob("*-pipeline-metrics.json"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if not candidates:
                self.console.print("[yellow]未找到 pipeline 指标文件，请先运行 super-dev \"需求\"[/yellow]")
                return 1
            metrics_file = candidates[0]

        try:
            payload = json.loads(metrics_file.read_text(encoding="utf-8"))
        except Exception:
            self.console.print(f"[red]指标文件解析失败: {metrics_file.name}[/red]")
            return 1
        self.console.print(f"[cyan]Pipeline 指标: {metrics_file.name}[/cyan]")
        self.console.print(f"  项目: {payload.get('project_name', '')}")
        self.console.print(f"  成功: {payload.get('success', False)}")
        self.console.print(f"  成功率: {payload.get('success_rate', 0)}%")
        self.console.print(f"  总耗时: {payload.get('total_duration_seconds', 0)}s")
        if payload.get("started_at"):
            self.console.print(f"  开始时间(UTC): {payload.get('started_at')}")
        if payload.get("finished_at"):
            self.console.print(f"  结束时间(UTC): {payload.get('finished_at')}")
        self.console.print(f"  阶段数: {len(payload.get('stages', []))}")
        if payload.get("failure_reason"):
            self.console.print(f"  失败原因: {payload['failure_reason']}")
        self.console.print(f"  文件: {metrics_file}")
        return 0

    # 阶段编号映射表
    STAGE_NUMBER_MAP: dict[str, str] = {
        "1": "research",
        "2": "prd",
        "3": "architecture",
        "4": "uiux",
        "5": "spec",
        "6": "frontend",
        "7": "backend",
        "8": "quality",
        "9": "delivery",
    }

    STAGE_LABELS: dict[str, str] = {
        "research": "同类产品研究",
        "prd": "产品需求文档",
        "architecture": "架构设计",
        "uiux": "UI/UX 设计",
        "spec": "规范与任务分解",
        "frontend": "前端开发",
        "backend": "后端开发",
        "quality": "质量检查",
        "delivery": "交付打包",
    }

    # 每个环节对应的专家角色和职责
    STAGE_EXPERTS: dict[str, dict[str, str]] = {
        "research": {"role": "PM + ARCHITECT", "title": "产品经理 + 架构师", "duty": "需求解析、知识库增强、同类产品研究"},
        "prd": {"role": "PM", "title": "产品经理", "duty": "需求分析、PRD 编写、用户故事、验收标准"},
        "architecture": {"role": "ARCHITECT", "title": "架构师", "duty": "系统设计、技术选型、API 设计、数据库建模"},
        "uiux": {"role": "UI + UX", "title": "UI/UX 设计师", "duty": "视觉设计、设计系统、组件规范、交互设计"},
        "spec": {"role": "PM + CODE", "title": "产品经理 + 代码专家", "duty": "需求拆解、任务分解、优先级排序"},
        "frontend": {"role": "CODE + UI", "title": "代码专家 + UI 设计师", "duty": "前端实现、组件开发、页面搭建"},
        "backend": {"role": "CODE + DBA", "title": "代码专家 + 数据库专家", "duty": "后端实现、API 开发、数据库迁移"},
        "quality": {"role": "QA + SECURITY", "title": "QA 专家 + 安全专家", "duty": "质量门禁、红队审查、测试验证"},
        "delivery": {"role": "DEVOPS + QA", "title": "DevOps + QA 专家", "duty": "CI/CD 配置、发布演练、交付打包"},
    }

    def _cmd_run(self, args) -> int:
        """跳转到任意环节执行/重做（支持名称或数字 1-9）"""
        if getattr(args, "status", False):
            return self._cmd_run_status(args)

        if getattr(args, "resume", False):
            return self._cmd_run_resume(args)

        confirm_phase = str(getattr(args, "confirm_phase", "") or "").strip()
        if confirm_phase:
            return self._cmd_run_confirm_phase(
                phase_name=confirm_phase,
                comment=str(getattr(args, "comment", "") or ""),
                actor=str(getattr(args, "actor", "") or "cli-user"),
            )
        jump_stage = str(getattr(args, "jump", "") or "").strip()
        if jump_stage:
            return self._cmd_run_from_stage(stage_selector=jump_stage, show_impact=True)
        phase_stage = str(getattr(args, "phase", "") or "").strip()
        if phase_stage:
            return self._cmd_run_from_stage(stage_selector=phase_stage, show_impact=False)

        stage_selector = str(getattr(args, "stage_selector", "") or "").strip()

        # 数字映射：super-dev run 1 → research, super-dev run 4 → uiux
        if stage_selector in self.STAGE_NUMBER_MAP:
            stage_selector = self.STAGE_NUMBER_MAP[stage_selector]

        if stage_selector:
            normalized = stage_selector.lower()
            label = self.STAGE_LABELS.get(normalized, normalized)

            # 专家角色映射
            expert_map = {
                "research": ("PM + ARCHITECT", "产品经理 + 架构师"),
                "prd": ("PM", "产品经理"),
                "architecture": ("ARCHITECT", "架构师"),
                "uiux": ("UI + UX", "UI/UX 设计师"),
                "spec": ("PM + CODE", "产品经理 + 代码专家"),
                "frontend": ("CODE + UI", "代码专家 + UI 设计师"),
                "backend": ("CODE + DBA", "代码专家 + 数据库专家"),
                "quality": ("QA + SECURITY", "QA 专家 + 安全专家"),
                "delivery": ("DEVOPS + QA", "DevOps + QA 专家"),
            }
            expert_role, expert_title = expert_map.get(normalized, ("CODE", "代码专家"))

            from rich.panel import Panel
            self.console.print("")
            self.console.print(Panel(
                f"[bold cyan]Super Dev Run[/bold cyan]\n\n"
                f"  [dim]环节[/dim]    {normalized} ({label})\n"
                f"  [dim]专家[/dim]    [bold]{expert_role}[/bold] - {expert_title}",
                border_style="cyan",
                expand=True,
                padding=(1, 2),
            ))
            self.console.print("")

            if normalized in {"research", "prd", "architecture", "uiux"}:
                return self._cmd_run_targeted_refresh(normalized)
            return self._cmd_run_from_stage(stage_selector=normalized, show_impact=False)

        # 没有指定阶段，显示环节菜单
        from rich.panel import Panel
        from rich.table import Table
        self.console.print("")
        table = Table(title="可用环节", expand=True, border_style="dim", title_style="bold cyan")
        table.add_column("编号", style="bold cyan", width=6, justify="center")
        table.add_column("专家", style="bold", min_width=16)
        table.add_column("环节", style="bold")
        table.add_column("说明", style="dim")

        expert_short = {
            "research": "PM + ARCHITECT",
            "prd": "PM",
            "architecture": "ARCHITECT",
            "uiux": "UI + UX",
            "spec": "PM + CODE",
            "frontend": "CODE + UI",
            "backend": "CODE + DBA",
            "quality": "QA + SECURITY",
            "delivery": "DEVOPS + QA",
        }
        for num, name in sorted(self.STAGE_NUMBER_MAP.items()):
            table.add_row(num, expert_short.get(name, ""), name, self.STAGE_LABELS.get(name, ""))
        self.console.print(table)
        self.console.print("")
        self.console.print("[cyan]用法示例:[/cyan]")
        self.console.print("  super-dev run 4          UI/UX 设计师重新生成设计文档")
        self.console.print("  super-dev run uiux       同上")
        self.console.print("  super-dev run --resume   从上次中断处继续")
        self.console.print("  super-dev run --status   查看流程状态")
        self.console.print("")
        return 0

    def _cmd_status(self, args) -> int:
        """快捷别名：查看当前流程状态"""
        return self._cmd_run_status(args)

    def _cmd_jump(self, args) -> int:
        """快捷别名：跳转到指定阶段"""
        stage = str(getattr(args, "stage", "") or "").strip()
        if not stage:
            self.console.print("[red]请指定目标阶段，例如: super-dev jump frontend[/red]")
            return 1
        return self._cmd_run_from_stage(stage_selector=stage, show_impact=True)

    def _cmd_confirm(self, args) -> int:
        """快捷别名：确认指定阶段"""
        phase_name = str(getattr(args, "phase", "") or "").strip()
        if not phase_name:
            self.console.print("[red]请指定要确认的阶段，例如: super-dev confirm docs[/red]")
            return 1
        return self._cmd_run_confirm_phase(
            phase_name=phase_name,
            comment=str(getattr(args, "comment", "") or ""),
            actor=str(getattr(args, "actor", "") or "cli-user"),
        )

    def _cmd_run_resume(self, args) -> int:
        """恢复最近一次 pipeline 运行"""

        project_dir = Path.cwd()
        run_state = self._read_pipeline_run_state(project_dir)
        if not run_state:
            self.console.print("[red]未找到最近一次 pipeline 运行记录[/red]")
            self.console.print("[dim]请先执行 super-dev \"需求\" 或 super-dev pipeline \"需求\"[/dim]")
            return 1

        status = str(run_state.get("status", "")).strip().lower()
        if status == "success":
            self.console.print("[yellow]最近一次 pipeline 已成功完成，无需恢复[/yellow]")
            return 1
        if status == "waiting_confirmation":
            if not self._docs_confirmation_is_confirmed(project_dir):
                self.console.print("[yellow]最近一次 pipeline 已停在文档确认门，请先确认三文档后再恢复[/yellow]")
                self.console.print("[dim]可执行: super-dev review docs --status confirmed --comment \"三文档已确认\"[/dim]")
                return 1
            if not self._ui_revision_is_clear(project_dir):
                self.console.print("[yellow]最近一次 pipeline 存在待处理 UI 改版请求，请先完成 UI 返工再恢复[/yellow]")
                self.console.print("[dim]可执行: super-dev review ui --status confirmed --comment \"UI 改版已通过\"[/dim]")
                return 1
            if not self._architecture_revision_is_clear(project_dir):
                self.console.print("[yellow]最近一次 pipeline 存在待处理架构返工请求，请先完成架构修订再恢复[/yellow]")
                self.console.print("[dim]可执行: super-dev review architecture --status confirmed --comment \"架构返工已通过\"[/dim]")
                return 1
            if not self._quality_revision_is_clear(project_dir):
                self.console.print("[yellow]最近一次 pipeline 存在待处理质量返工请求，请先完成质量整改再恢复[/yellow]")
                self.console.print("[dim]可执行: super-dev review quality --status confirmed --comment \"质量返工已通过\"[/dim]")
                return 1
        elif status == "waiting_ui_revision":
            if not self._ui_revision_is_clear(project_dir):
                self.console.print("[yellow]最近一次 pipeline 已停在 UI 改版门，请先完成 UIUX 更新、前端返工与 UI review[/yellow]")
                self.console.print("[dim]可执行: super-dev review ui --status confirmed --comment \"UI 改版已通过\"[/dim]")
                return 1
        elif status == "waiting_architecture_revision":
            if not self._architecture_revision_is_clear(project_dir):
                self.console.print("[yellow]最近一次 pipeline 已停在架构返工门，请先完成 output/*-architecture.md 修订和实现同步[/yellow]")
                self.console.print("[dim]可执行: super-dev review architecture --status confirmed --comment \"架构返工已通过\"[/dim]")
                return 1
        elif status == "waiting_quality_revision":
            if not self._quality_revision_is_clear(project_dir):
                self.console.print("[yellow]最近一次 pipeline 已停在质量返工门，请先完成质量整改并重新执行 quality gate[/yellow]")
                self.console.print("[dim]可执行: super-dev review quality --status confirmed --comment \"质量返工已通过\"[/dim]")
                return 1
        elif status not in {"failed", "running"}:
            self.console.print("[yellow]最近一次 pipeline 状态不支持恢复[/yellow]")
            return 1

        raw_args = run_state.get("pipeline_args", {})
        if not isinstance(raw_args, dict):
            self.console.print("[red]运行记录损坏：缺少 pipeline 参数[/red]")
            return 1

        pipeline_args = argparse.Namespace(
            description=str(raw_args.get("description", "")).strip(),
            platform=str(raw_args.get("platform", "web")),
            frontend=str(raw_args.get("frontend", "react")),
            backend=str(raw_args.get("backend", "node")),
            domain=str(raw_args.get("domain", "")),
            name=raw_args.get("name"),
            cicd=str(raw_args.get("cicd", "all")),
            skip_redteam=bool(raw_args.get("skip_redteam", False)),
            skip_scaffold=bool(raw_args.get("skip_scaffold", False)),
            skip_quality_gate=bool(raw_args.get("skip_quality_gate", False)),
            skip_rehearsal_verify=bool(raw_args.get("skip_rehearsal_verify", False)),
            offline=bool(raw_args.get("offline", False)),
            quality_threshold=raw_args.get("quality_threshold"),
            resume=True,
        )

        if not pipeline_args.description:
            self.console.print("[red]运行记录缺少 description，无法恢复[/red]")
            return 1

        if status == "running":
            self.console.print("[yellow]检测到最近一次运行状态为 running，按中断恢复处理[/yellow]")
        self.console.print("[cyan]恢复最近一次失败/中断的 pipeline 运行...[/cyan]")
        self.console.print(f"[dim]需求: {pipeline_args.description}[/dim]")
        return self._cmd_pipeline(pipeline_args)

    def _cmd_run_status(self, args) -> int:
        project_dir = Path.cwd()
        run_state = self._read_pipeline_run_state(project_dir) or {}
        docs_state = self._get_docs_confirmation_state(project_dir)
        ui_state = self._get_ui_revision_state(project_dir)
        architecture_state = self._get_architecture_revision_state(project_dir)
        quality_state = self._get_quality_revision_state(project_dir)
        phase_confirmations = {}
        if isinstance(run_state.get("phase_confirmations"), dict):
            phase_confirmations = dict(run_state.get("phase_confirmations") or {})
        payload = {
            "run_state_exists": bool(run_state),
            "status": str(run_state.get("status", "")).strip() or "unknown",
            "description": str((run_state.get("pipeline_args") or {}).get("description", "")).strip(),
            "failed_stage": str(run_state.get("failed_stage", "")).strip(),
            "resume_from_stage": str(run_state.get("resume_from_stage", "")).strip(),
            "docs_confirmation": docs_state,
            "ui_revision": ui_state,
            "architecture_revision": architecture_state,
            "quality_revision": quality_state,
            "phase_confirmations": phase_confirmations,
            "recommended_next": self._run_status_recommendation(
                run_state=run_state,
                docs_state=docs_state,
                ui_state=ui_state,
                architecture_state=architecture_state,
                quality_state=quality_state,
            ),
        }
        if getattr(args, "json", False):
            self.console.print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        self.console.print("[cyan]Super Dev 流程状态[/cyan]")
        self.console.print(f"  运行状态: {payload['status']}")
        self.console.print(f"  当前需求: {payload['description'] or '-'}")
        self.console.print(f"  失败阶段: {payload['failed_stage'] or '-'}")
        self.console.print(f"  恢复起点: {payload['resume_from_stage'] or '-'}")
        self.console.print(f"  文档确认: {self._docs_confirmation_label(docs_state['status'])}")
        self.console.print(f"  UI 改版: {self._review_status_label(ui_state['status'], review_type='ui')}")
        self.console.print(
            f"  架构返工: {self._review_status_label(architecture_state['status'], review_type='architecture')}"
        )
        self.console.print(
            f"  质量返工: {self._review_status_label(quality_state['status'], review_type='quality')}"
        )
        if phase_confirmations:
            self.console.print("  阶段确认:")
            for phase, item in sorted(phase_confirmations.items()):
                status = str((item or {}).get("status", "")).strip() or "pending_review"
                actor = str((item or {}).get("actor", "")).strip() or "-"
                self.console.print(f"    - {phase}: {self._review_status_label(status)} | {actor}")
        self.console.print(f"  下一步: {payload['recommended_next']}")
        return 0

    def _cmd_run_confirm_phase(self, *, phase_name: str, comment: str, actor: str) -> int:
        project_dir = Path.cwd()
        normalized = phase_name.strip().lower()
        if normalized in {"docs", "document", "documents"}:
            path = save_docs_confirmation(
                project_dir,
                {
                    "status": "confirmed",
                    "comment": comment or "三文档确认通过",
                    "actor": actor,
                    "run_id": "",
                },
            )
            self.console.print(f"[green]✓[/green] 已确认 docs 阶段: {path}")
            return 0
        if normalized in {"ui", "frontend-ui"}:
            path = save_ui_revision(
                project_dir,
                {
                    "status": "confirmed",
                    "comment": comment or "UI 阶段确认通过",
                    "actor": actor,
                    "run_id": "",
                },
            )
            self.console.print(f"[green]✓[/green] 已确认 ui 阶段: {path}")
            return 0
        if normalized in {"architecture", "arch"}:
            path = save_architecture_revision(
                project_dir,
                {
                    "status": "confirmed",
                    "comment": comment or "架构阶段确认通过",
                    "actor": actor,
                    "run_id": "",
                },
            )
            self.console.print(f"[green]✓[/green] 已确认 architecture 阶段: {path}")
            return 0
        if normalized in {"quality", "qa"}:
            path = save_quality_revision(
                project_dir,
                {
                    "status": "confirmed",
                    "comment": comment or "质量阶段确认通过",
                    "actor": actor,
                    "run_id": "",
                },
            )
            self.console.print(f"[green]✓[/green] 已确认 quality 阶段: {path}")
            return 0
        run_state = self._read_pipeline_run_state(project_dir) or {}
        phase_confirmations = run_state.get("phase_confirmations")
        if not isinstance(phase_confirmations, dict):
            phase_confirmations = {}
        phase_confirmations[normalized] = {
            "status": "confirmed",
            "comment": comment or f"{normalized} 阶段确认通过",
            "actor": actor,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        run_state["phase_confirmations"] = phase_confirmations
        run_state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_pipeline_run_state(project_dir, run_state)
        self.console.print(f"[green]✓[/green] 已确认阶段: {normalized}")
        return 0

    def _cmd_run_targeted_refresh(self, target: str) -> int:
        project_dir = Path.cwd()
        config = get_config_manager(project_dir).config
        project_name = self._sanitize_project_name(config.name or project_dir.name)
        output_dir = project_dir / str(config.output_dir or "output")
        output_dir.mkdir(parents=True, exist_ok=True)
        run_state = self._read_pipeline_run_state(project_dir) or {}
        pipeline_args = run_state.get("pipeline_args") if isinstance(run_state, dict) else {}
        if not isinstance(pipeline_args, dict):
            pipeline_args = {}
        description = (
            str(pipeline_args.get("description", "")).strip()
            or str(config.description or "").strip()
            or project_name
        )
        domain = str(pipeline_args.get("domain", "")).strip() or str(config.domain or "")
        frontend = str(pipeline_args.get("frontend", "")).strip() or self._normalize_pipeline_frontend(config.frontend)
        backend = str(pipeline_args.get("backend", "")).strip() or str(config.backend or "node")
        request_mode = str((run_state.get("context") or {}).get("request_mode", "")).strip() or "feature"

        if target == "research":
            import os

            from .orchestrator.knowledge import KnowledgeAugmenter

            disable_web = os.getenv("SUPER_DEV_DISABLE_WEB", "").strip().lower() in {"1", "true", "yes"}
            augmenter = KnowledgeAugmenter(
                project_dir=project_dir,
                web_enabled=not disable_web,
                allowed_web_domains=config.knowledge_allowed_domains,
                cache_ttl_seconds=config.knowledge_cache_ttl_seconds,
            )
            bundle = augmenter.augment(requirement=description, domain=domain)
            research_file = output_dir / f"{project_name}-research.md"
            research_file.write_text(augmenter.to_markdown(bundle), encoding="utf-8")
            cache_file = augmenter.save_bundle(
                bundle=bundle,
                output_dir=output_dir,
                project_name=project_name,
                requirement=description,
                domain=domain,
            )
            self.console.print(f"[green]✓[/green] 已重跑 research: {research_file}")
            self.console.print(f"[green]✓[/green] 知识缓存: {cache_file}")
            return 0

        from .creators import DocumentGenerator

        knowledge_summary = {}
        bundle_path = output_dir / "knowledge-cache" / f"{project_name}-knowledge-bundle.json"
        if bundle_path.exists():
            try:
                knowledge_payload = json.loads(bundle_path.read_text(encoding="utf-8"))
                if isinstance(knowledge_payload, dict):
                    knowledge_summary = dict(knowledge_payload.get("research_summary") or {})
                    enriched = str(knowledge_payload.get("enriched_requirement", "")).strip()
                    if enriched:
                        description = enriched
            except Exception:
                pass

        generator = DocumentGenerator(
            name=project_name,
            description=description,
            request_mode=request_mode,
            platform=str(config.platform or "web"),
            frontend=frontend,
            backend=backend,
            domain=domain,
            ui_library=config.ui_library,
            style_solution=config.style_solution,
            state_management=list(config.state_management or []),
            testing_frameworks=list(config.testing_frameworks or []),
            language_preferences=list(config.language_preferences or []),
            knowledge_summary=knowledge_summary,
        )

        target_map = {
            "prd": (
                output_dir / f"{project_name}-prd.md",
                generator.generate_prd,
            ),
            "architecture": (
                output_dir / f"{project_name}-architecture.md",
                generator.generate_architecture,
            ),
            "uiux": (
                output_dir / f"{project_name}-uiux.md",
                generator.generate_uiux,
            ),
        }
        file_path, factory = target_map[target]
        file_path.write_text(factory(), encoding="utf-8")
        self.console.print(f"[green]✓[/green] 已重跑 {target}: {file_path}")
        return 0

    def _cmd_run_from_stage(self, *, stage_selector: str, show_impact: bool) -> int:
        project_dir = Path.cwd()
        run_state = self._read_pipeline_run_state(project_dir)
        if not run_state:
            self.console.print("[red]未找到可恢复运行记录，无法按阶段继续[/red]")
            self.console.print("[dim]请先执行一次 super-dev \"需求\" 或 super-dev pipeline \"需求\"[/dim]")
            return 1
        stage_number = self._resolve_pipeline_stage_selector(stage_selector)
        if stage_number is None:
            self.console.print(f"[red]无法识别阶段: {stage_selector}[/red]")
            self.console.print(
                "[dim]可用阶段: research/docs/spec/frontend/backend/quality/delivery/rehearsal[/dim]"
            )
            return 1
        if show_impact:
            impact_lines = self._stage_jump_impact(stage_number)
            self.console.print(f"[cyan]阶段回跳影响分析（目标: {stage_selector} / 第 {stage_number} 阶段）[/cyan]")
            for line in impact_lines:
                self.console.print(f"  - {line}")
        run_state["status"] = "failed"
        run_state["failed_stage"] = str(stage_number)
        run_state["resume_from_stage"] = str(stage_number)
        run_state["next_stage"] = str(stage_number)
        run_state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_pipeline_run_state(project_dir, run_state)
        self.console.print(f"[cyan]将从第 {stage_number} 阶段继续执行...[/cyan]")
        return self._cmd_run_resume(argparse.Namespace(resume=True))

    def _run_status_recommendation(
        self,
        *,
        run_state: dict[str, Any],
        docs_state: dict[str, Any],
        ui_state: dict[str, Any],
        architecture_state: dict[str, Any],
        quality_state: dict[str, Any],
    ) -> str:
        if docs_state.get("status") != "confirmed":
            return 'super-dev review docs --status confirmed --comment "三文档已确认"'
        if ui_state.get("status") == "revision_requested":
            return 'super-dev review ui --status confirmed --comment "UI 改版已通过"'
        if architecture_state.get("status") == "revision_requested":
            return 'super-dev review architecture --status confirmed --comment "架构返工已通过"'
        if quality_state.get("status") == "revision_requested":
            return 'super-dev review quality --status confirmed --comment "质量返工已通过"'
        status = str(run_state.get("status", "")).strip().lower()
        if status in {"failed", "running", "waiting_confirmation", "waiting_ui_revision", "waiting_architecture_revision", "waiting_quality_revision"}:
            return "super-dev run --resume"
        return "super-dev run --phase frontend"

    def _resolve_pipeline_stage_selector(self, value: str) -> int | None:
        normalized = str(value).strip().lower()
        stage_map = {
            "research": 0,
            "discovery": 0,
            "docs": 1,
            "document": 1,
            "documents": 1,
            "prd": 1,
            "architecture": 1,
            "uiux": 1,
            "spec": 2,
            "frontend": 3,
            "ui": 3,
            "backend": 4,
            "implementation": 4,
            "redteam": 5,
            "quality": 6,
            "qa": 6,
            "review": 7,
            "prompt": 8,
            "cicd": 9,
            "deploy-fix": 10,
            "delivery": 11,
            "rehearsal": 12,
        }
        if normalized.isdigit():
            stage_number = int(normalized)
            if 0 <= stage_number <= 12:
                return stage_number
            return None
        return stage_map.get(normalized)

    def _stage_jump_impact(self, stage_number: int) -> list[str]:
        if stage_number <= 1:
            return [
                "将重做 research / PRD / Architecture / UIUX",
                "会使 Spec 与任务拆解重新计算",
                "后续实现与质量验证需要全量重跑",
            ]
        if stage_number == 2:
            return [
                "将重算 Spec 与 tasks",
                "前后端实现任务依赖会刷新",
                "建议在继续前确认三文档未变更",
            ]
        if stage_number == 3:
            return [
                "将重做前端骨架与预览验证",
                "可能触发 UI 改版门重新确认",
            ]
        if stage_number == 4:
            return [
                "将重做实现骨架与任务执行",
                "后续红队与质量门禁会重新执行",
            ]
        if stage_number >= 5:
            return [
                "将从质量/交付后段开始重跑",
                "不会重建前置文档与 spec，除非门禁判定需要回退",
            ]
        return ["将按目标阶段继续执行并自动校验前置门禁"]

    def _cmd_policy(self, args) -> int:
        """Policy DSL 管理"""
        from .policy import PipelinePolicyManager

        action = getattr(args, "action", "") or "show"
        manager = PipelinePolicyManager(Path.cwd())

        if action == "presets":
            self.console.print("[cyan]可用策略预设:[/cyan]")
            self.console.print("  - default: 默认策略（兼顾灵活性）")
            self.console.print("  - balanced: 团队协作增强（要求 host profile）")
            self.console.print("  - enterprise: 商业级强治理（required hosts + ready 校验）")
            return 0

        if action == "init":
            preset = str(getattr(args, "preset", "default") or "default")
            force = bool(getattr(args, "force", False))
            path = manager.ensure_exists(preset=preset, force=force)
            self.console.print(f"[green]✓[/green] 已生成策略文件: {path}")
            self.console.print(f"[dim]预设: {preset} | force={force}[/dim]")
            return 0

        policy = manager.load()
        self.console.print("[cyan]当前流水线策略:[/cyan]")
        self.console.print(json.dumps(policy.__dict__, ensure_ascii=False, indent=2))
        self.console.print(f"[dim]策略文件: {manager.policy_path}[/dim]")
        if not manager.policy_path.exists():
            self.console.print("[yellow]提示: 当前使用内置默认策略，执行 super-dev policy init 可写入文件[/yellow]")
        return 0

    def _cmd_preview(self, args) -> int:
        """生成原型"""
        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.console.print(f"[cyan]生成原型: {output_path}[/cyan]")
        if self._export_preview_from_output_frontend(output_path):
            self.console.print("[green]✓[/green] 已基于 output/frontend 生成可预览页面")
            return 0

        # 回退：生成文档概览预览页
        output_dir = Path.cwd() / "output"
        docs = sorted(output_dir.glob("*.md")) if output_dir.exists() else []
        rows = "\n".join(
            f"<li><a href=\"{doc.name}\" target=\"_blank\">{doc.name}</a></li>"
            for doc in docs[:20]
        ) or "<li>未找到可预览文档，请先在宿主会话触发 /super-dev，或运行 super-dev start / super-dev create 生成治理产物。</li>"

        fallback_html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Super Dev Preview</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; line-height: 1.6; }}
    h1 {{ margin-bottom: 8px; }}
    .hint {{ color: #555; margin-bottom: 16px; }}
    ul {{ padding-left: 18px; }}
  </style>
</head>
<body>
  <h1>Super Dev 预览页</h1>
  <p class="hint">未检测到宿主已实现的 output/frontend 前端骨架，以下为当前治理产物文档列表：</p>
  <ul>{rows}</ul>
</body>
</html>
"""
        output_path.write_text(fallback_html, encoding="utf-8")
        self.console.print("[yellow]未检测到 output/frontend，已生成文档概览预览页[/yellow]")
        return 0

    def _export_preview_from_output_frontend(self, output_path: Path) -> bool:
        import shutil

        frontend_dir = Path.cwd() / "output" / "frontend"
        index_file = frontend_dir / "index.html"
        css_file = frontend_dir / "styles.css"
        js_file = frontend_dir / "app.js"

        if not index_file.exists():
            return False

        html = index_file.read_text(encoding="utf-8")
        output_path.write_text(html, encoding="utf-8")

        if css_file.exists():
            shutil.copyfile(css_file, output_path.parent / "styles.css")
        if js_file.exists():
            shutil.copyfile(js_file, output_path.parent / "app.js")
        return True

    def _frontend_runtime_report_paths(self, output_dir: Path, project_name: str) -> dict[str, Path]:
        return {
            "markdown": output_dir / f"{project_name}-frontend-runtime.md",
            "json": output_dir / f"{project_name}-frontend-runtime.json",
        }

    def _load_frontend_runtime_validation(self, *, output_dir: Path, project_name: str) -> dict[str, Any]:
        report_file = self._frontend_runtime_report_paths(output_dir=output_dir, project_name=project_name)["json"]
        if not report_file.exists():
            return {"passed": False, "checks": {}, "preview_file": "", "report_file": str(report_file)}
        try:
            payload = json.loads(report_file.read_text(encoding="utf-8"))
        except Exception:
            return {"passed": False, "checks": {}, "preview_file": "", "report_file": str(report_file)}
        if not isinstance(payload, dict):
            return {"passed": False, "checks": {}, "preview_file": "", "report_file": str(report_file)}
        payload["report_file"] = str(report_file)
        return payload

    def _write_frontend_runtime_validation(
        self,
        *,
        project_dir: Path,
        output_dir: Path,
        project_name: str,
    ) -> dict[str, Any]:
        frontend_dir = output_dir / "frontend"
        index_file = frontend_dir / "index.html"
        css_file = frontend_dir / "styles.css"
        js_file = frontend_dir / "app.js"
        preview_file = project_dir / "preview.html"

        exported_preview = self._export_preview_from_output_frontend(preview_file) if index_file.exists() else False
        checks = {
            "output_frontend_index": index_file.exists(),
            "output_frontend_styles": css_file.exists(),
            "output_frontend_script": js_file.exists(),
            "preview_html": preview_file.exists(),
        }
        passed = all(checks.values())
        report = {
            "project_name": project_name,
            "passed": passed,
            "checks": checks,
            "preview_file": str(preview_file) if preview_file.exists() else "",
            "generated_from_output_frontend": exported_preview,
        }
        report_paths = self._frontend_runtime_report_paths(output_dir=output_dir, project_name=project_name)
        report_paths["json"].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        lines = [
            "# Frontend Runtime Validation",
            "",
            f"- Passed: {'yes' if passed else 'no'}",
            f"- Preview file: `{preview_file}`" if preview_file.exists() else "- Preview file: missing",
            "",
            "## Checks",
            "",
        ]
        for key, value in checks.items():
            lines.append(f"- {key}: {'ok' if value else 'missing'}")
        report_paths["markdown"].write_text("\n".join(lines) + "\n", encoding="utf-8")
        report["report_files"] = {name: str(path) for name, path in report_paths.items()}
        return report

    def _cmd_deploy(self, args) -> int:
        """生成部署配置"""
        from .deployers import CICDGenerator, LaunchRehearsalGenerator, LaunchRehearsalRunner

        project_dir = Path.cwd()
        config_manager = ConfigManager(project_dir)
        config = config_manager.load()

        tech_stack = {
            "platform": config.platform,
            "frontend": self._normalize_pipeline_frontend(config.frontend),
            "backend": config.backend,
            "domain": config.domain,
        }
        project_name = self._sanitize_project_name(config.name or project_dir.name)

        platform = self._normalize_cicd_platform(args.cicd or "github")
        generator = CICDGenerator(
            project_dir=project_dir,
            name=project_name,
            tech_stack=tech_stack,
            platform=platform,
        )
        generated_files = generator.generate()

        cicd_map = {
            "github": [".github/workflows/ci.yml", ".github/workflows/cd.yml"],
            "gitlab": [".gitlab-ci.yml"],
            "jenkins": ["Jenkinsfile"],
            "azure": [".azure-pipelines.yml"],
            "bitbucket": ["bitbucket-pipelines.yml"],
            "all": [
                ".github/workflows/ci.yml",
                ".github/workflows/cd.yml",
                ".gitlab-ci.yml",
                "Jenkinsfile",
                ".azure-pipelines.yml",
                "bitbucket-pipelines.yml",
            ],
        }
        docker_related = [
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "k8s/deployment.yaml",
            "k8s/service.yaml",
            "k8s/ingress.yaml",
            "k8s/configmap.yaml",
            "k8s/secret.yaml",
        ]

        want_cicd = bool(args.cicd) or (not args.cicd and not args.docker)
        want_docker = bool(args.docker) or (not args.cicd and not args.docker)

        selected_keys: list[str] = []
        if want_cicd:
            selected_keys.extend(cicd_map.get(platform, []))
        if want_docker:
            selected_keys.extend(docker_related)

        selected_keys = [key for key in selected_keys if key in generated_files]
        if not selected_keys:
            self.console.print("[yellow]没有可生成的部署配置[/yellow]")
            if not args.rehearsal:
                return 0

        self.console.print("[cyan]生成部署配置...[/cyan]")
        written = 0
        for relative_path in selected_keys:
            full_path = project_dir / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_files[relative_path], encoding="utf-8")
            self.console.print(f"  [green]✓[/green] {relative_path}")
            written += 1

        self.console.print(f"[green]✓[/green] 已生成 {written} 个部署文件")

        if args.rehearsal:
            rehearsal_generator = LaunchRehearsalGenerator(
                project_dir=project_dir,
                name=project_name,
                tech_stack=tech_stack,
            )
            rehearsal_files = rehearsal_generator.generate(cicd_platform=args.cicd or "github")
            self.console.print("[cyan]生成发布演练文档...[/cyan]")
            for relative_path, content in rehearsal_files.items():
                full_path = project_dir / relative_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                self.console.print(f"  [green]✓[/green] {relative_path}")

        if args.rehearsal_verify:
            runner = LaunchRehearsalRunner(
                project_dir=project_dir,
                project_name=project_name,
                cicd_platform=args.cicd or "github",
            )
            rehearsal_result = runner.run()
            report_files = runner.write(rehearsal_result)
            status = "[green]通过[/green]" if rehearsal_result.passed else "[red]未通过[/red]"
            self.console.print("[cyan]发布演练验证...[/cyan]")
            self.console.print(f"  {status} 分数: {rehearsal_result.score}/100")
            self.console.print(f"  [green]✓[/green] 报告: {report_files['markdown']}")
            self.console.print(f"  [green]✓[/green] 数据: {report_files['json']}")
            if not rehearsal_result.passed:
                self.console.print("[yellow]演练未通过，请根据报告补齐缺失项后重试[/yellow]")
                return 1

        return 0

    def _cmd_wizard(self, args) -> int:
        """零门槛向导：收集需求并执行完整流水线"""
        self.console.print("[cyan]Super Dev 向导模式[/cyan]")

        if args.quick and not args.idea:
            self.console.print("[red]--quick 需要配合 --idea 使用[/red]")
            return 2

        interactive = not bool(args.idea)
        if interactive and not sys.stdin.isatty():
            self.console.print("[red]非交互环境请使用 --idea 提供需求[/red]")
            return 2

        idea = args.idea
        if interactive:
            raw = input("请输入你的业务需求（例如：做一个企业级 CRM 系统）: ").strip()
            if not raw:
                self.console.print("[red]需求不能为空[/red]")
                return 2
            idea = raw
        if not idea:
            self.console.print("[red]需求不能为空[/red]")
            return 2

        def _pick_choice(
            provided: str | None,
            prompt: str,
            choices: list[str],
            default: str,
        ) -> str:
            if provided:
                return provided
            if not interactive or args.quick:
                return default
            self.console.print(f"[dim]{prompt} 可选: {', '.join(choices)}[/dim]")
            selected = input(f"{prompt} (默认 {default}): ").strip().lower()
            if not selected:
                return default
            if selected in choices:
                return selected
            self.console.print(f"[yellow]输入无效，已使用默认值: {default}[/yellow]")
            return default

        platform = _pick_choice(args.platform, "目标平台", SUPPORTED_PLATFORMS, "web")
        frontend = _pick_choice(args.frontend, "前端框架", SUPPORTED_PIPELINE_FRONTENDS, "react")
        backend = _pick_choice(args.backend, "后端框架", SUPPORTED_PIPELINE_BACKENDS, "node")
        domain_candidates = [item for item in SUPPORTED_DOMAINS if item]
        domain = _pick_choice(args.domain, "业务领域", domain_candidates, "saas")
        cicd = _pick_choice(args.cicd, "CI/CD 平台", SUPPORTED_CICD, "all")

        offline = bool(args.offline)
        if interactive and not args.quick and not args.offline:
            offline_answer = input("是否离线模式（禁用联网检索）? [y/N]: ").strip().lower()
            offline = offline_answer in {"y", "yes"}

        self.console.print("")
        self.console.print("[cyan]向导结果[/cyan]")
        self.console.print(f"  需求: {idea}")
        self.console.print(f"  技术栈: {platform} | {frontend} | {backend}")
        self.console.print(f"  领域: {domain}")
        self.console.print(f"  CI/CD: {cicd}")
        self.console.print(f"  离线模式: {'yes' if offline else 'no'}")
        if args.name:
            self.console.print(f"  项目名: {args.name}")
        self.console.print("")

        pipeline_args = argparse.Namespace(
            description=idea,
            mode="feature",
            platform=platform,
            frontend=frontend,
            backend=backend,
            domain=domain,
            name=args.name,
            cicd=cicd,
            skip_redteam=False,
            skip_scaffold=False,
            skip_quality_gate=False,
            skip_rehearsal_verify=False,
            offline=offline,
            quality_threshold=None,
            resume=False,
        )
        return self._cmd_pipeline(pipeline_args)

    def _cmd_fix(self, args) -> int:
        """显式缺陷修复模式。"""
        self.console.print("[cyan]Super Dev Bugfix Mode[/cyan]")
        self.console.print("[dim]将执行：问题复现与影响分析 -> 轻量补丁文档 -> 定点修复与回归验证 -> 质量门禁与交付[/dim]")
        self.console.print("")
        pipeline_args = argparse.Namespace(
            description=args.description,
            mode="bugfix",
            platform=args.platform,
            frontend=args.frontend,
            backend=args.backend,
            domain=args.domain,
            name=args.name,
            cicd=args.cicd,
            skip_redteam=bool(args.skip_redteam),
            skip_scaffold=bool(args.skip_scaffold),
            skip_quality_gate=bool(args.skip_quality_gate),
            skip_rehearsal_verify=bool(args.skip_rehearsal_verify),
            offline=bool(args.offline),
            quality_threshold=args.quality_threshold,
            resume=False,
        )
        return self._cmd_pipeline(pipeline_args)

    def _cmd_create(self, args) -> int:
        """一键创建项目 - 从想法到规范"""
        from .creators import ProjectCreator

        self.console.print("[cyan]Super Dev 项目创建器[/cyan]")
        self._print_governance_boundary_notice(
            "当前命令生成治理产物与执行提示，不替代宿主 AI 的实际编码。"
        )
        self.console.print(f"[dim]描述: {args.description}[/dim]")
        self.console.print(f"[dim]请求模式: {args.mode}[/dim]")
        self.console.print(f"[dim]平台: {args.platform} | 前端: {args.frontend} | 后端: {args.backend}[/dim]")
        self.console.print("")

        # 确定项目名称
        project_name = args.name
        if not project_name:
            # 从描述生成项目名称
            import re
            words = re.findall(r'[\w]+', args.description)
            if words:
                project_name = '-'.join(words[:3]).lower()
            else:
                project_name = "my-project"
        project_name = self._sanitize_project_name(project_name)

        # 创建项目目录
        project_dir = Path.cwd()
        project_config = ConfigManager(project_dir).load()

        try:
            creator = ProjectCreator(
                project_dir=project_dir,
                name=project_name,
                description=args.description,
                request_mode=args.mode,
                platform=args.platform,
                frontend=args.frontend,
                backend=args.backend,
                domain=args.domain,
                ui_library=getattr(args, 'ui_library', None),
                style_solution=getattr(args, 'style', None),
                state_management=getattr(args, 'state', []) or [],
                testing_frameworks=getattr(args, 'testing', []) or [],
                language_preferences=project_config.language_preferences,
            )

            # 1. 生成文档
            if not args.skip_docs:
                self.console.print("[cyan]第 1 步: 生成专业文档...[/cyan]")
                docs = creator.generate_documents()
                self.console.print(f"  [green]✓[/green] PRD: {docs['prd']}")
                self.console.print(f"  [green]✓[/green] 架构: {docs['architecture']}")
                self.console.print(f"  [green]✓[/green] UI/UX: {docs['uiux']}")
                if docs.get("plan"):
                    self.console.print(f"  [green]✓[/green] 执行路线图: {docs['plan']}")
                if docs.get("frontend_blueprint"):
                    self.console.print(f"  [green]✓[/green] 前端蓝图: {docs['frontend_blueprint']}")
                self.console.print("")

            # 2. 创建 Spec
            self.console.print("[cyan]第 2 步: 创建 Spec 规范...[/cyan]")
            change_id = creator.create_spec()
            self.console.print(f"  [green]✓[/green] 变更 ID: {change_id}")
            self.console.print("")

            # 3. 生成 AI 提示词
            self.console.print("[cyan]第 3 步: 生成 AI 提示词...[/cyan]")
            prompt_file = creator.generate_ai_prompt()
            self.console.print(f"  [green]✓[/green] 提示词: {prompt_file}")
            self.console.print("")

            # 完成
            self.console.print("[green]✓ 项目创建完成！[/green]")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print("  1. 查看生成的文档:")
            self.console.print(f"     - PRD: output/{project_name}-prd.md")
            self.console.print(f"     - 架构: output/{project_name}-architecture.md")
            self.console.print(f"     - UI/UX: output/{project_name}-uiux.md")
            self.console.print(f"     - 执行路线图: output/{project_name}-execution-plan.md")
            self.console.print(f"     - 前端蓝图: output/{project_name}-frontend-blueprint.md")
            self.console.print(f"  2. 查看规范: super-dev spec show {change_id}")
            self.console.print(f"  3. 复制治理提示词并交给宿主会话: cat {prompt_file}")
            self.console.print("  4. 在宿主会话中按 tasks 顺序开发并持续更新规范")

        except Exception as e:
            self.console.print(f"[red]创建失败: {e}[/red]")
            import traceback
            self.console.print(traceback.format_exc())
            return 1

        return 0

    def _cmd_design(self, args) -> int:
        """设计智能引擎命令"""
        from .design import DesignIntelligenceEngine, DesignSystemGenerator, TokenGenerator

        if args.design_command == "search":
            # 搜索设计资产
            self.console.print(f"[cyan]搜索设计资产: {args.query}[/cyan]")

            engine = DesignIntelligenceEngine()

            result = engine.search(
                query=args.query,
                domain=args.domain,
                max_results=args.max_results,
            )

            # 显示结果
            if "error" in result:
                self.console.print(f"[red]搜索失败: {result['error']}[/red]")
                return 1

            domain_name = {
                "style": "风格",
                "color": "配色",
                "typography": "字体",
                "component": "组件",
                "layout": "布局",
                "animation": "动画",
                "ux": "UX 指南",
                "chart": "图表",
                "product": "产品",
            }.get(result["domain"], result["domain"])

            self.console.print(f"\n[green]找到 {result['count']} 个{domain_name}结果:[/green]\n")

            for idx, item in enumerate(result["results"], 1):
                relevance_color = {
                    "high": "green",
                    "medium": "yellow",
                    "low": "dim",
                }.get(item.get("relevance", "low"), "dim")

                self.console.print(f"[{relevance_color}]{idx}.[/] [bold]{item.get('name', item.get('Style Category', item.get('Font Pairing Name', 'N/A')))}[/] (相关度: {item.get('relevance', 'N/A')})")

                # 显示关键信息
                if "description" in item:
                    self.console.print(f"    {item['description']}")
                if "keywords" in item:
                    self.console.print(f"    关键词: {item['keywords']}")
                if "primary_colors" in item:
                    self.console.print(f"    色彩: {item['primary_colors']}")
                if "mood" in item:
                    self.console.print(f"    风格: {item['mood']}")

                self.console.print()

            return 0

        elif args.design_command == "generate":
            # 生成完整设计系统
            self.console.print("[cyan]生成设计系统[/cyan]")
            self.console.print(f"  产品: {args.product}")
            self.console.print(f"  行业: {args.industry}")
            self.console.print(f"  关键词: {' '.join(args.keywords) if args.keywords else 'N/A'}")
            self.console.print(f"  平台: {args.platform}")
            self.console.print()

            generator = DesignSystemGenerator()

            design_system = generator.generate(
                product_type=args.product,
                industry=args.industry,
                keywords=args.keywords or [],
                platform=args.platform,
                aesthetic=args.aesthetic,
            )

            self.console.print("[green]设计系统已生成:[/green]\n")
            self.console.print(f"  名称: {design_system.name}")
            self.console.print(f"  描述: {design_system.description}")

            if design_system.aesthetic:
                self.console.print(f"  美学方向: {design_system.aesthetic.name}")
                self.console.print(f"  差异化特征: {design_system.aesthetic.differentiation}")

            self.console.print("\n[cyan]生成文件...[/cyan]")

            output_dir = Path(args.output)
            generated_files = generator.generate_documentation(design_system, output_dir)

            for file_path in generated_files:
                self.console.print(f"  [green]✓[/green] {file_path}")

            self.console.print("\n[dim]下一步:[/dim]")
            self.console.print(f"  1. 查看 {output_dir / 'DESIGN_SYSTEM.md'} 了解设计系统")
            self.console.print(f"  2. 使用 {output_dir / 'design-tokens.css'} 导入 CSS 变量")
            self.console.print(f"  3. 使用 {output_dir / 'tailwind.config.json'} 配置 Tailwind")

            return 0

        elif args.design_command == "tokens":
            # 生成 design tokens
            self.console.print("[cyan]生成 design tokens[/cyan]")
            self.console.print(f"  主色: {args.primary}")
            self.console.print(f"  类型: {args.type}")
            self.console.print()

            token_gen = TokenGenerator()

            if args.format == "css":
                tokens = token_gen.generate_all_tokens(args.primary, args.type)

                css_content = [":root {"]
                css_content.append("  /* Colors */")

                for name, value in tokens["colors"].items():
                    css_content.append(f"  --color-{name}: {value};")

                css_content.append("")
                css_content.append("  /* Spacing */")

                for name, value in tokens["spacing"].items():
                    css_content.append(f"  --space-{name}: {value};")

                css_content.append("")
                css_content.append("  /* Shadows */")

                for name, value in tokens["shadows"].items():
                    css_content.append(f"  --shadow-{name}: {value};")

                css_content.append("}")

                output = "\n".join(css_content)

                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]✓[/green] 已保存到 {args.output}")
                else:
                    self.console.print(output)

            elif args.format == "json":
                tokens = token_gen.generate_all_tokens(args.primary, args.type)
                output = json.dumps(tokens, indent=2)

                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]✓[/green] 已保存到 {args.output}")
                else:
                    self.console.print(output)

            elif args.format == "tailwind":
                tokens = token_gen.generate_all_tokens(args.primary, args.type)

                tailwind_config = {
                    "theme": {
                        "extend": {
                            "colors": {f"{k}": v for k, v in tokens["colors"].items()},
                            "spacing": tokens["spacing"],
                            "boxShadow": tokens["shadows"],
                        }
                    }
                }

                output = json.dumps(tailwind_config, indent=2)

                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]✓[/green] 已保存到 {args.output}")
                else:
                    self.console.print(output)

            return 0

        elif args.design_command == "landing":
            # Landing 页面模式生成
            from .design import get_landing_generator

            landing_gen = get_landing_generator()

            # 列出所有模式
            if hasattr(args, 'list') and args.list:
                pattern_names = landing_gen.list_patterns()
                self.console.print(f"\n[green]可用的 Landing 页面模式 ({len(pattern_names)} 个):[/green]\n")
                for i, pattern_name in enumerate(pattern_names, 1):
                    self.console.print(f"  {i}. {pattern_name}")
                self.console.print()
                return 0

            # 智能推荐
            if hasattr(args, 'product_type') and args.product_type:
                self.console.print("[cyan]智能推荐 Landing 页面模式[/cyan]")
                self.console.print(f"  产品类型: {args.product_type}")
                self.console.print(f"  目标: {args.goal if hasattr(args, 'goal') and args.goal else 'N/A'}")
                self.console.print(f"  受众: {args.audience if hasattr(args, 'audience') and args.audience else 'N/A'}")
                self.console.print()

                recommended = landing_gen.recommend(
                    product_type=args.product_type,
                    goal=args.goal if hasattr(args, 'goal') and args.goal else "",
                    audience=args.audience if hasattr(args, 'audience') and args.audience else ""
                )

                if recommended:
                    self.console.print(f"[green]推荐模式: {recommended.name}[/green]")
                    self.console.print(f"  {recommended.description}")
                    self.console.print(f"  适合: {', '.join(recommended.best_for)}")
                    self.console.print(f"  复杂度: {recommended.complexity}")
                    self.console.print()
                    return 0

            # 搜索模式
            query = args.query if hasattr(args, 'query') and args.query else ""
            if query:
                self.console.print(f"[cyan]搜索 Landing 页面模式: {query}[/cyan]\n")

                landing_results = landing_gen.search(query, max_results=args.max_results)

                if not landing_results:
                    self.console.print("[yellow]未找到匹配的模式[/yellow]")
                    return 1

                self.console.print(f"[green]找到 {len(landing_results)} 个结果:[/green]\n")

                for idx, landing_pattern in enumerate(landing_results, 1):
                    self.console.print(f"[cyan]{idx}. {landing_pattern.name}[/cyan]")
                    self.console.print(f"    {landing_pattern.description}")
                    self.console.print(f"    适合: {', '.join(landing_pattern.best_for)}")
                    self.console.print(f"    复杂度: {landing_pattern.complexity}")
                    self.console.print()

                return 0

            # 默认显示所有模式
            pattern_names = landing_gen.list_patterns()
            self.console.print(f"\n[green]可用的 Landing 页面模式 ({len(pattern_names)} 个):[/green]\n")
            for i, pattern_name in enumerate(pattern_names, 1):
                self.console.print(f"  {i}. {pattern_name}")
            self.console.print()
            return 0

        elif args.design_command == "chart":
            # 图表类型推荐
            from .design import get_chart_recommender

            chart_recommender = get_chart_recommender()

            # 列出所有图表类型
            if hasattr(args, 'list') and args.list:
                chart_types = chart_recommender.list_chart_types()
                categories = chart_recommender.list_categories()
                self.console.print(f"\n[green]可用的图表类型 ({len(chart_types)} 个, {len(categories)} 个类别):[/green]\n")
                for category in sorted(categories):
                    types = [ct for ct in chart_types if ct in [c.name for c in chart_recommender.chart_types if c.category.value == category]]
                    self.console.print(f"  [cyan]{category}:[/cyan]")
                    for ct in sorted(types):
                        self.console.print(f"    - {ct}")
                self.console.print()
                return 0

            # 推荐图表类型
            data_description = args.data_description if hasattr(args, 'data_description') else ""
            if data_description:
                self.console.print("[cyan]推荐图表类型[/cyan]")
                self.console.print(f"  数据描述: {data_description}")
                self.console.print(f"  框架: {args.framework}")
                self.console.print()

                chart_recommendations = chart_recommender.recommend(
                    data_description=data_description,
                    framework=args.framework,
                    max_results=args.max_results
                )

                if not chart_recommendations:
                    self.console.print("[yellow]未找到合适的图表类型[/yellow]")
                    return 1

                self.console.print("[green]推荐结果:[/green]\n")

                for idx, chart_rec in enumerate(chart_recommendations, 1):
                    confidence_pct = int(chart_rec.confidence * 100)
                    self.console.print(f"[cyan]{idx}. {chart_rec.chart_type.name}[/cyan] (置信度: {confidence_pct}%)")
                    self.console.print(f"    {chart_rec.chart_type.description}")
                    self.console.print(f"    理由: {chart_rec.reasoning}")
                    self.console.print(f"    推荐库: {chart_rec.library_recommendation}")
                    self.console.print(f"    无障碍: {chart_rec.chart_type.accessibility_notes}")
                    if chart_rec.alternatives:
                        self.console.print(f"    替代方案: {', '.join([a.name for a in chart_rec.alternatives])}")
                    self.console.print()

                return 0

            # 默认显示所有图表类型
            chart_types = chart_recommender.list_chart_types()
            self.console.print(f"\n[green]可用的图表类型 ({len(chart_types)} 个):[/green]\n")
            for i, ct in enumerate(chart_types, 1):
                self.console.print(f"  {i}. {ct}")
            self.console.print()
            return 0

        elif args.design_command == "ux":
            # UX 指南查询
            from .design import get_ux_guide

            ux_guide = get_ux_guide()

            # 列出所有领域
            if hasattr(args, 'list_domains') and args.list_domains:
                domains = ux_guide.list_domains()
                self.console.print(f"\n[green]UX 指南领域 ({len(domains)} 个):[/green]\n")
                for i, domain in enumerate(domains, 1):
                    self.console.print(f"  {i}. {domain}")
                self.console.print()
                return 0

            # 快速见效的改进
            if hasattr(args, 'quick_wins') and args.quick_wins:
                self.console.print("[cyan]快速见效的 UX 改进建议[/cyan]\n")

                ux_quick_wins = ux_guide.get_quick_wins(max_results=args.max_results)

                if not ux_quick_wins:
                    self.console.print("[yellow]未找到快速见效的建议[/yellow]")
                    return 1

                for idx, ux_rec in enumerate(ux_quick_wins, 1):
                    self.console.print(f"[cyan]{idx}. {ux_rec.guideline.topic}[/cyan] ({ux_rec.guideline.domain.value})")
                    self.console.print(f"    [green]最佳实践:[/green] {ux_rec.guideline.best_practice}")
                    self.console.print(f"    [red]反模式:[/red] {ux_rec.guideline.anti_pattern}")
                    self.console.print(f"    影响: {ux_rec.guideline.impact}")
                    self.console.print(f"    优先级: {ux_rec.priority} | 实现难度: {ux_rec.implementation_effort} | 用户影响: {ux_rec.user_impact}")
                    if ux_rec.resources:
                        self.console.print(f"    资源: {', '.join(ux_rec.resources)}")
                    self.console.print()

                return 0

            # 检查清单
            if hasattr(args, 'checklist') and args.checklist:
                self.console.print("[cyan]UX 检查清单[/cyan]\n")

                checklist = ux_guide.get_checklist(domains=[args.domain] if hasattr(args, 'domain') and args.domain else None)

                for domain, items in sorted(checklist.items()):
                    self.console.print(f"[cyan]{domain}:[/cyan]")
                    for item in items:
                        self.console.print(f"  {item}")
                    self.console.print()

                return 0

            # 搜索 UX 指南
            query = args.query if hasattr(args, 'query') and args.query else ""
            if query:
                self.console.print(f"[cyan]搜索 UX 指南: {query}[/cyan]\n")

                ux_recommendations = ux_guide.search(
                    query=query,
                    domain=args.domain if hasattr(args, 'domain') else None,
                    max_results=args.max_results
                )

                if not ux_recommendations:
                    self.console.print("[yellow]未找到匹配的 UX 指南[/yellow]")
                    return 1

                self.console.print(f"[green]找到 {len(ux_recommendations)} 个结果:[/green]\n")

                for idx, ux_rec in enumerate(ux_recommendations, 1):
                    self.console.print(f"[cyan]{idx}. {ux_rec.guideline.topic}[/cyan] ({ux_rec.guideline.domain.value})")
                    self.console.print(f"    [green]最佳实践:[/green] {ux_rec.guideline.best_practice}")
                    self.console.print(f"    [red]反模式:[/red] {ux_rec.guideline.anti_pattern}")
                    self.console.print(f"    影响: {ux_rec.guideline.impact}")
                    self.console.print(f"    优先级: {ux_rec.priority} | 实现难度: {ux_rec.implementation_effort} | 用户影响: {ux_rec.user_impact}")
                    if ux_rec.resources:
                        self.console.print(f"    资源: {', '.join(ux_rec.resources)}")
                    self.console.print()

                return 0

            # 默认显示所有领域
            domains = ux_guide.list_domains()
            self.console.print(f"\n[green]UX 指南领域 ({len(domains)} 个):[/green]\n")
            for i, domain in enumerate(domains, 1):
                self.console.print(f"  {i}. {domain}")
            self.console.print()
            return 0

        elif args.design_command == "stack":
            # 技术栈最佳实践
            from .design import get_tech_stack_engine

            tech_engine = get_tech_stack_engine()

            # 列出所有技术栈
            if hasattr(args, 'list') and args.list:
                stacks = tech_engine.list_stacks()
                self.console.print(f"\n[green]支持的技术栈 ({len(stacks)} 个):[/green]\n")
                for i, stack in enumerate(stacks, 1):
                    self.console.print(f"  {i}. {stack}")
                self.console.print()
                return 0

            # 查询参数
            stack_name = args.stack
            query = args.query if hasattr(args, 'query') and args.query else None
            category = args.category if hasattr(args, 'category') else None

            # 显示设计模式
            if hasattr(args, 'patterns') and args.patterns:
                tech_patterns = tech_engine.get_patterns(stack_name)

                if not tech_patterns:
                    self.console.print(f"[yellow]未找到 {stack_name} 的设计模式[/yellow]")
                    return 1

                self.console.print(f"\n[cyan]{stack_name} 设计模式 ({len(tech_patterns)} 个):[/cyan]\n")

                for idx, tech_pattern in enumerate(tech_patterns, 1):
                    self.console.print(f"[cyan]{idx}. {tech_pattern.name}[/cyan]")
                    self.console.print(f"    描述: {tech_pattern.description}")
                    self.console.print(f"    使用场景: {tech_pattern.use_case}")
                    if tech_pattern.pros:
                        self.console.print(f"    优点: {', '.join(tech_pattern.pros)}")
                    if tech_pattern.cons:
                        self.console.print(f"    缺点: {', '.join(tech_pattern.cons)}")
                    self.console.print()

                return 0

            # 显示性能优化建议
            if hasattr(args, 'performance') and args.performance:
                tips = tech_engine.get_performance_tips(stack_name)

                if not tips:
                    self.console.print(f"[yellow]未找到 {stack_name} 的性能建议[/yellow]")
                    return 1

                self.console.print(f"\n[cyan]{stack_name} 性能优化建议 ({len(tips)} 个):[/cyan]\n")

                for idx, tip in enumerate(tips, 1):
                    self.console.print(f"[cyan]{idx}. {tip.topic} - {tip.technique}[/cyan]")
                    self.console.print(f"    描述: {tip.description}")
                    self.console.print(f"    影响: {tip.impact} | 实施难度: {tip.effort}")
                    if tip.code_snippet:
                        self.console.print(f"    代码示例:\n    [dim]{tip.code_snippet}[/dim]")
                    self.console.print()

                return 0

            # 快速见效的性能优化
            if hasattr(args, 'quick_wins') and args.quick_wins:
                tips = tech_engine.get_quick_wins(stack_name)

                if not tips:
                    self.console.print(f"[yellow]未找到 {stack_name} 的快速性能优化[/yellow]")
                    return 1

                self.console.print(f"\n[cyan]{stack_name} 快速见效的性能优化 ({len(tips)} 个):[/cyan]\n")

                for idx, tip in enumerate(tips, 1):
                    self.console.print(f"[cyan]{idx}. {tip.topic} - {tip.technique}[/cyan]")
                    self.console.print(f"    描述: {tip.description}")
                    if tip.code_snippet:
                        self.console.print(f"    代码示例:\n    [dim]{tip.code_snippet}[/dim]")
                    self.console.print()

                return 0

            # 搜索最佳实践
            self.console.print(f"[cyan]搜索 {stack_name} 最佳实践[/cyan]\n")

            if query:
                self.console.print(f"查询: {query}\n")

            stack_recommendations = tech_engine.search_practices(
                stack=stack_name,
                query=query,
                category=category,
                max_results=args.max_results
            )

            if not stack_recommendations:
                self.console.print("[yellow]未找到匹配的最佳实践[/yellow]")
                return 1

            for idx, stack_rec in enumerate(stack_recommendations, 1):
                self.console.print(f"[cyan]{idx}. {stack_rec.practice.topic}[/cyan] ({stack_rec.practice.category.value})")
                self.console.print(f"    [green]最佳实践:[/green] {stack_rec.practice.practice}")
                self.console.print(f"    [red]反模式:[/red] {stack_rec.practice.anti_pattern}")
                self.console.print(f"    好处: {stack_rec.practice.benefits}")
                self.console.print(f"    优先级: {stack_rec.priority} | 复杂度: {stack_rec.practice.complexity}")
                if stack_rec.context:
                    self.console.print(f"    上下文: {stack_rec.context}")
                if stack_rec.alternatives:
                    self.console.print(
                        f"    替代方案: {', '.join([a.value if hasattr(a, 'value') else str(a) for a in stack_rec.alternatives])}"
                    )
                if stack_rec.resources:
                    self.console.print(f"    资源: {', '.join(stack_rec.resources)}")
                if stack_rec.practice.code_example:
                    self.console.print(f"    代码示例:\n    [dim]{stack_rec.practice.code_example[:200]}...[/dim]")
                self.console.print()

            return 0

        elif args.design_command == "codegen":
            # 代码片段生成
            from .design import get_code_generator
            from .design.codegen import Framework

            codegen = get_code_generator()

            # 列出所有可用组件
            if hasattr(args, 'list') and args.list:
                components = codegen.get_available_components(
                    framework=Framework(args.framework) if hasattr(args, 'framework') else None
                )

                self.console.print(f"\n[green]可用组件 ({args.framework or 'all'}):[/green]\n")

                for category, comp_list in sorted(components.items()):
                    self.console.print(f"[cyan]{category}:[/cyan]")
                    for comp in comp_list:
                        self.console.print(f"  - {comp}")
                    self.console.print()

                return 0

            # 搜索组件
            if hasattr(args, 'search') and args.search:
                component_snippets = codegen.search_components(
                    query=args.search,
                    framework=args.framework if hasattr(args, 'framework') else None
                )

                if not component_snippets:
                    self.console.print(f"[yellow]未找到匹配的组件: {args.search}[/yellow]")
                    return 1

                self.console.print(f"\n[green]找到 {len(component_snippets)} 个组件:[/green]\n")

                for idx, snippet in enumerate(component_snippets, 1):
                    self.console.print(f"[cyan]{idx}. {snippet.name}[/cyan] ({snippet.framework.value})")
                    self.console.print(f"    类别: {snippet.category.value}")
                    self.console.print(f"    描述: {snippet.description}")
                    self.console.print(f"    依赖: {', '.join(snippet.dependencies)}")
                    if snippet.preview:
                        self.console.print(f"    预览: [dim]{snippet.preview}[/dim]")
                    self.console.print()

                return 0

            # 生成组件代码
            component_name = args.component
            framework = args.framework if hasattr(args, 'framework') else "react"

            self.console.print(f"[cyan]生成 {component_name} 组件 ({framework})[/cyan]\n")

            component = codegen.generate_component(
                component_name=component_name,
                framework=Framework(framework)
            )

            if not component:
                self.console.print(f"[yellow]未找到组件: {component_name}[/yellow]")
                self.console.print("使用 --list 查看可用组件")
                return 1

            self.console.print(f"[green]组件名称:[/green] {component_name}")
            self.console.print(f"[green]描述:[/green] {component.description}\n")

            self.console.print("[cyan]代码:[/cyan]")
            self.console.print(f"```{framework}")
            self.console.print(component.code)
            self.console.print("```\n")

            if component.imports:
                self.console.print("[cyan]导入语句:[/cyan]")
                for imp in component.imports:
                    self.console.print(f"  {imp}")
                self.console.print()

            if component.dependencies:
                self.console.print("[cyan]依赖:[/cyan]")
                self.console.print(f"  {', '.join(component.dependencies)}")
                self.console.print()

            if component.usage_example:
                self.console.print("[cyan]使用示例:[/cyan]")
                self.console.print(f"  [dim]{component.usage_example}[/dim]")

            # 输出到文件
            if hasattr(args, 'output') and args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(component.code)

                self.console.print(f"\n[green]已保存到: {output_path}[/green]")

            return 0

        else:
            self.console.print("[yellow]请指定设计子命令[/yellow]")
            self.console.print("  可用命令: search, generate, tokens, landing, chart, ux, stack, codegen")
            self.console.print("  使用 'super-dev design <command> -h' 查看帮助")
            return 1

    def _cmd_pipeline(self, args) -> int:
        """运行完整流水线 - 从想法到部署"""
        self._print_governance_boundary_notice(
            "流水线负责生成研究、文档、门禁与交付产物；实际编码能力仍由宿主 AI 提供。"
        )
        request_mode_override = getattr(args, "mode", "feature")
        if request_mode_override not in {"feature", "bugfix"}:
            request_mode_override = "feature"
        # 确定项目名称
        project_name = args.name
        if not project_name:
            import re
            words = re.findall(r'[\w]+', args.description)
            if words:
                project_name = '-'.join(words[:3]).lower()
            else:
                project_name = "my-project"
        project_name = self._sanitize_project_name(project_name)

        tech_stack = {
            "platform": args.platform,
            "frontend": args.frontend,
            "backend": args.backend,
            "domain": args.domain,
        }

        project_dir = Path.cwd()
        output_dir = project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        pipeline_config = ConfigManager(project_dir).load()
        if not self._ensure_pipeline_host_ready(project_dir=project_dir, config=pipeline_config):
            return 1
        resume_requested = bool(getattr(args, "resume", False))
        from .policy import PipelinePolicyManager

        policy_manager = PipelinePolicyManager(project_dir)
        policy_violations = policy_manager.validate_pipeline_args(args=args, config=pipeline_config)
        if policy_violations:
            self.console.print("[red]流水线策略校验未通过:[/red]")
            for item in policy_violations:
                self.console.print(f"  - {item}")
            self.console.print(f"[dim]策略文件: {policy_manager.policy_path}[/dim]")
            self.console.print("[dim]可使用 `super-dev policy show` 查看当前策略[/dim]")
            return 1

        pipeline_args_snapshot: dict[str, Any] = {
            "description": args.description,
            "mode": request_mode_override,
            "platform": args.platform,
            "frontend": args.frontend,
            "backend": args.backend,
            "domain": args.domain,
            "name": args.name,
            "cicd": args.cicd,
            "skip_redteam": bool(args.skip_redteam),
            "skip_scaffold": bool(args.skip_scaffold),
            "skip_quality_gate": bool(args.skip_quality_gate),
            "skip_rehearsal_verify": bool(args.skip_rehearsal_verify),
            "offline": bool(args.offline),
            "quality_threshold": args.quality_threshold,
        }
        pipeline_policy = policy_manager.load()

        self.console.print(f"[cyan]{'=' * 60}[/cyan]")
        self.console.print("[cyan]Super Dev 完整流水线[/cyan]")
        self.console.print(f"[cyan]{'=' * 60}[/cyan]")
        self.console.print(f"[dim]项目: {project_name}[/dim]")
        self.console.print(f"[dim]请求模式: {request_mode_override}[/dim]")
        self.console.print(f"[dim]技术栈: {args.platform} | {args.frontend} | {args.backend}[/dim]")
        self.console.print("")

        from .orchestrator.contracts import PipelineContractReport
        from .orchestrator.telemetry import PipelineTelemetryReport

        telemetry = PipelineTelemetryReport(project_name=project_name)
        contract_report = PipelineContractReport(project_name=project_name)
        pipeline_started_at = time.perf_counter()
        current_stage = ""
        current_stage_title = ""
        stage_started_at = pipeline_started_at
        resume_from_stage: int | None = None
        scenario = ""
        requirements: list[dict[str, Any]] = []
        phases: list[Any] = []
        change_id = ""
        enriched_description = args.description
        scaffold_result: dict[str, list[str]] = {"frontend_files": [], "backend_files": []}
        task_execution_summary = None
        run_state = self._read_pipeline_run_state(project_dir) if resume_requested else None
        metrics_payload = self._load_pipeline_metrics_payload(output_dir=output_dir, project_name=project_name)
        run_context = self._extract_resume_context(run_state=run_state, metrics_payload=metrics_payload)

        stored_scenario = run_context.get("scenario")
        if isinstance(stored_scenario, str) and stored_scenario in {"0-1", "1-N+1"}:
            scenario = stored_scenario
        stored_requirements = run_context.get("requirements")
        requirements = self._normalize_requirements_payload(stored_requirements)
        stored_change_id = run_context.get("change_id")
        if isinstance(stored_change_id, str) and stored_change_id.strip():
            change_id = stored_change_id.strip()
        else:
            detected_change = self._detect_latest_change_id(project_dir)
            if detected_change:
                change_id = detected_change
                run_context["change_id"] = detected_change
        stored_enriched_desc = run_context.get("enriched_description")
        if isinstance(stored_enriched_desc, str) and stored_enriched_desc.strip():
            enriched_description = stored_enriched_desc

        research_file = output_dir / f"{project_name}-research.md"
        prd_file = output_dir / f"{project_name}-prd.md"
        arch_file = output_dir / f"{project_name}-architecture.md"
        uiux_file = output_dir / f"{project_name}-uiux.md"
        plan_file = output_dir / f"{project_name}-execution-plan.md"
        frontend_blueprint_file = output_dir / f"{project_name}-frontend-blueprint.md"
        resume_audit_payload: dict[str, Any] | None = None
        resume_audit_files: dict[str, Path] | None = None
        stage_output_evidence: list[str] = []

        def _start_stage(stage: str, title: str) -> None:
            nonlocal current_stage, current_stage_title, stage_started_at
            current_stage = stage
            current_stage_title = title
            stage_started_at = time.perf_counter()

        def _record_stage(success: bool, details: dict[str, Any] | None = None) -> None:
            nonlocal stage_output_evidence
            if not current_stage:
                return
            normalized_details = details or {}
            stage_outputs = self._extract_stage_artifacts(normalized_details)
            stage_notes = self._extract_stage_notes(normalized_details)
            telemetry.record_stage(
                stage=current_stage,
                title=current_stage_title,
                success=success,
                duration_seconds=time.perf_counter() - stage_started_at,
                details=normalized_details,
            )
            contract_report.record_stage(
                stage=current_stage,
                title=current_stage_title,
                success=success,
                duration_seconds=time.perf_counter() - stage_started_at,
                inputs=list(stage_output_evidence),
                outputs=stage_outputs,
                notes=stage_notes,
            )
            stage_output_evidence = stage_outputs or stage_output_evidence

        def _write_metrics_snapshot() -> Path:
            """写入当前指标快照，供后续发布演练校验读取。"""
            snapshot_file = output_dir / f"{project_name}-pipeline-metrics.json"
            snapshot_payload = telemetry.to_dict()
            snapshot_file.write_text(
                json.dumps(snapshot_payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return snapshot_file

        def _finalize_metrics(success: bool, reason: str = "") -> dict[str, Path]:
            telemetry.finalize(
                success=success,
                total_duration_seconds=time.perf_counter() - pipeline_started_at,
                failure_reason=reason,
            )
            return telemetry.write(output_dir=output_dir)

        def _finalize_contract(success: bool, reason: str = "") -> dict[str, Path]:
            contract_report.finalize(success=success, failure_reason=reason)
            return contract_report.write(output_dir=output_dir)

        def _persist_run_state(status: str, extra: dict[str, Any] | None = None) -> None:
            payload = {
                "status": status,
                "status_normalized": self._normalize_run_status(status),
                "project_name": project_name,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "pipeline_args": pipeline_args_snapshot,
                "context": run_context,
            }
            if extra:
                payload.update(extra)
            self._write_pipeline_run_state(project_dir, payload)

        def _update_run_context(**values: Any) -> None:
            for key, value in values.items():
                if value is None:
                    continue
                run_context[key] = value

        _update_run_context(pipeline_policy=pipeline_policy.__dict__)

        def _should_skip_for_resume(stage_num: int) -> bool:
            return resume_from_stage is not None and stage_num < resume_from_stage

        def _flush_resume_audit(status: str, failure_reason: str = "") -> None:
            nonlocal resume_audit_payload, resume_audit_files
            if not resume_audit_payload:
                return
            resume_audit_payload["status"] = status
            resume_audit_payload["finished_at"] = datetime.now(timezone.utc).isoformat()
            if failure_reason:
                resume_audit_payload["failure_reason"] = failure_reason
            resume_audit_files = self._write_resume_audit(
                output_dir=output_dir,
                project_name=project_name,
                payload=resume_audit_payload,
            )

        try:
            _persist_run_state("running")
            if resume_requested:
                run_status = (
                    str((run_state or {}).get("status", "")).strip().lower()
                    if isinstance(run_state, dict)
                    else ""
                )
                fallback_reasons: list[str] = []
                if run_status in {"waiting_confirmation", "waiting_ui_revision", "waiting_architecture_revision", "waiting_quality_revision"}:
                    failed_stage = None
                    resume_from_stage = None
                    if isinstance(run_state, dict):
                        resume_from_stage = self._coerce_stage_number(run_state.get("resume_from_stage"))
                        if resume_from_stage is None:
                            resume_from_stage = self._coerce_stage_number(run_state.get("next_stage"))
                    if resume_from_stage is None:
                        resume_from_stage = 2
                    initial_resume_stage = resume_from_stage
                    if run_status == "waiting_ui_revision":
                        self.console.print(
                            f"[cyan]恢复模式：UI 改版门已通过，将从第 {resume_from_stage} 阶段继续[/cyan]"
                        )
                    elif run_status == "waiting_architecture_revision":
                        self.console.print(
                            f"[cyan]恢复模式：架构返工已通过，将从第 {resume_from_stage} 阶段继续[/cyan]"
                        )
                    elif run_status == "waiting_quality_revision":
                        self.console.print(
                            f"[cyan]恢复模式：质量返工已通过，将从第 {resume_from_stage} 阶段继续[/cyan]"
                        )
                    else:
                        self.console.print(
                            f"[cyan]恢复模式：文档确认已完成，将从第 {resume_from_stage} 阶段继续[/cyan]"
                        )
                else:
                    failed_stage = None
                    if isinstance(run_state, dict):
                        failed_stage = self._coerce_stage_number(run_state.get("failed_stage"))
                    if failed_stage is None:
                        failed_stage = self._detect_failed_stage_from_metrics_payload(metrics_payload)
                    if failed_stage is None:
                        failed_stage = self._detect_failed_stage(output_dir=output_dir, project_name=project_name)

                    resume_from_stage = self._resolve_resume_start_stage(
                        failed_stage=failed_stage,
                        skip_redteam=bool(args.skip_redteam),
                    )
                    initial_resume_stage = resume_from_stage
                    adjusted_resume_stage, fallback_reasons = self._adjust_resume_stage_for_artifacts(
                        project_dir=project_dir,
                        output_dir=output_dir,
                        project_name=project_name,
                        resume_from_stage=resume_from_stage,
                    )
                    if adjusted_resume_stage != resume_from_stage and adjusted_resume_stage is not None:
                        for reason in fallback_reasons:
                            self.console.print(f"[yellow]恢复校验: {reason}[/yellow]")
                        self.console.print(
                            f"[yellow]恢复起点已自动下调到第 {adjusted_resume_stage} 阶段[/yellow]"
                        )
                    resume_from_stage = adjusted_resume_stage
                    if failed_stage is None:
                        self.console.print("[yellow]未检测到可恢复的失败记录，将执行完整流水线[/yellow]")
                    elif resume_from_stage is not None:
                        self.console.print(
                            f"[cyan]恢复模式：检测到上次失败阶段 {failed_stage}，将从第 {resume_from_stage} 阶段继续[/cyan]"
                        )
                    else:
                        self.console.print(
                            f"[yellow]上次失败发生在第 {failed_stage} 阶段，当前将执行完整流水线以确保一致性[/yellow]"
                        )
                _update_run_context(
                    resume_detected_failed_stage=failed_stage,
                    resume_from_stage=resume_from_stage,
                )
                _persist_run_state(
                    "running",
                    {
                        "failed_stage": str(failed_stage) if failed_stage is not None else "",
                        "resume_from_stage": (
                            str(resume_from_stage) if resume_from_stage is not None else ""
                        ),
                    },
                )
                resume_audit_payload = {
                    "project_name": project_name,
                    "status": "running",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "finished_at": "",
                    "run_state_status": (
                        str((run_state or {}).get("status", "")) if isinstance(run_state, dict) else ""
                    ),
                    "detected_failed_stage": failed_stage,
                    "initial_resume_stage": initial_resume_stage,
                    "final_resume_stage": resume_from_stage,
                    "planned_skipped_stages": (
                        list(range(resume_from_stage)) if resume_from_stage is not None else []
                    ),
                    "fallback_reasons": fallback_reasons,
                }
                resume_audit_files = self._write_resume_audit(
                    output_dir=output_dir,
                    project_name=project_name,
                    payload=resume_audit_payload,
                )
                self.console.print(f"[dim]恢复审计报告: {resume_audit_files['markdown']}[/dim]")

            knowledge_dir = project_dir / "knowledge"
            knowledge_cache_file = output_dir / "knowledge-cache" / f"{project_name}-knowledge-bundle.json"
            knowledge_file_count = 0
            if knowledge_dir.exists():
                knowledge_file_count = sum(
                    1
                    for path in knowledge_dir.rglob("*")
                    if path.is_file() and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml"}
                )
            self.console.print(
                f"[dim]知识库扫描: knowledge 文件 {knowledge_file_count} 条 | "
                f"缓存 {'存在' if knowledge_cache_file.exists() else '不存在'}[/dim]"
            )
            _update_run_context(
                knowledge_file_count=knowledge_file_count,
                knowledge_cache_exists=knowledge_cache_file.exists(),
            )

            # ========== 第 0 阶段: 需求增强 ==========
            _start_stage("0", "需求增强")
            if _should_skip_for_resume(0):
                self.console.print("[yellow]第 0 阶段: 需求增强 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
                _update_run_context(enriched_description=enriched_description)
            else:
                self.console.print("[cyan]第 0 阶段: 需求增强 (联网 + 知识库)...[/cyan]")
                import os

                from .orchestrator.knowledge import KnowledgeAugmenter

                disable_web = args.offline or (
                    os.getenv("SUPER_DEV_DISABLE_WEB", "").strip().lower() in {"1", "true", "yes"}
                )
                augmenter = KnowledgeAugmenter(
                    project_dir=project_dir,
                    web_enabled=not disable_web,
                    allowed_web_domains=pipeline_config.knowledge_allowed_domains,
                    cache_ttl_seconds=pipeline_config.knowledge_cache_ttl_seconds,
                )
                knowledge_bundle = augmenter.load_cached_bundle(
                    output_dir=output_dir,
                    project_name=project_name,
                    requirement=args.description,
                    domain=args.domain or "",
                )
                cache_hit = knowledge_bundle is not None
                if knowledge_bundle is None:
                    knowledge_bundle = augmenter.augment(
                        requirement=args.description,
                        domain=args.domain or "",
                    )
                research_file = output_dir / f"{project_name}-research.md"
                research_file.write_text(augmenter.to_markdown(knowledge_bundle), encoding="utf-8")
                if cache_hit:
                    knowledge_cache_file = output_dir / "knowledge-cache" / f"{project_name}-knowledge-bundle.json"
                else:
                    knowledge_cache_file = augmenter.save_bundle(
                        bundle=knowledge_bundle,
                        output_dir=output_dir,
                        project_name=project_name,
                        requirement=args.description,
                        domain=args.domain or "",
                    )

                enriched_description = knowledge_bundle.get("enriched_requirement", args.description)
                self.console.print(f"  [green]✓[/green] 需求增强报告: {research_file}")
                self.console.print(f"  [green]✓[/green] 知识缓存: {knowledge_cache_file}")
                self.console.print(f"  [dim]缓存命中: {'yes' if cache_hit else 'no'}[/dim]")
                self.console.print(
                    f"  [dim]本地知识 {len(knowledge_bundle.get('local_knowledge', []))} 条 | "
                    f"联网结果 {len(knowledge_bundle.get('web_knowledge', []))} 条[/dim]"
                )
                self.console.print("")
                _record_stage(
                    True,
                    details={
                        "local_knowledge_count": len(knowledge_bundle.get("local_knowledge", [])),
                        "web_knowledge_count": len(knowledge_bundle.get("web_knowledge", [])),
                        "cache_file": str(knowledge_cache_file),
                        "cache_hit": cache_hit,
                        "knowledge_cache_ttl_seconds": pipeline_config.knowledge_cache_ttl_seconds,
                        "knowledge_allowed_domains": pipeline_config.knowledge_allowed_domains,
                        "web_filtered_out_count": (
                            (knowledge_bundle.get("metadata") or {})
                            .get("web_stats", {})
                            .get("filtered_out_count", 0)
                        ),
                    },
                )
                _update_run_context(enriched_description=enriched_description)

            # ========== 第 1 阶段: 生成文档 ==========
            _start_stage("1", "专业文档生成")
            if _should_skip_for_resume(1):
                self.console.print("[yellow]第 1 阶段: 生成专业文档 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 1 阶段: 生成专业文档...[/cyan]")
                from .creators import (
                    DocumentGenerator,
                    RequirementParser,
                )

                parser = RequirementParser()
                scenario = parser.detect_scenario(project_dir)
                request_mode = request_mode_override or parser.detect_request_mode(enriched_description)

                doc_generator = DocumentGenerator(
                    name=project_name,
                    description=enriched_description,
                    request_mode=request_mode,
                    platform=args.platform,
                    frontend=args.frontend,
                    backend=args.backend,
                    domain=args.domain,
                    language_preferences=pipeline_config.language_preferences,
                    knowledge_summary=(
                        knowledge_bundle.get("research_summary", {})
                        if isinstance(knowledge_bundle, dict)
                        else {}
                    ),
                )

                # 生成文档内容
                prd_content = doc_generator.generate_prd()
                arch_content = doc_generator.generate_architecture()
                uiux_content = doc_generator.generate_uiux()

                # 写入文件
                prd_file = output_dir / f"{project_name}-prd.md"
                arch_file = output_dir / f"{project_name}-architecture.md"
                uiux_file = output_dir / f"{project_name}-uiux.md"

                prd_file.write_text(prd_content, encoding="utf-8")
                arch_file.write_text(arch_content, encoding="utf-8")
                uiux_file.write_text(uiux_content, encoding="utf-8")

                plan_file = output_dir / f"{project_name}-execution-plan.md"
                frontend_blueprint_file = output_dir / f"{project_name}-frontend-blueprint.md"
                plan_file.write_text(
                    doc_generator.generate_execution_plan(
                        scenario=scenario,
                        request_mode=request_mode,
                    ),
                    encoding="utf-8",
                )
                frontend_blueprint_file.write_text(doc_generator.generate_frontend_blueprint(), encoding="utf-8")

                self.console.print(f"  [green]✓[/green] PRD: {prd_file}")
                self.console.print(f"  [green]✓[/green] 架构: {arch_file}")
                self.console.print(f"  [green]✓[/green] UI/UX: {uiux_file}")
                self.console.print(f"  [green]✓[/green] 执行路线图: {plan_file}")
                self.console.print(f"  [green]✓[/green] 前端蓝图: {frontend_blueprint_file}")
                self.console.print(f"  [dim]场景识别: {scenario}[/dim]")
                self.console.print("")
                _record_stage(
                    True,
                    details={
                        "scenario": scenario,
                        "docs": [
                            str(prd_file),
                            str(arch_file),
                            str(uiux_file),
                            str(plan_file),
                            str(frontend_blueprint_file),
                        ],
                    },
                )

                # 保存技术栈到配置文件（供后续阶段使用）
                self._save_tech_stack_to_config(project_dir, tech_stack, args.description)

                requirements = self._normalize_requirements_payload(doc_generator.extract_requirements())
                phases = parser.build_execution_phases(scenario, requirements, request_mode=request_mode)
                _update_run_context(
                    scenario=scenario,
                    request_mode=request_mode,
                    requirements=requirements,
                )

            docs_confirmation = self._get_docs_confirmation_state(project_dir)
            _update_run_context(docs_confirmation=docs_confirmation)
            if not self._docs_confirmation_is_confirmed(project_dir):
                waiting_reason = (
                    "revision_requested"
                    if docs_confirmation["status"] == "revision_requested"
                    else "pending_review"
                )
                self.console.print("[yellow]已完成 research 与三文档，当前进入文档确认门[/yellow]")
                self.console.print(f"  [dim]研究报告: {research_file}[/dim]")
                self.console.print(f"  [dim]PRD: {prd_file}[/dim]")
                self.console.print(f"  [dim]架构: {arch_file}[/dim]")
                self.console.print(f"  [dim]UI/UX: {uiux_file}[/dim]")
                if docs_confirmation["status"] == "revision_requested":
                    self.console.print("[yellow]当前状态: 用户已要求修改文档，请先修正文档并再次确认。[/yellow]")
                else:
                    self.console.print("[yellow]当前状态: 待用户确认三文档，确认前不会创建 Spec 或开始编码。[/yellow]")
                self.console.print("[cyan]继续方式:[/cyan]")
                self.console.print("  1. 在宿主中查看并修订 output/*-prd.md / *-architecture.md / *-uiux.md")
                self.console.print('  2. 终端执行: super-dev review docs --status confirmed --comment "三文档已确认"')
                self.console.print("  3. 然后执行: super-dev run --resume")
                metric_files = _finalize_metrics(success=False, reason="waiting_confirmation")
                contract_files = _finalize_contract(success=False, reason="waiting_confirmation")
                _persist_run_state(
                    "waiting_confirmation",
                    {
                        "failure_reason": waiting_reason,
                        "failed_stage": "2",
                        "next_stage": "2",
                        "resume_from_stage": "2",
                        "metrics_file": str(metric_files["json"]),
                        "contract_file": str(contract_files["json"]),
                    },
                )
                _flush_resume_audit(status="waiting_confirmation", failure_reason=waiting_reason)
                self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                if resume_audit_files:
                    self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                return 0

            ui_revision = self._get_ui_revision_state(project_dir)
            _update_run_context(ui_revision=ui_revision)
            if ui_revision["status"] == "revision_requested":
                self.console.print("[yellow]当前存在 UI 改版请求，必须先完成 UI 返工后才能继续[/yellow]")
                if ui_revision["comment"]:
                    self.console.print(f"  [dim]备注: {ui_revision['comment']}[/dim]")
                self.console.print("[cyan]继续方式:[/cyan]")
                self.console.print("  1. 先更新 output/*-uiux.md")
                self.console.print("  2. 重做前端并重新执行 frontend runtime 与 UI review")
                self.console.print('  3. 终端执行: super-dev review ui --status confirmed --comment "UI 改版已通过"')
                self.console.print("  4. 然后执行: super-dev run --resume")
                metric_files = _finalize_metrics(success=False, reason="waiting_ui_revision")
                contract_files = _finalize_contract(success=False, reason="waiting_ui_revision")
                _persist_run_state(
                    "waiting_ui_revision",
                    {
                        "failure_reason": "revision_requested",
                        "failed_stage": "2",
                        "next_stage": "2",
                        "resume_from_stage": "2",
                        "metrics_file": str(metric_files["json"]),
                        "contract_file": str(contract_files["json"]),
                    },
                )
                _flush_resume_audit(status="waiting_ui_revision", failure_reason="revision_requested")
                self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                if resume_audit_files:
                    self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                return 0

            architecture_revision = self._get_architecture_revision_state(project_dir)
            _update_run_context(architecture_revision=architecture_revision)
            if architecture_revision["status"] == "revision_requested":
                self.console.print("[yellow]当前存在架构返工请求，必须先完成架构方案修订后才能继续[/yellow]")
                if architecture_revision["comment"]:
                    self.console.print(f"  [dim]备注: {architecture_revision['comment']}[/dim]")
                self.console.print("[cyan]继续方式:[/cyan]")
                self.console.print("  1. 先更新 output/*-architecture.md")
                self.console.print("  2. 同步调整任务拆解与相关实现方案")
                self.console.print('  3. 终端执行: super-dev review architecture --status confirmed --comment "架构返工已通过"')
                self.console.print("  4. 然后执行: super-dev run --resume")
                metric_files = _finalize_metrics(success=False, reason="waiting_architecture_revision")
                contract_files = _finalize_contract(success=False, reason="waiting_architecture_revision")
                _persist_run_state(
                    "waiting_architecture_revision",
                    {
                        "failure_reason": "revision_requested",
                        "failed_stage": "2",
                        "next_stage": "2",
                        "resume_from_stage": "2",
                        "metrics_file": str(metric_files["json"]),
                        "contract_file": str(contract_files["json"]),
                    },
                )
                _flush_resume_audit(status="waiting_architecture_revision", failure_reason="revision_requested")
                self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                if resume_audit_files:
                    self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                return 0

            quality_revision = self._get_quality_revision_state(project_dir)
            _update_run_context(quality_revision=quality_revision)
            if quality_revision["status"] == "revision_requested":
                self.console.print("[yellow]当前存在质量返工请求，必须先修复质量/安全问题后才能继续[/yellow]")
                if quality_revision["comment"]:
                    self.console.print(f"  [dim]备注: {quality_revision['comment']}[/dim]")
                self.console.print("[cyan]继续方式:[/cyan]")
                self.console.print("  1. 先修复质量门禁或安全问题")
                self.console.print("  2. 重新执行 quality gate 与 release proof-pack")
                self.console.print('  3. 终端执行: super-dev review quality --status confirmed --comment "质量返工已通过"')
                self.console.print("  4. 然后执行: super-dev run --resume")
                metric_files = _finalize_metrics(success=False, reason="waiting_quality_revision")
                contract_files = _finalize_contract(success=False, reason="waiting_quality_revision")
                _persist_run_state(
                    "waiting_quality_revision",
                    {
                        "failure_reason": "revision_requested",
                        "failed_stage": "2",
                        "next_stage": "2",
                        "resume_from_stage": "2",
                        "metrics_file": str(metric_files["json"]),
                        "contract_file": str(contract_files["json"]),
                    },
                )
                _flush_resume_audit(status="waiting_quality_revision", failure_reason="revision_requested")
                self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                if resume_audit_files:
                    self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                return 0

            # ========== 第 2 阶段: 创建 Spec ==========
            _start_stage("2", "Spec 创建")
            if _should_skip_for_resume(2):
                self.console.print("[yellow]第 2 阶段: 创建 Spec 规范 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 2 阶段: 创建 Spec 规范...[/cyan]")
                from .creators import SpecBuilder

                spec_builder = SpecBuilder(
                    project_dir=project_dir,
                    name=project_name,
                    description=args.description
                )

                change_id = spec_builder.create_change(requirements, tech_stack, scenario=scenario)

                self.console.print(f"  [green]✓[/green] 变更 ID: {change_id}")
                self.console.print(f"  [green]✓[/green] Spec: .super-dev/changes/{change_id}/")
                self.console.print("")
                _record_stage(True, details={"change_id": change_id})
                _update_run_context(change_id=change_id)

            # ========== 第 3 阶段: 生成前端可演示骨架 ==========
            _start_stage("3", "前端可演示骨架")
            if _should_skip_for_resume(3):
                self.console.print("[yellow]第 3 阶段: 生成前端可演示骨架 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 3 阶段: 生成前端可演示骨架...[/cyan]")
                from .creators import FrontendScaffoldBuilder

                frontend_builder = FrontendScaffoldBuilder(
                    project_dir=project_dir,
                    name=project_name,
                    description=args.description,
                    frontend=args.frontend,
                )
                frontend_files = frontend_builder.generate(
                    requirements=requirements,
                    phases=phases,
                    docs={
                        "prd": str(prd_file),
                        "architecture": str(arch_file),
                        "uiux": str(uiux_file),
                        "plan": str(plan_file),
                        "frontend_blueprint": str(frontend_blueprint_file),
                    },
                )
                self.console.print(f"  [green]✓[/green] 页面: {frontend_files['html']}")
                self.console.print(f"  [green]✓[/green] 样式: {frontend_files['css']}")
                self.console.print(f"  [green]✓[/green] 脚本: {frontend_files['js']}")
                frontend_runtime = self._write_frontend_runtime_validation(
                    project_dir=project_dir,
                    output_dir=output_dir,
                    project_name=project_name,
                )
                self.console.print(
                    f"  [green]✓[/green] 前端运行验证: {frontend_runtime['report_files']['markdown']}"
                )
                if frontend_runtime["preview_file"]:
                    self.console.print(f"  [green]✓[/green] 预览页: {frontend_runtime['preview_file']}")
                if not frontend_runtime["passed"]:
                    raise RuntimeError("前端运行验证未通过，当前不得进入后端与交付阶段")
                self.console.print("")
                _record_stage(
                    True,
                    details={
                        "files": frontend_files,
                        "frontend_runtime_report": frontend_runtime["report_files"]["json"],
                        "preview_file": frontend_runtime["preview_file"],
                    },
                )

            # ========== 第 4 阶段: 生成实现骨架 ==========
            _start_stage("4", "实现骨架与任务执行")
            if _should_skip_for_resume(4):
                self.console.print("[yellow]第 4 阶段: 生成前后端实现骨架 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                if not args.skip_scaffold:
                    self.console.print("[cyan]第 4 阶段: 生成前后端实现骨架...[/cyan]")
                    from .creators import ImplementationScaffoldBuilder, SpecTaskExecutor

                    frontend_runtime = self._load_frontend_runtime_validation(
                        output_dir=output_dir,
                        project_name=project_name,
                    )
                    if not frontend_runtime.get("passed", False):
                        raise RuntimeError("前端运行验证未通过，禁止进入实现骨架与后端阶段")

                    implementation_builder = ImplementationScaffoldBuilder(
                        project_dir=project_dir,
                        name=project_name,
                        frontend=args.frontend,
                        backend=args.backend,
                    )
                    scaffold_result = implementation_builder.generate(requirements=requirements)
                    self.console.print(
                        f"  [green]✓[/green] 前端骨架文件: {len(scaffold_result['frontend_files'])} 个"
                    )
                    self.console.print(
                        f"  [green]✓[/green] 后端骨架文件: {len(scaffold_result['backend_files'])} 个"
                    )
                    task_executor = SpecTaskExecutor(project_dir=project_dir, project_name=project_name)
                    task_execution_summary = task_executor.execute(
                        change_id=change_id,
                        tech_stack=tech_stack,
                        max_retries=1,
                    )
                    self.console.print(
                        f"  [green]✓[/green] Spec 任务执行: {task_execution_summary.completed_tasks}/{task_execution_summary.total_tasks}"
                    )
                    self.console.print(
                        f"  [green]✓[/green] 任务报告: {task_execution_summary.report_file}"
                    )
                    if task_execution_summary.failed_tasks:
                        self.console.print(
                            f"  [yellow]未完成任务: {', '.join(task_execution_summary.failed_tasks)}[/yellow]"
                        )
                    if task_execution_summary.repaired_actions:
                        self.console.print(
                            f"  [dim]自动修复: {len(task_execution_summary.repaired_actions)} 项[/dim]"
                        )
                    self.console.print("")
                    _record_stage(
                        True,
                        details={
                            "frontend_files": len(scaffold_result["frontend_files"]),
                            "backend_files": len(scaffold_result["backend_files"]),
                            "frontend_runtime_report": str(
                                self._frontend_runtime_report_paths(output_dir=output_dir, project_name=project_name)["json"]
                            ),
                            "task_completed": (
                                f"{task_execution_summary.completed_tasks}/{task_execution_summary.total_tasks}"
                                if task_execution_summary is not None
                                else "0/0"
                            ),
                            "task_failed_count": (
                                len(task_execution_summary.failed_tasks)
                                if task_execution_summary is not None
                                else 0
                            ),
                        },
                    )
                else:
                    self.console.print("[yellow]第 4 阶段: 生成前后端实现骨架 (跳过)[/yellow]")
                    self.console.print("")
                    _record_stage(True, details={"skipped": True})

            # ========== 第 5 阶段: 红队审查 ==========
            _start_stage("5", "红队审查")
            redteam_report = None
            if _should_skip_for_resume(5):
                self.console.print("[yellow]第 5 阶段: 红队审查 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            elif not args.skip_redteam:
                self.console.print("[cyan]第 5 阶段: 红队审查...[/cyan]")
                from .reviewers import RedTeamReviewer

                reviewer = RedTeamReviewer(
                    project_dir=project_dir,
                    name=project_name,
                    tech_stack=tech_stack
                )
                redteam_report = reviewer.review()

                # 保存红队审查报告
                redteam_file = project_dir / "output" / f"{project_name}-redteam.md"
                redteam_file.parent.mkdir(parents=True, exist_ok=True)
                redteam_file.write_text(redteam_report.to_markdown(), encoding="utf-8")

                self.console.print(f"  [green]✓[/green] 安全问题: {sum(1 for i in redteam_report.security_issues if i.severity in ('critical', 'high'))} high/critical")
                self.console.print(f"  [green]✓[/green] 性能问题: {sum(1 for i in redteam_report.performance_issues if i.severity in ('critical', 'high'))} high/critical")
                self.console.print(f"  [green]✓[/green] 架构问题: {sum(1 for i in redteam_report.architecture_issues if i.severity in ('critical', 'high'))} high/critical")
                self.console.print(f"  [green]✓[/green] 总分: {redteam_report.total_score}/100")
                self.console.print(f"  [green]✓[/green] 报告: {redteam_file}")
                self.console.print("")

                # 红队未通过时直接阻断，确保“先通过红队，再进入质量门禁”
                if not redteam_report.passed:
                    _record_stage(
                        False,
                        details={
                            "score": redteam_report.total_score,
                            "blocking_reasons": redteam_report.blocking_reasons,
                        },
                    )
                    metric_files = _finalize_metrics(
                        success=False,
                        reason="redteam_failed",
                    )
                    contract_files = _finalize_contract(success=False, reason="redteam_failed")
                    _persist_run_state(
                        "failed",
                        {
                            "failure_reason": "redteam_failed",
                            "failed_stage": "5",
                            "metrics_file": str(metric_files["json"]),
                            "contract_file": str(contract_files["json"]),
                        },
                    )
                    _flush_resume_audit(status="failed", failure_reason="redteam_failed")
                    self.console.print("[red]红队审查未通过，流水线终止[/red]")
                    for reason in redteam_report.blocking_reasons:
                        self.console.print(f"  - {reason}")
                    self.console.print("[dim]可使用 --skip-redteam 跳过该阶段（不推荐生产使用）[/dim]")
                    self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                    self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                    if resume_audit_files:
                        self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                    return 1
                _record_stage(
                    True,
                    details={
                        "score": redteam_report.total_score,
                        "critical_count": redteam_report.critical_count,
                        "high_count": redteam_report.high_count,
                    },
                )
            else:
                self.console.print("[yellow]第 5 阶段: 红队审查 (跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True})

            # ========== 第 6 阶段: 质量门禁 ==========
            _start_stage("6", "质量门禁")
            if _should_skip_for_resume(6):
                self.console.print("[yellow]第 6 阶段: 质量门禁检查 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            elif not args.skip_quality_gate:
                self.console.print("[cyan]第 6 阶段: 质量门禁检查...[/cyan]")
                from .reviewers import QualityGateChecker

                gate_checker = QualityGateChecker(
                    project_dir=project_dir,
                    name=project_name,
                    tech_stack=tech_stack,
                    scenario_override=scenario,
                    threshold_override=args.quality_threshold,
                    host_compatibility_min_score_override=pipeline_config.host_compatibility_min_score,
                    host_compatibility_min_ready_hosts_override=pipeline_config.host_compatibility_min_ready_hosts,
                )

                gate_result = gate_checker.check(redteam_report)

                # 显示场景信息
                scenario_label = "0-1 新建项目" if gate_result.scenario == "0-1" else "1-N+1 增量开发"
                self.console.print(f"  [dim]场景: {scenario_label}[/dim]")

                # 保存质量门禁报告
                gate_file = project_dir / "output" / f"{project_name}-quality-gate.md"
                gate_file.parent.mkdir(parents=True, exist_ok=True)
                gate_file.write_text(gate_result.to_markdown(), encoding="utf-8")
                if gate_checker.latest_ui_review_report is not None:
                    ui_review_file = project_dir / "output" / f"{project_name}-ui-review.md"
                    ui_review_json_file = project_dir / "output" / f"{project_name}-ui-review.json"
                    ui_review_file.write_text(
                        gate_checker.latest_ui_review_report.to_markdown(),
                        encoding="utf-8",
                    )
                    ui_review_json_file.write_text(
                        json.dumps(
                            gate_checker.latest_ui_review_report.to_dict(),
                            ensure_ascii=False,
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                status = "[green]通过[/green]" if gate_result.passed else "[red]未通过[/red]"
                self.console.print(f"  {status} 总分: {gate_result.total_score}/100")
                self.console.print(f"  [green]✓[/green] 报告: {gate_file}")
                if gate_checker.latest_ui_review_report is not None:
                    self.console.print(f"  [green]✓[/green] UI 审查: {ui_review_file}")
                    self.console.print(f"  [green]✓[/green] UI 审查 JSON: {ui_review_json_file}")
                self.console.print("")

                # 质量门禁未通过，停止流水线
                if not gate_result.passed:
                    _record_stage(
                        False,
                        details={
                            "score": gate_result.total_score,
                            "critical_failures": gate_result.critical_failures,
                        },
                    )
                    metric_files = _finalize_metrics(
                        success=False,
                        reason="quality_gate_failed",
                    )
                    contract_files = _finalize_contract(success=False, reason="quality_gate_failed")
                    _persist_run_state(
                        "failed",
                        {
                            "failure_reason": "quality_gate_failed",
                            "failed_stage": "6",
                            "metrics_file": str(metric_files["json"]),
                            "contract_file": str(contract_files["json"]),
                        },
                    )
                    _flush_resume_audit(status="failed", failure_reason="quality_gate_failed")
                    self.console.print("[red]质量门禁未通过，流水线终止[/red]")
                    self.console.print("[cyan]请修复以下问题后重新运行:[/cyan]")
                    for failure in gate_result.critical_failures:
                        self.console.print(f"  - {failure}")
                    self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                    self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                    if resume_audit_files:
                        self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                    return 1
                _record_stage(
                    True,
                    details={
                        "score": gate_result.total_score,
                        "scenario": gate_result.scenario,
                    },
                )
            else:
                self.console.print("[yellow]第 6 阶段: 质量门禁检查 (跳过)[/yellow]")
                self.console.print("[dim]提示: 使用 --skip-quality-gate 跳过了质量门禁检查，建议后续补充测试和质量检查[/dim]")
                self.console.print("")
                _record_stage(True, details={"skipped": True})

            # ========== 第 7 阶段: 代码审查指南 ==========
            _start_stage("7", "代码审查指南")
            if _should_skip_for_resume(7):
                self.console.print("[yellow]第 7 阶段: 代码审查指南 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 7 阶段: 生成代码审查指南...[/cyan]")
                from .reviewers import CodeReviewGenerator

                review_gen = CodeReviewGenerator(
                    project_dir=project_dir,
                    name=project_name,
                    tech_stack=tech_stack
                )

                review_guide = review_gen.generate()
                review_file = project_dir / "output" / f"{project_name}-code-review.md"
                review_file.write_text(review_guide, encoding="utf-8")

                self.console.print(f"  [green]✓[/green] 代码审查指南: {review_file}")
                self.console.print("")
                _record_stage(True, details={"report": str(review_file)})

            # ========== 第 8 阶段: AI 提示词 ==========
            _start_stage("8", "AI 提示词")
            if _should_skip_for_resume(8):
                self.console.print("[yellow]第 8 阶段: AI 提示词 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 8 阶段: 生成 AI 提示词...[/cyan]")
                from .creators import AIPromptGenerator

                prompt_gen = AIPromptGenerator(
                    project_dir=project_dir,
                    name=project_name
                )

                prompt_content = prompt_gen.generate()
                prompt_file = project_dir / "output" / f"{project_name}-ai-prompt.md"
                prompt_file.write_text(prompt_content, encoding="utf-8")

                self.console.print(f"  [green]✓[/green] AI 提示词: {prompt_file}")
                self.console.print("")
                _record_stage(True, details={"prompt_file": str(prompt_file)})

            # ========== 第 9 阶段: CI/CD 配置 ==========
            _start_stage("9", "CI/CD 配置")
            if _should_skip_for_resume(9):
                self.console.print("[yellow]第 9 阶段: CI/CD 配置 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print(f"[cyan]第 9 阶段: 生成 CI/CD 配置 ({args.cicd.upper()})...[/cyan]")
                from .deployers import CICDGenerator

                cicd_gen = CICDGenerator(
                    project_dir=project_dir,
                    name=project_name,
                    tech_stack=tech_stack,
                    platform=self._normalize_cicd_platform(args.cicd)
                )

                cicd_files = cicd_gen.generate()

                for file_path, content in cicd_files.items():
                    full_path = project_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content, encoding="utf-8")
                    self.console.print(f"  [green]✓[/green] {file_path}")

                self.console.print("")
                _record_stage(True, details={"generated_files": len(cicd_files)})

            # ========== 第 10 阶段: 部署修复模板 ==========
            _start_stage("10", "部署修复模板")
            if _should_skip_for_resume(10):
                self.console.print("[yellow]第 10 阶段: 部署修复模板 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 10 阶段: 生成部署修复模板...[/cyan]")
                remediation_outputs = self._export_deploy_remediation_templates(
                    project_dir=project_dir,
                    cicd_platform=args.cicd,
                    only_missing=True,
                )
                self.console.print(f"  [green]✓[/green] 环境模板: {remediation_outputs['env_file']}")
                self.console.print(f"  [green]✓[/green] 检查清单: {remediation_outputs['checklist_file']}")
                self.console.print(f"  [dim]缺失变量条目: {remediation_outputs['items_count']}[/dim]")
                if remediation_outputs.get("per_platform_files"):
                    self.console.print(f"  [green]✓[/green] 平台拆分模板: {len(remediation_outputs['per_platform_files'])} 组")
                self.console.print("")
                _record_stage(
                    True,
                    details={
                        "items_count": remediation_outputs["items_count"],
                        "per_platform_groups": len(remediation_outputs.get("per_platform_files") or []),
                    },
                )

            # ========== 第 11 阶段: 数据库迁移 + 项目交付包 ==========
            _start_stage("11", "迁移与交付")
            if _should_skip_for_resume(11):
                self.console.print("[yellow]第 11 阶段: 迁移与交付 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 11 阶段: 生成数据库迁移脚本 + 项目交付包...[/cyan]")
                from .deployers import DeliveryPackager, MigrationGenerator

                migration_gen = MigrationGenerator(
                    project_dir=project_dir,
                    name=project_name,
                    tech_stack=tech_stack
                )

                migration_files = migration_gen.generate()

                for file_path, content in migration_files.items():
                    full_path = project_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content, encoding="utf-8")
                    self.console.print(f"  [green]✓[/green] {file_path}")

                packager = DeliveryPackager(
                    project_dir=project_dir,
                    name=project_name,
                    version=__version__,
                )
                delivery_outputs = packager.package(cicd_platform=args.cicd)
                missing_required_raw = delivery_outputs.get("missing_required_count", 0)
                missing_required_count = missing_required_raw if isinstance(missing_required_raw, int) else 0
                self.console.print(f"  [green]✓[/green] 清单: {delivery_outputs['manifest_file']}")
                self.console.print(f"  [green]✓[/green] 报告: {delivery_outputs['report_file']}")
                self.console.print(f"  [green]✓[/green] 交付包: {delivery_outputs['archive_file']}")
                self.console.print(
                    f"  [dim]状态: {delivery_outputs['status']} | 缺失必需项: {missing_required_count}[/dim]"
                )
                if missing_required_count > 0:
                    self.console.print("[red]  交付包标记为 incomplete，当前不得进入发布演练验证[/red]")
                    _record_stage(
                        False,
                        details={
                            "migration_files": len(migration_files),
                            "delivery_status": delivery_outputs["status"],
                            "delivery_missing_required_count": missing_required_count,
                        },
                    )
                    metric_files = _finalize_metrics(success=False, reason="delivery_packaging_incomplete")
                    contract_files = _finalize_contract(success=False, reason="delivery_packaging_incomplete")
                    _persist_run_state(
                        "failed",
                        {
                            "failure_reason": "delivery_packaging_incomplete",
                            "failed_stage": "11",
                            "metrics_file": str(metric_files["json"]),
                            "contract_file": str(contract_files["json"]),
                        },
                    )
                    _flush_resume_audit(status="failed", failure_reason="delivery_packaging_incomplete")
                    self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                    self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                    if resume_audit_files:
                        self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                    return 1
                self.console.print("")
                _record_stage(
                    True,
                    details={
                        "migration_files": len(migration_files),
                        "delivery_status": delivery_outputs["status"],
                        "delivery_missing_required_count": missing_required_count,
                    },
                )

            # ========== 第 12 阶段: 发布演练验证 ==========
            _start_stage("12", "发布演练验证")
            self.console.print("[cyan]第 12 阶段: 发布演练文档与验证...[/cyan]")
            from .deployers import LaunchRehearsalGenerator, LaunchRehearsalRunner

            rehearsal_generator = LaunchRehearsalGenerator(
                project_dir=project_dir,
                name=project_name,
                tech_stack=tech_stack,
            )
            rehearsal_files = rehearsal_generator.generate(cicd_platform=args.cicd or "github")
            for relative_path, content in rehearsal_files.items():
                full_path = project_dir / relative_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                self.console.print(f"  [green]✓[/green] {relative_path}")

            if args.skip_rehearsal_verify:
                self.console.print("[yellow]发布演练验证已跳过（--skip-rehearsal-verify）[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "skip-rehearsal-verify"})
            elif args.skip_redteam or args.skip_quality_gate:
                self.console.print("[yellow]检测到上游门禁被跳过，发布演练验证自动跳过[/yellow]")
                self.console.print("[dim]提示: 建议在不跳过红队/质量门禁时执行完整发布演练[/dim]")
                self.console.print("")
                _record_stage(
                    True,
                    details={
                        "skipped": True,
                        "reason": "prerequisite_skipped",
                        "skip_redteam": bool(args.skip_redteam),
                        "skip_quality_gate": bool(args.skip_quality_gate),
                    },
                )
            else:
                metrics_snapshot_file = _write_metrics_snapshot()
                runner = LaunchRehearsalRunner(
                    project_dir=project_dir,
                    project_name=project_name,
                    cicd_platform=args.cicd or "github",
                )
                rehearsal_result = runner.run()
                rehearsal_reports = runner.write(rehearsal_result)
                status = "[green]通过[/green]" if rehearsal_result.passed else "[red]未通过[/red]"
                self.console.print(f"  {status} 分数: {rehearsal_result.score}/100")
                self.console.print(f"  [green]✓[/green] 报告: {rehearsal_reports['markdown']}")
                self.console.print(f"  [green]✓[/green] 数据: {rehearsal_reports['json']}")
                self.console.print(f"  [dim]指标快照: {metrics_snapshot_file}[/dim]")
                self.console.print("")

                if not rehearsal_result.passed:
                    _record_stage(
                        False,
                        details={
                            "score": rehearsal_result.score,
                            "failed_checks": [check.name for check in rehearsal_result.failed_checks],
                        },
                    )
                    metric_files = _finalize_metrics(success=False, reason="rehearsal_failed")
                    contract_files = _finalize_contract(success=False, reason="rehearsal_failed")
                    _persist_run_state(
                        "failed",
                        {
                            "failure_reason": "rehearsal_failed",
                            "failed_stage": "12",
                            "metrics_file": str(metric_files["json"]),
                            "contract_file": str(contract_files["json"]),
                        },
                    )
                    _flush_resume_audit(status="failed", failure_reason="rehearsal_failed")
                    self.console.print("[red]发布演练验证未通过，流水线终止[/red]")
                    for check in rehearsal_result.failed_checks:
                        self.console.print(f"  - {check.name}: {check.detail}")
                    self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
                    self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
                    if resume_audit_files:
                        self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
                    return 1

                _record_stage(
                    True,
                    details={
                        "score": rehearsal_result.score,
                        "failed_checks": len(rehearsal_result.failed_checks),
                    },
                )

            metric_files = _finalize_metrics(success=True)
            contract_files = _finalize_contract(success=True)

            # ========== 完成 ==========
            self.console.print(f"[cyan]{'=' * 60}[/cyan]")
            self.console.print("[green]✓ 流水线完成！[/green]")
            self.console.print(f"[cyan]{'=' * 60}[/cyan]")
            self.console.print("")
            self.console.print("[cyan]生成的文件:[/cyan]")
            self.console.print("  文档:")
            self.console.print(f"    - 需求增强报告: output/{project_name}-research.md")
            self.console.print(f"    - PRD: output/{project_name}-prd.md")
            self.console.print(f"    - 架构: output/{project_name}-architecture.md")
            self.console.print(f"    - UI/UX: output/{project_name}-uiux.md")
            self.console.print(f"    - 执行路线图: output/{project_name}-execution-plan.md")
            self.console.print(f"    - 前端蓝图: output/{project_name}-frontend-blueprint.md")
            if not args.skip_redteam:
                self.console.print(f"    - 红队审查: output/{project_name}-redteam.md")
            if not args.skip_quality_gate:
                self.console.print(f"    - 质量门禁: output/{project_name}-quality-gate.md")
            self.console.print(f"    - 代码审查: output/{project_name}-code-review.md")
            self.console.print(f"    - AI 提示词: output/{project_name}-ai-prompt.md")
            self.console.print("")
            self.console.print("  前端演示:")
            self.console.print("    - output/frontend/index.html")
            self.console.print("    - output/frontend/styles.css")
            self.console.print("    - output/frontend/app.js")
            self.console.print("")
            if not args.skip_scaffold:
                self.console.print("  实现骨架:")
                self.console.print("    - frontend/src/*")
                self.console.print("    - backend/src/*")
                self.console.print("    - backend/API_CONTRACT.md")
                self.console.print("    - backend/migrations/*.sql")
                if task_execution_summary is not None:
                    self.console.print(
                        f"    - {Path(str(task_execution_summary.report_file)).relative_to(project_dir)}"
                    )
                self.console.print("")
            self.console.print("  CI/CD:")
            for file_path in cicd_files.keys():
                self.console.print(f"    - {file_path}")
            self.console.print("")
            self.console.print("  部署修复模板:")
            self.console.print(f"    - {Path(remediation_outputs['env_file']).name}")
            self.console.print(f"    - {Path(remediation_outputs['checklist_file']).relative_to(project_dir)}")
            per_platform_files = remediation_outputs.get("per_platform_files")
            if isinstance(per_platform_files, list):
                for item in per_platform_files:
                    if not isinstance(item, dict):
                        continue
                    checklist_file = item.get("checklist_file")
                    if isinstance(checklist_file, str):
                        self.console.print(
                            f"    - {Path(checklist_file).relative_to(project_dir)}"
                        )
                    env_file = item.get("env_file")
                    if isinstance(env_file, str):
                        self.console.print(
                            f"    - {Path(env_file).relative_to(project_dir)}"
                        )
            self.console.print("")
            self.console.print("  数据库迁移:")
            for file_path in migration_files.keys():
                self.console.print(f"    - {file_path}")
            self.console.print("")
            self.console.print("  项目交付包:")
            self.console.print(
                f"    - {Path(str(delivery_outputs['manifest_file'])).relative_to(project_dir)}"
            )
            self.console.print(
                f"    - {Path(str(delivery_outputs['report_file'])).relative_to(project_dir)}"
            )
            self.console.print(
                f"    - {Path(str(delivery_outputs['archive_file'])).relative_to(project_dir)}"
            )
            self.console.print("")
            self.console.print("  发布演练:")
            self.console.print(f"    - output/rehearsal/{project_name}-launch-rehearsal.md")
            self.console.print(f"    - output/rehearsal/{project_name}-rollback-playbook.md")
            self.console.print(f"    - output/rehearsal/{project_name}-smoke-checklist.md")
            if not args.skip_rehearsal_verify and not args.skip_redteam and not args.skip_quality_gate:
                self.console.print(f"    - output/rehearsal/{project_name}-rehearsal-report.md")
                self.console.print(f"    - output/rehearsal/{project_name}-rehearsal-report.json")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print("  1. 打开 output/frontend/index.html 评审前端骨架")
            self.console.print("  2. 对照执行路线图按阶段推进开发")
            self.console.print("  3. 使用代码审查指南进行评审和修复")
            self.console.print("  4. 配置 CI/CD 平台 (设置 secrets/credentials)")
            self.console.print("  5. 运行数据库迁移脚本并推送代码触发流水线")
            self.console.print("  6. 执行并保存发布演练报告用于上线审批")
            self.console.print("  7. 使用 output/delivery/* 作为对外交付包")
            self.console.print(f"  8. 查看 pipeline 指标: output/{project_name}-pipeline-metrics.md")
            self.console.print("")
            self.console.print("[cyan]可观测性:[/cyan]")
            self.console.print(f"  - 指标 JSON: {metric_files['json']}")
            self.console.print(f"  - 指标 Markdown: {metric_files['markdown']}")
            self.console.print(f"  - 契约 JSON: {contract_files['json']}")
            self.console.print(f"  - 契约 Markdown: {contract_files['markdown']}")
            if "history_json" in metric_files:
                self.console.print(f"  - 历史 JSON: {metric_files['history_json']}")
            if "history_markdown" in metric_files:
                self.console.print(f"  - 历史 Markdown: {metric_files['history_markdown']}")
            self.console.print("")
            _persist_run_state(
                "success",
                {
                    "metrics_file": str(metric_files["json"]),
                    "contract_file": str(contract_files["json"]),
                },
            )
            _flush_resume_audit(status="success")
            if resume_audit_files:
                self.console.print("[cyan]恢复审计:[/cyan]")
                self.console.print(f"  - JSON: {resume_audit_files['json']}")
                self.console.print(f"  - Markdown: {resume_audit_files['markdown']}")
                self.console.print("")

        except Exception as e:
            _record_stage(False, details={"error": str(e)})
            metric_files = _finalize_metrics(success=False, reason=str(e))
            contract_files = _finalize_contract(success=False, reason=str(e))
            failed_stage_label = current_stage or "unknown"
            _persist_run_state(
                "failed",
                {
                    "failure_reason": str(e),
                    "failed_stage": failed_stage_label,
                    "metrics_file": str(metric_files["json"]),
                    "contract_file": str(contract_files["json"]),
                },
            )
            _flush_resume_audit(status="failed", failure_reason=str(e))
            self.console.print(f"[red]流水线失败: {e}[/red]")
            import traceback
            self.console.print(traceback.format_exc())
            self.console.print(f"[dim]指标报告: {metric_files['json']}[/dim]")
            self.console.print(f"[dim]契约审计: {contract_files['markdown']}[/dim]")
            if resume_audit_files:
                self.console.print(f"[dim]恢复审计: {resume_audit_files['markdown']}[/dim]")
            return 1

        return 0

    def _cmd_config(self, args) -> int:
        """配置管理"""
        config_manager = get_config_manager()

        if not config_manager.exists():
            self.console.print("[red]未找到项目配置[/red]")
            return 1

        if args.action == "list":
            # 列出所有配置
            config = config_manager.config
            self.console.print("[cyan]项目配置:[/cyan]")
            for key, value in config.__dict__.items():
                if not key.startswith("_"):
                    self.console.print(f"  {key}: {value}")

        elif args.action == "get":
            if not args.key:
                self.console.print("[red]请指定配置键[/red]")
                return 1
            value = config_manager.get(args.key)
            self.console.print(f"{args.key}: {value}")

        elif args.action == "set":
            if not args.key or not args.value:
                self.console.print("[red]请指定配置键和值[/red]")
                return 1
            valid_keys = {
                key for key in ProjectConfig.__dataclass_fields__.keys()  # type: ignore[attr-defined]
                if not key.startswith("_")
            }
            if args.key not in valid_keys:
                self.console.print(f"[red]未知配置键: {args.key}[/red]")
                self.console.print(f"[dim]可用配置键: {', '.join(sorted(valid_keys))}[/dim]")
                return 1
            try:
                updated = config_manager.update(**{args.key: args.value})
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")
                return 1
            actual = getattr(updated, args.key, args.value)
            self.console.print(f"[green]✓[/green] {args.key} = {actual}")

        return 0

    def _cmd_skill(self, args) -> int:
        """Skill 管理"""
        from .skills import SkillManager

        manager = SkillManager(Path.cwd())

        if args.action == "targets":
            self.console.print("[cyan]支持的 Skill 目标平台:[/cyan]")
            for target in manager.list_targets():
                self.console.print(f"  - {target}")
            return 0

        if args.action == "list":
            installed = manager.list_installed(args.target)
            if not installed:
                self.console.print(f"[dim]{args.target} 未安装任何 skill[/dim]")
                return 0

            self.console.print(f"[cyan]{args.target} 已安装 skill:[/cyan]")
            for skill_name in installed:
                self.console.print(f"  - {skill_name}")
            return 0

        if args.action == "install":
            if not args.source_or_name:
                self.console.print("[red]请提供 skill 来源（目录/git/super-dev）[/red]")
                return 1

            try:
                result = manager.install(
                    source=args.source_or_name,
                    target=args.target,
                    name=args.name,
                    force=args.force,
                )
            except Exception as e:
                self.console.print(f"[red]Skill 安装失败: {e}[/red]")
                return 1

            self.console.print("[green]✓ Skill 安装成功[/green]")
            self.console.print(f"  名称: {result.name}")
            self.console.print(f"  目标: {result.target}")
            self.console.print(f"  路径: {result.path}")
            self.console.print(f"  来源: {result.source}")
            return 0

        if args.action == "uninstall":
            if not args.source_or_name:
                self.console.print("[red]请提供要卸载的 skill 名称[/red]")
                return 1

            try:
                removed_path = manager.uninstall(args.source_or_name, args.target)
            except Exception as e:
                self.console.print(f"[red]Skill 卸载失败: {e}[/red]")
                return 1

            self.console.print("[green]✓ Skill 已卸载[/green]")
            self.console.print(f"  路径: {removed_path}")
            return 0

        self.console.print("[yellow]未知 skill 操作[/yellow]")
        return 1

    def _cmd_integrate(self, args) -> int:
        """多平台集成配置"""
        from .integrations import IntegrationManager

        manager = IntegrationManager(Path.cwd())

        if args.action == "list":
            self.console.print("[cyan]支持的集成平台:[/cyan]")
            for target in manager.list_targets():
                self.console.print(f"  - {target.name}: {target.description}")
            return 0

        if args.action == "setup":
            if args.all:
                results = manager.setup_all(force=args.force)
                self.console.print("[green]✓ 已完成所有平台集成配置[/green]")
                for platform, files in results.items():
                    if not files:
                        self.console.print(f"  {platform}: [dim]无变更[/dim]")
                        continue
                    self.console.print(f"  {platform}:")
                    for file_path in files:
                        self.console.print(f"    - {file_path}")
                return 0

            if not args.target:
                self.console.print("[red]请通过 --target 指定平台，或使用 --all[/red]")
                return 1

            files = manager.setup(args.target, force=args.force)
            if not files:
                self.console.print("[yellow]配置已存在，无需修改（可加 --force 覆盖）[/yellow]")
                return 0

            self.console.print("[green]✓ 集成配置已生成[/green]")
            for file_path in files:
                self.console.print(f"  - {file_path}")
            return 0

        if args.action == "harden":
            from .skills import SkillManager

            project_dir = Path.cwd()
            available_targets = [item.name for item in manager.list_targets()]
            detected_meta: dict[str, list[str]] = {}
            if args.target:
                targets = [args.target]
            elif args.all:
                targets = available_targets
            else:
                targets, detected_meta = self._detect_host_targets(available_targets=available_targets)
                if not targets:
                    targets = available_targets
            hardening_results: dict[str, Any] = {}
            skill_manager = SkillManager(project_dir)
            official_compare_enabled = bool(getattr(args, "official_compare", False)) or True
            usage_profiles: dict[str, dict[str, Any]] = {}
            for target in targets:
                profile = manager.get_adapter_profile(target)
                plan = manager.host_hardening_blueprint(target)
                usage_profiles[target] = self._build_host_usage_profile(
                    integration_manager=manager,
                    target=target,
                )
                written_files = [str(path) for path in manager.setup(target=target, force=True)]
                slash_file = manager.setup_slash_command(target=target, force=True)
                if slash_file is not None:
                    written_files.append(str(slash_file))
                global_protocol = manager.setup_global_protocol(target=target, force=True)
                if global_protocol is not None:
                    written_files.append(str(global_protocol))
                global_slash = manager.setup_global_slash_command(target=target, force=True)
                if global_slash is not None:
                    written_files.append(str(global_slash))
                skill_install: dict[str, Any] = {"required": manager.requires_skill(target), "installed": False}
                if manager.requires_skill(target):
                    try:
                        skill_path = skill_manager.install(
                            source="super-dev",
                            target=target,
                            name="super-dev-core",
                            force=True,
                        ).path
                        skill_install = {
                            "required": True,
                            "installed": True,
                            "path": str(skill_path),
                        }
                    except Exception as exc:
                        skill_install = {
                            "required": True,
                            "installed": False,
                            "error": str(exc),
                        }
                docs_check = manager.verify_official_docs(target) if bool(getattr(args, "verify_docs", False)) else {}
                official_compare = (
                    manager.compare_official_capabilities(target, timeout_seconds=8.0)
                    if official_compare_enabled
                    else {}
                )
                hardening_results[target] = {
                    "host": target,
                    "category": profile.category,
                    "adapter_mode": profile.adapter_mode,
                    "plan": plan,
                    "written_files": written_files,
                    "skill_install": skill_install,
                    "contract": {},
                    "docs_check": docs_check,
                    "official_compare": official_compare,
                }
            report = self._collect_host_diagnostics(
                project_dir=project_dir,
                targets=targets,
                skill_name="super-dev-core",
                check_integrate=True,
                check_skill=True,
                check_slash=True,
            )
            compatibility = self._build_compatibility_summary(
                report=report,
                targets=targets,
                check_integrate=True,
                check_skill=True,
                check_slash=True,
            )
            hosts_report = report.get("hosts", {}) if isinstance(report, dict) else {}
            if isinstance(hosts_report, dict):
                for target in targets:
                    host_info = hosts_report.get(target, {})
                    checks = host_info.get("checks", {}) if isinstance(host_info, dict) else {}
                    contract = checks.get("contract", {}) if isinstance(checks, dict) else {}
                    item = hardening_results.get(target, {})
                    if isinstance(item, dict):
                        item["contract"] = contract if isinstance(contract, dict) else {}
            payload = {
                "project_dir": str(project_dir),
                "detected_hosts": targets if not detected_meta else list(detected_meta.keys()),
                "detection_details": detected_meta,
                "selected_targets": targets,
                "hardening_results": hardening_results,
                "report": report,
                "compatibility": compatibility,
                "usage_profiles": usage_profiles,
            }
            official_compare_summary = self._build_official_compare_summary(hardening_results=hardening_results)
            host_parity_summary = self._build_host_parity_summary(usage_profiles=usage_profiles)
            host_gate_summary = self._build_host_gate_summary(report=report, targets=targets)
            host_runtime_script_summary = self._build_host_runtime_script_summary(usage_profiles=usage_profiles)
            host_recovery_summary = self._build_host_recovery_summary(
                targets=targets,
                usage_profiles=usage_profiles,
            )
            payload["official_compare_summary"] = official_compare_summary
            payload["host_parity_summary"] = host_parity_summary
            payload["host_gate_summary"] = host_gate_summary
            payload["host_runtime_script_summary"] = host_runtime_script_summary
            payload["host_recovery_summary"] = host_recovery_summary
            parity_index = self._build_host_parity_index(
                threshold=float(getattr(args, "parity_threshold", 95.0)),
                official_compare_summary=official_compare_summary,
                host_parity_summary=host_parity_summary,
                host_gate_summary=host_gate_summary,
                host_runtime_script_summary=host_runtime_script_summary,
                host_recovery_summary=host_recovery_summary,
                compatibility=compatibility,
            )
            payload["host_parity_index"] = parity_index
            if not bool(args.no_save):
                report_files = self._write_host_hardening_report(project_dir=project_dir, payload=payload)
                payload["report_files"] = {name: str(path) for name, path in report_files.items()}
            if args.json:
                sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
                return 0 if bool(report.get("overall_ready", False)) and bool(parity_index.get("passed", False)) else 1

            self.console.print("[cyan]Super Dev 宿主系统级深适配[/cyan]")
            self.console.print(f"[dim]项目目录: {project_dir}[/dim]")
            self.console.print(
                f"[cyan]兼容性评分: {compatibility['overall_score']:.2f}/100 "
                f"(ready {compatibility['ready_hosts']}/{compatibility['total_hosts']})[/cyan]"
            )
            self.console.print(
                f"[cyan]流程一致性: {compatibility.get('flow_consistency_score', 0):.2f}/100 "
                f"({compatibility.get('flow_consistent_hosts', 0)}/{compatibility.get('total_hosts', 0)})[/cyan]"
            )
            self.console.print(
                f"[cyan]官方文档对照: {official_compare_summary.get('score', 0):.2f}/100 "
                f"({official_compare_summary.get('passed', 0)}/{official_compare_summary.get('total', 0)})[/cyan]"
            )
            self.console.print(
                f"[cyan]宿主体验一致性: {host_parity_summary.get('score', 0):.2f}/100 "
                f"({host_parity_summary.get('passed', 0)}/{host_parity_summary.get('total', 0)})[/cyan]"
            )
            self.console.print(
                f"[cyan]确认门禁一致性: {host_gate_summary.get('score', 0):.2f}/100 "
                f"({host_gate_summary.get('passed', 0)}/{host_gate_summary.get('total', 0)})[/cyan]"
            )
            self.console.print(
                f"[cyan]真人验收脚本一致性: {host_runtime_script_summary.get('score', 0):.2f}/100 "
                f"({host_runtime_script_summary.get('passed', 0)}/{host_runtime_script_summary.get('total', 0)})[/cyan]"
            )
            self.console.print(
                f"[cyan]失败恢复一致性: {host_recovery_summary.get('score', 0):.2f}/100 "
                f"({host_recovery_summary.get('passed', 0)}/{host_recovery_summary.get('total', 0)})[/cyan]"
            )
            self.console.print(
                f"[cyan]Host Parity Index: {parity_index.get('score', 0):.2f}/100 "
                f"(threshold {parity_index.get('threshold', 95.0):.2f}, "
                f"{'pass' if bool(parity_index.get('passed', False)) else 'fail'})[/cyan]"
            )
            for target in targets:
                item = hardening_results.get(target, {})
                contract = item.get("contract", {})
                ok = bool((contract or {}).get("ok", False))
                self.console.print("")
                self.console.print(
                    f"[cyan]- {target}[/cyan] "
                    f"{'[green]contract ok[/green]' if ok else '[yellow]needs review[/yellow]'}"
                )
                written_files = item.get("written_files", [])
                if isinstance(written_files, list) and written_files:
                    self.console.print("  已更新:")
                    for file_path in written_files:
                        self.console.print(f"    - {file_path}")
                skill_install = item.get("skill_install", {})
                if isinstance(skill_install, dict) and bool(skill_install.get("required", False)):
                    if bool(skill_install.get("installed", False)):
                        self.console.print(f"  Skill 安装: [green]ok[/green] ({skill_install.get('path', '-')})")
                    else:
                        self.console.print(f"  Skill 安装: [yellow]failed[/yellow] ({skill_install.get('error', '-')})")
                docs_check = item.get("docs_check", {})
                if isinstance(docs_check, dict) and docs_check:
                    self.console.print(
                        f"  文档在线核验: {docs_check.get('status', 'unknown')} "
                        f"({docs_check.get('reachable', 0)}/{docs_check.get('checked', 0)})"
                    )
                official_compares = payload.get("official_compares", {})
                if isinstance(official_compares, dict):
                    compare = official_compares.get(target, {})
                    if isinstance(compare, dict) and compare:
                        self.console.print(
                            f"  官方对照: {compare.get('status', 'unknown')} "
                            f"({compare.get('reachable_urls', 0)}/{compare.get('checked_urls', 0)})"
                        )
                official_compare = item.get("official_compare", {})
                if isinstance(official_compare, dict) and official_compare:
                    self.console.print(
                        f"  官方对照: {official_compare.get('status', 'unknown')} "
                        f"({official_compare.get('reachable_urls', 0)}/{official_compare.get('checked_urls', 0)})"
                    )
                invalid = (contract or {}).get("invalid_surfaces", {})
                if isinstance(invalid, dict) and invalid:
                    self.console.print("  [yellow]仍有不一致面[/yellow]:")
                    for surface_key in invalid.keys():
                        self.console.print(f"    - {surface_key}")
                else:
                    self.console.print("  [green]✓[/green] 接入面已与系统流程契约对齐")
            if "report_files" in payload:
                report_files = payload["report_files"]
                if isinstance(report_files, dict):
                    self.console.print("")
                    self.console.print("[cyan]深适配报告[/cyan]")
                    for name, path in report_files.items():
                        self.console.print(f"  - {name}: {path}")
            return 0 if bool(report.get("overall_ready", False)) and bool(parity_index.get("passed", False)) else 1

        if args.action == "matrix":
            targets: list[str] | None = [args.target] if args.target else None
            profiles = manager.list_adapter_profiles(targets=targets)
            docs_checks: dict[str, Any] = {}
            official_compares: dict[str, Any] = {}
            if bool(getattr(args, "verify_docs", False)):
                for profile in profiles:
                    docs_checks[profile.host] = manager.verify_official_docs(profile.host)
            if bool(getattr(args, "official_compare", False)):
                for profile in profiles:
                    official_compares[profile.host] = manager.compare_official_capabilities(profile.host)
            if args.json:
                payload = {
                    "profiles": [profile.to_dict() for profile in profiles],
                    "docs_checks": docs_checks,
                    "official_compares": official_compares,
                }
                sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
                return 0

            self.console.print("[cyan]Super Dev 宿主适配矩阵[/cyan]")
            verified_count = sum(1 for item in profiles if item.docs_verified)
            self.console.print(
                f"[dim]官方文档核验: {verified_count}/{len(profiles)}[/dim]"
            )
            for profile in profiles:
                self.console.print(f"[cyan]- {profile.host} ({profile.category})[/cyan]")
                self.console.print(f"  适配模式: {profile.adapter_mode}")
                self.console.print(f"  使用模式: {profile.usage_mode}")
                self.console.print(f"  模型提供方: {profile.host_model_provider}")
                docs_badge = "verified" if profile.docs_verified else "pending"
                docs_url = profile.official_docs_url or "-"
                self.console.print(f"  官方文档: {docs_url} ({docs_badge})")
                if profile.official_docs_references:
                    self.console.print(f"  官方参考: {len(profile.official_docs_references)} 条")
                labels = profile.capability_labels or {}
                capability_summary = ", ".join(f"{key}={value}" for key, value in labels.items()) if labels else "-"
                self.console.print(f"  能力标签: {capability_summary}")
                if profile.host in docs_checks:
                    docs_check = docs_checks[profile.host]
                    self.console.print(
                        f"  文档在线核验: {docs_check.get('status', 'unknown')} "
                        f"({docs_check.get('reachable', 0)}/{docs_check.get('checked', 0)})"
                    )
                if profile.host in official_compares:
                    compare = official_compares[profile.host]
                    self.console.print(
                        f"  官方对照: {compare.get('status', 'unknown')} "
                        f"({compare.get('reachable_urls', 0)}/{compare.get('checked_urls', 0)})"
                    )
                self.console.print(f"  主入口: {profile.primary_entry}")
                self.console.print(f"  触发命令: {profile.trigger_command}")
                self.console.print(f"  触发上下文: {profile.trigger_context}")
                self.console.print(f"  触发位置: {profile.usage_location}")
                self.console.print(f"  终端入口: {profile.terminal_entry}")
                self.console.print(f"  终端范围: {profile.terminal_entry_scope}")
                self.console.print(
                    f"  接入后重启: {'是' if profile.requires_restart_after_onboard else '否'}"
                )
                self.console.print(f"  规则文件: {', '.join(profile.integration_files)}")
                self.console.print(f"  Slash 文件: {profile.slash_command_file}")
                self.console.print(f"  Skill 目录: {profile.skill_dir}")
                commands = ", ".join(profile.detection_commands) if profile.detection_commands else "-"
                paths = ", ".join(profile.detection_paths) if profile.detection_paths else "-"
                self.console.print(f"  探测命令: {commands}")
                self.console.print(f"  探测路径: {paths}")
                if profile.post_onboard_steps:
                    self.console.print("  接入后步骤:")
                    for step in profile.post_onboard_steps:
                        self.console.print(f"    - {step}")
                if profile.usage_notes:
                    self.console.print("  使用提示:")
                    for note in profile.usage_notes:
                        self.console.print(f"    - {note}")
                self.console.print(f"  Smoke Prompt: {profile.smoke_test_prompt}")
                self.console.print(f"  Smoke Signal: {profile.smoke_success_signal}")
                self.console.print(f"  备注: {profile.notes}")
            return 0

        if args.action == "smoke":
            targets: list[str] = [args.target] if args.target else [item.name for item in manager.list_targets()]
            profiles = manager.list_adapter_profiles(targets=targets)
            if args.json:
                payload = [
                    {
                        "host": profile.host,
                        "final_trigger": str(profile.trigger_command).replace("<需求描述>", "你的需求"),
                        "smoke_test_prompt": profile.smoke_test_prompt,
                        "smoke_test_steps": list(profile.smoke_test_steps),
                        "smoke_success_signal": profile.smoke_success_signal,
                    }
                    for profile in profiles
                ]
                sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
                return 0

            self.console.print("[cyan]Super Dev 宿主 Smoke 验收[/cyan]")
            for profile in profiles:
                self.console.print(f"[cyan]- {profile.host}[/cyan]")
                self.console.print(
                    f"  最终输入: {str(profile.trigger_command).replace('<需求描述>', '你的需求')}"
                )
                self.console.print(f"  验收语句: {profile.smoke_test_prompt}")
                self.console.print("  验收步骤:")
                for step in profile.smoke_test_steps:
                    self.console.print(f"    - {step}")
                self.console.print(f"  通过标准: {profile.smoke_success_signal}")
            return 0

        if args.action == "audit":
            project_dir = Path.cwd()
            available_targets = [item.name for item in manager.list_targets()]
            targets: list[str]
            detected_meta: dict[str, list[str]] = {}
            if args.target:
                targets = [args.target]
            elif args.all:
                targets = available_targets
            else:
                targets, detected_meta = self._detect_host_targets(available_targets=available_targets)
                if not targets:
                    targets = available_targets

            report = self._collect_host_diagnostics(
                project_dir=project_dir,
                targets=targets,
                skill_name="super-dev-core",
                check_integrate=True,
                check_skill=True,
                check_slash=True,
            )
            repair_actions: dict[str, dict[str, str]] = {}
            if args.repair:
                repair_actions = self._repair_host_diagnostics(
                    project_dir=project_dir,
                    report=report,
                    skill_name="super-dev-core",
                    force=bool(args.force),
                    check_integrate=True,
                    check_skill=True,
                    check_slash=True,
                )
                report = self._collect_host_diagnostics(
                    project_dir=project_dir,
                    targets=targets,
                    skill_name="super-dev-core",
                    check_integrate=True,
                    check_skill=True,
                    check_slash=True,
                )

            compatibility = self._build_compatibility_summary(
                report=report,
                targets=targets,
                check_integrate=True,
                check_skill=True,
                check_slash=True,
            )
            usage_profiles = {
                target: self._build_host_usage_profile(
                    integration_manager=manager,
                    target=target,
                )
                for target in targets
            }
            payload = {
                "project_dir": str(project_dir),
                "detected_hosts": targets if not detected_meta else list(detected_meta.keys()),
                "detection_details": detected_meta,
                "selected_targets": targets,
                "report": report,
                "compatibility": compatibility,
                "usage_profiles": usage_profiles,
                "repair_actions": repair_actions,
            }
            payload["host_parity_summary"] = self._build_host_parity_summary(usage_profiles=usage_profiles)
            payload["host_gate_summary"] = self._build_host_gate_summary(report=report, targets=targets)
            payload["host_runtime_script_summary"] = self._build_host_runtime_script_summary(usage_profiles=usage_profiles)
            payload["host_recovery_summary"] = self._build_host_recovery_summary(
                targets=targets,
                usage_profiles=usage_profiles,
            )
            if bool(getattr(args, "verify_docs", False)):
                payload["docs_checks"] = {
                    target: manager.verify_official_docs(target)
                    for target in targets
                }
            if bool(getattr(args, "official_compare", False)):
                official_compares = {
                    target: manager.compare_official_capabilities(target, timeout_seconds=8.0)
                    for target in targets
                }
                payload["official_compares"] = official_compares
                payload["official_compare_summary"] = self._build_official_compare_summary(
                    hardening_results={
                        target: {"official_compare": official_compares.get(target, {})}
                        for target in targets
                    }
                )
            payload["host_parity_index"] = self._build_host_parity_index(
                threshold=float(getattr(args, "parity_threshold", 95.0)),
                official_compare_summary=payload.get("official_compare_summary", {}),
                host_parity_summary=payload.get("host_parity_summary", {}),
                host_gate_summary=payload.get("host_gate_summary", {}),
                host_runtime_script_summary=payload.get("host_runtime_script_summary", {}),
                host_recovery_summary=payload.get("host_recovery_summary", {}),
                compatibility=compatibility,
            )
            if not bool(args.no_save):
                report_files = self._write_host_surface_audit_report(project_dir=project_dir, payload=payload)
                payload["report_files"] = {name: str(path) for name, path in report_files.items()}

            if args.json:
                sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
                parity_index = payload.get("host_parity_index", {})
                return 0 if bool(report.get("overall_ready", False)) and bool((parity_index or {}).get("passed", False)) else 1

            self.console.print("[cyan]Super Dev 宿主 Surface 审计[/cyan]")
            self.console.print(f"[dim]项目目录: {project_dir}[/dim]")
            if detected_meta:
                self.console.print(
                    f"[cyan]自动检测到 {len(detected_meta)} 个宿主：{', '.join(detected_meta)}[/cyan]"
                )
            self.console.print(
                f"[cyan]兼容性评分: {compatibility['overall_score']:.2f}/100 "
                f"(ready {compatibility['ready_hosts']}/{compatibility['total_hosts']})[/cyan]"
            )
            self.console.print(
                f"[cyan]流程一致性: {compatibility.get('flow_consistency_score', 0):.2f}/100 "
                f"({compatibility.get('flow_consistent_hosts', 0)}/{compatibility.get('total_hosts', 0)})[/cyan]"
            )
            host_parity = payload.get("host_parity_summary", {})
            if isinstance(host_parity, dict) and host_parity:
                self.console.print(
                    f"[cyan]宿主体验一致性: {host_parity.get('score', 0):.2f}/100 "
                    f"({host_parity.get('passed', 0)}/{host_parity.get('total', 0)})[/cyan]"
                )
            host_gate = payload.get("host_gate_summary", {})
            if isinstance(host_gate, dict) and host_gate:
                self.console.print(
                    f"[cyan]确认门禁一致性: {host_gate.get('score', 0):.2f}/100 "
                    f"({host_gate.get('passed', 0)}/{host_gate.get('total', 0)})[/cyan]"
                )
            host_runtime_script = payload.get("host_runtime_script_summary", {})
            if isinstance(host_runtime_script, dict) and host_runtime_script:
                self.console.print(
                    f"[cyan]真人验收脚本一致性: {host_runtime_script.get('score', 0):.2f}/100 "
                    f"({host_runtime_script.get('passed', 0)}/{host_runtime_script.get('total', 0)})[/cyan]"
                )
            host_recovery = payload.get("host_recovery_summary", {})
            if isinstance(host_recovery, dict) and host_recovery:
                self.console.print(
                    f"[cyan]失败恢复一致性: {host_recovery.get('score', 0):.2f}/100 "
                    f"({host_recovery.get('passed', 0)}/{host_recovery.get('total', 0)})[/cyan]"
                )
            official_summary = payload.get("official_compare_summary", {})
            if isinstance(official_summary, dict) and official_summary:
                self.console.print(
                    f"[cyan]官方文档对照: {official_summary.get('score', 0):.2f}/100 "
                    f"({official_summary.get('passed', 0)}/{official_summary.get('total', 0)})[/cyan]"
                )
            parity_index = payload.get("host_parity_index", {})
            if isinstance(parity_index, dict) and parity_index:
                self.console.print(
                    f"[cyan]Host Parity Index: {parity_index.get('score', 0):.2f}/100 "
                    f"(threshold {parity_index.get('threshold', 95.0):.2f}, "
                    f"{'pass' if bool(parity_index.get('passed', False)) else 'fail'})[/cyan]"
                )
            if args.repair and repair_actions:
                self.console.print("[cyan]修复动作[/cyan]")
                for target, actions in repair_actions.items():
                    action_text = ", ".join(f"{key}={value}" for key, value in actions.items())
                    self.console.print(f"  - {target}: {action_text}")
            for target in targets:
                host = report["hosts"].get(target, {})
                usage = usage_profiles.get(target, {})
                ready = bool(host.get("ready", False))
                self.console.print("")
                self.console.print(f"[cyan]- {target}[/cyan] {'[green]ready[/green]' if ready else '[yellow]needs repair[/yellow]'}")
                self.console.print(f"  触发命令: {usage.get('final_trigger', '-')}")
                self.console.print(f"  宿主协议: {usage.get('host_protocol_summary', '-')}")
                checks = host.get("checks", {})
                contract = checks.get("contract", {}) if isinstance(checks, dict) else {}
                invalid_surfaces = contract.get("invalid_surfaces", {}) if isinstance(contract, dict) else {}
                if isinstance(invalid_surfaces, dict) and invalid_surfaces:
                    self.console.print("  [yellow]过期/缺失的接入面[/yellow]:")
                    for surface_key, surface_info in invalid_surfaces.items():
                        if not isinstance(surface_info, dict):
                            continue
                        missing_markers = surface_info.get("missing_markers", [])
                        marker_text = ", ".join(str(item) for item in missing_markers) if isinstance(missing_markers, list) else "-"
                        self.console.print(f"    - {surface_key}")
                        self.console.print(f"      path: {surface_info.get('path', '-')}")
                        self.console.print(f"      missing: {marker_text}")
                else:
                    self.console.print("  [green]✓[/green] 所有受管接入面契约完整")
                suggestions = host.get("suggestions", [])
                if isinstance(suggestions, list) and suggestions:
                    self.console.print("  建议修复:")
                    for suggestion in suggestions:
                        self.console.print(f"    - {suggestion}")
            if "report_files" in payload:
                report_files = payload["report_files"]
                if isinstance(report_files, dict):
                    self.console.print("")
                    self.console.print("[cyan]审计报告[/cyan]")
                    for name, path in report_files.items():
                        self.console.print(f"  - {name}: {path}")
            return 0 if bool(report.get("overall_ready", False)) and bool((parity_index or {}).get("passed", False)) else 1

        if args.action == "validate":
            project_dir = Path.cwd()
            available_targets = [item.name for item in manager.list_targets()]
            detected_meta: dict[str, list[str]] = {}
            if args.status and not args.target:
                self.console.print("[red]--status 仅可与 --target 一起使用[/red]")
                return 1
            if args.status and args.status not in {"pending", "passed", "failed"}:
                self.console.print("[red]无效的运行时验收状态[/red]")
                return 1
            if args.status and args.target:
                runtime_state, file_path = self._update_host_runtime_validation_state(
                    project_dir=project_dir,
                    target=args.target,
                    status=args.status,
                    comment=args.comment or "",
                    actor=args.actor or "user",
                )
                status_label = self._host_runtime_status_label(args.status)
                if args.json:
                    sys.stdout.write(
                        json.dumps(
                            {
                                "status": "success",
                                "host": args.target,
                                "manual_runtime_status": args.status,
                                "manual_runtime_status_label": status_label,
                                "comment": args.comment or "",
                                "actor": args.actor or "user",
                                "file_path": str(file_path),
                                "updated_at": runtime_state.get("updated_at", ""),
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                        + "\n"
                    )
                    return 0
                self.console.print(f"[green]已更新宿主真人验收状态[/green] {args.target}: {status_label}")
                if args.comment:
                    self.console.print(f"[dim]备注: {args.comment}[/dim]")
                self.console.print(f"[dim]状态文件: {file_path}[/dim]")
                return 0

            if args.target:
                targets = [args.target]
            elif args.all:
                targets = available_targets
            else:
                targets, detected_meta = self._detect_host_targets(available_targets=available_targets)
                if not targets:
                    targets = available_targets

            report = self._collect_host_diagnostics(
                project_dir=project_dir,
                targets=targets,
                skill_name="super-dev-core",
                check_integrate=True,
                check_skill=True,
                check_slash=True,
            )
            usage_profiles = {
                target: self._build_host_usage_profile(
                    integration_manager=manager,
                    target=target,
                )
                for target in targets
            }
            payload = self._build_host_runtime_validation_payload(
                project_dir=project_dir,
                targets=targets,
                detected_meta=detected_meta,
                report=report,
                usage_profiles=usage_profiles,
            )

            if not bool(args.no_save):
                report_files = self._write_host_runtime_validation_report(project_dir=project_dir, payload=payload)
                payload["report_files"] = {name: str(path) for name, path in report_files.items()}

            if args.json:
                sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
                return 0

            self.console.print("[cyan]Super Dev 宿主运行时验收矩阵[/cyan]")
            self.console.print(f"[dim]项目目录: {project_dir}[/dim]")
            if detected_meta:
                self.console.print(
                    f"[cyan]自动检测到 {len(detected_meta)} 个宿主：{', '.join(detected_meta)}[/cyan]"
                )
            summary = payload.get("summary", {})
            if isinstance(summary, dict):
                self.console.print(
                    f"[cyan]中心摘要: fully-ready {summary.get('fully_ready_count', 0)}/{summary.get('total_hosts', 0)} "
                    f"| surface-ready {summary.get('surface_ready_count', 0)}/{summary.get('total_hosts', 0)} "
                    f"| passed {summary.get('runtime_passed_count', 0)} "
                    f"| pending {summary.get('runtime_pending_count', 0)} "
                    f"| failed {summary.get('runtime_failed_count', 0)}[/cyan]"
                )
            blockers = payload.get("blockers", [])
            if isinstance(blockers, list) and blockers:
                self.console.print("[yellow]当前阻塞项[/yellow]")
                for item in blockers[:8]:
                    if not isinstance(item, dict):
                        continue
                    self.console.print(
                        f"  - {item.get('host', '-')}: {item.get('summary', '-')}"
                    )
            for host in payload.get("hosts", []):
                if not isinstance(host, dict):
                    continue
                ready_badge = "[green]surface-ready[/green]" if bool(host.get("surface_ready", False)) else "[yellow]surface-not-ready[/yellow]"
                self.console.print("")
                self.console.print(f"[cyan]- {host.get('host', '-') }[/cyan] {ready_badge}")
                self.console.print(f"  触发命令: {host.get('final_trigger', '-')}")
                self.console.print(f"  宿主协议: {host.get('host_protocol_summary', '-')}")
                self.console.print(f"  人工验收状态: {host.get('manual_runtime_status_label', '-')}")
                if host.get("blocking_reason"):
                    self.console.print(f"  阻塞原因: {host.get('blocking_reason')}")
                if host.get("recommended_action"):
                    self.console.print(f"  建议动作: {host.get('recommended_action')}")
                comment = host.get("manual_runtime_comment", "")
                if isinstance(comment, str) and comment.strip():
                    self.console.print(f"  验收备注: {comment.strip()}")
                self.console.print("  运行时检查清单:")
                checklist = host.get("runtime_checklist", [])
                if isinstance(checklist, list):
                    for item in checklist:
                        self.console.print(f"    - {item}")
                self.console.print("  通过标准:")
                criteria = host.get("pass_criteria", [])
                if isinstance(criteria, list):
                    for item in criteria:
                        self.console.print(f"    - {item}")
            if "report_files" in payload:
                report_files = payload["report_files"]
                if isinstance(report_files, dict):
                    self.console.print("")
                    self.console.print("[cyan]验收矩阵报告[/cyan]")
                    for name, path in report_files.items():
                        self.console.print(f"  - {name}: {path}")
            if isinstance(summary, dict):
                next_actions = summary.get("next_actions", [])
                if isinstance(next_actions, list) and next_actions:
                    self.console.print("")
                    self.console.print("[cyan]推荐动作[/cyan]")
                    for item in next_actions[:8]:
                        self.console.print(f"  - {item}")
            return 0

        self.console.print("[yellow]未知 integrate 操作[/yellow]")
        return 1

    def _resolve_onboard_targets(
        self,
        *,
        available_targets: list[str],
        host: str | None,
        all_targets: bool,
        non_interactive: bool,
    ) -> list[str]:
        targets: list[str] = []
        if all_targets:
            return available_targets
        if host:
            return [host]
        if non_interactive:
            return available_targets

        interactive_targets = self._interactive_host_selector(available_targets=available_targets)
        if interactive_targets is not None:
            return interactive_targets

        self._render_host_selection_guide(available_targets=available_targets)
        raw = input("宿主选择: ").strip()
        if not raw:
            return available_targets
        try:
            selected_indices = [int(item.strip()) for item in raw.split(",") if item.strip()]
        except ValueError:
            raise ValueError("输入无效，请输入数字编号（如 1,3）")
        for index in selected_indices:
            if index < 1 or index > len(available_targets):
                raise ValueError(f"编号超出范围: {index}")

        seen = set()
        for index in selected_indices:
            target = available_targets[index - 1]
            if target in seen:
                continue
            seen.add(target)
            targets.append(target)
        return targets

    def _super_dev_ascii_banner(self) -> str:
        return (
            "  ____                        ____             \n"
            " / ___| _   _ _ __   ___ _ __|  _ \\  _____   __\n"
            " \\___ \\| | | | '_ \\ / _ \\ '__| | | |/ _ \\ \\ / /\n"
            "  ___) | |_| | |_) |  __/ |  | |_| |  __/\\ V / \n"
            " |____/ \\__,_| .__/ \\___|_|  |____/ \\___| \\_/  \n"
            "             |_|                               "
        )

    def _read_single_key(self) -> str:
        if os.name == "nt":
            import msvcrt

            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                special = msvcrt.getwch()
                return {
                    "H": "UP",
                    "P": "DOWN",
                }.get(special, special)
            if key == "\r":
                return "ENTER"
            if key == " ":
                return "SPACE"
            if key == "\x1b":
                return "ESC"
            return key

        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            first = sys.stdin.read(1)
            if first == "\x1b":
                second = sys.stdin.read(1)
                if second == "[":
                    third = sys.stdin.read(1)
                    return {
                        "A": "UP",
                        "B": "DOWN",
                    }.get(third, "ESC")
                return "ESC"
            if first in ("\r", "\n"):
                return "ENTER"
            if first == " ":
                return "SPACE"
            return first
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _interactive_host_selector(self, *, available_targets: list[str]) -> list[str] | None:
        from .integrations import IntegrationManager

        if not RICH_AVAILABLE:
            return None
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return None

        integration_manager = IntegrationManager(Path.cwd())
        detected_targets, _ = self._detect_host_targets(available_targets=available_targets)
        selected: set[str] = set(detected_targets)
        cursor = 0
        status_message = ""

        def renderable() -> Group:
            subtitle = (
                "Space 勾选，Enter 安装，U 卸载选中，↑/↓ 移动，A 全选，C 仅 CLI，I 仅 IDE，R 清空，Esc 取消\n"
                f"[{symbol('cursor')}] 当前光标  [{symbol('selected')}] 已选中  [{symbol('unselected')}] 未选中\n"
                "slash 宿主用 /super-dev；非 slash 宿主用 super-dev: / super-dev："
            )
            header = Panel(f"{self._super_dev_ascii_banner()}\n\n{normalize_terminal_text(subtitle)}", title="Super Dev")

            table = Table(title="选择宿主工具", show_header=True, header_style="bold cyan")
            table.add_column("当前", width=6)
            table.add_column("#", width=4, style="cyan")
            table.add_column("宿主", style="bold")
            table.add_column("认证", width=12)
            table.add_column("触发", width=12)
            table.add_column("协议", overflow="fold")
            table.add_column("检测", width=8)

            for idx, target in enumerate(available_targets, 1):
                profile = integration_manager.get_adapter_profile(target)
                selected_mark = f"[{symbol('selected')}]" if target in selected else f"[{symbol('unselected')}]"
                pointer = f"[{symbol('cursor')}]" if idx - 1 == cursor else "   "
                trigger = "/super-dev" if integration_manager.supports_slash(target) else "super-dev:"
                detected = "已检测" if target in detected_targets else ""
                host_label = Text()
                host_label.append(f"{selected_mark} ", style="green" if target in selected else "dim")
                host_label.append(target, style="bold white" if idx - 1 == cursor else "bold")
                table.add_row(
                    pointer,
                    str(idx),
                    host_label,
                    profile.certification_label,
                    trigger,
                    profile.host_protocol_summary or profile.host_protocol_mode,
                    detected,
                )

            selected_text = ", ".join(sorted(selected)) if selected else "未选择"
            footer = Text()
            footer.append("当前选择: ", style="cyan")
            footer.append(selected_text, style="bold white")

            parts: list[object] = [header, table, footer]
            if status_message:
                parts.append(Text(status_message, style="yellow"))
            return Group(*parts)

        with Live(renderable(), console=self.console, refresh_per_second=8, transient=True, auto_refresh=False) as live:
            while True:
                key = self._read_single_key()
                status_message = ""
                if key == "UP":
                    cursor = (cursor - 1) % len(available_targets)
                    live.update(renderable(), refresh=True)
                    continue
                if key == "DOWN":
                    cursor = (cursor + 1) % len(available_targets)
                    live.update(renderable(), refresh=True)
                    continue
                if key == "SPACE":
                    target = available_targets[cursor]
                    if target in selected:
                        selected.remove(target)
                    else:
                        selected.add(target)
                    live.update(renderable(), refresh=True)
                    continue
                if key in ("a", "A"):
                    selected = set(available_targets)
                    live.update(renderable(), refresh=True)
                    continue
                if key in ("c", "C"):
                    selected = {
                        target for target in available_targets
                        if integration_manager.get_adapter_profile(target).category == "cli"
                    }
                    live.update(renderable(), refresh=True)
                    continue
                if key in ("i", "I"):
                    selected = {
                        target for target in available_targets
                        if integration_manager.get_adapter_profile(target).category == "ide"
                    }
                    live.update(renderable(), refresh=True)
                    continue
                if key in ("r", "R"):
                    selected.clear()
                    live.update(renderable(), refresh=True)
                    continue
                if key in ("u", "U"):
                    if not selected:
                        status_message = "请先选中要卸载的宿主"
                        live.update(renderable(), refresh=True)
                        continue
                    # 卸载选中宿主的 super-dev 集成
                    from .skills import SkillManager
                    skill_manager = SkillManager(Path.cwd())
                    uninstalled_count = 0
                    for target in sorted(selected):
                        try:
                            removed = integration_manager.remove(target=target)
                            if removed:
                                uninstalled_count += len(removed)
                        except Exception:
                            pass
                        try:
                            if skill_manager.skill_surface_available(target):
                                skill_manager.uninstall("super-dev-core", target)
                                uninstalled_count += 1
                        except Exception:
                            pass
                    status_message = f"已从 {len(selected)} 个宿主卸载 Super Dev（{uninstalled_count} 个文件）"
                    selected.clear()
                    live.update(renderable(), refresh=True)
                    continue
                if key == "ENTER":
                    chosen = [target for target in available_targets if target in selected]
                    if chosen:
                        return chosen
                    status_message = "请至少选择一个宿主"
                    live.update(renderable(), refresh=True)
                    continue
                if key == "ESC":
                    raise ValueError("已取消宿主选择")
                live.update(renderable(), refresh=True)

    def _build_install_summary(self, *, available_targets: list[str]) -> str:
        from .integrations import IntegrationManager

        integration_manager = IntegrationManager(Path.cwd())
        slash_hosts = [target for target in available_targets if integration_manager.supports_slash(target)]
        text_hosts = [target for target in available_targets if not integration_manager.supports_slash(target)]
        return (
            f"slash 宿主 ({len(slash_hosts)}): " + ", ".join(slash_hosts) + "\n"
            f"text 宿主 ({len(text_hosts)}): " + ", ".join(text_hosts)
        )

    def _render_host_selection_guide(self, *, available_targets: list[str]) -> None:
        from .integrations import IntegrationManager

        if not RICH_AVAILABLE:
            self.console.print("[cyan]请选择宿主 AI Coding 工具（可多选）:[/cyan]")
            for idx, target in enumerate(available_targets, 1):
                self.console.print(f"  {idx}. {target}")
            self.console.print("[dim]输入编号（逗号分隔），直接回车表示全部[/dim]")
            return

        integration_manager = IntegrationManager(Path.cwd())
        detected_targets, _ = self._detect_host_targets(available_targets=available_targets)
        intro = (
            "安装后直接在宿主里触发。\n"
            "支持 slash 的宿主使用 `/super-dev 你的需求`。\n"
            f"不支持 slash 的宿主使用 `super-dev: 你的需求` 或 `super-dev：你的需求`。\n"
            f"当前版本内置 {len(available_targets)} 个宿主适配配置。"
        )
        self.console.print(Panel(intro, title="Super Dev 安装向导", padding=(1, 2)))

        table = Table(title="宿主选择", show_header=True, header_style="bold cyan")
        table.add_column("#", style="cyan", width=4)
        table.add_column("宿主", style="bold")
        table.add_column("认证", width=12)
        table.add_column("触发", width=12)
        table.add_column("宿主协议", overflow="fold")
        table.add_column("检测", width=8)

        for idx, target in enumerate(available_targets, 1):
            profile = integration_manager.get_adapter_profile(target)
            trigger = "/super-dev" if integration_manager.supports_slash(target) else "super-dev:"
            detected = "已检测" if target in detected_targets else ""
            table.add_row(
                str(idx),
                target,
                profile.certification_label,
                trigger,
                profile.host_protocol_summary or profile.host_protocol_mode,
                detected,
            )
        self.console.print(table)
        self.console.print("[dim]输入编号（逗号分隔），直接回车表示全部[/dim]")

    def _render_install_intro(self, *, args) -> None:
        from .integrations import IntegrationManager

        if not RICH_AVAILABLE:
            self.console.print("[cyan]Super Dev 安装入口[/cyan]")
            self.console.print("宿主负责编码与模型调用；Super Dev 负责流程、门禁、审计与交付标准。")
            self.console.print("slash 宿主输入 /super-dev；非 slash 宿主输入 super-dev: 或 super-dev：")
            return

        integration_manager = IntegrationManager(Path.cwd())
        available_targets = self._public_host_targets(integration_manager=integration_manager)
        lines = [
            "宿主负责编码、工具调用和模型能力。",
            "Super Dev 负责 research → 三文档 → 确认门 → Spec → 前端优先 → 质量门禁 → 交付。",
            "slash 宿主输入 `/super-dev 你的需求`，非 slash 宿主输入 `super-dev: 你的需求` 或 `super-dev：你的需求`。",
            "",
            self._build_install_summary(available_targets=available_targets),
        ]
        if getattr(args, "auto", False):
            lines.append("当前模式: 自动检测宿主。")
        elif getattr(args, "host", None):
            lines.append(f"当前模式: 仅接入 {args.host}。")
        elif getattr(args, "all", False):
            lines.append("当前模式: 接入全部宿主。")
        self.console.print(Panel("\n".join(lines), title="Super Dev 安装入口", padding=(1, 2)))

    def _detect_host_targets(
        self,
        *,
        available_targets: list[str],
    ) -> tuple[list[str], dict[str, list[str]]]:
        detected: list[str] = []
        details: dict[str, list[str]] = {}

        for target in available_targets:
            reasons: list[str] = []

            for command in HOST_COMMAND_CANDIDATES.get(target, []):
                if shutil.which(command):
                    reasons.append(f"cmd:{command}")
                    break

            for candidate in host_path_candidates(target):
                if glob.glob(candidate):
                    reasons.append(f"path:{candidate}")
                    break

            if reasons:
                detected.append(target)
                details[target] = reasons

        return detected, details

    def _collect_configured_host_targets(
        self,
        *,
        project_dir: Path,
        available_targets: list[str],
    ) -> list[str]:
        from .integrations import IntegrationManager
        from .skills import SkillManager

        configured: list[str] = []
        skill_manager = SkillManager(project_dir)
        for target in available_targets:
            integration_files = IntegrationManager.TARGETS[target].files

            has_integration = any((project_dir / relative).exists() for relative in integration_files)
            if IntegrationManager.supports_slash(target):
                project_slash_exists = IntegrationManager.resolve_slash_command_path(
                    target=target,
                    scope="project",
                    project_dir=project_dir,
                ).exists()
                global_slash_exists = IntegrationManager.resolve_slash_command_path(
                    target=target,
                    scope="global",
                ).exists()
            else:
                project_slash_exists = False
                global_slash_exists = False
            has_slash = project_slash_exists or global_slash_exists
            has_skill = False
            if IntegrationManager.requires_skill(target):
                try:
                    has_skill = skill_manager.skill_surface_available(target)
                except ValueError:
                    has_skill = False
            if has_integration or has_slash or has_skill:
                configured.append(target)
        return configured

    def _is_env_truthy(self, key: str) -> bool:
        value = os.getenv(key, "").strip().lower()
        return value in {"1", "true", "yes", "on"}

    def _ensure_pipeline_host_ready(self, *, project_dir: Path, config: ProjectConfig) -> bool:
        from .integrations import IntegrationManager

        if self._is_env_truthy("SUPER_DEV_ALLOW_NO_HOST"):
            self.console.print("[dim]检测到 SUPER_DEV_ALLOW_NO_HOST=1，跳过宿主硬门禁[/dim]")
            return True

        available_targets = [item.name for item in IntegrationManager(project_dir).list_targets()]
        detected_targets, _ = self._detect_host_targets(available_targets=available_targets)
        configured_targets = self._collect_configured_host_targets(
            project_dir=project_dir,
            available_targets=available_targets,
        )

        if config.host_profile_enforce_selected and config.host_profile_targets:
            candidate_targets = [item for item in config.host_profile_targets if item in available_targets]
        else:
            candidate_targets = sorted(set(detected_targets + configured_targets))

        if not candidate_targets:
            self.console.print("[red]流水线宿主校验失败：未检测到可用宿主[/red]")
            self.console.print("[dim]请先执行: super-dev install --auto --force --yes[/dim]")
            self.console.print("[dim]或手动接入: super-dev setup --host codex-cli --force --yes[/dim]")
            return False

        report = self._collect_host_diagnostics(
            project_dir=project_dir,
            targets=candidate_targets,
            skill_name="super-dev-core",
            check_integrate=True,
            check_skill=True,
            check_slash=True,
        )
        compatibility = self._build_compatibility_summary(
            report=report,
            targets=candidate_targets,
            check_integrate=True,
            check_skill=True,
            check_slash=True,
        )

        host_scores = compatibility.get("hosts", {})
        if not isinstance(host_scores, dict):
            host_scores = {}
        ready_targets = [
            target for target in candidate_targets
            if bool((host_scores.get(target) or {}).get("ready", False))
        ]
        ready_detected_targets = [target for target in ready_targets if target in detected_targets]

        if ready_detected_targets:
            self.console.print(
                "[dim]宿主硬门禁通过: "
                + ", ".join(ready_detected_targets)
                + "[/dim]"
            )
            return True

        self.console.print("[red]流水线宿主校验失败：未找到 ready 的已检测宿主[/red]")
        if ready_targets:
            self.console.print(
                "[yellow]检测到已接入宿主但未识别到本机可执行宿主: "
                + ", ".join(ready_targets)
                + "[/yellow]"
            )

        hosts_report = report.get("hosts", {})
        if isinstance(hosts_report, dict):
            for target in candidate_targets:
                host = hosts_report.get(target, {})
                if not isinstance(host, dict):
                    continue
                suggestions = host.get("suggestions", [])
                if isinstance(suggestions, list):
                    for item in suggestions:
                        self.console.print(f"[dim]- {item}[/dim]")

        self.console.print("[dim]建议先执行: super-dev detect --auto --save-profile[/dim]")
        return False

    def _collect_host_diagnostics(
        self,
        *,
        project_dir: Path,
        targets: list[str],
        skill_name: str,
        check_integrate: bool,
        check_skill: bool,
        check_slash: bool,
    ) -> dict[str, Any]:
        from .integrations import IntegrationManager
        from .skills import SkillManager

        integration_manager = IntegrationManager(project_dir)
        integration_targets = IntegrationManager.TARGETS
        skill_manager = SkillManager(project_dir)

        report: dict[str, Any] = {"hosts": {}, "overall_ready": True}
        for target in targets:
            host_report: dict[str, Any] = {
                "ready": True,
                "checks": {},
                "missing": [],
                "suggestions": [],
            }

            surface_audit: dict[str, dict[str, Any]] = {}
            for surface_key, surface_path in integration_manager.collect_managed_surface_paths(
                target=target,
                skill_name=skill_name,
            ).items():
                exists = surface_path.exists()
                audit_entry: dict[str, Any] = {
                    "path": str(surface_path),
                    "exists": exists,
                    "missing_markers": [],
                }
                if exists:
                    try:
                        content = surface_path.read_text(encoding="utf-8")
                    except Exception as exc:
                        audit_entry["read_error"] = str(exc)
                        audit_entry["missing_markers"] = ["unreadable"]
                    else:
                        audit_entry["missing_markers"] = integration_manager.audit_surface_contract(
                            target,
                            surface_key,
                            surface_path,
                            content,
                        )
                surface_audit[surface_key] = audit_entry

            invalid_surfaces = {
                key: value
                for key, value in surface_audit.items()
                if value.get("exists") and value.get("missing_markers")
            }
            host_report["checks"]["contract"] = {
                "ok": not invalid_surfaces,
                "surfaces": surface_audit,
                "invalid_surfaces": invalid_surfaces,
            }
            if invalid_surfaces:
                host_report["ready"] = False
                host_report["missing"].append("contract")
                host_report["suggestions"].append(
                    f"super-dev onboard --host {target} --force --yes"
                )

            if check_integrate:
                integrate_files = [project_dir / item for item in integration_targets[target].files]
                integrate_ok = all(path.exists() for path in integrate_files)
                host_report["checks"]["integrate"] = {
                    "ok": integrate_ok,
                    "files": [str(item) for item in integrate_files],
                }
                if not integrate_ok:
                    host_report["ready"] = False
                    host_report["missing"].append("integrate")
                    host_report["suggestions"].append(
                        f"super-dev integrate setup --target {target} --force"
                    )

            if check_skill and IntegrationManager.requires_skill(target):
                skill_root = skill_manager._target_dir(target)
                skill_file = skill_root / skill_name / "SKILL.md"
                surface_available = skill_manager.skill_surface_available(target)
                skill_ok = skill_file.exists() if surface_available else True
                host_report["checks"]["skill"] = {
                    "ok": skill_ok,
                    "file": str(skill_file),
                    "surface_available": surface_available,
                    "mode": "managed" if surface_available else "compatibility-surface-unavailable",
                }
                if surface_available and not skill_ok:
                    host_report["ready"] = False
                    host_report["missing"].append("skill")
                    host_report["suggestions"].append(
                        f"super-dev skill install super-dev --target {target} --name {skill_name} --force"
                    )

            if check_slash:
                if IntegrationManager.supports_slash(target):
                    project_slash = IntegrationManager.resolve_slash_command_path(
                        target=target,
                        scope="project",
                        project_dir=project_dir,
                    )
                    global_slash = IntegrationManager.resolve_slash_command_path(
                        target=target,
                        scope="global",
                    )
                    project_ok = project_slash.exists()
                    global_ok = global_slash.exists()
                    slash_ok = project_ok or global_ok
                    scope = "project" if project_ok else ("global" if global_ok else "missing")
                    host_report["checks"]["slash"] = {
                        "ok": slash_ok,
                        "scope": scope,
                        "project_file": str(project_slash),
                        "global_file": str(global_slash),
                    }
                    if not slash_ok:
                        host_report["ready"] = False
                        host_report["missing"].append("slash")
                        host_report["suggestions"].append(
                            f"super-dev onboard --host {target} --skip-integrate --skip-skill --force --yes"
                        )
                else:
                    host_report["checks"]["slash"] = {
                        "ok": True,
                        "scope": "n/a",
                        "project_file": "",
                        "global_file": "",
                        "mode": "rules-only",
                    }

            host_report["usage_profile"] = self._build_host_usage_profile(
                integration_manager=integration_manager,
                target=target,
            )
            usage_profile = host_report["usage_profile"]
            if isinstance(usage_profile, dict):
                precondition_status = str(usage_profile.get("precondition_status", "")).strip()
                precondition_label = str(usage_profile.get("precondition_label", "")).strip()
                precondition_guidance = usage_profile.get("precondition_guidance", [])
                precondition_signals = usage_profile.get("precondition_signals", {})
                precondition_items = usage_profile.get("precondition_items", [])
                host_report["preconditions"] = {
                    "status": precondition_status,
                    "label": precondition_label,
                    "guidance": precondition_guidance if isinstance(precondition_guidance, list) else [],
                    "signals": precondition_signals if isinstance(precondition_signals, dict) else {},
                    "items": precondition_items if isinstance(precondition_items, list) else [],
                }
                if precondition_status == "host-auth-required":
                    host_report["suggestions"].append(
                        "若宿主报 Invalid API key provided，请先在宿主内完成 /auth 或更新宿主 API key 配置。"
                    )
                if precondition_status == "session-restart-required":
                    host_report["suggestions"].append("接入后先关闭旧宿主会话，再开一个新会话后重试。")
                if precondition_status == "project-context-required":
                    host_report["suggestions"].append("确认当前聊天/终端绑定的是目标项目，再重新触发 Super Dev。")
            report["hosts"][target] = host_report
            if not host_report["ready"]:
                report["overall_ready"] = False

        return report

    def _build_compatibility_summary(
        self,
        *,
        report: dict[str, Any],
        targets: list[str],
        check_integrate: bool,
        check_skill: bool,
        check_slash: bool,
    ) -> dict[str, Any]:
        from .integrations import IntegrationManager

        enabled_checks = ["contract"]
        if check_integrate:
            enabled_checks.append("integrate")
        if check_skill and any(IntegrationManager.requires_skill(target) for target in targets):
            enabled_checks.append("skill")
        if check_slash and any(IntegrationManager.supports_slash(target) for target in targets):
            enabled_checks.append("slash")

        per_host: dict[str, dict[str, Any]] = {}
        total_passed = 0
        total_possible = 0
        ready_hosts = 0
        flow_consistent_hosts = 0
        hosts = report.get("hosts", {})
        if not isinstance(hosts, dict):
            hosts = {}

        for target in targets:
            host = hosts.get(target, {})
            checks = host.get("checks", {}) if isinstance(host, dict) else {}
            if not isinstance(checks, dict):
                checks = {}
            passed = 0
            possible = len(enabled_checks)
            for check_name in enabled_checks:
                check_value = checks.get(check_name, {})
                if isinstance(check_value, dict) and bool(check_value.get("ok", False)):
                    passed += 1
            flow_consistent = False
            contract_check = checks.get("contract", {})
            if isinstance(contract_check, dict):
                flow_consistent = True
                surfaces = contract_check.get("surfaces", {})
                if isinstance(surfaces, dict):
                    for item in surfaces.values():
                        if not isinstance(item, dict):
                            continue
                        missing_markers = item.get("missing_markers", [])
                        if isinstance(missing_markers, list) and "flow" in missing_markers:
                            flow_consistent = False
                            break
            score = round((passed / possible) * 100, 2) if possible > 0 else 100.0
            per_host[target] = {
                "score": score,
                "passed": passed,
                "possible": possible,
                "ready": bool(host.get("ready", False)) if isinstance(host, dict) else False,
                "flow_consistent": flow_consistent,
            }
            total_passed += passed
            total_possible += possible
            if bool(host.get("ready", False)) if isinstance(host, dict) else False:
                ready_hosts += 1
            if flow_consistent:
                flow_consistent_hosts += 1

        overall_score = round((total_passed / total_possible) * 100, 2) if total_possible > 0 else 100.0
        flow_consistency_score = round((flow_consistent_hosts / len(targets)) * 100, 2) if targets else 100.0
        return {
            "overall_score": overall_score,
            "ready_hosts": ready_hosts,
            "total_hosts": len(targets),
            "enabled_checks": enabled_checks,
            "flow_consistent_hosts": flow_consistent_hosts,
            "flow_consistency_score": flow_consistency_score,
            "hosts": per_host,
        }

    def _build_official_compare_summary(self, *, hardening_results: dict[str, Any]) -> dict[str, Any]:
        total = 0
        passed = 0
        partial = 0
        unknown = 0
        failed = 0
        per_host: dict[str, str] = {}
        for host, item in hardening_results.items():
            total += 1
            status = "unknown"
            if isinstance(item, dict):
                official_compare = item.get("official_compare", {})
                if isinstance(official_compare, dict):
                    status = str(official_compare.get("status", "unknown")).strip() or "unknown"
            per_host[str(host)] = status
            if status == "passed":
                passed += 1
            elif status == "partial":
                partial += 1
            elif status == "failed":
                failed += 1
            else:
                unknown += 1
        score = round((passed / total) * 100, 2) if total else 100.0
        return {
            "total": total,
            "passed": passed,
            "partial": partial,
            "failed": failed,
            "unknown": unknown,
            "score": score,
            "hosts": per_host,
        }

    def _build_host_parity_summary(self, *, usage_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
        total = 0
        passed = 0
        per_host: dict[str, dict[str, Any]] = {}
        required_keys = ("slash", "rules", "skills", "trigger")
        for host, usage in usage_profiles.items():
            total += 1
            labels = usage.get("capability_labels", {}) if isinstance(usage, dict) else {}
            trigger_command = str(usage.get("trigger_command", "")) if isinstance(usage, dict) else ""
            smoke_prompt = str(usage.get("smoke_test_prompt", "")) if isinstance(usage, dict) else ""
            smoke_signal = str(usage.get("smoke_success_signal", "")) if isinstance(usage, dict) else ""
            protocol_mode = str(usage.get("host_protocol_mode", "")).strip() if isinstance(usage, dict) else ""
            slash_label = str((labels or {}).get("slash", "")).strip()
            trigger_ok = (
                trigger_command.startswith("/super-dev")
                if slash_label == "native"
                else trigger_command.startswith("super-dev:")
            )
            checks = {
                "trigger": trigger_ok,
                "smoke_prompt": "SMOKE_OK" in smoke_prompt,
                "smoke_signal": "SMOKE_OK" in smoke_signal,
                "protocol_mode": bool(protocol_mode),
                "capability_labels": all(key in labels for key in required_keys),
            }
            check_total = len(checks)
            check_passed = sum(1 for item in checks.values() if bool(item))
            host_pass = check_passed == check_total
            if host_pass:
                passed += 1
            per_host[str(host)] = {
                "passed": host_pass,
                "score": round((check_passed / check_total) * 100, 2) if check_total else 100.0,
                "checks": checks,
            }
        score = round((passed / total) * 100, 2) if total else 100.0
        return {
            "total": total,
            "passed": passed,
            "score": score,
            "hosts": per_host,
        }

    def _build_host_recovery_summary(
        self,
        *,
        targets: list[str],
        usage_profiles: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        from .integrations import IntegrationManager

        total = 0
        passed = 0
        hosts: dict[str, dict[str, Any]] = {}
        for target in targets:
            total += 1
            usage = usage_profiles.get(target, {}) if isinstance(usage_profiles, dict) else {}
            slash_label = ""
            if isinstance(usage, dict):
                labels = usage.get("capability_labels", {})
                if isinstance(labels, dict):
                    slash_label = str(labels.get("slash", "")).strip()
            commands = [f"super-dev integrate setup --target {target} --force"]
            if IntegrationManager.requires_skill(target):
                commands.append(f"super-dev skill install super-dev --target {target} --name super-dev-core --force")
            if slash_label == "native":
                commands.append(f"super-dev onboard --host {target} --skip-integrate --skip-skill --force --yes")
            commands.append(f"super-dev integrate audit --target {target} --repair --force")
            checks = {
                "has_setup": any(cmd.startswith("super-dev integrate setup --target ") for cmd in commands),
                "has_repair_audit": any(cmd.startswith("super-dev integrate audit --target ") for cmd in commands),
                "contains_target": all(f" {target} " in f" {cmd} " for cmd in commands),
            }
            if IntegrationManager.requires_skill(target):
                checks["has_skill_install"] = any(cmd.startswith("super-dev skill install ") for cmd in commands)
            if slash_label == "native":
                checks["has_slash_recovery"] = any(cmd.startswith("super-dev onboard --host ") for cmd in commands)
            host_pass = all(bool(item) for item in checks.values())
            if host_pass:
                passed += 1
            hosts[target] = {
                "passed": host_pass,
                "checks": checks,
                "recommended_commands": commands,
            }
        score = round((passed / total) * 100, 2) if total else 100.0
        return {
            "total": total,
            "passed": passed,
            "score": score,
            "hosts": hosts,
        }

    def _build_host_gate_summary(self, *, report: dict[str, Any], targets: list[str]) -> dict[str, Any]:
        total = 0
        passed = 0
        hosts: dict[str, dict[str, Any]] = {}
        report_hosts = report.get("hosts", {}) if isinstance(report, dict) else {}
        if not isinstance(report_hosts, dict):
            report_hosts = {}
        for target in targets:
            total += 1
            host = report_hosts.get(target, {})
            checks = host.get("checks", {}) if isinstance(host, dict) else {}
            contract = checks.get("contract", {}) if isinstance(checks, dict) else {}
            surfaces = contract.get("surfaces", {}) if isinstance(contract, dict) else {}
            docs_confirm_ok = True
            preview_confirm_ok = True
            if isinstance(surfaces, dict):
                for surface in surfaces.values():
                    if not isinstance(surface, dict):
                        continue
                    if not bool(surface.get("exists", False)):
                        continue
                    missing = surface.get("missing_markers", [])
                    if not isinstance(missing, list):
                        continue
                    if "confirmation" in missing:
                        docs_confirm_ok = False
                    if "flow" in missing:
                        preview_confirm_ok = False
            host_pass = docs_confirm_ok and preview_confirm_ok
            if host_pass:
                passed += 1
            hosts[target] = {
                "passed": host_pass,
                "checks": {
                    "docs_confirm_gate": docs_confirm_ok,
                    "preview_confirm_gate": preview_confirm_ok,
                },
            }
        score = round((passed / total) * 100, 2) if total else 100.0
        return {
            "total": total,
            "passed": passed,
            "score": score,
            "hosts": hosts,
        }

    def _build_host_runtime_script_summary(self, *, usage_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
        total = 0
        passed = 0
        hosts: dict[str, dict[str, Any]] = {}
        for host, usage in usage_profiles.items():
            total += 1
            if not isinstance(usage, dict):
                usage = {}
            smoke_steps = usage.get("smoke_test_steps", [])
            post_steps = usage.get("post_onboard_steps", [])
            checks = {
                "has_final_trigger": bool(str(usage.get("final_trigger", "")).strip()),
                "has_smoke_prompt": "SMOKE_OK" in str(usage.get("smoke_test_prompt", "")),
                "has_smoke_signal": "SMOKE_OK" in str(usage.get("smoke_success_signal", "")),
                "has_smoke_steps": isinstance(smoke_steps, list) and len(smoke_steps) > 0,
                "has_post_onboard_steps": isinstance(post_steps, list) and len(post_steps) > 0,
            }
            host_pass = all(bool(item) for item in checks.values())
            if host_pass:
                passed += 1
            hosts[str(host)] = {
                "passed": host_pass,
                "checks": checks,
            }
        score = round((passed / total) * 100, 2) if total else 100.0
        return {
            "total": total,
            "passed": passed,
            "score": score,
            "hosts": hosts,
        }

    def _build_host_parity_index(
        self,
        *,
        threshold: float,
        official_compare_summary: dict[str, Any] | None,
        host_parity_summary: dict[str, Any] | None,
        host_gate_summary: dict[str, Any] | None,
        host_runtime_script_summary: dict[str, Any] | None,
        host_recovery_summary: dict[str, Any] | None,
        compatibility: dict[str, Any] | None,
    ) -> dict[str, Any]:
        metrics: dict[str, float] = {}
        mapping: list[tuple[str, dict[str, Any] | None]] = [
            ("official_compare", official_compare_summary),
            ("host_parity", host_parity_summary),
            ("host_gate", host_gate_summary),
            ("runtime_script", host_runtime_script_summary),
            ("host_recovery", host_recovery_summary),
        ]
        for name, summary in mapping:
            if isinstance(summary, dict):
                if name == "official_compare":
                    total = int(summary.get("total", 0) or 0)
                    passed = int(summary.get("passed", 0) or 0)
                    partial = int(summary.get("partial", 0) or 0)
                    failed = int(summary.get("failed", 0) or 0)
                    if total <= 0 or (passed + partial + failed) <= 0:
                        continue
                try:
                    metrics[name] = float(summary.get("score", 0))
                except Exception:
                    metrics[name] = 0.0
        if isinstance(compatibility, dict):
            try:
                metrics["flow_consistency"] = float(compatibility.get("flow_consistency_score", 0))
            except Exception:
                metrics["flow_consistency"] = 0.0
        if metrics:
            score = round(sum(metrics.values()) / len(metrics), 2)
        else:
            score = 0.0
        limit = float(threshold)
        return {
            "score": score,
            "threshold": limit,
            "passed": score >= limit,
            "metrics": metrics,
        }

    def _repair_host_diagnostics(
        self,
        *,
        project_dir: Path,
        report: dict[str, Any],
        skill_name: str,
        force: bool,
        check_integrate: bool,
        check_skill: bool,
        check_slash: bool,
    ) -> dict[str, dict[str, str]]:
        from .integrations import IntegrationManager
        from .skills import SkillManager

        integration_manager = IntegrationManager(project_dir)
        skill_manager = SkillManager(project_dir)
        actions: dict[str, dict[str, str]] = {}

        hosts = report.get("hosts", {})
        if not isinstance(hosts, dict):
            return actions

        for target, host in hosts.items():
            if not isinstance(target, str) or not isinstance(host, dict):
                continue
            missing = host.get("missing", [])
            if not isinstance(missing, list):
                continue

            host_actions: dict[str, str] = {}
            contract_needs_repair = "contract" in missing

            if contract_needs_repair:
                try:
                    integration_manager.setup(target=target, force=True)
                    integration_manager.setup_global_protocol(target=target, force=True)
                    if integration_manager.supports_slash(target):
                        integration_manager.setup_slash_command(target=target, force=True)
                        integration_manager.setup_global_slash_command(target=target, force=True)
                    if check_skill and IntegrationManager.requires_skill(target) and skill_manager.skill_surface_available(target):
                        skill_manager.install(
                            source="super-dev",
                            target=target,
                            name=skill_name,
                            force=True,
                        )
                    host_actions["contract"] = "refreshed"
                except Exception as exc:
                    host_actions["contract"] = f"failed: {exc}"

            try:
                if check_integrate and "integrate" in missing and not contract_needs_repair:
                    integration_manager.setup(target=target, force=force)
                    host_actions["integrate"] = "fixed"
            except Exception as exc:
                host_actions["integrate"] = f"failed: {exc}"

            try:
                if check_skill and IntegrationManager.requires_skill(target) and "skill" in missing and not contract_needs_repair:
                    skill_manager.install(
                        source="super-dev",
                        target=target,
                        name=skill_name,
                        force=force,
                    )
                    host_actions["skill"] = "fixed"
            except Exception as exc:
                host_actions["skill"] = f"failed: {exc}"

            try:
                if check_slash and integration_manager.supports_slash(target) and not contract_needs_repair:
                    integration_manager.setup_slash_command(target=target, force=force)
                    integration_manager.setup_global_slash_command(target=target, force=force)
                    if "slash" in missing:
                        host_actions["slash"] = "fixed"
            except Exception as exc:
                host_actions["slash"] = f"failed: {exc}"

            if host_actions:
                actions[target] = host_actions

        return actions

    def _cmd_onboard(self, args) -> int:
        """首次接入向导：宿主选择 + 集成 + skill + slash"""
        from .integrations import IntegrationManager
        from .skills import SkillManager

        if not self._ensure_host_support_matrix():
            return 1

        project_dir = Path.cwd()
        integration_manager = IntegrationManager(project_dir)
        skill_manager = SkillManager(project_dir)

        available_targets = self._public_host_targets(integration_manager=integration_manager)
        targets: list[str]
        detected_meta: dict[str, list[str]] = {}

        if args.host:
            targets = [args.host]
        elif args.all:
            targets = available_targets
        elif args.auto:
            targets, detected_meta = self._detect_host_targets(available_targets=available_targets)
            if not targets:
                self.console.print("[red]未检测到可用宿主，请改用 --host 指定或使用 --all[/red]")
                return 1
            self.console.print(
                f"[cyan]自动检测到 {len(targets)} 个宿主：{', '.join(targets)}[/cyan]"
            )
            for target in targets:
                reasons = ", ".join(detected_meta.get(target, []))
                if reasons:
                    self.console.print(f"[dim]  - {target}: {reasons}[/dim]")
        else:
            try:
                targets = self._resolve_onboard_targets(
                    available_targets=available_targets,
                    host=args.host,
                    all_targets=bool(args.all),
                    non_interactive=bool(args.yes),
                )
            except ValueError as exc:
                self.console.print(f"[red]{exc}[/red]")
                return 1

        if not targets:
            self.console.print("[red]未选择任何宿主工具[/red]")
            return 1

        if getattr(args, 'stable_only', False):
            stable_targets = []
            for t in targets:
                profile = integration_manager.get_adapter_profile(t)
                cert = profile.certification_label.lower()
                if cert.startswith("certified") or cert.startswith("compatible"):
                    stable_targets.append(t)
            if not stable_targets:
                self.console.print("[yellow]未找到 Certified 或 Compatible 级别的宿主[/yellow]")
                return 1
            skipped = set(targets) - set(stable_targets)
            if skipped:
                self.console.print(f"[dim]跳过 Experimental 宿主: {', '.join(sorted(skipped))}[/dim]")
            targets = stable_targets

        setattr(args, "_selected_targets", list(targets))

        self.console.print("")
        from rich.panel import Panel
        from rich.rule import Rule
        self.console.print(Panel(
            f"[bold cyan]Super Dev Onboard[/bold cyan]\n\n"
            f"  [dim]项目[/dim]      {project_dir.name}\n"
            f"  [dim]目标宿主[/dim]  {len(targets)} 个\n"
            f"  [dim]版本[/dim]      {__version__}",
            border_style="cyan",
            expand=True,
            padding=(1, 2),
        ))
        self.console.print("")
        has_error = False
        for idx, target in enumerate(targets, 1):
            protocol = integration_manager._protocol_profile(target=target)
            protocol_summary = protocol.get("summary", "") if isinstance(protocol, dict) else ""
            self.console.print(Rule(
                f"[bold cyan] {idx}/{len(targets)} [/bold cyan] [bold]{target}[/bold]  [dim]{protocol_summary}[/dim]",
                style="dim cyan",
            ))
            self.console.print("")
            profile = integration_manager.get_adapter_profile(target)

            if getattr(args, "dry_run", False):
                surfaces = integration_manager.collect_managed_surface_paths(target=target)
                self.console.print("  [dim]将写入以下文件:[/dim]")
                for key, path in surfaces.items():
                    exists = path.exists()
                    status = "[dim]已存在[/dim]" if exists else "[cyan]新建[/cyan]"
                    self.console.print(f"    {status} {path}")
                self.console.print("")
                continue

            if not args.skip_integrate:
                try:
                    written_files = integration_manager.setup(target=target, force=args.force)
                    if written_files:
                        for item in written_files:
                            self.console.print(f"  [green]✓[/green] 集成规则: {item}")
                    else:
                        self.console.print("  [dim]- 集成规则已存在（可加 --force 覆盖）[/dim]")
                    global_protocol = integration_manager.setup_global_protocol(target=target, force=args.force)
                    if global_protocol is not None:
                        self.console.print(f"  [green]✓[/green] 宿主协议: {global_protocol}")
                except Exception as exc:
                    has_error = True
                    self.console.print(f"  [red]✗[/red] 集成失败: {exc}")

            if not args.skip_skill and IntegrationManager.requires_skill(target):
                try:
                    if not skill_manager.skill_surface_available(target):
                        self.console.print("  [dim]- 未检测到官方或兼容 Skill 目录，已跳过宿主级 Skill 安装[/dim]")
                    else:
                        installed = set(skill_manager.list_installed(target))
                        if args.skill_name in installed and not args.force:
                            self.console.print(
                                f"  [dim]- Skill 已存在: {args.skill_name}（可加 --force 重装）[/dim]"
                            )
                        else:
                            install_result = skill_manager.install(
                                source="super-dev",
                                target=target,
                                name=args.skill_name,
                                force=args.force,
                            )
                            self.console.print(f"  [green]✓[/green] Skill: {install_result.path}")
                except Exception as exc:
                    has_error = True
                    self.console.print(f"  [red]✗[/red] Skill 安装失败: {exc}")
            elif not args.skip_skill:
                self.console.print("  [dim]- 该宿主默认按项目规则运行，已跳过 Skill 安装[/dim]")

            if not args.skip_slash:
                try:
                    if integration_manager.supports_slash(target):
                        slash_file = integration_manager.setup_slash_command(
                            target=target,
                            force=args.force,
                        )
                        if slash_file is None:
                            self.console.print("  [dim]- /super-dev 映射已存在（可加 --force 覆盖）[/dim]")
                        else:
                            self.console.print(f"  [green]✓[/green] /super-dev 映射: {slash_file}")
                        global_slash_file = integration_manager.setup_global_slash_command(
                            target=target,
                            force=args.force,
                        )
                        if global_slash_file is None:
                            self.console.print("  [dim]- 全局 /super-dev 映射已存在（可加 --force 覆盖）[/dim]")
                        elif slash_file is None or global_slash_file.resolve() != slash_file.resolve():
                            self.console.print(f"  [green]✓[/green] 全局 /super-dev 映射: {global_slash_file}")
                    else:
                        self.console.print("  [dim]- 该宿主不支持 /super-dev，已跳过 slash 映射[/dim]")
                except Exception as exc:
                    has_error = True
                    self.console.print(f"  [red]✗[/red] /super-dev 映射失败: {exc}")

            self.console.print(f"  [cyan]主入口[/cyan]: {profile.primary_entry}")
            if profile.requires_restart_after_onboard:
                self.console.print("  [yellow]注意[/yellow]: 接入完成后需要重启宿主")
            for step in profile.post_onboard_steps:
                self.console.print(f"  [dim]- {step}[/dim]")

            contract_surfaces = integration_manager.collect_managed_surface_paths(target=target, skill_name=args.skill_name)
            contract_failures: list[str] = []
            for surface_key, surface_path in contract_surfaces.items():
                if surface_key.startswith("skill:") and args.skip_skill:
                    continue
                if not surface_path.exists():
                    continue
                try:
                    content = surface_path.read_text(encoding="utf-8")
                except Exception:
                    contract_failures.append(str(surface_path))
                    continue
                if integration_manager.audit_surface_contract(target, surface_key, surface_path, content):
                    contract_failures.append(str(surface_path))
            if contract_failures:
                has_error = True
                self.console.print("  [red]✗[/red] 宿主契约校验失败:")
                for item in contract_failures[:6]:
                    self.console.print(f"  [dim]- {item}[/dim]")
            else:
                self.console.print("  [green]✓[/green] 宿主契约校验通过")

        self.console.print("")
        if args.dry_run:
            self.console.print(Panel(
                "[bold cyan]Dry Run 完成[/bold cyan]\n\n"
                "  以上为预览，未实际写入任何文件\n"
                "  去掉 --dry-run 参数执行实际安装",
                border_style="cyan",
                expand=True,
                padding=(1, 2),
            ))
            return 0
        if has_error:
            self.console.print(Panel(
                "[bold red]Onboard 完成（部分失败）[/bold red]\n\n"
                "  请检查上方错误信息\n"
                "  使用 [cyan]super-dev doctor[/cyan] 诊断并自动修复",
                border_style="red",
                expand=True,
                padding=(1, 2),
            ))
            return 1

        next_steps = self._build_onboard_next_steps(targets=targets)
        steps_text = "\n".join(f"  [green]>[/green] {line}" for line in next_steps)
        self.console.print(Panel(
            f"[bold green]Onboard 完成[/bold green]\n\n"
            f"[bold]接下来这样用:[/bold]\n\n{steps_text}\n\n"
            f"[dim]提示: 终端 super-dev \"你的需求\" 仅触发本地编排，不替代宿主会话编码[/dim]",
            border_style="green",
            expand=True,
            padding=(1, 2),
        ))
        return 0

    def _cmd_doctor(self, args) -> int:
        """诊断宿主接入状态"""
        from .integrations import IntegrationManager

        if not self._ensure_host_support_matrix():
            return 1

        project_dir = Path.cwd()
        integration_manager = IntegrationManager(project_dir)
        available_targets = [item.name for item in integration_manager.list_targets()]
        targets: list[str]
        if args.host:
            targets = [args.host]
        elif args.auto:
            targets, detected_meta = self._detect_host_targets(available_targets=available_targets)
            if not targets:
                self.console.print("[yellow]未检测到可用宿主，已回退为诊断全部目标[/yellow]")
                targets = available_targets
            else:
                self.console.print(
                    f"[cyan]自动检测到 {len(targets)} 个宿主：{', '.join(targets)}[/cyan]"
                )
                for target in targets:
                    reasons = ", ".join(detected_meta.get(target, []))
                    if reasons:
                        self.console.print(f"[dim]  - {target}: {reasons}[/dim]")
        elif args.all:
            targets = available_targets
        else:
            targets = available_targets

        report = self._collect_host_diagnostics(
            project_dir=project_dir,
            targets=targets,
            skill_name=args.skill_name,
            check_integrate=not args.skip_integrate,
            check_skill=not args.skip_skill,
            check_slash=not args.skip_slash,
        )
        compatibility = self._build_compatibility_summary(
            report=report,
            targets=targets,
            check_integrate=not args.skip_integrate,
            check_skill=not args.skip_skill,
            check_slash=not args.skip_slash,
        )
        repair_actions: dict[str, dict[str, str]] = {}
        if args.repair:
            repair_actions = self._repair_host_diagnostics(
                project_dir=project_dir,
                report=report,
                skill_name=args.skill_name,
                force=bool(args.force),
                check_integrate=not args.skip_integrate,
                check_skill=not args.skip_skill,
                check_slash=not args.skip_slash,
            )
            report = self._collect_host_diagnostics(
                project_dir=project_dir,
                targets=targets,
                skill_name=args.skill_name,
                check_integrate=not args.skip_integrate,
                check_skill=not args.skip_skill,
                check_slash=not args.skip_slash,
            )
            compatibility = self._build_compatibility_summary(
                report=report,
                targets=targets,
                check_integrate=not args.skip_integrate,
                check_skill=not args.skip_skill,
                check_slash=not args.skip_slash,
            )
            report["repair_actions"] = repair_actions
        report["compatibility"] = compatibility

        if args.json:
            sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            return 0 if bool(report.get("overall_ready", False)) else 1

        self.console.print("[cyan]Super Dev Doctor[/cyan]")
        self.console.print(f"[dim]项目目录: {project_dir}[/dim]")
        self.console.print(
            f"[dim]终端输出: {output_mode_label()} ({output_mode_reason()})[/dim]"
        )
        self.console.print(
            f"[cyan]兼容性评分: {compatibility['overall_score']:.2f}/100 "
            f"(ready {compatibility['ready_hosts']}/{compatibility['total_hosts']})[/cyan]"
        )
        self.console.print(
            f"[cyan]流程一致性: {compatibility.get('flow_consistency_score', 0):.2f}/100 "
            f"({compatibility.get('flow_consistent_hosts', 0)}/{compatibility.get('total_hosts', 0)})[/cyan]"
        )
        certified_count = sum(
            1 for t in targets
            if integration_manager.get_adapter_profile(t).certification_label.lower().startswith("certified")
        )
        compatible_count = sum(
            1 for t in targets
            if integration_manager.get_adapter_profile(t).certification_label.lower().startswith("compatible")
        )
        experimental_count = len(targets) - certified_count - compatible_count
        self.console.print(
            f"[cyan]认证分布: Certified {certified_count} / Compatible {compatible_count} / Experimental {experimental_count}[/cyan]"
        )
        self.console.print("")
        if args.repair:
            self.console.print("[cyan]Repair 模式已执行[/cyan]")
            if repair_actions:
                for target, actions in repair_actions.items():
                    action_text = ", ".join(f"{k}={v}" for k, v in actions.items())
                    self.console.print(f"[dim]- {target}: {action_text}[/dim]")
            else:
                self.console.print("[dim]- 无需修复或未执行修复动作[/dim]")
            self.console.print("")
        # 摘要表格
        from rich.table import Table
        summary_table = Table(
            title="宿主接入状态",
            expand=True,
            show_lines=False,
            border_style="dim",
            title_style="bold cyan",
        )
        summary_table.add_column("宿主", style="bold", min_width=18)
        summary_table.add_column("状态", justify="center", min_width=8)
        summary_table.add_column("集成规则", justify="center")
        summary_table.add_column("Skill", justify="center")
        summary_table.add_column("Slash", justify="center")
        summary_table.add_column("认证", justify="center", min_width=12)
        summary_table.add_column("协议", style="dim")

        for target in targets:
            host = report["hosts"][target]
            protocol = integration_manager._protocol_profile(target=target)
            protocol_summary = protocol.get("summary", "") if isinstance(protocol, dict) else ""

            status = "[green]已就绪[/green]" if host["ready"] else "[red]未安装[/red]"

            integrate_ok = host.get("integrate_ok", True)
            skill_ok = host.get("skill_ok", True)
            slash_ok = host.get("slash_ok", True)

            integrate_text = "[green]已安装[/green]" if integrate_ok else "[red]未安装[/red]"
            skill_text = "[green]已安装[/green]" if skill_ok else ("[dim]不适用[/dim]" if not IntegrationManager.requires_skill(target) else "[red]未安装[/red]")
            slash_text = "[green]已安装[/green]" if slash_ok else ("[dim]不适用[/dim]" if not integration_manager.supports_slash(target) else "[red]未安装[/red]")

            profile = integration_manager.get_adapter_profile(target)
            cert_label = profile.certification_label
            if "certified" in cert_label.lower():
                cert_text = f"[bold green]{cert_label}[/bold green]"
            elif "compatible" in cert_label.lower():
                cert_text = f"[cyan]{cert_label}[/cyan]"
            else:
                cert_text = f"[yellow]{cert_label}[/yellow]"

            summary_table.add_row(target, status, integrate_text, skill_text, slash_text, cert_text, protocol_summary)

        self.console.print(summary_table)
        self.console.print("")

        for target in targets:
            host = report["hosts"][target]
            if host["ready"]:
                self.console.print(f"[green]✓ {target}[/green] ready")
            else:
                self.console.print(f"[red]✗ {target}[/red] [red]未安装[/red]")
                for check_name in host.get("missing", []):
                    self.console.print(f"  [red]- 缺失: {check_name}[/red]")
                for suggestion in host.get("suggestions", []):
                    self.console.print(f"  [dim]建议: {suggestion}[/dim]")
            self._print_host_usage_guidance(
                integration_manager=integration_manager,
                target=target,
                indent="  ",
            )

        self.console.print("")
        if bool(report.get("overall_ready", False)):
            self.console.print("[green]✓ Doctor 通过：所有宿主接入完整[/green]")
            return 0
        self.console.print("[red]Doctor 未通过：请按建议修复后重试[/red]")
        return 1

    def _cmd_setup(self, args) -> int:
        """一步接入：onboard + doctor"""
        setup_all = bool(args.all or (bool(args.yes) and not args.host and not args.auto))
        onboard_args = argparse.Namespace(
            host=args.host,
            all=setup_all,
            auto=bool(args.auto and not args.host and not args.all),
            skill_name=args.skill_name,
            skip_integrate=bool(args.skip_integrate),
            skip_skill=bool(args.skip_skill),
            skip_slash=bool(args.skip_slash),
            yes=bool(args.yes),
            force=bool(args.force),
            dry_run=False,
            stable_only=False,
        )
        onboard_result = self._cmd_onboard(onboard_args)
        if onboard_result != 0:
            return onboard_result

        if args.skip_doctor:
            return 0

        selected_targets = getattr(onboard_args, "_selected_targets", None)
        if isinstance(selected_targets, list) and selected_targets:
            final_code = 0
            for target in selected_targets:
                doctor_args = argparse.Namespace(
                    host=target,
                    all=False,
                    auto=False,
                    skill_name=args.skill_name,
                    skip_integrate=bool(args.skip_integrate),
                    skip_skill=bool(args.skip_skill),
                    skip_slash=bool(args.skip_slash),
                    json=False,
                    repair=False,
                    force=bool(args.force),
                )
                result = self._cmd_doctor(doctor_args)
                if result != 0:
                    final_code = result
            return final_code

        doctor_args = argparse.Namespace(
            host=args.host,
            all=setup_all,
            auto=bool(args.auto and not args.host and not args.all),
            skill_name=args.skill_name,
            skip_integrate=bool(args.skip_integrate),
            skip_skill=bool(args.skip_skill),
            skip_slash=bool(args.skip_slash),
            json=False,
            repair=False,
            force=bool(args.force),
        )
        return self._cmd_doctor(doctor_args)

    def _cmd_install(self, args) -> int:
        """面向 PyPI 用户的一键安装入口"""
        self._render_install_intro(args=args)
        setup_args = argparse.Namespace(
            host=args.host,
            all=bool(args.all),
            auto=bool(args.auto),
            skill_name=args.skill_name,
            skip_integrate=bool(args.skip_integrate),
            skip_skill=bool(args.no_skill),
            skip_slash=bool(args.skip_slash),
            skip_doctor=bool(args.skip_doctor),
            force=bool(args.force),
            yes=bool(args.yes),
        )
        return self._cmd_setup(setup_args)

    def _cmd_start(self, args) -> int:
        """面向非技术用户的起步入口：自动选宿主、接入并输出最短试用路径。"""
        from .integrations import IntegrationManager

        if not self._ensure_host_support_matrix():
            return 1

        project_dir = Path.cwd()
        integration_manager = IntegrationManager(project_dir)
        available_targets = self._public_host_targets(integration_manager=integration_manager)
        detected_targets, detected_meta = self._detect_host_targets(available_targets=available_targets)

        target = args.host
        selection_reason = "manual"
        if not target:
            if detected_targets:
                target = self._select_best_start_host(
                    integration_manager=integration_manager,
                    targets=detected_targets,
                )
                selection_reason = "auto-detected"
            else:
                payload = {
                    "status": "error",
                    "reason": "no-host-detected",
                    "message": "未检测到可用宿主，请先安装受支持宿主后重试。",
                    "recommended_hosts": self._recommended_start_hosts(
                        integration_manager=integration_manager
                    ),
                }
                if args.json:
                    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
                else:
                    self.console.print("[red]未检测到可用宿主[/red]")
                    self.console.print("[dim]请先安装至少一个受支持宿主，再执行 super-dev start[/dim]")
                    self.console.print("[cyan]优先建议安装这些宿主:[/cyan]")
                    for host in payload["recommended_hosts"]:
                        self.console.print(
                            f"  - {host['name']} ({host['id']}) [{host['certification_label']}]"
                        )
                return 1

        usage = self._build_host_usage_profile(
            integration_manager=integration_manager,
            target=target,
        )

        onboard_performed = False
        if not bool(args.skip_onboard):
            onboard_args = argparse.Namespace(
                host=target,
                all=False,
                auto=False,
                skill_name="super-dev-core",
                skip_integrate=False,
                skip_skill=False,
                skip_slash=False,
                yes=True,
                force=bool(args.force),
            )
            onboard_result = self._cmd_onboard(onboard_args)
            onboard_performed = True
            if onboard_result != 0:
                return onboard_result

        profile_saved = False
        profile_save_error = ""
        if not bool(args.no_save_profile):
            try:
                ConfigManager(project_dir).update(
                    host_profile_targets=[target],
                    host_profile_enforce_selected=True,
                )
                profile_saved = True
            except Exception as exc:
                profile_save_error = str(exc)

        quick_start = self._build_host_quick_start_text(
            host_profile=usage,
            host_id=target,
            host_name=integration_manager.TARGETS[target].description,
            idea=args.idea,
        )
        payload = {
            "status": "success",
            "project_dir": str(project_dir),
            "selected_host": target,
            "selection_reason": selection_reason,
            "detected_hosts": detected_targets,
            "detection_details": detected_meta,
            "onboard_performed": onboard_performed,
            "profile_saved": profile_saved,
            "profile_save_error": profile_save_error,
            "usage_profile": usage,
            "recommended_trigger": self._build_host_trigger_example(target=target, idea=args.idea),
            "quick_start": quick_start,
        }

        if args.json:
            sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            return 0

        profile = integration_manager.get_adapter_profile(target)
        self.console.print("[cyan]Super Dev Start[/cyan]")
        self.console.print(f"[cyan]已选择宿主[/cyan]: {target}")
        self.console.print(
            f"[cyan]认证等级[/cyan]: {profile.certification_label} ({profile.certification_level})"
        )
        if selection_reason == "auto-detected":
            reasons = ", ".join(detected_meta.get(target, []))
            if reasons:
                self.console.print(f"[dim]自动选择依据: {reasons}[/dim]")
        self.console.print(f"[dim]{profile.certification_reason}[/dim]")
        if profile_saved:
            self.console.print("[green]✓[/green] 已写入宿主画像到 super-dev.yaml")
        elif profile_save_error:
            self.console.print(f"[yellow]宿主画像写入失败: {profile_save_error}[/yellow]")
        self.console.print("")
        self.console.print(quick_start)
        return 0

    def _cmd_detect(self, args) -> int:
        """宿主探测 + 接入兼容性评分"""
        from .integrations import IntegrationManager

        if not self._ensure_host_support_matrix():
            return 1

        project_dir = Path.cwd()
        integration_manager = IntegrationManager(project_dir)
        available_targets = [item.name for item in integration_manager.list_targets()]
        detected_targets, detected_meta = self._detect_host_targets(available_targets=available_targets)

        if args.host:
            targets = [args.host]
        elif args.all:
            targets = available_targets
        else:
            targets = detected_targets

        report = self._collect_host_diagnostics(
            project_dir=project_dir,
            targets=targets,
            skill_name=args.skill_name,
            check_integrate=not args.skip_integrate,
            check_skill=not args.skip_skill,
            check_slash=not args.skip_slash,
        )
        compatibility = self._build_compatibility_summary(
            report=report,
            targets=targets,
            check_integrate=not args.skip_integrate,
            check_skill=not args.skip_skill,
            check_slash=not args.skip_slash,
        )

        payload: dict[str, Any] = {
            "project_dir": str(project_dir),
            "detected_hosts": detected_targets,
            "detection_details": detected_meta,
            "selected_targets": targets,
            "report": report,
            "compatibility": compatibility,
            "usage_profiles": {
                target: self._build_host_usage_profile(
                    integration_manager=integration_manager,
                    target=target,
                )
                for target in targets
            },
        }
        if not bool(args.no_save):
            report_files = self._write_host_compatibility_report(project_dir=project_dir, payload=payload)
            payload["report_files"] = {name: str(path) for name, path in report_files.items()}

        if bool(args.save_profile):
            try:
                config_manager = ConfigManager(project_dir)
                config_manager.update(
                    host_profile_targets=targets,
                    host_profile_enforce_selected=True,
                )
                payload["host_profile_updated"] = True
            except Exception as exc:
                payload["host_profile_updated"] = False
                payload["host_profile_update_error"] = str(exc)

        if args.json:
            sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            return 0

        self.console.print("[cyan]Super Dev Host Detect[/cyan]")
        self.console.print(f"[dim]项目目录: {project_dir}[/dim]")
        if detected_targets:
            self.console.print(
                f"[cyan]自动检测到 {len(detected_targets)} 个宿主：{', '.join(detected_targets)}[/cyan]"
            )
            for target in detected_targets:
                reasons = ", ".join(detected_meta.get(target, []))
                if reasons:
                    self.console.print(f"[dim]  - {target}: {reasons}[/dim]")
        else:
            self.console.print("[yellow]未检测到宿主（可用 --all 查看全部兼容评分）[/yellow]")

        self.console.print("")
        self.console.print(
            f"[cyan]兼容性评分: {compatibility['overall_score']:.2f}/100 "
            f"(ready {compatibility['ready_hosts']}/{compatibility['total_hosts']})[/cyan]"
        )
        self.console.print(
            f"[cyan]流程一致性: {compatibility.get('flow_consistency_score', 0):.2f}/100 "
            f"({compatibility.get('flow_consistent_hosts', 0)}/{compatibility.get('total_hosts', 0)})[/cyan]"
        )
        for target in targets:
            host_compat = compatibility["hosts"].get(target, {})
            score = host_compat.get("score", 0.0)
            ready = bool(host_compat.get("ready", False))
            badge = "[green]ready[/green]" if ready else "[yellow]not-ready[/yellow]"
            self.console.print(f"  - {target}: {score:.2f}/100 {badge}")
            self._print_host_usage_guidance(
                integration_manager=integration_manager,
                target=target,
                indent="    ",
            )
        if not bool(args.no_save):
            saved_report_files = payload.get("report_files", {})
            if isinstance(saved_report_files, dict):
                json_file = saved_report_files.get("json")
                md_file = saved_report_files.get("markdown")
                if isinstance(json_file, str) and isinstance(md_file, str):
                    self.console.print(f"[dim]报告: {md_file}[/dim]")
                    self.console.print(f"[dim]数据: {json_file}[/dim]")
        if bool(args.save_profile):
            if bool(payload.get("host_profile_updated", False)):
                self.console.print("[green]✓[/green] 已更新宿主画像: host_profile_targets + host_profile_enforce_selected")
            else:
                err = payload.get("host_profile_update_error", "")
                self.console.print(f"[yellow]宿主画像更新失败: {err}[/yellow]")

        return 0

    def _cmd_update(self, args) -> int:
        latest_version = self._fetch_latest_pypi_version()
        if latest_version is None:
            self.console.print("[red]无法获取 PyPI 最新版本信息，请检查网络后重试[/red]")
            return 1

        current_version = __version__
        self.console.print(f"[cyan]当前版本[/cyan]: {current_version}")
        self.console.print(f"[cyan]PyPI 最新版本[/cyan]: {latest_version}")

        method = self._resolve_update_method(args.method)
        if args.check:
            if self._is_version_newer(latest_version, current_version):
                self.console.print("[yellow]发现新版本，可执行 `super-dev update` 完成升级[/yellow]")
            elif self._version_key(current_version) > self._version_key(latest_version):
                self.console.print("[yellow]当前本地版本高于 PyPI 最新版本，可能是尚未发布的开发版本[/yellow]")
            else:
                self.console.print("[green]✓ 当前已是最新版本[/green]")
            return 0

        if self._version_key(current_version) > self._version_key(latest_version):
            self.console.print("[yellow]当前本地版本高于 PyPI 最新版本，将继续执行升级命令以刷新当前安装[/yellow]")
        elif not self._is_version_newer(latest_version, current_version):
            self.console.print("[green]当前版本已与 PyPI 一致，将继续执行升级命令以确保安装状态最新[/green]")

        self.console.print(f"[cyan]升级方式[/cyan]: {method}")
        command = self._build_update_command(method=method)
        self.console.print(f"[dim]执行命令: {' '.join(command)}[/dim]")
        try:
            completed = subprocess.run(command, check=False)
        except FileNotFoundError:
            self.console.print(f"[red]未找到升级工具: {method}[/red]")
            return 1

        if completed.returncode != 0:
            self.console.print("[red]升级失败，请根据上面的命令手动执行[/red]")
            return completed.returncode

        from rich.panel import Panel
        self.console.print("")
        self.console.print(Panel(
            "[bold green]升级完成[/bold green]\n\n"
            "  [bold]请关闭当前终端，重新打开后再使用 super-dev[/bold]\n\n"
            "  [dim]当前进程仍加载旧版本代码，必须重启终端才能生效[/dim]\n"
            "  [dim]验证: super-dev --version[/dim]",
            border_style="green",
            expand=True,
            padding=(1, 2),
        ))
        return 0

    def _fetch_latest_pypi_version(self) -> str | None:
        try:
            response = requests.get("https://pypi.org/pypi/super-dev/json", timeout=10)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return None
        info = payload.get("info", {})
        version = info.get("version")
        return version if isinstance(version, str) and version.strip() else None

    def _resolve_update_method(self, preferred: str) -> str:
        if preferred in {"pip", "uv"}:
            return preferred
        uv_binary = shutil.which("uv")
        runtime_markers = [
            sys.executable,
            shutil.which("super-dev") or "",
            os.environ.get("UV_TOOL_BIN_DIR", ""),
            os.environ.get("PATH", ""),
        ]
        if uv_binary and any(".local/share/uv" in marker or "/uv/tools/" in marker for marker in runtime_markers):
            return "uv"
        return "uv" if uv_binary and "uv" in sys.executable.lower() else "pip"

    def _build_update_command(self, *, method: str) -> list[str]:
        if method == "uv":
            return ["uv", "tool", "upgrade", "super-dev"]
        return [sys.executable, "-m", "pip", "install", "-U", "super-dev"]

    def _is_version_newer(self, latest: str, current: str) -> bool:
        return self._version_key(latest) > self._version_key(current)

    def _version_key(self, version: str) -> tuple[int, ...]:
        parts = []
        for part in version.replace("-", ".").split("."):
            digits = "".join(ch for ch in part if ch.isdigit())
            parts.append(int(digits or 0))
        return tuple(parts)

    def _print_host_usage_guidance(
        self,
        *,
        integration_manager,
        target: str,
        indent: str = "",
    ) -> None:
        usage = self._build_host_usage_profile(
            integration_manager=integration_manager,
            target=target,
        )
        self.console.print(f"{indent}[cyan]主入口[/cyan]: {usage['primary_entry']}")
        self.console.print(
            f"{indent}认证等级: {usage['certification_label']} ({usage['certification_level']})"
        )
        self.console.print(f"{indent}使用模式: {usage['usage_mode']}")
        protocol_mode = str(usage.get("host_protocol_mode", "")).strip()
        protocol_summary = str(usage.get("host_protocol_summary", "")).strip()
        if protocol_mode or protocol_summary:
            protocol_text = protocol_summary or protocol_mode
            if protocol_mode and protocol_summary and protocol_mode != protocol_summary:
                protocol_text = f"{protocol_summary} ({protocol_mode})"
            self.console.print(f"{indent}宿主协议: {protocol_text}")
        self.console.print(f"{indent}触发命令: {usage['trigger_command']}")
        self.console.print(f"{indent}触发上下文: {usage['trigger_context']}")
        self.console.print(f"{indent}触发位置: {usage['usage_location']}")
        self.console.print(f"{indent}接入后重启: {usage['restart_required_label']}")
        precondition_label = usage.get("precondition_label", "")
        if isinstance(precondition_label, str) and precondition_label.strip():
            self.console.print(f"{indent}宿主前置条件: {precondition_label}")
        precondition_items = usage.get("precondition_items", [])
        if isinstance(precondition_items, list) and precondition_items:
            self.console.print(f"{indent}前置条件项:")
            for item in precondition_items:
                if not isinstance(item, dict):
                    continue
                item_label = str(item.get("label", "")).strip()
                item_status = str(item.get("status", "")).strip()
                item_text = item_label or item_status
                if item_text:
                    self.console.print(f"{indent}  - {item_text}")
        precondition_guidance = usage.get("precondition_guidance", [])
        if isinstance(precondition_guidance, list) and precondition_guidance:
            self.console.print(f"{indent}前置条件说明:")
            for item in precondition_guidance:
                self.console.print(f"{indent}  - {item}")
        if usage.get("certification_reason"):
            self.console.print(f"{indent}认证说明: {usage['certification_reason']}")
        official_project = usage.get("official_project_surfaces", [])
        if isinstance(official_project, list) and official_project:
            self.console.print(f"{indent}官方项目级接入面:")
            for item in official_project:
                self.console.print(f"{indent}  - {item}")
        official_user = usage.get("official_user_surfaces", [])
        if isinstance(official_user, list) and official_user:
            self.console.print(f"{indent}官方用户级接入面:")
            for item in official_user:
                self.console.print(f"{indent}  - {item}")
        observed_surfaces = usage.get("observed_compatibility_surfaces", [])
        if isinstance(observed_surfaces, list) and observed_surfaces:
            self.console.print(f"{indent}兼容增强路径:")
            for item in observed_surfaces:
                self.console.print(f"{indent}  - {item}")
        steps = usage.get("post_onboard_steps", [])
        if isinstance(steps, list) and steps:
            self.console.print(f"{indent}接入后步骤:")
            for step in steps:
                self.console.print(f"{indent}  - {step}")
        notes = usage.get("usage_notes", [])
        if isinstance(notes, list) and notes:
            self.console.print(f"{indent}使用提示:")
            for note in notes:
                self.console.print(f"{indent}  - {note}")
        smoke_prompt = usage.get("smoke_test_prompt", "")
        if isinstance(smoke_prompt, str) and smoke_prompt:
            self.console.print(f"{indent}Smoke 验收语句: {smoke_prompt}")
        smoke_steps = usage.get("smoke_test_steps", [])
        if isinstance(smoke_steps, list) and smoke_steps:
            self.console.print(f"{indent}Smoke 验收步骤:")
            for step in smoke_steps:
                self.console.print(f"{indent}  - {step}")
        smoke_signal = usage.get("smoke_success_signal", "")
        if isinstance(smoke_signal, str) and smoke_signal:
            self.console.print(f"{indent}Smoke 通过标准: {smoke_signal}")

    def _host_certification_rank(self, level: str) -> int:
        order = {"certified": 0, "compatible": 1, "experimental": 2}
        return order.get(level, 3)

    def _select_best_start_host(self, *, integration_manager, targets: list[str]) -> str:
        scored: list[tuple[int, int, int, str]] = []
        for target in targets:
            profile = integration_manager.get_adapter_profile(target)
            scored.append(
                (
                    self._host_certification_rank(profile.certification_level),
                    0 if integration_manager.supports_slash(target) else 1,
                    0 if profile.category == "cli" else 1,
                    target,
                )
            )
        scored.sort()
        return scored[0][3]

    def _recommended_start_hosts(self, *, integration_manager) -> list[dict[str, str]]:
        from .integrations import IntegrationManager

        items: list[dict[str, str]] = []
        for target in sorted(IntegrationManager.TARGETS):
            profile = integration_manager.get_adapter_profile(target)
            if profile.certification_level != "certified":
                continue
            items.append(
                {
                    "id": target,
                    "name": IntegrationManager.TARGETS[target].description,
                    "certification_label": profile.certification_label,
                }
            )
        return items

    def _build_host_trigger_example(self, *, target: str, idea: str | None) -> str:
        from .integrations import IntegrationManager

        if not idea:
            return ""
        escaped = idea.replace('"', '\\"')
        if target == "codex-cli":
            return f"{IntegrationManager.TEXT_TRIGGER_PREFIX} {idea}"
        if target == "trae":
            return f"{IntegrationManager.TEXT_TRIGGER_PREFIX} {idea}"
        if IntegrationManager.supports_slash(target):
            return f'/super-dev "{escaped}"'
        return f"{IntegrationManager.TEXT_TRIGGER_PREFIX} {idea}"

    def _build_onboard_next_steps(self, *, targets: list[str]) -> list[str]:
        from .integrations import IntegrationManager

        project_dir = Path.cwd()
        integration_manager = IntegrationManager(project_dir)
        lines: list[str] = []
        for target in targets:
            profile = integration_manager.get_adapter_profile(target)
            trigger = str(profile.trigger_command).replace("<需求描述>", "你的需求")
            line = f"{target}: 打开宿主后输入 {trigger}"
            if profile.requires_restart_after_onboard:
                line += "（先重启宿主）"
            lines.append(line)
        return lines

    def _build_host_quick_start_text(
        self,
        *,
        host_profile: dict[str, Any],
        host_id: str,
        host_name: str,
        idea: str | None,
    ) -> str:
        lines = [
            f"{host_name} 起步步骤",
            "",
            f"1. 认证等级：{host_profile.get('certification_label', '-')}"
            f" ({host_profile.get('certification_level', '-')})",
            f"2. 主入口：{host_profile.get('primary_entry', '-')}",
            f"3. 使用模式：{host_profile.get('usage_mode', '-')}",
            f"4. 触发上下文：{host_profile.get('trigger_context', '-')}",
            f"5. 接入后重启：{host_profile.get('restart_required_label', '-')}",
        ]
        reason = host_profile.get("certification_reason", "")
        if isinstance(reason, str) and reason.strip():
            lines.extend(["", "认证说明", reason])
        steps = host_profile.get("post_onboard_steps", [])
        if isinstance(steps, list) and steps:
            lines.extend(["", "接入后步骤"])
            for index, step in enumerate(steps, start=1):
                lines.append(f"{index}. {step}")
        if idea:
            lines.extend([
                "",
                "把这句放进宿主会话",
                self._build_host_trigger_example(target=host_id, idea=idea),
            ])
        lines.extend([
            "",
            "如果要重新接入或修复",
            f"super-dev setup --host {host_id} --force --yes",
            f"super-dev doctor --host {host_id} --repair --force",
        ])
        return "\n".join(lines)

    def _build_host_usage_profile(
        self,
        *,
        integration_manager,
        target: str,
    ) -> dict[str, Any]:
        profile = integration_manager.get_adapter_profile(target)
        final_trigger = str(profile.trigger_command).replace("<需求描述>", "你的需求")
        return {
            "host": profile.host,
            "category": profile.category,
            "certification_level": profile.certification_level,
            "certification_label": profile.certification_label,
            "certification_reason": profile.certification_reason,
            "certification_evidence": list(profile.certification_evidence),
            "host_protocol_mode": profile.host_protocol_mode,
            "host_protocol_summary": profile.host_protocol_summary,
            "capability_labels": dict(profile.capability_labels),
            "official_project_surfaces": list(profile.official_project_surfaces),
            "official_user_surfaces": list(profile.official_user_surfaces),
            "observed_compatibility_surfaces": list(profile.observed_compatibility_surfaces),
            "official_docs_url": profile.official_docs_url,
            "official_docs_references": list(profile.official_docs_references),
            "docs_check_status": profile.docs_check_status,
            "docs_check_summary": profile.docs_check_summary,
            "usage_mode": profile.usage_mode,
            "primary_entry": profile.primary_entry,
            "trigger_command": profile.trigger_command,
            "final_trigger": final_trigger,
            "trigger_context": profile.trigger_context,
            "usage_location": profile.usage_location,
            "requires_restart_after_onboard": profile.requires_restart_after_onboard,
            "restart_required_label": "是" if profile.requires_restart_after_onboard else "否",
            "post_onboard_steps": list(profile.post_onboard_steps),
            "usage_notes": list(profile.usage_notes),
            "smoke_test_prompt": profile.smoke_test_prompt,
            "smoke_test_steps": list(profile.smoke_test_steps),
            "smoke_success_signal": profile.smoke_success_signal,
            "precondition_status": profile.precondition_status,
            "precondition_label": profile.precondition_label,
            "precondition_guidance": list(profile.precondition_guidance),
            "precondition_signals": dict(profile.precondition_signals),
            "precondition_items": list(profile.precondition_items),
            "notes": profile.notes,
        }

    def _load_host_runtime_validation_state(self, *, project_dir: Path) -> dict[str, Any]:
        payload = load_host_runtime_validation(project_dir) or {}
        if not isinstance(payload, dict):
            return {"hosts": {}, "updated_at": ""}
        hosts = payload.get("hosts", {})
        if not isinstance(hosts, dict):
            hosts = {}
        return {
            "hosts": hosts,
            "updated_at": str(payload.get("updated_at", "")).strip(),
        }

    def _host_runtime_status_label(self, status: str) -> str:
        mapping = {
            "pending": "待真人验收",
            "passed": "已真人通过",
            "failed": "真人验收失败",
        }
        return mapping.get(status, "待真人验收")

    def _update_host_runtime_validation_state(
        self,
        *,
        project_dir: Path,
        target: str,
        status: str,
        comment: str,
        actor: str,
    ) -> tuple[dict[str, Any], Path]:
        payload = self._load_host_runtime_validation_state(project_dir=project_dir)
        hosts = dict(payload.get("hosts", {}))
        current = hosts.get(target, {})
        if not isinstance(current, dict):
            current = {}
        hosts[target] = {
            "status": status,
            "comment": comment.strip(),
            "actor": actor.strip() or "user",
            "updated_at": current.get("updated_at", ""),
        }
        file_path = save_host_runtime_validation(
            project_dir,
            {
                "hosts": hosts,
            },
        )
        updated = self._load_host_runtime_validation_state(project_dir=project_dir)
        return updated, file_path

    def _resolve_report_project_name(self, project_dir: Path) -> str:
        try:
            config = ConfigManager(project_dir).load()
            raw = config.name or project_dir.name
        except Exception:
            raw = project_dir.name
        return self._sanitize_project_name(raw)

    def _render_host_compatibility_markdown(self, payload: dict[str, Any]) -> str:
        compatibility = payload.get("compatibility", {})
        report = payload.get("report", {})
        selected_targets = payload.get("selected_targets", [])
        detected_hosts = payload.get("detected_hosts", [])
        if not isinstance(compatibility, dict):
            compatibility = {}
        if not isinstance(report, dict):
            report = {}
        if not isinstance(selected_targets, list):
            selected_targets = []
        if not isinstance(detected_hosts, list):
            detected_hosts = []

        lines = [
            "# Host Compatibility Report",
            "",
            f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
            f"- Project Dir: {payload.get('project_dir', '')}",
            f"- Detected Hosts: {', '.join(str(item) for item in detected_hosts) if detected_hosts else '(none)'}",
            f"- Selected Targets: {', '.join(str(item) for item in selected_targets) if selected_targets else '(none)'}",
            "",
            "## Summary",
            f"- Overall Score: {compatibility.get('overall_score', 0)}/100",
            f"- Ready Hosts: {compatibility.get('ready_hosts', 0)}/{compatibility.get('total_hosts', 0)}",
            f"- Enabled Checks: {', '.join(str(item) for item in compatibility.get('enabled_checks', []))}",
            "",
            "## Per-Host Scores",
            "",
            "| Host | Certification | Score | Ready | Passed/Total |",
            "|---|---|---:|---|---:|",
        ]

        host_scores = compatibility.get("hosts", {})
        if isinstance(host_scores, dict):
            for target in selected_targets:
                info = host_scores.get(target, {}) if isinstance(target, str) else {}
                if not isinstance(info, dict):
                    info = {}
                usage_profiles = payload.get("usage_profiles", {})
                certification = "-"
                if isinstance(usage_profiles, dict):
                    usage = usage_profiles.get(target, {})
                    if isinstance(usage, dict):
                        certification = str(usage.get("certification_label", "-"))
                score = info.get("score", 0)
                ready = "yes" if bool(info.get("ready", False)) else "no"
                passed = int(info.get("passed", 0))
                possible = int(info.get("possible", 0))
                lines.append(f"| {target} | {certification} | {score} | {ready} | {passed}/{possible} |")

        lines.extend(["", "## Usage Guidance", ""])
        usage_profiles = payload.get("usage_profiles", {})
        if isinstance(usage_profiles, dict):
            for target in selected_targets:
                usage = usage_profiles.get(target, {}) if isinstance(target, str) else {}
                if not isinstance(usage, dict):
                    usage = {}
                lines.append(f"### {target}")
                lines.append(
                    f"- Certification: {usage.get('certification_label', '-')} ({usage.get('certification_level', '-')})"
                )
                reason = usage.get("certification_reason", "")
                if isinstance(reason, str) and reason.strip():
                    lines.append(f"- Certification Reason: {reason}")
                evidence = usage.get("certification_evidence", [])
                if isinstance(evidence, list) and evidence:
                    lines.append("- Certification Evidence:")
                    for item in evidence:
                        lines.append(f"  - {item}")
                lines.append(f"- Primary Entry: {usage.get('primary_entry', '-')}")
                lines.append(f"- Usage Mode: {usage.get('usage_mode', '-')}")
                lines.append(f"- Trigger Command: {usage.get('trigger_command', '-')}")
                lines.append(f"- Trigger Context: {usage.get('trigger_context', '-')}")
                lines.append(f"- Restart Required: {usage.get('restart_required_label', '-')}")
                precondition_label = usage.get("precondition_label", "")
                if isinstance(precondition_label, str) and precondition_label.strip():
                    lines.append(f"- Host Preconditions: {precondition_label}")
                precondition_items = usage.get("precondition_items", [])
                if isinstance(precondition_items, list) and precondition_items:
                    lines.append("- Host Precondition Items:")
                    for item in precondition_items:
                        if not isinstance(item, dict):
                            continue
                        item_label = str(item.get("label", "")).strip()
                        item_status = str(item.get("status", "")).strip()
                        item_text = item_label or item_status
                        if item_text:
                            lines.append(f"  - {item_text}")
                precondition_guidance = usage.get("precondition_guidance", [])
                if isinstance(precondition_guidance, list) and precondition_guidance:
                    lines.append("- Host Precondition Guidance:")
                    for item in precondition_guidance:
                        lines.append(f"  - {item}")
                steps = usage.get("post_onboard_steps", [])
                if isinstance(steps, list) and steps:
                    lines.append("- Post Onboard Steps:")
                    for step in steps:
                        lines.append(f"  - {step}")
                note = usage.get("notes", "")
                if isinstance(note, str) and note.strip():
                    lines.append(f"- Notes: {note}")
                lines.append("")

        lines.extend(["## Missing Items", ""])
        hosts = report.get("hosts", {})
        if isinstance(hosts, dict):
            for target in selected_targets:
                host = hosts.get(target, {}) if isinstance(target, str) else {}
                if not isinstance(host, dict):
                    continue
                missing = host.get("missing", [])
                if not isinstance(missing, list) or not missing:
                    continue
                lines.append(f"### {target}")
                lines.append(f"- Missing: {', '.join(str(item) for item in missing)}")
                suggestions = host.get("suggestions", [])
                if isinstance(suggestions, list):
                    for suggestion in suggestions:
                        lines.append(f"- Suggestion: `{suggestion}`")
                lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _render_host_surface_audit_markdown(self, payload: dict[str, Any]) -> str:
        report = payload.get("report", {})
        compatibility = payload.get("compatibility", {})
        selected_targets = payload.get("selected_targets", [])
        detected_hosts = payload.get("detected_hosts", [])
        usage_profiles = payload.get("usage_profiles", {})
        repair_actions = payload.get("repair_actions", {})
        if not isinstance(report, dict):
            report = {}
        if not isinstance(compatibility, dict):
            compatibility = {}
        if not isinstance(selected_targets, list):
            selected_targets = []
        if not isinstance(detected_hosts, list):
            detected_hosts = []
        if not isinstance(usage_profiles, dict):
            usage_profiles = {}
        if not isinstance(repair_actions, dict):
            repair_actions = {}

        lines = [
            "# Host Surface Audit Report",
            "",
            f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
            f"- Project Dir: {payload.get('project_dir', '')}",
            f"- Detected Hosts: {', '.join(str(item) for item in detected_hosts) if detected_hosts else '(none)'}",
            f"- Selected Targets: {', '.join(str(item) for item in selected_targets) if selected_targets else '(none)'}",
            f"- Overall Score: {compatibility.get('overall_score', 0)}/100",
            "",
        ]
        if repair_actions:
            lines.extend(["## Repair Actions", ""])
            for target, actions in repair_actions.items():
                if isinstance(actions, dict):
                    action_text = ", ".join(f"{key}={value}" for key, value in actions.items())
                    lines.append(f"- {target}: {action_text}")
            lines.append("")

        hosts = report.get("hosts", {})
        if not isinstance(hosts, dict):
            hosts = {}

        for target in selected_targets:
            host = hosts.get(target, {}) if isinstance(target, str) else {}
            usage = usage_profiles.get(target, {}) if isinstance(target, str) else {}
            if not isinstance(host, dict):
                host = {}
            if not isinstance(usage, dict):
                usage = {}
            checks = host.get("checks", {})
            contract = checks.get("contract", {}) if isinstance(checks, dict) else {}
            surfaces = contract.get("surfaces", {}) if isinstance(contract, dict) else {}
            invalid_surfaces = contract.get("invalid_surfaces", {}) if isinstance(contract, dict) else {}
            lines.extend(
                [
                    f"## {target}",
                    "",
                    f"- Ready: {'yes' if bool(host.get('ready', False)) else 'no'}",
                    f"- Trigger: {usage.get('final_trigger', '-')}",
                    f"- Protocol: {usage.get('host_protocol_summary', '-')}",
                    "",
                    "| Surface | Exists | Missing Markers | Path |",
                    "|---|---|---|---|",
                ]
            )
            if isinstance(surfaces, dict):
                for surface_key, surface_info in surfaces.items():
                    if not isinstance(surface_info, dict):
                        continue
                    exists = "yes" if bool(surface_info.get("exists", False)) else "no"
                    missing = surface_info.get("missing_markers", [])
                    missing_text = ", ".join(str(item) for item in missing) if isinstance(missing, list) and missing else "-"
                    lines.append(
                        f"| {surface_key} | {exists} | {missing_text} | {surface_info.get('path', '-')} |"
                    )
            suggestions = host.get("suggestions", [])
            if isinstance(invalid_surfaces, dict) and invalid_surfaces:
                lines.extend(["", "### Fix Guidance", ""])
                for surface_key, surface_info in invalid_surfaces.items():
                    if not isinstance(surface_info, dict):
                        continue
                    missing = surface_info.get("missing_markers", [])
                    missing_text = ", ".join(str(item) for item in missing) if isinstance(missing, list) and missing else "-"
                    lines.append(f"- `{surface_key}` -> {missing_text}")
            if isinstance(suggestions, list) and suggestions:
                lines.extend(["", "### Suggested Commands", ""])
                for suggestion in suggestions:
                    lines.append(f"- `{suggestion}`")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _build_host_runtime_validation_payload(
        self,
        *,
        project_dir: Path,
        targets: list[str],
        detected_meta: dict[str, list[str]],
        report: dict[str, Any],
        usage_profiles: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        runtime_state = self._load_host_runtime_validation_state(project_dir=project_dir)
        runtime_hosts = runtime_state.get("hosts", {})
        if not isinstance(runtime_hosts, dict):
            runtime_hosts = {}
        hosts = report.get("hosts", {})
        if not isinstance(hosts, dict):
            hosts = {}
        entries: list[dict[str, Any]] = []
        blockers: list[dict[str, Any]] = []
        next_actions: list[str] = []
        for target in targets:
            host = hosts.get(target, {}) if isinstance(target, str) else {}
            usage = usage_profiles.get(target, {}) if isinstance(target, str) else {}
            runtime_entry = runtime_hosts.get(target, {}) if isinstance(target, str) else {}
            if not isinstance(host, dict):
                host = {}
            if not isinstance(usage, dict):
                usage = {}
            if not isinstance(runtime_entry, dict):
                runtime_entry = {}
            runtime_status = str(runtime_entry.get("status", "")).strip() or "pending"
            surface_ready = bool(host.get("ready", False))
            precondition_label = usage.get("precondition_label", "-")
            precondition_guidance = usage.get("precondition_guidance", [])
            precondition_items = usage.get("precondition_items", [])
            blocking_reason = ""
            recommended_action = ""
            blocker_type = ""
            if not surface_ready:
                blocking_reason = "宿主接入面仍存在 contract 缺口"
                recommended_action = f"super-dev integrate audit --target {target} --repair --force"
                blocker_type = "surface"
            elif runtime_status == "failed":
                blocking_reason = "宿主真人运行时验收失败"
                recommended_action = f"super-dev integrate audit --target {target} --repair --force"
                blocker_type = "runtime"
            elif runtime_status != "passed":
                blocking_reason = "宿主尚未完成真人运行时验收"
                recommended_action = (
                    f"super-dev integrate validate --target {target} --status passed --comment \"首轮先进入 research，三文档已真实落盘\""
                )
                blocker_type = "validation"

            if not surface_ready or runtime_status != "passed":
                blocker_entry = {
                    "host": target,
                    "type": blocker_type or "runtime",
                    "summary": blocking_reason,
                    "next_action": recommended_action,
                }
                blockers.append(blocker_entry)
                if recommended_action and recommended_action not in next_actions:
                    next_actions.append(recommended_action)

            if isinstance(precondition_guidance, list):
                for item in precondition_guidance[:2]:
                    if isinstance(item, str) and item.strip() and item not in next_actions and runtime_status != "passed":
                        next_actions.append(item.strip())

            entries.append(
                {
                    "host": target,
                    "surface_ready": surface_ready,
                    "ready_for_delivery": surface_ready and runtime_status == "passed",
                    "blocking_reason": blocking_reason,
                    "recommended_action": recommended_action,
                    "manual_runtime_status": runtime_status,
                    "manual_runtime_status_label": self._host_runtime_status_label(runtime_status),
                    "manual_runtime_comment": str(runtime_entry.get("comment", "")).strip(),
                    "manual_runtime_actor": str(runtime_entry.get("actor", "")).strip(),
                    "manual_runtime_updated_at": str(runtime_entry.get("updated_at", "")).strip(),
                    "final_trigger": usage.get("final_trigger", "-"),
                    "host_protocol_mode": usage.get("host_protocol_mode", "-"),
                    "host_protocol_summary": usage.get("host_protocol_summary", "-"),
                    "certification_label": usage.get("certification_label", "-"),
                    "precondition_label": precondition_label,
                    "precondition_guidance": precondition_guidance,
                    "precondition_items": precondition_items if isinstance(precondition_items, list) else [],
                    "smoke_test_prompt": usage.get("smoke_test_prompt", ""),
                    "smoke_success_signal": usage.get("smoke_success_signal", ""),
                    "runtime_checklist": [
                        "在宿主中使用最终触发命令进入 Super Dev 流水线。",
                        "确认首轮响应明确进入 research，而不是直接开始编码。",
                        "确认真实写入 output/*-research.md、output/*-prd.md、output/*-architecture.md、output/*-uiux.md。",
                        "确认三文档完成后暂停等待用户确认，而不是直接继续实现。",
                        "确认文档确认后能继续进入 Spec、前端运行验证、后端与交付阶段。",
                    ],
                    "pass_criteria": [
                        "首轮响应符合 Super Dev 首轮契约。",
                        "关键文档真实落盘到项目目录。",
                        "确认门真实生效。",
                        "后续恢复路径可用。",
                    ],
                }
            )

        total_hosts = len(entries)
        surface_ready_count = sum(1 for item in entries if bool(item.get("surface_ready", False)))
        runtime_passed_count = sum(1 for item in entries if item.get("manual_runtime_status") == "passed")
        runtime_failed_count = sum(1 for item in entries if item.get("manual_runtime_status") == "failed")
        runtime_pending_count = sum(1 for item in entries if item.get("manual_runtime_status") == "pending")
        fully_ready_count = sum(1 for item in entries if bool(item.get("ready_for_delivery", False)))

        return {
            "project_dir": str(project_dir),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "runtime_state_file": str(host_runtime_validation_file(project_dir)),
            "runtime_state_updated_at": runtime_state.get("updated_at", ""),
            "detected_hosts": list(detected_meta.keys()),
            "detection_details": detected_meta,
            "selected_targets": targets,
            "summary": {
                "overall_status": "ready" if total_hosts > 0 and fully_ready_count == total_hosts else "attention",
                "total_hosts": total_hosts,
                "surface_ready_count": surface_ready_count,
                "runtime_passed_count": runtime_passed_count,
                "runtime_failed_count": runtime_failed_count,
                "runtime_pending_count": runtime_pending_count,
                "fully_ready_count": fully_ready_count,
                "blocking_count": len(blockers),
                "next_actions": next_actions,
            },
            "blockers": blockers,
            "hosts": entries,
        }

    def _render_host_runtime_validation_markdown(self, payload: dict[str, Any]) -> str:
        hosts = payload.get("hosts", [])
        if not isinstance(hosts, list):
            hosts = []
        lines = [
            "# Host Runtime Validation Matrix",
            "",
            f"- Generated At (UTC): {payload.get('generated_at', '')}",
            f"- Project Dir: {payload.get('project_dir', '')}",
            f"- Detected Hosts: {', '.join(str(item) for item in payload.get('detected_hosts', [])) or '(none)'}",
            "",
        ]
        summary = payload.get("summary", {})
        if isinstance(summary, dict):
            lines.extend(
                [
                    "## Summary",
                    "",
                    f"- Overall Status: {summary.get('overall_status', '-')}",
                    f"- Fully Ready: {summary.get('fully_ready_count', 0)}/{summary.get('total_hosts', 0)}",
                    f"- Surface Ready: {summary.get('surface_ready_count', 0)}/{summary.get('total_hosts', 0)}",
                    f"- Runtime Passed: {summary.get('runtime_passed_count', 0)}",
                    f"- Runtime Failed: {summary.get('runtime_failed_count', 0)}",
                    f"- Runtime Pending: {summary.get('runtime_pending_count', 0)}",
                    "",
                ]
            )
        blockers = payload.get("blockers", [])
        if isinstance(blockers, list):
            lines.extend(["## Current Blockers", ""])
            if blockers:
                for item in blockers:
                    if not isinstance(item, dict):
                        continue
                    lines.append(
                        f"- **{item.get('host', '-')}** ({item.get('type', '-')}) {item.get('summary', '-')}"
                    )
            else:
                lines.append("- 当前没有阻塞项。")
            lines.extend(["", "## Recommended Next Actions", ""])
            next_actions = summary.get("next_actions", []) if isinstance(summary, dict) else []
            if isinstance(next_actions, list) and next_actions:
                for item in next_actions:
                    lines.append(f"- {item}")
            else:
                lines.append("- 当前宿主验收中心没有额外动作。")
            lines.append("")
        lines.extend(
            [
            "| Host | Surface Ready | Trigger | Protocol | Manual Runtime Status |",
            "|---|---|---|---|---|",
            ]
        )
        for host in hosts:
            if not isinstance(host, dict):
                continue
            lines.append(
                f"| {host.get('host', '-')} | {'yes' if bool(host.get('surface_ready', False)) else 'no'} | "
                f"{host.get('final_trigger', '-')} | {host.get('host_protocol_summary', '-')} | {host.get('manual_runtime_status_label', '-')} |"
            )

        for host in hosts:
            if not isinstance(host, dict):
                continue
            lines.extend(
                [
                    "",
                    f"## {host.get('host', '-')}",
                    "",
                    f"- Trigger: {host.get('final_trigger', '-')}",
                    f"- Protocol: {host.get('host_protocol_summary', '-')}",
                    f"- Surface Ready: {'yes' if bool(host.get('surface_ready', False)) else 'no'}",
                    f"- Manual Runtime Status: {host.get('manual_runtime_status_label', '-')}",
                    f"- Host Preconditions: {host.get('precondition_label', '-')}",
                    f"- Smoke Prompt: {host.get('smoke_test_prompt', '-')}",
                    f"- Smoke Success Signal: {host.get('smoke_success_signal', '-')}",
                    "",
                    "### Runtime Checklist",
                    "",
                ]
            )
            comment = host.get("manual_runtime_comment", "")
            if isinstance(comment, str) and comment.strip():
                lines.extend(["### Runtime Validation Note", "", f"- {comment.strip()}", ""])
            preconditions = host.get("precondition_guidance", [])
            if isinstance(preconditions, list) and preconditions:
                lines.extend(["", "### Host Precondition Guidance", ""])
                for item in preconditions:
                    lines.append(f"- {item}")
            checklist = host.get("runtime_checklist", [])
            if isinstance(checklist, list):
                for item in checklist:
                    lines.append(f"- {item}")
            lines.extend(["", "### Pass Criteria", ""])
            criteria = host.get("pass_criteria", [])
            if isinstance(criteria, list):
                for item in criteria:
                    lines.append(f"- {item}")
        return "\n".join(lines).rstrip() + "\n"

    def _write_host_surface_audit_report(
        self,
        *,
        project_dir: Path,
        payload: dict[str, Any],
    ) -> dict[str, Path]:
        project_name = self._resolve_report_project_name(project_dir)
        output_dir = project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        json_file = output_dir / f"{project_name}-host-surface-audit.json"
        md_file = output_dir / f"{project_name}-host-surface-audit.md"
        json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_file.write_text(self._render_host_surface_audit_markdown(payload), encoding="utf-8")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        history_dir = output_dir / "host-surface-audit-history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_json = history_dir / f"{project_name}-host-surface-audit-{stamp}.json"
        history_md = history_dir / f"{project_name}-host-surface-audit-{stamp}.md"
        history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        history_md.write_text(self._render_host_surface_audit_markdown(payload), encoding="utf-8")

        return {
            "json": json_file,
            "markdown": md_file,
            "history_json": history_json,
            "history_markdown": history_md,
        }

    def _render_host_hardening_markdown(self, payload: dict[str, Any]) -> str:
        compatibility = payload.get("compatibility", {})
        selected_targets = payload.get("selected_targets", [])
        hardening_results = payload.get("hardening_results", {})
        if not isinstance(compatibility, dict):
            compatibility = {}
        if not isinstance(selected_targets, list):
            selected_targets = []
        if not isinstance(hardening_results, dict):
            hardening_results = {}
        lines = [
            "# Host System Hardening Report",
            "",
            f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
            f"- Project Dir: {payload.get('project_dir', '')}",
            f"- Selected Targets: {', '.join(str(item) for item in selected_targets) if selected_targets else '(none)'}",
            f"- Compatibility Score: {compatibility.get('overall_score', 0)}/100",
            f"- Flow Consistency: {compatibility.get('flow_consistency_score', 0)}/100",
            f"- Official Doc Alignment: {((payload.get('official_compare_summary', {}) or {}).get('score', 0))}/100",
            f"- Host Parity: {((payload.get('host_parity_summary', {}) or {}).get('score', 0))}/100",
            f"- Host Gate Parity: {((payload.get('host_gate_summary', {}) or {}).get('score', 0))}/100",
            f"- Host Runtime Script Parity: {((payload.get('host_runtime_script_summary', {}) or {}).get('score', 0))}/100",
            f"- Host Recovery Parity: {((payload.get('host_recovery_summary', {}) or {}).get('score', 0))}/100",
            "",
        ]
        for target in selected_targets:
            item = hardening_results.get(target, {}) if isinstance(target, str) else {}
            if not isinstance(item, dict):
                item = {}
            plan = item.get("plan", {})
            contract = item.get("contract", {})
            official_compare = item.get("official_compare", {})
            gate_hosts = (payload.get("host_gate_summary", {}) or {}).get("hosts", {})
            gate_info = gate_hosts.get(target, {}) if isinstance(gate_hosts, dict) else {}
            runtime_script_hosts = (payload.get("host_runtime_script_summary", {}) or {}).get("hosts", {})
            runtime_script_info = runtime_script_hosts.get(target, {}) if isinstance(runtime_script_hosts, dict) else {}
            recovery_hosts = (payload.get("host_recovery_summary", {}) or {}).get("hosts", {})
            recovery_info = recovery_hosts.get(target, {}) if isinstance(recovery_hosts, dict) else {}
            lines.extend([f"## {target}", ""])
            lines.append(f"- Trigger: {plan.get('final_trigger', '-')}")
            lines.append(f"- Trigger Mode: {plan.get('trigger_mode', '-')}")
            lines.append(f"- Contract OK: {'yes' if bool((contract or {}).get('ok', False)) else 'no'}")
            if isinstance(gate_info, dict) and gate_info:
                lines.append(f"- Gate Parity: {'yes' if bool(gate_info.get('passed', False)) else 'no'}")
            if isinstance(runtime_script_info, dict) and runtime_script_info:
                lines.append(
                    f"- Runtime Script Parity: {'yes' if bool(runtime_script_info.get('passed', False)) else 'no'}"
                )
            if isinstance(recovery_info, dict) and recovery_info:
                lines.append(f"- Recovery Parity: {'yes' if bool(recovery_info.get('passed', False)) else 'no'}")
                commands = recovery_info.get("recommended_commands", [])
                if isinstance(commands, list) and commands:
                    lines.append("- Recovery Commands:")
                    for cmd in commands:
                        lines.append(f"  - {cmd}")
            if isinstance(official_compare, dict) and official_compare:
                lines.append(
                    f"- Official Compare: {official_compare.get('status', 'unknown')} "
                    f"({official_compare.get('reachable_urls', 0)}/{official_compare.get('checked_urls', 0)})"
                )
            written_files = item.get("written_files", [])
            if isinstance(written_files, list) and written_files:
                lines.append("- Updated Files:")
                for path in written_files:
                    lines.append(f"  - {path}")
            required_steps = plan.get("required_steps", [])
            if isinstance(required_steps, list) and required_steps:
                lines.append("- Required Steps:")
                for step in required_steps:
                    lines.append(f"  - {step}")
            skill_install = item.get("skill_install", {})
            if isinstance(skill_install, dict) and bool(skill_install.get("required", False)):
                lines.append(
                    f"- Skill Install: {'ok' if bool(skill_install.get('installed', False)) else 'failed'}"
                )
                if skill_install.get("path"):
                    lines.append(f"  - Path: {skill_install.get('path')}")
                if skill_install.get("error"):
                    lines.append(f"  - Error: {skill_install.get('error')}")
            invalid = (contract or {}).get("invalid_surfaces", {})
            if isinstance(invalid, dict) and invalid:
                lines.append("- Invalid Surfaces:")
                for surface_key in invalid.keys():
                    lines.append(f"  - {surface_key}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _render_host_parity_onepage_markdown(self, payload: dict[str, Any]) -> str:
        selected_targets = payload.get("selected_targets", [])
        if not isinstance(selected_targets, list):
            selected_targets = []
        hardening_results = payload.get("hardening_results", {})
        if not isinstance(hardening_results, dict):
            hardening_results = {}
        parity_index = payload.get("host_parity_index", {})
        if not isinstance(parity_index, dict):
            parity_index = {}
        lines = [
            "# Host Parity Onepage",
            "",
            f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
            f"- Project Dir: {payload.get('project_dir', '')}",
            f"- Host Parity Index: {parity_index.get('score', 0)}/100 "
            f"(threshold {parity_index.get('threshold', 95.0)}, "
            f"{'pass' if bool(parity_index.get('passed', False)) else 'fail'})",
            "",
            "| Host | Status | Failed Dimension | Next Command |",
            "|---|---|---|---|",
        ]
        official_hosts = (payload.get("official_compare_summary", {}) or {}).get("hosts", {})
        parity_hosts = (payload.get("host_parity_summary", {}) or {}).get("hosts", {})
        gate_hosts = (payload.get("host_gate_summary", {}) or {}).get("hosts", {})
        runtime_hosts = (payload.get("host_runtime_script_summary", {}) or {}).get("hosts", {})
        recovery_hosts = (payload.get("host_recovery_summary", {}) or {}).get("hosts", {})
        flow_hosts = (payload.get("compatibility", {}) or {}).get("hosts", {})
        for target in selected_targets:
            item = hardening_results.get(target, {}) if isinstance(target, str) else {}
            contract = item.get("contract", {}) if isinstance(item, dict) else {}
            recovery = recovery_hosts.get(target, {}) if isinstance(recovery_hosts, dict) else {}
            recovery_commands = recovery.get("recommended_commands", []) if isinstance(recovery, dict) else []
            dimensions: list[tuple[str, bool]] = []
            dimensions.append(("official_compare", str((official_hosts or {}).get(target, "unknown")) == "passed"))
            dimensions.append(("host_parity", bool(((parity_hosts or {}).get(target, {}) or {}).get("passed", False))))
            dimensions.append(("host_gate", bool(((gate_hosts or {}).get(target, {}) or {}).get("passed", False))))
            dimensions.append(("runtime_script", bool(((runtime_hosts or {}).get(target, {}) or {}).get("passed", False))))
            dimensions.append(("host_recovery", bool(((recovery_hosts or {}).get(target, {}) or {}).get("passed", False))))
            dimensions.append(("flow_consistency", bool(((flow_hosts or {}).get(target, {}) or {}).get("flow_consistent", False))))
            contract_ok = bool((contract or {}).get("ok", False))
            status = "PASS" if contract_ok and all(ok for _, ok in dimensions) else "FAIL"
            failed = [name for name, ok in dimensions if not ok]
            failed_text = ", ".join(failed) if failed else "-"
            next_command = recovery_commands[0] if isinstance(recovery_commands, list) and recovery_commands else "-"
            lines.append(f"| {target} | {status} | {failed_text} | `{next_command}` |")
        return "\n".join(lines).rstrip() + "\n"

    def _write_host_hardening_report(
        self,
        *,
        project_dir: Path,
        payload: dict[str, Any],
    ) -> dict[str, Path]:
        project_name = self._resolve_report_project_name(project_dir)
        output_dir = project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / f"{project_name}-host-hardening.json"
        md_file = output_dir / f"{project_name}-host-hardening.md"
        onepage_file = output_dir / f"{project_name}-host-parity-onepage.md"
        json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_file.write_text(self._render_host_hardening_markdown(payload), encoding="utf-8")
        onepage_file.write_text(self._render_host_parity_onepage_markdown(payload), encoding="utf-8")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        history_dir = output_dir / "host-hardening-history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_json = history_dir / f"{project_name}-host-hardening-{stamp}.json"
        history_md = history_dir / f"{project_name}-host-hardening-{stamp}.md"
        history_onepage = history_dir / f"{project_name}-host-parity-onepage-{stamp}.md"
        history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        history_md.write_text(self._render_host_hardening_markdown(payload), encoding="utf-8")
        history_onepage.write_text(self._render_host_parity_onepage_markdown(payload), encoding="utf-8")
        return {
            "json": json_file,
            "markdown": md_file,
            "onepage_markdown": onepage_file,
            "history_json": history_json,
            "history_markdown": history_md,
            "history_onepage_markdown": history_onepage,
        }

    def _write_host_runtime_validation_report(
        self,
        *,
        project_dir: Path,
        payload: dict[str, Any],
    ) -> dict[str, Path]:
        project_name = self._resolve_report_project_name(project_dir)
        output_dir = project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        json_file = output_dir / f"{project_name}-host-runtime-validation.json"
        md_file = output_dir / f"{project_name}-host-runtime-validation.md"
        json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_file.write_text(self._render_host_runtime_validation_markdown(payload), encoding="utf-8")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        history_dir = output_dir / "host-runtime-validation-history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_json = history_dir / f"{project_name}-host-runtime-validation-{stamp}.json"
        history_md = history_dir / f"{project_name}-host-runtime-validation-{stamp}.md"
        history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        history_md.write_text(self._render_host_runtime_validation_markdown(payload), encoding="utf-8")

        return {
            "json": json_file,
            "markdown": md_file,
            "history_json": history_json,
            "history_markdown": history_md,
        }

    def _write_host_compatibility_report(
        self,
        *,
        project_dir: Path,
        payload: dict[str, Any],
    ) -> dict[str, Path]:
        project_name = self._resolve_report_project_name(project_dir)
        output_dir = project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        json_file = output_dir / f"{project_name}-host-compatibility.json"
        md_file = output_dir / f"{project_name}-host-compatibility.md"
        json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_file.write_text(self._render_host_compatibility_markdown(payload), encoding="utf-8")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        history_dir = output_dir / "host-compatibility-history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_json = history_dir / f"{project_name}-host-compatibility-{stamp}.json"
        history_md = history_dir / f"{project_name}-host-compatibility-{stamp}.md"
        history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        history_md.write_text(self._render_host_compatibility_markdown(payload), encoding="utf-8")

        return {
            "json": json_file,
            "markdown": md_file,
            "history_json": history_json,
            "history_markdown": history_md,
        }

    def _cmd_spec(self, args) -> int:
        """Spec-Driven Development 命令"""
        from .specs import ChangeManager, SpecGenerator, SpecManager
        from .specs.models import ChangeStatus

        project_dir = Path.cwd()

        if args.spec_action == "init":
            # 初始化 SDD 目录结构
            generator = SpecGenerator(project_dir)
            agents_path, project_path = generator.init_sdd()
            config = get_config_manager(project_dir).config
            workflow_file, summary_file = self._bootstrap_project_contract(
                project_dir=project_dir,
                config=config,
            )

            self.console.print("[green]✓[/green] SDD 目录结构已初始化")
            self.console.print("  [dim].super-dev/specs/[/dim] - 当前规范")
            self.console.print("  [dim].super-dev/changes/[/dim] - 变更提案")
            self.console.print("  [dim].super-dev/archive/[/dim] - 已归档变更")
            self.console.print(f"  [dim]{workflow_file}[/dim] - 工作流契约")
            self.console.print(f"  [dim]{summary_file}[/dim] - Bootstrap 摘要")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print("  1. 编辑 .super-dev/project.md 填写项目上下文")
            self.console.print("  2. 查看 output/*-bootstrap.md 确认初始化结果")
            self.console.print("  3. 运行 'super-dev spec propose <id>' 创建变更提案")

        elif args.spec_action == "list":
            # 列出所有变更
            manager = ChangeManager(project_dir)
            status_filter = None
            if args.status:
                status_filter = ChangeStatus(args.status)

            changes = manager.list_changes(status=status_filter)

            if not changes:
                self.console.print("[dim]没有找到变更[/dim]")
                return 0

            self.console.print("[cyan]变更列表:[/cyan]")
            for change in changes:
                status_color = {
                    ChangeStatus.DRAFT: "dim",
                    ChangeStatus.PROPOSED: "yellow",
                    ChangeStatus.APPROVED: "blue",
                    ChangeStatus.IN_PROGRESS: "cyan",
                    ChangeStatus.COMPLETED: "green",
                    ChangeStatus.ARCHIVED: "dim",
                }.get(change.status, "white")

                self.console.print(
                    f"  [{status_color}]{change.id}[/] - {change.title} "
                    f"({change.status.value})"
                )
                if change.tasks:
                    rate = change.completion_rate
                    self.console.print(f"    [dim]进度: {rate:.0f}% ({sum(1 for t in change.tasks if t.status.value == 'completed')}/{len(change.tasks)} 任务)[/dim]")

        elif args.spec_action == "show":
            # 显示变更详情
            manager = ChangeManager(project_dir)
            loaded_change = manager.load_change(args.change_id)

            if not loaded_change:
                self.console.print(f"[red]变更不存在: {args.change_id}[/red]")
                return 1

            self.console.print(f"[cyan]变更详情: {loaded_change.id}[/cyan]")
            self.console.print(f"  标题: {loaded_change.title}")
            self.console.print(f"  状态: {loaded_change.status.value}")

            if loaded_change.proposal:
                self.console.print("")
                self.console.print("[cyan]提案:[/cyan]")
                if loaded_change.proposal.description:
                    self.console.print(f"  {loaded_change.proposal.description}")
                if loaded_change.proposal.motivation:
                    self.console.print(f"[dim]动机: {loaded_change.proposal.motivation}[/dim]")

            if loaded_change.tasks:
                self.console.print("")
                self.console.print("[cyan]任务:[/cyan]")
                for task in loaded_change.tasks:
                    checkbox = "[x]" if task.status.value == "completed" else "[ ]"
                    self.console.print(f"  {checkbox} {task.id}: {task.title}")

            if loaded_change.spec_deltas:
                self.console.print("")
                self.console.print("[cyan]规范变更:[/cyan]")
                for delta in loaded_change.spec_deltas:
                    self.console.print(f"  - {delta.spec_name} ({delta.delta_type.value})")

        elif args.spec_action == "propose":
            if not self._ensure_execution_gates(project_dir, action_label="创建 Spec 变更"):
                return 1
            # 创建变更提案
            generator = SpecGenerator(project_dir)
            change = generator.create_change(
                change_id=args.change_id,
                title=args.title,
                description=args.description,
                motivation=args.motivation or "",
                impact=args.impact or ""
            )
            scaffolded_files: dict[str, Path] = {}
            if not bool(getattr(args, "no_scaffold", False)):
                scaffolded_files = generator.scaffold_change_artifacts(change.id, force=False)

            self.console.print(f"[green]✓[/green] 变更提案已创建: {change.id}")
            self.console.print(f"  [dim].super-dev/changes/{change.id}/[/dim]")
            if scaffolded_files:
                self.console.print("  [dim]已生成 spec/plan/tasks/checklist 四件套[/dim]")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print(f"  1. 运行 'super-dev spec add-req {change.id} <spec> <req> <desc>' 添加需求")
            self.console.print(f"  2. 运行 'super-dev spec validate {change.id} -v' 先做规格校验")
            self.console.print(f"  3. 或 'super-dev spec show {change.id}' 查看详情")

        elif args.spec_action == "add-req":
            # 向变更添加需求
            generator = SpecGenerator(project_dir)
            delta = generator.add_requirement_to_change(
                change_id=args.change_id,
                spec_name=args.spec_name,
                requirement_name=args.req_name,
                description=args.description
            )

            self.console.print("[green]✓[/green] 需求已添加到变更")
            self.console.print(f"  规范: {delta.spec_name}")
            self.console.print(f"  需求: {args.req_name}")

        elif args.spec_action == "scaffold":
            generator = SpecGenerator(project_dir)
            try:
                generated = generator.scaffold_change_artifacts(
                    args.change_id,
                    force=bool(getattr(args, "force", False)),
                )
            except FileNotFoundError as e:
                self.console.print(f"[red]{e}[/red]")
                return 1
            self.console.print(f"[green]✓[/green] 已生成模板: {args.change_id}")
            for _, file_path in sorted(generated.items(), key=lambda item: str(item[1])):
                self.console.print(f"  [dim]{file_path.relative_to(project_dir)}[/dim]")

        elif args.spec_action == "archive":
            # 归档变更
            if not args.yes:
                self.console.print(f"[yellow]即将归档变更: {args.change_id}[/yellow]")
                self.console.print("[dim]这将把规范增量合并到主规范中[/dim]")
                response = input("确认? (y/N): ")
                if response.lower() != "y":
                    self.console.print("[dim]已取消[/dim]")
                    return 0

            change_manager = ChangeManager(project_dir)
            spec_manager = SpecManager(project_dir)

            try:
                change = change_manager.archive_change(args.change_id, spec_manager)
                self.console.print(f"[green]✓[/green] 变更已归档: {change.id}")
                self.console.print(f"  [dim].super-dev/archive/{change.id}/[/dim]")
            except FileNotFoundError as e:
                self.console.print(f"[red]{e}[/red]")
                return 1
            except Exception as e:
                self.console.print(f"[red]归档失败: {e}[/red]")
                return 1

        elif args.spec_action == "validate":
            # 验证规格格式
            from .specs import SpecValidator

            validator = SpecValidator(project_dir)

            if args.change_id:
                # 验证单个变更
                result = validator.validate_change(args.change_id)
                self.console.print(f"[cyan]验证变更: {args.change_id}[/cyan]")
            else:
                # 验证所有变更
                result = validator.validate_all()
                self.console.print("[cyan]验证所有变更[/cyan]")

            self.console.print(result.to_summary())

            if args.verbose or (not result.is_valid):
                # 显示详细信息
                for error in result.errors:
                    self.console.print(
                        f"  [red]错误[/red]: {error.message}"
                    )
                    if error.line > 0:
                        self.console.print(
                            f"    [dim]{error.file}:{error.line}[/dim]"
                        )

                for warning in result.warnings:
                    self.console.print(
                        f"  [yellow]警告[/yellow]: {warning.message}"
                    )
                    if warning.line > 0:
                        self.console.print(
                            f"    [dim]{warning.file}:{warning.line}[/dim]"
                        )

            return 0 if result.is_valid else 1

        elif args.spec_action == "quality":
            from rich.table import Table

            from .specs import SpecValidator

            validator = SpecValidator(project_dir)
            report = validator.assess_change_quality(args.change_id)
            if getattr(args, "json", False):
                sys.stdout.write(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n")
                return 0 if report.score >= 75 else 1

            score_color = "green" if report.score >= 90 else ("yellow" if report.score >= 75 else "red")
            self.console.print(
                f"[cyan]Spec 质量评估: {report.change_id}[/cyan] "
                f"[{score_color}]{report.score:.1f}[/] ({report.level})"
            )

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("维度", style="cyan", width=16)
            table.add_column("结果", style="white", width=10)
            table.add_column("说明", style="dim", width=44)
            for key, item in report.checks.items():
                passed = bool(item.get("passed", False))
                reason = str(item.get("reason", "")).strip() or "-"
                table.add_row(key, "[green]pass[/green]" if passed else "[red]fail[/red]", reason)
            self.console.print(table)

            if report.blockers:
                self.console.print("[yellow]缺口:[/yellow]")
                for blocker in report.blockers:
                    self.console.print(f"  - {blocker}")

            if report.suggestions:
                self.console.print("[cyan]建议动作:[/cyan]")
                for suggestion in report.suggestions:
                    self.console.print(f"  - {suggestion}")

            if report.action_plan:
                self.console.print("[cyan]执行计划:[/cyan]")
                for item in report.action_plan:
                    priority = str(item.get("priority", "")).strip()
                    step = str(item.get("step", "")).strip()
                    command = str(item.get("command", "")).strip()
                    prefix = f"[{priority}] " if priority else ""
                    self.console.print(f"  - {prefix}{step}")
                    if command:
                        self.console.print(f"    [dim]{command}[/dim]")

            return 0 if report.score >= 75 else 1

        elif args.spec_action == "view":
            # 交互式仪表板
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text

            console = create_console()
            change_manager = ChangeManager(project_dir)
            spec_manager = SpecManager(project_dir)

            # 获取所有变更和规范
            changes = change_manager.list_changes()
            specs = spec_manager.list_specs()

            # 标题
            title = Text.assemble(
                ("Super Dev ", "bold cyan"),
                ("Spec Dashboard", "bold white"),
            )
            console.print(Panel(title, padding=(0, 1)))

            # 变更统计
            if changes:
                table = Table(title="活跃变更", show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan", width=20)
                table.add_column("标题", style="white", width=30)
                table.add_column("状态", style="yellow", width=12)
                table.add_column("进度", style="green", width=10)
                table.add_column("任务", style="blue", width=8)

                for change in changes:
                    progress = f"{change.completion_rate:.0f}%"
                    tasks = f"{sum(1 for t in change.tasks if t.status.value == 'completed')}/{len(change.tasks)}"
                    table.add_row(
                        change.id,
                        change.title or "(无标题)",
                        change.status.value,
                        progress,
                        tasks
                    )

                console.print(table)
            else:
                console.print("[dim]没有活跃变更[/dim]")

            # 规范列表
            if specs:
                console.print("")
                specs_table = Table(title="当前规范", show_header=True, header_style="bold green")
                specs_table.add_column("规范名称", style="cyan", width=30)
                specs_table.add_column("文件路径", style="dim", width=50)

                for spec_name in specs:
                    spec_path = spec_manager.get_spec_path(spec_name)
                    specs_table.add_row(spec_name, str(spec_path.relative_to(project_dir)))

                console.print(specs_table)

            # 统计信息
            console.print("")
            stats_table = Table(show_header=False, box=None)
            stats_table.add_column("指标", style="bold white")
            stats_table.add_column("数量", style="cyan")

            stats_table.add_row("活跃变更", str(len(changes)))
            stats_table.add_row("规范文件", str(len(specs)))
            stats_table.add_row("待处理任务", str(sum(1 for c in changes for t in c.tasks if t.status.value == "pending")))

            console.print(stats_table)

            return 0

        else:
            self.console.print("[yellow]请指定 SDD 命令[/yellow]")
            return 1

        return 0

    # ==================== 辅助方法 ====================

    def _is_direct_requirement_input(self, argv: list[str]) -> bool:
        """判断是否为直达需求输入（非子命令模式）"""
        if not argv:
            return False

        first = argv[0]
        if first.startswith("-"):
            return False

        known_commands = {
            "init", "analyze", "workflow", "studio", "expert", "quality", "metrics", "preview",
            "deploy", "create", "wizard", "design", "spec", "task", "pipeline", "run", "config", "skill", "integrate",
            "onboard", "doctor", "setup", "install", "start", "bootstrap", "detect", "policy", "update", "review", "release",
            "fix", "repo-map", "impact", "regression-guard", "dependency-graph",
            "status", "jump", "confirm",
        }
        return first not in known_commands

    def _parse_direct_requirement_args(self, argv: list[str]) -> tuple[str, dict[str, Any]]:
        """
        解析直达模式参数。

        支持写法：
        - super-dev "需求描述"
        - super-dev "需求描述" --offline --domain saas --backend python
        """
        value_flags = {
            "-p": "platform",
            "--platform": "platform",
            "-f": "frontend",
            "--frontend": "frontend",
            "-b": "backend",
            "--backend": "backend",
            "-d": "domain",
            "--domain": "domain",
            "--name": "name",
            "--cicd": "cicd",
            "--quality-threshold": "quality_threshold",
        }
        bool_flags = {
            "--skip-redteam": "skip_redteam",
            "--skip-scaffold": "skip_scaffold",
            "--skip-quality-gate": "skip_quality_gate",
            "--skip-rehearsal-verify": "skip_rehearsal_verify",
            "--offline": "offline",
        }

        description_tokens: list[str] = []
        overrides: dict[str, Any] = {}
        index = 0
        while index < len(argv):
            token = argv[index]

            if token in bool_flags:
                overrides[bool_flags[token]] = True
                index += 1
                continue

            if token in value_flags:
                if index + 1 >= len(argv):
                    raise ValueError(f"参数 {token} 缺少取值")
                raw_value = argv[index + 1]
                key = value_flags[token]
                if key == "quality_threshold":
                    if not raw_value.isdigit():
                        raise ValueError("--quality-threshold 需要整数值")
                    overrides[key] = int(raw_value)
                else:
                    overrides[key] = raw_value
                index += 2
                continue

            description_tokens.append(token)
            index += 1

        description = " ".join(description_tokens).strip()
        if not description:
            raise ValueError("请提供需求描述")
        return description, overrides

    def _review_status_label(self, status: str, *, review_type: str = "docs") -> str:
        if status == "confirmed":
            return "已通过" if review_type in {"ui", "architecture", "quality"} else "已确认"
        if status == "revision_requested":
            if review_type == "ui":
                return "需改版"
            if review_type == "architecture":
                return "需返工"
            if review_type == "quality":
                return "需整改"
            return "需修改"
        return "待确认"

    def _docs_confirmation_label(self, status: str) -> str:
        return self._review_status_label(status, review_type="docs")

    def _get_docs_confirmation_state(self, project_dir: Path) -> dict[str, Any]:
        payload = load_docs_confirmation(project_dir) or {}
        return {
            "status": str(payload.get("status", "")).strip() or "pending_review",
            "comment": str(payload.get("comment", "")).strip(),
            "actor": str(payload.get("actor", "")).strip(),
            "run_id": str(payload.get("run_id", "")).strip(),
            "updated_at": str(payload.get("updated_at", "")).strip(),
            "exists": bool(payload),
            "file_path": str(docs_confirmation_file(project_dir)),
        }

    def _docs_confirmation_is_confirmed(self, project_dir: Path) -> bool:
        return self._get_docs_confirmation_state(project_dir)["status"] == "confirmed"

    def _get_ui_revision_state(self, project_dir: Path) -> dict[str, Any]:
        payload = load_ui_revision(project_dir) or {}
        return {
            "status": str(payload.get("status", "")).strip() or "pending_review",
            "comment": str(payload.get("comment", "")).strip(),
            "actor": str(payload.get("actor", "")).strip(),
            "run_id": str(payload.get("run_id", "")).strip(),
            "updated_at": str(payload.get("updated_at", "")).strip(),
            "exists": bool(payload),
            "file_path": str(ui_revision_file(project_dir)),
        }

    def _ui_revision_is_clear(self, project_dir: Path) -> bool:
        return self._get_ui_revision_state(project_dir)["status"] != "revision_requested"

    def _get_architecture_revision_state(self, project_dir: Path) -> dict[str, Any]:
        payload = load_architecture_revision(project_dir) or {}
        return {
            "status": str(payload.get("status", "")).strip() or "pending_review",
            "comment": str(payload.get("comment", "")).strip(),
            "actor": str(payload.get("actor", "")).strip(),
            "run_id": str(payload.get("run_id", "")).strip(),
            "updated_at": str(payload.get("updated_at", "")).strip(),
            "exists": bool(payload),
            "file_path": str(architecture_revision_file(project_dir)),
        }

    def _architecture_revision_is_clear(self, project_dir: Path) -> bool:
        return self._get_architecture_revision_state(project_dir)["status"] != "revision_requested"

    def _get_quality_revision_state(self, project_dir: Path) -> dict[str, Any]:
        payload = load_quality_revision(project_dir) or {}
        return {
            "status": str(payload.get("status", "")).strip() or "pending_review",
            "comment": str(payload.get("comment", "")).strip(),
            "actor": str(payload.get("actor", "")).strip(),
            "run_id": str(payload.get("run_id", "")).strip(),
            "updated_at": str(payload.get("updated_at", "")).strip(),
            "exists": bool(payload),
            "file_path": str(quality_revision_file(project_dir)),
        }

    def _quality_revision_is_clear(self, project_dir: Path) -> bool:
        return self._get_quality_revision_state(project_dir)["status"] != "revision_requested"

    def _has_core_docs(self, project_dir: Path) -> bool:
        output_dir = project_dir / "output"
        if not output_dir.exists():
            return False
        return (
            any(output_dir.glob("*-prd.md"))
            and any(output_dir.glob("*-architecture.md"))
            and any(output_dir.glob("*-uiux.md"))
        )

    def _ensure_docs_confirmation_for_execution(self, project_dir: Path, *, action_label: str) -> bool:
        if not self._has_core_docs(project_dir):
            return True
        if self._docs_confirmation_is_confirmed(project_dir):
            return True

        current = self._get_docs_confirmation_state(project_dir)
        self.console.print(f"[red]{action_label}前，必须先完成三文档确认[/red]")
        self.console.print(f"[dim]当前状态: {self._docs_confirmation_label(current['status'])}[/dim]")
        if current["comment"]:
            self.console.print(f"[dim]备注: {current['comment']}[/dim]")
        self.console.print("[dim]先查看 output/*-prd.md、*-architecture.md、*-uiux.md[/dim]")
        self.console.print('[dim]然后执行: super-dev review docs --status confirmed --comment "三文档已确认"[/dim]')
        return False

    def _ensure_ui_revision_clear_for_execution(self, project_dir: Path, *, action_label: str) -> bool:
        current = self._get_ui_revision_state(project_dir)
        if current["status"] != "revision_requested":
            return True

        self.console.print(f"[red]{action_label}前，必须先完成 UI 改版返工[/red]")
        self.console.print(f"[dim]当前状态: {self._review_status_label(current['status'], review_type='ui')}[/dim]")
        if current["comment"]:
            self.console.print(f"[dim]备注: {current['comment']}[/dim]")
        self.console.print("[dim]先更新 output/*-uiux.md，再重做前端，并重新执行 frontend runtime 与 UI review[/dim]")
        self.console.print('[dim]完成后执行: super-dev review ui --status confirmed --comment "UI 改版已通过"[/dim]')
        return False

    def _ensure_architecture_revision_clear_for_execution(self, project_dir: Path, *, action_label: str) -> bool:
        current = self._get_architecture_revision_state(project_dir)
        if current["status"] != "revision_requested":
            return True

        self.console.print(f"[red]{action_label}前，必须先完成架构返工[/red]")
        self.console.print(f"[dim]当前状态: {self._review_status_label(current['status'], review_type='architecture')}[/dim]")
        if current["comment"]:
            self.console.print(f"[dim]备注: {current['comment']}[/dim]")
        self.console.print("[dim]先更新 output/*-architecture.md，再同步调整实现方案与相关任务拆解[/dim]")
        self.console.print('[dim]完成后执行: super-dev review architecture --status confirmed --comment "架构返工已通过"[/dim]')
        return False

    def _ensure_quality_revision_clear_for_execution(self, project_dir: Path, *, action_label: str) -> bool:
        current = self._get_quality_revision_state(project_dir)
        if current["status"] != "revision_requested":
            return True

        self.console.print(f"[red]{action_label}前，必须先完成质量返工[/red]")
        self.console.print(f"[dim]当前状态: {self._review_status_label(current['status'], review_type='quality')}[/dim]")
        if current["comment"]:
            self.console.print(f"[dim]备注: {current['comment']}[/dim]")
        self.console.print("[dim]先修复质量/安全问题，重新执行 quality gate 与 release proof-pack[/dim]")
        self.console.print('[dim]完成后执行: super-dev review quality --status confirmed --comment "质量返工已通过"[/dim]')
        return False

    def _ensure_execution_gates(self, project_dir: Path, *, action_label: str) -> bool:
        return self._ensure_docs_confirmation_for_execution(
            project_dir, action_label=action_label
        ) and self._ensure_ui_revision_clear_for_execution(
            project_dir, action_label=action_label
        ) and self._ensure_architecture_revision_clear_for_execution(
            project_dir, action_label=action_label
        ) and self._ensure_quality_revision_clear_for_execution(
            project_dir, action_label=action_label
        )

    def _cmd_task(self, args) -> int:
        """Spec 任务执行与状态查看"""
        from .creators import SpecTaskExecutor
        from .specs import ChangeManager

        project_dir = Path.cwd()
        manager = ChangeManager(project_dir)

        if args.action == "list":
            changes = manager.list_changes()
            if not changes:
                self.console.print("[dim]没有找到变更[/dim]")
                return 0
            self.console.print("[cyan]变更任务概览:[/cyan]")
            for change in changes:
                completed = sum(1 for task in change.tasks if task.status.value == "completed")
                total = len(change.tasks)
                self.console.print(
                    f"  - {change.id}: {change.status.value} | 任务 {completed}/{total}"
                )
            return 0

        if not args.change_id:
            self.console.print("[red]请提供 change_id[/red]")
            return 1

        loaded_change = manager.load_change(args.change_id)
        if not loaded_change:
            self.console.print(f"[red]变更不存在: {args.change_id}[/red]")
            return 1

        if args.action == "status":
            completed = sum(1 for task in loaded_change.tasks if task.status.value == "completed")
            in_progress = sum(1 for task in loaded_change.tasks if task.status.value == "in_progress")
            pending = sum(1 for task in loaded_change.tasks if task.status.value == "pending")
            self.console.print(f"[cyan]任务状态: {loaded_change.id}[/cyan]")
            self.console.print(f"  标题: {loaded_change.title}")
            self.console.print(f"  状态: {loaded_change.status.value}")
            self.console.print(f"  已完成: {completed}")
            self.console.print(f"  进行中: {in_progress}")
            self.console.print(f"  待处理: {pending}")
            for task in loaded_change.tasks:
                marker = "[x]" if task.status.value == "completed" else "[~]" if task.status.value == "in_progress" else "[ ]"
                self.console.print(f"  {marker} {task.id} {task.title}")
            return 0

        config_manager = get_config_manager()
        config_exists = config_manager.exists()
        config = config_manager.config

        tech_stack = {
            "platform": args.platform or (config.platform if config_exists else "web"),
            "frontend": args.frontend or (self._normalize_pipeline_frontend(config.frontend) if config_exists else "react"),
            "backend": args.backend or (config.backend if config_exists else "node"),
            "domain": args.domain if args.domain is not None else (config.domain if config_exists else ""),
        }

        project_name = (
            args.project_name
            or (config.name if config_exists and config.name else args.change_id)
        )

        if not self._ensure_execution_gates(project_dir, action_label="执行 Spec 任务"):
            return 1

        executor = SpecTaskExecutor(project_dir=project_dir, project_name=project_name)
        summary = executor.execute(
            change_id=args.change_id,
            tech_stack=tech_stack,
            max_retries=max(0, int(args.max_retries)),
        )

        self.console.print("[green]✓ Spec 任务执行完成[/green]")
        self.console.print(f"  变更: {summary.change_id}")
        self.console.print(f"  完成: {summary.completed_tasks}/{summary.total_tasks}")
        self.console.print(f"  报告: {summary.report_file}")
        if summary.repaired_actions:
            self.console.print(f"  自动修复: {len(summary.repaired_actions)} 项")
        if summary.failed_tasks:
            self.console.print(f"  [yellow]未完成任务: {', '.join(summary.failed_tasks)}[/yellow]")
            return 1
        return 0

    def _normalize_pipeline_frontend(self, frontend: str) -> str:
        """将 init 的前端框架映射到 pipeline 可接受值"""
        mapping = {
            "next": "react",
            "remix": "react",
            "react-vite": "react",
            "gatsby": "react",
            "nuxt": "vue",
            "vue-vite": "vue",
            "sveltekit": "svelte",
            "astro": "react",
            "solid": "react",
            "qwik": "react",
        }
        if frontend in set(SUPPORTED_PIPELINE_FRONTENDS):
            return frontend
        return mapping.get(frontend, "react")

    def _normalize_cicd_platform(self, value: str) -> CICDPlatform:
        valid = set(SUPPORTED_CICD)
        normalized = (value or "github").lower()
        if normalized not in valid:
            raise ValueError(f"不支持的 CI/CD 平台: {value}")
        return cast(CICDPlatform, normalized)

    def _validate_host_support_matrix(self) -> list[str]:
        from .integrations import IntegrationManager
        from .skills import SkillManager

        issues: list[str] = []
        integration_gaps = IntegrationManager.coverage_gaps()
        if integration_gaps.get("missing_in_targets"):
            issues.append(
                "IntegrationManager.TARGETS 缺失宿主: "
                + ", ".join(integration_gaps["missing_in_targets"])
            )
        if integration_gaps.get("extra_in_targets"):
            issues.append(
                "IntegrationManager.TARGETS 存在未声明宿主: "
                + ", ".join(integration_gaps["extra_in_targets"])
            )
        if integration_gaps.get("missing_in_slash"):
            issues.append(
                "IntegrationManager.SLASH_COMMAND_FILES 缺失宿主: "
                + ", ".join(integration_gaps["missing_in_slash"])
            )
        if integration_gaps.get("extra_in_slash"):
            issues.append(
                "IntegrationManager.SLASH_COMMAND_FILES 存在未声明宿主: "
                + ", ".join(integration_gaps["extra_in_slash"])
            )
        if integration_gaps.get("missing_in_docs_map"):
            issues.append(
                "IntegrationManager.OFFICIAL_DOCS 缺失宿主: "
                + ", ".join(integration_gaps["missing_in_docs_map"])
            )
        if integration_gaps.get("extra_in_docs_map"):
            issues.append(
                "IntegrationManager.OFFICIAL_DOCS 存在未声明宿主: "
                + ", ".join(integration_gaps["extra_in_docs_map"])
            )

        skill_gaps = SkillManager.coverage_gaps()
        if skill_gaps.get("missing_in_skill_targets"):
            issues.append(
                "SkillManager.TARGET_PATHS 缺失宿主: "
                + ", ".join(skill_gaps["missing_in_skill_targets"])
            )
        if skill_gaps.get("extra_in_skill_targets"):
            issues.append(
                "SkillManager.TARGET_PATHS 存在未声明宿主: "
                + ", ".join(skill_gaps["extra_in_skill_targets"])
            )
        return issues

    def _ensure_host_support_matrix(self) -> bool:
        issues = self._validate_host_support_matrix()
        if not issues:
            return True
        self.console.print("[red]宿主支持矩阵配置不一致，请先修复后再执行[/red]")
        for item in issues:
            self.console.print(f"  - {item}")
        return False

    def _sanitize_project_name(self, name: str) -> str:
        """清理项目名，避免路径非法字符"""
        import re

        cleaned = re.sub(r"[\\/:*?\"<>|]+", "-", name.strip())
        cleaned = re.sub(r"\s+", "-", cleaned)
        cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
        return cleaned or "my-project"

    def _pipeline_run_state_path(self, project_dir: Path) -> Path:
        return project_dir / ".super-dev" / "runs" / "last-pipeline.json"

    def _normalize_run_status(self, status: Any) -> str:
        normalized = str(status or "").strip().lower()
        if normalized in {"success", "completed"}:
            return "completed"
        if normalized in {"failed"}:
            return "failed"
        if normalized in {"cancelled"}:
            return "cancelled"
        if normalized in {"running", "cancelling", "waiting_confirmation", "waiting_ui_revision", "waiting_architecture_revision", "waiting_quality_revision"}:
            return "running"
        if normalized in {"queued"}:
            return "queued"
        return "unknown"

    def _write_pipeline_run_state(self, project_dir: Path, payload: dict[str, Any]) -> None:
        state_file = self._pipeline_run_state_path(project_dir)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        payload_with_normalized = dict(payload)
        payload_with_normalized["status_normalized"] = self._normalize_run_status(payload_with_normalized.get("status"))
        lock_file = state_file.parent / ".runs.lock"
        lock_handle = lock_file.open("a+", encoding="utf-8")
        try:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=state_file.parent,
                prefix=".last-pipeline.",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_file.write(json.dumps(payload_with_normalized, ensure_ascii=False, indent=2))
                temp_path = Path(temp_file.name)
            os.replace(temp_path, state_file)
        finally:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            lock_handle.close()

    def _read_pipeline_run_state(self, project_dir: Path) -> dict[str, Any] | None:
        state_file = self._pipeline_run_state_path(project_dir)
        if not state_file.exists():
            return None
        try:
            raw = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(raw, dict):
            return None
        return raw

    def _resume_audit_paths(self, output_dir: Path, project_name: str) -> dict[str, Path]:
        return {
            "json": output_dir / f"{project_name}-resume-audit.json",
            "markdown": output_dir / f"{project_name}-resume-audit.md",
        }

    def _render_resume_audit_markdown(self, payload: dict[str, Any]) -> str:
        detected_stage = payload.get("detected_failed_stage", "")
        initial_stage = payload.get("initial_resume_stage", "")
        final_stage = payload.get("final_resume_stage", "")
        planned_skips = payload.get("planned_skipped_stages", [])
        if isinstance(planned_skips, list):
            skip_text = ", ".join(str(item) for item in planned_skips) if planned_skips else "-"
        else:
            skip_text = "-"

        lines = [
            "# Resume Audit",
            "",
            f"- Project: `{payload.get('project_name', '')}`",
            f"- Status: `{payload.get('status', '')}`",
            f"- Run state status: `{payload.get('run_state_status', '')}`",
            f"- Detected failed stage: `{detected_stage}`",
            f"- Initial resume stage: `{initial_stage}`",
            f"- Final resume stage: `{final_stage}`",
            f"- Planned skipped stages: `{skip_text}`",
            f"- Started at (UTC): `{payload.get('started_at', '')}`",
            f"- Finished at (UTC): `{payload.get('finished_at', '')}`",
        ]
        failure_reason = str(payload.get("failure_reason", "")).strip()
        if failure_reason:
            lines.append(f"- Failure reason: `{failure_reason}`")

        reasons = payload.get("fallback_reasons", [])
        lines.extend(["", "## Fallback Reasons", ""])
        if isinstance(reasons, list) and reasons:
            lines.extend([f"- {str(item)}" for item in reasons])
        else:
            lines.append("- None")

        return "\n".join(lines) + "\n"

    def _write_resume_audit(
        self,
        *,
        output_dir: Path,
        project_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Path]:
        files = self._resume_audit_paths(output_dir=output_dir, project_name=project_name)
        files["json"].parent.mkdir(parents=True, exist_ok=True)
        files["json"].write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        files["markdown"].write_text(self._render_resume_audit_markdown(payload), encoding="utf-8")
        return files

    def _coerce_stage_number(self, raw_stage: Any) -> int | None:
        text = str(raw_stage).strip()
        if not text.isdigit():
            return None
        return int(text)

    def _load_pipeline_metrics_payload(self, output_dir: Path, project_name: str) -> dict[str, Any] | None:
        metrics_file = output_dir / f"{project_name}-pipeline-metrics.json"
        if not metrics_file.exists():
            return None
        try:
            payload = json.loads(metrics_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def _extract_metrics_stage_details(
        self,
        metrics_payload: dict[str, Any] | None,
        stage: str,
    ) -> dict[str, Any]:
        if not isinstance(metrics_payload, dict):
            return {}
        stages = metrics_payload.get("stages", [])
        if not isinstance(stages, list):
            return {}
        for item in stages:
            if not isinstance(item, dict):
                continue
            if str(item.get("stage", "")).strip() != stage:
                continue
            details = item.get("details", {})
            if isinstance(details, dict):
                return details
            return {}
        return {}

    def _resolve_resume_start_stage(self, failed_stage: int | None, skip_redteam: bool) -> int | None:
        """
        将失败阶段映射为安全恢复起点。

        - 0-4: 仍执行全量重跑（需要重建上下文，避免不一致）
        - 5: 直接从红队继续
        - 6: 默认回退到 5（需要 redteam_report 输入）；若本次跳过红队则可从 6 开始
        - 7-8: 直接从失败阶段恢复
        - 9-12: 统一从 9 恢复，保证后续汇总变量完整
        """
        if failed_stage is None:
            return None
        if failed_stage < 5:
            return None
        if failed_stage >= 9:
            return 9
        if failed_stage == 8:
            return 8
        if failed_stage == 7:
            return 7
        if failed_stage == 6:
            return 6 if skip_redteam else 5
        return 5

    def _stage_one_artifact_paths(self, output_dir: Path, project_name: str) -> dict[str, Path]:
        return {
            "research": output_dir / f"{project_name}-research.md",
            "prd": output_dir / f"{project_name}-prd.md",
            "architecture": output_dir / f"{project_name}-architecture.md",
            "uiux": output_dir / f"{project_name}-uiux.md",
            "execution_plan": output_dir / f"{project_name}-execution-plan.md",
            "frontend_blueprint": output_dir / f"{project_name}-frontend-blueprint.md",
        }

    def _adjust_resume_stage_for_artifacts(
        self,
        *,
        project_dir: Path,
        output_dir: Path,
        project_name: str,
        resume_from_stage: int | None,
    ) -> tuple[int | None, list[str]]:
        if resume_from_stage is None:
            return None, []

        adjusted = resume_from_stage
        reasons: list[str] = []

        # 中后段恢复依赖前置文档产物，缺失时回退到第 1 阶段重建上下文。
        if adjusted in {5, 6, 7, 8}:
            required_docs = self._stage_one_artifact_paths(output_dir=output_dir, project_name=project_name)
            missing_docs = [name for name, path in required_docs.items() if not path.exists()]
            if missing_docs:
                adjusted = 1
                reasons.append(f"缺少前置文档产物: {', '.join(missing_docs)}")

        if adjusted in {4, 5, 6, 7, 8} and not self._detect_latest_change_id(project_dir):
            adjusted = 2
            reasons.append("未检测到可用 Spec 变更目录")

        if adjusted in {4, 5, 6, 7, 8}:
            frontend_runtime_report = output_dir / f"{project_name}-frontend-runtime.json"
            if not frontend_runtime_report.exists():
                adjusted = 3
                reasons.append("缺少前端运行验证报告")

        return adjusted, reasons

    def _detect_latest_change_id(self, project_dir: Path) -> str:
        changes_dir = project_dir / ".super-dev" / "changes"
        if not changes_dir.exists():
            return ""
        change_dirs = [item for item in changes_dir.iterdir() if item.is_dir()]
        if not change_dirs:
            return ""
        latest = max(change_dirs, key=lambda item: item.stat().st_mtime)
        return latest.name

    def _extract_resume_context(
        self,
        run_state: dict[str, Any] | None,
        metrics_payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {}
        if isinstance(run_state, dict):
            stored_context = run_state.get("context")
            if isinstance(stored_context, dict):
                context.update(stored_context)

        stage1_details = self._extract_metrics_stage_details(metrics_payload, "1")
        scenario = stage1_details.get("scenario")
        if (
            "scenario" not in context
            and isinstance(scenario, str)
            and scenario in {"0-1", "1-N+1"}
        ):
            context["scenario"] = scenario

        stage3_details = self._extract_metrics_stage_details(metrics_payload, "3")
        change_id = stage3_details.get("change_id")
        if "change_id" not in context and isinstance(change_id, str) and change_id.strip():
            context["change_id"] = change_id.strip()

        return context

    def _normalize_requirements_payload(self, raw: Any) -> list[dict[str, Any]]:
        import re

        if not isinstance(raw, list):
            return []

        normalized: list[dict[str, Any]] = []
        for item in raw:
            if isinstance(item, dict):
                spec_name = str(item.get("spec_name", "core")).strip() or "core"
                req_name = str(
                    item.get("req_name")
                    or item.get("name")
                    or "requirement"
                ).strip() or "requirement"
                description = str(item.get("description", "")).strip() or req_name
                scenarios = item.get("scenarios", [])
                if not isinstance(scenarios, list):
                    scenarios = []
                normalized.append(
                    {
                        "spec_name": spec_name,
                        "req_name": req_name,
                        "description": description,
                        "scenarios": scenarios,
                    }
                )
                continue

            if isinstance(item, str):
                text = item.strip()
                if not text:
                    continue
                safe_name = re.sub(r"[^a-z0-9_]+", "-", text.lower()).strip("-") or "requirement"
                normalized.append(
                    {
                        "spec_name": "core",
                        "req_name": safe_name,
                        "description": text,
                        "scenarios": [],
                    }
                )

        return normalized

    def _extract_stage_artifacts(self, details: dict[str, Any]) -> list[str]:
        artifacts: list[str] = []
        seen: set[str] = set()

        def _append_if_path(value: str) -> None:
            candidate = value.strip()
            if not candidate:
                return
            path = Path(candidate)
            if not path.is_absolute():
                path = (Path.cwd() / path).resolve()
            if not path.exists():
                return
            try:
                rel = str(path.relative_to(Path.cwd()))
            except ValueError:
                rel = str(path)
            if rel in seen:
                return
            seen.add(rel)
            artifacts.append(rel)

        def _walk(value: Any) -> None:
            if isinstance(value, str):
                _append_if_path(value)
                return
            if isinstance(value, Path):
                _append_if_path(str(value))
                return
            if isinstance(value, dict):
                for item in value.values():
                    _walk(item)
                return
            if isinstance(value, list | tuple | set):
                for item in value:
                    _walk(item)

        _walk(details)
        return artifacts

    def _extract_stage_notes(self, details: dict[str, Any]) -> list[str]:
        notes: list[str] = []
        if bool(details.get("skipped", False)):
            reason = str(details.get("reason", "manual")).strip() or "manual"
            notes.append(f"skipped:{reason}")
        if "score" in details:
            notes.append(f"score={details.get('score')}")
        if "scenario" in details:
            notes.append(f"scenario={details.get('scenario')}")
        if "critical_failures" in details and isinstance(details["critical_failures"], list):
            notes.append(f"critical_failures={len(details['critical_failures'])}")
        return notes

    def _detect_failed_stage_from_metrics_payload(self, metrics_payload: dict[str, Any] | None) -> int | None:
        if not isinstance(metrics_payload, dict):
            return None
        if bool(metrics_payload.get("success", False)):
            return None
        stages = metrics_payload.get("stages", [])
        if not isinstance(stages, list):
            return None
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            if bool(stage.get("success", False)):
                continue
            parsed = self._coerce_stage_number(stage.get("stage"))
            if parsed is not None:
                return parsed
        return None

    def _detect_failed_stage(self, output_dir: Path, project_name: str) -> int | None:
        payload = self._load_pipeline_metrics_payload(output_dir=output_dir, project_name=project_name)
        return self._detect_failed_stage_from_metrics_payload(payload)

    def _run_direct_requirement(self, description: str, direct_overrides: dict[str, Any] | None = None) -> int:
        """将 `super-dev <需求描述>` 直达路由到完整流水线"""
        if not description:
            self.console.print("[red]请提供需求描述[/red]")
            return 1

        direct_overrides = direct_overrides or {}
        config_manager = get_config_manager()
        config_exists = config_manager.exists()
        config = config_manager.config

        platform = str(direct_overrides.get("platform") or (config.platform if config_exists else "web"))
        frontend = str(
            direct_overrides.get("frontend")
            or (self._normalize_pipeline_frontend(config.frontend) if config_exists else "react")
        )
        backend = str(direct_overrides.get("backend") or (config.backend if config_exists else "node"))
        domain = str(direct_overrides.get("domain") or (config.domain if config_exists else ""))
        cicd = str(direct_overrides.get("cicd") or "all")

        if platform not in SUPPORTED_PLATFORMS:
            self.console.print(f"[red]不支持的平台: {platform}[/red]")
            return 2
        if frontend not in SUPPORTED_PIPELINE_FRONTENDS:
            self.console.print(f"[red]不支持的前端框架: {frontend}[/red]")
            return 2
        if backend not in SUPPORTED_PIPELINE_BACKENDS:
            self.console.print(f"[red]不支持的后端框架: {backend}[/red]")
            return 2
        if domain not in SUPPORTED_DOMAINS:
            self.console.print(f"[red]不支持的业务领域: {domain}[/red]")
            return 2
        if cicd not in SUPPORTED_CICD:
            self.console.print(f"[red]不支持的 CI/CD 平台: {cicd}[/red]")
            return 2

        args = argparse.Namespace(
            description=description,
            platform=platform,
            frontend=frontend,
            backend=backend,
            domain=domain,
            name=direct_overrides.get("name"),
            cicd=cicd,
            skip_redteam=bool(direct_overrides.get("skip_redteam", False)),
            skip_scaffold=bool(direct_overrides.get("skip_scaffold", False)),
            skip_quality_gate=bool(direct_overrides.get("skip_quality_gate", False)),
            skip_rehearsal_verify=bool(direct_overrides.get("skip_rehearsal_verify", False)),
            offline=bool(direct_overrides.get("offline", False)),
            quality_threshold=direct_overrides.get("quality_threshold"),
            resume=False,
        )

        self.console.print("[cyan]需求直达模式：自动执行治理流水线[/cyan]")
        self._print_governance_boundary_notice(
            "该入口只负责生成治理产物与流程约束，实际编码应在宿主会话内完成。"
        )
        return self._cmd_pipeline(args)

    def _save_tech_stack_to_config(self, project_dir: Path, tech_stack: dict, description: str) -> None:
        """保存技术栈到项目配置文件"""
        import yaml  # type: ignore[import-untyped]

        config_file = project_dir / "super-dev.yaml"

        # 读取现有配置（如果有）
        config: dict[str, Any] = {}
        if config_file.exists():
            with open(config_file, encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

        # 更新配置
        config['platform'] = tech_stack.get('platform', 'web')
        config['frontend'] = tech_stack.get('frontend', 'react')
        config['backend'] = tech_stack.get('backend', 'node')
        config['domain'] = tech_stack.get('domain', '')
        config['description'] = description

        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    def _export_deploy_remediation_templates(
        self,
        project_dir: Path,
        cicd_platform: str,
        only_missing: bool = True,
    ) -> dict:
        """导出部署修复模板：环境变量示例 + secrets 检查清单。"""
        env_hints_map = {
            "github": [
                {"name": "DOCKER_USERNAME", "description": "Docker 镜像仓库用户名"},
                {"name": "DOCKER_PASSWORD", "description": "Docker 镜像仓库密码/Token"},
                {"name": "KUBE_CONFIG_DEV", "description": "开发环境 Kubernetes kubeconfig"},
                {"name": "KUBE_CONFIG_PROD", "description": "生产环境 Kubernetes kubeconfig"},
            ],
            "gitlab": [
                {"name": "CI_REGISTRY_USER", "description": "GitLab Registry 用户名"},
                {"name": "CI_REGISTRY_PASSWORD", "description": "GitLab Registry 密码/Token"},
                {"name": "KUBE_CONTEXT_DEV", "description": "开发环境 K8s 上下文"},
                {"name": "KUBE_CONTEXT_PROD", "description": "生产环境 K8s 上下文"},
            ],
            "azure": [
                {"name": "AZURE_ACR_SERVICE_CONNECTION", "description": "Azure ACR 服务连接标识"},
                {"name": "AZURE_DEV_K8S_CONNECTION", "description": "开发环境 AKS 服务连接标识"},
                {"name": "AZURE_PROD_K8S_CONNECTION", "description": "生产环境 AKS 服务连接标识"},
            ],
            "bitbucket": [
                {"name": "REGISTRY_URL", "description": "镜像仓库地址"},
                {"name": "KUBE_CONFIG_DEV", "description": "开发环境 Kubernetes kubeconfig"},
                {"name": "KUBE_CONFIG_PROD", "description": "生产环境 Kubernetes kubeconfig"},
            ],
        }
        manual_hints_map = {
            "jenkins": [
                "Jenkins Credentials: docker-credentials",
                "Jenkins Credentials: kubeconfig-dev",
                "Jenkins Credentials: kubeconfig-prod",
            ]
        }
        platform_guidance_map = {
            "github": [
                "在 GitHub Settings > Secrets and variables > Actions 配置变量。",
                "按 dev/prod 环境拆分敏感变量。",
            ],
            "gitlab": [
                "在 GitLab Settings > CI/CD > Variables 中配置变量并启用 Masked。",
            ],
            "jenkins": [
                "在 Jenkins Credentials 中创建与流水线一致的凭据 ID。",
            ],
            "azure": [
                "在 Azure DevOps 配置 Service Connection 和 Variable Group。",
            ],
            "bitbucket": [
                "在 Bitbucket Repository variables 中配置密钥。",
            ],
        }

        def _resolve_env_hints(platform: str) -> list[dict]:
            if platform == "all":
                merged = []
                seen = set()
                for item_platform in ("github", "gitlab", "azure", "bitbucket"):
                    for item in env_hints_map.get(item_platform, []):
                        if item["name"] in seen:
                            continue
                        seen.add(item["name"])
                        merged.append(item)
                return merged
            return list(env_hints_map.get(platform, []))

        def _resolve_manual_hints(platform: str) -> list[str]:
            if platform == "all":
                return list(manual_hints_map.get("jenkins", []))
            return list(manual_hints_map.get(platform, []))

        def _resolve_guidance(platform: str) -> list[str]:
            if platform == "all":
                merged = []
                seen = set()
                for item_platform in ("github", "gitlab", "jenkins", "azure", "bitbucket"):
                    for item in platform_guidance_map.get(item_platform, []):
                        if item in seen:
                            continue
                        seen.add(item)
                        merged.append(item)
                return merged
            return list(platform_guidance_map.get(platform, []))

        def _collect_items(platform: str) -> list[dict]:
            env_hints = _resolve_env_hints(platform)
            items = []
            for item in env_hints:
                name = item["name"]
                present = bool(os.getenv(name, "").strip())
                if only_missing and present:
                    continue
                items.append(
                    {
                        "name": name,
                        "description": item["description"],
                        "present": present,
                        "template": f'{name}="<value>"',
                    }
                )
            return items

        def _write_env_example(file_path: Path, platform: str, items: list[dict]) -> None:
            lines = [
                "# Super Dev Deployment Environment Template",
                f"# Platform: {platform}",
                f"# only_missing: {str(only_missing).lower()}",
                "",
            ]
            if not items:
                lines.append("# No variables to export for current filter.")
            else:
                for item in items:
                    lines.append(f"# {item['description']}")
                    lines.append(item["template"])
                    lines.append("")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

        def _write_checklist(
            file_path: Path,
            platform: str,
            items: list[dict],
            manual_hints: list[str],
            platform_guidance: list[str],
        ) -> None:
            lines = [
                "# Deploy Remediation Checklist",
                "",
                f"- Platform: `{platform}`",
                f"- only_missing: `{str(only_missing).lower()}`",
                "",
                "## Environment Variables",
                "",
                "| Name | Status | Description | Template |",
                "|:---|:---:|:---|:---|",
            ]
            if items:
                for item in items:
                    status = "present" if item["present"] else "missing"
                    lines.append(
                        f"| `{item['name']}` | `{status}` | {item['description']} | `{item['template']}` |"
                    )
            else:
                lines.append("| - | - | No variables in current filter | - |")

            lines.extend(["", "## Platform Guidance", ""])
            if platform_guidance:
                lines.extend([f"- {line}" for line in platform_guidance])
            else:
                lines.append("- No guidance available.")

            lines.extend(["", "## Manual Requirements", ""])
            if manual_hints:
                lines.extend([f"- {line}" for line in manual_hints])
            else:
                lines.append("- No manual requirements.")

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

        output_dir = project_dir / "output" / "deploy"
        output_dir.mkdir(parents=True, exist_ok=True)

        aggregate_items = _collect_items(cicd_platform)
        env_path = project_dir / ".env.deploy.example"
        checklist_path = output_dir / f"{cicd_platform}-secrets-checklist.md"
        _write_env_example(env_path, cicd_platform, aggregate_items)
        _write_checklist(
            checklist_path,
            cicd_platform,
            aggregate_items,
            _resolve_manual_hints(cicd_platform),
            _resolve_guidance(cicd_platform),
        )

        per_platform_files = []
        if cicd_platform == "all":
            platform_dir = output_dir / "platforms"
            for platform in ("github", "gitlab", "jenkins", "azure", "bitbucket"):
                platform_items = _collect_items(platform)
                platform_env = platform_dir / f".env.deploy.{platform}.example"
                platform_checklist = platform_dir / f"{platform}-secrets-checklist.md"
                _write_env_example(platform_env, platform, platform_items)
                _write_checklist(
                    platform_checklist,
                    platform,
                    platform_items,
                    _resolve_manual_hints(platform),
                    _resolve_guidance(platform),
                )
                per_platform_files.append(
                    {
                        "platform": platform,
                        "env_file": str(platform_env),
                        "checklist_file": str(platform_checklist),
                        "items_count": len(platform_items),
                    }
                )

        return {
            "env_file": str(env_path),
            "checklist_file": str(checklist_path),
            "items_count": len(aggregate_items),
            "per_platform_files": per_platform_files,
        }

    def _print_banner(self) -> None:
        """打印欢迎横幅"""
        if self.console:
            banner = Text()
            banner.append("Super Dev ", style="bold cyan")
            banner.append(f"v{__version__}\n", style="dim")
            banner.append(__description__, style="white")
            banner.append("\n宿主负责编码，Super Dev 负责治理与交付标准", style="dim")

            self.console.print(Panel.fit(
                banner,
                title="Super Dev",
                border_style="cyan"
            ))

    def _print_governance_boundary_notice(self, message: str) -> None:
        if not self.console:
            return
        self.console.print(
            f"[dim]治理边界: {message} 宿主负责模型调用、工具使用与代码产出。[/dim]"
        )


def main() -> int:
    """主入口"""
    cli = SuperDevCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
