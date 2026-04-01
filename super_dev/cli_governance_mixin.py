"""CLI mixin for governance commands: memory, hooks, experts, compact, enforce."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class CliGovernanceMixin:
    """Mixin that adds memory / hooks / experts / compact subcommands."""

    # ------------------------------------------------------------------
    # memory commands
    # ------------------------------------------------------------------

    def _cmd_memory(self, args: Any) -> int:
        """Route memory subcommands."""
        action = getattr(args, "memory_action", None)
        if action == "list":
            return self._cmd_memory_list(args)
        if action == "show":
            return self._cmd_memory_show(args)
        if action == "forget":
            return self._cmd_memory_forget(args)
        if action == "consolidate":
            return self._cmd_memory_consolidate(args)
        self.console.print(
            "[yellow]请指定 memory 子命令: list / show / forget / consolidate[/yellow]"
        )
        return 1

    def _cmd_memory_list(self, _args: Any) -> int:
        """List all memories from .super-dev/memory/."""
        memory_dir = Path.cwd() / ".super-dev" / "memory"
        if not memory_dir.exists():
            self.console.print("[yellow]未发现记忆目录 (.super-dev/memory/)[/yellow]")
            return 0

        entries = sorted(
            p for p in memory_dir.iterdir() if p.is_file() and not p.name.startswith(".")
        )
        if not entries:
            self.console.print("[yellow]记忆目录为空[/yellow]")
            return 0

        if RICH_AVAILABLE:
            table = Table(title="Memory Entries")
            table.add_column("Name", style="cyan")
            table.add_column("Size", justify="right")
            table.add_column("Modified")
            for entry in entries:
                stat = entry.stat()
                table.add_row(
                    entry.stem,
                    f"{stat.st_size:,} B",
                    _format_mtime(stat.st_mtime),
                )
            self.console.print(table)
        else:
            for entry in entries:
                self.console.print(f"  {entry.stem}  ({entry.stat().st_size} B)")

        return 0

    def _cmd_memory_show(self, args: Any) -> int:
        """Show a specific memory entry."""
        name = getattr(args, "name", None)
        if not name:
            self.console.print("[red]请指定记忆名称[/red]")
            return 1

        memory_dir = Path.cwd() / ".super-dev" / "memory"
        candidates = list(memory_dir.glob(f"{name}*")) if memory_dir.exists() else []
        if not candidates:
            self.console.print(f"[red]未找到记忆: {name}[/red]")
            return 1

        target = candidates[0]
        try:
            content = target.read_text(encoding="utf-8")
        except Exception as exc:
            self.console.print(f"[red]读取失败: {exc}[/red]")
            return 1

        self.console.print(content)
        return 0

    def _cmd_memory_forget(self, args: Any) -> int:
        """Delete a memory entry."""
        name = getattr(args, "name", None)
        if not name:
            self.console.print("[red]请指定记忆名称[/red]")
            return 1

        memory_dir = Path.cwd() / ".super-dev" / "memory"
        candidates = list(memory_dir.glob(f"{name}*")) if memory_dir.exists() else []
        if not candidates:
            self.console.print(f"[red]未找到记忆: {name}[/red]")
            return 1

        target = candidates[0]
        try:
            target.unlink()
            self.console.print(f"[green]已删除: {target.name}[/green]")
        except Exception as exc:
            self.console.print(f"[red]删除失败: {exc}[/red]")
            return 1
        return 0

    def _cmd_memory_consolidate(self, _args: Any) -> int:
        """Trigger dream consolidation manually."""
        memory_dir = Path.cwd() / ".super-dev" / "memory"
        if not memory_dir.exists():
            self.console.print("[yellow]未发现记忆目录[/yellow]")
            return 0

        entries = sorted(
            p for p in memory_dir.iterdir() if p.is_file() and not p.name.startswith(".")
        )
        if not entries:
            self.console.print("[yellow]记忆目录为空，无需整合[/yellow]")
            return 0

        # Build a simple consolidation summary
        consolidated: list[dict[str, str]] = []
        for entry in entries:
            try:
                text = entry.read_text(encoding="utf-8")
                first_line = text.strip().split("\n", 1)[0][:120]
                consolidated.append({"name": entry.stem, "summary": first_line})
            except Exception:
                consolidated.append({"name": entry.stem, "summary": "(unreadable)"})

        # Write consolidated index
        index_path = memory_dir / "_consolidated_index.json"
        index_path.write_text(
            json.dumps(consolidated, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        self.console.print(f"[green]已整合 {len(consolidated)} 条记忆 → {index_path.name}[/green]")
        return 0

    # ------------------------------------------------------------------
    # hooks commands
    # ------------------------------------------------------------------

    def _cmd_hooks(self, args: Any) -> int:
        """Route hooks subcommands."""
        action = getattr(args, "hooks_action", None)
        if action == "list":
            return self._cmd_hooks_list(args)
        if action == "test":
            return self._cmd_hooks_test(args)
        self.console.print("[yellow]请指定 hooks 子命令: list / test[/yellow]")
        return 1

    def _cmd_hooks_list(self, _args: Any) -> int:
        """List configured hooks from super-dev.yaml."""
        try:
            from .config import get_config_manager

            cm = get_config_manager()
            config = cm.load_config()
            hooks = config.get("hooks", {}) if isinstance(config, dict) else {}
        except Exception:
            hooks = {}

        if not hooks:
            self.console.print("[yellow]未配置 hooks（super-dev.yaml → hooks 字段为空）[/yellow]")
            return 0

        if RICH_AVAILABLE:
            table = Table(title="Configured Hooks")
            table.add_column("Event", style="cyan")
            table.add_column("Command")
            for event, cmd in hooks.items():
                table.add_row(str(event), str(cmd))
            self.console.print(table)
        else:
            for event, cmd in hooks.items():
                self.console.print(f"  {event}: {cmd}")

        return 0

    def _cmd_hooks_test(self, args: Any) -> int:
        """Test execute a hook event (dry run)."""
        event = getattr(args, "event", None)
        if not event:
            self.console.print("[red]请指定要测试的 hook 事件名[/red]")
            return 1

        try:
            from .config import get_config_manager

            cm = get_config_manager()
            config = cm.load_config()
            hooks = config.get("hooks", {}) if isinstance(config, dict) else {}
        except Exception:
            hooks = {}

        cmd = hooks.get(event)
        if not cmd:
            self.console.print(f"[red]未找到 hook 事件: {event}[/red]")
            return 1

        self.console.print(f"[cyan]Dry-run hook '{event}':[/cyan] {cmd}")
        self.console.print("[green]（dry-run 模式，未实际执行）[/green]")
        return 0

    # ------------------------------------------------------------------
    # experts commands
    # ------------------------------------------------------------------

    def _cmd_experts(self, args: Any) -> int:
        """Route experts subcommands."""
        action = getattr(args, "experts_action", None)
        if action == "list":
            return self._cmd_experts_list(args)
        if action == "show":
            return self._cmd_experts_show(args)
        self.console.print("[yellow]请指定 experts 子命令: list / show[/yellow]")
        return 1

    def _cmd_experts_list(self, _args: Any) -> int:
        """List all experts (builtin + custom)."""
        try:
            from .orchestrator.experts import EXPERT_REGISTRY

            builtin_experts = list(EXPERT_REGISTRY.keys())
        except Exception:
            builtin_experts = [
                "PM",
                "ARCHITECT",
                "UI",
                "UX",
                "SECURITY",
                "CODE",
                "DBA",
                "QA",
                "DEVOPS",
                "RCA",
            ]

        # Check for custom experts in config
        custom_experts: list[str] = []
        try:
            from .config import get_config_manager

            cm = get_config_manager()
            config = cm.load_config()
            custom = config.get("custom_experts", []) if isinstance(config, dict) else []
            if isinstance(custom, list):
                custom_experts = [str(e) for e in custom]
        except Exception:
            pass

        if RICH_AVAILABLE:
            table = Table(title="Expert Roles")
            table.add_column("Name", style="cyan")
            table.add_column("Source")
            for name in builtin_experts:
                table.add_row(name, "builtin")
            for name in custom_experts:
                table.add_row(name, "custom")
            self.console.print(table)
        else:
            self.console.print("Builtin experts:")
            for name in builtin_experts:
                self.console.print(f"  {name}")
            if custom_experts:
                self.console.print("Custom experts:")
                for name in custom_experts:
                    self.console.print(f"  {name}")

        return 0

    def _cmd_experts_show(self, args: Any) -> int:
        """Show expert definition details."""
        name = getattr(args, "name", None)
        if not name:
            self.console.print("[red]请指定专家名称[/red]")
            return 1

        try:
            from .orchestrator.experts import EXPERT_REGISTRY

            expert = EXPERT_REGISTRY.get(name.upper())
            if expert is None:
                self.console.print(f"[red]未找到专家: {name}[/red]")
                return 1

            self.console.print(f"[bold cyan]{name.upper()}[/bold cyan]")
            if hasattr(expert, "description"):
                self.console.print(f"  描述: {expert.description}")
            if hasattr(expert, "responsibilities"):
                self.console.print("  职责:")
                for r in expert.responsibilities:
                    self.console.print(f"    - {r}")
        except ImportError:
            self.console.print(f"[yellow]专家模块不可用，无法展示 {name} 详情[/yellow]")
            return 1
        except Exception as exc:
            self.console.print(f"[red]查询失败: {exc}[/red]")
            return 1

        return 0

    # ------------------------------------------------------------------
    # compact commands
    # ------------------------------------------------------------------

    def _cmd_compact(self, args: Any) -> int:
        """Route compact subcommands."""
        action = getattr(args, "compact_action", None)
        if action == "show":
            return self._cmd_compact_show(args)
        if action == "list":
            return self._cmd_compact_list(args)
        self.console.print("[yellow]请指定 compact 子命令: show / list[/yellow]")
        return 1

    def _cmd_compact_show(self, _args: Any) -> int:
        """Show most recent compact summaries."""
        compact_dir = Path.cwd() / ".super-dev" / "compact"
        if not compact_dir.exists():
            self.console.print("[yellow]未发现 compact 目录 (.super-dev/compact/)[/yellow]")
            return 0

        files = sorted(
            (p for p in compact_dir.iterdir() if p.is_file() and not p.name.startswith(".")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not files:
            self.console.print("[yellow]compact 目录为空[/yellow]")
            return 0

        # Show the most recent one
        latest = files[0]
        self.console.print(f"[bold cyan]Latest compact: {latest.name}[/bold cyan]\n")
        try:
            content = latest.read_text(encoding="utf-8")
            self.console.print(content)
        except Exception as exc:
            self.console.print(f"[red]读取失败: {exc}[/red]")
            return 1

        return 0

    def _cmd_compact_list(self, _args: Any) -> int:
        """List all phase compact files."""
        compact_dir = Path.cwd() / ".super-dev" / "compact"
        if not compact_dir.exists():
            self.console.print("[yellow]未发现 compact 目录 (.super-dev/compact/)[/yellow]")
            return 0

        files = sorted(
            (p for p in compact_dir.iterdir() if p.is_file() and not p.name.startswith(".")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not files:
            self.console.print("[yellow]compact 目录为空[/yellow]")
            return 0

        if RICH_AVAILABLE:
            table = Table(title="Compact Summaries")
            table.add_column("File", style="cyan")
            table.add_column("Size", justify="right")
            table.add_column("Modified")
            for f in files:
                stat = f.stat()
                table.add_row(
                    f.name,
                    f"{stat.st_size:,} B",
                    _format_mtime(stat.st_mtime),
                )
            self.console.print(table)
        else:
            for f in files:
                self.console.print(f"  {f.name}  ({f.stat().st_size} B)")

        return 0

    # ------------------------------------------------------------------
    # enforce commands
    # ------------------------------------------------------------------

    def _cmd_enforce(self, args: Any) -> int:
        """Route enforce subcommands: install / validate / status."""
        action = getattr(args, "enforce_action", None)
        if action == "install":
            return self._cmd_enforce_install(args)
        if action == "validate":
            return self._cmd_enforce_validate(args)
        if action == "status":
            return self._cmd_enforce_status(args)
        self.console.print("[yellow]请指定 enforce 子命令: install / validate / status[/yellow]")
        return 1

    def _cmd_enforce_install(self, args: Any) -> int:
        """Install enforcement hooks, validation script, and pre-code checklist."""
        try:
            from .enforcement import HostHooksConfigurator
        except Exception as exc:
            self.console.print(f"[red]加载 enforcement 模块失败: {exc}[/red]")
            return 1

        project_dir = Path.cwd()
        host = getattr(args, "host", "claude-code")
        frontend = getattr(args, "frontend", "")
        backend = getattr(args, "backend", "")
        icon_library = getattr(args, "icon_library", "lucide")

        configurator = HostHooksConfigurator(project_dir)
        results: list[str] = []

        # 1. Install hooks
        try:
            settings_path = configurator.install_hooks(host=host)
            results.append(f"Hooks 已安装 -> {settings_path.relative_to(project_dir)}")
        except Exception as exc:
            self.console.print(f"[red]Hooks 安装失败: {exc}[/red]")

        # 2. Generate validation script
        try:
            from .enforcement.validation import ValidationScriptGenerator

            gen = ValidationScriptGenerator()
            script_path = gen.generate(project_dir, frontend=frontend, icon_library=icon_library)
            results.append(f"验证脚本 -> {script_path.relative_to(project_dir)}")
        except Exception as exc:
            self.console.print(f"[red]验证脚本生成失败: {exc}[/red]")

        # 3. Generate pre-code checklist
        try:
            checklist_path = configurator.generate_pre_code_checklist(
                frontend=frontend, backend=backend
            )
            results.append(f"编码前清单 -> {checklist_path.relative_to(project_dir)}")
        except Exception as exc:
            self.console.print(f"[red]编码前清单生成失败: {exc}[/red]")

        if results:
            self.console.print("[green]Enforcement 安装完成:[/green]")
            for r in results:
                self.console.print(f"  {r}")
        else:
            self.console.print("[red]未安装任何 enforcement 组件。[/red]")
            return 1

        return 0

    def _cmd_enforce_validate(self, _args: Any) -> int:
        """Run the validation script."""
        project_dir = Path.cwd()
        script_path = project_dir / "scripts" / "validate-superdev.sh"
        if not script_path.exists():
            self.console.print(
                "[yellow]未找到验证脚本。"
                "请先运行 'super-dev enforce install'。[/yellow]"
            )
            return 1

        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout:
                self.console.print(result.stdout.rstrip())
            if result.stderr:
                self.console.print(f"[dim]{result.stderr.rstrip()}[/dim]")
            return result.returncode
        except subprocess.TimeoutExpired:
            self.console.print("[red]验证脚本执行超时。[/red]")
            return 1
        except Exception as exc:
            self.console.print(f"[red]验证脚本执行失败: {exc}[/red]")
            return 1

    def _cmd_enforce_status(self, _args: Any) -> int:
        """Show enforcement status."""
        try:
            from .enforcement import HostHooksConfigurator
        except Exception as exc:
            self.console.print(f"[red]加载 enforcement 模块失败: {exc}[/red]")
            return 1

        project_dir = Path.cwd()
        configurator = HostHooksConfigurator(project_dir)
        status = configurator.get_status(host="claude-code")

        if RICH_AVAILABLE:
            table = Table(title="Enforcement Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status")
            for key, val in status.items():
                if key == "host":
                    continue
                label = key.replace("_", " ").title()
                if isinstance(val, bool):
                    indicator = "[green]Active[/green]" if val else "[red]Not installed[/red]"
                else:
                    indicator = str(val)
                table.add_row(label, indicator)
            self.console.print(table)
        else:
            self.console.print(f"Host: {status.get('host', 'unknown')}")
            for key, val in status.items():
                if key == "host":
                    continue
                label = key.replace("_", " ").title()
                indicator = "Active" if val else "Not installed"
                self.console.print(f"  {label}: {indicator}")

        # Also check pre-code gate completion
        try:
            from .enforcement.pre_code_gate import PreCodeGate

            gate = PreCodeGate()
            complete, incomplete = gate.check_completion(project_dir)
            if (project_dir / ".super-dev" / "PRE_CODE_CHECKLIST.md").exists():
                if complete:
                    self.console.print("\n[green]Pre-code checklist: ALL COMPLETE[/green]")
                else:
                    self.console.print(
                        f"\n[yellow]Pre-code checklist: "
                        f"{len(incomplete)} item(s) remaining[/yellow]"
                    )
                    for item in incomplete[:5]:
                        self.console.print(f"  - {item}")
        except Exception:
            pass

        return 0

    # ------------------------------------------------------------------
    # generate commands
    # ------------------------------------------------------------------

    def _cmd_generate(self, args: Any) -> int:
        """Route generate subcommands."""
        action = getattr(args, "generate_action", None)
        if action == "scaffold":
            return self._cmd_generate_scaffold(args)
        if action == "components":
            return self._cmd_generate_components(args)
        if action == "types":
            return self._cmd_generate_types(args)
        if action == "tailwind":
            return self._cmd_generate_tailwind(args)
        self.console.print(
            "[yellow]请指定 generate 子命令: scaffold / components / types / tailwind[/yellow]"
        )
        return 1

    def _cmd_generate_scaffold(self, args: Any) -> int:
        """Generate a full project scaffold."""
        frontend = getattr(args, "frontend", "next")

        if frontend != "next":
            self.console.print(
                f"[yellow]前端框架 '{frontend}' 的脚手架生成暂未支持 (coming soon)[/yellow]"
            )
            return 1

        from .creators.nextjs_scaffold import NextjsScaffoldGenerator

        project_dir = Path.cwd()
        project_name = getattr(args, "name", "") or project_dir.name

        generator = NextjsScaffoldGenerator()
        files = generator.generate(project_dir, project_name)

        self.console.print(f"[green]Next.js scaffold generated ({len(files)} files):[/green]")
        for f in files:
            try:
                rel = f.relative_to(project_dir)
            except ValueError:
                rel = f
            self.console.print(f"  {rel}")

        return 0

    def _cmd_generate_components(self, _args: Any) -> int:
        """Generate UI component scaffold from UIUX spec."""
        try:
            from .creators.component_scaffold import ComponentScaffoldGenerator

            project_dir = Path.cwd()
            generator = ComponentScaffoldGenerator()
            written = generator.generate_for_project(project_dir)

            if not written:
                self.console.print(
                    "[yellow]未生成组件文件（请确认 frontend 为 React 系框架）[/yellow]"
                )
                return 1

            self.console.print(f"[green]组件脚手架已生成 ({len(written)} files):[/green]")
            for f in written:
                try:
                    rel = f.relative_to(project_dir)
                except ValueError:
                    rel = f
                self.console.print(f"  {rel}")
            return 0
        except Exception as exc:
            self.console.print(f"[red]组件生成失败: {exc}[/red]")
            return 1

    def _cmd_generate_types(self, _args: Any) -> int:
        """Generate shared TypeScript types from architecture doc."""
        try:
            from .creators.api_contract import APIContractGenerator

            project_dir = Path.cwd()
            generator = APIContractGenerator()
            written = generator.generate_for_project(project_dir)

            if not written:
                self.console.print("[yellow]未生成类型文件[/yellow]")
                return 1

            self.console.print(f"[green]API 类型已生成 ({len(written)} files):[/green]")
            for f in written:
                try:
                    rel = f.relative_to(project_dir)
                except ValueError:
                    rel = f
                self.console.print(f"  {rel}")
            return 0
        except Exception as exc:
            self.console.print(f"[red]类型生成失败: {exc}[/red]")
            return 1

    def _cmd_generate_tailwind(self, _args: Any) -> int:
        """Generate tailwind.config.ts from UIUX spec."""
        try:
            from .creators.component_scaffold import ComponentScaffoldGenerator

            project_dir = Path.cwd()
            generator = ComponentScaffoldGenerator()
            files = generator.generate_all(project_dir)

            if "tailwind.config.ts" not in files:
                self.console.print(
                    "[yellow]未生成 tailwind 配置（请确认 frontend 为 React 系框架）[/yellow]"
                )
                return 1

            output_path = project_dir / "output" / "components" / "tailwind.config.ts"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(files["tailwind.config.ts"], encoding="utf-8")

            try:
                rel = output_path.relative_to(project_dir)
            except ValueError:
                rel = output_path
            self.console.print(f"[green]Tailwind 配置已生成:[/green] {rel}")
            return 0
        except Exception as exc:
            self.console.print(f"[red]Tailwind 配置生成失败: {exc}[/red]")
            return 1

    # ------------------------------------------------------------------
    # completion 命令
    # ------------------------------------------------------------------

    def _cmd_completion(self, args: Any) -> int:
        """输出 shell 补全脚本。"""
        shell = getattr(args, "shell", None)
        if not shell:
            self.console.print("[yellow]请指定 shell 类型: bash / zsh / fish[/yellow]")
            return 1

        from .completion import (
            generate_bash_completion,
            generate_fish_completion,
            generate_zsh_completion,
        )

        generators = {
            "bash": generate_bash_completion,
            "zsh": generate_zsh_completion,
            "fish": generate_fish_completion,
        }
        gen = generators.get(shell)
        if gen is None:
            self.console.print(f"[red]不支持的 shell 类型: {shell}[/red]")
            return 1

        print(gen())  # noqa: T201 — 直接 print 以便 eval 捕获
        return 0

    # ------------------------------------------------------------------
    # feedback 命令
    # ------------------------------------------------------------------

    def _cmd_feedback(self, _args: Any) -> int:
        """打开 GitHub Issues 页面。"""
        url = "https://github.com/shangyankeji/super-dev/issues"
        try:
            import webbrowser

            webbrowser.open(url)
            self.console.print(f"[green]已在浏览器中打开反馈页面:[/green] {url}")
        except Exception:
            self.console.print(f"请在浏览器中打开: {url}")
        return 0

    # ------------------------------------------------------------------
    # migrate 命令
    # ------------------------------------------------------------------

    def _cmd_migrate(self, _args: Any) -> int:
        """执行项目迁移 (2.2.0 -> 2.3.0)。"""
        from .migrate import migrate_project

        project_dir = Path.cwd()
        self.console.print("[cyan]正在执行 2.2.0 → 2.3.0 迁移...[/cyan]\n")

        changes = migrate_project(project_dir)

        if not changes:
            self.console.print("[green]项目已是最新状态，无需迁移。[/green]")
            return 0

        self.console.print(f"[green]迁移完成，共 {len(changes)} 项变更:[/green]")
        for change in changes:
            self.console.print(f"  - {change}")
        return 0


def _format_mtime(mtime: float) -> str:
    """Format a file modification timestamp for display."""
    try:
        from datetime import datetime, timezone

        dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(int(mtime))
