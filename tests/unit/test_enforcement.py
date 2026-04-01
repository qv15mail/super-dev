"""Unit tests for the enforcement module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """Create a minimal project directory."""
    (tmp_path / ".super-dev").mkdir()
    return tmp_path


class TestHostHooksConfigurator:
    def test_generate_hooks_config_claude_code(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        cfg = HostHooksConfigurator(project_dir)
        hooks = cfg.generate_hooks_config(host="claude-code")

        assert "PreToolUse" in hooks
        assert "PostToolUse" in hooks
        assert len(hooks["PreToolUse"]) >= 1
        assert hooks["PreToolUse"][0]["matcher"] == "Write|Edit"
        assert hooks["PostToolUse"][0]["matcher"] == "Bash"

    def test_generate_hooks_config_unknown_host(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        cfg = HostHooksConfigurator(project_dir)
        assert cfg.generate_hooks_config(host="unknown") == {}

    def test_install_hooks_creates_settings_file(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        cfg = HostHooksConfigurator(project_dir)
        path = cfg.install_hooks(host="claude-code")

        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "hooks" in data
        assert "PreToolUse" in data["hooks"]
        assert "PostToolUse" in data["hooks"]

    def test_install_hooks_merges_existing(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        claude_dir = project_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        settings_path = claude_dir / "settings.local.json"
        existing = {
            "permissions": {"allow": ["Read"]},
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}
                ]
            },
        }
        settings_path.write_text(json.dumps(existing), encoding="utf-8")

        cfg = HostHooksConfigurator(project_dir)
        cfg.install_hooks(host="claude-code")

        data = json.loads(settings_path.read_text(encoding="utf-8"))
        # Original permission preserved
        assert data["permissions"]["allow"] == ["Read"]
        # Original Bash hook preserved + Write|Edit added
        matchers = {e["matcher"] for e in data["hooks"]["PreToolUse"]}
        assert "Bash" in matchers
        assert "Write|Edit" in matchers

    def test_install_hooks_does_not_duplicate(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        cfg = HostHooksConfigurator(project_dir)
        cfg.install_hooks(host="claude-code")
        cfg.install_hooks(host="claude-code")

        settings_path = project_dir / ".claude" / "settings.local.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        pre_matchers = [e["matcher"] for e in data["hooks"]["PreToolUse"]]
        assert pre_matchers.count("Write|Edit") == 1

    def test_install_hooks_unsupported_host_raises(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        cfg = HostHooksConfigurator(project_dir)
        with pytest.raises(ValueError, match="Unsupported host"):
            cfg.install_hooks(host="unknown")

    def test_get_status(self, project_dir: Path):
        from super_dev.enforcement.host_hooks import HostHooksConfigurator

        cfg = HostHooksConfigurator(project_dir)

        # Before install
        status = cfg.get_status()
        assert status["hooks_installed"] is False
        assert status["validation_script_exists"] is False
        assert status["pre_code_checklist_exists"] is False

        # After install
        cfg.install_hooks()
        cfg.generate_validation_script()
        cfg.generate_pre_code_checklist()

        status = cfg.get_status()
        assert status["hooks_installed"] is True
        assert status["validation_script_exists"] is True
        assert status["pre_code_checklist_exists"] is True


class TestValidationScriptGenerator:
    def test_generate_creates_executable_script(self, project_dir: Path):
        from super_dev.enforcement.validation import ValidationScriptGenerator

        gen = ValidationScriptGenerator()
        path = gen.generate(project_dir)

        assert path.exists()
        assert path.name == "validate-superdev.sh"
        content = path.read_text(encoding="utf-8")
        assert content.startswith("#!/bin/bash")
        assert "ERRORS=0" in content
        assert "emoji" in content.lower()

    def test_generate_nextjs_check(self, project_dir: Path):
        from super_dev.enforcement.validation import ValidationScriptGenerator

        gen = ValidationScriptGenerator()
        path = gen.generate(project_dir, frontend="next")
        content = path.read_text(encoding="utf-8")
        assert "App Router" in content or "route" in content.lower()

    def test_generate_eslint_rules(self, project_dir: Path):
        from super_dev.enforcement.validation import ValidationScriptGenerator

        gen = ValidationScriptGenerator()
        path = gen.generate_eslint_rules(project_dir, icon_library="lucide")

        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "rules" in data
        assert "lucide-react" in json.dumps(data)

    def test_icon_package_mapping(self):
        from super_dev.enforcement.validation import ValidationScriptGenerator

        gen = ValidationScriptGenerator()
        assert gen._icon_package("lucide") == "lucide-react"
        assert gen._icon_package("heroicons") == "@heroicons/react"
        assert gen._icon_package("unknown") == "lucide-react"


class TestPreCodeGate:
    def test_generate_checklist(self, project_dir: Path):
        from super_dev.enforcement.pre_code_gate import PreCodeGate

        gate = PreCodeGate()
        path = gate.generate_checklist(project_dir, frontend="next", backend="node")

        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Pre-Code Checklist" in content
        assert "App Router" in content
        assert "node" in content

    def test_check_completion_not_exists(self, project_dir: Path):
        from super_dev.enforcement.pre_code_gate import PreCodeGate

        gate = PreCodeGate()
        ok, items = gate.check_completion(project_dir)
        assert ok is False
        assert "does not exist" in items[0]

    def test_check_completion_incomplete(self, project_dir: Path):
        from super_dev.enforcement.pre_code_gate import PreCodeGate

        gate = PreCodeGate()
        gate.generate_checklist(project_dir)

        ok, items = gate.check_completion(project_dir)
        assert ok is False
        assert len(items) > 0

    def test_check_completion_all_done(self, project_dir: Path):
        from super_dev.enforcement.pre_code_gate import PreCodeGate

        gate = PreCodeGate()
        path = gate.generate_checklist(project_dir)

        # Mark all items as complete
        content = path.read_text(encoding="utf-8")
        content = content.replace("- [ ]", "- [x]")
        path.write_text(content, encoding="utf-8")

        ok, items = gate.check_completion(project_dir)
        assert ok is True
        assert items == []


class TestEnforcementBridge:
    def test_auto_install_enforcement(self, project_dir: Path):
        from super_dev._enforcement_bridge import auto_install_enforcement

        files = auto_install_enforcement(project_dir)
        # Only hooks config is installed during auto-setup;
        # validation script and checklist are generated on demand.
        assert len(files) == 1
        names = {f.name for f in files}
        assert "settings.local.json" in names
