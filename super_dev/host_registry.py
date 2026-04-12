"""Formal host registry for Super Dev.

This module keeps host metadata in one place so callers can read display names,
install modes, trigger surfaces, and documentation surfaces without depending
on the larger integration manager.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class HostInstallMode(str, Enum):
    """How a host is installed and maintained."""

    PROJECT = "project"
    USER = "user"
    HYBRID = "hybrid"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class HostDefinition:
    """Immutable metadata for a supported host."""

    host_id: str
    display_name: str
    install_mode: HostInstallMode
    protocol_mode: str
    protocol_summary: str
    supports_slash: bool
    triggers: tuple[str, ...]
    docs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HostRegistry:
    """Read-only registry with lookup helpers."""

    definitions: tuple[HostDefinition, ...]
    _by_id: dict[str, HostDefinition] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_id: dict[str, HostDefinition] = {}
        duplicates: list[str] = []
        for definition in self.definitions:
            if definition.host_id in by_id:
                duplicates.append(definition.host_id)
            by_id[definition.host_id] = definition
        if duplicates:
            duplicate_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Duplicate host ids in registry: {duplicate_list}")
        object.__setattr__(self, "_by_id", by_id)

    def get(self, host_id: str) -> HostDefinition | None:
        return self._by_id.get(host_id)

    def require(self, host_id: str) -> HostDefinition:
        definition = self.get(host_id)
        if definition is None:
            raise KeyError(host_id)
        return definition

    def list_host_ids(self) -> tuple[str, ...]:
        return tuple(definition.host_id for definition in self.definitions)

    def list_by_install_mode(self, install_mode: HostInstallMode) -> tuple[HostDefinition, ...]:
        return tuple(
            definition for definition in self.definitions if definition.install_mode == install_mode
        )

    def list_manual_hosts(self) -> tuple[HostDefinition, ...]:
        return self.list_by_install_mode(HostInstallMode.MANUAL)

    def list_hybrid_hosts(self) -> tuple[HostDefinition, ...]:
        return self.list_by_install_mode(HostInstallMode.HYBRID)

    def list_project_hosts(self) -> tuple[HostDefinition, ...]:
        return self.list_by_install_mode(HostInstallMode.PROJECT)

    def list_user_hosts(self) -> tuple[HostDefinition, ...]:
        return self.list_by_install_mode(HostInstallMode.USER)


def _tuple(*items: str) -> tuple[str, ...]:
    return tuple(item for item in items if item)


DEFAULT_HOST_REGISTRY = HostRegistry(
    definitions=(
        HostDefinition(
            host_id="antigravity",
            display_name="Antigravity",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-workflow",
            protocol_summary="官方 commands + workflows + skills",
            supports_slash=True,
            triggers=_tuple("super-dev: <需求描述>", "super-dev：<需求描述>", "/super-dev"),
            docs=_tuple(
                "Project root `GEMINI.md`",
                "Project-level `.gemini/commands/`",
                "Project-level `.agent/workflows/`",
                "User-level `~/.gemini/GEMINI.md`",
                "User-level `~/.gemini/commands/`",
                "User-level `~/.gemini/skills/super-dev/SKILL.md`",
            ),
        ),
        HostDefinition(
            host_id="claude-code",
            display_name="Claude Code",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-skill",
            protocol_summary="官方 CLAUDE.md + Skills + optional repo plugin enhancement",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev：", "/super-dev-seeai"),
            docs=_tuple(
                "Project root `CLAUDE.md`",
                "Project-level `.claude/skills/super-dev/`",
                "Project-level `.claude/commands/super-dev.md`",
                "User-level `~/.claude/skills/super-dev/`",
                "User-level `~/.claude/commands/super-dev.md`",
            ),
        ),
        HostDefinition(
            host_id="cline",
            display_name="Cline",
            install_mode=HostInstallMode.PROJECT,
            protocol_mode="official-context",
            protocol_summary="官方 .clinerules + skills + AGENTS.md compatibility",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev："),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project-level `.clinerules/`",
                "Project-level `.cline/skills/`",
                "User-level `~/.cline/skills/super-dev/SKILL.md`",
            ),
        ),
        HostDefinition(
            host_id="codebuddy-cli",
            display_name="CodeBuddy CLI",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-subagent",
            protocol_summary="官方 CODEBUDDY.md + commands + skills + AGENTS.md compatibility",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev：", "/super-dev-seeai"),
            docs=_tuple(
                "Project root `CODEBUDDY.md`",
                "Project-level `.codebuddy/rules/`",
                "Project-level `.codebuddy/commands/`",
                "Project-level `.codebuddy/skills/`",
                "User-level `~/.codebuddy/CODEBUDDY.md`",
                "User-level `~/.codebuddy/skills/`",
            ),
        ),
        HostDefinition(
            host_id="codebuddy",
            display_name="CodeBuddy IDE",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-subagent",
            protocol_summary="官方 CODEBUDDY.md + rules + commands + agents + skills",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev：", "/super-dev-seeai"),
            docs=_tuple(
                "Project root `CODEBUDDY.md`",
                "Project-level `.codebuddy/rules/`",
                "Project-level `.codebuddy/agents/`",
                "Project-level `.codebuddy/commands/`",
                "Project-level `.codebuddy/skills/`",
                "User-level `~/.codebuddy/CODEBUDDY.md`",
                "User-level `~/.codebuddy/skills/`",
            ),
        ),
        HostDefinition(
            host_id="codex-cli",
            display_name="Codex",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-skill",
            protocol_summary="官方 AGENTS.md + 官方 Skills + optional repo plugin enhancement",
            supports_slash=False,
            triggers=_tuple(
                "$super-dev", "$super-dev-seeai", "super-dev:", "super-dev：", "/super-dev"
            ),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project-level `.agents/skills/super-dev/`",
                "Project-level `.agents/skills/super-dev-seeai/`",
                "Project-level `.agents/plugins/marketplace.json`",
                "User-level `~/.codex/AGENTS.md`",
                "User-level `~/.agents/skills/super-dev/`",
                "User-level `~/.agents/skills/super-dev-seeai/`",
            ),
        ),
        HostDefinition(
            host_id="copilot-cli",
            display_name="Copilot CLI",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-context",
            protocol_summary="官方 copilot-instructions + skills + AGENTS.md compatibility",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev："),
            docs=_tuple(
                "Project root `.github/copilot-instructions.md`",
                "Project-level `.github/skills/`",
                "User-level `~/.copilot/skills/`",
            ),
        ),
        HostDefinition(
            host_id="cursor-cli",
            display_name="Cursor CLI",
            install_mode=HostInstallMode.PROJECT,
            protocol_mode="official-context",
            protocol_summary="官方 commands + rules + AGENTS.md compatibility",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev："),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project root `CLAUDE.md`",
                "Project-level `.cursor/rules/`",
            ),
        ),
        HostDefinition(
            host_id="cursor",
            display_name="Cursor IDE",
            install_mode=HostInstallMode.PROJECT,
            protocol_mode="official-context",
            protocol_summary="官方 commands + rules + AGENTS.md compatibility",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev："),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project root `CLAUDE.md`",
                "Project-level `.cursor/rules/`",
            ),
        ),
        HostDefinition(
            host_id="gemini-cli",
            display_name="Gemini CLI",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-context",
            protocol_summary="官方 commands + GEMINI.md",
            supports_slash=True,
            triggers=_tuple("super-dev:", "super-dev：", "/super-dev"),
            docs=_tuple(
                "Project root `GEMINI.md`",
                "Project-level `.gemini/commands/`",
                "Project-level `.gemini/skills/`",
                "User-level `~/.gemini/GEMINI.md`",
                "User-level `~/.gemini/commands/`",
                "User-level `~/.gemini/skills/`",
            ),
        ),
        HostDefinition(
            host_id="kiro-cli",
            display_name="Kiro CLI",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-steering",
            protocol_summary="官方 steering + slash entry + skills",
            supports_slash=True,
            triggers=_tuple("super-dev:", "super-dev：", "/super-dev"),
            docs=_tuple(
                "Project-level `.kiro/steering/`",
                "Project-level `.kiro/skills/`",
                "User-level `~/.kiro/steering/`",
                "User-level `~/.kiro/skills/`",
            ),
        ),
        HostDefinition(
            host_id="kiro",
            display_name="Kiro IDE",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-steering",
            protocol_summary="官方 steering + slash entry + skills",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev："),
            docs=_tuple(
                "Project-level `.kiro/steering/`",
                "Project-level `.kiro/skills/`",
                "User-level `~/.kiro/steering/`",
                "User-level `~/.kiro/skills/`",
            ),
        ),
        HostDefinition(
            host_id="kilo-code",
            display_name="Kilo Code",
            install_mode=HostInstallMode.PROJECT,
            protocol_mode="official-skill",
            protocol_summary="官方 commands + rules",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev："),
            docs=_tuple(
                "Project-level `.kilocode/rules/`",
                "Project-level `.kilocode/commands/`",
            ),
        ),
        HostDefinition(
            host_id="opencode",
            display_name="OpenCode",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-skill",
            protocol_summary="官方 commands + skills + AGENTS.md compatibility",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev："),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project-level `.opencode/commands/`",
                "Project-level `.opencode/skills/`",
                "User-level `~/.config/opencode/AGENTS.md`",
                "User-level `~/.config/opencode/skills/`",
            ),
        ),
        HostDefinition(
            host_id="openclaw",
            display_name="OpenClaw",
            install_mode=HostInstallMode.MANUAL,
            protocol_mode="manual-skill",
            protocol_summary="官方自然语言任务 + Skills + MCP + 文件侧栏",
            supports_slash=True,
            triggers=_tuple(
                "super-dev:", "super-dev：", "/super-dev", "super-dev-seeai:", "super-dev-seeai："
            ),
            docs=_tuple(
                "OpenClaw Plugin SDK",
                "Project-level `.openclaw/rules/super-dev.md`",
                "Project-level `.openclaw/commands/super-dev.md`",
                "Project-level `.openclaw/commands/super-dev-seeai.md`",
                "User-level `~/.openclaw/skills/super-dev/SKILL.md`",
                "User-level `~/.openclaw/skills/super-dev-seeai/SKILL.md`",
            ),
        ),
        HostDefinition(
            host_id="qoder-cli",
            display_name="Qoder CLI",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-skill",
            protocol_summary="官方 commands + rules + skills + AGENTS.md compatibility",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev：", "/super-dev-seeai"),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project-level `.qoder/rules/`",
                "Project-level `.qoder/commands/`",
                "Project-level `.qoder/skills/`",
                "User-level `~/.qoder/AGENTS.md`",
                "User-level `~/.qoder/skills/`",
            ),
        ),
        HostDefinition(
            host_id="qoder",
            display_name="Qoder IDE",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-skill",
            protocol_summary="官方 commands + rules + skills + AGENTS.md compatibility",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev：", "/super-dev-seeai"),
            docs=_tuple(
                "Project root `AGENTS.md`",
                "Project-level `.qoder/rules/`",
                "Project-level `.qoder/commands/`",
                "Project-level `.qoder/skills/`",
                "User-level `~/.qoder/AGENTS.md`",
                "User-level `~/.qoder/skills/`",
            ),
        ),
        HostDefinition(
            host_id="roo-code",
            display_name="Roo Code",
            install_mode=HostInstallMode.PROJECT,
            protocol_mode="official-skill",
            protocol_summary="官方 commands + rules",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev："),
            docs=_tuple(
                "Project-level `.roo/rules/`",
                "Project-level `.roo/commands/`",
            ),
        ),
        HostDefinition(
            host_id="trae",
            display_name="Trae",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-context",
            protocol_summary="官方 project_rules + rules + skills",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev：", "super-dev-seeai:", "super-dev-seeai："),
            docs=_tuple(
                "Project-level `.trae/project_rules.md`",
                "Project-level `.trae/rules.md`",
                "User-level `~/.trae/user_rules.md`",
                "User-level `~/.trae/rules.md`",
                "User-level `~/.trae/skills/super-dev/SKILL.md`",
            ),
        ),
        HostDefinition(
            host_id="windsurf",
            display_name="Windsurf",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="official-workflow",
            protocol_summary="官方 commands + workflows + skills",
            supports_slash=True,
            triggers=_tuple("/super-dev", "super-dev:", "super-dev：", "/super-dev-seeai"),
            docs=_tuple(
                "Project-level `.windsurf/rules/`",
                "Project-level `.windsurf/workflows/`",
                "Project-level `.windsurf/skills/`",
                "User-level `~/.codeium/windsurf/skills/`",
            ),
        ),
        HostDefinition(
            host_id="workbuddy",
            display_name="WorkBuddy",
            install_mode=HostInstallMode.HYBRID,
            protocol_mode="skills",
            protocol_summary="官方 Skills + MCP + 文件侧栏",
            supports_slash=False,
            triggers=_tuple("super-dev:", "super-dev：", "super-dev-seeai:", "super-dev-seeai："),
            docs=_tuple(
                "WorkBuddy 当前任务 / 对话会话",
                "WorkBuddy 技能市场",
                "项目工作目录或授权文件夹",
            ),
        ),
    )
)


HOST_REGISTRY = DEFAULT_HOST_REGISTRY


def get_host_definition(host_id: str) -> HostDefinition | None:
    """Return the registered definition for a host id."""

    return HOST_REGISTRY.get(host_id)


def get_display_name(host_id: str) -> str | None:
    definition = get_host_definition(host_id)
    return definition.display_name if definition else None


def get_install_mode(host_id: str) -> HostInstallMode | None:
    definition = get_host_definition(host_id)
    return definition.install_mode if definition else None


def get_protocol_mode(host_id: str) -> str | None:
    definition = get_host_definition(host_id)
    return definition.protocol_mode if definition else None


def get_protocol_summary(host_id: str) -> str | None:
    definition = get_host_definition(host_id)
    return definition.protocol_summary if definition else None


def supports_slash(host_id: str) -> bool:
    definition = get_host_definition(host_id)
    return definition.supports_slash if definition else False


def get_triggers(host_id: str) -> tuple[str, ...]:
    definition = get_host_definition(host_id)
    return definition.triggers if definition else ()


def get_docs(host_id: str) -> tuple[str, ...]:
    definition = get_host_definition(host_id)
    return definition.docs if definition else ()


def iter_host_definitions() -> tuple[HostDefinition, ...]:
    return HOST_REGISTRY.definitions


def list_host_ids() -> tuple[str, ...]:
    return HOST_REGISTRY.list_host_ids()


def list_manual_hosts() -> tuple[HostDefinition, ...]:
    return HOST_REGISTRY.list_manual_hosts()


def list_hybrid_hosts() -> tuple[HostDefinition, ...]:
    return HOST_REGISTRY.list_hybrid_hosts()


def list_project_hosts() -> tuple[HostDefinition, ...]:
    return HOST_REGISTRY.list_project_hosts()


def list_user_hosts() -> tuple[HostDefinition, ...]:
    return HOST_REGISTRY.list_user_hosts()


__all__ = [
    "DEFAULT_HOST_REGISTRY",
    "HOST_REGISTRY",
    "HostDefinition",
    "HostInstallMode",
    "HostRegistry",
    "get_display_name",
    "get_docs",
    "get_host_definition",
    "get_install_mode",
    "get_protocol_mode",
    "get_protocol_summary",
    "get_triggers",
    "iter_host_definitions",
    "list_host_ids",
    "list_hybrid_hosts",
    "list_manual_hosts",
    "list_project_hosts",
    "list_user_hosts",
    "supports_slash",
]
