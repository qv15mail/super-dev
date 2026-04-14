"""CLI preview/wizard/create/design mixin helpers."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .catalogs import (
    CICD_PLATFORM_IDS,
    DOMAIN_IDS,
    PIPELINE_BACKEND_IDS,
    PIPELINE_FRONTEND_TEMPLATE_IDS,
    PLATFORM_IDS,
)
from .config import ConfigManager, get_config_manager

SUPPORTED_PLATFORMS = list(PLATFORM_IDS)
SUPPORTED_PIPELINE_FRONTENDS = list(PIPELINE_FRONTEND_TEMPLATE_IDS)
SUPPORTED_PIPELINE_BACKENDS = list(PIPELINE_BACKEND_IDS)
SUPPORTED_DOMAINS = list(DOMAIN_IDS)
SUPPORTED_CICD = list(CICD_PLATFORM_IDS)


class CliExperienceMixin:
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
        rows = (
            "\n".join(
                f'<li><a href="{doc.name}" target="_blank">{doc.name}</a></li>' for doc in docs[:20]
            )
            or "<li>未找到可预览文档，请先在宿主会话触发 /super-dev，或运行 super-dev start / super-dev create 生成治理产物。</li>"
        )

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
        self.console.print(
            "[dim]将执行：问题复现与影响分析 -> 轻量补丁文档 -> 定点修复与回归验证 -> 质量门禁与交付[/dim]"
        )
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
        self.console.print(
            f"[dim]平台: {args.platform} | 前端: {args.frontend} | 后端: {args.backend}[/dim]"
        )
        self.console.print("")

        # 确定项目名称
        project_name = args.name
        if not project_name:
            # 从描述生成项目名称
            import re

            words = re.findall(r"[\w]+", args.description)
            if words:
                project_name = "-".join(words[:3]).lower()
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
                ui_library=getattr(args, "ui_library", None),
                style_solution=getattr(args, "style", None),
                state_management=getattr(args, "state", []) or [],
                testing_frameworks=getattr(args, "testing", []) or [],
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

    def _resolve_design_command_context(
        self,
        *,
        idea: str = "",
        frontend: str = "",
        product_type: str = "",
        industry: str = "",
        style: str = "",
    ) -> dict[str, object]:
        project_dir = Path.cwd()
        config_manager = get_config_manager(project_dir)
        config = config_manager.load()

        config_exists = config_manager.exists()
        base_name = str(config.name or "").strip() if config_exists else project_dir.name
        if not base_name:
            base_name = project_dir.name or "my-project"
        project_name = self._sanitize_project_name(base_name)
        description = (
            str(idea or "").strip() or str(config.description or "").strip() or project_name
        )
        platform_value = str(config.platform or "web").strip() or "web"
        frontend_value = str(frontend or config.frontend or "next").strip() or "next"
        backend_value = str(config.backend or "node").strip() or "node"
        domain_value = str(config.domain or "").strip()

        from .creators import DocumentGenerator

        generator = DocumentGenerator(
            name=project_name,
            description=description,
            platform=platform_value,
            frontend=frontend_value,
            backend=backend_value,
            domain=domain_value,
            ui_library=config.ui_library,
            style_solution=config.style_solution,
            state_management=list(config.state_management or []),
            testing_frameworks=list(config.testing_frameworks or []),
            design_inspiration_slug=str(getattr(config, "design_inspiration_slug", "") or ""),
            language_preferences=list(config.language_preferences or []),
        )
        analysis = generator._analyze_project_for_design()
        if product_type:
            analysis["product_type"] = product_type.strip().lower()
        if industry:
            analysis["industry"] = industry.strip().lower()
        if style:
            analysis["style"] = style.strip().lower()

        return {
            "project_dir": project_dir,
            "project_name": project_name,
            "description": description,
            "platform": platform_value,
            "frontend": frontend_value,
            "backend": backend_value,
            "domain": domain_value,
            "analysis": analysis,
            "config_manager": config_manager,
            "config_exists": config_exists,
        }

    def _render_design_inspiration_list(self, inspirations: list[dict[str, object]]) -> None:
        if not inspirations:
            self.console.print("[yellow]未找到匹配的设计灵感锚点[/yellow]")
            return

        self.console.print(f"[green]设计灵感锚点 ({len(inspirations)} 个):[/green]\n")
        for idx, item in enumerate(inspirations, 1):
            signals = " / ".join(str(signal) for signal in list(item.get("signals", []))[:3])
            self.console.print(
                f"[cyan]{idx}. {item.get('name', 'N/A')}[/cyan]  [dim]slug={item.get('slug', 'N/A')}[/dim]"
            )
            self.console.print(f"    方向: {item.get('direction', 'N/A')}")
            self.console.print(f"    理由: {item.get('rationale', 'N/A')}")
            if signals:
                self.console.print(f"    参考信号: {signals}")
            source = str(item.get("source", "")).strip()
            if source:
                self.console.print(f"    来源: {source}")
            self.console.print()

    def _cmd_design(self, args) -> int:
        """设计智能引擎命令"""
        from .design import (
            DesignIntelligenceEngine,
            DesignSystemGenerator,
            TokenGenerator,
            UIIntelligenceAdvisor,
        )

        if args.design_command == "list":
            advisor = UIIntelligenceAdvisor()
            inspirations = [
                item.to_dict()
                for item in advisor.list_design_references(
                    product_type=str(getattr(args, "product_type", "") or "").strip().lower()
                    or None,
                    industry=str(getattr(args, "industry", "") or "").strip().lower() or None,
                    style=str(getattr(args, "style", "") or "").strip().lower() or None,
                    frontend=str(getattr(args, "frontend", "") or "").strip() or None,
                    limit=max(int(getattr(args, "max_results", 10) or 10), 1),
                )
            ]
            self._render_design_inspiration_list(inspirations)
            return 0

        if args.design_command == "recommend":
            advisor = UIIntelligenceAdvisor()
            context = self._resolve_design_command_context(
                idea=str(getattr(args, "idea", "") or ""),
                frontend=str(getattr(args, "frontend", "") or ""),
                product_type=str(getattr(args, "product_type", "") or ""),
                industry=str(getattr(args, "industry", "") or ""),
                style=str(getattr(args, "style", "") or ""),
            )
            analysis = context["analysis"]
            if not isinstance(analysis, dict):
                self.console.print("[red]无法解析当前项目的设计上下文[/red]")
                return 1

            profile = advisor.recommend(
                description=str(context["description"]),
                frontend=str(context["frontend"]),
                product_type=str(analysis.get("product_type", "general")),
                industry=str(analysis.get("industry", "general")),
                style=str(analysis.get("style", "modern")),
            )
            inspirations = [
                item
                for item in list(profile.get("design_references", []))[
                    : max(int(getattr(args, "max_results", 3) or 3), 1)
                ]
                if isinstance(item, dict)
            ]

            self.console.print("[cyan]设计灵感推荐[/cyan]")
            self.console.print(
                f"  项目: {context['project_name']} | 前端: {context['frontend']} | 产品类型: {analysis.get('product_type', 'general')}"
            )
            self.console.print(
                f"  行业: {analysis.get('industry', 'general')} | 风格: {analysis.get('style', 'modern')}"
            )
            self.console.print(
                "  真源: 内部仍以 output/*-uiux.md + output/*-ui-contract.json 为准\n"
            )
            self._render_design_inspiration_list(inspirations)
            return 0

        if args.design_command == "apply":
            advisor = UIIntelligenceAdvisor()
            selected = advisor.get_design_reference(args.slug)
            if selected is None:
                self.console.print(f"[red]未知设计灵感 slug: {args.slug}[/red]")
                self.console.print("[dim]先运行 `super-dev design list` 查看可用 slug[/dim]")
                return 1

            context = self._resolve_design_command_context(
                idea=str(getattr(args, "idea", "") or "")
            )
            config_manager = context["config_manager"]
            if not isinstance(config_manager, ConfigManager):
                self.console.print("[red]无法加载项目配置管理器[/red]")
                return 1

            if not bool(context["config_exists"]):
                config_manager.create(
                    name=str(context["project_name"]),
                    description=str(context["description"]),
                    platform=str(context["platform"]),
                    frontend=str(context["frontend"]),
                    backend=str(context["backend"]),
                    domain=str(context["domain"]),
                )

            update_payload: dict[str, object] = {"design_inspiration_slug": selected.slug}
            if (
                str(getattr(args, "idea", "") or "").strip()
                and not str(config_manager.config.description or "").strip()
            ):
                update_payload["description"] = str(getattr(args, "idea", "")).strip()
            updated_config = config_manager.update(**update_payload)

            output_dir = Path.cwd() / str(updated_config.output_dir or "output")
            output_dir.mkdir(parents=True, exist_ok=True)
            project_name = self._sanitize_project_name(
                str(updated_config.name or context["project_name"])
            )
            record_path = output_dir / f"{project_name}-design-inspiration.json"
            record_payload = {
                "slug": selected.slug,
                "name": selected.name,
                "rationale": selected.rationale,
                "direction": selected.direction,
                "source": selected.source,
                "signals": list(selected.signals),
                "cautions": list(selected.cautions),
                "applied_at": datetime.now(timezone.utc).isoformat(),
            }
            record_path.write_text(
                json.dumps(record_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            self.console.print(
                f"[green]✓[/green] 已应用设计灵感: {selected.name} ({selected.slug})"
            )
            self.console.print(f"  来源: {selected.source}")
            self.console.print(f"  已写入配置: design_inspiration_slug = {selected.slug}")
            self.console.print(f"  记录文件: {record_path}")

            if getattr(args, "write_uiux", True):
                return self._cmd_run_targeted_refresh("uiux")
            return 0

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

                self.console.print(
                    f"[{relevance_color}]{idx}.[/] [bold]{item.get('name', item.get('Style Category', item.get('Font Pairing Name', 'N/A')))}[/] (相关度: {item.get('relevance', 'N/A')})"
                )

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
            if hasattr(args, "list") and args.list:
                pattern_names = landing_gen.list_patterns()
                self.console.print(
                    f"\n[green]可用的 Landing 页面模式 ({len(pattern_names)} 个):[/green]\n"
                )
                for i, pattern_name in enumerate(pattern_names, 1):
                    self.console.print(f"  {i}. {pattern_name}")
                self.console.print()
                return 0

            # 智能推荐
            if hasattr(args, "product_type") and args.product_type:
                self.console.print("[cyan]智能推荐 Landing 页面模式[/cyan]")
                self.console.print(f"  产品类型: {args.product_type}")
                self.console.print(
                    f"  目标: {args.goal if hasattr(args, 'goal') and args.goal else 'N/A'}"
                )
                self.console.print(
                    f"  受众: {args.audience if hasattr(args, 'audience') and args.audience else 'N/A'}"
                )
                self.console.print()

                recommended = landing_gen.recommend(
                    product_type=args.product_type,
                    goal=args.goal if hasattr(args, "goal") and args.goal else "",
                    audience=args.audience if hasattr(args, "audience") and args.audience else "",
                )

                if recommended:
                    self.console.print(f"[green]推荐模式: {recommended.name}[/green]")
                    self.console.print(f"  {recommended.description}")
                    self.console.print(f"  适合: {', '.join(recommended.best_for)}")
                    self.console.print(f"  复杂度: {recommended.complexity}")
                    self.console.print()
                    return 0

            # 搜索模式
            query = args.query if hasattr(args, "query") and args.query else ""
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
            self.console.print(
                f"\n[green]可用的 Landing 页面模式 ({len(pattern_names)} 个):[/green]\n"
            )
            for i, pattern_name in enumerate(pattern_names, 1):
                self.console.print(f"  {i}. {pattern_name}")
            self.console.print()
            return 0

        elif args.design_command == "chart":
            # 图表类型推荐
            from .design import get_chart_recommender

            chart_recommender = get_chart_recommender()

            # 列出所有图表类型
            if hasattr(args, "list") and args.list:
                chart_types = chart_recommender.list_chart_types()
                categories = chart_recommender.list_categories()
                self.console.print(
                    f"\n[green]可用的图表类型 ({len(chart_types)} 个, {len(categories)} 个类别):[/green]\n"
                )
                for category in sorted(categories):
                    types = [
                        ct
                        for ct in chart_types
                        if ct
                        in [
                            c.name
                            for c in chart_recommender.chart_types
                            if c.category.value == category
                        ]
                    ]
                    self.console.print(f"  [cyan]{category}:[/cyan]")
                    for ct in sorted(types):
                        self.console.print(f"    - {ct}")
                self.console.print()
                return 0

            # 推荐图表类型
            data_description = args.data_description if hasattr(args, "data_description") else ""
            if data_description:
                self.console.print("[cyan]推荐图表类型[/cyan]")
                self.console.print(f"  数据描述: {data_description}")
                self.console.print(f"  框架: {args.framework}")
                self.console.print()

                chart_recommendations = chart_recommender.recommend(
                    data_description=data_description,
                    framework=args.framework,
                    max_results=args.max_results,
                )

                if not chart_recommendations:
                    self.console.print("[yellow]未找到合适的图表类型[/yellow]")
                    return 1

                self.console.print("[green]推荐结果:[/green]\n")

                for idx, chart_rec in enumerate(chart_recommendations, 1):
                    confidence_pct = int(chart_rec.confidence * 100)
                    self.console.print(
                        f"[cyan]{idx}. {chart_rec.chart_type.name}[/cyan] (置信度: {confidence_pct}%)"
                    )
                    self.console.print(f"    {chart_rec.chart_type.description}")
                    self.console.print(f"    理由: {chart_rec.reasoning}")
                    self.console.print(f"    推荐库: {chart_rec.library_recommendation}")
                    self.console.print(f"    无障碍: {chart_rec.chart_type.accessibility_notes}")
                    if chart_rec.alternatives:
                        self.console.print(
                            f"    替代方案: {', '.join([a.name for a in chart_rec.alternatives])}"
                        )
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
            if hasattr(args, "list_domains") and args.list_domains:
                domains = ux_guide.list_domains()
                self.console.print(f"\n[green]UX 指南领域 ({len(domains)} 个):[/green]\n")
                for i, domain in enumerate(domains, 1):
                    self.console.print(f"  {i}. {domain}")
                self.console.print()
                return 0

            # 快速见效的改进
            if hasattr(args, "quick_wins") and args.quick_wins:
                self.console.print("[cyan]快速见效的 UX 改进建议[/cyan]\n")

                ux_quick_wins = ux_guide.get_quick_wins(max_results=args.max_results)

                if not ux_quick_wins:
                    self.console.print("[yellow]未找到快速见效的建议[/yellow]")
                    return 1

                for idx, ux_rec in enumerate(ux_quick_wins, 1):
                    self.console.print(
                        f"[cyan]{idx}. {ux_rec.guideline.topic}[/cyan] ({ux_rec.guideline.domain.value})"
                    )
                    self.console.print(
                        f"    [green]最佳实践:[/green] {ux_rec.guideline.best_practice}"
                    )
                    self.console.print(f"    [red]反模式:[/red] {ux_rec.guideline.anti_pattern}")
                    self.console.print(f"    影响: {ux_rec.guideline.impact}")
                    self.console.print(
                        f"    优先级: {ux_rec.priority} | 实现难度: {ux_rec.implementation_effort} | 用户影响: {ux_rec.user_impact}"
                    )
                    if ux_rec.resources:
                        self.console.print(f"    资源: {', '.join(ux_rec.resources)}")
                    self.console.print()

                return 0

            # 检查清单
            if hasattr(args, "checklist") and args.checklist:
                self.console.print("[cyan]UX 检查清单[/cyan]\n")

                checklist = ux_guide.get_checklist(
                    domains=[args.domain] if hasattr(args, "domain") and args.domain else None
                )

                for domain, items in sorted(checklist.items()):
                    self.console.print(f"[cyan]{domain}:[/cyan]")
                    for item in items:
                        self.console.print(f"  {item}")
                    self.console.print()

                return 0

            # 搜索 UX 指南
            query = args.query if hasattr(args, "query") and args.query else ""
            if query:
                self.console.print(f"[cyan]搜索 UX 指南: {query}[/cyan]\n")

                ux_recommendations = ux_guide.search(
                    query=query,
                    domain=args.domain if hasattr(args, "domain") else None,
                    max_results=args.max_results,
                )

                if not ux_recommendations:
                    self.console.print("[yellow]未找到匹配的 UX 指南[/yellow]")
                    return 1

                self.console.print(f"[green]找到 {len(ux_recommendations)} 个结果:[/green]\n")

                for idx, ux_rec in enumerate(ux_recommendations, 1):
                    self.console.print(
                        f"[cyan]{idx}. {ux_rec.guideline.topic}[/cyan] ({ux_rec.guideline.domain.value})"
                    )
                    self.console.print(
                        f"    [green]最佳实践:[/green] {ux_rec.guideline.best_practice}"
                    )
                    self.console.print(f"    [red]反模式:[/red] {ux_rec.guideline.anti_pattern}")
                    self.console.print(f"    影响: {ux_rec.guideline.impact}")
                    self.console.print(
                        f"    优先级: {ux_rec.priority} | 实现难度: {ux_rec.implementation_effort} | 用户影响: {ux_rec.user_impact}"
                    )
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
            if hasattr(args, "list") and args.list:
                stacks = tech_engine.list_stacks()
                self.console.print(f"\n[green]支持的技术栈 ({len(stacks)} 个):[/green]\n")
                for i, stack in enumerate(stacks, 1):
                    self.console.print(f"  {i}. {stack}")
                self.console.print()
                return 0

            # 查询参数
            stack_name = args.stack
            query = args.query if hasattr(args, "query") and args.query else None
            category = args.category if hasattr(args, "category") else None

            # 显示设计模式
            if hasattr(args, "patterns") and args.patterns:
                tech_patterns = tech_engine.get_patterns(stack_name)

                if not tech_patterns:
                    self.console.print(f"[yellow]未找到 {stack_name} 的设计模式[/yellow]")
                    return 1

                self.console.print(
                    f"\n[cyan]{stack_name} 设计模式 ({len(tech_patterns)} 个):[/cyan]\n"
                )

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
            if hasattr(args, "performance") and args.performance:
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
            if hasattr(args, "quick_wins") and args.quick_wins:
                tips = tech_engine.get_quick_wins(stack_name)

                if not tips:
                    self.console.print(f"[yellow]未找到 {stack_name} 的快速性能优化[/yellow]")
                    return 1

                self.console.print(
                    f"\n[cyan]{stack_name} 快速见效的性能优化 ({len(tips)} 个):[/cyan]\n"
                )

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
                stack=stack_name, query=query, category=category, max_results=args.max_results
            )

            if not stack_recommendations:
                self.console.print("[yellow]未找到匹配的最佳实践[/yellow]")
                return 1

            for idx, stack_rec in enumerate(stack_recommendations, 1):
                self.console.print(
                    f"[cyan]{idx}. {stack_rec.practice.topic}[/cyan] ({stack_rec.practice.category.value})"
                )
                self.console.print(f"    [green]最佳实践:[/green] {stack_rec.practice.practice}")
                self.console.print(f"    [red]反模式:[/red] {stack_rec.practice.anti_pattern}")
                self.console.print(f"    好处: {stack_rec.practice.benefits}")
                self.console.print(
                    f"    优先级: {stack_rec.priority} | 复杂度: {stack_rec.practice.complexity}"
                )
                if stack_rec.context:
                    self.console.print(f"    上下文: {stack_rec.context}")
                if stack_rec.alternatives:
                    self.console.print(
                        f"    替代方案: {', '.join([a.value if hasattr(a, 'value') else str(a) for a in stack_rec.alternatives])}"
                    )
                if stack_rec.resources:
                    self.console.print(f"    资源: {', '.join(stack_rec.resources)}")
                if stack_rec.practice.code_example:
                    self.console.print(
                        f"    代码示例:\n    [dim]{stack_rec.practice.code_example[:200]}...[/dim]"
                    )
                self.console.print()

            return 0

        elif args.design_command == "codegen":
            # 代码片段生成
            from .design import get_code_generator
            from .design.codegen import Framework

            codegen = get_code_generator()

            # 列出所有可用组件
            if hasattr(args, "list") and args.list:
                components = codegen.get_available_components(
                    framework=Framework(args.framework) if hasattr(args, "framework") else None
                )

                self.console.print(f"\n[green]可用组件 ({args.framework or 'all'}):[/green]\n")

                for category, comp_list in sorted(components.items()):
                    self.console.print(f"[cyan]{category}:[/cyan]")
                    for comp in comp_list:
                        self.console.print(f"  - {comp}")
                    self.console.print()

                return 0

            # 搜索组件
            if hasattr(args, "search") and args.search:
                component_snippets = codegen.search_components(
                    query=args.search,
                    framework=args.framework if hasattr(args, "framework") else None,
                )

                if not component_snippets:
                    self.console.print(f"[yellow]未找到匹配的组件: {args.search}[/yellow]")
                    return 1

                self.console.print(f"\n[green]找到 {len(component_snippets)} 个组件:[/green]\n")

                for idx, snippet in enumerate(component_snippets, 1):
                    self.console.print(
                        f"[cyan]{idx}. {snippet.name}[/cyan] ({snippet.framework.value})"
                    )
                    self.console.print(f"    类别: {snippet.category.value}")
                    self.console.print(f"    描述: {snippet.description}")
                    self.console.print(f"    依赖: {', '.join(snippet.dependencies)}")
                    if snippet.preview:
                        self.console.print(f"    预览: [dim]{snippet.preview}[/dim]")
                    self.console.print()

                return 0

            # 生成组件代码
            component_name = args.component
            framework = args.framework if hasattr(args, "framework") else "react"

            self.console.print(f"[cyan]生成 {component_name} 组件 ({framework})[/cyan]\n")

            component = codegen.generate_component(
                component_name=component_name, framework=Framework(framework)
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
            if hasattr(args, "output") and args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(component.code)

                self.console.print(f"\n[green]已保存到: {output_path}[/green]")

            return 0

        else:
            self.console.print("[yellow]请指定设计子命令[/yellow]")
            self.console.print(
                "  可用命令: list, recommend, apply, search, generate, tokens, landing, chart, ux, stack, codegen"
            )
            self.console.print("  使用 'super-dev design <command> -h' 查看帮助")
            return 1
