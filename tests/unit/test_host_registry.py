"""Tests for the formal host registry module."""

from super_dev.host_registry import (
    HOST_REGISTRY,
    HostInstallMode,
    get_display_name,
    get_docs,
    get_host_definition,
    get_install_mode,
    get_protocol_mode,
    get_protocol_summary,
    get_triggers,
    list_host_ids,
    list_hybrid_hosts,
    list_manual_hosts,
    list_project_hosts,
    supports_slash,
)


def test_registry_exposes_key_and_manual_hosts():
    host_ids = set(list_host_ids())

    assert {
        "claude-code",
        "codex-cli",
        "codebuddy-cli",
        "codebuddy",
        "openclaw",
        "workbuddy",
    }.issubset(host_ids)
    assert len(host_ids) == len(list_host_ids())


def test_registry_helpers_return_expected_host_metadata():
    claude = get_host_definition("claude-code")
    assert claude is not None
    assert get_display_name("claude-code") == "Claude Code"
    assert get_install_mode("claude-code") == HostInstallMode.HYBRID
    assert get_protocol_mode("claude-code") == "official-skill"
    assert (
        get_protocol_summary("claude-code")
        == "官方 CLAUDE.md + Skills + optional repo plugin enhancement"
    )
    assert supports_slash("claude-code") is True
    assert "/super-dev" in get_triggers("claude-code")
    assert "Project root `CLAUDE.md`" in get_docs("claude-code")
    assert "User-level `~/.claude/skills/super-dev/`" in get_docs("claude-code")

    codex = get_host_definition("codex-cli")
    assert codex is not None
    assert get_protocol_mode("codex-cli") == "official-skill"
    assert (
        get_protocol_summary("codex-cli")
        == "官方 AGENTS.md + 官方 Skills + optional repo plugin enhancement"
    )
    assert supports_slash("codex-cli") is False

    codebuddy = get_host_definition("codebuddy")
    assert codebuddy is not None
    assert get_protocol_mode("codebuddy") == "official-subagent"
    assert (
        get_protocol_summary("codebuddy")
        == "官方 CODEBUDDY.md + rules + commands + agents + skills"
    )
    assert supports_slash("codebuddy") is True

    openclaw = get_host_definition("openclaw")
    assert openclaw is not None
    assert get_display_name("openclaw") == "OpenClaw"
    assert get_install_mode("openclaw") == HostInstallMode.MANUAL
    assert get_protocol_mode("openclaw") == "manual-skill"
    assert get_protocol_summary("openclaw") == "官方自然语言任务 + Skills + MCP + 文件侧栏"
    assert supports_slash("openclaw") is True
    assert "super-dev-seeai:" in get_triggers("openclaw")
    assert "OpenClaw Plugin SDK" in get_docs("openclaw")

    workbuddy = get_host_definition("workbuddy")
    assert workbuddy is not None
    assert get_display_name("workbuddy") == "WorkBuddy"
    assert get_install_mode("workbuddy") == HostInstallMode.HYBRID
    assert get_protocol_mode("workbuddy") == "skills"
    assert get_protocol_summary("workbuddy") == "官方 Skills + MCP + 文件侧栏"
    assert supports_slash("workbuddy") is False
    assert "super-dev-seeai:" in get_triggers("workbuddy")
    assert "WorkBuddy 技能市场" in get_docs("workbuddy")


def test_registry_groups_by_install_mode():
    manual_hosts = {item.host_id for item in list_manual_hosts()}
    hybrid_hosts = {item.host_id for item in list_hybrid_hosts()}
    project_hosts = {item.host_id for item in list_project_hosts()}

    assert {"openclaw"} == manual_hosts
    assert {"claude-code", "codex-cli", "codebuddy-cli", "codebuddy", "workbuddy"}.issubset(hybrid_hosts)
    assert {"cursor", "cursor-cli", "roo-code", "kilo-code"}.issubset(project_hosts)
    assert manual_hosts.isdisjoint(hybrid_hosts)
    assert manual_hosts.isdisjoint(project_hosts)


def test_registry_protocol_fields_are_populated_for_key_hosts():
    key_hosts = {
        "antigravity",
        "claude-code",
        "codebuddy-cli",
        "codebuddy",
        "codex-cli",
        "gemini-cli",
        "kiro",
        "kiro-cli",
        "openclaw",
        "qoder",
        "qoder-cli",
        "windsurf",
        "workbuddy",
    }

    for host_id in key_hosts:
        assert get_protocol_mode(host_id)
        assert get_protocol_summary(host_id)


def test_registry_is_frozen_and_unknown_hosts_are_safe():
    definition = get_host_definition("does-not-exist")
    assert definition is None
    assert get_display_name("does-not-exist") is None
    assert get_install_mode("does-not-exist") is None
    assert get_protocol_mode("does-not-exist") is None
    assert get_protocol_summary("does-not-exist") is None
    assert get_triggers("does-not-exist") == ()
    assert get_docs("does-not-exist") == ()
    assert supports_slash("does-not-exist") is False
    assert HOST_REGISTRY.require("claude-code").host_id == "claude-code"
