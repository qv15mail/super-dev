"""Thin bridge so integrations.manager can call enforcement without circular imports."""

from __future__ import annotations

from pathlib import Path


def auto_install_enforcement(project_dir: Path) -> list[Path]:
    """Install enforcement hooks during host setup.

    Only installs the hooks config (e.g. settings.local.json).
    Validation script and pre-code checklist are generated on demand
    via ``super-dev enforce install`` / ``super-dev enforce validate``.

    Returns list of written file paths.  Errors are swallowed so the
    caller's setup flow is never broken.
    """
    written: list[Path] = []
    try:
        from .enforcement.host_hooks import HostHooksConfigurator

        configurator = HostHooksConfigurator(project_dir)
        settings_path = configurator.install_hooks(host="claude-code")
        written.append(settings_path)
    except Exception:
        pass

    return written
