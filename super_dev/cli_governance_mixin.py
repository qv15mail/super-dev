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
        if action == "history":
            return self._cmd_hooks_history(args)
        if action == "test":
            return self._cmd_hooks_test(args)
        self.console.print("[yellow]请指定 hooks 子命令: list / history / test[/yellow]")
        return 1

    # ------------------------------------------------------------------
    # harness commands
    # ------------------------------------------------------------------

    def _cmd_harness(self, args: Any) -> int:
        """Route harness subcommands."""
        action = getattr(args, "harness_action", None)
        if action == "status":
            return self._cmd_harness_status(args)
        if action == "workflow":
            return self._cmd_harness_workflow(args)
        if action == "framework":
            return self._cmd_harness_framework(args)
        if action == "operational":
            return self._cmd_harness_operational(args)
        if action == "timeline":
            return self._cmd_harness_timeline(args)
        if action == "hooks":
            return self._cmd_harness_hooks(args)
        self.console.print(
            "[yellow]请指定 harness 子命令: status / workflow / framework / operational / timeline / hooks[/yellow]"
        )
        return 1

    def _build_harness_payload(self, *, hook_limit: int = 20) -> dict[str, Any]:
        from .harness_registry import build_operational_harness_payload, derive_operational_focus
        from .operational_harness import OperationalHarnessBuilder

        project_dir = Path.cwd()
        builder = OperationalHarnessBuilder(project_dir)
        report = builder.build(hook_limit=max(hook_limit, 1))
        files = builder.write(report)
        payload = build_operational_harness_payload(
            project_dir,
            hook_limit=max(hook_limit, 1),
            write_reports=True,
        )
        payload["enabled"] = report.enabled
        payload["passed"] = report.passed
        payload["enabled_count"] = report.enabled_count
        payload["passed_count"] = report.passed_count
        payload["blockers"] = list(report.blockers)
        payload["next_actions"] = list(report.next_actions)
        payload["recent_timeline"] = list(report.recent_timeline)
        payload["operational_focus"] = derive_operational_focus(
            project_dir, hook_limit=max(hook_limit, 1)
        )
        payload["report_file"] = str(files["markdown"])
        payload["json_file"] = str(files["json"])
        return payload

    @staticmethod
    def _summarize_harness_item(item: dict[str, Any]) -> str:
        kind = str(item.get("kind", ""))
        if not item.get("enabled"):
            if kind == "workflow":
                return "未检测到活动 workflow continuity trail"
            if kind == "framework":
                return "未检测到跨平台 framework playbook"
            if kind == "hooks":
                return "未检测到 hook 审计历史"
            return "未启用"
        if item.get("passed"):
            if kind == "workflow":
                recent_timeline = item.get("recent_timeline") or []
                if isinstance(recent_timeline, list) and recent_timeline:
                    first = recent_timeline[0] if isinstance(recent_timeline[0], dict) else {}
                    message = str(first.get("message", "")).strip()
                    if message:
                        return message
                return str(item.get("current_step_label") or item.get("workflow_status") or "workflow continuity 正常")
            if kind == "framework":
                return f"{item.get('framework') or 'framework'} harness 已通过"
            if kind == "hooks":
                return f"最近 {item.get('total_events', 0)} 条 hook 审计干净"
            return "已通过"
        blockers = item.get("blockers") or []
        if blockers:
            return "；".join(str(part) for part in blockers[:2])
        return "存在待处理阻塞项"

    def _render_harness_item(self, item: dict[str, Any]) -> None:
        label = str(item.get("label") or str(item.get("kind", "")) or "Harness")
        status = "ready" if item.get("passed") else ("disabled" if not item.get("enabled") else "pending")
        self.console.print(f"[cyan]{label}[/cyan] [{status}]")
        self.console.print(f"  概览: {self._summarize_harness_item(item)}")
        self.console.print(f"  JSON: {item.get('json_file', '-')}")
        self.console.print(f"  Markdown: {item.get('report_file', '-')}")
        blockers = item.get("blockers") or []
        if blockers:
            self.console.print("  阻塞:")
            for blocker in blockers[:3]:
                self.console.print(f"    - {blocker}")
        next_actions = item.get("next_actions") or []
        if next_actions:
            self.console.print("  下一步:")
            for action in next_actions[:2]:
                self.console.print(f"    - {action}")
        recent_timeline = item.get("recent_timeline") or []
        if isinstance(recent_timeline, list) and recent_timeline:
            self.console.print("  最近关键时间线:")
            for entry in recent_timeline[:3]:
                if not isinstance(entry, dict):
                    continue
                timestamp = str(entry.get("timestamp", "")).strip() or "-"
                title = str(entry.get("title", "")).strip() or str(entry.get("kind", "")).strip()
                message = str(entry.get("message", "")).strip() or "-"
                self.console.print(f"    - {timestamp} · {title} · {message}")

    def _cmd_harness_status(self, args: Any) -> int:
        hook_limit = max(int(getattr(args, "hook_limit", 20) or 20), 1)
        payload = self._build_harness_payload(hook_limit=hook_limit)
        if bool(getattr(args, "json", False)):
            self.console.print_json(data=payload)
            return 0

        harnesses = payload.get("harnesses", {})
        if RICH_AVAILABLE:
            table = Table(title="Operational Harness Status")
            table.add_column("Harness", style="cyan")
            table.add_column("Enabled")
            table.add_column("Passed")
            table.add_column("Summary")
            table.add_column("Report")
            for key in ("workflow", "framework", "hooks"):
                item = harnesses.get(key, {})
                table.add_row(
                    key,
                    "yes" if item.get("enabled") else "no",
                    "yes" if item.get("passed") else "no",
                    self._summarize_harness_item(item),
                    str(item.get("json_file", "-")),
                )
            self.console.print(table)
        else:
            for key in ("workflow", "framework", "hooks"):
                item = harnesses.get(key, {})
                self.console.print(f"{key}: {self._summarize_harness_item(item)}")
        self.console.print(f"[dim]Operational Harness JSON:[/dim] {payload.get('json_file', '-')}")
        self.console.print(f"[dim]Operational Harness Markdown:[/dim] {payload.get('report_file', '-')}")
        focus = payload.get("operational_focus", {})
        if isinstance(focus, dict) and str(focus.get("summary", "")).strip():
            self.console.print(f"[dim]当前治理焦点:[/dim] {focus.get('summary')}")
            action = str(focus.get("recommended_action", "")).strip()
            if action:
                self.console.print(f"[dim]建议先做:[/dim] {action}")

        return 0

    def _cmd_harness_workflow(self, args: Any) -> int:
        payload = self._build_harness_payload()
        item = payload["harnesses"]["workflow"]
        if bool(getattr(args, "json", False)):
            self.console.print_json(data=item)
            return 0
        self._render_harness_item(item)
        return 0

    def _cmd_harness_framework(self, args: Any) -> int:
        payload = self._build_harness_payload()
        item = payload["harnesses"]["framework"]
        if bool(getattr(args, "json", False)):
            self.console.print_json(data=item)
            return 0
        self._render_harness_item(item)
        return 0

    def _cmd_harness_operational(self, args: Any) -> int:
        from .operational_harness import OperationalHarnessBuilder

        hook_limit = max(int(getattr(args, "hook_limit", 20) or 20), 1)
        builder = OperationalHarnessBuilder(Path.cwd())
        report = builder.build(hook_limit=hook_limit)
        files = builder.write(report)
        payload = report.to_dict()
        payload["report_file"] = str(files["markdown"])
        payload["json_file"] = str(files["json"])
        if bool(getattr(args, "json", False)):
            self.console.print_json(data=payload)
            return 0
        self.console.print("[cyan]Operational Harness[/cyan]")
        self.console.print(
            f"  状态: {'passed' if payload.get('passed') else 'pending'} "
            f"({payload.get('passed_count', 0)}/{payload.get('enabled_count', 0)})"
        )
        self.console.print(f"  JSON: {payload.get('json_file', '-')}")
        self.console.print(f"  Markdown: {payload.get('report_file', '-')}")
        blockers = payload.get("blockers") or []
        if blockers:
            self.console.print("  阻塞:")
            for blocker in blockers[:3]:
                self.console.print(f"    - {blocker}")
        next_actions = payload.get("next_actions") or []
        if next_actions:
            self.console.print("  下一步:")
            for action in next_actions[:3]:
                self.console.print(f"    - {action}")
        timeline = payload.get("recent_timeline") or []
        if timeline:
            self.console.print("  最近关键时间线:")
            for entry in timeline[:5]:
                if not isinstance(entry, dict):
                    continue
                timestamp = str(entry.get("timestamp", "")).strip() or "-"
                title = str(entry.get("title", "")).strip() or str(entry.get("kind", "")).strip()
                message = str(entry.get("message", "")).strip() or "-"
                self.console.print(f"    - {timestamp} · {title} · {message}")
        return 0

    def _cmd_harness_timeline(self, args: Any) -> int:
        from .review_state import load_recent_operational_timeline

        limit = max(int(getattr(args, "limit", 10) or 10), 1)
        timeline = load_recent_operational_timeline(Path.cwd(), limit=limit)
        payload = {
            "project_dir": str(Path.cwd().resolve()),
            "count": len(timeline),
            "timeline": timeline,
        }
        if bool(getattr(args, "json", False)):
            self.console.print_json(data=payload)
            return 0
        if not timeline:
            self.console.print("[yellow]当前没有统一运行时时间线。[/yellow]")
            return 0
        self.console.print("[cyan]Operational Timeline[/cyan]")
        for item in timeline:
            timestamp = str(item.get("timestamp", "")).strip() or "-"
            title = str(item.get("title", "")).strip() or str(item.get("kind", "")).strip()
            message = str(item.get("message", "")).strip() or "-"
            self.console.print(f"  - {timestamp} · {title} · {message}")
        return 0

    def _cmd_harness_hooks(self, args: Any) -> int:
        limit = max(int(getattr(args, "limit", 20) or 20), 1)
        payload = self._build_harness_payload(hook_limit=limit)
        item = payload["harnesses"]["hooks"]
        if bool(getattr(args, "json", False)):
            self.console.print_json(data=item)
            return 0
        self._render_harness_item(item)
        return 0

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

    def _cmd_hooks_history(self, args: Any) -> int:
        """Show recent persisted hook execution history."""
        try:
            from .hooks.manager import HookManager

            limit = max(int(getattr(args, "limit", 10) or 10), 1)
            results = HookManager.load_recent_history(Path.cwd(), limit=limit)
        except Exception as exc:
            self.console.print(f"[red]读取 hook 历史失败: {exc}[/red]")
            return 1

        if not results:
            self.console.print("[yellow]暂无 hook 执行历史[/yellow]")
            return 0

        if RICH_AVAILABLE:
            table = Table(title="Recent Hook History")
            table.add_column("Time", style="cyan")
            table.add_column("Event")
            table.add_column("Phase")
            table.add_column("Hook")
            table.add_column("Status")
            table.add_column("Source")
            for item in results:
                table.add_row(
                    item.timestamp.replace("T", " ")[:19],
                    item.event,
                    item.phase or "-",
                    item.hook_name,
                    "blocked" if item.blocked else ("ok" if item.success else "failed"),
                    item.source or "-",
                )
            self.console.print(table)
        else:
            for item in results:
                status = "blocked" if item.blocked else ("ok" if item.success else "failed")
                self.console.print(
                    f"{item.timestamp} {item.event} {item.phase or '-'} {item.hook_name} {status}"
                )
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
        """执行项目迁移 (2.2.0+ -> 2.3.6)。"""
        from .migrate import migrate_project

        project_dir = Path.cwd()
        self.console.print("[cyan]正在执行 2.2.0+ → 2.3.6 迁移...[/cyan]\n")

        changes = migrate_project(project_dir)

        if not changes:
            self.console.print("[green]项目已是最新状态，无需迁移。[/green]")
            return 0

        self.console.print(f"[green]迁移完成，共 {len(changes)} 项变更:[/green]")
        for change in changes:
            self.console.print(f"  - {change}")
        return 0

    # ------------------------------------------------------------------
    # rollback 命令
    # ------------------------------------------------------------------

    def _cmd_rollback(self, args: Any) -> int:
        """将项目状态恢复到之前的流水线检查点。"""
        project_dir = Path.cwd()
        superdev_dir = project_dir / ".super-dev"
        checkpoint_dir = superdev_dir / "checkpoints"
        history_dir = superdev_dir / "workflow-history"

        if not superdev_dir.exists():
            self.console.print("[yellow]未发现 .super-dev/ 目录，当前项目尚未初始化。[/yellow]")
            return 1

        # --list: 列出可用检查点
        if getattr(args, "list", False):
            return self._rollback_list_checkpoints(checkpoint_dir, history_dir, superdev_dir)

        # --last: 回退到上一个检查点
        if getattr(args, "last", False):
            return self._rollback_to_last(checkpoint_dir, history_dir, superdev_dir, project_dir)

        # --phase <name>: 回退到指定阶段
        phase_name = getattr(args, "phase", None)
        if phase_name:
            return self._rollback_to_phase(
                phase_name, checkpoint_dir, history_dir, superdev_dir, project_dir
            )

        # 无参数时显示帮助
        self.console.print(
            "[yellow]请指定回退目标: --list (列出检查点), --last (回退上一个), "
            "--phase <阶段名> (回退到指定阶段)[/yellow]"
        )
        return 1

    def _rollback_list_checkpoints(
        self,
        checkpoint_dir: Path,
        history_dir: Path,
        superdev_dir: Path,
    ) -> int:
        """列出所有可用的检查点。"""
        checkpoints: list[dict[str, Any]] = []

        # 从 checkpoints/ 收集
        if checkpoint_dir.exists():
            for cp_file in sorted(checkpoint_dir.glob("*.json")):
                try:
                    data = json.loads(cp_file.read_text(encoding="utf-8"))
                    data["_source"] = "checkpoint"
                    data["_file"] = str(cp_file)
                    checkpoints.append(data)
                except Exception:
                    pass

        # 从 workflow-history/ 收集
        if history_dir.exists():
            for hist_file in sorted(history_dir.glob("*.json")):
                try:
                    data = json.loads(hist_file.read_text(encoding="utf-8"))
                    data["_source"] = "history"
                    data["_file"] = str(hist_file)
                    checkpoints.append(data)
                except Exception:
                    pass

        # 从 pipeline-state.json 收集
        pipeline_state_file = superdev_dir / "pipeline-state.json"
        if pipeline_state_file.exists():
            try:
                data = json.loads(pipeline_state_file.read_text(encoding="utf-8"))
                checkpoints.append({
                    "phase": data.get("current_phase", "unknown"),
                    "timestamp": data.get("last_updated", ""),
                    "_source": "pipeline-state",
                    "_file": str(pipeline_state_file),
                    "phases_completed": data.get("phases_completed", []),
                    "phases_remaining": data.get("phases_remaining", []),
                })
            except Exception:
                pass

        if not checkpoints:
            self.console.print("[yellow]未找到任何检查点。[/yellow]")
            return 0

        # 按时间排序（最新在前）
        checkpoints.sort(key=lambda c: str(c.get("timestamp", "")), reverse=True)

        if RICH_AVAILABLE:
            from rich.table import Table

            table = Table(title="可用检查点", show_lines=True)
            table.add_column("阶段", style="cyan", min_width=14)
            table.add_column("时间戳", style="green", min_width=20)
            table.add_column("来源", style="magenta", min_width=14)
            table.add_column("状态", style="yellow", min_width=8)
            table.add_column("质量分", style="blue", min_width=6)

            for cp in checkpoints:
                phase = str(cp.get("phase", "-"))
                ts = str(cp.get("timestamp", "-"))
                # Truncate microseconds for display
                if "." in ts:
                    ts = ts.split(".")[0]
                source = str(cp.get("_source", "-"))
                success = cp.get("success")
                if success is True:
                    status = "[green]✓ 成功[/green]"
                elif success is False:
                    status = "[red]✗ 失败[/red]"
                else:
                    status = "[dim]-[/dim]"
                qscore = str(cp.get("quality_score", "-"))
                if qscore != "-":
                    try:
                        score = float(qscore)
                        qscore = f"{score:.1f}"
                    except (ValueError, TypeError):
                        pass
                table.add_row(phase, ts, source, status, qscore)

            self.console.print(table)
            self.console.print(
                f"\n[dim]共 {len(checkpoints)} 个检查点。"
                "使用 --phase <阶段名> 或 --last 回退到指定检查点。[/dim]"
            )
        else:
            self.console.print(f"共 {len(checkpoints)} 个检查点:")
            for cp in checkpoints:
                phase = cp.get("phase", "-")
                ts = cp.get("timestamp", "-")
                source = cp.get("_source", "-")
                self.console.print(f"  {phase} | {ts} | {source}")

        return 0

    def _rollback_to_last(
        self,
        checkpoint_dir: Path,
        history_dir: Path,
        superdev_dir: Path,
        project_dir: Path,
    ) -> int:
        """回退到上一个检查点。"""
        # 收集历史检查点（按时间排序）
        history_files = sorted(
            history_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ) if history_dir.exists() else []

        # 也收集 checkpoint 文件
        checkpoint_files = sorted(
            checkpoint_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ) if checkpoint_dir.exists() else []

        # 合并所有来源，排除 pipeline-state
        all_candidates: list[tuple[float, Path]] = []
        for f in history_files:
            all_candidates.append((f.stat().st_mtime, f))
        for f in checkpoint_files:
            all_candidates.append((f.stat().st_mtime, f))

        # 加入 workflow-state.json
        ws_file = superdev_dir / "workflow-state.json"
        if ws_file.exists():
            all_candidates.append((ws_file.stat().st_mtime, ws_file))

        # 排除当前活跃的 pipeline-state.json
        pipeline_state = superdev_dir / "pipeline-state.json"
        all_candidates = [
            (mt, fp) for mt, fp in all_candidates if fp.resolve() != pipeline_state.resolve()
        ]

        if not all_candidates:
            self.console.print("[red]未找到可回退的检查点。[/red]")
            return 1

        # 排序取最新的非当前状态
        all_candidates.sort(key=lambda x: x[0], reverse=True)

        # 优先使用 workflow-history 中的条目
        target_path = all_candidates[0][1]

        return self._do_rollback(target_path, superdev_dir, project_dir)

    def _rollback_to_phase(
        self,
        phase_name: str,
        checkpoint_dir: Path,
        history_dir: Path,
        superdev_dir: Path,
        project_dir: Path,
    ) -> int:
        """回退到指定阶段的检查点。"""
        # 查找该阶段的检查点文件
        cp_file = checkpoint_dir / f"{phase_name}.json"
        if not cp_file.exists():
            # 尝试在 workflow-history 中查找
            candidates: list[Path] = []
            if history_dir.exists():
                for hf in history_dir.glob("*.json"):
                    try:
                        data = json.loads(hf.read_text(encoding="utf-8"))
                        if data.get("phase") == phase_name or data.get("current_phase") == phase_name:
                            candidates.append(hf)
                    except Exception:
                        pass
            if not candidates:
                self.console.print(f"[red]未找到阶段 '{phase_name}' 的检查点。[/red]")
                self.console.print("使用 [cyan]--list[/cyan] 查看所有可用检查点。")
                return 1
            # 取最新的匹配
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            cp_file = candidates[0]

        return self._do_rollback(cp_file, superdev_dir, project_dir)

    def _do_rollback(
        self,
        source_path: Path,
        superdev_dir: Path,
        project_dir: Path,
    ) -> int:
        """执行实际的回退操作。"""
        from datetime import datetime, timezone

        # 读取目标检查点数据
        try:
            checkpoint_data = json.loads(source_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.console.print(f"[red]无法读取检查点: {exc}[/red]")
            return 1

        # 备份当前状态
        history_dir = superdev_dir / "workflow-history"
        history_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = history_dir / f"pre-rollback-{timestamp}.json"

        current_state_files = ["pipeline-state.json", "workflow-state.json"]
        backup_data: dict[str, Any] = {
            "backup_reason": "pre-rollback",
            "backup_timestamp": datetime.now(timezone.utc).isoformat(),
            "restored_from": str(source_path),
            "current_states": {},
        }

        for state_file in current_state_files:
            state_path = superdev_dir / state_file
            if state_path.exists():
                try:
                    backup_data["current_states"][state_file] = json.loads(
                        state_path.read_text(encoding="utf-8")
                    )
                except Exception:
                    backup_data["current_states"][state_file] = None

        backup_path.write_text(
            json.dumps(backup_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 恢复检查点到 pipeline-state.json
        phase = checkpoint_data.get("phase", checkpoint_data.get("current_phase", "unknown"))
        new_state: dict[str, Any] = {
            "current_phase": phase,
            "phase_index": checkpoint_data.get("phase_index", 0),
            "total_phases": checkpoint_data.get("total_phases", 0),
            "phases_completed": checkpoint_data.get("phases_completed", []),
            "phases_remaining": checkpoint_data.get("phases_remaining", []),
            "started_at": checkpoint_data.get("started_at", checkpoint_data.get("timestamp", "")),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "restored_from_checkpoint": str(source_path),
            "rollback_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        pipeline_state_path = superdev_dir / "pipeline-state.json"
        pipeline_state_path.write_text(
            json.dumps(new_state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        # 如果检查点包含 workflow-state 数据，也恢复它
        ws_data = checkpoint_data.get("workflow_state") or checkpoint_data.get("workflow-state")
        if ws_data:
            ws_path = superdev_dir / "workflow-state.json"
            ws_path.write_text(
                json.dumps(ws_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )

        # 输出恢复确认
        if RICH_AVAILABLE:
            from rich.panel import Panel

            ts_display = str(checkpoint_data.get("timestamp", "-"))
            if "." in ts_display:
                ts_display = ts_display.split(".")[0]

            quality = checkpoint_data.get("quality_score")
            quality_str = f"{quality:.1f}" if quality is not None else "-"

            panel_content = (
                f"[bold cyan]已回退到检查点[/bold cyan]\n\n"
                f"  阶段: [green]{phase}[/green]\n"
                f"  检查点时间: {ts_display}\n"
                f"  质量分: [blue]{quality_str}[/blue]\n"
                f"  来源: [magenta]{source_path.name}[/magenta]\n\n"
                f"  备份位置: [dim]{backup_path.name}[/dim]"
            )
            self.console.print(Panel(panel_content, title="Rollback", border_style="green"))
        else:
            self.console.print(f"已回退到阶段: {phase}")
            self.console.print(f"来源: {source_path.name}")
            self.console.print(f"备份: {backup_path.name}")

        return 0

    # ------------------------------------------------------------------
    # replay 命令
    # ------------------------------------------------------------------

    def _cmd_replay(self, args: Any) -> int:
        """逐步查看流水线各阶段的执行详情和变更。"""
        project_dir = Path.cwd()
        superdev_dir = project_dir / ".super-dev"
        checkpoint_dir = superdev_dir / "checkpoints"
        history_dir = superdev_dir / "workflow-history"
        events_file = superdev_dir / "workflow-events.jsonl"

        if not superdev_dir.exists():
            self.console.print("[yellow]未发现 .super-dev/ 目录，当前项目尚未初始化。[/yellow]")
            return 1

        run_id = getattr(args, "run_id", None)

        # 收集所有阶段数据
        phases_data: list[dict[str, Any]] = []

        # 1. 从 checkpoints/ 收集阶段数据
        if checkpoint_dir.exists():
            for cp_file in sorted(checkpoint_dir.glob("*.json")):
                try:
                    data = json.loads(cp_file.read_text(encoding="utf-8"))
                    phases_data.append(data)
                except Exception:
                    pass

        # 2. 从 workflow-events.jsonl 收集事件数据
        events: list[dict[str, Any]] = []
        if events_file.exists():
            try:
                for line in events_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except Exception:
                            pass
            except Exception:
                pass

        # 3. 从 workflow-history/ 收集历史快照
        history_snapshots: list[dict[str, Any]] = []
        if history_dir.exists():
            for hist_file in sorted(history_dir.glob("*.json")):
                try:
                    data = json.loads(hist_file.read_text(encoding="utf-8"))
                    data["_file"] = str(hist_file)
                    history_snapshots.append(data)
                except Exception:
                    pass

        # 4. 如果有 pipeline-state.json，也加入
        pipeline_state_file = superdev_dir / "pipeline-state.json"
        pipeline_state: dict[str, Any] = {}
        if pipeline_state_file.exists():
            try:
                pipeline_state = json.loads(pipeline_state_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # 如果指定了 run-id，筛选数据
        if run_id:
            phases_data = [
                p for p in phases_data
                if str(p.get("run_id", "")) == run_id
                or str(p.get("project", "")) == run_id
            ]
            events = [
                e for e in events
                if str(e.get("run_id", "")) == run_id
            ]

        if not phases_data and not events and not history_snapshots:
            self.console.print("[yellow]未找到任何流水线执行记录。[/yellow]")
            return 0

        # 按时间排序
        phases_data.sort(key=lambda d: str(d.get("timestamp", "")))

        # 渲染时间线
        if RICH_AVAILABLE:
            from rich.panel import Panel
            from rich.table import Table

            # 总览
            total_phases = len(phases_data)
            successful = sum(1 for p in phases_data if p.get("success") is True)
            failed = sum(1 for p in phases_data if p.get("success") is False)
            avg_quality = 0.0
            quality_scores = [
                float(p.get("quality_score", 0))
                for p in phases_data
                if p.get("quality_score") is not None
            ]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)

            overview_text = (
                f"[bold]流水线执行总览[/bold]\n\n"
                f"  阶段总数: {total_phases}\n"
                f"  成功: [green]{successful}[/green]  失败: [red]{failed}[/red]\n"
                f"  平均质量分: [blue]{avg_quality:.1f}[/blue]\n"
                f"  事件记录: {len(events)} 条\n"
                f"  历史快照: {len(history_snapshots)} 个"
            )
            if pipeline_state:
                current = pipeline_state.get("current_phase", "-")
                completed_list = pipeline_state.get("phases_completed", [])
                overview_text += f"\n  当前阶段: [cyan]{current}[/cyan]"
                overview_text += f"\n  已完成阶段: {', '.join(completed_list) if completed_list else '-'}"

            self.console.print(Panel(overview_text, title="Pipeline Replay", border_style="cyan"))
            self.console.print("")

            # 阶段时间线表
            if phases_data:
                table = Table(title="阶段执行时间线", show_lines=True)
                table.add_column("#", style="dim", width=3)
                table.add_column("阶段", style="cyan", min_width=14)
                table.add_column("状态", min_width=8)
                table.add_column("耗时", style="yellow", min_width=8)
                table.add_column("质量分", style="blue", min_width=8)
                table.add_column("时间戳", style="green", min_width=20)

                for idx, phase in enumerate(phases_data, 1):
                    p_name = str(phase.get("phase", "-"))
                    success = phase.get("success")
                    if success is True:
                        status = "[green]✓ 成功[/green]"
                    elif success is False:
                        status = "[red]✗ 失败[/red]"
                    else:
                        status = "[dim]-[/dim]"

                    duration = phase.get("duration")
                    if duration is not None:
                        try:
                            dur_val = float(duration)
                            if dur_val < 60:
                                dur_str = f"{dur_val:.1f}s"
                            else:
                                dur_str = f"{dur_val / 60:.1f}m"
                        except (ValueError, TypeError):
                            dur_str = str(duration)
                    else:
                        dur_str = "-"

                    qscore = phase.get("quality_score")
                    if qscore is not None:
                        try:
                            qs = float(qscore)
                            if qs >= 90:
                                qscore_str = f"[green]{qs:.1f}[/green]"
                            elif qs >= 70:
                                qscore_str = f"[yellow]{qs:.1f}[/yellow]"
                            else:
                                qscore_str = f"[red]{qs:.1f}[/red]"
                        except (ValueError, TypeError):
                            qscore_str = str(qscore)
                    else:
                        qscore_str = "-"

                    ts = str(phase.get("timestamp", "-"))
                    if "." in ts:
                        ts = ts.split(".")[0]

                    table.add_row(str(idx), p_name, status, dur_str, qscore_str, ts)

                self.console.print(table)

            # 每个阶段的详细 Panel
            if phases_data:
                self.console.print("")
                for phase in phases_data:
                    p_name = str(phase.get("phase", "-"))
                    ts = str(phase.get("timestamp", "-"))
                    if "." in ts:
                        ts = ts.split(".")[0]

                    detail_lines = [f"时间戳: {ts}"]

                    duration = phase.get("duration")
                    if duration is not None:
                        detail_lines.append(f"耗时: {float(duration):.1f}s")

                    qscore = phase.get("quality_score")
                    if qscore is not None:
                        detail_lines.append(f"质量分: {float(qscore):.1f}")

                    errors = phase.get("errors", [])
                    if errors:
                        detail_lines.append(f"错误: {len(errors)} 个")
                        for err in errors[:3]:
                            detail_lines.append(f"  - {err}")

                    # 显示关联的输出文件
                    project_name = phase.get("project", "")
                    phase_val = phase.get("phase", "")
                    if project_name and phase_val:
                        output_dir = project_dir / "output"
                        if output_dir.exists():
                            related = list(output_dir.glob(f"{project_name}-{phase_val}*"))[:3]
                            if related:
                                detail_lines.append("产出文件:")
                                for rf in related:
                                    detail_lines.append(f"  - {rf.name}")

                    panel_content = "\n".join(detail_lines)
                    border = "green" if phase.get("success") else "red"
                    self.console.print(
                        Panel(panel_content, title=f"阶段: {p_name}", border_style=border)
                    )

            # 事件时间线
            if events:
                self.console.print("")
                self.console.print("[bold cyan]事件记录[/bold cyan]")
                for event in events[-20:]:  # 只展示最近 20 条
                    evt_ts = str(event.get("timestamp", "-"))
                    if "." in evt_ts:
                        evt_ts = evt_ts.split(".")[0]
                    evt_type = str(event.get("type", event.get("event", "-")))
                    evt_phase = str(event.get("phase", ""))
                    evt_msg = str(event.get("message", event.get("detail", "")))
                    line = f"  [dim]{evt_ts}[/dim] [{evt_type}] {evt_phase} {evt_msg}".strip()
                    self.console.print(line)

            # 历史快照概要
            if history_snapshots:
                self.console.print("")
                self.console.print(f"[dim]历史快照: {len(history_snapshots)} 个 "
                                   f"(位于 .super-dev/workflow-history/)[/dim]")

        else:
            # 非 Rich 模式
            self.console.print("=== Pipeline Replay ===")
            self.console.print(f"阶段总数: {len(phases_data)}")
            self.console.print(f"事件记录: {len(events)} 条")
            self.console.print(f"历史快照: {len(history_snapshots)} 个")
            self.console.print("")
            for phase in phases_data:
                p_name = phase.get("phase", "-")
                success = phase.get("success")
                dur = phase.get("duration", "-")
                qs = phase.get("quality_score", "-")
                status = "成功" if success else ("失败" if success is False else "-")
                self.console.print(f"  {p_name}: {status} | 耗时: {dur} | 质量分: {qs}")

        return 0

    # ------------------------------------------------------------------
    # guard command
    # ------------------------------------------------------------------

    def _cmd_guard(self, args: Any) -> int:
        """Run the real-time governance guard."""
        from ..guard import GovernanceGuard

        project_dir = Path.cwd()
        guard = GovernanceGuard(project_dir=project_dir)
        watch = not getattr(args, "no_watch", False)
        interval = getattr(args, "interval", 2.0)
        return guard.run(watch=watch, interval=interval)


def _format_mtime(mtime: float) -> str:
    """Format a file modification timestamp for display."""
    try:
        from datetime import datetime, timezone

        dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(int(mtime))
