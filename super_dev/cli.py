# -*- coding: utf-8 -*-
"""
开发：Excellent（11964948@qq.com）
功能：Super Dev CLI 主入口
作用：提供命令行界面，统一访问所有功能
创建时间：2025-12-30
最后修改：2025-01-29
"""

import sys
import os
import argparse
import traceback
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from . import __version__, __description__
from .config import get_config_manager, ConfigManager
from .orchestrator import WorkflowEngine, Phase
from .exceptions import SuperDevError, ConfigurationError, ValidationError
from .utils import get_logger


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
            choices=["web", "mobile", "wechat", "desktop"],
            default="web",
            help="目标平台"
        )
        init_parser.add_argument(
            "-f", "--frontend",
            choices=[
                "next", "remix", "react-vite", "gatsby",
                "nuxt", "vue-vite",
                "angular",
                "sveltekit",
                "astro", "solid", "qwik",
                "none"
            ],
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
            choices=["node", "python", "go", "java", "none"],
            default="node",
            help="后端框架"
        )
        init_parser.add_argument(
            "--domain",
            choices=["", "fintech", "ecommerce", "medical", "social", "iot", "education"],
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
            choices=["github", "gitlab", "jenkins", "azure", "bitbucket", "all"],
            help="生成 CI/CD 配置"
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
            choices=["claude-code", "codex-cli", "opencode", "cursor", "qoder", "trae", "codebuddy", "antigravity"],
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
            choices=["list", "setup"],
            help="操作类型"
        )
        integrate_parser.add_argument(
            "-t", "--target",
            choices=["claude-code", "codex-cli", "opencode", "cursor", "qoder", "trae", "codebuddy", "antigravity"],
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
            choices=["web", "mobile", "wechat", "desktop"],
            default="web",
            help="目标平台"
        )
        create_parser.add_argument(
            "-f", "--frontend",
            choices=["react", "vue", "angular", "svelte", "none"],
            default="react",
            help="前端框架"
        )
        create_parser.add_argument(
            "-b", "--backend",
            choices=["node", "python", "go", "java", "none"],
            default="node",
            help="后端框架"
        )
        create_parser.add_argument(
            "-d", "--domain",
            choices=["", "fintech", "ecommerce", "medical", "social", "iot", "education", "auth", "content"],
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
        spec_init_parser = spec_subparsers.add_parser(
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
            choices=["web", "mobile", "wechat", "desktop"],
            default="web",
            help="目标平台"
        )
        pipeline_parser.add_argument(
            "-f", "--frontend",
            choices=["react", "vue", "angular", "svelte", "none"],
            default="react",
            help="前端框架"
        )
        pipeline_parser.add_argument(
            "-b", "--backend",
            choices=["node", "python", "go", "java", "none"],
            default="node",
            help="后端框架"
        )
        pipeline_parser.add_argument(
            "-d", "--domain",
            choices=["", "fintech", "ecommerce", "medical", "social", "iot", "education", "auth", "content"],
            default="",
            help="业务领域"
        )
        pipeline_parser.add_argument(
            "--name",
            help="项目名称 (默认根据描述生成)"
        )
        pipeline_parser.add_argument(
            "--cicd",
            choices=["github", "gitlab", "jenkins", "azure", "bitbucket", "all"],
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

        return parser

    def run(self, args: Optional[list] = None) -> int:
        """
        运行 CLI

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        argv = list(args) if args is not None else sys.argv[1:]

        # 直达入口：`super-dev <需求描述>`
        if self._is_direct_requirement_input(argv):
            return self._run_direct_requirement(" ".join(argv).strip())

        parsed_args = self.parser.parse_args(argv)

        if parsed_args.command is None:
            self._print_banner()
            self.parser.print_help()
            return 0

        # 路由到对应命令
        command_handler = getattr(self, f"_cmd_{parsed_args.command}", None)
        if command_handler is None:
            self.console.print(f"[red]未知命令: {parsed_args.command}[/red]")
            return 1

        try:
            return command_handler(parsed_args)

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

        self.console.print(f"\n[dim]下一步:[/dim]")
        self.console.print(f"  1. 编辑 super-dev.yaml 配置项目详情")
        self.console.print(f"  2. 运行 'super-dev workflow' 开始开发")

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
                self.console.print(f"[cyan]项目分析报告[/cyan]")
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
            self.logger.error(f"分析失败: 文件不存在", extra={'path': str(e)})
            return 1

        except PermissionError as e:
            self.console.print(f"[red]权限不足: {e}[/red]")
            self.logger.error(f"分析失败: 权限错误", extra={'path': str(e)})
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
        config_manager = get_config_manager()

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
        engine = WorkflowEngine()
        results = asyncio.run(engine.run(phases=phases))

        # 检查是否全部成功
        all_success = all(r.success for r in results.values())

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
        from .experts import list_experts, has_expert, save_expert_advice

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
        ) or "<li>未找到可预览文档，请先运行 super-dev create 或 super-dev pipeline。</li>"

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
        from .deployers import CICDGenerator

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

        platform = args.cicd or "github"
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
        return 0

    def _cmd_create(self, args) -> int:
        """一键创建项目 - 从想法到规范"""
        from .creators import ProjectCreator

        self.console.print(f"[cyan]Super Dev 项目创建器[/cyan]")
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
            self.console.print(f"  1. 查看生成的文档:")
            self.console.print(f"     - PRD: output/{project_name}-prd.md")
            self.console.print(f"     - 架构: output/{project_name}-architecture.md")
            self.console.print(f"     - UI/UX: output/{project_name}-uiux.md")
            self.console.print(f"     - 执行路线图: output/{project_name}-execution-plan.md")
            self.console.print(f"     - 前端蓝图: output/{project_name}-frontend-blueprint.md")
            self.console.print(f"  2. 查看规范: super-dev spec show {change_id}")
            self.console.print(f"  3. 复制 AI 提示词: cat {prompt_file}")
            self.console.print(f"  4. 开始开发: 按 tasks 顺序实现并持续更新规范")

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
            self.console.print(f"[cyan]生成设计系统[/cyan]")
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

            self.console.print(f"[green]设计系统已生成:[/green]\n")
            self.console.print(f"  名称: {design_system.name}")
            self.console.print(f"  描述: {design_system.description}")

            if design_system.aesthetic:
                self.console.print(f"  美学方向: {design_system.aesthetic.name}")
                self.console.print(f"  差异化特征: {design_system.aesthetic.differentiation}")

            self.console.print(f"\n[cyan]生成文件...[/cyan]")

            output_dir = Path(args.output)
            generated_files = generator.generate_documentation(design_system, output_dir)

            for file_path in generated_files:
                self.console.print(f"  [green]✓[/green] {file_path}")

            self.console.print(f"\n[dim]下一步:[/dim]")
            self.console.print(f"  1. 查看 {output_dir / 'DESIGN_SYSTEM.md'} 了解设计系统")
            self.console.print(f"  2. 使用 {output_dir / 'design-tokens.css'} 导入 CSS 变量")
            self.console.print(f"  3. 使用 {output_dir / 'tailwind.config.json'} 配置 Tailwind")

            return 0

        elif args.design_command == "tokens":
            # 生成 design tokens
            self.console.print(f"[cyan]生成 design tokens[/cyan]")
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
                patterns = landing_gen.list_patterns()
                self.console.print(f"\n[green]可用的 Landing 页面模式 ({len(patterns)} 个):[/green]\n")
                for i, pattern in enumerate(patterns, 1):
                    self.console.print(f"  {i}. {pattern}")
                self.console.print()
                return 0

            # 智能推荐
            if hasattr(args, 'product_type') and args.product_type:
                self.console.print(f"[cyan]智能推荐 Landing 页面模式[/cyan]")
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

                results = landing_gen.search(query, max_results=args.max_results)

                if not results:
                    self.console.print("[yellow]未找到匹配的模式[/yellow]")
                    return 1

                self.console.print(f"[green]找到 {len(results)} 个结果:[/green]\n")

                for idx, pattern in enumerate(results, 1):
                    self.console.print(f"[cyan]{idx}. {pattern.name}[/cyan]")
                    self.console.print(f"    {pattern.description}")
                    self.console.print(f"    适合: {', '.join(pattern.best_for)}")
                    self.console.print(f"    复杂度: {pattern.complexity}")
                    self.console.print()

                return 0

            # 默认显示所有模式
            patterns = landing_gen.list_patterns()
            self.console.print(f"\n[green]可用的 Landing 页面模式 ({len(patterns)} 个):[/green]\n")
            for i, pattern in enumerate(patterns, 1):
                self.console.print(f"  {i}. {pattern}")
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
                self.console.print(f"[cyan]推荐图表类型[/cyan]")
                self.console.print(f"  数据描述: {data_description}")
                self.console.print(f"  框架: {args.framework}")
                self.console.print()

                recommendations = chart_recommender.recommend(
                    data_description=data_description,
                    framework=args.framework,
                    max_results=args.max_results
                )

                if not recommendations:
                    self.console.print("[yellow]未找到合适的图表类型[/yellow]")
                    return 1

                self.console.print(f"[green]推荐结果:[/green]\n")

                for idx, rec in enumerate(recommendations, 1):
                    confidence_pct = int(rec.confidence * 100)
                    self.console.print(f"[cyan]{idx}. {rec.chart_type.name}[/cyan] (置信度: {confidence_pct}%)")
                    self.console.print(f"    {rec.chart_type.description}")
                    self.console.print(f"    理由: {rec.reasoning}")
                    self.console.print(f"    推荐库: {rec.library_recommendation}")
                    self.console.print(f"    无障碍: {rec.chart_type.accessibility_notes}")
                    if rec.alternatives:
                        self.console.print(f"    替代方案: {', '.join([a.name for a in rec.alternatives])}")
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
                self.console.print(f"[cyan]快速见效的 UX 改进建议[/cyan]\n")

                quick_wins = ux_guide.get_quick_wins(max_results=args.max_results)

                if not quick_wins:
                    self.console.print("[yellow]未找到快速见效的建议[/yellow]")
                    return 1

                for idx, rec in enumerate(quick_wins, 1):
                    self.console.print(f"[cyan]{idx}. {rec.guideline.topic}[/cyan] ({rec.guideline.domain.value})")
                    self.console.print(f"    [green]最佳实践:[/green] {rec.guideline.best_practice}")
                    self.console.print(f"    [red]反模式:[/red] {rec.guideline.anti_pattern}")
                    self.console.print(f"    影响: {rec.guideline.impact}")
                    self.console.print(f"    优先级: {rec.priority} | 实现难度: {rec.implementation_effort} | 用户影响: {rec.user_impact}")
                    if rec.resources:
                        self.console.print(f"    资源: {', '.join(rec.resources)}")
                    self.console.print()

                return 0

            # 检查清单
            if hasattr(args, 'checklist') and args.checklist:
                self.console.print(f"[cyan]UX 检查清单[/cyan]\n")

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

                recommendations = ux_guide.search(
                    query=query,
                    domain=args.domain if hasattr(args, 'domain') else None,
                    max_results=args.max_results
                )

                if not recommendations:
                    self.console.print("[yellow]未找到匹配的 UX 指南[/yellow]")
                    return 1

                self.console.print(f"[green]找到 {len(recommendations)} 个结果:[/green]\n")

                for idx, rec in enumerate(recommendations, 1):
                    self.console.print(f"[cyan]{idx}. {rec.guideline.topic}[/cyan] ({rec.guideline.domain.value})")
                    self.console.print(f"    [green]最佳实践:[/green] {rec.guideline.best_practice}")
                    self.console.print(f"    [red]反模式:[/red] {rec.guideline.anti_pattern}")
                    self.console.print(f"    影响: {rec.guideline.impact}")
                    self.console.print(f"    优先级: {rec.priority} | 实现难度: {rec.implementation_effort} | 用户影响: {rec.user_impact}")
                    if rec.resources:
                        self.console.print(f"    资源: {', '.join(rec.resources)}")
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
                patterns = tech_engine.get_patterns(stack_name)

                if not patterns:
                    self.console.print(f"[yellow]未找到 {stack_name} 的设计模式[/yellow]")
                    return 1

                self.console.print(f"\n[cyan]{stack_name} 设计模式 ({len(patterns)} 个):[/cyan]\n")

                for idx, pattern in enumerate(patterns, 1):
                    self.console.print(f"[cyan]{idx}. {pattern.name}[/cyan]")
                    self.console.print(f"    描述: {pattern.description}")
                    self.console.print(f"    使用场景: {pattern.use_case}")
                    if pattern.pros:
                        self.console.print(f"    优点: {', '.join(pattern.pros)}")
                    if pattern.cons:
                        self.console.print(f"    缺点: {', '.join(pattern.cons)}")
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

            recommendations = tech_engine.search_practices(
                stack=stack_name,
                query=query,
                category=category,
                max_results=args.max_results
            )

            if not recommendations:
                self.console.print("[yellow]未找到匹配的最佳实践[/yellow]")
                return 1

            for idx, rec in enumerate(recommendations, 1):
                self.console.print(f"[cyan]{idx}. {rec.practice.topic}[/cyan] ({rec.practice.category.value})")
                self.console.print(f"    [green]最佳实践:[/green] {rec.practice.practice}")
                self.console.print(f"    [red]反模式:[/red] {rec.practice.anti_pattern}")
                self.console.print(f"    好处: {rec.practice.benefits}")
                self.console.print(f"    优先级: {rec.priority} | 复杂度: {rec.practice.complexity}")
                if rec.context:
                    self.console.print(f"    上下文: {rec.context}")
                if rec.alternatives:
                    self.console.print(f"    替代方案: {', '.join(rec.alternatives)}")
                if rec.resources:
                    self.console.print(f"    资源: {', '.join(rec.resources)}")
                if rec.practice.code_example:
                    self.console.print(f"    代码示例:\n    [dim]{rec.practice.code_example[:200]}...[/dim]")
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
                results = codegen.search_components(
                    query=args.search,
                    framework=args.framework if hasattr(args, 'framework') else None
                )

                if not results:
                    self.console.print(f"[yellow]未找到匹配的组件: {args.search}[/yellow]")
                    return 1

                self.console.print(f"\n[green]找到 {len(results)} 个组件:[/green]\n")

                for idx, snippet in enumerate(results, 1):
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
                self.console.print(f"使用 --list 查看可用组件")
                return 1

            self.console.print(f"[green]组件名称:[/green] {component_name}")
            self.console.print(f"[green]描述:[/green] {component.description}\n")

            self.console.print(f"[cyan]代码:[/cyan]")
            self.console.print(f"```{framework}")
            self.console.print(component.code)
            self.console.print("```\n")

            if component.imports:
                self.console.print(f"[cyan]导入语句:[/cyan]")
                for imp in component.imports:
                    self.console.print(f"  {imp}")
                self.console.print()

            if component.dependencies:
                self.console.print(f"[cyan]依赖:[/cyan]")
                self.console.print(f"  {', '.join(component.dependencies)}")
                self.console.print()

            if component.usage_example:
                self.console.print(f"[cyan]使用示例:[/cyan]")
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

        self.console.print(f"[cyan]{'=' * 60}[/cyan]")
        self.console.print(f"[cyan]Super Dev 完整流水线[/cyan]")
        self.console.print(f"[cyan]{'=' * 60}[/cyan]")
        self.console.print(f"[dim]项目: {project_name}[/dim]")
        self.console.print(f"[dim]技术栈: {args.platform} | {args.frontend} | {args.backend}[/dim]")
        self.console.print("")

        try:
            # ========== 第 0 阶段: 需求增强 ==========
            self.console.print("[cyan]第 0 阶段: 需求增强 (联网 + 知识库)...[/cyan]")
            import os
            from .orchestrator.knowledge import KnowledgeAugmenter

            output_dir = project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            disable_web = args.offline or (
                os.getenv("SUPER_DEV_DISABLE_WEB", "").strip().lower() in {"1", "true", "yes"}
            )
            augmenter = KnowledgeAugmenter(project_dir=project_dir, web_enabled=not disable_web)
            knowledge_bundle = augmenter.augment(
                requirement=args.description,
                domain=args.domain or "",
            )
            research_file = output_dir / f"{project_name}-research.md"
            research_file.write_text(augmenter.to_markdown(knowledge_bundle), encoding="utf-8")

            enriched_description = knowledge_bundle.get("enriched_requirement", args.description)
            self.console.print(f"  [green]✓[/green] 需求增强报告: {research_file}")
            self.console.print(
                f"  [dim]本地知识 {len(knowledge_bundle.get('local_knowledge', []))} 条 | "
                f"联网结果 {len(knowledge_bundle.get('web_knowledge', []))} 条[/dim]"
            )
            self.console.print("")

            # ========== 第 1 阶段: 生成文档 ==========
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
                domain=args.domain
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

            # 保存技术栈到配置文件（供后续阶段使用）
            self._save_tech_stack_to_config(project_dir, tech_stack, args.description)

            requirements = doc_generator.extract_requirements()
            phases = parser.build_execution_phases(scenario, requirements)

            # ========== 第 2 阶段: 生成前端可演示骨架 ==========
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

            # ========== 第 3 阶段: 创建 Spec ==========
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

            # ========== 第 4 阶段: 生成实现骨架 ==========
            scaffold_result = {"frontend_files": [], "backend_files": []}
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
                self.console.print("")
            else:
                self.console.print("[yellow]第 4 阶段: 生成前后端实现骨架 (跳过)[/yellow]")
                self.console.print("")

            # ========== 第 5 阶段: 红队审查 ==========
            redteam_report = None
            if not args.skip_redteam:
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
            else:
                self.console.print("[yellow]第 5 阶段: 红队审查 (跳过)[/yellow]")
                self.console.print("")

            # ========== 第 6 阶段: 质量门禁 ==========
            if not args.skip_quality_gate:
                self.console.print("[cyan]第 6 阶段: 质量门禁检查...[/cyan]")
                from .reviewers import QualityGateChecker

                gate_checker = QualityGateChecker(
                    project_dir=project_dir,
                    name=project_name,
                    tech_stack=tech_stack,
                    scenario_override=scenario,
                    threshold_override=args.quality_threshold,
                )

                gate_result = gate_checker.check(redteam_report)

                # 显示场景信息
                scenario_label = "0-1 新建项目" if gate_result.scenario == "0-1" else "1-N+1 增量开发"
                if gate_result.scenario == "0-1":
                    self.console.print(f"  [dim]场景: {scenario_label} (使用放宽标准)[/dim]")

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
                    self.console.print("[red]质量门禁未通过，流水线终止[/red]")
                    self.console.print("[cyan]请修复以下问题后重新运行:[/cyan]")
                    for failure in gate_result.critical_failures:
                        self.console.print(f"  - {failure}")
                    return 1
            else:
                self.console.print("[yellow]第 6 阶段: 质量门禁检查 (跳过)[/yellow]")
                self.console.print("[dim]提示: 使用 --skip-quality-gate 跳过了质量门禁检查，建议后续补充测试和质量检查[/dim]")
                self.console.print("")

            # ========== 第 7 阶段: 代码审查指南 ==========
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

            # ========== 第 8 阶段: AI 提示词 ==========
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

            # ========== 第 9 阶段: CI/CD 配置 ==========
            self.console.print(f"[cyan]第 9 阶段: 生成 CI/CD 配置 ({args.cicd.upper()})...[/cyan]")
            from .deployers import CICDGenerator

            cicd_gen = CICDGenerator(
                project_dir=project_dir,
                name=project_name,
                tech_stack=tech_stack,
                platform=args.cicd
            )

            cicd_files = cicd_gen.generate()

            for file_path, content in cicd_files.items():
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                self.console.print(f"  [green]✓[/green] {file_path}")

            self.console.print("")

            # ========== 第 10 阶段: 部署修复模板 ==========
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

            # ========== 第 11 阶段: 数据库迁移 ==========
            self.console.print("[cyan]第 11 阶段: 生成数据库迁移脚本...[/cyan]")
            from .deployers import MigrationGenerator

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

            self.console.print("")

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
                self.console.print("")
            self.console.print("  CI/CD:")
            for file_path in cicd_files.keys():
                self.console.print(f"    - {file_path}")
            self.console.print("")
            self.console.print("  部署修复模板:")
            self.console.print(f"    - {Path(remediation_outputs['env_file']).name}")
            self.console.print(f"    - {Path(remediation_outputs['checklist_file']).relative_to(project_dir)}")
            if remediation_outputs.get("per_platform_files"):
                for item in remediation_outputs["per_platform_files"]:
                    self.console.print(
                        f"    - {Path(item['checklist_file']).relative_to(project_dir)}"
                    )
                    self.console.print(
                        f"    - {Path(item['env_file']).relative_to(project_dir)}"
                    )
            self.console.print("")
            self.console.print("  数据库迁移:")
            for file_path in migration_files.keys():
                self.console.print(f"    - {file_path}")
            self.console.print("")
            self.console.print("[cyan]下一步:[/cyan]")
            self.console.print("  1. 打开 output/frontend/index.html 评审前端骨架")
            self.console.print("  2. 对照执行路线图按阶段推进开发")
            self.console.print("  3. 使用代码审查指南进行评审和修复")
            self.console.print("  4. 配置 CI/CD 平台 (设置 secrets/credentials)")
            self.console.print("  5. 运行数据库迁移脚本并推送代码触发流水线")
            self.console.print("")

        except Exception as e:
            self.console.print(f"[red]流水线失败: {e}[/red]")
            import traceback
            self.console.print(traceback.format_exc())
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
            self.console.print(f"[cyan]项目配置:[/cyan]")
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
            config_manager.update(**{args.key: args.value})
            self.console.print(f"[green]✓[/green] {args.key} = {args.value}")

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

        self.console.print("[yellow]未知 integrate 操作[/yellow]")
        return 1

    def _cmd_spec(self, args) -> int:
        """Spec-Driven Development 命令"""
        from .specs import SpecGenerator, ChangeManager, SpecManager
        from .specs.models import ChangeStatus

        project_dir = Path.cwd()

        if args.spec_action == "init":
            # 初始化 SDD 目录结构
            generator = SpecGenerator(project_dir)
            agents_path, project_path = generator.init_sdd()

            self.console.print("[green]✓[/green] SDD 目录结构已初始化")
            self.console.print(f"  [dim].super-dev/specs/[/dim] - 当前规范")
            self.console.print(f"  [dim].super-dev/changes/[/dim] - 变更提案")
            self.console.print(f"  [dim].super-dev/archive/[/dim] - 已归档变更")
            self.console.print("")
            self.console.print(f"[cyan]下一步:[/cyan]")
            self.console.print(f"  1. 编辑 .super-dev/project.md 填写项目上下文")
            self.console.print(f"  2. 运行 'super-dev spec propose <id>' 创建变更提案")

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

            self.console.print(f"[cyan]变更列表:[/cyan]")
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
            change = manager.load_change(args.change_id)

            if not change:
                self.console.print(f"[red]变更不存在: {args.change_id}[/red]")
                return 1

            self.console.print(f"[cyan]变更详情: {change.id}[/cyan]")
            self.console.print(f"  标题: {change.title}")
            self.console.print(f"  状态: {change.status.value}")

            if change.proposal:
                self.console.print("")
                self.console.print("[cyan]提案:[/cyan]")
                if change.proposal.description:
                    self.console.print(f"  {change.proposal.description}")
                if change.proposal.motivation:
                    self.console.print(f"[dim]动机: {change.proposal.motivation}[/dim]")

            if change.tasks:
                self.console.print("")
                self.console.print("[cyan]任务:[/cyan]")
                for task in change.tasks:
                    checkbox = "[x]" if task.status.value == "completed" else "[ ]"
                    self.console.print(f"  {checkbox} {task.id}: {task.title}")

            if change.spec_deltas:
                self.console.print("")
                self.console.print("[cyan]规范变更:[/cyan]")
                for delta in change.spec_deltas:
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
            self.console.print(f"[cyan]下一步:[/cyan]")
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

            self.console.print(f"[green]✓[/green] 需求已添加到变更")
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
            from rich.table import Table
            from rich.panel import Panel
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
            "init", "analyze", "workflow", "studio", "expert", "quality", "preview",
            "deploy", "create", "design", "spec", "pipeline", "config", "skill", "integrate",
        }
        return first not in known_commands

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
        if frontend in {"react", "vue", "angular", "svelte", "none"}:
            return frontend
        return mapping.get(frontend, "react")

    def _sanitize_project_name(self, name: str) -> str:
        """清理项目名，避免路径非法字符"""
        import re

        cleaned = re.sub(r"[\\/:*?\"<>|]+", "-", name.strip())
        cleaned = re.sub(r"\s+", "-", cleaned)
        cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
        return cleaned or "my-project"

    def _run_direct_requirement(self, description: str) -> int:
        """将 `super-dev <需求描述>` 直达路由到完整流水线"""
        if not description:
            self.console.print("[red]请提供需求描述[/red]")
            return 1

        config_manager = get_config_manager()
        config_exists = config_manager.exists()
        config = config_manager.config

        args = argparse.Namespace(
            description=description,
            platform=config.platform if config_exists else "web",
            frontend=self._normalize_pipeline_frontend(config.frontend) if config_exists else "react",
            backend=config.backend if config_exists else "node",
            domain=config.domain if config_exists else "",
            name=None,
            cicd="all",
            skip_redteam=False,
            skip_scaffold=False,
            skip_quality_gate=False,
            offline=False,
            quality_threshold=None,
        )

        self.console.print("[cyan]需求直达模式：自动执行完整流水线[/cyan]")
        return self._cmd_pipeline(args)

    def _save_tech_stack_to_config(self, project_dir: Path, tech_stack: dict, description: str) -> None:
        """保存技术栈到项目配置文件"""
        import yaml
        from pathlib import Path

        config_file = project_dir / "super-dev.yaml"

        # 读取现有配置（如果有）
        config = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
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
