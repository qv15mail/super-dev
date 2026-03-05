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
import sys
import time
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, cast

try:
    from rich.console import Console
    from rich.panel import Panel
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
    HOST_PATH_PATTERNS,
    HOST_TOOL_IDS,
    PIPELINE_BACKEND_IDS,
    PIPELINE_FRONTEND_TEMPLATE_IDS,
    PLATFORM_IDS,
)
from .config import ConfigManager, ProjectConfig, get_config_manager
from .exceptions import SuperDevError
from .orchestrator import Phase, WorkflowContext, WorkflowEngine
from .utils import get_logger

CICDPlatform = Literal["github", "gitlab", "jenkins", "azure", "bitbucket", "all"]

SUPPORTED_PLATFORMS = list(PLATFORM_IDS)
SUPPORTED_PIPELINE_FRONTENDS = list(PIPELINE_FRONTEND_TEMPLATE_IDS)
SUPPORTED_INIT_FRONTENDS = list(FULL_FRONTEND_TEMPLATE_IDS)
SUPPORTED_PIPELINE_BACKENDS = list(PIPELINE_BACKEND_IDS)
SUPPORTED_DOMAINS = list(DOMAIN_IDS)
SUPPORTED_CICD = list(CICD_PLATFORM_IDS)
SUPPORTED_HOST_TOOLS = list(HOST_TOOL_IDS)


class SuperDevCLI:
    """Super Dev 命令行接口"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
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

        # workflow 命令
        workflow_parser = subparsers.add_parser(
            "workflow",
            help="运行工作流",
            description="执行 Super Dev 6 阶段工作流"
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
            choices=["prd", "architecture", "ui", "ux", "code", "all"],
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
            choices=["list", "setup", "matrix"],
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
            "--force",
            action="store_true",
            help="覆盖已存在的配置文件"
        )
        integrate_parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 输出集成矩阵（用于自动化）"
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

        # run 命令 - 运行控制（如失败恢复）
        run_parser = subparsers.add_parser(
            "run",
            help="运行控制",
            description="运行控制命令（如 pipeline 失败恢复）"
        )
        run_parser.add_argument(
            "--resume",
            action="store_true",
            help="恢复最近一次失败的 pipeline 运行",
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
        command_handler = getattr(self, f"_cmd_{parsed_args.command}", None)
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

        self.console.print("\n[dim]下一步:[/dim]")
        self.console.print("  1. 编辑 super-dev.yaml 配置项目详情")
        self.console.print("  2. 运行 'super-dev workflow' 开始开发")

        return 0

    def _cmd_analyze(self, args) -> int:
        """分析现有项目"""
        from .analyzer import ProjectAnalyzer

        project_path = Path(args.path).resolve()

        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        self.console.print(f"[cyan]正在分析项目: {project_path}[/cyan]")

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
                    self.console.print(f"[green]报告已保存到: {args.output}[/green]")
                else:
                    self.console.print(output)

            elif output_format == "markdown":
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
        from .reviewers import QualityGateChecker

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

        scenario_label = "0-1 新建项目" if gate_result.scenario == "0-1" else "1-N+1 增量开发"
        status = "[green]通过[/green]" if gate_result.passed else "[red]未通过[/red]"

        self.console.print(f"  [dim]场景: {scenario_label}[/dim]")
        self.console.print(f"  {status} 总分: {gate_result.total_score}/100")
        self.console.print(f"  [green]✓[/green] 报告: {gate_file}")

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

    def _cmd_run(self, args) -> int:
        """运行控制命令（恢复等）"""
        if not args.resume:
            self.console.print("[yellow]请指定运行控制参数，例如: super-dev run --resume[/yellow]")
            return 1

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
        if status not in {"failed", "running"}:
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
        import shutil

        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.console.print(f"[cyan]生成原型: {output_path}[/cyan]")

        frontend_dir = Path.cwd() / "output" / "frontend"
        index_file = frontend_dir / "index.html"
        css_file = frontend_dir / "styles.css"
        js_file = frontend_dir / "app.js"

        if index_file.exists():
            html = index_file.read_text(encoding="utf-8")
            output_path.write_text(html, encoding="utf-8")

            if css_file.exists():
                shutil.copyfile(css_file, output_path.parent / "styles.css")
            if js_file.exists():
                shutil.copyfile(js_file, output_path.parent / "app.js")

            self.console.print("[green]✓[/green] 已基于 output/frontend 生成可预览页面")
            return 0

        # 回退：生成文档概览预览页
        output_dir = Path.cwd() / "output"
        docs = sorted(output_dir.glob("*.md")) if output_dir.exists() else []
        rows = "\n".join(
            f"<li><a href=\"{doc.name}\" target=\"_blank\">{doc.name}</a></li>"
            for doc in docs[:20]
        ) or "<li>未找到可预览文档，请先运行 super-dev \"你的需求\" 或 super-dev create。</li>"

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
  <p class="hint">未检测到 output/frontend 前端骨架，以下为当前 output 文档列表：</p>
  <ul>{rows}</ul>
</body>
</html>
"""
        output_path.write_text(fallback_html, encoding="utf-8")
        self.console.print("[yellow]未检测到 output/frontend，已生成文档概览预览页[/yellow]")
        return 0

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

    def _cmd_create(self, args) -> int:
        """一键创建项目 - 从想法到规范"""
        from .creators import ProjectCreator

        self.console.print("[cyan]Super Dev 项目创建器[/cyan]")
        self.console.print(f"[dim]描述: {args.description}[/dim]")
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
            self.console.print(f"  3. 复制 AI 提示词: cat {prompt_file}")
            self.console.print("  4. 开始开发: 按 tasks 顺序实现并持续更新规范")

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
                    FrontendScaffoldBuilder,
                    ImplementationScaffoldBuilder,
                    RequirementParser,
                )

                parser = RequirementParser()
                scenario = parser.detect_scenario(project_dir)

                doc_generator = DocumentGenerator(
                    name=project_name,
                    description=enriched_description,
                    platform=args.platform,
                    frontend=args.frontend,
                    backend=args.backend,
                    domain=args.domain,
                    language_preferences=pipeline_config.language_preferences,
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
                plan_file.write_text(doc_generator.generate_execution_plan(scenario=scenario), encoding="utf-8")
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
                phases = parser.build_execution_phases(scenario, requirements)
                _update_run_context(
                    scenario=scenario,
                    requirements=requirements,
                )

            # ========== 第 2 阶段: 生成前端可演示骨架 ==========
            _start_stage("2", "前端可演示骨架")
            if _should_skip_for_resume(2):
                self.console.print("[yellow]第 2 阶段: 生成前端可演示骨架 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 2 阶段: 生成前端可演示骨架...[/cyan]")
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
                self.console.print("")
                _record_stage(True, details={"files": frontend_files})

            # ========== 第 3 阶段: 创建 Spec ==========
            _start_stage("3", "Spec 创建")
            if _should_skip_for_resume(3):
                self.console.print("[yellow]第 3 阶段: 创建 Spec 规范 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                self.console.print("[cyan]第 3 阶段: 创建 Spec 规范...[/cyan]")
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

            # ========== 第 4 阶段: 生成实现骨架 ==========
            _start_stage("4", "实现骨架与任务执行")
            if _should_skip_for_resume(4):
                self.console.print("[yellow]第 4 阶段: 生成前后端实现骨架 (resume 跳过)[/yellow]")
                self.console.print("")
                _record_stage(True, details={"skipped": True, "reason": "resume"})
            else:
                if not args.skip_scaffold:
                    self.console.print("[cyan]第 4 阶段: 生成前后端实现骨架...[/cyan]")
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
                    from .creators import SpecTaskExecutor

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

                status = "[green]通过[/green]" if gate_result.passed else "[red]未通过[/red]"
                self.console.print(f"  {status} 总分: {gate_result.total_score}/100")
                self.console.print(f"  [green]✓[/green] 报告: {gate_file}")
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
                    self.console.print("[yellow]  交付包标记为 incomplete，请补齐缺失项后重新打包[/yellow]")
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

        if args.action == "matrix":
            targets: list[str] | None = [args.target] if args.target else None
            profiles = manager.list_adapter_profiles(targets=targets)
            if args.json:
                payload = [profile.to_dict() for profile in profiles]
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
                self.console.print(f"  模型提供方: {profile.host_model_provider}")
                docs_badge = "verified" if profile.docs_verified else "pending"
                docs_url = profile.official_docs_url or "-"
                self.console.print(f"  官方文档: {docs_url} ({docs_badge})")
                self.console.print(f"  主入口: {profile.primary_entry}")
                self.console.print(f"  终端入口: {profile.terminal_entry}")
                self.console.print(f"  终端范围: {profile.terminal_entry_scope}")
                self.console.print(f"  规则文件: {', '.join(profile.integration_files)}")
                self.console.print(f"  Slash 文件: {profile.slash_command_file}")
                self.console.print(f"  Skill 目录: {profile.skill_dir}")
                commands = ", ".join(profile.detection_commands) if profile.detection_commands else "-"
                paths = ", ".join(profile.detection_paths) if profile.detection_paths else "-"
                self.console.print(f"  探测命令: {commands}")
                self.console.print(f"  探测路径: {paths}")
                self.console.print(f"  备注: {profile.notes}")
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

        self.console.print("[cyan]请选择宿主 AI Coding 工具（可多选）:[/cyan]")
        for idx, target in enumerate(available_targets, 1):
            self.console.print(f"  {idx}. {target}")
        self.console.print("[dim]输入编号（逗号分隔），直接回车表示全部[/dim]")
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

            for pattern in HOST_PATH_PATTERNS.get(target, []):
                expanded = os.path.expanduser(pattern)
                if glob.glob(expanded):
                    reasons.append(f"path:{pattern}")
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
        for target in available_targets:
            integration_files = IntegrationManager.TARGETS[target].files
            skill_dir = SkillManager.TARGET_PATHS.get(target, "")

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
            has_skill = bool(skill_dir) and (project_dir / skill_dir).exists()
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

        integration_targets = IntegrationManager.TARGETS
        skill_paths = SkillManager.TARGET_PATHS

        report: dict[str, Any] = {"hosts": {}, "overall_ready": True}
        for target in targets:
            host_report: dict[str, Any] = {
                "ready": True,
                "checks": {},
                "missing": [],
                "suggestions": [],
            }

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

            if check_skill:
                skill_file = project_dir / skill_paths[target] / skill_name / "SKILL.md"
                skill_ok = skill_file.exists()
                host_report["checks"]["skill"] = {"ok": skill_ok, "file": str(skill_file)}
                if not skill_ok:
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
                        "mode": "skill-only",
                    }

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

        enabled_checks = []
        if check_integrate:
            enabled_checks.append("integrate")
        if check_skill:
            enabled_checks.append("skill")
        if check_slash and any(IntegrationManager.supports_slash(target) for target in targets):
            enabled_checks.append("slash")

        per_host: dict[str, dict[str, Any]] = {}
        total_passed = 0
        total_possible = 0
        ready_hosts = 0
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
            score = round((passed / possible) * 100, 2) if possible > 0 else 100.0
            per_host[target] = {
                "score": score,
                "passed": passed,
                "possible": possible,
                "ready": bool(host.get("ready", False)) if isinstance(host, dict) else False,
            }
            total_passed += passed
            total_possible += possible
            if bool(host.get("ready", False)) if isinstance(host, dict) else False:
                ready_hosts += 1

        overall_score = round((total_passed / total_possible) * 100, 2) if total_possible > 0 else 100.0
        return {
            "overall_score": overall_score,
            "ready_hosts": ready_hosts,
            "total_hosts": len(targets),
            "enabled_checks": enabled_checks,
            "hosts": per_host,
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
            try:
                if check_integrate and "integrate" in missing:
                    integration_manager.setup(target=target, force=force)
                    host_actions["integrate"] = "fixed"
            except Exception as exc:
                host_actions["integrate"] = f"failed: {exc}"

            try:
                if check_skill and "skill" in missing:
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
                if check_slash and integration_manager.supports_slash(target):
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

        available_targets = [item.name for item in integration_manager.list_targets()]
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
        setattr(args, "_selected_targets", list(targets))

        self.console.print("[cyan]开始执行 Onboard...[/cyan]")
        has_error = False
        for target in targets:
            self.console.print(f"[cyan]- {target}[/cyan]")

            if not args.skip_integrate:
                try:
                    written_files = integration_manager.setup(target=target, force=args.force)
                    if written_files:
                        for item in written_files:
                            self.console.print(f"  [green]✓[/green] 集成规则: {item}")
                    else:
                        self.console.print("  [dim]- 集成规则已存在（可加 --force 覆盖）[/dim]")
                except Exception as exc:
                    has_error = True
                    self.console.print(f"  [red]✗[/red] 集成失败: {exc}")

            if not args.skip_skill:
                try:
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
                        self.console.print("  [dim]- 该宿主为 Skill-only 模式，已跳过 /super-dev 映射[/dim]")
                except Exception as exc:
                    has_error = True
                    self.console.print(f"  [red]✗[/red] /super-dev 映射失败: {exc}")

        self.console.print("")
        if has_error:
            self.console.print("[red]Onboard 完成（部分失败）[/red]")
            return 1

        self.console.print("[green]✓ Onboard 完成[/green]")
        self.console.print("[cyan]在宿主工具里触发方式:[/cyan]")
        self.console.print('  - 原生 slash 宿主: /super-dev "你的需求"')
        self.console.print('  - Skill-only 宿主: 调用 super-dev-core Skill，再按 output/* 与 tasks.md 执行')
        self.console.print("[dim]终端 super-dev \"你的需求\" 仅触发本地编排，不替代宿主会话编码[/dim]")
        return 0

    def _cmd_doctor(self, args) -> int:
        """诊断宿主接入状态"""
        from .integrations import IntegrationManager

        if not self._ensure_host_support_matrix():
            return 1

        project_dir = Path.cwd()
        available_targets = [item.name for item in IntegrationManager(project_dir).list_targets()]
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
            f"[cyan]兼容性评分: {compatibility['overall_score']:.2f}/100 "
            f"(ready {compatibility['ready_hosts']}/{compatibility['total_hosts']})[/cyan]"
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
        for target in targets:
            host = report["hosts"][target]
            if host["ready"]:
                self.console.print(f"[green]✓ {target}[/green] ready")
                continue
            self.console.print(f"[yellow]! {target}[/yellow] not ready")
            for check_name in host.get("missing", []):
                self.console.print(f"  [yellow]- 缺失: {check_name}[/yellow]")
            for suggestion in host.get("suggestions", []):
                self.console.print(f"  [dim]建议: {suggestion}[/dim]")

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

    def _cmd_detect(self, args) -> int:
        """宿主探测 + 接入兼容性评分"""
        from .integrations import IntegrationManager

        if not self._ensure_host_support_matrix():
            return 1

        project_dir = Path.cwd()
        available_targets = [item.name for item in IntegrationManager(project_dir).list_targets()]
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
        for target in targets:
            host_compat = compatibility["hosts"].get(target, {})
            score = host_compat.get("score", 0.0)
            ready = bool(host_compat.get("ready", False))
            badge = "[green]ready[/green]" if ready else "[yellow]not-ready[/yellow]"
            self.console.print(f"  - {target}: {score:.2f}/100 {badge}")
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
            "| Host | Score | Ready | Passed/Total |",
            "|---|---:|---|---:|",
        ]

        host_scores = compatibility.get("hosts", {})
        if isinstance(host_scores, dict):
            for target in selected_targets:
                info = host_scores.get(target, {}) if isinstance(target, str) else {}
                if not isinstance(info, dict):
                    info = {}
                score = info.get("score", 0)
                ready = "yes" if bool(info.get("ready", False)) else "no"
                passed = int(info.get("passed", 0))
                possible = int(info.get("possible", 0))
                lines.append(f"| {target} | {score} | {ready} | {passed}/{possible} |")

        lines.extend(["", "## Missing Items", ""])
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

            self.console.print("[green]✓[/green] SDD 目录结构已初始化")
            self.console.print("  [dim].super-dev/specs/[/dim] - 当前规范")
            self.console.print("  [dim].super-dev/changes/[/dim] - 变更提案")
            self.console.print("  [dim].super-dev/archive/[/dim] - 已归档变更")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print("  1. 编辑 .super-dev/project.md 填写项目上下文")
            self.console.print("  2. 运行 'super-dev spec propose <id>' 创建变更提案")

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
            # 创建变更提案
            generator = SpecGenerator(project_dir)
            change = generator.create_change(
                change_id=args.change_id,
                title=args.title,
                description=args.description,
                motivation=args.motivation or "",
                impact=args.impact or ""
            )

            self.console.print(f"[green]✓[/green] 变更提案已创建: {change.id}")
            self.console.print(f"  [dim].super-dev/changes/{change.id}/[/dim]")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print(f"  1. 运行 'super-dev spec add-req {change.id} <spec> <req> <desc>' 添加需求")
            self.console.print(f"  2. 或 'super-dev spec show {change.id}' 查看详情")

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

        elif args.spec_action == "view":
            # 交互式仪表板
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text

            console = Console()
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
            "onboard", "doctor", "setup", "install", "detect", "policy",
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

    def _write_pipeline_run_state(self, project_dir: Path, payload: dict[str, Any]) -> None:
        state_file = self._pipeline_run_state_path(project_dir)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

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

        # 若未来允许从第 4 阶段恢复，需要确保 Spec 变更存在。
        if adjusted == 4 and not self._detect_latest_change_id(project_dir):
            adjusted = 3
            reasons.append("未检测到可用 Spec 变更目录")

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

        self.console.print("[cyan]需求直达模式：自动执行完整流水线[/cyan]")
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

            self.console.print(Panel.fit(
                banner,
                title="Super Dev",
                border_style="cyan"
            ))


def main() -> int:
    """主入口"""
    cli = SuperDevCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
