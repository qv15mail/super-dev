from pathlib import Path

from super_dev.migrate import _detect_onboarded_hosts, migrate_project


def test_detect_onboarded_hosts_ignores_shared_surface_only(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# shared\n", encoding="utf-8")
    detected = _detect_onboarded_hosts(tmp_path)
    assert detected == []


def test_detect_onboarded_hosts_uses_family_specific_markers(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# shared\n", encoding="utf-8")
    (tmp_path / ".opencode" / "commands").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".opencode" / "commands" / "super-dev.md").write_text(
        "# command\n", encoding="utf-8"
    )
    detected = _detect_onboarded_hosts(tmp_path)
    assert detected == ["opencode"]


def test_detect_onboarded_hosts_prefers_manifest(tmp_path: Path) -> None:
    manifest_dir = tmp_path / ".super-dev"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "install-manifest.json").write_text(
        """
        {
          "version": 1,
          "targets": {
            "cursor": {
              "host": "cursor",
              "family": "cursor",
              "scopes": {"project": true, "global": false, "runtime": false},
              "paths": [".cursor/rules/super-dev.mdc"]
            }
          }
        }
        """.strip(),
        encoding="utf-8",
    )
    (tmp_path / ".cursor" / "rules").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".cursor" / "rules" / "super-dev.mdc").write_text("rule", encoding="utf-8")

    detected = _detect_onboarded_hosts(tmp_path)
    assert detected == ["cursor"]


def test_migrate_project_does_not_install_claude_hooks_without_claude(tmp_path: Path) -> None:
    (tmp_path / "super-dev.yaml").write_text("name: demo\nversion: 2.3.3\n", encoding="utf-8")
    changes = migrate_project(tmp_path)
    assert any("版本号" in item for item in changes)
    assert not (tmp_path / ".claude" / "settings.local.json").exists()
