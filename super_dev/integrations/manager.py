"""
多平台 AI Coding 工具集成管理器
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

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
    host_protocol_mode: str
    host_protocol_summary: str
    official_project_surfaces: list[str]
    official_user_surfaces: list[str]
    observed_compatibility_surfaces: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class IntegrationManager:
    """为不同 AI Coding 平台生成集成配置"""

    TEXT_TRIGGER_PREFIX = "super-dev:"
    NO_SKILL_TARGETS: set[str] = {"claude-code", "kiro"}
    HOST_USAGE_LOCATIONS: dict[str, str] = {
        "claude-code": "在项目目录启动 Claude Code 当前会话后，直接在同一会话里触发。",
        "codebuddy-cli": "在项目目录启动 CodeBuddy CLI 会话后触发。",
        "codebuddy": "打开 CodeBuddy IDE 的 Agent Chat，在项目上下文内触发。",
        "codex-cli": "在项目目录完成接入后，重启 codex，然后在新的 Codex CLI 会话里触发。",
        "cursor-cli": "在项目目录启动 Cursor CLI 当前会话后触发。",
        "cursor": "打开 Cursor 的 Agent Chat，并确保当前工作区就是目标项目。",
        "windsurf": "打开 Windsurf 的 Agent Chat 或 Workflow 入口，在项目上下文内触发。",
        "gemini-cli": "在项目目录启动 Gemini CLI 会话后触发。",
        "iflow": "在项目目录启动 iFlow CLI 会话后触发。",
        "kimi-cli": "在项目目录启动 Kimi CLI 会话后触发。",
        "kiro-cli": "在项目目录启动 Kiro CLI 会话后触发。",
        "opencode": "在项目目录启动 OpenCode CLI 会话后触发。",
        "qoder-cli": "在项目目录启动 Qoder CLI 会话后触发。",
        "kiro": "打开 Kiro IDE 的 Agent Chat 或 AI 面板，在项目上下文内触发。",
        "qoder": "打开 Qoder IDE 的 Agent Chat，在当前项目内触发。",
        "trae": "打开 Trae Agent Chat，在当前项目上下文内直接触发。",
    }
    HOST_USAGE_NOTES: dict[str, list[str]] = {
        "claude-code": [
            "推荐作为首选 CLI 宿主。",
            "接入后可先执行 super-dev doctor --host claude-code 确认 slash 已生效。",
            "Claude Code 官方已公开 `.claude/agents/` 与 `~/.claude/agents/`，Super Dev 会生成 subagent 协议文件。",
        ],
        "codebuddy-cli": [
            "在当前 CLI 会话中直接输入即可。",
            "如果会话早于接入动作启动，建议重开会话后再试。",
            "官方文档已公开 ~/.codebuddy/skills 与 .codebuddy/skills，可与 slash 一起增强宿主对 Super Dev 流水线的理解。",
        ],
        "codebuddy": [
            "建议在项目级 Agent Chat 中使用，不要脱离项目上下文。",
            "先让宿主完成 research，再继续文档和编码。",
            "官方文档已公开 .codebuddy/skills 与 ~/.codebuddy/skills。",
        ],
        "codex-cli": [
            "不要输入 /super-dev，Codex 当前不走自定义 slash。",
            "实际依赖 .codex/AGENTS.md 和 .codex/skills/super-dev-core/SKILL.md。",
            "如果旧会话没加载新 Skill，重启 codex 再试。",
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
        "iflow": [
            "当前按 slash 宿主适配。",
            "如果 slash 未出现，先检查项目级命令文件是否已写入。",
            "官方文档已公开 .iflow/skills 与 ~/.iflow/skills。",
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
            "Trae 始终依赖项目级 .trae/rules.md；若检测到宿主级 ~/.trae/skills/super-dev-core/SKILL.md，则会额外增强。",
            "安装后建议新开一个 Trae Agent Chat，让新的规则与 Skill 一起生效。",
            "随后按 output/* 与 .super-dev/changes/*/tasks.md 推进开发。",
        ],
    }

    TARGETS: dict[str, IntegrationTarget] = {
        "claude-code": IntegrationTarget(
            name="claude-code",
            description="Claude Code CLI 深度集成",
            files=[".claude/CLAUDE.md", ".claude/agents/super-dev-core.md"],
        ),
        "codebuddy-cli": IntegrationTarget(
            name="codebuddy-cli",
            description="CodeBuddy CLI 项目规则注入",
            files=[".codebuddy/AGENTS.md"],
        ),
        "codebuddy": IntegrationTarget(
            name="codebuddy",
            description="CodeBuddy IDE 规则注入",
            files=[".codebuddy/rules.md"],
        ),
        "codex-cli": IntegrationTarget(
            name="codex-cli",
            description="Codex CLI 项目上下文注入",
            files=[".codex/AGENTS.md"],
        ),
        "cursor-cli": IntegrationTarget(
            name="cursor-cli",
            description="Cursor CLI 项目规则注入",
            files=[".cursor/rules/super-dev.mdc"],
        ),
        "windsurf": IntegrationTarget(
            name="windsurf",
            description="Windsurf IDE 规则注入",
            files=[".windsurf/rules.md"],
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
            files=[".trae/rules.md"],
        ),
    }
    SLASH_COMMAND_FILES: dict[str, str] = {
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
        "cursor": ".cursor/commands/super-dev.md",
    }
    GLOBAL_SLASH_COMMAND_FILES: dict[str, str] = {
        "opencode": ".config/opencode/commands/super-dev.md",
    }
    NO_SLASH_TARGETS: set[str] = {"codex-cli", "kimi-cli", "kiro", "trae"}
    OFFICIAL_DOCS: dict[str, str] = {
        "claude-code": "https://docs.anthropic.com/en/docs/claude-code/slash-commands",
        "codebuddy-cli": "https://www.codebuddy.ai/docs/cli/slash-commands",
        "codebuddy": "https://www.codebuddy.ai/docs/cli/ide-integrations",
        "codex-cli": "https://platform.openai.com/docs/codex",
        "cursor-cli": "https://docs.cursor.com/en/cli/reference/slash-commands",
        "windsurf": "https://docs.windsurf.com/plugins/cascade/workflows",
        "gemini-cli": "https://google-gemini.github.io/gemini-cli/docs/",
        "iflow": "https://platform.iflow.cn/en/cli/examples/slash-commands",
        "kimi-cli": "https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html",
        "kiro-cli": "https://kiro.dev/docs/cli/",
        "opencode": "https://opencode.ai/docs/commands/",
        "qoder-cli": "https://docs.qoder.com/cli/using-cli",
        "cursor": "https://docs.cursor.com/en/agent/chat/commands",
        "kiro": "https://kiro.dev/docs/steering/",
        "qoder": "https://docs.qoder.com/user-guide/commands",
        "trae": "https://www.traeide.com/docs/what-is-trae-rules",
    }
    DOCS_VERIFIED_TARGETS: set[str] = {key for key, value in OFFICIAL_DOCS.items() if bool(value)}
    HOST_CERTIFICATIONS: dict[str, dict[str, object]] = {
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
            "reason": "Trae 官方公开面目前可确认的是项目 rules；宿主级 skills 仍按兼容增强处理，因此当前保持稳定兼容而非认证级。",
            "evidence": [
                "公开文档确认 Trae rules 机制",
                "本机若存在 ~/.trae/skills，可作为兼容增强路径协同生效",
                "Super Dev 已同时建模项目 rules 与可选宿主级 Skill 增强",
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
            "reason": "IDE 侧能力存在，但对 Agent Chat slash 的项目级行为仍缺少持续真机验证。",
            "evidence": [
                "官方文档公开 IDE integrations",
                "Super Dev 已写入规则、Skill 与命令映射",
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

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        self.templates_dir = self.project_dir / "templates"

    def _first_response_contract_zh(self) -> str:
        return (
            "## 首轮响应契约（首次触发必须执行）\n"
            "- 当用户输入 `/super-dev ...` 或 `super-dev: ...` 后，第一轮回复必须明确：已进入 Super Dev 流水线，而不是普通聊天。\n"
            "- 第一轮回复必须明确当前阶段是 `research`，会先读取 `knowledge/` 与 `output/knowledge-cache/*-knowledge-bundle.json`（若存在），再用宿主原生联网研究同类产品。\n"
            "- 第一轮回复必须明确后续顺序：research -> 三份核心文档 -> 等待用户确认 -> Spec / tasks -> 前端优先并运行验证 -> 后端 / 测试 / 交付。\n"
            "- 第一轮回复必须明确承诺：三份核心文档完成后会暂停并等待用户确认；未经确认不会创建 Spec，也不会开始编码。\n\n"
        )

    def _first_response_contract_en(self) -> str:
        return (
            "## First-Response Contract\n"
            "- On the first reply after `/super-dev ...` or `super-dev: ...`, explicitly state that Super Dev pipeline mode is now active rather than normal chat mode.\n"
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
        docs_url = self.OFFICIAL_DOCS.get(target, "")
        docs_verified = target in self.DOCS_VERIFIED_TARGETS
        adapter_mode = self._adapter_mode(target=target, category=category, integration_files=integration_files)
        usage = self._usage_profile(target=target, category=category)
        certification = self._certification_profile(target)
        smoke = self._smoke_profile(target=target, category=category)
        surfaces = self._install_surfaces(target=target)
        protocol = self._protocol_profile(target=target)

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
            host_protocol_mode=str(protocol["mode"]),
            host_protocol_summary=str(protocol["summary"]),
            official_project_surfaces=list(surfaces["official_project_surfaces"]),
            official_user_surfaces=list(surfaces["official_user_surfaces"]),
            observed_compatibility_surfaces=list(surfaces["observed_compatibility_surfaces"]),
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
                "primary_entry": '在 Codex CLI 会话输入 `super-dev: <需求描述>`（由 .codex/AGENTS.md + ~/.codex/skills/super-dev-core/SKILL.md 生效）',
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "trigger_context": "Codex CLI 当前会话",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重启 codex，使 AGENTS.md 与 ~/.codex/skills/super-dev-core/SKILL.md 生效。",
                    "不要输入 /super-dev，在 Codex 会话里输入 `super-dev: <需求描述>`。",
                ],
                "usage_notes": usage_notes,
                "notes": "该 CLI 宿主当前不走自定义 slash，使用项目级 .codex/AGENTS.md 作为核心约束，并通过官方用户级 Skills 目录 ~/.codex/skills 安装 super-dev-core。",
            }
        if target == "trae":
            return {
                "usage_mode": "rules-and-skill",
                "primary_entry": '在 Trae Agent Chat 输入 `super-dev: <需求描述>`（由 .trae/rules.md + 兼容 Skill〔若检测到〕生效）',
                "trigger_command": f"{self.TEXT_TRIGGER_PREFIX} <需求描述>",
                "trigger_context": "Trae IDE Agent Chat",
                "usage_location": usage_location,
                "requires_restart_after_onboard": True,
                "post_onboard_steps": [
                    "完成接入后重新打开 Trae，或至少新开一个 Trae Agent Chat，使新的规则与兼容 Skill（若已安装）一起生效。",
                    "确保当前项目就是已接入 Super Dev 的工作区。",
                    "输入 `super-dev: <需求描述>` 触发完整流程。",
                    "按 output/* 与 .super-dev/changes/*/tasks.md 执行开发。",
                ],
                "usage_notes": usage_notes,
                "notes": "该宿主当前以项目级 .trae/rules.md 为核心接入面；若检测到 ~/.trae/skills，则会增强安装 super-dev-core，但这条路径仍只视为兼容增强。",
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

    def _protocol_profile(self, *, target: str) -> dict[str, str]:
        mapping = {
            "claude-code": {
                "mode": "official-subagent",
                "summary": "官方 commands + subagents",
            },
            "codebuddy-cli": {
                "mode": "official-skill",
                "summary": "官方 commands + skills",
            },
            "codebuddy": {
                "mode": "official-skill",
                "summary": "官方 commands + skills",
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
            "kiro": {
                "mode": "official-steering",
                "summary": "官方 project steering + global steering",
            },
            "codex-cli": {
                "mode": "official-skill",
                "summary": "官方 AGENTS.md + 官方 Skills",
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
            "codebuddy-cli": {
                "official_project_surfaces": [
                    ".codebuddy/AGENTS.md",
                    ".codebuddy/commands/super-dev.md",
                    ".codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": ["~/.codebuddy/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": [],
            },
            "codebuddy": {
                "official_project_surfaces": [
                    ".codebuddy/rules.md",
                    ".codebuddy/commands/super-dev.md",
                    ".codebuddy/skills/super-dev-core/SKILL.md",
                ],
                "official_user_surfaces": ["~/.codebuddy/skills/super-dev-core/SKILL.md"],
                "observed_compatibility_surfaces": [],
            },
            "codex-cli": {
                "official_project_surfaces": [".codex/AGENTS.md"],
                "official_user_surfaces": ["~/.codex/skills/super-dev-core/SKILL.md"],
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
                    ".windsurf/rules.md",
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
                "official_project_surfaces": [".trae/rules.md"],
                "official_user_surfaces": [],
                "observed_compatibility_surfaces": ["~/.trae/skills/super-dev-core/SKILL.md"],
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
            if file_path.exists() and not force:
                continue
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = self._build_file_content(target=target, relative=relative)
            file_path.write_text(content, encoding="utf-8")
            written_files.append(file_path)

        return written_files

    def setup_global_protocol(self, target: str, force: bool = False) -> Path | None:
        if target == "claude-code":
            protocol_file = Path.home() / ".claude" / "agents" / "super-dev-core.md"
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(self._build_claude_agent_content(), encoding="utf-8")
            return protocol_file

        if target == "kiro":
            protocol_file = Path.home() / ".kiro" / "steering" / "AGENTS.md"
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(self._build_kiro_global_steering_content(), encoding="utf-8")
            return protocol_file

        if target == "gemini-cli":
            protocol_file = Path.home() / ".gemini" / "GEMINI.md"
            if protocol_file.exists() and not force:
                return None
            protocol_file.parent.mkdir(parents=True, exist_ok=True)
            protocol_file.write_text(self._build_content(target), encoding="utf-8")
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
        command_file.write_text(self._build_slash_command_content(target), encoding="utf-8")
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
        if target == "claude-code" and relative.endswith(".claude/agents/super-dev-core.md"):
            return self._build_claude_agent_content()

        if target == "cursor":
            cursor_template = self.templates_dir / ".cursorrules.template"
            if cursor_template.exists():
                body = cursor_template.read_text(encoding="utf-8")
                return (
                    f"{body}\n\n"
                    "# Super Dev Pipeline Rules\n"
                    "- Always read output/*-prd.md, output/*-architecture.md, output/*-uiux.md first.\n"
                    "- Execute frontend-first delivery before backend/database tasks.\n"
                    "- Meet the active quality gate threshold before release.\n"
                )

        if target == "antigravity":
            return self._antigravity_workflow_rules()

        if target in {
            "cursor",
            "windsurf",
            "cline",
            "continue",
            "vscode-copilot",
            "jetbrains-ai",
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

    def _build_claude_agent_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: Activate the Super Dev pipeline for research-first, commercial-grade project delivery.\n"
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
            "## Boundary\n"
            "- Claude Code remains the execution host.\n"
            "- Super Dev is the governance layer, not a separate model platform.\n"
            "- Prefer repository-local rules and commands as the source of project-specific context.\n"
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
                '- Preferred: say `super-dev: <需求描述>` in the host chat so AGENTS.md + super-dev-core Skill can govern the workflow.\n'
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
            "1. Use the host's native browse/search/web capability to research similar products first and produce output/*-research.md\n"
            "2. Freeze PRD, architecture and UIUX documents\n"
            "3. Stop after the three core documents, summarize them to the user, and wait for explicit confirmation before creating Spec or coding\n"
            "4. Create Spec proposal/tasks only after the user confirms the documents\n"
            "5. Implement and run the frontend first so it becomes demonstrable before backend-heavy work\n"
            "6. Implement backend APIs and data layer, then run tests, quality gate, and release preparation\n"
        )

    def _generic_ide_rules(self, target: str) -> str:
        return (
            f"# Super Dev IDE Rules ({target})\n\n"
            "## Positioning\n"
            "- Super Dev is a host-level workflow governor, not an LLM platform.\n"
            "- Keep using the host's model capabilities; do not expect extra model APIs from Super Dev.\n"
            "- The host remains responsible for actual coding, tool execution, and file changes.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus this host rule file, not as a separate coding engine.\n"
            "- When the user says `/super-dev ...` or `super-dev: ...`, immediately enter the Super Dev pipeline.\n"
            "- Use host-native browse/search/web for research and host-native editing/terminal for implementation.\n"
            "- Use local `super-dev` commands when you need to generate or refresh documents, spec artifacts, quality reports, or delivery manifests.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting the three core documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and inherit its matched local knowledge into PRD, architecture, UIUX, Spec, and execution.\n"
            "- Treat local knowledge hits as hard project constraints, especially for standards, anti-patterns, checklists, and scenario packs.\n\n"
            "## Working Agreement\n"
            "- If the host supports browse/search/web, research similar products first and summarize the findings in output/*-research.md.\n"
            "- Generate PRD, architecture and UIUX documents before coding, then pause and ask the user to confirm the three documents.\n"
            "- If the user requests revisions, update the documents first and ask again; do not create Spec or code before confirmation.\n"
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
            "- When the user triggers `/super-dev`, enter the Super Dev pipeline immediately rather than handling it like casual chat.\n"
            "- Use Claude Code browse/search for research and Claude Code terminal/editing for implementation.\n"
            "- Use local `super-dev` commands whenever you need to generate/update docs, spec artifacts, quality reports, and delivery outputs.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting PRD, architecture, and UIUX.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and inherit its local knowledge hits into later stages.\n"
            "- Treat matched local standards, scenario packs, and checklists as hard constraints, not optional hints.\n\n"
            "## Before coding\n"
            "1. If Claude Code browse/search is available, research similar products first and write output/*-research.md\n"
            "2. Read output/*-prd.md\n"
            "3. Read output/*-architecture.md\n"
            "4. Read output/*-uiux.md\n"
            "5. Summarize the three core documents to the user and wait for explicit confirmation before creating Spec or coding\n"
            "6. Read output/*-execution-plan.md\n"
            "7. Follow .super-dev/changes/*/tasks.md after confirmation, with frontend-first implementation and runtime verification\n\n"
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
        文件写入 .agents/workflows/super-dev.md，
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
