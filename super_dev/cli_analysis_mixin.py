"""CLI analysis command mixin helpers."""

from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from .config import ConfigManager, get_config_manager
from .orchestrator import Phase, WorkflowContext, WorkflowEngine


class CliAnalysisMixin:
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

    def _cmd_feature_checklist(self, args) -> int:
        """审计 PRD 范围覆盖率。"""
        from .analyzer import FeatureChecklistBuilder

        project_path = Path(args.path).resolve()
        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        try:
            builder = FeatureChecklistBuilder(project_path)
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

            self.console.print(f"[cyan]正在审计范围覆盖率: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]Feature Checklist 已保存到: {args.output}[/green]")
                else:
                    paths = builder.write(report)
                    self.console.print("[green]Feature Checklist 已生成[/green]")
                    self.console.print(f"  Markdown: {paths['markdown']}")
                    self.console.print(f"  JSON: {paths['json']}")
                return 0

            paths = builder.write(report)
            coverage_text = (
                f"{report.coverage_rate:.1f}%"
                if report.coverage_rate is not None
                else "unknown"
            )
            self.console.print("[green]Feature Checklist 已生成[/green]")
            self.console.print(f"  项目: {report.project_name}")
            self.console.print(f"  状态: {report.status}")
            self.console.print(f"  覆盖率: {coverage_text}")
            self.console.print(f"  Markdown: {paths['markdown']}")
            self.console.print(f"  JSON: {paths['json']}")
            self.console.print(f"  功能项总数: {report.total_features}")
            self.console.print(f"  已覆盖: {report.covered_count}")
            self.console.print(f"  规划中: {report.planned_count}")
            self.console.print(f"  缺失: {report.missing_count}")
            self.console.print(f"  未知: {report.unknown_count}")
            self.console.print(f"  高优先级缺口: {report.high_priority_gap_count}")
            self.console.print("")
            self.console.print(f"[cyan]{report.summary}[/cyan]")
            return 0

        except Exception as e:
            self.console.print(f"[red]Feature Checklist 生成失败: {e}[/red]")
            self.logger.error(
                "Feature Checklist 生成失败",
                extra={"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()},
            )
            if '--debug' in sys.argv or '-d' in sys.argv:
                self.console.print(traceback.format_exc())
            return 1

    def _cmd_product_audit(self, args) -> int:
        """生成产品总审查报告。"""
        from .analyzer import ProductAuditBuilder

        project_path = Path(args.path).resolve()
        if not project_path.exists():
            self.console.print(f"[red]项目不存在: {project_path}[/red]")
            return 1

        try:
            builder = ProductAuditBuilder(project_path)
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

            self.console.print(f"[cyan]正在生成 Product Audit: {project_path}[/cyan]")

            if output_format == "markdown":
                output = report.to_markdown()
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    self.console.print(f"[green]Product Audit 已保存到: {args.output}[/green]")
                else:
                    paths = builder.write(report)
                    self.console.print("[green]Product Audit 已生成[/green]")
                    self.console.print(f"  Markdown: {paths['markdown']}")
                    self.console.print(f"  JSON: {paths['json']}")
                return 0

            paths = builder.write(report)
            self.console.print("[green]Product Audit 已生成[/green]")
            self.console.print(f"  项目: {report.project_name}")
            self.console.print(f"  状态: {report.status}")
            self.console.print(f"  分数: {report.score}/100")
            self.console.print(f"  Markdown: {paths['markdown']}")
            self.console.print(f"  JSON: {paths['json']}")
            self.console.print(f"  发现问题: {len(report.findings)}")
            self.console.print("")
            self.console.print(f"[cyan]{report.summary}[/cyan]")
            if report.findings:
                self.console.print("")
                self.console.print("[yellow]优先问题:[/yellow]")
                for item in report.findings[:5]:
                    self.console.print(f"  - [{item.severity}] {item.title}")
            return 0 if report.status == "ready" else 1

        except Exception as e:
            self.console.print(f"[red]Product Audit 生成失败: {e}[/red]")
            self.logger.error(
                "Product Audit 生成失败",
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
