"""
多平台 AI Coding 工具集成管理器
"""

from __future__ import annotations

import os
import ssl
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from ..catalogs import HOST_TOOL_CATEGORY_MAP, HOST_TOOL_IDS


@dataclass
class IntegrationTarget:
    name: str
    description: str
    files: list[str]


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
    observed_compatibility_surfaces: list[str]
    official_docs_references: list[str]
    docs_check_status: str
    docs_check_summary: str
    capability_labels: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class IntegrationManager:
    """为不同 AI Coding 平台生成集成配置"""

    TEXT_TRIGGER_PREFIX = "super-dev:"
    TEXT_TRIGGER_PREFIX_FULLWIDTH = "super-dev："
    CODEX_AGENTS_BEGIN = "<!-- BEGIN SUPER DEV CODEX -->"
    CODEX_AGENTS_END = "<!-- END SUPER DEV CODEX -->"
    NO_SKILL_TARGETS: set[str] = {
        "aider",
        "claude-code",
        "cline",
        "jetbrains-ai",
        "kilo-code",
        "kiro",
        "vscode-copilot",
    }
    HOST_USAGE_LOCATIONS: dict[str, str] = {
        "antigravity": "打开 Antigravity 的 Agent Chat / Prompt 面板，并确保当前工作区就是目标项目。",
        "aider": "在项目目录启动 aider 会话后触发。",
        "claude-code": "在项目目录启动 Claude Code 当前会话后，直接在同一会话里触发。",
        "cline": "在 VS Code 的 Cline 面板中，绑定当前项目后触发。",
        "codebuddy-cli": "在项目目录启动 CodeBuddy CLI 会话后触发。",
        "codebuddy": "打开 CodeBuddy IDE 的 Agent Chat，在项目上下文内触发。",
        "codex-cli": "在项目目录完成接入后，重启 codex，然后在新的 Codex CLI 会话里触发。",
        "copilot-cli": "在项目目录启动 Copilot CLI 会话后触发。",
        "cursor-cli": "在项目目录启动 Cursor CLI 当前会话后触发。",
        "cursor": "打开 Cursor 的 Agent Chat，并确保当前工作区就是目标项目。",
        "windsurf": "打开 Windsurf 的 Agent Chat 或 Workflow 入口，在项目上下文内触发。",
        "gemini-cli": "在项目目录启动 Gemini CLI 会话后触发。",
        "iflow": "在项目目录启动 iFlow CLI 会话后触发。",
        "jetbrains-ai": "在 JetBrains IDE 的 Junie/AI Agent 会话中触发。",
        "kimi-cli": "在项目目录启动 Kimi CLI 会话后触发。",
        "kiro-cli": "在项目目录启动 Kiro CLI 会话后触发。",
        "opencode": "在项目目录启动 OpenCode CLI 会话后触发。",
        "qoder-cli": "在项目目录启动 Qoder CLI 会话后触发。",
        "roo-code": "在 VS Code 的 Roo Code 聊天面板中触发。",
        "vscode-copilot": "在 VS Code Copilot Chat 绑定当前项目后触发。",
        "kilo-code": "在 VS Code 的 Kilo Code 聊天面板中触发。",
        "kiro": "打开 Kiro IDE 的 Agent Chat 或 AI 面板，在项目上下文内触发。",
        "qoder": "打开 Qoder IDE 的 Agent Chat，在当前项目内触发。",
        "trae": "打开 Trae Agent Chat，在当前项目上下文内直接触发。",
    }
    HOST_USAGE_NOTES: dict[str, list[str]] = {
        "antigravity": [
            "Antigravity 当前优先按 `GEMINI.md + .agent/workflows + /super-dev` 模式接入。",
            "项目内会写入 `GEMINI.md`、`.gemini/commands/super-dev.md` 与 `.agent/workflows/super-dev.md`。",
            "用户级会补充 `~/.gemini/GEMINI.md`、`~/.gemini/commands/super-dev.md` 与 `~/.gemini/skills/super-dev-core/SKILL.md`。",
            "接入后建议新开一个 Antigravity Chat，使 GEMINI 上下文、slash 与 Skill 一起生效。",
        ],
        "aider": [
            "Aider 是终端宿主，建议配合 `.aider.conf.yml` 与 `--read` 只读上下文文件。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，不走 slash。",
        ],
        "claude-code": [
            "推荐作为首选 CLI 宿主。",
            "接入后可先执行 super-dev doctor --host claude-code 确认 slash 已生效。",
            "Claude Code 官方已公开 `.claude/agents/` 与 `~/.claude/agents/`，Super Dev 会生成 subagent 协议文件。",
        ],
        "cline": [
            "Cline 优先使用 `.clinerules/` 规则目录，确保项目约束在每次任务开始时自动注入。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，减少与内建 slash 的语义冲突。",
        ],
        "codebuddy-cli": [
            "在当前 CLI 会话中直接输入即可。",
            "如果会话早于接入动作启动，建议重开会话后再试。",
            "官方文档已公开 ~/.codebuddy/skills 与 .codebuddy/skills，可与 slash 一起增强宿主对 Super Dev 流水线的理解。",
        ],
        "codebuddy": [
            "建议在项目级 Agent Chat 中使用，不要脱离项目上下文。",
            "先让宿主完成 research，再继续文档和编码。",
            "官方文档已公开 `.codebuddy/commands/`、`.codebuddy/agents/`、`.codebuddy/skills/` 与 `~/.codebuddy/agents/`、`~/.codebuddy/skills/`。",
        ],
        "codex-cli": [
            "不要输入 /super-dev，Codex 当前不走自定义 slash。",
            "实际依赖项目根 AGENTS.md 和 ~/.codex/skills/super-dev-core/SKILL.md。",
            "如果旧会话没加载新 Skill，重启 codex 再试。",
        ],
        "copilot-cli": [
            "Copilot CLI 优先按 `.github/copilot-instructions.md` + `AGENTS.md` 注入项目约束。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，不走自定义 slash。",
            "如果宿主未加载项目规则，重启 copilot 会话再试。",
        ],
        "cursor-cli": [
            "适合终端内连续执行研究、文档和编码。",
            "若命令列表未刷新，可重开一次 Cursor CLI 会话。",
        ],
        "cursor": [
            "建议固定在同一个 Agent Chat 会话里完成整条流水线。",
            "如果项目规则没加载，先重新打开工作区或重新发起聊天。",
        ],
        "windsurf": [
            "当前按 IDE slash/workflow 模式适配。",
            "更适合在同一个 Workflow 里连续完成研究、三文档、确认门、Spec 与编码。",
            "官方文档已公开 .windsurf/skills 与 ~/.codeium/windsurf/skills。",
        ],
        "gemini-cli": [
            "优先在同一会话中完成 research -> 三文档 -> 用户确认 -> Spec -> 前端运行验证 -> 后端/交付。",
            "若宿主支持联网，先让它完成同类产品研究。",
        ],
        "jetbrains-ai": [
            "JetBrains Junie 推荐使用 `.junie/AGENTS.md` 统一项目级上下文。",
            "当前按文本触发 `super-dev: <需求描述>` 适配，不依赖自定义 slash。",
        ],
        "iflow": [
            "当前按 slash 宿主适配。",
            "如果 slash 未出现，先检查项目级命令文件是否已写入。",
            "官方文档已公开 .iflow/skills 与 ~/.iflow/skills。",
            "如果宿主报 `Invalid API key provided`，先在 iFlow 会话内执行 `/auth`，或更新 IFLOW_API_KEY / settings.json 后重启宿主。",
        ],
        "kimi-cli": [
            "Kimi CLI 当前优先按 AGENTS.md + 宿主级 Skill / 自然语言触发，不走 `/super-dev`。",
            "建议先用 super-dev doctor --host kimi-cli 做一次确认。",
        ],
        "kiro-cli": [
            "CLI 模式下直接使用 slash。",
            "如果项目规则未刷新，重新进入项目目录再启动 Kiro CLI。",
        ],
        "opencode": [
            "按 CLI slash 模式使用。",
            "即使你也使用全局命令目录，仍建议保留项目级接入文件。",
            "官方文档已公开 .opencode/skills 与 ~/.config/opencode/skills。",
        ],
        "qoder-cli": [
            "适合命令行流水线开发。",
            "若 slash 未生效，先确认 .qoder/commands/super-dev.md 已生成。",
            "官方文档已公开 .qoder/skills 与 ~/.qoder/skills。",
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
            "Kiro IDE 当前优先按 steering/rules + 宿主级 Skill 模式触发，不走 /super-dev。",
            "如果 steering、rules 或 Skill 未加载，先重开项目窗口或新开一个 Agent Chat。",
            "Kiro 官方已公开全局 steering 目录 `~/.kiro/steering/`，Super Dev 会优先写入全局 AGENTS.md。",
        ],
        "qoder": [
            "Qoder IDE 当前优先按项目级 commands + rules + 宿主级 Skill 模式触发，可直接使用 /super-dev。",
            "若新增命令未出现，重新打开项目或新开一个 Agent Chat。",
            "官方文档已公开 .qoder/skills 与 ~/.qoderwork/skills。",
        ],
        "trae": [
            "不要输入 /super-dev。",
            "Trae 优先依赖项目级 `.trae/project_rules.md` 与用户级 `~/.trae/user_rules.md`；同时会兼容写入 `.trae/rules.md` 与 `~/.trae/rules.md`，用于命中当前已观测到的规则加载面。",
            "若检测到宿主级 ~/.trae/skills/super-dev-core/SKILL.md，则会额外增强。",
            "安装后建议新开一个 Trae Agent Chat，让新的规则与 Skill 一起生效。",
            "随后按 output/* 与 .super-dev/changes/*/tasks.md 推进开发。",
        ],
    }
    HOST_PRECONDITION_GUIDANCE: dict[str, list[str]] = {
        "iflow": [
            "iFlow 的模型鉴权由宿主自身管理，不由 Super Dev 接管。",
            "若宿主返回 `Invalid API key provided`，先在 iFlow 会话内执行 `/auth` 重新登录。",
            "若使用 API key 模式，更新 `IFLOW_API_KEY`，或写入 `~/.iflow/settings.json` / `./.iflow/settings.json` 后重启 iFlow 会话。",
        ],
        "codex-cli": [
            "Codex CLI 接入后必须重启 `codex`，旧会话不会自动重新加载 AGENTS.md 与宿主级 Skill。",
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
        "kimi-cli": [
            "Kimi CLI 触发前确认当前终端已进入目标项目目录，并让新的会话读取 `.kimi/AGENTS.md`。",
        ],
        "kiro": [
            "Kiro IDE 接入后建议重新打开 Agent Chat，让 steering / rules 在新会话里生效。",
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
            "OpenCode CLI 触发前确认当前终端已进入目标项目目录。",
        ],
        "claude-code": [
            "Claude Code 触发前确认当前会话就是目标项目目录下的当前会话。",
        ],
        "aider": [
            "Aider 触发前确认当前终端已进入目标项目目录，并在同一会话中加载项目上下文。",
        ],
        "cline": [
            "Cline 触发前确认当前聊天绑定的是目标工作区，并让 `.clinerules/` 已被重新加载。",
        ],
        "kilo-code": [
            "Kilo Code 触发前确认当前聊天绑定的是目标工作区，并让 `.kilocode/rules/` 已被重新加载。",
        ],
        "jetbrains-ai": [
            "JetBrains AI / Junie 触发前确认当前 IDE 已打开目标项目，并在新的 Agent 会话中加载 `.junie/AGENTS.md`。",
        ],
        "roo-code": [
            "Roo Code 触发前确认当前聊天位于目标项目工作区，并重新加载 `.roo/` 规则与命令。",
        ],
        "vscode-copilot": [
            "VS Code Copilot 触发前确认当前工作区就是目标项目，并让新的 Chat 会话读取项目级说明文件。",
        ],
    }

    TARGETS: dict[str, IntegrationTarget] = {
        "antigravity": IntegrationTarget(
            name="antigravity",
            description="Antigravity IDE 工作流 + Gemini 上下文注入",
            files=["GEMINI.md", ".agent/workflows/super-dev.md"],
        ),
        "aider": IntegrationTarget(
            name="aider",
            description="Aider CLI 约束文件注入",
            files=["AGENTS.md"],
        ),
        "claude-code": IntegrationTarget(
            name="claude-code",
            description="Claude Code CLI 深度集成",
            files=[".claude/CLAUDE.md", ".claude/agents/super-dev-core.md"],
        ),
        "cline": IntegrationTarget(
            name="cline",
            description="Cline IDE 规则注入",
            files=[".clinerules/super-dev.md"],
        ),
        "codebuddy-cli": IntegrationTarget(
            name="codebuddy-cli",
            description="CodeBuddy CLI 项目规则注入",
            files=[".codebuddy/AGENTS.md"],
        ),
        "codebuddy": IntegrationTarget(
            name="codebuddy",
            description="CodeBuddy IDE rules + agent protocol 注入",
            files=[
                ".codebuddy/rules.md",
                ".codebuddy/agents/super-dev-core.md",
                ".codebuddy/skills/super-dev-core/SKILL.md",
            ],
        ),
        "codex-cli": IntegrationTarget(
            name="codex-cli",
            description="Codex CLI 项目上下文注入",
            files=["AGENTS.md"],
        ),
        "copilot-cli": IntegrationTarget(
            name="copilot-cli",
            description="GitHub Copilot CLI 指令注入",
            files=[".github/copilot-instructions.md"],
        ),
        "cursor-cli": IntegrationTarget(
            name="cursor-cli",
            description="Cursor CLI 项目规则注入",
            files=[".cursor/rules/super-dev.mdc"],
        ),
        "windsurf": IntegrationTarget(
            name="windsurf",
            description="Windsurf IDE 规则注入",
            files=[".windsurf/rules/super-dev.md"],
        ),
        "gemini-cli": IntegrationTarget(
            name="gemini-cli",
            description="Gemini CLI 项目规则注入",
            files=["GEMINI.md"],
        ),
        "iflow": IntegrationTarget(
            name="iflow",
            description="iFlow CLI 项目规则注入",
            files=[".iflow/AGENTS.md"],
        ),
        "jetbrains-ai": IntegrationTarget(
            name="jetbrains-ai",
            description="JetBrains Junie 项目规则注入",
            files=[".junie/AGENTS.md"],
        ),
        "kilo-code": IntegrationTarget(
            name="kilo-code",
            description="Kilo Code 规则注入",
            files=[".kilocode/rules/super-dev.md"],
        ),
        "kimi-cli": IntegrationTarget(
            name="kimi-cli",
            description="Kimi CLI 项目规则注入",
            files=[".kimi/AGENTS.md"],
        ),
        "kiro-cli": IntegrationTarget(
            name="kiro-cli",
            description="Kiro CLI 项目规则注入",
            files=[".kiro/AGENTS.md"],
        ),
        "qoder-cli": IntegrationTarget(
            name="qoder-cli",
            description="Qoder CLI 项目规则注入",
            files=[".qoder/AGENTS.md"],
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
            description="OpenCode CLI 项目规则注入",
            files=[".opencode/AGENTS.md"],
        ),
        "cursor": IntegrationTarget(
            name="cursor",
            description="Cursor IDE 规则注入",
            files=[".cursor/rules/super-dev.mdc"],
        ),
        "kiro": IntegrationTarget(
            name="kiro",
            description="Kiro IDE 项目规则注入",
            files=[".kiro/AGENTS.md", ".kiro/steering/super-dev.md"],
        ),
        "qoder": IntegrationTarget(
            name="qoder",
            description="Qoder IDE 规则 + 命令注入",
            files=[".qoder/rules.md"],
        ),
        "trae": IntegrationTarget(
            name="trae",
            description="Trae IDE 项目规则 + 宿主 Skill 注入",
            files=[".trae/project_rules.md", ".trae/rules.md"],
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
        "iflow": ".iflow/commands/super-dev.toml",
        "kiro-cli": ".kiro/commands/super-dev.md",
        "opencode": ".opencode/commands/super-dev.md",
        "qoder-cli": ".qoder/commands/super-dev.md",
        "qoder": ".qoder/commands/super-dev.md",
        "roo-code": ".roo/commands/super-dev.md",
        "cursor": ".cursor/commands/super-dev.md",
    }
    GLOBAL_SLASH_COMMAND_FILES: dict[str, str] = {
        "antigravity": ".gemini/commands/super-dev.md",
        "opencode": ".config/opencode/commands/super-dev.md",
    }
    NO_SLASH_TARGETS: set[str] = {
        "aider",
        "cline",
        "codex-cli",
        "copilot-cli",
        "jetbrains-ai",
        "kilo-code",
        "kimi-cli",
        "kiro",
        "trae",
        "vscode-copilot",
    }
    OFFICIAL_DOCS_INDEX: dict[str, tuple[str, ...]] = {
        "antigravity": (
            "https://antigravity.im/documentation",
        ),
        "aider": (
            "https://aider.chat/docs/",
            "https://aider.chat/docs/config/aider_conf.html",
            "https://aider.chat/docs/usage/conventions.html",
        ),
        "claude-code": (
            "https://docs.anthropic.com/en/docs/claude-code/slash-commands",
            "https://docs.anthropic.com/en/docs/claude-code/sub-agents",
        ),
        "cline": (
            "https://docs.cline.bot/customization/cline-rules",
        ),
        "codebuddy-cli": (
            "https://www.codebuddy.ai/docs/cli/slash-commands",
            "https://www.codebuddy.ai/docs/cli/skills",
        ),
        "codebuddy": (
            "https://www.codebuddy.ai/docs/cli/ide-integrations",
            "https://www.codebuddy.ai/docs/ide/Features/Subagents",
            "https://www.codebuddy.ai/docs/cli/skills",
        ),
        "codex-cli": (
            "https://developers.openai.com/codex/cli",
            "https://developers.openai.com/codex/guides/agents-md",
            "https://developers.openai.com/codex/skills",
        ),
        "copilot-cli": (
            "https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions",
            "https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot",
        ),
        "cursor-cli": (
            "https://docs.cursor.com/en/cli/overview",
            "https://docs.cursor.com/en/cli/reference/slash-commands",
        ),
        "windsurf": (
            "https://docs.windsurf.com/plugins/cascade/workflows",
            "https://docs.windsurf.com/windsurf/cascade/memories#custom-skills",
        ),
        "gemini-cli": (
            "https://google-gemini.github.io/gemini-cli/docs/",
        ),
        "iflow": (
            "https://platform.iflow.cn/en/cli/examples/slash-commands",
            "https://platform.iflow.cn/en/cli/examples/skill",
        ),
        "jetbrains-ai": (
            "https://junie.jetbrains.com/docs/agent-skills.html",
            "https://www.jetbrains.com/help/junie/customize-guidelines.html",
        ),
        "kilo-code": (
            "https://kilocode.ai/docs/features/rules",
        ),
        "kimi-cli": (
            "https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html",
            "https://www.kimi.com/code/docs/en/kimi-cli/guides/agents.html",
        ),
        "kiro-cli": (
            "https://kiro.dev/docs/cli/",
        ),
        "opencode": (
            "https://opencode.ai/docs/commands/",
            "https://opencode.ai/docs/skills/",
        ),
        "qoder-cli": (
            "https://docs.qoder.com/cli/using-cli",
            "https://docs.qoder.com/cli/skills",
        ),
        "roo-code": (
            "https://docs.roocode.com/features/slash-commands",
            "https://docs.roocode.com/features/custom-instructions",
            "https://docs.roocode.com/features/custom-modes",
        ),
        "vscode-copilot": (
            "https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions",
            "https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot",
        ),
        "cursor": (
            "https://docs.cursor.com/en/agent/chat/commands",
        ),
        "kiro": (
            "https://kiro.dev/docs/steering/",
        ),
        "qoder": (
            "https://docs.qoder.com/user-guide/commands",
            "https://docs.qoder.com/user-guide/skills",
        ),
        "trae": (
            "https://docs.trae.ai/docs/what-is-trae-rules",
        ),
    }
    OFFICIAL_DOCS: dict[str, str] = {
        key: (values[0] if values else "")
        for key, values in OFFICIAL_DOCS_INDEX.items()
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
            "reason": "原生 slash 命令、宿主文档明确、项目规则与 slash 安装路径已做运行级适配。",
            "evidence": [
                "官方文档明确支持 slash commands",
                "Super Dev 已内置专用 slash + 规则文件接入",
                "当前项目已针对该宿主做过多轮实际验证",
            ],
        },
        "codex-cli": {
            "level": "certified",
            "reason": "已按 Codex 的真实能力改成 AGENTS.md + Skill 模式，不再误判为 slash 宿主。",
            "evidence": [
                "官方运行时明确 $CODEX_HOME/skills（默认 ~/.codex/skills）",
                "Super Dev 已为 Codex 修正成 AGENTS.md + 官方 Skills 接入路径",
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
            "reason": "官方文档明确、slash 路径可接入，但仍缺少长期真机回归矩阵。",
            "evidence": [
                "官方文档公开 slash commands",
                "Super Dev 已提供规则、Skill 与 slash 安装路径",
            ],
        },
        "cursor-cli": {
            "level": "compatible",
            "reason": "官方 CLI slash 文档明确，当前接入链路完整，但仍需更多运行级认证样本。",
            "evidence": [
                "官方文档公开 CLI slash commands",
                "Super Dev 已提供规则、Skill 与 slash 安装路径",
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
            "reason": "CLI 接入与 Kiro 生态规则一致，但仍需补更完整的长期回归样本。",
            "evidence": [
                "官方文档公开 Kiro CLI",
                "Super Dev 已提供规则、Skill 与 slash/steering 接入",
            ],
        },
        "qoder-cli": {
            "level": "compatible",
            "reason": "Qoder CLI 文档明确、接入链路完整，当前定位为稳定兼容而非已认证。",
            "evidence": [
                "官方文档公开 Qoder CLI 与 rules",
                "Super Dev 已提供规则、Skill 与 slash 安装路径",
            ],
        },
        "codebuddy": {
            "level": "experimental",
            "reason": "IDE 侧 commands + agents + skills 接入完整，但对 Agent Chat slash 的项目级行为仍缺少持续真机验证。",
            "evidence": [
                "官方文档公开 IDE integrations",
                "官方文档公开 Subagents 与 Skills",
                "Super Dev 已写入 rules、commands、agents 与 skills 接入面",
            ],
        },
        "copilot-cli": {
            "level": "experimental",
            "reason": "Copilot CLI 按 copilot-instructions + AGENTS.md 接入，当前定位为实验级。",
            "evidence": [
                "官方文档公开 copilot-instructions.md 自定义指令机制",
                "Super Dev 已写入 .github/copilot-instructions.md 接入面",
            ],
        },
        "cursor": {
            "level": "experimental",
            "reason": "IDE Agent Chat 能力可映射，但项目级 slash 行为仍需持续运行级验证。",
            "evidence": [
                "官方文档公开 Agent commands",
                "Super Dev 已写入规则、Skill 与命令映射",
            ],
        },
        "windsurf": {
            "level": "experimental",
            "reason": "当前依赖 workflow/rules 适配，交互模式可用但还未达到认证级稳定性。",
            "evidence": [
                "官方文档公开 workflows",
                "Super Dev 已写入规则与 workflow 触发文件",
            ],
        },
        "iflow": {
            "level": "experimental",
            "reason": "slash 适配已实现，但真实宿主行为与项目级命令注入仍需更多验证。",
            "evidence": [
                "官方文档公开 slash command 示例",
                "Super Dev 已写入规则、Skill 与 TOML 命令文件",
            ],
        },
        "kimi-cli": {
            "level": "experimental",
            "reason": "Kimi CLI 可稳定接入，但当前更适合 AGENTS.md / 自然语言触发，尚未确认项目级自定义 slash。",
            "evidence": [
                "官方文档公开了内置 slash 与自然语言交互方式",
                "官方文档公开了 /init 生成 AGENTS.md 的路径",
                "Super Dev 当前按 AGENTS.md + 文本触发方式接入",
            ],
        },
        "opencode": {
            "level": "experimental",
            "reason": "命令与全局配置路径已适配，但仍需要更强的运行级认证覆盖。",
            "evidence": [
                "官方文档公开 commands",
                "Super Dev 已写入规则、Skill 与项目/全局命令文件",
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
            "reason": "IDE steering 模式已对齐，但手动触发与 Agent 行为仍需更多真机验证。",
            "evidence": [
                "官方文档公开 steering",
                "Super Dev 已写入规则、Skill 与 steering 文件",
            ],
        },
        "qoder": {
            "level": "experimental",
            "reason": "官方文档明确支持项目级 commands，当前已按 Agent Chat slash + project rules 建模，但仍需要更多真机样本。",
            "evidence": [
                "官方文档公开 Commands 且支持项目级 .qoder/commands/",
                "Super Dev 已同时写入 .qoder/rules.md 与 .qoder/commands/super-dev.md",
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
            "- 当用户输入 `/super-dev ...`、`super-dev: ...` 或 `super-dev：...` 后，第一轮回复必须明确：已进入 Super Dev 流水线，而不是普通聊天。\n"
            "- 第一轮回复前，优先读取 `.super-dev/WORKFLOW.md` 与 `output/*-bootstrap.md`（若存在），把其中的初始化契约视为当前仓库的显式 bootstrap 规则。\n"
            "- 第一轮回复必须明确当前阶段是 `research`，会先读取 `knowledge/` 与 `output/knowledge-cache/*-knowledge-bundle.json`（若存在），再用宿主原生联网研究同类产品。\n"
            "- 第一轮回复必须明确后续顺序：research -> 三份核心文档 -> 等待用户确认 -> Spec / tasks -> 前端优先并运行验证 -> 后端 / 测试 / 交付。\n"
            "- 第一轮回复必须明确承诺：三份核心文档完成后会暂停并等待用户确认；未经确认不会创建 Spec，也不会开始编码。\n\n"
        )

    def _first_response_contract_en(self) -> str:
        return (
            "## First-Response Contract\n"
            "- On the first reply after `/super-dev ...`, `super-dev: ...`, or `super-dev：...`, explicitly state that Super Dev pipeline mode is now active rather than normal chat mode.\n"
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

    def get_adapter_profile(self, target: str) -> HostAdapterProfile:
        from ..catalogs import HOST_COMMAND_CANDIDATES, host_path_candidates
        from ..skills import SkillManager

        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        category = HOST_TOOL_CATEGORY_MAP.get(target, "ide")
        integration_files = list(self.TARGETS[target].files)
        slash_file = self.SLASH_COMMAND_FILES.get(target, "") if self.supports_slash(target) else ""
        skill_dir = SkillManager.TARGET_PATHS.get(target, "") if self.requires_skill(target) else ""
        docs_references = self._official_docs_references(target)
        docs_url = docs_references[0] if docs_references else ""
        docs_verified = bool(docs_references)
        adapter_mode = self._adapter_mode(target=target, category=category, integration_files=integration_files)
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
            observed_compatibility_surfaces=list(surfaces["observed_compatibility_surfaces"]),
            official_docs_references=docs_references,
            docs_check_status="declared" if docs_references else "missing",
            docs_check_summary=(
                f"declared {len(docs_references)} refs" if docs_references else "no official docs references"
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
            item.strip()
            for item in evidence
            if isinstance(item, str) and item.strip()
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
        }

    def _official_docs_references(self, target: str) -> list[str]:
        references = list(self.OFFICIAL_DOCS_INDEX.get(target, ()))
        return [item.strip() for item in references if isinstance(item, str) and item.strip()]

    def _capability_labels(self, *, target: str) -> dict[str, str]:
        slash_label = "native" if self.supports_slash(target) else "none"
        protocol = self._protocol_profile(target=target)
        mode = str(protocol.get("mode", "")).strip().lower()
        if mode in {"official-context", "official-steering"}:
            rules_label = "official"
        elif mode.startswith("official"):
            rules_label = "official"
        else:
            rules_label = "compat"
        if self.requires_skill(target):
            compatibility_skill_targets = {"cursor-cli", "cursor", "gemini-cli", "kimi-cli", "kiro-cli", "kiro", "trae"}
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

    def verify_official_docs(self, target: str, *, timeout_seconds: float = 5.0) -> dict[str, object]:
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
                    open_kwargs["context"] = ssl._create_unverified_context()
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

    def compare_official_capabilities(self, target: str, *, timeout_seconds: float = 5.0) -> dict[str, object]:
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
                "reason": "matched" if ok else ("no-reachable-docs" if not reachable else "keyword-mismatch"),
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
    def resolve_global_protocol_path(cls, target: str) -> Path | None:
        mapping = {
            "claude-code": Path.home() / ".claude" / "agents" / "super-dev-core.md",
            "codebuddy": Path.home() / ".codebuddy" / "agents" / "super-dev-core.md",
            "kiro": Path.home() / ".kiro" / "steering" / "AGENTS.md",
            "gemini-cli": Path.home() / ".gemini" / "GEMINI.md",
            "antigravity": Path.home() / ".gemini" / "GEMINI.md",
            "trae": Path.home() / ".trae" / "user_rules.md",
        }
        return mapping.get(target)

    @classmethod
    def resolve_compatibility_protocol_path(cls, target: str) -> Path | None:
        if target == "trae":
            return Path.home() / ".trae" / "rules.md"
        return None

    @classmethod
    def expected_skill_path(cls, target: str, skill_name: str = "super-dev-core") -> Path | None:
        from ..skills import SkillManager

        if not cls.requires_skill(target):
            return None
        if target not in SkillManager.TARGET_PATHS:
            return None
        return Path(SkillManager.TARGET_PATHS[target]).expanduser() / skill_name / "SKILL.md"

    @classmethod
    def contract_validation_groups(cls, target: str) -> list[tuple[str, tuple[str, ...]]]:
        trigger_group = cls.CONTRACT_TRIGGER_GROUPS["slash" if cls.supports_slash(target) else "text"]
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

        if normalized.endswith("AGENTS.md") and target == "codex-cli":
            return [trigger_group, documents_group, confirmation_group, artifacts_group, flow_group]

        if normalized.endswith("GEMINI.md"):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        if normalized.endswith("/steering/AGENTS.md") or normalized.endswith("/steering/super-dev.md"):
            return [trigger_group, documents_group, confirmation_group, flow_group]

        if normalized.endswith("/rules.md") or normalized.endswith("/project_rules.md"):
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
        for label, options in cls.contract_validation_groups_for_surface(target, surface_key, surface_path):
            if not any(option in normalized for option in options):
                missing.append(label)
        return missing

    def collect_managed_surface_paths(self, target: str, skill_name: str = "super-dev-core") -> dict[str, Path]:
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
            surfaces[f"compatibility-protocol:{compatibility_protocol_path}"] = compatibility_protocol_path

        if self.supports_slash(target):
            project_slash = self.resolve_slash_command_path(target=target, scope="project", project_dir=self.project_dir)
            if project_slash is not None:
                surfaces[f"project-slash:{project_slash}"] = project_slash
            global_slash = self.resolve_slash_command_path(target=target, scope="global")
            if global_slash is not None and global_slash != project_slash:
                surfaces[f"global-slash:{global_slash}"] = global_slash

        skill_path = self.expected_skill_path(target=target, skill_name=skill_name)
        if skill_path is not None:
            surfaces[f"skill:{skill_path}"] = skill_path

        return surfaces

    def remove(self, target: str) -> list[Path]:
        """卸载指定宿主的 Super Dev 集成文件"""
        surfaces = self.collect_managed_surface_paths(target=target)
        removed: list[Path] = []
        for _key, path in surfaces.items():
            if path.exists():
                try:
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
        if target == "jetbrains-ai":
            return "native-jetbrains-ai-prompt-config"
        return "native-ide-rule-file"

    def _usage_profile(self, *, target: str, category: str) -> dict[str, object]:
        usage_location = self.HOST_USAGE_LOCATIONS.get(target, "")
        usage_notes = list(self.HOST_USAGE_NOTES.get(target, []))
        if target == "codex-cli":
            return {
                "usage_mode": "agents-and-skill",
                "primary_entry": '在 Codex CLI 会话输入 `super-dev: <需求描述>`（由项目根 AGENTS.md + ~/.codex/skills/super-dev-core/SKILL.md 生效）',
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "trigger_context": "Codex CLI 当前会话",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重启 codex，使项目根 AGENTS.md 与 ~/.codex/skills/super-dev-core/SKILL.md 生效。",
                    "不要输入 /super-dev，在 Codex 会话里输入 `super-dev: <需求描述>`。",
                ],
                "usage_notes": usage_notes,
                "notes": "该 CLI 宿主当前不走自定义 slash，使用项目根 AGENTS.md 作为核心约束，并通过官方用户级 Skills 目录 ~/.codex/skills 安装 super-dev-core。",
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
                "primary_entry": '在 Trae Agent Chat 输入 `super-dev: <需求描述>`（由 .trae/project_rules.md + ~/.trae/user_rules.md + .trae/rules.md / ~/.trae/rules.md〔兼容规则面〕 + 兼容 Skill〔若检测到〕生效）',
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
        if target == "kimi-cli":
            return {
                "usage_mode": "agents-and-skill",
                "primary_entry": '在 Kimi CLI 会话输入 `super-dev: <需求描述>`（由 .kimi/AGENTS.md 生效；若检测到兼容 Skill 会额外增强）',
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "trigger_context": "Kimi CLI 当前会话",
                "usage_location": usage_location,
                "requires_restart_after_onboard": False,
                "post_onboard_steps": [
                    "打开 Kimi CLI，并确保当前目录就是已接入 Super Dev 的项目。",
                    "输入 `super-dev: <需求描述>` 触发完整流程。",
                    "按 output/* 与 .super-dev/changes/*/tasks.md 执行开发。",
                ],
                "usage_notes": usage_notes,
                "notes": "该宿主当前以项目级 .kimi/AGENTS.md 为核心上下文；若检测到 ~/.kimi/skills，则会增强安装 super-dev-core，但不再把 Skill 当成官方默认前提。",
            }
        if target == "kiro":
            return {
                "usage_mode": "rules-and-skill",
                "primary_entry": '在 Kiro IDE Agent Chat 输入 `super-dev: <需求描述>`（由 .kiro/steering/super-dev.md + 兼容 Skill〔若检测到〕生效）',
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "trigger_context": "Kiro IDE Agent Chat",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重新打开 Kiro，或至少新开一个 Agent Chat，使 steering、rules 与兼容 Skill（若已安装）一起生效。",
                    "确保当前项目就是已接入 Super Dev 的工作区。",
                    "输入 `super-dev: <需求描述>` 触发完整流程。",
                    "按 output/* 与 .super-dev/changes/*/tasks.md 执行开发。",
                ],
                "usage_notes": usage_notes,
                "notes": "该宿主当前走 steering/rules + compatibility skill 模式：项目级 .kiro/steering/super-dev.md 是核心约束；若检测到 ~/.kiro/skills，则会增强安装 super-dev-core。",
            }
        if self.supports_slash(target):
            if category == "cli":
                return {
                    "usage_mode": "native-slash",
                    "primary_entry": '/super-dev "<需求描述>"（在该 CLI 宿主会话内）',
                    "trigger_command": '/super-dev "<需求描述>"',
                    "trigger_context": "当前 CLI 宿主会话",
                    "usage_location": usage_location or "在项目目录启动宿主当前 CLI 会话后，直接在同一会话里触发。",
                    "requires_restart_after_onboard": False,
                    "post_onboard_steps": [
                        "保持在宿主当前会话中执行 /super-dev。",
                        "让宿主先完成同类产品研究，再继续文档与编码阶段。",
                    ],
                    "usage_notes": usage_notes or [
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
                "usage_location": usage_location or "打开宿主 IDE 的 Agent Chat，在当前项目上下文内触发。",
                "requires_restart_after_onboard": False,
                "post_onboard_steps": [
                    "在 IDE Agent Chat 中执行 /super-dev。",
                    "保持研究、文档、Spec 与编码在同一上下文中连续完成。",
                ],
                "usage_notes": usage_notes or [
                    "建议固定在项目级 Agent Chat 中完成整条流水线。",
                    "接入时还会安装宿主级 super-dev-core Skill，让宿主理解完整流水线契约。",
                ],
                "notes": "IDE 宿主优先通过 Agent Chat 触发；slash 负责触发，host skill 负责让宿主理解 Super Dev 流水线协议。",
            }
        return {
            "usage_mode": "rules-only",
            "primary_entry": "输入 `super-dev: <需求描述>`（由项目规则生效）",
            "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
            "trigger_context": "宿主当前会话",
            "usage_location": usage_location or "在宿主当前项目会话里触发。",
            "requires_restart_after_onboard": False,
            "post_onboard_steps": [
                "直接在宿主会话输入 `super-dev: <需求描述>`。",
                "按 output/* 与 tasks.md 继续执行开发流程。",
            ],
            "usage_notes": usage_notes or [
                "该宿主当前通过规则文件约束执行流程。",
            ],
            "notes": "该宿主通过项目规则文件约束执行流程。",
        }

    def _smoke_profile(self, *, target: str, category: str) -> dict[str, object]:
        trigger = self.TEXT_TRIGGER_PREFIX + " 请先不要开始编码，只回复 SMOKE_OK，并确认已读取当前项目中的 Super Dev 规则。"
        if self.supports_slash(target):
            trigger = '/super-dev "请先不要开始编码，只回复 SMOKE_OK，并确认已读取当前项目中的 Super Dev 规则。"'
        if target == "codex-cli":
            steps = [
                "完成接入后先重启 codex。",
                "进入已接入 Super Dev 的项目目录。",
                f"在 Codex 会话输入：{trigger}",
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
        usage = self._usage_profile(target=target, category=HOST_TOOL_CATEGORY_MAP.get(target, "ide"))

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

        if target == "iflow":
            project_settings = self.project_dir / ".iflow" / "settings.json"
            user_settings = Path.home() / ".iflow" / "settings.json"
            env_key = bool(os.getenv("IFLOW_API_KEY", "").strip())
            project_cfg = project_settings.exists()
            user_cfg = user_settings.exists()
            any_signal = env_key or project_cfg or user_cfg
            items.insert(
                0,
                {
                    "status": "host-auth-required",
                    "label": "已检测到鉴权配置" if any_signal else "需宿主鉴权",
                    "guidance": guidance,
                    "signals": {
                        "env_iflow_api_key": env_key,
                        "project_settings_json": project_cfg,
                        "user_settings_json": user_cfg,
                    },
                },
            )
        else:
            extra = [item for item in guidance if isinstance(item, str) and item.strip()]
            if extra:
                items[0]["guidance"] = list(dict.fromkeys([*items[0]["guidance"], *extra])) if items else extra

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
                if isinstance(guidance_item, str) and guidance_item.strip() and guidance_item not in combined_guidance:
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
                "mode": "official-subagent",
                "summary": "官方 commands + subagents",
            },
            "antigravity": {
                "mode": "official-workflow",
                "summary": "官方 commands + workflows + skills",
            },
            "codebuddy-cli": {
                "mode": "official-skill",
                "summary": "官方 commands + skills",
            },
            "codebuddy": {
                "mode": "official-subagent",
                "summary": "官方 commands + agents + skills",
            },
            "vscode-copilot": {
                "mode": "official-context",
                "summary": "官方 copilot-instructions + AGENTS",
            },
            "jetbrains-ai": {
                "mode": "official-context",
                "summary": "官方 .junie/AGENTS + agent skills",
            },
            "cline": {
                "mode": "official-context",
                "summary": "官方 .clinerules + AGENTS",
            },
            "roo-code": {
                "mode": "official-skill",
                "summary": "官方 commands + rules + modes",
            },
            "aider": {
                "mode": "official-context",
                "summary": "官方 .aider.conf + conventions/read-only context",
            },
            "qoder-cli": {
                "mode": "official-skill",
                "summary": "官方 commands + skills",
            },
            "qoder": {
                "mode": "official-skill",
                "summary": "官方 commands + rules + skills",
            },
            "windsurf": {
                "mode": "official-skill",
                "summary": "官方 workflows + skills",
            },
            "opencode": {
                "mode": "official-skill",
                "summary": "官方 commands + skills",
            },
            "iflow": {
                "mode": "official-skill",
                "summary": "官方 commands + skills",
            },
            "kilo-code": {
                "mode": "official-rules",
                "summary": "官方 rules",
            },
            "kiro": {
                "mode": "official-steering",
                "summary": "官方 project steering + global steering",
            },
            "codex-cli": {
                "mode": "official-skill",
                "summary": "官方 AGENTS.md + 官方 Skills",
            },
            "copilot-cli": {
                "mode": "official-context",
                "summary": "官方 copilot-instructions + AGENTS",
            },
            "cursor-cli": {
                "mode": "official-context",
                "summary": "官方 commands + rules",
            },
            "cursor": {
                "mode": "official-context",
                "summary": "官方 commands + rules",
            },
            "gemini-cli": {
                "mode": "official-context",
                "summary": "官方 commands + GEMINI.md",
            },
            "kimi-cli": {
                "mode": "official-context",
                "summary": "官方 AGENTS.md + 文本触发",
            },
            "kiro-cli": {
                "mode": "official-context",
                "summary": "官方 commands + AGENTS.md",
            },
            "trae": {
                "mode": "compatibility-skill",
                "summary": "官方 rules + 兼容 Skill",
            },
        }
        return mapping.get(target, {"mode": "none", "summary": ""})

    def _install_surfaces(self, *, target: str) -> dict[str, list[str]]:
        by_target: dict[str, dict[str, list[str]]] = {
            "claude-code": {
                "official_project_surfaces": [
                    ".claude/CLAUDE.md",
                    ".claude/commands/super-dev.md",
                    ".claude/agents/super-dev-core.md",
                ],
                "official_user_surfaces": ["~/.claude/agents/super-dev-core.md"],
                "observed_compatibility_surfaces": [],
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
                    ".codebuddy/AGENTS.md",
                    ".codebuddy/commands/super-dev.md",
                    ".codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.codebuddy/commands/super-dev.md",
                    "~/.codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "codebuddy": {
                "official_project_surfaces": [
                    ".codebuddy/rules.md",
                    ".codebuddy/commands/super-dev.md",
                    ".codebuddy/agents/super-dev-core.md",
                    ".codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.codebuddy/commands/super-dev.md",
                    "~/.codebuddy/agents/super-dev-core.md",
                    "~/.codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "vscode-copilot": {
                "official_project_surfaces": [
                    ".github/copilot-instructions.md",
                    "AGENTS.md",
                ],
                "official_user_surfaces": ["~/.copilot/copilot-instructions.md"],
                "observed_compatibility_surfaces": [],
            },
            "jetbrains-ai": {
                "official_project_surfaces": [
                    ".junie/AGENTS.md",
                    ".junie/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": ["~/.junie/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": [],
            },
            "cline": {
                "official_project_surfaces": [".clinerules/super-dev.md", "AGENTS.md"],
                "official_user_surfaces": ["~/Documents/Cline/Rules/super-dev.md"],
                "observed_compatibility_surfaces": [],
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
                "official_user_surfaces": ["~/.roo/rules/super-dev.md", "~/.roo/commands/super-dev.md"],
                "observed_compatibility_surfaces": [],
            },
            "aider": {
                "official_project_surfaces": ["AGENTS.md", ".aider.conf.yml"],
                "official_user_surfaces": ["~/.aider.conf.yml"],
                "observed_compatibility_surfaces": [],
            },
            "codex-cli": {
                "official_project_surfaces": ["AGENTS.md"],
                "official_user_surfaces": ["~/.codex/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": [],
            },
            "copilot-cli": {
                "official_project_surfaces": [
                    ".github/copilot-instructions.md",
                    "AGENTS.md",
                ],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": [],
            },
            "cursor-cli": {
                "official_project_surfaces": [".cursor/rules/super-dev.mdc", ".cursor/commands/super-dev.md"],
                "official_user_surfaces": ["~/.cursor/commands/super-dev.md"],
                "observed_compatibility_surfaces": ["~/.cursor/skills/super-dev-core/SKILL.md"],
            },
            "cursor": {
                "official_project_surfaces": [".cursor/rules/super-dev.mdc", ".cursor/commands/super-dev.md"],
                "official_user_surfaces": ["~/.cursor/commands/super-dev.md"],
                "observed_compatibility_surfaces": ["~/.cursor/skills/super-dev-core/SKILL.md"],
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
                "official_user_surfaces": ["~/.gemini/GEMINI.md"],
                "observed_compatibility_surfaces": ["~/.gemini/skills/super-dev-core/SKILL.md"],
            },
            "iflow": {
                "official_project_surfaces": [
                    ".iflow/AGENTS.md",
                    ".iflow/commands/super-dev.toml",
                    ".iflow/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": ["~/.iflow/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": [],
            },
            "kimi-cli": {
                "official_project_surfaces": [".kimi/AGENTS.md"],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": ["~/.kimi/skills/super-dev-core/SKILL.md"],
            },
            "kiro-cli": {
                "official_project_surfaces": [".kiro/AGENTS.md", ".kiro/commands/super-dev.md"],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": ["~/.kiro/skills/super-dev-core/SKILL.md"],
            },
            "kiro": {
                "official_project_surfaces": [".kiro/AGENTS.md", ".kiro/steering/super-dev.md"],
                "official_user_surfaces": ["~/.kiro/steering/AGENTS.md"],
                "observed_compatibility_surfaces": ["~/.kiro/skills/super-dev-core/SKILL.md"],
            },
            "opencode": {
                "official_project_surfaces": [
                    ".opencode/AGENTS.md",
                    ".opencode/commands/super-dev.md",
                    ".opencode/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.config/opencode/commands/super-dev.md",
                    "~/.config/opencode/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "qoder-cli": {
                "official_project_surfaces": [
                    ".qoder/AGENTS.md",
                    ".qoder/commands/super-dev.md",
                    ".qoder/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.qoder/commands/super-dev.md",
                    "~/.qoder/skills/super-dev-core/SKILL.md",
                ],
                "observed_compatibility_surfaces": [],
            },
            "qoder": {
                "official_project_surfaces": [
                    ".qoder/rules.md",
                    ".qoder/commands/super-dev.md",
                    ".qoder/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": [
                    "~/.qoder/commands/super-dev.md",
                    "~/.qoderwork/skills/super-dev-core/SKILL.md",
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
        }
        return by_target.get(
            target,
            {
                "official_project_surfaces": [],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": [],
            },
        )

    def setup(self, target: str, force: bool = False) -> list[Path]:
        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        written_files: list[Path] = []
        integration = self.TARGETS[target]
        for relative in integration.files:
            file_path = self.project_dir / relative
            if target == "codex-cli" and relative == "AGENTS.md":
                block_content = self._append_flow_contract(
                    content=self._build_file_content(target=target, relative=relative),
                    relative=relative,
                )
                updated = self._upsert_managed_block(
                    file_path=file_path,
                    begin=self.CODEX_AGENTS_BEGIN,
                    end=self.CODEX_AGENTS_END,
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

        return written_files

    def setup_global_protocol(self, target: str, force: bool = False) -> Path | None:
        protocol_file = self.resolve_global_protocol_path(target)

        if target == "claude-code" and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_claude_agent_content(),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target == "codebuddy" and protocol_file is not None:
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(
                self._append_flow_contract(
                    content=self._build_codebuddy_agent_content(),
                    relative=protocol_file.as_posix(),
                ),
                encoding="utf-8",
            )
            return protocol_file

        if target == "kiro" and protocol_file is not None:
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

    def _build_kiro_global_steering_content(self) -> str:
        return (
            "# Super Dev Global Steering\n\n"
            "This global steering file activates Super Dev governance for Kiro workspaces that opt into the pipeline.\n\n"
            "## Activation\n"
            "- When the user types `super-dev: ...`, enter the Super Dev workflow immediately.\n"
            "- Treat project-local `.kiro/steering/super-dev.md` as the project-specific source of truth.\n\n"
            "## Required Sequence\n"
            "1. Research first\n"
            "2. Draft PRD, architecture, and UIUX\n"
            "3. Stop for user confirmation\n"
            "4. Create Spec/tasks only after confirmation\n"
            "5. Frontend runtime verification before backend and delivery\n\n"
            "## Boundary\n"
            "- Kiro remains the execution host.\n"
            "- Super Dev is the governance layer and local Python tooling, not a separate model platform.\n"
        )

    def setup_all(self, force: bool = False) -> dict[str, list[Path]]:
        result: dict[str, list[Path]] = {}
        for target in self.TARGETS:
            result[target] = self.setup(target=target, force=force)
        return result

    def _upsert_managed_block(
        self,
        *,
        file_path: Path,
        begin: str,
        end: str,
        block_content: str,
    ) -> bool:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        existing = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        managed = f"{begin}\n{block_content.rstrip()}\n{end}\n"
        if begin in existing and end in existing:
            start = existing.index(begin)
            stop = existing.index(end, start) + len(end)
            updated = f"{existing[:start]}{managed}{existing[stop:]}"
        elif existing.strip():
            spacer = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
            updated = f"{existing}{spacer}{managed}"
        else:
            updated = managed
        if updated == existing:
            return False
        file_path.write_text(updated, encoding="utf-8")
        return True

    def setup_slash_command(self, target: str, force: bool = False) -> Path | None:
        return self.setup_slash_command_for_scope(target=target, force=force, scope="project")

    def setup_global_slash_command(self, target: str, force: bool = False) -> Path | None:
        return self.setup_slash_command_for_scope(target=target, force=force, scope="global")

    def setup_slash_command_for_scope(self, target: str, force: bool = False, scope: str = "project") -> Path | None:
        if not self.supports_slash(target):
            return None
        command_file = self.resolve_slash_command_path(
            target=target,
            scope=scope,
            project_dir=self.project_dir,
        )
        if command_file.exists() and not force:
            return None
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_content = self._append_flow_contract(
            content=self._build_slash_command_content(target),
            relative=command_file.name,
        )
        command_file.write_text(command_content, encoding="utf-8")
        return command_file

    @classmethod
    def resolve_slash_command_path(
        cls,
        *,
        target: str,
        scope: str,
        project_dir: Path | None = None,
    ) -> Path:
        if not cls.supports_slash(target):
            raise ValueError(f"Unsupported target: {target}")

        if scope == "project":
            if project_dir is None:
                raise ValueError("project_dir is required when scope='project'")
            relative = cls.SLASH_COMMAND_FILES[target]
            return Path(project_dir).resolve() / relative

        if scope == "global":
            relative = cls.GLOBAL_SLASH_COMMAND_FILES.get(target, cls.SLASH_COMMAND_FILES[target])
            return Path.home() / relative

        raise ValueError(f"Unsupported slash scope: {scope}")

    @classmethod
    def supports_slash(cls, target: str) -> bool:
        return target in cls.SLASH_COMMAND_FILES and target not in cls.NO_SLASH_TARGETS

    @classmethod
    def requires_skill(cls, target: str) -> bool:
        return target not in cls.NO_SKILL_TARGETS

    def setup_all_slash_commands(self, force: bool = False) -> dict[str, Path | None]:
        result: dict[str, Path | None] = {}
        for target in self.TARGETS:
            result[target] = self.setup_slash_command(target=target, force=force)
        return result

    def _build_content(self, target: str) -> str:
        return self._build_file_content(target=target, relative="")

    def _build_file_content(self, target: str, relative: str) -> str:
        if target == "codex-cli" and relative == "AGENTS.md":
            return self._build_codex_agents_content()

        if target == "claude-code" and relative.endswith(".claude/agents/super-dev-core.md"):
            return self._build_claude_agent_content()

        if target == "codebuddy" and relative.endswith(".codebuddy/agents/super-dev-core.md"):
            return self._build_codebuddy_agent_content()

        if target == "trae":
            return self._trae_rules()

        if relative.endswith("/skills/super-dev-core/SKILL.md"):
            return self._build_embedded_skill_content()

        if target in {"cursor", "cursor-cli"}:
            rules_body = (
                "# Super Dev Pipeline Rules\n"
                "- When the user triggers `/super-dev ...`, enter Super Dev pipeline mode immediately.\n"
                "- Start with research and write output/*-research.md as a real file in the repository.\n"
                "- Always read and maintain output/*-prd.md, output/*-architecture.md, and output/*-uiux.md as source-of-truth project files.\n"
                "- Summarize the three core documents to the user and wait for user confirmation before creating Spec/tasks or writing code.\n"
                "- Create Spec/tasks only after confirmation.\n"
                "- Execute frontend-first delivery before backend/database tasks, then run quality gate before release.\n"
            )
            cursor_template = self.templates_dir / ".cursorrules.template"
            if cursor_template.exists():
                body = cursor_template.read_text(encoding="utf-8")
                rules_body = f"{body}\n\n{rules_body}"
            return (
                "---\n"
                'description: "Super Dev pipeline governance - research-first commercial-grade delivery. Activates when user says /super-dev or super-dev:"\n'
                "alwaysApply: true\n"
                "---\n\n"
                f"{rules_body}"
            )

        if target == "kiro" and relative.endswith("steering/super-dev.md"):
            frontmatter = (
                "---\n"
                "inclusion: always\n"
                "name: super-dev\n"
                "description: Super Dev pipeline governance for research-first commercial-grade delivery\n"
                "---\n\n"
            )
            return frontmatter + self._generic_ide_rules(target)

        if target == "antigravity":
            if relative.endswith(".agent/workflows/super-dev.md"):
                return self._antigravity_workflow_rules()
            return self._build_antigravity_context_content()

        if target in {
            "cursor",
            "windsurf",
            "cline",
            "continue",
            "vscode-copilot",
            "jetbrains-ai",
            "kilo-code",
            "roo-code",
            "augment",
            "qoder",
            "kiro",
            "trae",
            "codebuddy",
            "tongyi-lingma",
            "codegeex",
        }:
            return self._generic_ide_rules(target)

        if target in {
            "codex-cli",
            "copilot-cli",
            "opencode",
            "gemini-cli",
            "kiro-cli",
            "cursor-cli",
            "qoder-cli",
            "codebuddy-cli",
            "iflow",
            "aider",
        }:
            return self._generic_cli_rules(target)

        if target == "claude-code":
            return self._claude_rules()

        return self._generic_cli_rules(target)

    def _build_codex_agents_content(self) -> str:
        return (
            "# Super Dev for Codex CLI\n\n"
            "When a user message starts with `super-dev:` or `super-dev：`, enter Super Dev pipeline mode immediately.\n\n"
            "## Required execution\n"
            "1. First reply: state that Super Dev pipeline mode is active and the current phase is `research`.\n"
            "2. Read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` when available.\n"
            "3. Use Codex native web/search/edit/terminal capabilities to perform similar-product research and write `output/*-research.md` into the repository workspace.\n"
            "4. Draft `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` in the same Codex session and save them as actual project files.\n"
            "5. Stop after the three core documents, summarize them, and wait for explicit confirmation.\n"
            "6. Only after confirmation, create `.super-dev/changes/*/proposal.md` and `.super-dev/changes/*/tasks.md`, then continue with frontend-first implementation.\n\n"
            "## Constraints\n"
            "- Do not start coding directly after `super-dev:` or `super-dev：`.\n"
            "- Do not create Spec before document confirmation.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign Spec/tasks and implementation.\n"
            "- If the user requests quality or security remediation, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue.\n"
            "- If a required artifact is only described in chat and not written into the repository, treat the step as incomplete.\n"
            "- Codex remains the execution host; Super Dev is the local governance workflow.\n"
            "- Use local `super-dev` CLI only for governance actions such as doctor, review, quality, release readiness, or update; do not outsource the main coding workflow to the CLI.\n\n"
            "## Super Dev System Flow Contract\n"
            "- SUPER_DEV_FLOW_CONTRACT_V1\n"
            "- PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery\n"
            "- DOC_CONFIRM_GATE: required\n"
            "- PREVIEW_CONFIRM_GATE: required\n"
            "- HOST_PARITY: required\n"
        )

    def _build_claude_agent_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: Activate the Super Dev pipeline for research-first, commercial-grade project delivery. Use when user says /super-dev or super-dev: followed by a requirement.\n"
            "model: inherit\n"
            "---\n"
            "# Super Dev Core Subagent\n\n"
            "You are the Claude Code subagent that activates Super Dev governance mode.\n\n"
            "## Purpose\n"
            "- Treat `/super-dev ...` as the entry point into the Super Dev pipeline.\n"
            "- Enforce the sequence: research -> three core docs -> wait for confirmation -> Spec/tasks -> frontend runtime verification -> backend/tests/delivery.\n"
            "- Use the local Python `super-dev` CLI for governance artifacts, checks, and delivery reports.\n"
            "- Use the host's native tools for browsing, coding, terminal execution, and debugging.\n\n"
            "## First Response Contract\n"
            "- On the first reply after `/super-dev ...`, explicitly say Super Dev pipeline mode is active.\n"
            "- Explicitly say the current phase is `research`.\n"
            "- Explicitly state that you will read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` first when present.\n"
            "- Explicitly promise that you will stop after PRD, architecture, and UIUX for user confirmation before creating Spec or writing code.\n\n"
            "## Artifact Contract\n"
            "- Write `output/*-research.md`, `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` as workspace files.\n"
            "- chat-only summaries do not count as completion.\n"
            "- If a required artifact is missing from the workspace, keep working until it is written.\n\n"
            "## Revision Contract\n"
            "- If the user requests UI changes, first update `output/*-uiux.md`, then redo the frontend and rerun frontend runtime plus UI review.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign Spec/tasks and implementation.\n"
            "- If the user requests quality or security remediation, fix the issues first and rerun quality gate plus `super-dev release proof-pack` before continuing.\n\n"
            "## Boundary\n"
            "- Claude Code remains the execution host.\n"
            "- Super Dev is the governance layer, not a separate model platform.\n"
            "- Prefer repository-local rules and commands as the source of project-specific context.\n"
        )

    def _build_codebuddy_agent_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: CodeBuddy subagent that activates the Super Dev pipeline for research-first, commercial-grade delivery.\n"
            "---\n"
            "# Super Dev Core Agent\n\n"
            "You are the CodeBuddy agent that activates Super Dev governance mode.\n\n"
            "## Purpose\n"
            "- Treat `/super-dev ...` as the entry point into the Super Dev pipeline.\n"
            "- Enforce the sequence: research -> three core docs -> wait for confirmation -> Spec/tasks -> frontend runtime verification -> backend/tests/delivery.\n"
            "- Use the local Python `super-dev` CLI for governance artifacts, checks, and delivery reports.\n"
            "- Use CodeBuddy native tools for browsing, coding, terminal execution, and debugging.\n\n"
            "## First Response Contract\n"
            "- On the first reply after `/super-dev ...`, explicitly say Super Dev pipeline mode is active.\n"
            "- Explicitly say the current phase is `research`.\n"
            "- Explicitly state that you will read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` first when present.\n"
            "- Explicitly promise that you will stop after PRD, architecture, and UIUX for user confirmation before creating Spec or writing code.\n\n"
            "## Artifact Contract\n"
            "- Write `output/*-research.md`, `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` as real workspace files.\n"
            "- Do not treat chat-only explanations as completed deliverables.\n"
            "- If a required artifact is not present in the repository, continue until it is written.\n\n"
            "## Revision Contract\n"
            "- If the user requests UI changes, first update `output/*-uiux.md`, then redo the frontend and rerun frontend runtime plus UI review.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign Spec/tasks and implementation.\n"
            "- If the user requests quality or security remediation, fix the issues first and rerun quality gate plus `super-dev release proof-pack` before continuing.\n\n"
            "## Boundary\n"
            "- CodeBuddy remains the execution host.\n"
            "- Super Dev is the governance layer, not a separate model platform.\n"
            "- Prefer repository-local rules, commands, and this agent file as the source of project-specific context.\n"
        )

    def _build_embedded_skill_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: Super Dev pipeline governance for research-first, commercial-grade AI coding delivery\n"
            "---\n"
            "# super-dev-core - Super Dev AI Coding Skill\n\n"
            "## 定位边界（强制）\n"
            "- 当前宿主负责调用模型、工具、终端与实际代码修改。\n"
            "- Super Dev 不是大模型平台，也不提供自己的代码生成 API。\n"
            "- 你的职责是利用宿主现有能力，严格执行 Super Dev 的流程规范、设计约束、质量门禁与交付标准。\n\n"
            "## 触发方式（强制）\n"
            "- 支持 slash 的宿主：`/super-dev <需求描述>`。\n"
            "- 非 slash 宿主：`super-dev: <需求描述>` 与 `super-dev：<需求描述>` 等效。\n\n"
            "## 首轮响应契约（强制）\n"
            "- 第一轮回复必须明确说明当前阶段是 `research`。\n"
            "- 第一轮回复必须说明会先读取 `knowledge/` 与 `output/knowledge-cache/*-knowledge-bundle.json`。\n"
            "- 三份核心文档完成后会暂停等待用户确认；未经确认不得创建 `.super-dev/changes/*` 或开始编码。\n\n"
            "## 本地知识库契约（强制）\n"
            "- 先读 `knowledge/`。\n"
            "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取并把命中的本地知识带入三文档、Spec 与实现。\n"
            "- research、PRD、架构、UIUX、Spec、质量报告等要求中的产物，必须真实写入项目文件，不能只在聊天里口头描述。\n"
            "- 用户要求 UI 改版时，先更新 `output/*-uiux.md`，再重做前端并重新执行 frontend runtime 与 UI review。\n"
            "- 用户要求架构返工时，先更新 `output/*-architecture.md`，再同步调整 Spec / tasks 与实现方案。\n"
            "- 用户要求质量整改时，先修复问题，再重新执行 quality gate 与 `super-dev release proof-pack`。\n"
        )

    def _build_slash_command_content(self, target: str) -> str:
        if target == "iflow":
            return (
                'description = "Super Dev 流水线式开发编排（先文档/Spec，再编码）"\n'
                "prompt = \"\"\"\n"
                "你正在执行 /super-dev。\n"
                "需求描述: {{args}}\n\n"
                "定位边界：宿主负责调用自身模型、工具与实际编码；Super Dev 负责流程规范、质量门禁、审计产物与交付标准。\n\n"
                "本地知识库要求：\n"
                "- 进入流水线后，先阅读当前项目 `knowledge/` 中与需求相关的知识文件\n"
                "- 若已生成 `output/knowledge-cache/*-knowledge-bundle.json`，必须读取其中命中的 `local_knowledge` 与 `research_summary`\n"
                "- 本地知识库命中的规范、检查清单、反模式与场景包默认视为项目硬约束\n\n"
                "严格执行顺序（不可跳步）：\n"
                "1. 先使用宿主原生联网/搜索能力研究同类产品，沉淀 output/*-research.md\n"
                "2. 再生成 output/*-prd.md、output/*-architecture.md、output/*-uiux.md\n"
                "3. 三份核心文档完成后，必须先向用户汇报并等待确认；用户未确认前禁止创建 Spec 或开始编码\n"
                "4. 用户确认后，再创建 .super-dev/changes/*/proposal.md 与 tasks.md\n"
                "5. 先实现并运行前端，再进入后端、联调、测试与交付\n\n"
                "研究要求：\n"
                "- 至少总结 3-5 个相似产品或可借鉴对象\n"
                "- 总结共性功能、关键流程、信息架构、交互模式、差异化机会\n"
                "- 未完成 research 阶段前不得直接编码\n\n"
                "执行命令：\n"
                "super-dev create \\\"{{args}}\\\"\n"
                "super-dev spec list\n\n"
                "UI 强制规则：\n"
                "- 禁止紫/粉渐变主视觉（除非品牌明确要求）\n"
                "- 禁止 emoji 充当功能图标\n"
                "- 禁止模板化、同质化页面直出\n"
                "- 必须在编码前先确定字体系统、颜色 token、栅格和状态矩阵\n"
                "\"\"\"\n"
            )

        if target == "windsurf":
            return (
                "---\n"
                "description: Super Dev 流水线式开发编排（先文档/Spec，再编码）\n"
                "---\n\n"
                "# /super-dev (windsurf)\n\n"
                "在当前项目触发 Super Dev 流水线。\n\n"
                "## 输入\n"
                "- 需求描述: `$ARGUMENTS`\n\n"
                "## 定位边界\n"
                "- 宿主负责调用自身模型、工具与实际编码。\n"
                "- Super Dev 负责流程规范、质量门禁、审计产物与交付标准。\n\n"
                "## 本地知识库要求\n"
                "- 先读取当前项目 `knowledge/` 下与需求相关的知识文件。\n"
                "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取其中的 `local_knowledge`、`web_knowledge` 与 `research_summary`。\n"
                "- 命中的本地知识应被继承到 PRD / 架构 / UIUX / Spec，而不是只停留在 research 文档。\n\n"
                "## 强制执行顺序\n"
                "1. 先使用宿主原生联网 / browse / search 研究同类产品，沉淀 `output/*-research.md`\n"
                "2. 再生成 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`\n"
                "3. 三份文档完成后，先向用户汇报文档摘要与路径，等待明确确认；未经确认不得创建 Spec 或开始编码\n"
                "4. 用户确认后，再生成 `.super-dev/changes/*/proposal.md` 与 `tasks.md`\n"
                "5. 先实现并运行前端，再进入后端、联调、测试与交付\n\n"
                "## 研究要求\n"
                "- 至少研究 3 到 5 个可借鉴产品\n"
                "- 总结共性功能、关键交互、信息架构、商业表达与差异化方向\n"
                "- 未完成 research 阶段前不得直接进入编码\n\n"
                "## 执行命令\n"
                "```bash\n"
                "super-dev create \"$ARGUMENTS\"\n"
                "super-dev spec list\n"
                "```\n"
            )

        if target == "kiro":
            return (
                "---\n"
                "inclusion: manual\n"
                "---\n\n"
                "# super-dev\n\n"
                "在 Kiro 手动触发 `/super-dev` 时执行以下流程：\n\n"
                "定位边界：宿主负责编码与工具调用，Super Dev 负责流程和质量治理。\n\n"
                "本地知识库要求：\n"
                "- 先读取当前项目 `knowledge/` 下与需求相关的知识文件\n"
                "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取其中命中的本地知识与研究摘要\n"
                "- 命中的规范、清单、反模式默认视为项目硬约束\n\n"
                "1. 先使用宿主原生联网 / browse / search 研究同类产品，沉淀 `output/*-research.md`\n"
                "2. 再生成 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`\n"
                "3. 三份文档完成后，先停下来向用户汇报并等待确认；未经确认不得创建 Spec 或开始编码\n"
                "4. 用户确认后，再创建 `.super-dev/changes/*/proposal.md` 与 `tasks.md`\n"
                "5. 先实现并运行前端，再进入后端、联调、测试与交付\n\n"
                "研究阶段至少输出：同类产品名单、共性功能、关键页面结构、交互模式、差异化建议。\n\n"
                "执行命令：\n"
                "```bash\n"
                "super-dev create \"$ARGUMENTS\"\n"
                "super-dev spec list\n"
                "```\n"
            )

        return (
            f"# /super-dev ({target})\n\n"
            "在当前项目触发 Super Dev 的流水线式开发编排。\n\n"
            "## 输入\n"
            "- 需求描述: `$ARGUMENTS`\n"
            "- 如果未提供参数，先要求用户补全需求后再执行。\n\n"
            "## Super Dev Runtime Contract\n"
            "- Super Dev 是当前项目里的本地 Python 工具 + 宿主规则/Skill 协议，不是独立模型平台。\n"
            "- 宿主负责推理、联网、编码、运行终端与修改文件。\n"
            "- 当用户触发 `/super-dev` 时，你要把它视为“进入 Super Dev 流水线”，而不是普通聊天命令。\n"
            "- 需要生成文档、Spec、质量报告、交付产物时，优先调用本地 `super-dev` CLI。\n"
            "- 需要研究、设计、编码、运行、修复时，优先使用宿主自身的 browse/search/terminal/edit 能力。\n\n"
            "## Local Knowledge Contract\n"
            "- 优先读取当前项目 `knowledge/` 目录里与需求相关的知识文件。\n"
            "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须读取其中命中的 `local_knowledge`、`web_knowledge` 与 `research_summary`。\n"
            "- 本地知识命中的规范、检查清单、反模式、场景包默认是当前项目的硬约束，后续三文档、Spec 与实现都要继承。\n\n"
            f"{self._first_response_contract_zh()}"
            "## 强制执行顺序（不可跳步）\n"
            "1. 先使用宿主原生联网 / browse / search 能力研究同类产品，并先产出：\n"
            "   - `output/*-research.md`\n"
            "   - 至少包含 3-5 个对标产品、共性功能、关键流程、信息架构、交互模式、差异化方向\n"
            "2. 再生成三份核心文档，再进入编码阶段：\n"
            "   - `output/*-prd.md`\n"
            "   - `output/*-architecture.md`\n"
            "   - `output/*-uiux.md`\n"
            "3. 三份核心文档完成后，必须先暂停并向用户汇报文档路径、摘要与待确认事项；未经用户明确确认，不得进入 Spec 或编码。\n"
            "4. 用户确认后，再创建 Spec 变更与任务清单：\n"
            "   - `.super-dev/changes/*/proposal.md`\n"
            "   - `.super-dev/changes/*/tasks.md`\n"
            "5. 先按 `tasks.md` 实现并运行前端，确保前端可演示、可审查、无明显错误。\n"
            "6. 再实现后端、联调、测试、质量门禁与可审计交付清单。\n\n"
            "## 执行命令（优先）\n"
            "```bash\n"
            "super-dev create \"$ARGUMENTS\"\n"
            "super-dev spec list\n"
            "```\n\n"
            "## 实现阶段要求\n"
            "- 如果宿主具备联网能力，必须优先在宿主中完成同类产品研究，不能跳过 research 阶段直接编码。\n"
            "- 研究结论必须回填到 `output/*-research.md`，并用于约束 PRD / 架构 / UIUX。\n"
            "- 编码前必须先读取 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`，并完成用户确认门。\n"
            "- 如果用户要求修改文档，只允许回到文档阶段修订，不能绕过确认门直接建 Spec 或开工。\n"
            "- UI 必须遵循 UI/UX 文档，禁止直接输出模板化、同质化页面。\n"
            "- 禁止使用“AI 感”设计：紫/粉渐变主视觉、emoji 充当功能图标、默认系统字体直出。\n"
            "- 编码前必须先明确视觉方向、字体系统、颜色 token、间距 token、栅格系统、组件状态矩阵。\n"
            "- 页面必须提供可访问交互：可见 `focus` 态、合理 hover/active、兼容 reduced-motion。\n"
            "- 严禁在三文档与 Spec 缺失时直接宣称“已完成”。\n\n"
            "## 汇报格式（每次回复都要包含）\n"
            "- 当前阶段（文档 / Spec / 实现 / 质量 / 交付）\n"
            "- 本次变更文件路径\n"
            "- 下一步动作\n\n"
            "## 说明\n"
            "- 宿主负责调用自身模型、工具与实际编码；Super Dev 只提供治理协议。\n"
            "- Super Dev 不提供模型能力；编码能力来自当前宿主。\n"
            "- 在宿主会话中执行本流程，确保上下文连续与结果可审计。\n"
        )

    def _generic_cli_rules(self, target: str) -> str:
        if self.supports_slash(target):
            trigger_lines = (
                "## Trigger\n"
                '- Preferred: `/super-dev "<需求描述>"`\n'
                '- Terminal entry (local orchestration only): `super-dev "<需求描述>"`\n'
                "- Terminal entry does not directly talk to the host model session.\n\n"
            )
        else:
            trigger_lines = (
                "## Trigger\n"
                '- Preferred: say `super-dev: <需求描述>` or `super-dev：<需求描述>` in the host chat so AGENTS.md + super-dev-core Skill can govern the workflow.\n'
                '- Local orchestration fallback: `super-dev "<需求描述>"`\n'
                "- Do not rely on `/super-dev` in this host.\n\n"
            )
        return (
            f"# Super Dev Integration for {target}\n\n"
            "Super Dev 是“超级开发战队”，一个流水线式 AI Coding 辅助工具。\n"
            "Super Dev does not provide model inference or coding APIs.\n"
            "The host remains responsible for model execution, tools, and actual code generation.\n"
            "Use the host model/runtime as-is; Super Dev only enforces the delivery protocol.\n"
            "Use Super Dev generated artifacts as source of truth.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as a local Python CLI plus host-side rules/skills, not as a separate model provider.\n"
            "- When the user triggers Super Dev, enter the protocol immediately instead of treating it as normal chat.\n"
            "- Use host-native web/search/browse for research and host-native editing/execution for implementation.\n"
            "- Use local `super-dev` commands to generate/update documents, spec artifacts, quality reports, and delivery outputs.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read its `local_knowledge`, `web_knowledge`, and `research_summary` first.\n"
            "- Treat matched local knowledge, checklists, anti-patterns, and scenario packs as project constraints that must flow into docs, spec, and implementation.\n\n"
            f"{trigger_lines}"
            "## Required Context\n"
            "- output/*-prd.md\n"
            "- output/*-architecture.md\n"
            "- output/*-uiux.md\n"
            "- output/*-execution-plan.md\n"
            "- .super-dev/changes/*/tasks.md\n\n"
            "## Execution Order\n"
            "1. Use the host's native browse/search/web capability to research similar products first and produce output/*-research.md as a real repository file\n"
            "2. Freeze PRD, architecture and UIUX documents and write them into output/* files rather than only describing them in chat\n"
            "3. Stop after the three core documents, summarize them to the user, and wait for explicit confirmation before creating Spec or coding\n"
            "4. Create Spec proposal/tasks only after the user confirms the documents\n"
            "5. Implement and run the frontend first so it becomes demonstrable before backend-heavy work\n"
            "6. Implement backend APIs and data layer, then run tests, quality gate, and release preparation\n"
            "7. If the user says the UI is unsatisfactory, asks for a redesign, or says the page looks AI-generated, first update `output/*-uiux.md`, then redo frontend implementation, rerun frontend runtime and UI review, and only then continue.\n"
            "8. If the user says the architecture is wrong or the technical plan must change, first update `output/*-architecture.md`, then realign tasks and implementation before continuing.\n"
            "9. If the user says quality or security is not acceptable, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue.\n"
        )

    def _generic_ide_rules(self, target: str) -> str:
        windsurf_frontmatter = ""
        if target == "windsurf":
            windsurf_frontmatter = (
                "---\n"
                "trigger: always_on\n"
                "---\n\n"
            )
        return (
            f"{windsurf_frontmatter}"
            f"# Super Dev IDE Rules ({target})\n\n"
            "## Positioning\n"
            "- Super Dev is a host-level workflow governor, not an LLM platform.\n"
            "- Keep using the host's model capabilities; do not expect extra model APIs from Super Dev.\n"
            "- The host remains responsible for actual coding, tool execution, and file changes.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus this host rule file, not as a separate coding engine.\n"
            "- When the user says `/super-dev ...`, `super-dev: ...`, or `super-dev：...`, immediately enter the Super Dev pipeline.\n"
            "- Use host-native browse/search/web for research and host-native editing/terminal for implementation.\n"
            "- Use local `super-dev` commands when you need to generate or refresh documents, spec artifacts, quality reports, or delivery manifests.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting the three core documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and inherit its matched local knowledge into PRD, architecture, UIUX, Spec, and execution.\n"
            "- Treat local knowledge hits as hard project constraints, especially for standards, anti-patterns, checklists, and scenario packs.\n\n"
            "## Working Agreement\n"
            "- If the host supports browse/search/web, research similar products first and write the findings into output/*-research.md.\n"
            "- Generate PRD, architecture and UIUX documents before coding, write them into output/* files, then pause and ask the user to confirm the three documents.\n"
            "- If the user requests revisions, update the documents first and ask again; do not create Spec or code before confirmation.\n"
            "- If the user requests a UI redesign or says the UI is unsatisfactory, first update `output/*-uiux.md`, then redo the frontend, and rerun frontend runtime + UI review before continuing.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign tasks and implementation before continuing.\n"
            "- If the user requests quality or security remediation, first fix the issues, rerun quality gate plus `super-dev release proof-pack`, and only then continue.\n"
            "- Respect Spec tasks sequence.\n"
            "- Implement and run the frontend before moving into backend-heavy work.\n"
            "- Keep architecture and UIUX consistency.\n\n"
            "## Delivery Criteria\n"
            "- Frontend can be demonstrated early.\n"
            "- Backend and migration scripts match specs.\n"
            "- Security/performance checks are resolved.\n"
            "- Quality gate threshold is met for the current scenario.\n"
            "- UI must avoid AI-looking output (purple/pink gradient-first theme, emoji as icons, default-font-only pages).\n"
            "- UI must define typography, tokens, grid, component states and trust signals before page implementation.\n"
            "- Prefer the component ecosystem and implementation baseline recommended in output/*-uiux.md instead of switching UI libraries ad hoc.\n"
        )

    def _trae_rules(self) -> str:
        return (
            "# Super Dev Trae Rules\n\n"
            "## Critical Trigger Switch\n"
            "- If a user message starts with `super-dev:` or `super-dev：`, immediately switch into Super Dev pipeline mode.\n"
            "- Do not treat `super-dev:` or `super-dev：` as normal chat, brainstorming, or generic coding mode.\n"
            "- After `super-dev:` or `super-dev：` is seen, do not start implementation directly.\n"
            "- Your first reply must say `SMOKE_OK` when the user is smoke-testing, or explicitly say Super Dev pipeline mode is active.\n"
            "- Your first reply must explicitly say the current phase is `research`.\n"
            "- Your first reply must explicitly promise the sequence: research -> three core documents -> wait for user confirmation -> Spec/tasks -> frontend runtime verification -> backend/tests/delivery.\n"
            "- After the three core documents are generated, you must stop and wait for approval before creating Spec or writing code.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus Trae rule files, not as a separate coding engine.\n"
            "- Keep using the host's model, tools, browse/search/web and editor capabilities.\n"
            "- Use local `super-dev` commands when you need to generate or refresh documents, specs, quality reports, or delivery manifests.\n"
            "- The host remains responsible for coding, tool execution, and file changes.\n\n"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting the three core documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and carry its matched local knowledge into PRD, architecture, UIUX, Spec, and execution.\n"
            "- Treat matched standards, anti-patterns, checklists, baselines, and scenario packs as hard constraints.\n\n"
            "## Working Agreement\n"
            "- If browse/search/web is available, research similar products first and write `output/*-research.md` into the project workspace.\n"
            "- Generate PRD, architecture, and UIUX before coding and save them as `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` instead of only replying in chat.\n"
            "- Ask the user to confirm or revise the three documents before creating Spec or code.\n"
            "- If a document is mentioned in chat but not written to the repository, treat the step as incomplete and keep working until the file exists.\n"
            "- If the user requests a UI redesign or says the UI is unsatisfactory, first update `output/*-uiux.md`, then redo the frontend, and rerun frontend runtime + UI review before continuing.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign tasks and implementation before continuing.\n"
            "- If the user requests quality or security remediation, first fix the issues, rerun quality gate plus `super-dev release proof-pack`, and only then continue.\n"
            "- Implement frontend first and verify runtime before moving into backend-heavy work.\n"
            "- Keep UI implementation consistent with `output/*-uiux.md` and avoid AI-looking templates.\n"
        )

    def _claude_rules(self) -> str:
        return (
            "# Super Dev Claude Code Integration\n\n"
            "This project uses a pipeline-driven development model.\n\n"
            "## Positioning\n"
            "- Super Dev does not own a model endpoint.\n"
            "- Claude Code remains the execution host for coding capability.\n"
            "- Super Dev provides governance: protocol, gates, and audit artifacts.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus Claude Code command/rule integration.\n"
            "- When the user triggers `/super-dev`, `super-dev:`, or `super-dev：`, enter the Super Dev pipeline immediately rather than handling it like casual chat.\n"
            "- Use Claude Code browse/search for research and Claude Code terminal/editing for implementation.\n"
            "- Use local `super-dev` commands whenever you need to generate/update docs, spec artifacts, quality reports, and delivery outputs.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting PRD, architecture, and UIUX.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and inherit its local knowledge hits into later stages.\n"
            "- Treat matched local standards, scenario packs, and checklists as hard constraints, not optional hints.\n\n"
            "## Before coding\n"
            "1. If Claude Code browse/search is available, research similar products first and write output/*-research.md as a real repository file\n"
            "2. Read output/*-prd.md\n"
            "3. Read output/*-architecture.md\n"
            "4. Read output/*-uiux.md\n"
            "5. Summarize the three core documents to the user and wait for explicit confirmation before creating Spec or coding\n"
            "6. Chat-only summaries do not count as completion; the required artifacts must exist in the workspace\n"
            "7. Read output/*-execution-plan.md\n"
            "8. Follow .super-dev/changes/*/tasks.md after confirmation, with frontend-first implementation and runtime verification\n\n"
            "9. If the user requests a UI redesign or says the UI is unsatisfactory, first update `output/*-uiux.md`, then redo the frontend, and rerun frontend runtime + UI review before continuing.\n\n"
            "## Output Quality\n"
            "- Keep security/performance constraints from red-team report.\n"
            "- Ensure quality gate threshold is met before merge.\n"
            "- UI must follow output/*-uiux.md and avoid AI-looking templates (purple gradient, emoji icons, default-font-only).\n"
            "- UI implementation must define typography system, tokens, page hierarchy and component states before polishing visuals.\n"
            "- Prioritize real screenshots, trust modules, proof points and task flows over decorative hero sections.\n"
        )

    def _antigravity_workflow_rules(self) -> str:
        """
        生成 Antigravity IDE 专属工作流配置。
        文件写入 .agent/workflows/super-dev.md，
        格式遵循 Antigravity Skill YAML frontmatter + markdown 规范。
        """
        return """\
---
description: Super Dev 流水线式 AI Coding 辅助工作流 - 从需求到交付的 12 阶段自动化流程
---

# Super Dev Pipeline Workflow

## 角色定义

本工作流激活 10 位专家角色自动协作：

| 专家 | 职责 |
|:---|:---|
| PM | 需求分析、PRD 生成、用户故事 |
| ARCHITECT | 架构设计、技术选型、API 契约 |
| UI/UX | 设计系统、交互规范、原型设计 |
| SECURITY | 红队审查、OWASP 检测、威胁建模 |
| CODE | 代码实现、最佳实践、代码审查 |
| DBA | 数据库设计、迁移脚本、索引优化 |
| QA | 测试策略、质量门禁、覆盖率要求 |
| DEVOPS | CI/CD 配置、容器化、监控告警 |
| RCA | 根因分析、故障复盘、风险识别 |

## 工作流步骤

### 前置：读取必备文档

在写任何一行代码前，必须先读取：

1. `output/*-prd.md` — 产品需求和验收标准
2. `output/*-architecture.md` — 技术栈和 API 设计
3. `output/*-uiux.md` — 设计系统和组件规范
4. `output/*-execution-plan.md` — 阶段任务路线图
5. `.super-dev/changes/*/tasks.md` — 具体实现任务清单

### 第 0 阶段：需求增强与同类产品研究

```bash
super-dev "你的需求描述"
```

- 解析自然语言需求，注入领域知识库
- 优先使用宿主原生联网能力研究同类产品、关键流程、页面结构和交互模式
- 联网检索补充市场和技术背景
- 输出 `output/*-research.md`，沉淀对标结论、共性功能和差异化机会
- 输出结构化需求蓝图

### 第 1 阶段：专业文档生成

自动生成：
- `output/*-prd.md` — PRD（产品需求文档）
- `output/*-architecture.md` — 架构设计文档
- `output/*-uiux.md` — UI/UX 设计文档
- 以上产物必须真实写入项目工作区；只在聊天里总结不算完成

### 第 2-4 阶段：骨架构建

- 前端可演示骨架（前端先行原则）
- Spec 规范（结构化规范风格）
- 前后端实现骨架 + API 契约

### 第 5-6 阶段：质量保障

- 红队审查（安全 + 性能 + 架构）
- 质量门禁（统一标准：80+）

### 第 7-8 阶段：交付准备

- 代码审查指南
- AI 提示词生成（直接传给 AI 开始开发）

### 第 9-11 阶段：部署与交付

- CI/CD 配置（GitHub/GitLab/Jenkins/Azure/Bitbucket）
- 数据库迁移脚本（Prisma/TypeORM/SQLAlchemy 等 6 种 ORM）
- 项目交付包（manifest + report + zip）

## 执行规则

- 进入 Super Dev 流程后，第一轮必须明确当前阶段是 `research`
- 三份核心文档完成后，必须暂停等待用户确认
- 未经用户确认，不得创建 `.super-dev/changes/*` 或开始编码
- **前端先行**：先完成可演示前端，再实现后端 API
- **禁止 emoji 图标**：使用 Lucide/Heroicons/Tabler Icons
- **参数化查询**：禁止字符串拼接 SQL
- **任务跟踪**：每完成一项在 tasks.md 标记 `[x]`
- **质量门禁**：交付前运行 `super-dev quality --type all`

## 常用命令

```bash
super-dev "需求"               # 完整 12 阶段流水线（推荐）
super-dev pipeline "需求"      # 高级参数模式
super-dev create "需求"        # 生成文档 + Spec
super-dev quality --type all   # 质量检查
super-dev expert SECURITY "需求"  # 单专家调用
super-dev skill install super-dev --target antigravity  # 安装 Skill
```
"""

    def _build_antigravity_context_content(self) -> str:
        return (
            "# Super Dev Antigravity Context\n\n"
            "Antigravity remains the execution host for model reasoning, browsing, terminal work, and code changes.\n"
            "Super Dev is the governance layer and local Python toolchain.\n\n"
            "## Trigger\n"
            "- Preferred: `/super-dev \"<需求描述>\"`\n"
            "- Fallback in local terminal only: `super-dev \"<需求描述>\"`\n"
            "- The terminal fallback does not replace the Antigravity host session.\n\n"
            "## Required First Response Contract\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read `knowledge/` first when relevant.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, inherit its local knowledge hits into research, PRD, architecture, UIUX, Spec, and implementation.\n\n"
            "## Artifact Contract\n"
            "- Write `output/*-research.md`, `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` into the repository workspace.\n"
            "- Chat-only summaries do not count as finished artifacts.\n"
            "- If a required artifact is missing from the workspace, continue until it exists.\n\n"
            "## Required Execution Order\n"
            "1. Research similar products first using host-native browse/search and write `output/*-research.md`\n"
            "2. Generate PRD, architecture, and UIUX and write them as project files\n"
            "3. Stop and wait for explicit user confirmation before Spec or coding\n"
            "4. Create Spec/tasks only after confirmation\n"
            "5. Implement and run the frontend first\n"
            "6. Continue with backend, tests, quality gate, and delivery\n"
            "7. If the user requests a UI redesign, first update `output/*-uiux.md`, then redo the frontend and rerun frontend runtime + UI review\n"
            "8. If the user requests architecture changes, first update `output/*-architecture.md`, then realign tasks and implementation\n"
            "9. If the user requests quality remediation, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue\n"
        )
