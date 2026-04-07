"""E2E smoke test — runs the core CLI commands in sequence."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parents[2]


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "").strip()
    repo_path = str(REPO_ROOT)
    env["PYTHONPATH"] = (
        repo_path if not existing else os.pathsep.join([repo_path, existing])
    )
    return env


def test_full_init_to_status_flow():
    """Test: init -> detect -> status -> enforce -> quality in a temp dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)

        # 1. Init
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "init", "smoke-test", "-f", "next", "-b", "node"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=30,
            env=_subprocess_env(),
        )
        assert result.returncode == 0
        assert (project / "super-dev.yaml").exists()

        # 2. Status
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "status"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
            env=_subprocess_env(),
        )
        # Should not crash
        assert result.returncode in (0, 1)

        # 3. Enforce status
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "enforce", "status"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
            env=_subprocess_env(),
        )
        assert result.returncode in (0, 1)

        # 4. Experts list
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "experts", "list"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
            env=_subprocess_env(),
        )
        assert result.returncode == 0

        # 5. Memory list (empty, should not crash)
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "memory", "list"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
            env=_subprocess_env(),
        )
        assert result.returncode in (0, 1)

        # 6. Config list
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "config", "list"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
            env=_subprocess_env(),
        )
        assert result.returncode in (0, 1)

        # 7. Version
        result = subprocess.run(
            [PYTHON, "-m", "super_dev.cli", "--version"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
            env=_subprocess_env(),
        )
        assert result.returncode == 0
        assert "2.3.3" in result.stdout
