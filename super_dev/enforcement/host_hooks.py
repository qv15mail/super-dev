"""
宿主侧 hooks 配置器 — 为 AI coding host 生成和安装执行 hooks。

支持的宿主:
- claude-code: 通过 .claude/settings.local.json 的 hooks 配置
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class HostHooksConfigurator:
    """为 AI coding host 生成和安装执行 hooks。"""

    SUPPORTED_HOSTS = ("claude-code",)

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def generate_hooks_config(self, host: str = "claude-code") -> dict[str, Any]:
        """生成宿主 hooks 配置。

        For Claude Code, this generates settings.json hooks:
        - PreToolUse for Write/Edit: validate no emoji, correct imports
        - PostToolUse for Bash: remind architecture conformance
        """
        if host == "claude-code":
            return self._claude_code_hooks()
        return {}

    def install_hooks(self, host: str = "claude-code") -> Path:
        """安装 hooks 到宿主配置文件。

        For Claude Code:
        - Reads existing .claude/settings.local.json
        - Merges Super Dev hooks into the hooks section
        - Does NOT overwrite user's existing hooks

        Returns:
            Path to the updated settings file.
        """
        if host == "claude-code":
            return self._install_claude_code_hooks()
        raise ValueError(f"Unsupported host: {host}")

    def generate_validation_script(self) -> Path:
        """生成 scripts/validate-superdev.sh 验证脚本。

        Delegates to ValidationScriptGenerator for the actual content.

        Returns:
            Path to the generated script.
        """
        from .validation import ValidationScriptGenerator

        generator = ValidationScriptGenerator()
        return generator.generate(self.project_dir)

    def generate_pre_code_checklist(self, frontend: str = "", backend: str = "") -> Path:
        """生成 .super-dev/PRE_CODE_CHECKLIST.md。

        Delegates to PreCodeGate for the actual content.

        Returns:
            Path to the generated checklist.
        """
        from .pre_code_gate import PreCodeGate

        gate = PreCodeGate()
        return gate.generate_checklist(self.project_dir, frontend=frontend, backend=backend)

    def get_status(self, host: str = "claude-code") -> dict[str, Any]:
        """返回当前 enforcement 状态摘要。"""
        status: dict[str, Any] = {
            "host": host,
            "hooks_installed": False,
            "validation_script_exists": False,
            "pre_code_checklist_exists": False,
        }
        try:
            if host == "claude-code":
                settings_path = self.project_dir / ".claude" / "settings.local.json"
                if settings_path.exists():
                    data = json.loads(settings_path.read_text(encoding="utf-8"))
                    hooks = data.get("hooks", {})
                    status["hooks_installed"] = bool(hooks.get("PreToolUse"))
            status["validation_script_exists"] = (
                self.project_dir / "scripts" / "validate-superdev.sh"
            ).exists()
            status["pre_code_checklist_exists"] = (
                self.project_dir / ".super-dev" / "PRE_CODE_CHECKLIST.md"
            ).exists()
        except Exception:
            pass
        return status

    # ------------------------------------------------------------------
    # Claude Code hooks
    # ------------------------------------------------------------------

    def _claude_code_hooks(self) -> dict[str, Any]:
        """Generate hooks config dict for Claude Code settings.local.json."""
        emoji_check_cmd = (
            'python3 -c "'
            "import sys,re,json; "
            "c=sys.stdin.read(); d=json.loads(c); "
            "ti=d.get('tool_input',{}); "
            "p=ti.get('file_path',''); "
            "ext=p.rsplit('.',1)[-1] if '.' in p else ''; "
            "content=ti.get('content','') or ti.get('new_string','') or ''; "
            "found=re.findall("
            "r'[\\u2600-\\u27BF\\U0001F300-\\U0001FAFF]', content) "
            "if ext in ('tsx','ts','jsx','js','vue','svelte') else []; "
            "unique=list(dict.fromkeys(found))[:5]; "
            "print(json.dumps("
            "{'decision':'block',"
            "'reason':'Super Dev: emoji ' + ' '.join(unique) + "
            "' found in .' + ext + ' file — use icon library instead'}"
            ' if unique else {}))"'
        )

        bash_remind_cmd = (
            'python3 -c "'
            "import sys,json; d=json.loads(sys.stdin.read()); "
            "cmd=d.get('tool_input',{}).get('command',''); "
            "print(json.dumps("
            "{'notify':'Super Dev: confirm output matches architecture docs'}"
            " if 'npm run' in cmd or 'pytest' in cmd else {}))\""
        )

        return {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": emoji_check_cmd,
                            "timeout": 5,
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": bash_remind_cmd,
                            "timeout": 5,
                        }
                    ],
                }
            ],
        }

    def _install_claude_code_hooks(self) -> Path:
        """Merge Super Dev hooks into .claude/settings.local.json."""
        claude_dir = self.project_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        settings_path = claude_dir / "settings.local.json"

        existing: dict[str, Any] = {}
        if settings_path.exists():
            try:
                existing = json.loads(settings_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = {}

        new_hooks = self._claude_code_hooks()
        merged_hooks = self._merge_hooks(existing.get("hooks", {}), new_hooks)
        existing["hooks"] = merged_hooks

        settings_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return settings_path

    @staticmethod
    def _merge_hooks(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        """Merge incoming hooks into existing without duplicating.

        Strategy: for each hook phase (PreToolUse, PostToolUse, etc.),
        add incoming entries whose *matcher* does not already appear.
        """
        merged = dict(existing)
        for phase, entries in incoming.items():
            if phase not in merged or not merged[phase]:
                merged[phase] = entries
                continue
            existing_matchers = {e.get("matcher") for e in merged[phase] if isinstance(e, dict)}
            for entry in entries:
                if entry.get("matcher") not in existing_matchers:
                    merged[phase].append(entry)
        return merged
