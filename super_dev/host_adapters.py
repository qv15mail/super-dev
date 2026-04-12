"""Specialized host adapters for high-variance hosts.

This module carries host-specific integration behavior for hosts that need
deeper guidance than the generic slash/text workflow path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SpecialAdapterContext:
    """Context needed to render host-specific adapter content."""

    target: str
    category: str
    usage_location: str
    usage_notes: tuple[str, ...]
    text_trigger_prefix: str = "super-dev:"
    seeai_text_trigger_prefix: str = "super-dev-seeai:"


@dataclass(frozen=True, slots=True)
class ManualInstallGuidance:
    """Manual install copy for hosts that do not use the unified installer."""

    title: str
    lines: tuple[str, ...]
    border_style: str = "yellow"
    plain_fallback: str = ""


@dataclass(frozen=True, slots=True)
class HostSpecialAdapter:
    """Specialized behavior for hosts that diverge from generic handling."""

    host_id: str
    adapter_mode_override: str = ""
    install_surfaces: dict[str, tuple[str, ...]] = field(default_factory=dict)
    runtime_checklist: tuple[str, ...] = ()
    pass_criteria: tuple[str, ...] = ()
    resume_checklist: tuple[str, ...] = ()
    competition_smoke_extra_steps: tuple[str, ...] = ()
    flow_probe: dict[str, Any] = field(default_factory=dict)
    manual_install_guidance: ManualInstallGuidance | None = None

    def build_usage_profile(self, context: SpecialAdapterContext) -> dict[str, object]:
        raise NotImplementedError


def _runtime_validation_payload(adapter: HostSpecialAdapter) -> dict[str, list[str]]:
    return {
        "runtime_checklist": list(adapter.runtime_checklist),
        "pass_criteria": list(adapter.pass_criteria),
        "resume_checklist": list(adapter.resume_checklist),
    }


@dataclass(frozen=True, slots=True)
class _CodeBuddyCliAdapter(HostSpecialAdapter):
    def build_usage_profile(self, context: SpecialAdapterContext) -> dict[str, object]:
        return {
            "usage_mode": "native-slash",
            "primary_entry": '在 CodeBuddy CLI 当前项目会话里优先使用 `/super-dev "<需求描述>"`；比赛模式优先使用 `/super-dev-seeai "<需求描述>"`。',
            "trigger_command": '/super-dev "<需求描述>"',
            "entry_variants": [
                {
                    "surface": "cli",
                    "label": "CodeBuddy CLI",
                    "entry": "/super-dev",
                    "mode": "official-subagent-slash",
                    "priority": "preferred",
                    "notes": "标准 Super Dev 主流程入口。",
                },
                {
                    "surface": "competition",
                    "label": "CodeBuddy CLI SEEAI",
                    "entry": "/super-dev-seeai",
                    "mode": "official-subagent-slash",
                    "priority": "preferred",
                    "notes": "比赛半小时极速版入口。",
                },
                {
                    "surface": "fallback",
                    "label": "Natural Language Fallback",
                    "entry": f"{context.text_trigger_prefix} <需求描述>",
                    "mode": "rules-natural-language-fallback",
                    "priority": "fallback",
                    "notes": "当 slash 不可用时的自然语言回退入口。",
                },
            ],
            "trigger_context": "CodeBuddy CLI 当前项目会话",
            "usage_location": context.usage_location,
            "requires_restart_after_onboard": False,
            "post_onboard_steps": [
                "确认项目内已生成 `CODEBUDDY.md`、`.codebuddy/commands/super-dev.md`、`.codebuddy/commands/super-dev-seeai.md`、`.codebuddy/skills/super-dev/SKILL.md` 与 `.codebuddy/skills/super-dev-seeai/SKILL.md`。",
                "确认用户目录已生成 `~/.codebuddy/CODEBUDDY.md`、`~/.codebuddy/commands/` 与 `~/.codebuddy/skills/`。",
                '在 CodeBuddy CLI 当前项目会话里优先输入 `/super-dev "<需求描述>"`；比赛模式优先输入 `/super-dev-seeai "<需求描述>"`。',
            ],
            "usage_notes": list(context.usage_notes),
            "notes": "CodeBuddy CLI 当前最佳接入面是 CODEBUDDY.md + commands + skills，并保持同一会话内连续完成 research、文档、Spec 与实现。",
            "runtime_validation": _runtime_validation_payload(self),
        }


@dataclass(frozen=True, slots=True)
class _CodeBuddyIdeAdapter(HostSpecialAdapter):
    def build_usage_profile(self, context: SpecialAdapterContext) -> dict[str, object]:
        return {
            "usage_mode": "native-slash",
            "primary_entry": '在 CodeBuddy IDE 的 Agent Chat 里优先使用 `/super-dev "<需求描述>"`；比赛模式优先使用 `/super-dev-seeai "<需求描述>"`。',
            "trigger_command": '/super-dev "<需求描述>"',
            "entry_variants": [
                {
                    "surface": "ide",
                    "label": "CodeBuddy IDE",
                    "entry": "/super-dev",
                    "mode": "official-subagent-slash",
                    "priority": "preferred",
                    "notes": "标准 Super Dev 主流程入口。",
                },
                {
                    "surface": "competition",
                    "label": "CodeBuddy IDE SEEAI",
                    "entry": "/super-dev-seeai",
                    "mode": "official-subagent-slash",
                    "priority": "preferred",
                    "notes": "比赛半小时极速版入口。",
                },
                {
                    "surface": "fallback",
                    "label": "Natural Language Fallback",
                    "entry": f"{context.text_trigger_prefix} <需求描述>",
                    "mode": "rules-natural-language-fallback",
                    "priority": "fallback",
                    "notes": "当 slash 不可用时的自然语言回退入口。",
                },
            ],
            "trigger_context": "CodeBuddy IDE Agent Chat",
            "usage_location": context.usage_location,
            "requires_restart_after_onboard": False,
            "post_onboard_steps": [
                "确认项目内已生成 `CODEBUDDY.md`、`.codebuddy/rules/super-dev/RULE.mdc`、`.codebuddy/commands/super-dev.md`、`.codebuddy/commands/super-dev-seeai.md`、`.codebuddy/agents/super-dev.md`、`.codebuddy/skills/super-dev/SKILL.md` 与 `.codebuddy/skills/super-dev-seeai/SKILL.md`。",
                "确认用户目录已生成 `~/.codebuddy/CODEBUDDY.md`、`~/.codebuddy/commands/`、`~/.codebuddy/agents/` 与 `~/.codebuddy/skills/`。",
                '在 CodeBuddy IDE 的 Agent Chat 里优先输入 `/super-dev "<需求描述>"`；比赛模式优先输入 `/super-dev-seeai "<需求描述>"`。',
            ],
            "usage_notes": list(context.usage_notes),
            "notes": "CodeBuddy IDE 需要规则、commands、agents 与 skills 四层同时稳定工作，比赛模式下优先保住 P0 主路径与 wow 点。",
            "runtime_validation": _runtime_validation_payload(self),
        }


@dataclass(frozen=True, slots=True)
class _OpenClawAdapter(HostSpecialAdapter):
    def build_usage_profile(self, context: SpecialAdapterContext) -> dict[str, object]:
        return {
            "usage_mode": "plugin-and-skill",
            "primary_entry": '在 OpenClaw Agent 会话里优先使用 `/super-dev "<需求描述>"`；如果命令面板未刷新，回退到 `super-dev: <需求描述>`。比赛模式优先 `/super-dev-seeai`，未刷新时回退 `super-dev-seeai:`。',
            "trigger_command": '/super-dev "<需求描述>"',
            "entry_variants": [
                {
                    "surface": "plugin",
                    "label": "OpenClaw Slash",
                    "entry": "/super-dev",
                    "mode": "plugin-slash",
                    "priority": "preferred",
                    "notes": "插件命令面已刷新时的标准入口。",
                },
                {
                    "surface": "fallback",
                    "label": "OpenClaw Text Fallback",
                    "entry": f"{context.text_trigger_prefix} <需求描述>",
                    "mode": "plugin-text-fallback",
                    "priority": "fallback",
                    "notes": "插件未刷新或当前命令面未暴露 slash 时的自然语言回退入口。",
                },
                {
                    "surface": "competition",
                    "label": "OpenClaw SEEAI",
                    "entry": "/super-dev-seeai",
                    "mode": "plugin-slash",
                    "priority": "preferred",
                    "notes": "比赛半小时极速版入口；未刷新时回退 `super-dev-seeai:`。",
                },
            ],
            "trigger_context": "OpenClaw Agent 会话",
            "usage_location": context.usage_location,
            "requires_restart_after_onboard": False,
            "post_onboard_steps": [
                "确认 OpenClaw 官方插件已安装。",
                "确认项目内已生成 `.openclaw/rules/super-dev.md`、`.openclaw/commands/super-dev.md` 与 `.openclaw/commands/super-dev-seeai.md`。",
                "确认用户目录已生成 `~/.openclaw/skills/super-dev/SKILL.md` 与 `~/.openclaw/skills/super-dev-seeai/SKILL.md`。",
                "优先走 slash；如果命令面板还没刷新，直接回退到 `super-dev:` / `super-dev-seeai:`。",
            ],
            "usage_notes": list(context.usage_notes),
            "notes": "OpenClaw 是插件宿主，关键是插件命令面、项目规则面和用户级 skills 同时生效；比赛模式下优先避免频繁切工具与上下文漂移。",
            "runtime_validation": _runtime_validation_payload(self),
        }


@dataclass(frozen=True, slots=True)
class _WorkBuddyAdapter(HostSpecialAdapter):
    def build_usage_profile(self, context: SpecialAdapterContext) -> dict[str, object]:
        return {
            "usage_mode": "manual-workbench-skill",
            "primary_entry": "在 WorkBuddy 当前任务/对话会话中输入 `super-dev: <需求描述>`；比赛模式使用 `super-dev-seeai: <需求描述>`。接入方式为手动启用 Skills，而不是自动写项目规则文件。",
            "trigger_command": f"{context.text_trigger_prefix} <需求描述>",
            "entry_variants": [
                {
                    "surface": "default",
                    "label": "WorkBuddy",
                    "entry": f"{context.text_trigger_prefix} <需求描述>",
                    "mode": "manual-skill-natural-language",
                    "priority": "preferred",
                    "notes": "标准 Super Dev 入口。",
                },
                {
                    "surface": "competition",
                    "label": "WorkBuddy SEEAI",
                    "entry": f"{context.seeai_text_trigger_prefix} <需求描述>",
                    "mode": "manual-skill-natural-language",
                    "priority": "preferred",
                    "notes": "比赛半小时极速版入口。",
                },
            ],
            "trigger_context": "WorkBuddy 当前任务/对话会话",
            "usage_location": context.usage_location,
            "requires_restart_after_onboard": False,
            "post_onboard_steps": [
                "在 WorkBuddy 中确认当前任务会话绑定了目标项目目录或授权文件夹。",
                "手动启用 Super Dev 标准版与 SEEAI 比赛版 Skills。",
                "在同一个任务会话里输入 `super-dev: <需求描述>` 或 `super-dev-seeai: <需求描述>`。",
            ],
            "usage_notes": list(context.usage_notes),
            "notes": "WorkBuddy 当前按手动接入宿主建模：宿主负责自然语言任务、自主执行、本地文件操作和 Skills/MCP；Super Dev 负责标准流程与 SEEAI 比赛合同。",
            "runtime_validation": _runtime_validation_payload(self),
        }


HOST_SPECIAL_ADAPTERS: dict[str, HostSpecialAdapter] = {
    "codebuddy-cli": _CodeBuddyCliAdapter(
        host_id="codebuddy-cli",
        install_surfaces={
            "official_project_surfaces": (
                "CODEBUDDY.md",
                ".codebuddy/commands/super-dev.md",
                ".codebuddy/commands/super-dev-seeai.md",
                ".codebuddy/skills/super-dev/SKILL.md",
                ".codebuddy/skills/super-dev-seeai/SKILL.md",
            ),
            "official_user_surfaces": (
                "~/.codebuddy/CODEBUDDY.md",
                "~/.codebuddy/commands/super-dev.md",
                "~/.codebuddy/commands/super-dev-seeai.md",
                "~/.codebuddy/skills/super-dev/SKILL.md",
                "~/.codebuddy/skills/super-dev-seeai/SKILL.md",
            ),
            "observed_compatibility_surfaces": (".codebuddy/AGENTS.md",),
        },
        runtime_checklist=(
            "确认当前 CodeBuddy CLI 会话就在目标项目目录中，再触发 `/super-dev`。",
            "确认项目级 `.codebuddy/commands/`、`.codebuddy/skills/` 与兼容 `AGENTS.md` 都被当前会话加载。",
            "确认文档返工与确认门阶段仍然保持在 Super Dev 流程内。",
            "比赛模式验收时，确认 `/super-dev-seeai` 或 `super-dev-seeai:` 会进入半小时时间盒，而不是回到标准长链路。",
            "确认比赛模式会按 P0/P1/P2 控制范围，优先保住主演示路径，再补 wow 点。",
        ),
        pass_criteria=(
            "CodeBuddy CLI 真实读取了项目级 commands、skills 与兼容规则面。",
            "CodeBuddy CLI 的 SEEAI 入口会进入 compact docs + compact spec + full-stack sprint 的比赛合同。",
        ),
        resume_checklist=(
            "CodeBuddy CLI 恢复时要确认仍在目标项目目录，并重新加载 `.codebuddy/commands/` 与 skills。",
            "若正在 SEEAI 比赛模式中恢复，确认继续语句仍回到当前比赛合同，而不是重新开题。",
        ),
        competition_smoke_extra_steps=(
            "确认宿主首轮先给出作品类型、wow 点、P0 主路径和主动放弃项，再声明 30 分钟比赛链路与 P0/P1/P2 取舍。",
        ),
        flow_probe={
            "enabled": True,
            "title": "CodeBuddy 标准流 / SEEAI 双模式验收",
            "summary": "分别验证标准入口和 SEEAI 入口，确认 CodeBuddy CLI 会按不同合同执行，但都持续留在 Super Dev 流程内。",
            "steps": (
                "先用 `/super-dev` 触发一次，确认首轮进入标准 Super Dev research，而不是直接编码。",
                "再用 `/super-dev-seeai` 或 `super-dev-seeai:` 触发一次，确认进入 30 分钟比赛链路，而不是标准 preview gate 流程。",
                "在 SEEAI 会话里继续说“继续改 / 再炫一点 / 补一个功能”，确认仍留在当前比赛冲刺，不会退回普通聊天。",
                "确认 Slash 如果刷新较慢，回退到 `super-dev-seeai:` 仍会进入同一条 SEEAI 比赛合同。",
            ),
            "success_signal": "CodeBuddy CLI 的标准入口和 SEEAI 入口都能稳定进入对应合同，并在多轮修改、确认和恢复时保持流程连续。",
        },
    ),
    "codebuddy": _CodeBuddyIdeAdapter(
        host_id="codebuddy",
        install_surfaces={
            "official_project_surfaces": (
                "CODEBUDDY.md",
                ".codebuddy/rules/super-dev/RULE.mdc",
                ".codebuddy/commands/super-dev.md",
                ".codebuddy/commands/super-dev-seeai.md",
                ".codebuddy/agents/super-dev.md",
                ".codebuddy/skills/super-dev/SKILL.md",
                ".codebuddy/skills/super-dev-seeai/SKILL.md",
            ),
            "official_user_surfaces": (
                "~/.codebuddy/CODEBUDDY.md",
                "~/.codebuddy/commands/super-dev.md",
                "~/.codebuddy/commands/super-dev-seeai.md",
                "~/.codebuddy/agents/super-dev.md",
                "~/.codebuddy/skills/super-dev/SKILL.md",
                "~/.codebuddy/skills/super-dev-seeai/SKILL.md",
            ),
            "observed_compatibility_surfaces": (".codebuddy/rules.md", ".codebuddy/AGENTS.md"),
        },
        runtime_checklist=(
            "确认当前 CodeBuddy IDE Agent Chat 绑定的是目标项目，而不是其他工作区。",
            "确认 `.codebuddy/commands/`、`.codebuddy/agents/` 与 `.codebuddy/skills/` 已在当前会话真实生效。",
            "确认用户继续说“改一下 / 补充 / 继续改”时，CodeBuddy 仍然停留在当前确认门内。",
            "比赛模式验收时，确认 `/super-dev-seeai` 或 `super-dev-seeai:` 进入的是 30 分钟比赛链路，而不是标准 preview gate 流程。",
            "确认比赛模式下固定同一个 Agent Chat 仍能持续沿用当前上下文，不因子会话切换而丢失范围控制。",
        ),
        pass_criteria=(
            "CodeBuddy IDE 在目标工作区真实读取了 commands、agents 与 skills。",
            "CodeBuddy IDE 的 SEEAI 入口会保留 compact 文档确认门，并在 Spec 后直接进入一体化快速开发。",
        ),
        resume_checklist=(
            "CodeBuddy IDE 恢复时要确认 Agent Chat 仍在目标项目，并继续当前确认门而不是重新开题。",
            "若当前是 SEEAI 比赛模式，恢复后仍应保持在同一个比赛冲刺会话里，而不是切回标准模式。",
        ),
        competition_smoke_extra_steps=(
            "确认宿主首轮先给出作品类型、wow 点、P0 主路径和主动放弃项，再声明 30 分钟比赛链路与 P0/P1/P2 取舍。",
        ),
        flow_probe={
            "enabled": True,
            "title": "CodeBuddy 标准流 / SEEAI 双模式验收",
            "summary": "分别验证标准入口和 SEEAI 入口，确认 CodeBuddy 会按不同合同执行，但都持续留在 Super Dev 流程内。",
            "steps": (
                "先用 `/super-dev` 触发一次，确认首轮进入标准 Super Dev research，而不是直接编码。",
                "再用 `/super-dev-seeai` 或 `super-dev-seeai:` 触发一次，确认进入 30 分钟比赛链路，而不是标准 preview gate 流程。",
                "在 SEEAI 会话里继续说“继续改 / 再炫一点 / 补一个功能”，确认仍留在当前比赛冲刺，不会退回普通聊天。",
                "确认 Slash 如果刷新较慢，回退到 `super-dev-seeai:` 仍会进入同一条 SEEAI 比赛合同。",
            ),
            "success_signal": "CodeBuddy 的标准入口和 SEEAI 入口都能稳定进入对应合同，并在多轮修改、确认和恢复时保持流程连续。",
        },
    ),
    "openclaw": _OpenClawAdapter(
        host_id="openclaw",
        install_surfaces={
            "official_project_surfaces": (
                ".openclaw/rules/super-dev.md",
                ".openclaw/commands/super-dev.md",
                ".openclaw/commands/super-dev-seeai.md",
            ),
            "official_user_surfaces": (
                "~/.openclaw/skills/super-dev/SKILL.md",
                "~/.openclaw/skills/super-dev-seeai/SKILL.md",
            ),
            "observed_compatibility_surfaces": (),
        },
        runtime_checklist=(
            "确认当前 OpenClaw Agent 会话绑定的是目标项目工作区，并且 plugin 安装后已经重启 Gateway 或新开会话。",
            "确认 `.openclaw/rules/super-dev.md`、`.openclaw/commands/super-dev.md`、`.openclaw/commands/super-dev-seeai.md` 与 `~/.openclaw/skills/` 已被当前会话真实加载。",
            "确认比赛模式优先可通过 `/super-dev-seeai` 或 `super-dev-seeai:` 进入；如果 slash 面板未刷新，也不会阻塞比赛入口。",
            "确认比赛模式中段不会频繁调用 Tool 打断开发，而是在 sprint 末段再统一做质量/状态收口。",
        ),
        pass_criteria=(
            "OpenClaw 在目标工作区真实读取了 rules、commands 与 skills，且标准模式与 SEEAI 比赛模式都能进入同一条 Super Dev 合同体系。",
            "OpenClaw 的 SEEAI 入口会保留 compact 文档确认门，并在 Spec 后直接进入一体化快速开发与最终 polish。",
        ),
        resume_checklist=(
            "OpenClaw 恢复时要确认重新打开的 Agent 会话仍绑定目标项目，并重新加载 `.openclaw/commands/` 与 skills。",
            "若当前处于 SEEAI 比赛模式，恢复后仍应回到当前比赛冲刺，而不是重新开始普通流水线。",
        ),
        competition_smoke_extra_steps=(
            "如果 `/super-dev-seeai` 还没出现在命令面板，直接用 `super-dev-seeai:` 验收文本入口。",
            "确认宿主首轮先给出作品类型、wow 点、P0 主路径和主动放弃项，再进入 compact 文档。",
        ),
        flow_probe={
            "enabled": True,
            "title": "OpenClaw 标准流 / SEEAI 插件验收",
            "summary": "验证 OpenClaw 插件安装后，标准入口和 SEEAI 比赛入口都能在同一个项目会话中稳定运行。",
            "steps": (
                "安装插件后重启 OpenClaw Gateway 或新开 Agent 会话，先用 `super-dev:` 或 `/super-dev` 触发一次，确认进入标准 Super Dev 流程。",
                "再用 `super-dev-seeai:` 或 `/super-dev-seeai` 触发一次，确认进入 30 分钟比赛链路，并保留 compact docs confirm gate。",
                "在 SEEAI 模式里继续说“继续做 / 做最终 polish / 补一个 wow 点”，确认 OpenClaw 不会切回普通聊天或重新开题。",
                "确认比赛中段不需要频繁切 Tool；只在 sprint 末段使用质量/状态 Tool 做收口即可。",
            ),
            "success_signal": "OpenClaw 的标准入口和 SEEAI 入口都能在当前项目会话里稳定进入对应 Super Dev 合同，并保持比赛冲刺连续性。",
        },
        manual_install_guidance=ManualInstallGuidance(
            title="OpenClaw 手动安装",
            border_style="cyan",
            plain_fallback="请直接在宿主侧手动安装官方插件：openclaw plugins install @super-dev/openclaw-plugin",
            lines=(
                "OpenClaw 不走 `super-dev {command_name}` 统一接入流。",
                "请直接在宿主侧安装原生 npm 插件：",
                "",
                "`openclaw plugins install @super-dev/openclaw-plugin`",
                "",
                "安装完成后再回到 OpenClaw Agent 会话里触发：`super-dev:` / `/super-dev`，比赛模式可用 `super-dev-seeai:` / `/super-dev-seeai`。",
                "{extra_doctor}",
            ),
        ),
    ),
    "workbuddy": _WorkBuddyAdapter(
        host_id="workbuddy",
        adapter_mode_override="skill-only",
        install_surfaces={
            "official_project_surfaces": (),
            "official_user_surfaces": (
                "~/.workbuddy/skills/super-dev/SKILL.md",
            ),
            "observed_compatibility_surfaces": (),
        },
        runtime_checklist=(
            "确认任务会话已经手动启用 Super Dev 标准版与 SEEAI 比赛版 Skills。",
            "确认自然语言入口可用且保持当前项目上下文。",
            "确认恢复后仍继续同一个 task/chat，而不是跳转成新任务。",
        ),
        pass_criteria=(
            "手动启用的 Skills 可稳定接管标准流程与 SEEAI 比赛流程。",
            "自然语言入口可在当前会话中直接触发。",
            "恢复会话后仍可继续同一作品任务。",
        ),
        resume_checklist=(
            "检查当前任务是否已经锁定作品类型。",
            "检查 compact docs 或 spec 是否已写入。",
            "检查是否需要继续当前比赛 sprint。",
        ),
        competition_smoke_extra_steps=(
            "确认 WorkBuddy 首轮先给出作品类型、wow 点、P0 主路径和主动放弃项，再进入 fast research 与 compact 文档。",
        ),
        manual_install_guidance=ManualInstallGuidance(
            title="WorkBuddy 手动安装",
            border_style="yellow",
            plain_fallback="请直接在 WorkBuddy 内手动启用 Super Dev 标准版与 SEEAI 比赛版 Skills。",
            lines=(
                "WorkBuddy 不走 `super-dev {command_name}` 统一接入流。",
                "请直接在 WorkBuddy 的技能市场/技能导入能力中手动启用：",
                "",
                "`Super Dev`（标准流程）",
                "`Super Dev SEEAI`（比赛模式）",
                "",
                "启用完成后，在 WorkBuddy 当前任务会话里触发：`super-dev:`；比赛模式使用 `super-dev-seeai:`。",
                "{extra_doctor}",
            ),
        ),
    ),
}


def get_special_adapter(host_id: str) -> HostSpecialAdapter | None:
    return HOST_SPECIAL_ADAPTERS.get(host_id)


def build_special_usage_profile(context: SpecialAdapterContext) -> dict[str, object] | None:
    adapter = get_special_adapter(context.target)
    if adapter is None:
        return None
    return adapter.build_usage_profile(context)


def get_special_install_surfaces(host_id: str) -> dict[str, list[str]] | None:
    adapter = get_special_adapter(host_id)
    if adapter is None or not adapter.install_surfaces:
        return None
    return {key: list(value) for key, value in adapter.install_surfaces.items()}


def get_competition_smoke_extra_steps(host_id: str) -> tuple[str, ...]:
    adapter = get_special_adapter(host_id)
    if adapter is None:
        return ()
    return adapter.competition_smoke_extra_steps


def get_runtime_checklist(host_id: str) -> tuple[str, ...]:
    adapter = get_special_adapter(host_id)
    if adapter is None:
        return ()
    return adapter.runtime_checklist


def get_pass_criteria(host_id: str) -> tuple[str, ...]:
    adapter = get_special_adapter(host_id)
    if adapter is None:
        return ()
    return adapter.pass_criteria


def get_resume_checklist(host_id: str) -> tuple[str, ...]:
    adapter = get_special_adapter(host_id)
    if adapter is None:
        return ()
    return adapter.resume_checklist


def get_special_flow_probe(host_id: str) -> dict[str, Any] | None:
    adapter = get_special_adapter(host_id)
    if adapter is None or not adapter.flow_probe:
        return None
    return dict(adapter.flow_probe)


def render_manual_install_guidance(
    *,
    host_id: str,
    command_name: str,
    docs: list[str] | tuple[str, ...],
) -> dict[str, Any] | None:
    adapter = get_special_adapter(host_id)
    guidance = adapter.manual_install_guidance if adapter is not None else None
    if guidance is None:
        return None

    extra_doctor = (
        f"如需核对接入说明，可再执行 `super-dev doctor --host {host_id}`。"
        if command_name != "doctor"
        else ""
    )
    lines: list[str] = []
    for line in guidance.lines:
        rendered = line.format(command_name=command_name, extra_doctor=extra_doctor).strip()
        if rendered or not line:
            lines.append(rendered)
    while lines and not lines[-1]:
        lines.pop()
    if docs:
        lines.append("")
        lines.append("官方文档:")
        for url in docs[:2]:
            lines.append(f"- {url}")
    return {
        "title": guidance.title,
        "lines": lines,
        "border_style": guidance.border_style,
        "plain_fallback": guidance.plain_fallback,
    }


def get_adapter_mode_override(host_id: str) -> str:
    adapter = get_special_adapter(host_id)
    if adapter is None:
        return ""
    return adapter.adapter_mode_override


__all__ = [
    "HostSpecialAdapter",
    "ManualInstallGuidance",
    "SpecialAdapterContext",
    "build_special_usage_profile",
    "get_adapter_mode_override",
    "get_competition_smoke_extra_steps",
    "get_pass_criteria",
    "get_resume_checklist",
    "get_special_adapter",
    "get_special_flow_probe",
    "get_special_install_surfaces",
    "get_runtime_checklist",
    "render_manual_install_guidance",
]
