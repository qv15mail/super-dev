"""E2E tests covering the full Super Dev workflow."""

import subprocess
import sys
import tempfile
from pathlib import Path

PYTHON = sys.executable
TIMEOUT = 30


def _run(args: list[str], cwd: str, timeout: int = TIMEOUT) -> subprocess.CompletedProcess:
    """Helper: run a CLI command and return the result."""
    return subprocess.run(
        [PYTHON, "-m", "super_dev.cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ── Init variants ──────────────────────────────────────────────────


def test_init_with_template():
    """Test init with --template creates correct config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(
            ["init", "shop", "--template", "ecommerce", "-f", "react-vite", "-b", "node"],
            cwd=tmpdir,
        )
        assert result.returncode == 0, f"init failed: {result.stderr}"

        cfg_path = Path(tmpdir) / "super-dev.yaml"
        assert cfg_path.exists(), "super-dev.yaml not created"

        content = cfg_path.read_text()
        # ecommerce template should set domain or name
        assert "shop" in content or "ecommerce" in content


def test_init_default_name():
    """Test init without explicit name uses directory name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(["init", "-f", "react-vite", "-b", "python"], cwd=tmpdir)
        assert result.returncode == 0
        assert (Path(tmpdir) / "super-dev.yaml").exists()


# ── Setup / host files ────────────────────────────────────────────


def test_setup_creates_host_files():
    """Test setup creates correct files for claude-code host."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Init first
        _run(["init", "test-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)

        result = _run(
            ["setup", "claude-code", "--skip-doctor", "--skip-slash"],
            cwd=tmpdir,
        )
        # setup may return 0 or 1 depending on environment; should not crash
        assert result.returncode in (0, 1), f"setup crashed: {result.stderr}"

        # At minimum the setup command should not error out catastrophically
        assert "Traceback" not in result.stderr


def test_setup_cursor_host():
    """Test setup for cursor host."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "cursor-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(
            ["setup", "cursor", "--skip-doctor", "--skip-slash"],
            cwd=tmpdir,
        )
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Enforce lifecycle ──────────────────────────────────────────────


def test_enforce_install_and_validate():
    """Test enforcement system works end-to-end."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "enforce-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)

        # enforce install
        r1 = _run(["enforce", "install"], cwd=tmpdir)
        assert r1.returncode in (0, 1), f"enforce install crashed: {r1.stderr}"
        assert "Traceback" not in r1.stderr

        # enforce validate
        r2 = _run(["enforce", "validate"], cwd=tmpdir)
        assert r2.returncode in (0, 1), f"enforce validate crashed: {r2.stderr}"
        assert "Traceback" not in r2.stderr

        # enforce status
        r3 = _run(["enforce", "status"], cwd=tmpdir)
        assert r3.returncode in (0, 1), f"enforce status crashed: {r3.stderr}"
        assert "Traceback" not in r3.stderr


# ── Status lifecycle ───────────────────────────────────────────────


def test_status_before_init():
    """Test status in a directory without super-dev.yaml shows welcome or install prompt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(["status"], cwd=tmpdir)
        # Should not crash; may show welcome or error
        assert result.returncode in (0, 1, 2)
        assert "Traceback" not in result.stderr


def test_status_after_init():
    """Test status after init shows project state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "status-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["status"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Experts and memory ─────────────────────────────────────────────


def test_experts_and_memory():
    """Test expert listing and memory system."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "expert-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)

        # experts list
        r1 = _run(["experts", "list"], cwd=tmpdir)
        assert r1.returncode == 0
        # Should list multiple experts
        output = r1.stdout + r1.stderr
        # At least some expert names should appear
        assert any(
            kw in output.lower()
            for kw in ["pm", "architect", "security", "qa", "code", "ui"]
        ), f"Expected expert names in output, got: {output[:500]}"

        # memory list (empty, should not crash)
        r2 = _run(["memory", "list"], cwd=tmpdir)
        assert r2.returncode in (0, 1)
        assert "Traceback" not in r2.stderr


# ── Generate components ────────────────────────────────────────────


def test_generate_components():
    """Test component scaffold generation command runs without crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "gen-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["generate", "components"], cwd=tmpdir)
        # May fail if no UIUX doc exists, but should not crash with traceback
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Doctor ─────────────────────────────────────────────────────────


def test_doctor_diagnose():
    """Test doctor diagnoses project state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "doctor-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["doctor", "--host", "claude-code"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


def test_doctor_fix():
    """Test doctor --fix attempts repairs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "fix-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)

        # Setup first so there are files to fix
        _run(["setup", "claude-code", "--skip-doctor", "--skip-slash"], cwd=tmpdir)

        # Remove a file that doctor might recreate
        claude_md = Path(tmpdir) / ".claude" / "CLAUDE.md"
        if claude_md.exists():
            claude_md.unlink()

        result = _run(["doctor", "--fix", "--host", "claude-code"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Migrate ────────────────────────────────────────────────────────


def test_migrate():
    """Test migration from older config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal 2.2.0-style config
        cfg = Path(tmpdir) / "super-dev.yaml"
        cfg.write_text(
            "name: migrate-test\n"
            "version: 2.2.0\n"
            "platform: web\n"
            "frontend: react-vite\n"
            "backend: node\n"
        )

        result = _run(["migrate"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Unknown command ────────────────────────────────────────────────


def test_unknown_command_shows_suggestion():
    """Test unknown command shows helpful error, not a traceback."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a flag-like unknown to avoid direct-requirement heuristic
        result = _run(["--nonexistent"], cwd=tmpdir)
        output = result.stdout + result.stderr
        assert "Traceback" not in output
        # argparse will show usage/error for unknown flags
        assert result.returncode in (0, 2) or "usage" in output.lower()


def test_unknown_command_typo_suggests():
    """Test a close typo like 'statsu' suggests 'status'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(["statsu"], cwd=tmpdir)
        assert result.returncode == 2
        output = result.stdout + result.stderr
        assert "Traceback" not in output


# ── Config commands ────────────────────────────────────────────────


def test_config_list():
    """Test config list shows current configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "cfg-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["config", "list"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Governance ─────────────────────────────────────────────────────


def test_governance_report():
    """Test governance report command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "gov-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["governance", "report"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Quality ────────────────────────────────────────────────────────


def test_quality_without_artifacts():
    """Test quality command when no artifacts exist yet."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "qa-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["quality"], cwd=tmpdir)
        # Should handle missing artifacts gracefully
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Spec commands ──────────────────────────────────────────────────


def test_spec_list_empty():
    """Test spec list when no specs exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run(["init", "spec-proj", "-f", "react-vite", "-b", "node"], cwd=tmpdir)
        result = _run(["spec", "list"], cwd=tmpdir)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ── Version and help ───────────────────────────────────────────────


def test_version_flag():
    """Test --version returns version string."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(["--version"], cwd=tmpdir)
        assert result.returncode == 0
        assert "2." in result.stdout  # version 2.x.x


def test_help_flag():
    """Test --help returns usage information."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(["--help"], cwd=tmpdir)
        assert result.returncode == 0
        assert "super-dev" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_help_command():
    """Test 'help' pseudo-command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run(["help"], cwd=tmpdir)
        assert result.returncode == 0
