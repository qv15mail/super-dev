"""
多平台 AI Coding 工具集成管理器
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from ..catalogs import HOST_TOOL_CATEGORY_MAP, HOST_TOOL_IDS
from .manager_content_mixin import IntegrationManagerContentMixin


@dataclass
class IntegrationTarget:
    name: str
    description: str
    files: list[str]
    optional_files: list[str] = field(default_factory=list)


@dataclass
class HostAdapterProfile:
    host: str
    category: str
    adapter_mode: str
    host_model_provider: str
    certification_level: str
    certification_label: str
    certification_reason: str
    certification_evidence: list[str]
    official_docs_url: str
    docs_verified: bool
    primary_entry: str
    terminal_entry: str
    terminal_entry_scope: str
    integration_files: list[str]
    slash_command_file: str
    skill_dir: str
    detection_commands: list[str]
    detection_paths: list[str]
    notes: str
    usage_mode: str
    trigger_command: str
    entry_variants: list[dict[str, str]]
    trigger_context: str
    usage_location: str
    requires_restart_after_onboard: bool
    post_onboard_steps: list[str]
    usage_notes: list[str]
    smoke_test_prompt: str
    smoke_test_steps: list[str]
    smoke_success_signal: str
    precondition_status: str
    precondition_label: str
    precondition_guidance: list[str]
    precondition_signals: dict[str, bool]
    precondition_items: list[dict[str, object]]
    host_protocol_mode: str
    host_protocol_summary: str
    official_project_surfaces: list[str]
    official_user_surfaces: list[str]
    optional_project_surfaces: list[str]
    optional_user_surfaces: list[str]
    observed_compatibility_surfaces: list[str]
    official_docs_references: list[str]
    docs_check_status: str
    docs_check_summary: str
    capability_labels: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class IntegrationManager(IntegrationManagerContentMixin):
    """为不同 AI Coding 平台生成集成配置"""

    TEXT_TRIGGER_PREFIX = "super-dev:"
    TEXT_TRIGGER_PREFIX_FULLWIDTH = "super-dev："
    CODEX_AGENTS_BEGIN = "<!-- BEGIN SUPER DEV CODEX -->"
    CODEX_AGENTS_END = "<!-- END SUPER DEV CODEX -->"
    OPENCODE_AGENTS_BEGIN = "<!-- BEGIN SUPER DEV OPENCODE -->"
    OPENCODE_AGENTS_END = "<!-- END SUPER DEV OPENCODE -->"
    QODER_AGENTS_BEGIN = "<!-- BEGIN SUPER DEV QODER -->"
    QODER_AGENTS_END = "<!-- END SUPER DEV QODER -->"
    CLAUDE_RULES_BEGIN = "<!-- BEGIN SUPER DEV CLAUDE -->"
    CLAUDE_RULES_END = "<!-- END SUPER DEV CLAUDE -->"
    NO_SKILL_TARGETS: set[str] = {
        "cline",
        "kilo-code",
        "vscode-copilot",
    }
    HOST_USAGE_LOCATIONS: dict[str, str] = {
        "antigravity": "打开 Antigravity 的 Agent Chat / Prompt 面板，并确保当前工作区就是目标项目。",
        "claude-code": "在项目目录启动 Claude Code 当前会话后，直接在同一会话里触发。",
        "cline": "在 VS Code 的 Cline 面板中，绑定当前项目后触发。",
        "codebuddy-cli": "在项目目录启动 CodeBuddy CLI 会话后触发。",
        "codebuddy": "打开 CodeBuddy IDE 的 Agent Chat，在项目上下文内触发。",
        "codex-cli": "在项目目录完成接入后，重启 codex，然后在新的 Codex 会话里触发。",
        "copilot-cli": "在项目目录启动 Copilot CLI 会话后触发。",
        "cursor-cli": "在项目目录启动 Cursor CLI 当前会话后触发。",
        "cursor": "打开 Cursor 的 Agent Chat，并确保当前工作区就是目标项目。",
        "windsurf": "打开 Windsurf 的 Agent Chat 或 Workflow 入口，在项目上下文内触发。",
        "gemini-cli": "在项目目录启动 Gemini CLI 会话后触发。",
        "kiro-cli": "在项目目录启动 Kiro CLI 会话后触发。",
        "opencode": "在项目目录启动 OpenCode 会话后触发。",
        "qoder-cli": "在项目目录启动 Qoder CLI 会话后触发。",
        "roo-code": "在 VS Code 的 Roo Code 聊天面板中触发。",
        "vscode-copilot": "在 VS Code Copilot Chat 绑定当前项目后触发。",
        "kilo-code": "在 VS Code 的 Kilo Code 聊天面板中触发。",
        "kiro": "打开 Kiro IDE 的 Agent Chat 或 AI 面板，在项目上下文内触发。",
        "qoder": "打开 Qoder IDE 的 Agent Chat，在当前项目内触发。",
        "trae": "打开 Trae Agent Chat，在当前项目上下文内直接触发。",
        "openclaw": "在 OpenClaw Agent 对话面板中，确保当前工作区为目标项目后触发。",
    }
    HOST_USAGE_NOTES: dict[str, list[str]] = {
        "antigravity": [
            "Antigravity 当前优先按 `GEMINI.md + .agent/workflows + /super-dev` 模式接入。",
            "项目内会写入 `GEMINI.md`、`.gemini/commands/super-dev.md` 与 `.agent/workflows/super-dev.md`。",
            "用户级会补充 `~/.gemini/GEMINI.md`、`~/.gemini/commands/super-dev.md` 与 `~/.gemini/skills/super-dev-core/SKILL.md`。",
            "接入后建议新开一个 Antigravity Chat，使 GEMINI 上下文、slash 与 Skill 一起生效。",
        ],
        "claude-code": [
            "推荐作为首选 CLI 宿主之一。",
            "接入后可先执行 super-dev doctor --host claude-code，确认根 `CLAUDE.md`、`.claude/skills/`、兼容 slash 与可选 plugin enhancement 一起生效。",
            "Claude Code 当前更接近 skills-first：项目根 `CLAUDE.md`、项目级 `.claude/skills/` 与用户级 `~/.claude/skills/` 是正式主面。",
            "`.claude/commands/` 与 `.claude/agents/` 仍保留为兼容增强面，不再作为唯一主接入面。",
            "仓库内还会额外生成可选的 repo plugin enhancement：`.claude-plugin/marketplace.json` + `plugins/super-dev-claude/.claude-plugin/plugin.json`。",
        ],
        "cline": [
            "Cline 优先使用 `.clinerules/` 规则目录，并补充项目级 `.cline/skills/` 让宿主在当前工作区内直接理解 Super Dev 协议。",
            "用户级 `~/.cline/skills/super-dev-core/SKILL.md` 会作为全局增强面一起安装。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，减少与内建 slash 的语义冲突。",
        ],
        "codebuddy-cli": [
            "在当前 CLI 会话中直接输入即可。",
            "如果会话早于接入动作启动，建议重开会话后再试。",
            "官方文档已公开 `CODEBUDDY.md`、`.codebuddy/commands/`、`.codebuddy/skills/` 与 `~/.codebuddy/CODEBUDDY.md` / `~/.codebuddy/skills/`。",
        ],
        "codebuddy": [
            "建议在项目级 Agent Chat 中使用，不要脱离项目上下文。",
            "先让宿主完成 research，再继续文档和编码。",
            "官方文档已公开 `CODEBUDDY.md`、`.codebuddy/rules/`、`.codebuddy/commands/`、`.codebuddy/agents/`、`.codebuddy/skills/` 与对应用户级目录。",
        ],
        "codex-cli": [
            "Codex 官方不走自定义项目 slash；桌面端请从 `/` 列表选择 `super-dev`，那是启用 Skill 的展示入口。",
            "实际依赖项目根 AGENTS.md、项目级 .agents/skills/super-dev/SKILL.md、全局 CODEX_HOME/AGENTS.md（默认 ~/.codex/AGENTS.md），以及官方用户级技能目录 ~/.agents/skills/super-dev/SKILL.md。",
            "仓库内还会额外生成 `.agents/plugins/marketplace.json` 与 `plugins/super-dev-codex/`，作为 Codex App/Desktop 的可选 repo plugin 增强层。",
            "保留 super-dev-core 作为兼容别名，避免旧安装和旧文档失效。",
            "如果旧会话没加载新 Skill，重启 codex 再试。",
        ],
        "copilot-cli": [
            "Copilot CLI 官方优先面是 `.github/copilot-instructions.md` 与 `.github/skills/` / `~/.copilot/skills/`。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，不走自定义 slash。",
            "如果宿主未加载项目规则，重启 copilot 会话再试。",
        ],
        "cursor-cli": [
            "适合终端内连续执行研究、文档和编码。",
            "若命令列表未刷新，可重开一次 Cursor CLI 会话。",
            "官方文档确认 Cursor CLI 会同时读取 `.cursor/rules/` 与项目根 `AGENTS.md` / `CLAUDE.md` 作为规则上下文。",
        ],
        "cursor": [
            "建议固定在同一个 Agent Chat 会话里完成整条流水线。",
            "如果项目规则没加载，先重新打开工作区或重新发起聊天。",
            "Cursor 官方规则面是 `.cursor/rules/`，并兼容读取项目根 `AGENTS.md` / `CLAUDE.md`。",
        ],
        "windsurf": [
            "当前按 IDE slash/workflow 模式适配。",
            "更适合在同一个 Workflow 里连续完成研究、三文档、确认门、Spec 与编码。",
            "官方文档已公开 .windsurf/skills 与 ~/.codeium/windsurf/skills。",
            "当前项目侧以 `.windsurf/rules/` + `.windsurf/workflows/` + `.windsurf/skills/` 为主接入面。",
        ],
        "gemini-cli": [
            "优先在同一会话中完成 research -> 三文档 -> 用户确认 -> Spec -> 前端运行验证 -> 后端/交付。",
            "若宿主支持联网，先让它完成同类产品研究。",
            "Gemini CLI 官方文档明确 `GEMINI.md` 与 `.gemini/commands/` 的项目级上下文与命令目录，用户级 `~/.gemini/commands/` 也会一并写入。",
        ],
        "kiro-cli": [
            "Kiro CLI 当前优先按 `.kiro/steering/super-dev.md` + `.kiro/skills/` / `~/.kiro/skills/` 适配，并通过 steering 的 inclusion 暴露 `/super-dev`。",
            "如果 steering 或 skills 未刷新，重新进入项目目录后重开 Kiro CLI 会话。",
            "官方文档已公开 `.kiro/steering/`、`.kiro/skills/`、`~/.kiro/steering/` 与 `~/.kiro/skills/`。",
        ],
        "opencode": [
            "按 CLI slash 模式使用。",
            "即使你也使用全局命令目录，仍建议保留项目级接入文件。",
            "官方文档已公开项目根 AGENTS.md、~/.config/opencode/AGENTS.md、.opencode/commands 与 skills 目录。",
        ],
        "qoder-cli": [
            "适合命令行流水线开发。",
            "若 slash 未生效，先确认 `AGENTS.md`、`.qoder/commands/super-dev.md` 已生成，并检查 `.qoder/rules/` 目录是否存在。",
            "官方文档已公开 `.qoder/skills/`、`~/.qoder/skills/`、项目根 `AGENTS.md` 与 `~/.qoder/AGENTS.md`。",
            "Qoder 官方规则目录是 `.qoder/rules/`，不要再依赖单文件 `.qoder/rules.md`。",
        ],
        "roo-code": [
            "Roo Code 支持项目级 `.roo/rules/` 与 `.roo/commands/`，建议与 `/super-dev` 命令一起使用。",
            "在同一会话连续完成 research、三文档确认、Spec 与开发实现。",
        ],
        "vscode-copilot": [
            "VS Code Copilot 建议使用 `.github/copilot-instructions.md` 固化流水线约束。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，确保与 Copilot Chat 一致。",
        ],
        "kilo-code": [
            "Kilo Code 优先使用 `.kilocode/rules/` 规则目录，确保项目约束在每次任务开始时自动注入。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，减少与内建 slash 的语义冲突。",
        ],
        "kiro": [
            "Kiro IDE 当前优先按 steering + skills 模式触发，并通过 steering 的 inclusion 暴露 `/super-dev`。",
            "如果 steering 或 Skill 未加载，先重开项目窗口或新开一个 Agent Chat。",
            "Kiro 官方已公开工作区 `.kiro/steering/`、`.kiro/skills/` 与全局 `~/.kiro/steering/`、`~/.kiro/skills/`。",
        ],
        "qoder": [
            "Qoder IDE 当前优先按项目级 commands + rules + 宿主级 Skill 模式触发，可直接使用 /super-dev。",
            "若新增命令未出现，重新打开项目或新开一个 Agent Chat。",
            "官方文档已公开 `.qoder/rules/`、`.qoder/commands/`、`.qoder/skills/`、项目根 `AGENTS.md` 与 `~/.qoder/AGENTS.md`。",
        ],
        "trae": [
            "不要输入 /super-dev。",
            "Trae 优先依赖项目级 `.trae/project_rules.md` 与用户级 `~/.trae/user_rules.md`；同时会兼容写入 `.trae/rules.md` 与 `~/.trae/rules.md`，用于命中当前已观测到的规则加载面。",
            "若检测到宿主级 ~/.trae/skills/super-dev-core/SKILL.md，则会额外增强。",
            "安装后建议新开一个 Trae Agent Chat，让新的规则与 Skill 一起生效。",
            "随后按 output/* 与 .super-dev/changes/*/tasks.md 推进开发。",
        ],
        "openclaw": [
            "OpenClaw 通过原生 Plugin SDK 集成，安装插件后 10 个专用 Tool 自动注册。",
            "项目内会写入 `.openclaw/rules/super-dev.md` 和 `.openclaw/commands/super-dev.md`。",
            "用户级 Skill 会安装到 `~/.openclaw/skills/super-dev-core/SKILL.md`。",
            "安装后建议重启 OpenClaw Gateway 或开启新会话，让 Plugin 和 Skill 一起生效。",
        ],
    }
    HOST_PRECONDITION_GUIDANCE: dict[str, list[str]] = {
        "codex-cli": [
            "Codex 接入后必须重启 `codex`，旧会话不会自动重新加载 AGENTS.md 与宿主级 Skill。",
            "触发前确认当前终端已经进入目标项目目录，并重新打开新的 Codex 会话。",
        ],
        "antigravity": [
            "Antigravity 接入后建议重新打开 Prompt / Agent Chat，让 GEMINI.md、workflows 与技能面一起加载。",
            "触发前确认当前工作区就是目标项目。",
        ],
        "trae": [
            "Trae 接入后建议完全关闭旧 Agent Chat，重新打开项目后再发起新会话。",
            "触发前确认当前 Agent Chat 绑定的是目标项目工作区。",
        ],
        "cursor": [
            "Cursor 需要在目标项目工作区的 Agent Chat 中触发，避免把规则加载到错误工作区。",
        ],
        "cursor-cli": [
            "Cursor CLI 触发前确认当前终端已进入目标项目目录。",
        ],
        "gemini-cli": [
            "Gemini CLI 触发前确认当前终端已进入目标项目目录，并让新的会话读取 `GEMINI.md`。",
        ],
        "kiro": [
            "Kiro IDE 接入后建议重新打开 Agent Chat，让 steering / skills 在新会话里生效。",
            "触发前确认当前工作区就是目标项目。",
        ],
        "kiro-cli": [
            "Kiro CLI 触发前确认当前终端已进入目标项目目录。",
        ],
        "qoder": [
            "Qoder IDE 触发前确认当前 Agent Chat 绑定的是目标项目；若新命令未出现，重新打开项目或新建会话。",
        ],
        "qoder-cli": [
            "Qoder CLI 触发前确认当前终端已进入目标项目目录。",
        ],
        "codebuddy": [
            "CodeBuddy IDE 触发前确认当前 Agent Chat 位于目标项目上下文。",
        ],
        "codebuddy-cli": [
            "CodeBuddy CLI 触发前确认当前终端已进入目标项目目录。",
        ],
        "copilot-cli": [
            "Copilot CLI 触发前确认当前终端已进入目标项目目录，并让新的会话读取 `.github/copilot-instructions.md`。",
        ],
        "windsurf": [
            "Windsurf 触发前确认当前 Agent Chat / Workflow 绑定的是目标项目工作区。",
        ],
        "opencode": [
            "OpenCode 触发前确认当前终端已进入目标项目目录。",
        ],
        "claude-code": [
            "Claude Code 触发前确认当前会话就是目标项目目录下的当前会话。",
        ],
        "cline": [
            "Cline 触发前确认当前聊天绑定的是目标工作区，并让 `.clinerules/` 已被重新加载。",
        ],
        "kilo-code": [
            "Kilo Code 触发前确认当前聊天绑定的是目标工作区，并让 `.kilocode/rules/` 已被重新加载。",
        ],
        "roo-code": [
            "Roo Code 触发前确认当前聊天位于目标项目工作区，并重新加载 `.roo/` 规则与命令。",
        ],
        "vscode-copilot": [
            "VS Code Copilot 触发前确认当前工作区就是目标项目，并让新的 Chat 会话读取项目级说明文件。",
        ],
        "openclaw": [
            "OpenClaw 触发前确认当前工作区就是目标项目，并确保 super-dev CLI 已安装在 PATH 中。",
        ],
    }

    TARGETS: dict[str, IntegrationTarget] = {
        "antigravity": IntegrationTarget(
            name="antigravity",
            description="Antigravity IDE 工作流 + Gemini 上下文注入",
            files=["GEMINI.md", ".agent/workflows/super-dev.md"],
        ),
        "claude-code": IntegrationTarget(
            name="claude-code",
            description="Claude Code CLI 深度集成",
            files=[
                "CLAUDE.md",
                ".claude/CLAUDE.md",
                ".claude/skills/super-dev/SKILL.md",
                ".claude/agents/super-dev-core.md",
                ".claude/commands/super-dev.md",
                ".claude-plugin/marketplace.json",
                "plugins/super-dev-claude/.claude-plugin/plugin.json",
                "plugins/super-dev-claude/README.md",
                "plugins/super-dev-claude/skills/super-dev/SKILL.md",
                "plugins/super-dev-claude/skills/super-dev-core/SKILL.md",
                "plugins/super-dev-claude/agents/super-dev-core.md",
            ],
            optional_files=[
                ".claude/CLAUDE.md",
                ".claude/commands/super-dev.md",
                ".claude/agents/super-dev-core.md",
                ".claude-plugin/marketplace.json",
                "plugins/super-dev-claude/.claude-plugin/plugin.json",
                "plugins/super-dev-claude/README.md",
                "plugins/super-dev-claude/skills/super-dev/SKILL.md",
                "plugins/super-dev-claude/skills/super-dev-core/SKILL.md",
                "plugins/super-dev-claude/agents/super-dev-core.md",
            ],
        ),
        "cline": IntegrationTarget(
            name="cline",
            description="Cline IDE 规则注入",
            files=[".clinerules/super-dev.md", ".cline/skills/super-dev-core/SKILL.md"],
        ),
        "codebuddy-cli": IntegrationTarget(
            name="codebuddy-cli",
            description="CodeBuddy CLI 项目规则注入",
            files=["CODEBUDDY.md", ".codebuddy/skills/super-dev-core/SKILL.md"],
        ),
        "codebuddy": IntegrationTarget(
            name="codebuddy",
            description="CodeBuddy IDE rules + agent protocol 注入",
            files=[
                "CODEBUDDY.md",
                ".codebuddy/rules/super-dev/RULE.mdc",
                ".codebuddy/agents/super-dev-core.md",
                ".codebuddy/skills/super-dev-core/SKILL.md",
            ],
        ),
        "codex-cli": IntegrationTarget(
            name="codex-cli",
            description="Codex 项目上下文注入",
            files=[
                "AGENTS.md",
                ".agents/skills/super-dev/SKILL.md",
                ".agents/plugins/marketplace.json",
                "plugins/super-dev-codex/.codex-plugin/plugin.json",
                "plugins/super-dev-codex/README.md",
                "plugins/super-dev-codex/skills/super-dev/SKILL.md",
                "plugins/super-dev-codex/skills/super-dev-core/SKILL.md",
            ],
            optional_files=[
                ".agents/plugins/marketplace.json",
                "plugins/super-dev-codex/.codex-plugin/plugin.json",
                "plugins/super-dev-codex/README.md",
                "plugins/super-dev-codex/skills/super-dev/SKILL.md",
                "plugins/super-dev-codex/skills/super-dev-core/SKILL.md",
            ],
        ),
        "copilot-cli": IntegrationTarget(
            name="copilot-cli",
            description="GitHub Copilot CLI 指令注入",
            files=[".github/copilot-instructions.md", ".github/skills/super-dev-core/SKILL.md"],
        ),
        "cursor-cli": IntegrationTarget(
            name="cursor-cli",
            description="Cursor CLI 项目规则注入",
            files=[".cursor/rules/super-dev.mdc"],
        ),
        "windsurf": IntegrationTarget(
            name="windsurf",
            description="Windsurf IDE 规则注入",
            files=[".windsurf/rules/super-dev.md", ".windsurf/skills/super-dev-core/SKILL.md"],
        ),
        "gemini-cli": IntegrationTarget(
            name="gemini-cli",
            description="Gemini CLI 项目规则注入",
            files=["GEMINI.md"],
        ),
        "kilo-code": IntegrationTarget(
            name="kilo-code",
            description="Kilo Code 规则注入",
            files=[".kilocode/rules/super-dev.md"],
        ),
        "kiro-cli": IntegrationTarget(
            name="kiro-cli",
            description="Kiro CLI 项目规则注入",
            files=[".kiro/steering/super-dev.md", ".kiro/skills/super-dev-core/SKILL.md"],
        ),
        "qoder-cli": IntegrationTarget(
            name="qoder-cli",
            description="Qoder CLI 项目规则注入",
            files=["AGENTS.md", ".qoder/rules/super-dev.md", ".qoder/skills/super-dev-core/SKILL.md"],
        ),
        "roo-code": IntegrationTarget(
            name="roo-code",
            description="Roo Code 规则 + 命令注入",
            files=[".roo/rules/super-dev.md"],
        ),
        "vscode-copilot": IntegrationTarget(
            name="vscode-copilot",
            description="GitHub Copilot 仓库级指令注入",
            files=[".github/copilot-instructions.md"],
        ),
        "opencode": IntegrationTarget(
            name="opencode",
            description="OpenCode 项目规则注入",
            files=["AGENTS.md", ".opencode/skills/super-dev-core/SKILL.md"],
        ),
        "cursor": IntegrationTarget(
            name="cursor",
            description="Cursor IDE 规则注入",
            files=[".cursor/rules/super-dev.mdc"],
        ),
        "kiro": IntegrationTarget(
            name="kiro",
            description="Kiro IDE 项目规则注入",
            files=[".kiro/steering/super-dev.md", ".kiro/skills/super-dev-core/SKILL.md"],
        ),
        "qoder": IntegrationTarget(
            name="qoder",
            description="Qoder IDE 规则 + 命令注入",
            files=["AGENTS.md", ".qoder/rules/super-dev.md", ".qoder/skills/super-dev-core/SKILL.md"],
        ),
        "trae": IntegrationTarget(
            name="trae",
            description="Trae IDE 项目规则 + 宿主 Skill 注入",
            files=[".trae/project_rules.md", ".trae/rules.md"],
        ),
        "openclaw": IntegrationTarget(
            name="openclaw",
            description="OpenClaw Agent 平台原生插件集成",
            files=[".openclaw/rules/super-dev.md"],
        ),
    }
    SLASH_COMMAND_FILES: dict[str, str] = {
        "antigravity": ".gemini/commands/super-dev.md",
        "claude-code": ".claude/commands/super-dev.md",
        "codebuddy-cli": ".codebuddy/commands/super-dev.md",
        "codebuddy": ".codebuddy/commands/super-dev.md",
        "cursor-cli": ".cursor/commands/super-dev.md",
        "windsurf": ".windsurf/workflows/super-dev.md",
        "gemini-cli": ".gemini/commands/super-dev.md",
        "kiro-cli": ".kiro/steering/super-dev.md",
        "kiro": ".kiro/steering/super-dev.md",
        "opencode": ".opencode/commands/super-dev.md",
        "qoder-cli": ".qoder/commands/super-dev.md",
        "qoder": ".qoder/commands/super-dev.md",
        "roo-code": ".roo/commands/super-dev.md",
        "cursor": ".cursor/commands/super-dev.md",
        "openclaw": ".openclaw/commands/super-dev.md",
    }
    GLOBAL_SLASH_COMMAND_FILES: dict[str, str] = {
        "antigravity": ".gemini/commands/super-dev.md",
        "claude-code": ".claude/commands/super-dev.md",
        "opencode": ".config/opencode/commands/super-dev.md",
    }
    NO_SLASH_TARGETS: set[str] = {
        "cline",
        "codex-cli",
        "copilot-cli",
        "kilo-code",
        "trae",
        "vscode-copilot",
    }
    OFFICIAL_DOCS_INDEX: dict[str, tuple[str, ...]] = {
        "antigravity": ("https://antigravity.im/documentation",),
        "claude-code": (
            "https://docs.anthropic.com/en/docs/claude-code/slash-commands",
            "https://docs.anthropic.com/en/docs/claude-code/hooks",
            "https://docs.anthropic.com/en/docs/claude-code/sdk",
            "https://docs.anthropic.com/en/docs/claude-code/settings#claude-md-memory",
        ),
        "cline": ("https://docs.cline.bot/customization/cline-rules",),
        "codebuddy-cli": (
            "https://www.codebuddy.ai/docs/cli/slash-commands",
            "https://www.codebuddy.ai/docs/cli/skills",
            "https://www.codebuddy.ai/docs/cli/plugins",
        ),
        "codebuddy": (
            "https://www.codebuddy.ai/docs/cli/ide-integrations",
            "https://www.codebuddy.ai/docs/zh/ide/User-guide/Rules",
            "https://www.codebuddy.ai/docs/ide/Features/Subagents",
            "https://www.codebuddy.ai/docs/zh/ide/Features/Skills",
        ),
        "codex-cli": (
            "https://developers.openai.com/codex/cli",
            "https://developers.openai.com/codex/guides/agents-md",
            "https://developers.openai.com/codex/skills",
            "https://developers.openai.com/codex/app/commands",
        ),
        "copilot-cli": (
            "https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions",
            "https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills",
            "https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli",
        ),
        "cursor-cli": (
            "https://docs.cursor.com/en/cli/using",
            "https://docs.cursor.com/en/cli/overview",
            "https://docs.cursor.com/en/cli/reference/slash-commands",
        ),
        "windsurf": (
            "https://docs.windsurf.com/plugins/cascade/workflows",
            "https://docs.windsurf.com/windsurf/cascade/memories#custom-skills",
            "https://docs.windsurf.com/windsurf/cascade/memories",
        ),
        "gemini-cli": (
            "https://google-gemini.github.io/gemini-cli/docs/",
            "https://google-gemini.github.io/gemini-cli/docs/cli/configuration.html",
            "https://google-gemini.github.io/gemini-cli/docs/cli/commands.html",
        ),
        "kilo-code": ("https://kilocode.ai/docs/features/rules",),
        "kiro-cli": (
            "https://kiro.dev/docs/cli/",
            "https://kiro.dev/docs/cli/skills/",
            "https://kiro.dev/docs/steering/",
            "https://kiro.dev/changelog/powers-auto-summarization-and-slash-commands",
        ),
        "opencode": (
            "https://opencode.ai/docs/rules/",
            "https://opencode.ai/docs/commands/",
            "https://opencode.ai/docs/skills/",
            "https://opencode.ai/docs/agents/",
        ),
        "qoder-cli": (
            "https://docs.qoder.com/cli/using-cli",
            "https://docs.qoder.com/zh/user-guide/rules",
            "https://docs.qoder.com/user-guide/commands",
            "https://docs.qoder.com/cli/skills",
        ),
        "roo-code": (
            "https://docs.roocode.com/features/slash-commands",
            "https://docs.roocode.com/features/custom-instructions",
            "https://docs.roocode.com/features/custom-modes",
        ),
        "vscode-copilot": (
            "https://docs.github.com/en/copilot/how-tos/copilot-chat/customize-copilot/add-repository-instructions",
            "https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot",
        ),
        "cursor": (
            "https://docs.cursor.com/en/agent/chat/commands",
            "https://docs.cursor.com/en/context/rules",
        ),
        "kiro": (
            "https://kiro.dev/docs/steering/",
            "https://kiro.dev/docs/cli/skills/",
        ),
        "qoder": (
            "https://docs.qoder.com/zh/user-guide/rules",
            "https://docs.qoder.com/user-guide/commands",
            "https://docs.qoder.com/user-guide/skills",
        ),
        "trae": ("https://docs.trae.ai/docs/what-is-trae-rules",),
        "openclaw": (
            "https://docs.openclaw.ai/plugins/building-plugins",
            "https://docs.openclaw.ai/tools/skills",
        ),
    }
    OFFICIAL_DOCS: dict[str, str] = {
        key: (values[0] if values else "") for key, values in OFFICIAL_DOCS_INDEX.items()
    }
    DOCS_VERIFIED_TARGETS: set[str] = {
        key for key, values in OFFICIAL_DOCS_INDEX.items() if bool(values)
    }
    HOST_CERTIFICATIONS: dict[str, dict[str, object]] = {
        "antigravity": {
            "level": "experimental",
            "reason": "Antigravity 当前按 GEMINI 上下文、项目 workflows 与 slash 组合面接入，本机已验证安装面，但还缺更完整的官方定制文档证据。",
            "evidence": [
                "本机已存在 ~/.gemini/GEMINI.md、~/.gemini/commands、~/.gemini/skills 与 Antigravity 独立应用目录",
                "项目历史与本机会话中已出现 .agent/workflows 作为 Antigravity 工作流面",
                "Super Dev 已按项目 GEMINI.md + .agent/workflows + 用户级 ~/.gemini 面完成接入",
            ],
        },
        "claude-code": {
            "level": "certified",
            "reason": "已收敛到 Claude Code 的新主模型：项目根 CLAUDE.md + project/user skills，并叠加兼容 commands/agents 与 repo plugin enhancement。",
            "evidence": [
                "泄露代码确认 `.claude/skills` 为一等面，`/commands` 已被当作 legacy surface 兼容加载",
                "泄露代码的 onboarding 明确检查项目根 `CLAUDE.md`，而不是只看 `.claude/CLAUDE.md`",
                "Super Dev 已补齐 `CLAUDE.md + .claude/skills + ~/.claude/skills + optional repo plugin enhancement`",
            ],
        },
        "codex-cli": {
            "level": "certified",
            "reason": "已按 Codex 的真实能力改成 AGENTS.md + Skills 主面，并增加 repo plugin enhancement，不再误判为项目 slash 宿主。",
            "evidence": [
                "官方文档明确仓库与用户级 skills 目录为 .agents/skills 与 ~/.agents/skills",
                "官方文档明确 repo / personal marketplace 与 .codex-plugin/plugin.json 的插件结构",
                "Super Dev 已为 Codex 修正成 AGENTS.md + 官方 Skills 接入路径，并补充 repo plugin enhancement",
                "接入后需要重启的行为已被显式建模与测试覆盖",
            ],
        },
        "trae": {
            "level": "compatible",
            "reason": "Trae 官方公开面当前可确认的是项目 rules 与用户 rules；同时本机已观测到 `.trae/rules.md` / `~/.trae/rules.md` 的兼容规则面，skills 仍按增强处理，因此当前保持稳定兼容而非认证级。",
            "evidence": [
                "公开文档确认 Trae project rules 与 user rules 机制",
                "本机已存在 ~/.trae/rules.md，可作为兼容规则面协同生效",
                "本机若存在 ~/.trae/skills，可作为兼容增强路径协同生效",
                "Super Dev 已同时建模项目 rules、用户 rules、兼容 rules 面与可选宿主级 Skill 增强",
            ],
        },
        "codebuddy-cli": {
            "level": "compatible",
            "reason": "官方文档已经转向 CODEBUDDY.md + commands + skills 模型，当前接入已对齐，但仍缺少长期真机回归矩阵。",
            "evidence": [
                "官方文档公开 CODEBUDDY.md、CLI slash commands 与 skills",
                "Super Dev 已改为写入 CODEBUDDY.md + commands + skills，并保留 AGENTS.md compatibility 观察面",
            ],
        },
        "cursor-cli": {
            "level": "compatible",
            "reason": "官方 CLI slash 文档明确，当前接入链路完整，但仍需更多运行级认证样本。",
            "evidence": [
                "官方文档公开 CLI slash commands 与 `.cursor/rules/` / `AGENTS.md` 上下文",
                "Super Dev 已提供 rules + slash command，并保留 AGENTS compatibility 说明",
            ],
        },
        "gemini-cli": {
            "level": "compatible",
            "reason": "CLI 规则与 slash 接入完整，文档可验证，但还未提升到认证级真机矩阵。",
            "evidence": [
                "官方文档公开 commands 与 GEMINI.md 上下文文件",
                "Super Dev 已提供项目级 GEMINI.md、命令映射与兼容 Skill 增强",
            ],
        },
        "kiro-cli": {
            "level": "compatible",
            "reason": "已按 Kiro 官方 steering + skills 机制接入，并把 steering slash entry 纳入正式模型，不再误建模成纯文本触发宿主。",
            "evidence": [
                "官方文档公开 Kiro CLI、steering 与 skills 目录，以及 steering inclusion 的 slash 入口",
                "Super Dev 已改为 `.kiro/steering/` + `.kiro/skills/` + `~/.kiro/steering/` + `~/.kiro/skills/` 接入",
            ],
        },
        "qoder-cli": {
            "level": "compatible",
            "reason": "Qoder CLI 已按官方 `.qoder/rules/`、commands、skills 与 AGENTS memory 接入，不再依赖旧的单文件规则面。",
            "evidence": [
                "官方文档公开 `.qoder/rules/`、commands、skills 与项目/用户 AGENTS.md memory",
                "Super Dev 已改为规则目录 + slash command + skills + AGENTS memory 接入",
            ],
        },
        "codebuddy": {
            "level": "experimental",
            "reason": "IDE 侧已对齐官方 CODEBUDDY.md + rules + commands + agents + skills，但 Agent Chat 的项目级行为仍缺少持续真机验证。",
            "evidence": [
                "官方文档公开 IDE rules、commands、subagents 与 skills",
                "Super Dev 已写入 CODEBUDDY.md、rules、commands、agents 与 skills 接入面",
            ],
        },
        "copilot-cli": {
            "level": "compatible",
            "reason": "Copilot CLI 已按官方 copilot-instructions + skills 面建模，文本触发稳定，但自定义 agent 的长期真机回归仍不足。",
            "evidence": [
                "官方文档公开 copilot-instructions.md、.github/skills 与 ~/.copilot/skills",
                "官方文档公开 Copilot CLI custom agents 目录 .github/agents 与 ~/.copilot/agents",
                "Super Dev 已写入 .github/copilot-instructions.md 与 .github/skills/super-dev-core/SKILL.md",
            ],
        },
        "cursor": {
            "level": "experimental",
            "reason": "IDE Agent Chat 能力可映射，但项目级 slash 行为仍需持续运行级验证。",
            "evidence": [
                "官方文档公开 Agent commands 与 rules 上下文",
                "Super Dev 已写入 `.cursor/rules/`、命令映射与兼容 Skill",
            ],
        },
        "windsurf": {
            "level": "experimental",
            "reason": "当前依赖 workflow/rules 适配，交互模式可用但还未达到认证级稳定性。",
            "evidence": [
                "官方文档公开 workflows 与 custom skills",
                "Super Dev 已写入 `.windsurf/rules/`、`.windsurf/workflows/` 与 skills",
            ],
        },
        "opencode": {
            "level": "experimental",
            "reason": "官方 rules / commands / skills 路径已适配，但仍需要更强的运行级认证覆盖。",
            "evidence": [
                "官方文档公开项目根 AGENTS.md、~/.config/opencode/AGENTS.md、commands、skills 与 agents",
                "Super Dev 已写入官方 rules、Skill 与项目/全局命令文件",
            ],
        },
        "kilo-code": {
            "level": "experimental",
            "reason": "Kilo Code 按 .kilocode/rules/ 规则目录适配，与 Roo Code 生态类似，但仍需更多真机验证。",
            "evidence": [
                "Kilo Code 支持项目级 .kilocode/rules/ 规则目录",
                "Super Dev 已写入规则文件",
            ],
        },
        "kiro": {
            "level": "experimental",
            "reason": "IDE 侧已按官方 steering + skills + steering slash entry 对齐，但仍需更多真机回归样本验证 Agent Chat 行为。",
            "evidence": [
                "官方文档公开 steering、skills 与 steering inclusion 的 slash 入口",
                "Super Dev 已改为 `.kiro/steering/` + `.kiro/skills/` + `~/.kiro/steering/` + `~/.kiro/skills/` 接入",
            ],
        },
        "qoder": {
            "level": "experimental",
            "reason": "官方文档已明确 `.qoder/rules/`、commands、skills 与 AGENTS memory，当前已切到目录化规则面，但仍需要更多真机样本。",
            "evidence": [
                "官方文档公开 `.qoder/rules/` 目录、commands、skills 与项目/用户 AGENTS.md memory",
                "Super Dev 已改为 `.qoder/rules/super-dev.md` + `.qoder/commands/super-dev.md` + `.qoder/skills/` + `AGENTS.md`",
            ],
        },
        "openclaw": {
            "level": "compatible",
            "reason": "OpenClaw 原生插件 SDK 支持 Tool 注册与 Skill 系统，通过 plugin 内嵌 SKILL.md + CLI subprocess 桥接完成接入。",
            "evidence": [
                "OpenClaw Plugin SDK 提供 definePluginEntry / registerTool / configSchema 机制",
                "Super Dev 通过 CLI subprocess 桥接保证功能完整性",
                "插件内嵌 SKILL.md 提供完整流水线行为指令",
                "官方文档公开 Plugin 与 Skills 开发指南",
            ],
        },
    }
    CERTIFICATION_LABELS: dict[str, str] = {
        "certified": "Certified",
        "compatible": "Compatible",
        "experimental": "Experimental",
    }
    TEXT_TRIGGER_PREFIXES: tuple[str, str] = (TEXT_TRIGGER_PREFIX, TEXT_TRIGGER_PREFIX_FULLWIDTH)
    CONTRACT_TRIGGER_GROUPS: dict[str, tuple[str, ...]] = {
        "slash": ("/super-dev",),
        "text": TEXT_TRIGGER_PREFIXES,
    }
    CONTRACT_DOC_GROUP: tuple[str, ...] = (
        "output/*-research.md",
        "output/*-prd.md",
        "output/*-architecture.md",
        "output/*-uiux.md",
        "three core documents",
        "three core docs",
        "三份核心文档",
        "PRD, architecture, and UIUX",
        "PRD / Architecture / UIUX",
        "PRD / 架构 / UIUX",
        "Draft PRD, architecture, and UIUX",
    )
    CONTRACT_CONFIRMATION_GROUP: tuple[str, ...] = (
        "wait for explicit confirmation",
        "wait for approval",
        "wait for user confirmation",
        "for user confirmation",
        "Stop for user confirmation",
        "Create Spec/tasks only after confirmation",
        "先向用户汇报文档摘要与路径，等待明确确认",
        "等待确认",
        "用户未确认前禁止创建 Spec",
        "未经确认不得创建 Spec",
        "暂停等待用户确认",
        "等待用户确认",
        "stop after the three core documents",
    )
    CONTRACT_ARTIFACT_GROUP: tuple[str, ...] = (
        "workspace files",
        "project files",
        "repository workspace",
        "project workspace",
        "项目文件",
        "真实写入项目文件",
        "chat-only summaries do not count",
        "只在聊天里总结不算完成",
        "instead of only replying in chat",
    )
    CONTRACT_FLOW_GROUP: tuple[str, ...] = (
        "SUPER_DEV_FLOW_CONTRACT_V1",
        "PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery",
        "DOC_CONFIRM_GATE: required",
        "PREVIEW_CONFIRM_GATE: required",
        "HOST_PARITY: required",
    )

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        self.templates_dir = self.project_dir / "templates"

    def _flow_contract_markdown_block(self) -> str:
        return (
            "## Super Dev System Flow Contract\n"
            "- SUPER_DEV_FLOW_CONTRACT_V1\n"
            "- PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery\n"
            "- DOC_CONFIRM_GATE: required\n"
            "- PREVIEW_CONFIRM_GATE: required\n"
            "- HOST_PARITY: required\n"
        )

    def _flow_contract_toml_block(self) -> str:
        return (
            "# SUPER_DEV_FLOW_CONTRACT_V1\n"
            "# PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery\n"
            "# DOC_CONFIRM_GATE: required\n"
            "# PREVIEW_CONFIRM_GATE: required\n"
            "# HOST_PARITY: required\n"
        )

    def _append_flow_contract(self, *, content: str, relative: str) -> str:
        normalized = content or ""
        if "SUPER_DEV_FLOW_CONTRACT_V1" in normalized:
            return normalized
        if str(relative).endswith(".toml"):
            return f"{normalized.rstrip()}\n\n{self._flow_contract_toml_block()}"
        return f"{normalized.rstrip()}\n\n{self._flow_contract_markdown_block()}"

    def _first_response_contract_zh(self) -> str:
        return (
            "## 首轮响应契约（首次触发必须执行）\n"
            "- 当用户通过宿主支持的 Super Dev 入口触发（例如 `/super-dev ...`、`$super-dev`、`super-dev: ...` 或 `super-dev：...`）后，第一轮回复必须明确：已进入 Super Dev 流水线，而不是普通聊天。\n"
            "- 如果仓库里已经存在 `super-dev.yaml`、`.super-dev/WORKFLOW.md`、`output/*`、`.super-dev/review-state/*` 或未完成的 run state，新会话里的第一次自然语言需求也必须默认继续 Super Dev 流程，而不是退回普通聊天。\n"
            "- 第一轮回复前，优先读取 `.super-dev/WORKFLOW.md` 与 `output/*-bootstrap.md`（若存在），把其中的初始化契约视为当前仓库的显式 bootstrap 规则。\n"
            "- 第一轮回复必须明确当前阶段是 `research`，会先读取 `knowledge/` 与 `output/knowledge-cache/*-knowledge-bundle.json`（若存在），再用宿主原生联网研究同类产品。\n"
            "- 第一轮回复必须明确后续顺序：research -> 三份核心文档 -> 等待用户确认 -> Spec / tasks -> 前端优先并运行验证 -> 后端 / 测试 / 交付。\n"
            "- 第一轮回复必须明确承诺：三份核心文档完成后会暂停并等待用户确认；未经确认不会创建 Spec，也不会开始编码。\n\n"
        )

    def _first_response_contract_en(self) -> str:
        return (
            "## First-Response Contract\n"
            "- On the first reply after a host-supported Super Dev entry (for example `/super-dev ...`, `$super-dev`, `super-dev: ...`, or `super-dev：...`), explicitly state that Super Dev pipeline mode is now active rather than normal chat mode.\n"
            "- If the repository already contains `super-dev.yaml`, `.super-dev/WORKFLOW.md`, `output/*`, `.super-dev/review-state/*`, or an unfinished run state, the first natural-language requirement in a new host session must also default to continuing Super Dev rather than plain chat.\n"
            "- Before the first reply, read `.super-dev/WORKFLOW.md` and `output/*-bootstrap.md` when present, and treat them as the explicit bootstrap contract for this repository.\n"
            "- The first reply must explicitly state that the current phase is `research`, and that you will read `knowledge/` plus `output/knowledge-cache/*-knowledge-bundle.json` first when available before similar-product research.\n"
            "- The first reply must explicitly state the next sequence: research -> three core documents -> wait for user confirmation -> Spec / tasks -> frontend first with runtime verification -> backend / tests / delivery.\n"
            "- The first reply must explicitly promise that you will stop after the three core documents and wait for approval before creating Spec or writing code.\n\n"
        )

    @classmethod
    def coverage_gaps(cls) -> dict[str, list[str]]:
        declared = set(HOST_TOOL_IDS)
        target_keys = set(cls.TARGETS)
        slash_keys = set(cls.SLASH_COMMAND_FILES)
        slash_required = declared - cls.NO_SLASH_TARGETS
        docs_keys = set(cls.OFFICIAL_DOCS)
        verified_keys = set(cls.DOCS_VERIFIED_TARGETS)
        declared_with_docs = {item for item, value in cls.OFFICIAL_DOCS.items() if bool(value)}
        return {
            "missing_in_targets": sorted(declared - target_keys),
            "extra_in_targets": sorted(target_keys - declared),
            "missing_in_slash": sorted(slash_required - slash_keys),
            "extra_in_slash": sorted(slash_keys - slash_required),
            "missing_in_docs_map": sorted(declared - docs_keys),
            "extra_in_docs_map": sorted(docs_keys - declared),
            "missing_official_docs_url": sorted(declared - declared_with_docs),
            "unverified_docs": sorted(declared - verified_keys),
        }

    def list_targets(self) -> list[IntegrationTarget]:
        return list(self.TARGETS.values())

    @classmethod
    def required_integration_files(cls, target: str) -> list[str]:
        target_info = cls.TARGETS.get(target)
        if target_info is None:
            return []
        optional = set(target_info.optional_files)
        return [item for item in target_info.files if item not in optional]

    @classmethod
    def optional_integration_files(cls, target: str) -> list[str]:
        target_info = cls.TARGETS.get(target)
        if target_info is None:
            return []
        return list(target_info.optional_files)

    def get_adapter_profile(self, target: str) -> HostAdapterProfile:
        from ..catalogs import HOST_COMMAND_CANDIDATES, host_path_candidates
        from ..skills import SkillManager

        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        category = HOST_TOOL_CATEGORY_MAP.get(target, "ide")
        integration_files = list(self.required_integration_files(target))
        slash_file = self.SLASH_COMMAND_FILES.get(target, "") if self.supports_slash(target) else ""
        skill_dir = SkillManager.TARGET_PATHS.get(target, "") if self.requires_skill(target) else ""
        docs_references = self._official_docs_references(target)
        docs_url = docs_references[0] if docs_references else ""
        docs_verified = bool(docs_references)
        adapter_mode = self._adapter_mode(
            target=target, category=category, integration_files=integration_files
        )
        usage = self._usage_profile(target=target, category=category)
        certification = self._certification_profile(target)
        smoke = self._smoke_profile(target=target, category=category)
        preconditions = self._precondition_profile(target=target)
        surfaces = self._install_surfaces(target=target)
        protocol = self._protocol_profile(target=target)
        capability_labels = self._capability_labels(target=target)

        return HostAdapterProfile(
            host=target,
            category=category,
            adapter_mode=adapter_mode,
            host_model_provider="host",
            certification_level=certification["level"],
            certification_label=certification["label"],
            certification_reason=certification["reason"],
            certification_evidence=list(certification["evidence"]),
            official_docs_url=docs_url,
            docs_verified=docs_verified,
            primary_entry=usage["primary_entry"],
            terminal_entry='super-dev "<需求描述>"',
            terminal_entry_scope="仅触发本地编排，不直接调用宿主模型会话",
            integration_files=integration_files,
            slash_command_file=slash_file,
            skill_dir=skill_dir,
            detection_commands=list(HOST_COMMAND_CANDIDATES.get(target, [])),
            detection_paths=list(host_path_candidates(target)),
            notes=usage["notes"],
            usage_mode=usage["usage_mode"],
            trigger_command=usage["trigger_command"],
            entry_variants=list(usage.get("entry_variants", [])),
            trigger_context=usage["trigger_context"],
            usage_location=usage["usage_location"],
            requires_restart_after_onboard=usage["requires_restart_after_onboard"],
            post_onboard_steps=list(usage["post_onboard_steps"]),
            usage_notes=list(usage["usage_notes"]),
            smoke_test_prompt=str(smoke["smoke_test_prompt"]),
            smoke_test_steps=list(smoke["smoke_test_steps"]),
            smoke_success_signal=str(smoke["smoke_success_signal"]),
            precondition_status=str(preconditions["status"]),
            precondition_label=str(preconditions["label"]),
            precondition_guidance=list(preconditions["guidance"]),
            precondition_signals=dict(preconditions["signals"]),
            precondition_items=list(preconditions["items"]),
            host_protocol_mode=str(protocol["mode"]),
            host_protocol_summary=str(protocol["summary"]),
            official_project_surfaces=list(surfaces["official_project_surfaces"]),
            official_user_surfaces=list(surfaces["official_user_surfaces"]),
            optional_project_surfaces=list(surfaces["optional_project_surfaces"]),
            optional_user_surfaces=list(surfaces["optional_user_surfaces"]),
            observed_compatibility_surfaces=list(surfaces["observed_compatibility_surfaces"]),
            official_docs_references=docs_references,
            docs_check_status="declared" if docs_references else "missing",
            docs_check_summary=(
                f"declared {len(docs_references)} refs"
                if docs_references
                else "no official docs references"
            ),
            capability_labels=capability_labels,
        )

    def _certification_profile(self, target: str) -> dict[str, object]:
        raw = self.HOST_CERTIFICATIONS.get(target, {})
        level = str(raw.get("level", "experimental")).strip().lower()
        if level not in self.CERTIFICATION_LABELS:
            level = "experimental"
        evidence = raw.get("evidence", [])
        normalized_evidence = [
            item.strip() for item in evidence if isinstance(item, str) and item.strip()
        ]
        return {
            "level": level,
            "label": self.CERTIFICATION_LABELS[level],
            "reason": str(raw.get("reason", "")).strip(),
            "evidence": normalized_evidence,
        }

    def list_adapter_profiles(self, targets: list[str] | None = None) -> list[HostAdapterProfile]:
        selected = targets or sorted(self.TARGETS.keys())
        return [self.get_adapter_profile(target) for target in selected]

    def host_hardening_blueprint(self, target: str) -> dict[str, object]:
        profile = self.get_adapter_profile(target)
        trigger_mode = "slash" if self.supports_slash(target) else "text"
        required_steps = [
            "setup project integration files",
            "inject system flow contract markers",
            "audit surface contract markers",
            "generate host usage profile",
        ]
        if self.supports_slash(target):
            required_steps.append("setup project slash command")
            required_steps.append("setup user-level slash command")
        if self.requires_skill(target):
            required_steps.append("install skill to host skill directory")
        protocol_mode = str(profile.host_protocol_mode or "")
        if protocol_mode:
            required_steps.append(f"apply host protocol mode: {protocol_mode}")
        return {
            "host": target,
            "trigger_mode": trigger_mode,
            "final_trigger": profile.trigger_command,
            "required_steps": required_steps,
            "required_project_surfaces": list(profile.official_project_surfaces),
            "required_user_surfaces": list(profile.official_user_surfaces),
            "optional_project_surfaces": list(profile.optional_project_surfaces),
            "optional_user_surfaces": list(profile.optional_user_surfaces),
        }

    def _official_docs_references(self, target: str) -> list[str]:
        references = list(self.OFFICIAL_DOCS_INDEX.get(target, ()))
        return [item.strip() for item in references if isinstance(item, str) and item.strip()]

    def _capability_labels(self, *, target: str) -> dict[str, str]:
        slash_label = "native" if self.supports_slash(target) else "none"
        if target == "codex-cli":
            slash_label = "skill-list"
        protocol = self._protocol_profile(target=target)
        mode = str(protocol.get("mode", "")).strip().lower()
        if mode in {"official-context", "official-steering"}:
            rules_label = "official"
        elif mode.startswith("official"):
            rules_label = "official"
        else:
            rules_label = "compat"
        if self.requires_skill(target):
            compatibility_skill_targets = {"cursor-cli", "cursor", "gemini-cli", "trae"}
            skill_label = "compat" if target in compatibility_skill_targets else "official"
        else:
            skill_label = "none"
        trigger_label = "slash" if self.supports_slash(target) else "text"
        return {
            "slash": slash_label,
            "rules": rules_label,
            "skills": skill_label,
            "trigger": trigger_label,
        }

    def verify_official_docs(
        self, target: str, *, timeout_seconds: float = 5.0
    ) -> dict[str, object]:
        references = self._official_docs_references(target)
        if not references:
            return {
                "target": target,
                "status": "missing",
                "checked": 0,
                "reachable": 0,
                "unreachable": 0,
                "details": [],
            }
        details: list[dict[str, object]] = []
        reachable = 0
        for url in references:
            probe = self._probe_official_url(url=url, timeout_seconds=timeout_seconds)
            ok = bool(probe.get("reachable", False))
            code = probe.get("status_code")
            reason = str(probe.get("error", ""))
            if ok:
                reachable += 1
            details.append(
                {
                    "url": url,
                    "reachable": ok,
                    "status_code": code,
                    "error": reason,
                    "method": str(probe.get("method", "")),
                    "tls_mode": str(probe.get("tls_mode", "")),
                }
            )
        checked = len(details)
        status = "verified" if reachable == checked else ("partial" if reachable > 0 else "failed")
        return {
            "target": target,
            "status": status,
            "checked": checked,
            "reachable": reachable,
            "unreachable": checked - reachable,
            "details": details,
        }

    def _fetch_official_doc_excerpt(
        self,
        url: str,
        *,
        timeout_seconds: float = 5.0,
        max_bytes: int = 120000,
    ) -> dict[str, object]:
        probe = self._probe_official_url(
            url=url,
            timeout_seconds=timeout_seconds,
            read_content=True,
            max_bytes=max_bytes,
        )
        return {
            "url": url,
            "reachable": bool(probe.get("reachable", False)),
            "status_code": probe.get("status_code"),
            "error": str(probe.get("error", "")),
            "content": str(probe.get("content", "")),
            "method": str(probe.get("method", "")),
            "tls_mode": str(probe.get("tls_mode", "")),
        }

    def _probe_official_url(
        self,
        *,
        url: str,
        timeout_seconds: float,
        read_content: bool = False,
        max_bytes: int = 120000,
    ) -> dict[str, object]:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; super-dev-host-audit/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        attempts: list[tuple[str, bool]]
        if read_content:
            attempts = [("GET", True), ("GET", False)]
        else:
            attempts = [("HEAD", True), ("GET", True), ("GET", False)]
        last_error = ""
        last_status: int | None = None
        for method, strict_tls in attempts:
            try:
                req = urllib_request.Request(url, headers=headers, method=method)
                open_kwargs: dict[str, object] = {"timeout": timeout_seconds}
                if not strict_tls:
                    # 不降级到不安全连接，跳过此尝试
                    continue
                with urllib_request.urlopen(req, **open_kwargs) as resp:
                    status = int(getattr(resp, "status", 200))
                    content = ""
                    if read_content and method == "GET":
                        content = resp.read(max_bytes).decode("utf-8", errors="ignore")
                    return {
                        "url": url,
                        "reachable": 200 <= status < 400,
                        "status_code": status,
                        "error": "",
                        "content": content,
                        "method": method,
                        "tls_mode": "strict" if strict_tls else "insecure-fallback",
                    }
            except urllib_error.HTTPError as exc:
                status = int(getattr(exc, "code", 0) or 0)
                last_status = status
                last_error = str(exc)
                if method == "HEAD" and status in {401, 403, 405, 406, 429}:
                    continue
                if 200 <= status < 400:
                    return {
                        "url": url,
                        "reachable": True,
                        "status_code": status,
                        "error": str(exc),
                        "content": "",
                        "method": method,
                        "tls_mode": "strict" if strict_tls else "insecure-fallback",
                    }
                if method == "GET" and not strict_tls:
                    break
            except Exception as exc:
                last_error = str(exc)
                if method == "HEAD":
                    continue
                if method == "GET" and strict_tls:
                    continue
                break
        try:
            return {
                "url": url,
                "reachable": False,
                "status_code": last_status,
                "error": last_error,
                "content": "",
                "method": "GET",
                "tls_mode": "strict",
            }
        except Exception:
            return {
                "url": url,
                "reachable": False,
                "status_code": last_status,
                "error": last_error,
                "content": "",
                "method": "GET",
                "tls_mode": "strict",
            }

    def compare_official_capabilities(
        self, target: str, *, timeout_seconds: float = 5.0
    ) -> dict[str, object]:
        references = self._official_docs_references(target)
        expected = self._capability_labels(target=target)
        if not references:
            return {
                "target": target,
                "status": "missing",
                "expected": expected,
                "checked_urls": 0,
                "reachable_urls": 0,
                "checks": {},
                "details": [],
            }
        fetched = [
            self._fetch_official_doc_excerpt(url, timeout_seconds=timeout_seconds)
            for url in references
        ]
        reachable = [item for item in fetched if bool(item.get("reachable", False))]
        corpus = "\n".join(str(item.get("content", "")).lower() for item in reachable)
        checks: dict[str, dict[str, object]] = {}
        keyword_map: dict[str, tuple[str, ...]] = {
            "slash": ("slash", "/super-dev", "commands", "workflow"),
            "rules": ("rules", "instruction", "guideline", "agents.md", "steering", "context"),
            "skills": ("skill", "skills", "subagent", "sub-agents", "agent"),
        }
        required = 0
        passed = 0
        for capability in ("slash", "rules", "skills"):
            label = str(expected.get(capability, "")).strip().lower()
            if label == "none":
                checks[capability] = {
                    "expected": label,
                    "ok": True,
                    "matched_keywords": [],
                    "reason": "not-required",
                }
                continue
            required += 1
            keywords = keyword_map.get(capability, ())
            matched = [item for item in keywords if item in corpus]
            ok = bool(matched) and bool(reachable)
            if ok:
                passed += 1
            checks[capability] = {
                "expected": label,
                "ok": ok,
                "matched_keywords": matched,
                "reason": (
                    "matched"
                    if ok
                    else ("no-reachable-docs" if not reachable else "keyword-mismatch")
                ),
            }
        if not reachable:
            status = "unknown"
        elif required == 0:
            status = "passed"
        elif passed == required:
            status = "passed"
        elif passed > 0:
            status = "partial"
        else:
            status = "failed"
        return {
            "target": target,
            "status": status,
            "expected": expected,
            "checked_urls": len(fetched),
            "reachable_urls": len(reachable),
            "checks": checks,
            "details": [
                {
                    "url": str(item.get("url", "")),
                    "reachable": bool(item.get("reachable", False)),
                    "status_code": item.get("status_code"),
                    "error": str(item.get("error", "")),
                }
                for item in fetched
            ],
        }

    @classmethod
    def _codex_home_dir(cls) -> Path:
        raw = os.getenv("CODEX_HOME", "").strip()
        if raw:
            return Path(raw).expanduser()
        return Path.home() / ".codex"

    @classmethod
    def resolve_global_protocol_path(cls, target: str) -> Path | None:
        mapping = {
            "claude-code": Path.home() / ".claude" / "CLAUDE.md",
            "codebuddy-cli": Path.home() / ".codebuddy" / "CODEBUDDY.md",
            "codebuddy": Path.home() / ".codebuddy" / "CODEBUDDY.md",
            "codex-cli": cls._codex_home_dir() / "AGENTS.md",
            "kiro-cli": Path.home() / ".kiro" / "steering" / "super-dev.md",
            "kiro": Path.home() / ".kiro" / "steering" / "super-dev.md",
            "gemini-cli": Path.home() / ".gemini" / "GEMINI.md",
            "antigravity": Path.home() / ".gemini" / "GEMINI.md",
            "opencode": Path.home() / ".config" / "opencode" / "AGENTS.md",
            "qoder-cli": Path.home() / ".qoder" / "AGENTS.md",
            "qoder": Path.home() / ".qoder" / "AGENTS.md",
            "trae": Path.home() / ".trae" / "user_rules.md",
        }
        return mapping.get(target)

    @classmethod
    def resolve_compatibility_protocol_path(cls, target: str) -> Path | None:
        if target == "trae":
            return Path.home() / ".trae" / "rules.md"
        return None

    @classmethod
    def expected_skill_path(
        cls,
        target: str,
        skill_name: str = "super-dev-core",
        project_dir: Path | None = None,
    ) -> Path | None:
        paths = cls.expected_skill_paths(target=target, skill_name=skill_name, project_dir=project_dir)
        return paths[0] if paths else None

    @classmethod
    def expected_skill_paths(
        cls,
        target: str,
        skill_name: str = "super-dev-core",
        project_dir: Path | None = None,
    ) -> list[Path]:
        from ..skills import SkillManager

        if not cls.requires_skill(target):
            return []
        paths: list[Path] = []
        project_root = Path(project_dir).resolve() if project_dir is not None else None
        surface_kind = SkillManager.target_path_kind(target)
        for name in SkillManager.compatibility_skill_names(target, skill_name):
            if project_root is not None:
                if target == "codex-cli":
                    paths.append(project_root / ".agents" / "skills" / name / "SKILL.md")
                elif target == "claude-code":
                    paths.append(project_root / ".claude" / "skills" / name / "SKILL.md")
            if target not in SkillManager.TARGET_PATHS:
                continue
            target_root = Path(SkillManager.TARGET_PATHS[target]).expanduser()
            if surface_kind == "observed-compatibility-surface" and not target_root.exists():
                continue
            paths.append(target_root / name / "SKILL.md")
            for mirror in SkillManager.COMPATIBILITY_MIRROR_PATHS.get(target, []):
                mirror_root = (
                    cls._codex_home_dir() / "skills"
                    if target == "codex-cli"
                    else Path(mirror).expanduser()
                )
                paths.append(mirror_root / name / "SKILL.md")
        deduped: list[Path] = []
        seen: set[str] = set()
        for item in paths:
            key = str(item)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    @classmethod
    def contract_validation_groups(cls, target: str) -> list[tuple[str, tuple[str, ...]]]:
        trigger_group = cls.CONTRACT_TRIGGER_GROUPS[
            "slash" if cls.supports_slash(target) else "text"
        ]
        return [
            ("trigger", trigger_group),
            ("documents", cls.CONTRACT_DOC_GROUP),
            ("confirmation", cls.CONTRACT_CONFIRMATION_GROUP),
            ("artifacts", cls.CONTRACT_ARTIFACT_GROUP),
            ("flow", cls.CONTRACT_FLOW_GROUP),
        ]

    @classmethod
    def audit_contract_text(cls, target: str, content: str) -> list[str]:
        normalized = content or ""
        missing: list[str] = []
        for label, options in cls.contract_validation_groups(target):
            if not any(option in normalized for option in options):
                missing.append(label)
        return missing

    @classmethod
    def contract_validation_groups_for_surface(
        cls,
        target: str,
        surface_key: str,
        surface_path: Path,
    ) -> list[tuple[str, tuple[str, ...]]]:
        groups = cls.contract_validation_groups(target)
        trigger_group = groups[0]
        documents_group = groups[1]
        confirmation_group = groups[2]
        artifacts_group = groups[3]
        flow_group = groups[4]

        normalized = surface_path.as_posix()

        if normalized.endswith("/plugins/marketplace.json") or normalized.endswith(
            "/.codex-plugin/plugin.json"
        ) or normalized.endswith("/.claude-plugin/plugin.json") or normalized.endswith(
            "/.claude-plugin/marketplace.json"
        ):
            return []

        if normalized.endswith("/plugins/super-dev-codex/README.md") or normalized.endswith(
            "/plugins/super-dev-claude/README.md"
        ):
            return []

        if "/plugins/super-dev-codex/skills/" in normalized or "/plugins/super-dev-claude/skills/" in normalized:
            return []

        if surface_key.startswith("project-slash:") or surface_key.startswith("global-slash:"):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        if surface_key.startswith("skill:"):
            return [trigger_group, documents_group, confirmation_group, artifacts_group, flow_group]

        if surface_key.startswith("compatibility-protocol:"):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        if normalized.endswith(".agent/workflows/super-dev.md"):
            return [documents_group, confirmation_group, flow_group]

        if normalized.endswith("/agents/super-dev-core.md"):
            return [trigger_group, documents_group, confirmation_group, artifacts_group, flow_group]

        if normalized.endswith("AGENTS.md") and target in {"codex-cli", "opencode"}:
            return [trigger_group, documents_group, confirmation_group, artifacts_group, flow_group]

        if normalized.endswith("GEMINI.md"):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        if normalized.endswith("/steering/AGENTS.md") or normalized.endswith(
            "/steering/super-dev.md"
        ):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        if (
            normalized.endswith("/rules.md")
            or normalized.endswith("/project_rules.md")
            or normalized.endswith("/rules/super-dev.md")
        ):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        return [documents_group, confirmation_group, flow_group]

    @classmethod
    def audit_surface_contract(
        cls,
        target: str,
        surface_key: str,
        surface_path: Path,
        content: str,
    ) -> list[str]:
        normalized = content or ""
        missing: list[str] = []
        for label, options in cls.contract_validation_groups_for_surface(
            target, surface_key, surface_path
        ):
            if not any(option in normalized for option in options):
                missing.append(label)
        return missing

    def collect_managed_surface_paths(
        self, target: str, skill_name: str = "super-dev-core"
    ) -> dict[str, Path]:
        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        surfaces: dict[str, Path] = {}
        for relative in self.TARGETS[target].files:
            surfaces[f"project:{relative}"] = self.project_dir / relative

        protocol_path = self.resolve_global_protocol_path(target)
        if protocol_path is not None:
            surfaces[f"global-protocol:{protocol_path}"] = protocol_path

        compatibility_protocol_path = self.resolve_compatibility_protocol_path(target)
        if compatibility_protocol_path is not None:
            surfaces[f"compatibility-protocol:{compatibility_protocol_path}"] = (
                compatibility_protocol_path
            )

        if self.supports_slash(target):
            project_slash = self.resolve_slash_command_path(
                target=target, scope="project", project_dir=self.project_dir
            )
            if project_slash is not None:
                surfaces[f"project-slash:{project_slash}"] = project_slash
            global_slash = self.resolve_slash_command_path(target=target, scope="global")
            if global_slash is not None and global_slash != project_slash:
                surfaces[f"global-slash:{global_slash}"] = global_slash

        for skill_path in self.expected_skill_paths(target=target, skill_name=skill_name):
            surfaces[f"skill:{skill_path}"] = skill_path

        return surfaces

    def _resolve_surface_declaration(self, *, target: str, surface: str) -> Path:
        normalized = str(surface).strip()
        if normalized == "~/.codex/AGENTS.md":
            return self.resolve_global_protocol_path("codex-cli") or Path(normalized).expanduser()
        if normalized.startswith("~/"):
            return Path(normalized).expanduser()
        return self.project_dir / normalized

    def surface_path_groups(
        self,
        *,
        target: str,
    ) -> dict[str, dict[str, Path]]:
        surfaces = self._install_surfaces(target=target)
        groups: dict[str, dict[str, Path]] = {
            "official_project": {},
            "official_user": {},
            "optional_project": {},
            "optional_user": {},
            "compatibility": {},
        }
        mapping = {
            "official_project_surfaces": "official_project",
            "official_user_surfaces": "official_user",
            "optional_project_surfaces": "optional_project",
            "optional_user_surfaces": "optional_user",
            "observed_compatibility_surfaces": "compatibility",
        }
        for source_key, group_key in mapping.items():
            for surface in surfaces.get(source_key, []):
                if not isinstance(surface, str) or not surface.strip():
                    continue
                path = self._resolve_surface_declaration(target=target, surface=surface)
                groups[group_key][surface] = path
        return groups

    def managed_surface_classification(
        self,
        *,
        target: str,
        skill_name: str = "super-dev-core",
    ) -> dict[str, dict[str, Any]]:
        managed = self.collect_managed_surface_paths(target=target, skill_name=skill_name)
        groups = self.surface_path_groups(target=target)
        group_path_sets = {
            name: {str(path.resolve()) for path in surfaces.values()}
            for name, surfaces in groups.items()
        }
        classified: dict[str, dict[str, Any]] = {}
        for surface_key, surface_path in managed.items():
            resolved = str(surface_path.resolve())
            group = "unclassified"
            for candidate, path_set in group_path_sets.items():
                if resolved in path_set:
                    group = candidate
                    break
            classified[surface_key] = {
                "path": surface_path,
                "group": group,
                "required": group in {"official_project", "official_user"},
            }
        return classified

    def readiness_surface_sets(
        self,
        *,
        target: str,
        skill_name: str = "super-dev-core",
    ) -> dict[str, list[Path]]:
        groups = self.surface_path_groups(target=target)
        skill_paths = self.expected_skill_paths(
            target=target,
            skill_name=skill_name,
            project_dir=self.project_dir,
        )

        official_skill_paths: list[Path] = []
        optional_skill_paths: list[Path] = []
        compatibility_skill_paths: list[Path] = []
        for path in skill_paths:
            resolved = str(path.resolve())
            if resolved in {str(item.resolve()) for item in groups["official_project"].values()} or resolved in {
                str(item.resolve()) for item in groups["official_user"].values()
            }:
                official_skill_paths.append(path)
            elif resolved in {str(item.resolve()) for item in groups["optional_project"].values()} or resolved in {
                str(item.resolve()) for item in groups["optional_user"].values()
            }:
                optional_skill_paths.append(path)
            else:
                compatibility_skill_paths.append(path)

        project_slash: Path | None = None
        global_slash: Path | None = None
        if self.supports_slash(target):
            project_slash = self.resolve_slash_command_path(
                target=target,
                scope="project",
                project_dir=self.project_dir,
            )
            global_slash = self.resolve_slash_command_path(target=target, scope="global")
        required_slash_paths: list[Path] = []
        optional_slash_paths: list[Path] = []
        compatibility_slash_paths: list[Path] = []
        for slash_path in [project_slash, global_slash]:
            if slash_path is None:
                continue
            resolved = str(slash_path.resolve())
            if resolved in {str(item.resolve()) for item in groups["official_project"].values()} or resolved in {
                str(item.resolve()) for item in groups["official_user"].values()
            }:
                required_slash_paths.append(slash_path)
            elif resolved in {str(item.resolve()) for item in groups["optional_project"].values()} or resolved in {
                str(item.resolve()) for item in groups["optional_user"].values()
            }:
                optional_slash_paths.append(slash_path)
            else:
                compatibility_slash_paths.append(slash_path)

        return {
            "official_project": list(groups["official_project"].values()),
            "official_user": list(groups["official_user"].values()),
            "optional_project": list(groups["optional_project"].values()),
            "optional_user": list(groups["optional_user"].values()),
            "compatibility": list(groups["compatibility"].values()),
            "official_skill": official_skill_paths,
            "optional_skill": optional_skill_paths,
            "compatibility_skill": compatibility_skill_paths,
            "required_slash": required_slash_paths,
            "optional_slash": optional_slash_paths,
            "compatibility_slash": compatibility_slash_paths,
        }

    def remove(self, target: str) -> list[Path]:
        """卸载指定宿主的 Super Dev 集成文件"""
        surfaces = self.collect_managed_surface_paths(target=target)
        removed: list[Path] = []
        for _key, path in surfaces.items():
            if path.exists():
                try:
                    if path.name == "AGENTS.md" and target in {"codex-cli", "opencode"}:
                        begin = (
                            self.CODEX_AGENTS_BEGIN
                            if target == "codex-cli"
                            else self.OPENCODE_AGENTS_BEGIN
                        )
                        end = (
                            self.CODEX_AGENTS_END
                            if target == "codex-cli"
                            else self.OPENCODE_AGENTS_END
                        )
                        if self._remove_managed_block(file_path=path, begin=begin, end=end):
                            removed.append(path)
                            continue
                    if path.name == "AGENTS.md" and target in {"qoder", "qoder-cli"}:
                        if self._remove_managed_block(
                            file_path=path,
                            begin=self.QODER_AGENTS_BEGIN,
                            end=self.QODER_AGENTS_END,
                        ):
                            removed.append(path)
                            continue
                    if target == "claude-code" and path.name == "CLAUDE.md":
                        if self._remove_managed_block(
                            file_path=path,
                            begin=self.CLAUDE_RULES_BEGIN,
                            end=self.CLAUDE_RULES_END,
                        ):
                            removed.append(path)
                            continue
                    path.unlink()
                    removed.append(path)
                    # 清理空父目录
                    parent = path.parent
                    if parent.exists() and not any(parent.iterdir()):
                        parent.rmdir()
                except OSError:
                    pass
        return removed

    def _adapter_mode(self, *, target: str, category: str, integration_files: list[str]) -> str:
        first_file = integration_files[0] if integration_files else ""
        if category == "cli":
            return "native-cli-session"
        if first_file.startswith(".super-dev/skills/"):
            return "compat-layer-via-project-skill"
        if target == "vscode-copilot":
            return "native-copilot-instruction-file"
        return "native-ide-rule-file"

    def _usage_profile(self, *, target: str, category: str) -> dict[str, object]:
        usage_location = self.HOST_USAGE_LOCATIONS.get(target, "")
        usage_notes = list(self.HOST_USAGE_NOTES.get(target, []))
        if target == "codex-cli":
            return {
                "usage_mode": "agents-and-skill",
                "primary_entry": "Codex App/Desktop 优先从 `/` 列表选择 `super-dev`；Codex CLI 优先显式输入 `$super-dev`；两端都可用 `super-dev: <需求描述>` 作为 AGENTS 驱动的自然语言回退入口。",
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "entry_variants": [
                    {
                        "surface": "app",
                        "label": "Codex App/Desktop",
                        "entry": "/super-dev",
                        "mode": "enabled-skill-slash-entry",
                        "priority": "preferred",
                        "notes": "在 `/` 列表中直接选择 `super-dev`；这是已启用 Skill 的官方入口，不是项目自定义 slash 文件。",
                    },
                    {
                        "surface": "cli",
                        "label": "Codex CLI",
                        "entry": "$super-dev",
                        "mode": "explicit-skill",
                        "priority": "preferred",
                        "notes": "CLI 中官方显式调用 Skill 的方式，最符合 Codex Skills 文档。",
                    },
                    {
                        "surface": "all",
                        "label": "Codex App/Desktop + CLI",
                        "entry": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                        "mode": "agents-natural-language-fallback",
                        "priority": "fallback",
                        "notes": "由项目 AGENTS.md 与全局 AGENTS.md 驱动的自然语言入口，适合作为统一回退方式。",
                    },
                ],
                "trigger_context": "Codex 当前会话",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重启 codex，使项目根 AGENTS.md、项目级 .agents/skills/super-dev、repo marketplace `.agents/plugins/marketplace.json`、repo plugin `plugins/super-dev-codex/`、全局 CODEX_HOME/AGENTS.md（默认 ~/.codex/AGENTS.md）与 ~/.agents/skills/super-dev/SKILL.md 生效。",
                    "Codex App/Desktop 优先从 `/` 列表选择 `super-dev` skill。",
                    "Codex CLI 优先显式输入 `$super-dev`。",
                    "如果你已经在自然语言上下文里继续当前流程，也可以直接说 `super-dev: <需求描述>`。",
                ],
                "usage_notes": usage_notes,
                "notes": "Codex 官方最佳接入面是项目根 AGENTS.md + 分层 `.agents/skills` + 全局 CODEX_HOME/AGENTS.md（默认 ~/.codex/AGENTS.md）+ 官方用户 skills 目录 ~/.agents/skills；repo 级 `.agents/plugins/marketplace.json` + `plugins/super-dev-codex/.codex-plugin/plugin.json` 作为 Codex App/Desktop 的可选 plugin enhancement 一并提供。Codex App/Desktop 的 `/super-dev` 是已启用 Skill 的官方入口；Codex CLI 的官方显式入口是 `$super-dev`；`super-dev:` 作为 AGENTS 驱动的自然语言回退入口保留。",
            }
        if target == "claude-code":
            return {
                "usage_mode": "native-slash-and-skill",
                "primary_entry": "在 Claude Code 当前项目会话里优先使用 `/super-dev \"<需求描述>\"`；底层由项目根 `CLAUDE.md`、项目级 `.claude/skills/super-dev/`、用户级 `~/.claude/skills/` 驱动，`.claude/commands/` 与 `.claude/agents/` 作为兼容增强面保留。",
                "trigger_command": '/super-dev "<需求描述>"',
                "entry_variants": [
                    {
                        "surface": "app_cli",
                        "label": "Claude Code",
                        "entry": "/super-dev",
                        "mode": "native-slash",
                        "priority": "preferred",
                        "notes": "Slash 仍是用户最直接的触发入口，但其底层应汇入根 `CLAUDE.md` + skills-first 的同一条 Super Dev 流程。",
                    },
                    {
                        "surface": "all",
                        "label": "Fallback",
                        "entry": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                        "mode": "rules-natural-language-fallback",
                        "priority": "fallback",
                        "notes": "自然语言回退入口仍保留，用于当前会话已在项目上下文中继续当前 Super Dev 流程。",
                    },
                ],
                "trigger_context": "Claude Code 当前项目会话",
                "usage_location": usage_location,
                "requires_restart_after_onboard": False,
                "post_onboard_steps": [
                    "确认项目根 `CLAUDE.md` 与兼容 `.claude/CLAUDE.md` 都已写入 Super Dev 规则块。",
                    "确认项目级 `.claude/skills/super-dev/SKILL.md` 与用户级 `~/.claude/skills/super-dev/SKILL.md` 已存在。",
                    "确认兼容 `.claude/commands/super-dev.md`、`.claude/agents/super-dev-core.md` 也已生成。",
                    "若要启用增强层，确认 `.claude-plugin/marketplace.json` 与 `plugins/super-dev-claude/.claude-plugin/plugin.json` 已存在。",
                    '在 Claude Code 当前项目会话里输入 `/super-dev "<需求描述>"` 触发完整流程。',
                ],
                "usage_notes": usage_notes,
                "notes": "Claude Code 当前最佳接入面是项目根 `CLAUDE.md` + 项目级 `.claude/skills/super-dev/` + 用户级 `~/.claude/skills/`；`.claude/commands/` 与 `.claude/agents/` 保留为兼容增强面；repo 级 `.claude-plugin/marketplace.json` + `plugins/super-dev-claude/.claude-plugin/plugin.json` 作为可选 plugin enhancement 一并提供。",
            }
        if target == "antigravity":
            return {
                "usage_mode": "native-slash",
                "primary_entry": '在 Antigravity Agent Chat 输入 `/super-dev "<需求描述>"`（由 GEMINI.md + .agent/workflows + ~/.gemini skills 生效）',
                "trigger_command": '/super-dev "<需求描述>"',
                "trigger_context": "Antigravity IDE Agent Chat",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重新打开 Antigravity，或至少新开一个 Agent Chat。",
                    "确认项目内已生成 `GEMINI.md`、`.gemini/commands/super-dev.md` 与 `.agent/workflows/super-dev.md`。",
                    "确认用户目录已生成 `~/.gemini/GEMINI.md`、`~/.gemini/commands/super-dev.md` 与 `~/.gemini/skills/super-dev-core/SKILL.md`。",
                    '在 Antigravity Agent Chat 输入 `/super-dev "<需求描述>"` 触发完整流程。',
                ],
                "usage_notes": usage_notes,
                "notes": "Antigravity 当前按 Gemini 上下文面 + 项目 workflow 面接入；slash 负责触发，宿主级 Skill 负责让宿主理解 Super Dev 流水线。",
            }
        if target == "trae":
            return {
                "usage_mode": "rules-and-skill",
                "primary_entry": "在 Trae Agent Chat 输入 `super-dev: <需求描述>`（由 .trae/project_rules.md + ~/.trae/user_rules.md + .trae/rules.md / ~/.trae/rules.md〔兼容规则面〕 + 兼容 Skill〔若检测到〕生效）",
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "trigger_context": "Trae Agent Chat",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重新打开 Trae，或至少新开一个 Agent Chat，使新的规则与兼容 Skill（若已安装）一起生效。",
                    "确认项目内已生成 `.trae/project_rules.md` 与 `.trae/rules.md`，用户目录已生成 `~/.trae/user_rules.md` 与 `~/.trae/rules.md`。",
                    "确保当前项目就是已接入 Super Dev 的工作区。",
                    "输入 `super-dev: <需求描述>` 触发完整流程。",
                    "按 output/* 与 .super-dev/changes/*/tasks.md 执行开发。",
                ],
                "usage_notes": usage_notes,
                "notes": "该宿主当前以项目级 `.trae/project_rules.md` 与用户级 `~/.trae/user_rules.md` 为官方核心接入面；同时会兼容写入 `.trae/rules.md` 与 `~/.trae/rules.md`，若检测到 ~/.trae/skills，则会增强安装 super-dev-core。",
            }
        if target == "kiro":
            return {
                "usage_mode": "native-slash",
                "primary_entry": '在 Kiro IDE Agent Chat 输入 `/super-dev "<需求描述>"`（由 `.kiro/steering/super-dev.md` + `.kiro/skills/` / `~/.kiro/steering/` + `~/.kiro/skills/` 生效）',
                "trigger_command": '/super-dev "<需求描述>"',
                "trigger_context": "Kiro IDE Agent Chat",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重新打开 Kiro，或至少新开一个 Agent Chat，使 steering 与 skills 一起生效。",
                    "确保当前项目就是已接入 Super Dev 的工作区。",
                    '优先输入 `/super-dev "<需求描述>"` 触发完整流程；若当前会话只接受自然语言，再回退到 `super-dev: <需求描述>`。',
                    "按 output/* 与 .super-dev/changes/*/tasks.md 执行开发。",
                ],
                "usage_notes": usage_notes,
                "notes": "该宿主当前走官方 steering + skills 模式：项目级 `.kiro/steering/super-dev.md` 会通过 steering inclusion 暴露 `/super-dev`，项目级 `.kiro/skills/` 与 `~/.kiro/skills/` 提供能力增强，`~/.kiro/steering/` 提供全局 steering 记忆。",
            }
        if target == "kiro-cli":
            return {
                "usage_mode": "native-slash",
                "primary_entry": '在 Kiro CLI 会话输入 `/super-dev "<需求描述>"`（由 `.kiro/steering/super-dev.md` + `.kiro/skills/` / `~/.kiro/steering/` + `~/.kiro/skills/` 生效）',
                "trigger_command": '/super-dev "<需求描述>"',
                "trigger_context": "Kiro CLI 当前会话",
                "usage_location": usage_location
                or "进入目标项目目录后，重开 Kiro CLI 会话再触发。",
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重开 Kiro CLI，使 `.kiro/steering/` 与 skills 在新会话里生效。",
                    "确认项目内已生成 `.kiro/steering/super-dev.md` 与 `.kiro/skills/super-dev-core/SKILL.md`。",
                    "确认用户目录已生成 `~/.kiro/steering/super-dev.md` 与 `~/.kiro/skills/super-dev-core/SKILL.md`。",
                    '在 Kiro CLI 会话里优先输入 `/super-dev "<需求描述>"`；若当前会话只接受自然语言，再回退到 `super-dev: <需求描述>`。',
                ],
                "usage_notes": usage_notes,
                "notes": "Kiro CLI 当前按官方 steering + skills 模式触发：steering inclusion 会把 `/super-dev` 暴露进 slash 入口，skills 负责让宿主理解完整 Super Dev 流程。",
            }
        if self.supports_slash(target):
            if category == "cli":
                return {
                    "usage_mode": "native-slash",
                    "primary_entry": '/super-dev "<需求描述>"（在该 CLI 宿主会话内）',
                    "trigger_command": '/super-dev "<需求描述>"',
                    "trigger_context": "当前 CLI 宿主会话",
                    "usage_location": usage_location
                    or "在项目目录启动宿主当前 CLI 会话后，直接在同一会话里触发。",
                    "requires_restart_after_onboard": False,
                    "post_onboard_steps": [
                        "保持在宿主当前会话中执行 /super-dev。",
                        "让宿主先完成同类产品研究，再继续文档与编码阶段。",
                    ],
                    "usage_notes": usage_notes
                    or [
                        "建议在同一会话里连续完成 research、文档、Spec 与编码。",
                        "接入时还会安装宿主级 super-dev-core Skill，让宿主理解完整流水线契约。",
                    ],
                    "notes": "CLI 宿主建议直接在当前会话执行 slash 命令；slash 负责触发，host skill 负责让宿主理解 Super Dev 流水线协议。",
                }
            return {
                "usage_mode": "native-slash",
                "primary_entry": '/super-dev "<需求描述>"（在 IDE Agent Chat 内）',
                "trigger_command": '/super-dev "<需求描述>"',
                "trigger_context": "IDE Agent Chat",
                "usage_location": usage_location
                or "打开宿主 IDE 的 Agent Chat，在当前项目上下文内触发。",
                "requires_restart_after_onboard": False,
                "post_onboard_steps": [
                    "在 IDE Agent Chat 中执行 /super-dev。",
                    "保持研究、文档、Spec 与编码在同一上下文中连续完成。",
                ],
                "usage_notes": usage_notes
                or [
                    "建议固定在项目级 Agent Chat 中完成整条流水线。",
                    "接入时还会安装宿主级 super-dev-core Skill，让宿主理解完整流水线契约。",
                ],
                "notes": "IDE 宿主优先通过 Agent Chat 触发；slash 负责触发，host skill 负责让宿主理解 Super Dev 流水线协议。",
            }
        return {
            "usage_mode": "rules-only",
            "primary_entry": "输入 `super-dev: <需求描述>`（由项目规则生效）",
            "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
            "entry_variants": [
                {
                    "surface": "default",
                    "label": "Default",
                    "entry": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                    "mode": "rules-natural-language",
                    "priority": "preferred",
                    "notes": "由项目规则文件驱动的标准入口。",
                }
            ],
            "trigger_context": "宿主当前会话",
            "usage_location": usage_location or "在宿主当前项目会话里触发。",
            "requires_restart_after_onboard": False,
            "post_onboard_steps": [
                "直接在宿主会话输入 `super-dev: <需求描述>`。",
                "按 output/* 与 tasks.md 继续执行开发流程。",
            ],
            "usage_notes": usage_notes
            or [
                "该宿主当前通过规则文件约束执行流程。",
            ],
            "notes": "该宿主通过项目规则文件约束执行流程。",
        }

    def _smoke_profile(self, *, target: str, category: str) -> dict[str, object]:
        trigger = (
            self.TEXT_TRIGGER_PREFIX
            + " 请先不要开始编码，只回复 SMOKE_OK，并确认已读取当前项目中的 Super Dev 规则。"
        )
        if self.supports_slash(target):
            trigger = '/super-dev "请先不要开始编码，只回复 SMOKE_OK，并确认已读取当前项目中的 Super Dev 规则。"'
        if target == "codex-cli":
            steps = [
                "完成接入后先重启 codex。",
                "进入已接入 Super Dev 的项目目录。",
                f"优先在 Codex 会话输入：{trigger}",
                "如果你想显式调用官方 Skill，可输入 `$super-dev`；如果桌面端 `/` 列表里出现 `super-dev`，也可以直接选择它。",
            ]
        else:
            steps = [
                "进入已接入 Super Dev 的项目目录或工作区。",
                f"在宿主正确的聊天/会话入口输入：{trigger}",
            ]
        if category == "ide":
            steps.insert(1, "确认当前 Agent Chat/Workflow 绑定的是目标项目。")
        return {
            "smoke_test_prompt": trigger,
            "smoke_test_steps": steps,
            "smoke_success_signal": "宿主回复 SMOKE_OK，并明确表示已读取当前项目内的 Super Dev 规则/AGENTS/命令映射，且没有直接开始编码。",
        }

    def _precondition_profile(self, *, target: str) -> dict[str, object]:
        guidance = list(self.HOST_PRECONDITION_GUIDANCE.get(target, []))
        items: list[dict[str, object]] = []
        usage = self._usage_profile(
            target=target, category=HOST_TOOL_CATEGORY_MAP.get(target, "ide")
        )

        context_item = {
            "status": "project-context-required",
            "label": "需在目标项目/工作区内触发",
            "guidance": [str(usage["usage_location"]).strip()],
            "signals": {
                "project_dir_exists": self.project_dir.exists(),
            },
        }
        if str(usage["usage_location"]).strip():
            items.append(context_item)

        if bool(usage["requires_restart_after_onboard"]):
            items.append(
                {
                    "status": "session-restart-required",
                    "label": "接入后需重开宿主会话",
                    "guidance": [
                        "完成 `super-dev onboard/setup` 后，关闭旧会话并新开一个宿主会话，再触发 Super Dev。",
                    ],
                    "signals": {},
                }
            )

        extra = [item for item in guidance if isinstance(item, str) and item.strip()]
        if extra and items:
            items[0]["guidance"] = list(dict.fromkeys([*items[0]["guidance"], *extra]))

        if not items:
            return {
                "status": "none",
                "label": "无额外前置条件",
                "guidance": [],
                "signals": {},
                "items": [],
            }

        priority = {
            "host-auth-required": 0,
            "session-restart-required": 1,
            "project-context-required": 2,
        }
        primary = min(
            items,
            key=lambda item: priority.get(str(item.get("status", "")), 99),
        )
        combined_guidance: list[str] = []
        combined_signals: dict[str, bool] = {}
        for item in items:
            for guidance_item in item.get("guidance", []):
                if (
                    isinstance(guidance_item, str)
                    and guidance_item.strip()
                    and guidance_item not in combined_guidance
                ):
                    combined_guidance.append(guidance_item.strip())
            item_signals = item.get("signals", {})
            if isinstance(item_signals, dict):
                for key, value in item_signals.items():
                    combined_signals[str(key)] = bool(value)

        return {
            "status": str(primary.get("status", "none")),
            "label": str(primary.get("label", "无额外前置条件")),
            "guidance": combined_guidance,
            "signals": combined_signals,
            "items": items,
        }

    def _protocol_profile(self, *, target: str) -> dict[str, str]:
        mapping = {
            "claude-code": {
                "mode": "official-skill",
                "summary": "官方 CLAUDE.md + Skills + optional repo plugin enhancement",
            },
            "antigravity": {
                "mode": "official-workflow",
                "summary": "官方 commands + workflows + skills",
            },
            "codebuddy-cli": {
                "mode": "official-skill",
                "summary": "官方 CODEBUDDY.md + commands + skills + AGENTS.md compatibility",
            },
            "codebuddy": {
                "mode": "official-subagent",
                "summary": "官方 CODEBUDDY.md + rules + commands + agents + skills",
            },
            "vscode-copilot": {
                "mode": "official-context",
                "summary": "官方 copilot-instructions + AGENTS.md compatibility",
            },
            "cline": {
                "mode": "official-context",
                "summary": "官方 .clinerules + skills + AGENTS.md compatibility",
            },
            "roo-code": {
                "mode": "official-skill",
                "summary": "官方 commands + rules",
            },
            "qoder-cli": {
                "mode": "official-skill",
                "summary": "官方 rules + commands + skills + AGENTS.md memory",
            },
            "qoder": {
                "mode": "official-skill",
                "summary": "官方 rules + commands + skills + AGENTS.md memory",
            },
            "windsurf": {
                "mode": "official-skill",
                "summary": "官方 rules + workflows + skills",
            },
            "opencode": {
                "mode": "official-skill",
                "summary": "官方 AGENTS.md + commands + skills",
            },
            "kilo-code": {
                "mode": "official-rules",
                "summary": "官方 rules",
            },
            "kiro": {
                "mode": "official-steering",
                "summary": "官方 steering + slash entry + skills",
            },
            "codex-cli": {
                "mode": "official-skill",
                "summary": "官方 AGENTS.md + 官方 Skills + optional repo plugin enhancement",
            },
            "copilot-cli": {
                "mode": "official-context",
                "summary": "官方 copilot-instructions + skills + AGENTS.md compatibility",
            },
            "cursor-cli": {
                "mode": "official-context",
                "summary": "官方 commands + rules + AGENTS.md compatibility",
            },
            "cursor": {
                "mode": "official-context",
                "summary": "官方 commands + rules + AGENTS.md compatibility",
            },
            "gemini-cli": {
                "mode": "official-context",
                "summary": "官方 commands + GEMINI.md",
            },
            "kiro-cli": {
                "mode": "official-steering",
                "summary": "官方 steering + slash entry + skills",
            },
            "trae": {
                "mode": "compatibility-skill",
                "summary": "官方 rules + 兼容 Skill",
            },
            "openclaw": {
                "mode": "official-skill",
                "summary": "官方 Plugin SDK + Skills",
            },
        }
        return mapping.get(target, {"mode": "none", "summary": ""})

    def _install_surfaces(self, *, target: str) -> dict[str, list[str]]:
        by_target: dict[str, dict[str, list[str]]] = {
            "claude-code": {
                "official_project_surfaces": [
                    "CLAUDE.md",
                    ".claude/skills/super-dev/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.claude/CLAUDE.md",
                    "~/.claude/skills/super-dev/SKILL.md",
                ],
                "optional_project_surfaces": [
                    ".claude/CLAUDE.md",
                    ".claude/commands/super-dev.md",
                    ".claude/agents/super-dev-core.md",
                    ".claude-plugin/marketplace.json",
                    "plugins/super-dev-claude/.claude-plugin/plugin.json",
                    "plugins/super-dev-claude/README.md",
                    "plugins/super-dev-claude/skills/super-dev/SKILL.md",
                    "plugins/super-dev-claude/skills/super-dev-core/SKILL.md",
                    "plugins/super-dev-claude/agents/super-dev-core.md",
                ],
                "optional_user_surfaces": ["~/.claude/commands/super-dev.md"],
                "observed_compatibility_surfaces": [
                    "~/.claude/skills/super-dev-core/SKILL.md",
                    "~/.claude/agents/super-dev-core.md",
                ],
            },
            "antigravity": {
                "official_project_surfaces": [
                    "GEMINI.md",
                    ".gemini/commands/super-dev.md",
                    ".agent/workflows/super-dev.md",
                ],
                "official_user_surfaces": [
                    "~/.gemini/GEMINI.md",
                    "~/.gemini/commands/super-dev.md",
                    "~/.gemini/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "codebuddy-cli": {
                "official_project_surfaces": [
                    "CODEBUDDY.md",
                    ".codebuddy/commands/super-dev.md",
                    ".codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.codebuddy/CODEBUDDY.md",
                    "~/.codebuddy/commands/super-dev.md",
                    "~/.codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [".codebuddy/AGENTS.md"],
            },
            "codebuddy": {
                "official_project_surfaces": [
                    "CODEBUDDY.md",
                    ".codebuddy/rules/super-dev/RULE.mdc",
                    ".codebuddy/commands/super-dev.md",
                    ".codebuddy/agents/super-dev-core.md",
                    ".codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.codebuddy/CODEBUDDY.md",
                    "~/.codebuddy/commands/super-dev.md",
                    "~/.codebuddy/agents/super-dev-core.md",
                    "~/.codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [".codebuddy/rules.md", ".codebuddy/AGENTS.md"],
            },
            "vscode-copilot": {
                "official_project_surfaces": [".github/copilot-instructions.md"],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": ["AGENTS.md"],
            },
            "cline": {
                "official_project_surfaces": [
                    ".clinerules/super-dev.md",
                    ".cline/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/Documents/Cline/Rules/super-dev.md",
                    "~/.cline/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": ["AGENTS.md"],
            },
            "kilo-code": {
                "official_project_surfaces": [".kilocode/rules/super-dev.md"],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": [],
            },
            "roo-code": {
                "official_project_surfaces": [
                    ".roo/rules/super-dev.md",
                    ".roo/commands/super-dev.md",
                ],
                "official_user_surfaces": [
                    "~/.roo/rules/super-dev.md",
                    "~/.roo/commands/super-dev.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "codex-cli": {
                "official_project_surfaces": [
                    "AGENTS.md",
                    ".agents/skills/super-dev/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.codex/AGENTS.md",
                    "~/.agents/skills/super-dev/SKILL.md",
                ],
                "optional_project_surfaces": [
                    ".agents/plugins/marketplace.json",
                    "plugins/super-dev-codex/.codex-plugin/plugin.json",
                    "plugins/super-dev-codex/README.md",
                    "plugins/super-dev-codex/skills/super-dev/SKILL.md",
                    "plugins/super-dev-codex/skills/super-dev-core/SKILL.md",
                ],
                "optional_user_surfaces": [],
                "observed_compatibility_surfaces": [
                    "~/.agents/skills/super-dev-core/SKILL.md",
                    "~/.codex/skills/super-dev/SKILL.md",
                    "~/.codex/skills/super-dev-core/SKILL.md",
                ],
            },
            "copilot-cli": {
                "official_project_surfaces": [
                    ".github/copilot-instructions.md",
                    ".github/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": ["~/.copilot/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": ["AGENTS.md"],
            },
            "cursor-cli": {
                "official_project_surfaces": [
                    ".cursor/rules/super-dev.mdc",
                    ".cursor/commands/super-dev.md",
                ],
                "official_user_surfaces": ["~/.cursor/commands/super-dev.md"],
                "observed_compatibility_surfaces": [
                    "AGENTS.md",
                    "~/.cursor/skills/super-dev-core/SKILL.md",
                ],
            },
            "cursor": {
                "official_project_surfaces": [
                    ".cursor/rules/super-dev.mdc",
                    ".cursor/commands/super-dev.md",
                ],
                "official_user_surfaces": ["~/.cursor/commands/super-dev.md"],
                "observed_compatibility_surfaces": [
                    "AGENTS.md",
                    "~/.cursor/skills/super-dev-core/SKILL.md",
                ],
            },
            "windsurf": {
                "official_project_surfaces": [
                    ".windsurf/rules/super-dev.md",
                    ".windsurf/workflows/super-dev.md",
                    ".windsurf/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": ["~/.codeium/windsurf/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": [],
            },
            "gemini-cli": {
                "official_project_surfaces": ["GEMINI.md", ".gemini/commands/super-dev.md"],
                "official_user_surfaces": [
                    "~/.gemini/GEMINI.md",
                    "~/.gemini/commands/super-dev.md",
                ],
                "observed_compatibility_surfaces": ["~/.gemini/skills/super-dev-core/SKILL.md"],
            },
            "kiro-cli": {
                "official_project_surfaces": [
                    ".kiro/steering/super-dev.md",
                    ".kiro/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.kiro/steering/super-dev.md",
                    "~/.kiro/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "kiro": {
                "official_project_surfaces": [
                    ".kiro/steering/super-dev.md",
                    ".kiro/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.kiro/steering/super-dev.md",
                    "~/.kiro/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": ["~/.kiro/steering/AGENTS.md"],
            },
            "opencode": {
                "official_project_surfaces": [
                    "AGENTS.md",
                    ".opencode/commands/super-dev.md",
                    ".opencode/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.config/opencode/AGENTS.md",
                    "~/.config/opencode/commands/super-dev.md",
                    "~/.config/opencode/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "qoder-cli": {
                "official_project_surfaces": [
                    "AGENTS.md",
                    ".qoder/rules/super-dev.md",
                    ".qoder/commands/super-dev.md",
                    ".qoder/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.qoder/AGENTS.md",
                    "~/.qoder/commands/super-dev.md",
                    "~/.qoder/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "qoder": {
                "official_project_surfaces": [
                    "AGENTS.md",
                    ".qoder/rules/super-dev.md",
                    ".qoder/commands/super-dev.md",
                    ".qoder/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.qoder/AGENTS.md",
                    "~/.qoder/commands/super-dev.md",
                    "~/.qoder/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "trae": {
                "official_project_surfaces": [".trae/project_rules.md"],
                "official_user_surfaces": ["~/.trae/user_rules.md"],
                "observed_compatibility_surfaces": [
                    ".trae/rules.md",
                    "~/.trae/rules.md",
                    "~/.trae/skills/super-dev-core/SKILL.md",
                ],
            },
            "openclaw": {
                "official_project_surfaces": [
                    ".openclaw/rules/super-dev.md",
                    ".openclaw/commands/super-dev.md",
                ],
                "official_user_surfaces": [
                    "~/.openclaw/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
        }
        surfaces = by_target.get(
            target,
            {
                "official_project_surfaces": [],
                "official_user_surfaces": [],
                "optional_project_surfaces": [],
                "optional_user_surfaces": [],
                "observed_compatibility_surfaces": [],
            },
        )
        surfaces.setdefault("optional_project_surfaces", [])
        surfaces.setdefault("optional_user_surfaces", [])
        return surfaces

    def setup(self, target: str, force: bool = False) -> list[Path]:
        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        written_files: list[Path] = []
        integration = self.TARGETS[target]
        for relative in integration.files:
            file_path = self.project_dir / relative
            if target in {"codex-cli", "opencode", "qoder", "qoder-cli"} and relative == "AGENTS.md":
                begin = (
                    self.CODEX_AGENTS_BEGIN
                    if target == "codex-cli"
                    else self.OPENCODE_AGENTS_BEGIN
                    if target == "opencode"
                    else self.QODER_AGENTS_BEGIN
                )
                end = (
                    self.CODEX_AGENTS_END
                    if target == "codex-cli"
                    else self.OPENCODE_AGENTS_END
                    if target == "opencode"
                    else self.QODER_AGENTS_END
                )
                block_content = self._append_flow_contract(
                    content=self._build_file_content(target=target, relative=relative),
                    relative=relative,
                )
                updated = self._upsert_managed_block(
                    file_path=file_path,
                    begin=begin,
                    end=end,
                    block_content=block_content,
                )
                if updated:
                    written_files.append(file_path)
                continue
            if target == "claude-code" and relative in {"CLAUDE.md", ".claude/CLAUDE.md"}:
                block_content = self._append_flow_contract(
                    content=self._build_file_content(target=target, relative=relative),
                    relative=relative,
                )
                updated = self._upsert_managed_block(
                    file_path=file_path,
                    begin=self.CLAUDE_RULES_BEGIN,
                    end=self.CLAUDE_RULES_END,
                    block_content=block_content,
                )
                if updated:
                    written_files.append(file_path)
                continue
            if file_path.exists() and not force:
                continue
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = self._append_flow_contract(
                content=self._build_file_content(target=target, relative=relative),
                relative=relative,
            )
            file_path.write_text(content, encoding="utf-8")
            written_files.append(file_path)

        # Auto-install enforcement hooks for supported hosts
        if target == "claude-code":
            try:
                from .._enforcement_bridge import auto_install_enforcement

                enforcement_files = auto_install_enforcement(self.project_dir)
                written_files.extend(enforcement_files)
            except Exception:
                pass  # Graceful degradation — enforcement is optional

        return written_files

    def setup_global_protocol(self, target: str, force: bool = False) -> Path | None:
        protocol_file = self.resolve_global_protocol_path(target)

        if target == "codex-cli" and protocol_file is not None:
            block_content = self._append_flow_contract(
                content=self._build_codex_agents_content(),
                relative=protocol_file.as_posix(),
            )
            updated = self._upsert_managed_block(
                file_path=protocol_file,
                begin=self.CODEX_AGENTS_BEGIN,
                end=self.CODEX_AGENTS_END,
                block_content=block_content,
            )
            return protocol_file if updated or protocol_file.exists() else None

        if target == "claude-code" and protocol_file is not None:
            block_content = self._append_flow_contract(
                content=self._build_file_content(target=target, relative=protocol_file.name),
                relative=protocol_file.as_posix(),
            )
            updated = self._upsert_managed_block(
                file_path=protocol_file,
                begin=self.CLAUDE_RULES_BEGIN,
                end=self.CLAUDE_RULES_END,
                block_content=block_content,
            )
            return protocol_file if updated or protocol_file.exists() else None

        if target in {"codebuddy", "codebuddy-cli"} and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_content(target),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target in {"kiro", "kiro-cli"} and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_kiro_global_steering_content(),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target in {"qoder", "qoder-cli"} and protocol_file is not None:
            block_content = self._append_flow_contract(
                content=self._build_content(target),
                relative=protocol_file.as_posix(),
            )
            updated = self._upsert_managed_block(
                file_path=protocol_file,
                begin=self.QODER_AGENTS_BEGIN,
                end=self.QODER_AGENTS_END,
                block_content=block_content,
            )
            return protocol_file if updated or protocol_file.exists() else None

        if target == "gemini-cli" and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_content(target),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target == "antigravity" and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_antigravity_context_content(),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target == "opencode" and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_content(target),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target == "trae" and protocol_file is not None:
            compatibility_file = self.resolve_compatibility_protocol_path(target)
            content = self._append_flow_contract(
                content=self._build_content(target),
                relative=protocol_file.as_posix(),
            )
            if protocol_file.exists() and not force:
                if compatibility_file is not None and not compatibility_file.exists():
                    compatibility_file.parent.mkdir(parents=True, exist_ok=True)
                    compatibility_file.write_text(
                        self._append_flow_contract(
                            content=content,
                            relative=compatibility_file.as_posix(),
                        ),
                        encoding="utf-8",
                    )
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(content, encoding="utf-8")
            if compatibility_file is not None:
                compatibility_file.parent.mkdir(parents=True, exist_ok=True)
                compatibility_file.write_text(
                    self._append_flow_contract(
                        content=content,
                        relative=compatibility_file.as_posix(),
                    ),
                    encoding="utf-8",
                )
            return protocol_file

        return None
