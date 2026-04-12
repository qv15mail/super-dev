from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .frameworks import summarize_framework_playbook
from .host_adapters import get_special_flow_probe
from .review_state import (
    load_architecture_revision,
    load_docs_confirmation,
    load_preview_confirmation,
    load_quality_revision,
    load_ui_revision,
    load_workflow_state,
)

PHASE_CHAIN: tuple[tuple[str, str, str], ...] = (
    ("research", "同类产品研究", "让宿主先联网研究同类产品，并沉淀 research 文档。"),
    ("core_docs", "三份核心文档", "生成 PRD、架构、UIUX 三份核心文档。"),
    ("confirmation_gate", "等待用户确认", "三文档生成后，必须先向用户汇报并等待确认或修改。"),
    ("spec", "Spec 与任务清单", "用户确认后，创建 proposal 与 tasks.md。"),
    ("frontend", "前端实现与运行验证", "先实现前端主流程，并运行验证可演示状态。"),
    ("preview_gate", "等待预览确认", "前端可演示后，必须先等待用户确认预览或继续修改。"),
    ("backend", "后端实现与联调", "在前端预览确认后，再进入后端、认证、数据层与联调。"),
    ("quality", "质量门禁", "执行红队审查、UI 审查与质量门禁。"),
    ("delivery", "交付与发布", "生成交付包、部署配置和审计产物。"),
)

WORKFLOW_MODE_LABELS: dict[str, str] = {
    "start": "开始新流程",
    "continue": "继续当前流程",
    "revise": "返工/补充当前流程",
    "release": "发布闭环",
}

WORKFLOW_MODE_DEFAULT_SHORTCUTS: dict[str, list[str]] = {
    "start": ["开始这个项目", "先研究同类产品", "先把宿主接好"],
    "continue": ["继续", "下一步", "按当前流程往下做"],
    "revise": ["这里补一下", "这个不对重做", "确认后继续"],
    "release": ["开始质量检查", "重新生成证据包", "准备交付"],
}

WORKFLOW_STATUS_CONTINUITY_RULES: dict[str, list[str]] = {
    "waiting_docs_confirmation": [
        "当前停在三文档确认门。用户的“修改、补充、重写、继续完善、这里不对”都属于文档修订，不是退出 Super Dev 流程。",
        "只要用户还没明确确认，就持续更新 PRD、Architecture、UIUX，重新总结变化，然后再次等待明确确认。",
        "只有用户明确表达“确认/通过/进入下一阶段”时，才允许从 docs_confirm 进入 Spec。",
    ],
    "waiting_ui_revision": [
        "当前停在 UI 改版门。用户的任何视觉、交互、布局、信息层级修改都属于本轮 UI 返工，不是普通聊天。",
        "每次修改后都要回到 UIUX / 前端闭环，重新总结变化并再次等待确认。",
    ],
    "waiting_preview_confirmation": [
        "当前停在前端预览确认门。用户的“再改一下 / 补一块 / 这里不对 / 继续调 UI”都属于本轮预览返工，不是退出 Super Dev 流程。",
        "每次修改后都要回到前端预览闭环，重新生成预览并再次等待明确确认。",
        "只有用户明确表达“预览确认 / 可以进入后端 / 继续下一阶段”时，才允许从 preview_confirm 进入 backend。",
    ],
    "waiting_architecture_revision": [
        "当前停在架构返工门。用户补充技术要求、边界条件或实现路线时，必须留在架构返工流程里。",
        "先更新架构文档，再同步任务和实现，完成后重新汇报并再次等待确认。",
    ],
    "waiting_quality_revision": [
        "当前停在质量整改门。用户提出新的安全、稳定性、测试或代码规范问题时，必须留在质量整改流程里。",
        "修复后重新过质量门禁，再汇报结果，而不是切回普通对话。",
    ],
}


def build_host_entry_prompts(
    *,
    target: str,
    instruction: str,
    supports_slash: bool = False,
    flow_variant: str = "standard",
) -> dict[str, Any]:
    escaped = instruction.replace('"', '\\"')
    normalized_variant = str(flow_variant).strip().lower()
    slash_command = "/super-dev-seeai" if normalized_variant == "seeai" else "/super-dev"
    cli_skill = "$super-dev-seeai" if normalized_variant == "seeai" else "$super-dev"
    fallback_prefix = "super-dev-seeai:" if normalized_variant == "seeai" else "super-dev:"
    fallback = f"{fallback_prefix} {instruction}"
    if target == "codex-cli":
        return {
            "preferred_entry": "app_desktop",
            "preferred_entry_label": "App/Desktop",
            "entry_prompts": {
                "app_desktop": f'{slash_command} "{escaped}"',
                "cli": f'{cli_skill} "{escaped}"',
                "fallback": fallback,
            },
        }
    if supports_slash:
        return {
            "preferred_entry": "slash",
            "preferred_entry_label": "Slash",
            "entry_prompts": {
                "slash": f'{slash_command} "{escaped}"',
                "fallback": fallback,
            },
        }
    return {
        "preferred_entry": "fallback",
        "preferred_entry_label": "Text",
        "entry_prompts": {"fallback": fallback},
    }


def build_host_flow_contract(target: str) -> dict[str, Any]:
    if target == "codex-cli":
        return {
            "consistent_flow_required": True,
            "summary": "无论使用 Codex App/Desktop 的 `/super-dev`、Codex CLI 的 `$super-dev`，还是 `super-dev:` 回退入口，都必须进入同一条 Super Dev 流程。",
            "preferred_entry_order": ["app_desktop", "cli", "fallback"],
            "preferred_entry_labels": {
                "app_desktop": "App/Desktop",
                "cli": "CLI",
                "fallback": "Fallback",
            },
            "continuity_rule": "长流程里继续修改、补充、确认或恢复时，优先沿用当前入口面，不要切回普通聊天。",
            "restart_rule": "接入或更新后必须彻底重开 Codex，新会话才会重新加载 AGENTS、Skills 和 repo plugin enhancement。",
        }
    return {
        "consistent_flow_required": True,
        "summary": "宿主支持的触发入口必须持续汇入同一条 Super Dev 流程，而不是在修改、确认或恢复时退回普通聊天。",
        "preferred_entry_order": [],
        "preferred_entry_labels": {},
        "continuity_rule": "长流程里继续修改、补充、确认或恢复时，保持在当前 Super Dev 流程。",
        "restart_rule": "",
    }


def build_host_flow_probe(target: str) -> dict[str, Any]:
    if target == "codex-cli":
        return {
            "enabled": True,
            "title": "Codex 三入口同流程验收",
            "summary": "分别用 App/Desktop、CLI、fallback 入口触发一次，确认它们都进入同一条 Super Dev 流程，并在后续修改/确认时不掉回普通聊天。",
            "steps": [
                "在 Codex App/Desktop 里从 `/` 列表选择 `super-dev`，确认第一轮直接进入 Super Dev 流程。",
                "在 Codex CLI 里输入 `$super-dev`，确认它进入的是同一条流程，而不是另一套独立上下文。",
                "在已有自然语言上下文里输入 `super-dev: 继续当前项目的 Super Dev 流程`，确认仍汇入同一条流程。",
                "继续说“改一下 / 补充 / 确认 / 通过”，确认三种入口后续都不会退回普通聊天。",
            ],
            "success_signal": "三种入口最终都进入同一条 Super Dev 流程，并且多轮修改、确认和恢复时保持在流程内。",
        }
    adapter_probe = get_special_flow_probe(target)
    if adapter_probe is not None:
        probe = dict(adapter_probe)
        probe["steps"] = list(probe.get("steps", ()))
        return probe
    return {
        "enabled": False,
        "title": "",
        "summary": "",
        "steps": [],
        "success_signal": "",
    }


def load_framework_playbook_summary(project_dir: Path) -> dict[str, Any]:
    project_dir = Path(project_dir).resolve()
    output_dir = project_dir / "output"
    candidates = sorted(output_dir.glob("*-ui-contract.json"))
    if not candidates:
        return {}
    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    playbook = payload.get("framework_playbook")
    return summarize_framework_playbook(playbook, limit=4)


def workflow_mode_label(workflow_mode: str) -> str:
    normalized = str(workflow_mode).strip().lower()
    return WORKFLOW_MODE_LABELS.get(normalized, normalized or "继续当前流程")


def workflow_mode_shortcuts(
    workflow_mode: str,
    *,
    examples: list[str] | None = None,
    limit: int = 4,
) -> list[str]:
    cleaned_examples = [str(item).strip() for item in (examples or []) if str(item).strip()]
    defaults = WORKFLOW_MODE_DEFAULT_SHORTCUTS.get(
        str(workflow_mode).strip().lower(),
        ["继续", "下一步"],
    )
    merged: list[str] = []
    for item in [*cleaned_examples, *defaults]:
        if item and item not in merged:
            merged.append(item)
        if len(merged) >= limit:
            break
    return merged


def workflow_continuity_rules(status: str) -> list[str]:
    normalized = str(status).strip().lower()
    if normalized in WORKFLOW_STATUS_CONTINUITY_RULES:
        return list(WORKFLOW_STATUS_CONTINUITY_RULES[normalized])
    if normalized in {
        "ready",
        "waiting_confirmation",
        "delivery_closure_incomplete",
        "product_revision_required",
        "proof_pack_incomplete",
    }:
        return [
            "当前仓库已经有活动的 Super Dev 流程。后续自然语言需求默认继续当前流程，不要切回普通聊天。",
            "除非用户明确说“取消当前流程、重新开始、切回普通聊天”，否则任何追问、补充约束、局部修改都视为当前流程内动作。",
        ]
    return [
        "只要仓库里还有活动的 Super Dev 上下文，后续自然语言需求默认继续当前流程，而不是切回普通聊天。",
    ]


def _has_any(candidates: list[Path]) -> bool:
    return any(path.exists() for path in candidates)


def detect_flow_variant(project_dir: Path) -> str:
    payload = load_workflow_state(project_dir) or {}
    for key in ("flow_variant", "entry_variant", "pipeline_variant", "mode_variant"):
        value = str(payload.get(key, "")).strip().lower()
        if value == "seeai":
            return "seeai"
    current_step = str(payload.get("current_step_label", "")).strip().lower()
    if "seeai" in current_step:
        return "seeai"
    return "standard"


def _latest_json(files: list[Path]) -> tuple[dict[str, Any], str]:
    if not files:
        return {}, ""
    latest = max(files, key=lambda path: path.stat().st_mtime)
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception:
        payload = {}
    return payload if isinstance(payload, dict) else {}, str(latest)


def _normalize_review_payload(
    payload: dict[str, Any] | None, *, default_status: str = "pending_review"
) -> dict[str, Any]:
    payload = payload or {}
    return {
        "status": str(payload.get("status", "")).strip() or default_status,
        "comment": str(payload.get("comment", "")).strip(),
        "run_id": str(payload.get("run_id", "")).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "actor": str(payload.get("actor", "")).strip(),
        "exists": bool(payload),
    }


def _build_action_card(
    *, workflow_status: str, recommended_command: str, blocker: str
) -> dict[str, Any]:
    default_exit = "只有用户明确说取消当前流程、重新开始或切回普通聊天，才允许离开当前流程。"
    mapping: dict[str, dict[str, Any]] = {
        "missing_research": {
            "mode": "start",
            "title": "先启动研究阶段",
            "user_action": "先让宿主进入 Super Dev 研究阶段，产出 research 文档。",
            "examples": ["做一个 X", "先研究同类产品", "开始这个项目"],
        },
        "missing_core_docs": {
            "mode": "start",
            "title": "先补齐三份核心文档",
            "user_action": "先完成 PRD、Architecture、UIUX 三文档，不要直接开始编码。",
            "examples": ["先把文档补齐", "先做 PRD", "先出架构和 UIUX"],
        },
        "waiting_docs_confirmation": {
            "mode": "revise",
            "title": "等待三文档确认",
            "user_action": "继续围绕 PRD、Architecture、UIUX 修改或确认，不要跳到 Spec/编码。",
            "examples": ["这里补一下", "这块文档不对", "文档确认，可以继续"],
        },
        "missing_spec": {
            "mode": "continue",
            "title": "进入 Spec 与任务拆解",
            "user_action": "根据已确认文档生成 proposal 与 tasks.md，进入执行计划。",
            "examples": ["继续做 Spec", "开始拆任务", "进入执行阶段"],
        },
        "missing_frontend": {
            "mode": "continue",
            "title": "先做前端与运行验证",
            "user_action": "先完成前端主流程和运行验证，再考虑后端和交付。",
            "examples": ["先做前端", "先把页面跑起来", "先做可演示版本"],
        },
        "waiting_preview_confirmation": {
            "mode": "revise",
            "title": "等待前端预览确认",
            "user_action": "继续改前端或确认预览，确认前不要进入后端和后续阶段。",
            "examples": ["这个页面再改一下", "预览可以继续", "继续调 UI"],
        },
        "missing_backend": {
            "mode": "continue",
            "title": "进入后端实现与联调",
            "user_action": "在前端预览确认后进入后端、数据层和联调。",
            "examples": ["继续做后端", "接接口", "联调数据层"],
        },
        "waiting_ui_revision": {
            "mode": "revise",
            "title": "等待 UI 改版闭环",
            "user_action": "先更新 UIUX 和前端实现，完成 UI 返工后再恢复主流程。",
            "examples": ["UI 重做", "页面太像模板", "布局再调一下"],
        },
        "waiting_architecture_revision": {
            "mode": "revise",
            "title": "等待架构返工闭环",
            "user_action": "先改架构文档和实现拆解，再恢复主流程。",
            "examples": ["架构不对", "这里要换技术路线", "模块边界要重做"],
        },
        "waiting_quality_revision": {
            "mode": "revise",
            "title": "等待质量整改闭环",
            "user_action": "先修质量/安全/测试问题，再恢复发布闭环。",
            "examples": ["这里有 bug", "安全不行", "补测试再继续"],
        },
        "missing_quality": {
            "mode": "release",
            "title": "补齐质量门禁",
            "user_action": "先补齐红队、UI review、quality gate，再继续交付。",
            "examples": ["开始质量检查", "跑门禁", "补齐发布前检查"],
        },
        "missing_delivery": {
            "mode": "release",
            "title": "补齐交付与发布产物",
            "user_action": "先生成 proof-pack、delivery manifest、发布演练与部署产物。",
            "examples": ["准备交付", "生成发布包", "做发布演练"],
        },
        "delivery_closure_incomplete": {
            "mode": "release",
            "title": "补齐交付闭环证据",
            "user_action": "先补齐缺失的质量和发布证据，再进入最终交付。",
            "examples": ["补齐证据", "重新跑 release readiness", "重新生成 proof-pack"],
        },
        "proof_pack_incomplete": {
            "mode": "release",
            "title": "重新生成证据包",
            "user_action": "先补齐 proof-pack 依赖证据，再继续发布。",
            "examples": ["重新打包证据", "补 delivery 材料", "重新生成 proof-pack"],
        },
        "product_revision_required": {
            "mode": "revise",
            "title": "处理产品审查修订项",
            "user_action": "先处理产品审查发现项，再恢复主流程。",
            "examples": ["按审查意见修改", "补产品缺口", "先修产品逻辑"],
        },
        "ready": {
            "mode": "continue",
            "title": "继续当前流程",
            "user_action": "按当前状态面板继续，不要重新开一轮普通聊天。",
            "examples": ["继续", "下一步", "按当前流程往下做"],
        },
    }
    action = dict(mapping.get(workflow_status, mapping["ready"]))
    raw_examples = action.get("examples")
    examples = raw_examples if isinstance(raw_examples, list) else []
    action["machine_action"] = recommended_command
    action["blocker"] = blocker
    action["exit_condition"] = default_exit
    action["examples"] = [str(item).strip() for item in examples if str(item).strip()]
    action["shortcuts"] = workflow_mode_shortcuts(
        str(action.get("mode", "")), examples=action["examples"]
    )
    action["continuity_rules"] = workflow_continuity_rules(workflow_status)
    return action


def build_workflow_scenario_cards(summary: dict[str, Any]) -> list[dict[str, Any]]:
    workflow_status = str(summary.get("workflow_status", "")).strip()
    workflow_mode = str(summary.get("workflow_mode", "")).strip() or "continue"
    recommended_command = (
        str(summary.get("recommended_command", "")).strip() or "在宿主里说“继续当前流程”"
    )
    action_card = summary.get("action_card")
    action_title = ""
    action_examples: list[str] = []
    user_message = "继续"
    if isinstance(action_card, dict):
        action_title = str(action_card.get("title", "")).strip()
        raw_examples = action_card.get("examples")
        if isinstance(raw_examples, list):
            action_examples = [str(item).strip() for item in raw_examples if str(item).strip()]
        user_message = (
            action_examples[0]
            if action_examples
            else (
                workflow_mode_shortcuts(
                    str(action_card.get("mode", "")).strip() or workflow_mode,
                    examples=action_examples,
                    limit=1,
                )[0]
                if workflow_mode_shortcuts(
                    str(action_card.get("mode", "")).strip() or workflow_mode,
                    examples=action_examples,
                    limit=1,
                )
                else "继续"
            )
        )

    stage_specific_titles: dict[str, str] = {
        "waiting_docs_confirmation": "当前在三文档确认门里继续修改",
        "waiting_preview_confirmation": "当前在前端预览确认门里继续修改",
        "waiting_ui_revision": "当前先处理 UI 改版",
        "waiting_architecture_revision": "当前先处理架构返工",
        "waiting_quality_revision": "当前先处理质量整改",
        "missing_spec": "当前进入 Spec 与任务拆解",
        "missing_frontend": "当前先推进前端实现",
        "missing_backend": "当前先推进后端与联调",
        "missing_quality": "当前先补质量门禁",
        "missing_delivery": "当前先补交付与发布",
        "delivery_closure_incomplete": "当前先补交付闭环证据",
        "proof_pack_incomplete": "当前先重建证据包",
    }
    stage_specific_when: dict[str, str] = {
        "waiting_docs_confirmation": "产品补需求、文档要重写或还没确认时",
        "waiting_preview_confirmation": "前端页面要再改、还没确认预览时",
        "waiting_ui_revision": "用户明确要求 UI 重做时",
        "waiting_architecture_revision": "用户明确要求改架构或技术路线时",
        "waiting_quality_revision": "质量、安全、测试问题要先修时",
        "missing_spec": "三文档刚确认，准备进入执行计划时",
        "missing_frontend": "文档和 Spec 已就绪，准备开始前端时",
        "missing_backend": "前端预览已确认，准备接后端时",
        "missing_quality": "功能已完成，准备做发布前检查时",
        "missing_delivery": "质量门禁已通过，准备交付时",
        "delivery_closure_incomplete": "proof-pack / readiness 还没闭环时",
        "proof_pack_incomplete": "交付证据包不完整时",
    }

    cards: list[dict[str, Any]] = [
        {
            "id": "resume_workday",
            "title": "第二天回来继续开发",
            "when": "关掉宿主、重启电脑、第二天继续时",
            "user_message": "继续当前流程",
            "cli_command": "回到宿主里说“继续当前流程”",
            "recommended": workflow_mode in {"continue", "revise", "release"},
        },
        {
            "id": "know_next",
            "title": "我只想知道现在先做什么",
            "when": "不想自己判断流程状态时",
            "user_message": "下一步",
            "cli_command": "回到宿主里说“现在下一步是什么”",
            "recommended": False,
        },
    ]

    if workflow_status:
        cards.append(
            {
                "id": "current_gate_or_stage",
                "title": stage_specific_titles.get(
                    workflow_status, action_title or "按当前流程继续"
                ),
                "when": stage_specific_when.get(
                    workflow_status, "当前流程还没结束，需要继续推进时"
                ),
                "user_message": user_message,
                "cli_command": recommended_command,
                "recommended": workflow_mode == "revise" or workflow_status.startswith("waiting_"),
            }
        )

    cards.append(
        {
            "id": "resume_pipeline",
            "title": "本地流程跑到一半中断后恢复",
            "when": "run / pipeline 中途失败、终端断开或想接着跑时",
            "user_message": "恢复本地流程",
            "cli_command": "回到宿主里说“继续当前流程，不要重新开题”",
            "recommended": workflow_status
            in {"missing_backend", "missing_quality", "missing_delivery"},
        }
    )

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in cards:
        scenario_id = str(item.get("id", "")).strip()
        if not scenario_id or scenario_id in seen:
            continue
        seen.add(scenario_id)
        deduped.append(item)
    return deduped


def detect_pipeline_summary(project_dir: Path, run: dict[str, Any] | None = None) -> dict[str, Any]:
    project_dir = Path(project_dir).resolve()
    output_dir = project_dir / "output"
    changes_dir = project_dir / ".super-dev" / "changes"
    flow_variant = detect_flow_variant(project_dir)

    research_done = any(output_dir.glob("*-research.md"))
    prd_done = any(output_dir.glob("*-prd.md"))
    architecture_done = any(output_dir.glob("*-architecture.md"))
    uiux_done = any(output_dir.glob("*-uiux.md"))
    docs_done = prd_done and architecture_done and uiux_done
    spec_done = any(changes_dir.glob("*/proposal.md")) and any(changes_dir.glob("*/tasks.md"))

    frontend_runtime_payload, frontend_runtime_path = _latest_json(
        sorted(output_dir.glob("*-frontend-runtime.json"))
    )
    frontend_runtime_passed = bool(frontend_runtime_payload.get("passed", False))
    frontend_done = frontend_runtime_passed

    backend_done = _has_any(
        [
            project_dir / "backend" / "src",
            project_dir / "backend" / "package.json",
            project_dir / "backend" / "pyproject.toml",
            project_dir / "backend" / "requirements.txt",
            project_dir / "backend" / "go.mod",
        ]
    )
    quality_done = any(output_dir.glob("*-quality-gate.md")) or any(
        output_dir.glob("*-ui-review.md")
    )

    delivery_manifest_payload, delivery_manifest_path = _latest_json(
        sorted((output_dir / "delivery").glob("*-delivery-manifest.json"))
        if (output_dir / "delivery").exists()
        else []
    )
    delivery_manifest_ready = (
        str(delivery_manifest_payload.get("status", "")).strip().lower() == "ready"
    )

    rehearsal_payload, rehearsal_report_path = _latest_json(
        sorted((output_dir / "rehearsal").glob("*-rehearsal-report.json"))
        if (output_dir / "rehearsal").exists()
        else []
    )
    rehearsal_report_passed = bool(rehearsal_payload.get("passed", False))
    delivery_done = delivery_manifest_ready and rehearsal_report_passed

    knowledge_payload, knowledge_cache_path = _latest_json(
        sorted((output_dir / "knowledge-cache").glob("*-knowledge-bundle.json"))
        if (output_dir / "knowledge-cache").exists()
        else []
    )
    knowledge_summary: dict[str, Any] = {
        "enabled": bool((project_dir / "knowledge").exists()),
        "cache_exists": bool(knowledge_cache_path),
        "cache_path": knowledge_cache_path,
        "local_hits": 0,
        "web_hits": 0,
        "top_local_sources": [],
    }
    if knowledge_payload:
        local_knowledge = knowledge_payload.get("local_knowledge", [])
        web_knowledge = knowledge_payload.get("web_knowledge", [])
        if isinstance(local_knowledge, list):
            knowledge_summary["local_hits"] = len(local_knowledge)
            knowledge_summary["top_local_sources"] = [
                str(item.get("source", ""))
                for item in local_knowledge[:3]
                if isinstance(item, dict) and str(item.get("source", "")).strip()
            ]
        if isinstance(web_knowledge, list):
            knowledge_summary["web_hits"] = len(web_knowledge)

    docs_confirmation = _normalize_review_payload(load_docs_confirmation(project_dir))
    preview_confirmation = _normalize_review_payload(load_preview_confirmation(project_dir))
    ui_revision = _normalize_review_payload(load_ui_revision(project_dir))
    architecture_revision = _normalize_review_payload(load_architecture_revision(project_dir))
    quality_revision = _normalize_review_payload(load_quality_revision(project_dir))

    explicit_docs_revision_requested = docs_confirmation["status"] == "revision_requested"
    explicit_ui_revision_requested = ui_revision["status"] == "revision_requested"
    explicit_architecture_revision_requested = (
        architecture_revision["status"] == "revision_requested"
    )
    explicit_quality_revision_requested = quality_revision["status"] == "revision_requested"
    explicit_preview_revision_requested = preview_confirmation["status"] == "revision_requested"

    docs_confirmed = docs_confirmation["status"] == "confirmed"
    preview_confirmed = preview_confirmation["status"] == "confirmed"
    docs_confirmation_waiting = docs_done and not (
        docs_confirmed
        or spec_done
        or frontend_done
        or backend_done
        or quality_done
        or delivery_done
    )
    preview_confirmation_waiting = (
        flow_variant != "seeai"
        and frontend_done
        and not (
            preview_confirmed
            or backend_done
            or quality_done
            or delivery_done
            or explicit_preview_revision_requested
        )
    )

    run = run or {}
    run_status = str(run.get("status", "unknown")).strip().lower()
    run_results = run.get("results") or []
    running_phase = None
    if run_status in {"running", "cancelling"}:
        completed = set(run.get("completed_phases") or [])
        requested = run.get("requested_phases") or []
        running_phase = next(
            (phase_id for phase_id in requested if phase_id not in completed), None
        )

    def _stage_status(done: bool, *, waiting: bool = False, running: bool = False) -> str:
        if done:
            return "completed"
        if running:
            return "running"
        if waiting:
            return "waiting"
        return "pending"

    stages = [
        {
            "id": "research",
            "name": "同类产品研究",
            "status": _stage_status(
                research_done,
                running=running_phase in {"discovery", "intelligence"} and not research_done,
            ),
            "description": PHASE_CHAIN[0][2],
        },
        {
            "id": "core_docs",
            "name": "三份核心文档",
            "status": _stage_status(
                docs_done, running=running_phase == "drafting" and not docs_done
            ),
            "description": PHASE_CHAIN[1][2],
        },
        {
            "id": "confirmation_gate",
            "name": "等待用户确认",
            "status": _stage_status(
                docs_confirmed
                or spec_done
                or frontend_done
                or backend_done
                or quality_done
                or delivery_done,
                waiting=docs_confirmation_waiting or explicit_docs_revision_requested,
            ),
            "description": PHASE_CHAIN[2][2],
        },
        {
            "id": "spec",
            "name": "Spec 与任务清单",
            "status": _stage_status(
                spec_done,
                running=running_phase == "drafting"
                and docs_done
                and docs_confirmed
                and not spec_done,
            ),
            "description": PHASE_CHAIN[3][2],
        },
        {
            "id": "frontend",
            "name": "前端实现与运行验证",
            "status": _stage_status(
                frontend_done,
                running=running_phase == "delivery" and spec_done and not frontend_done,
            ),
            "description": PHASE_CHAIN[4][2],
        },
        {
            "id": "preview_gate",
            "name": "等待预览确认",
            "status": _stage_status(
                preview_confirmed or backend_done or quality_done or delivery_done,
                waiting=preview_confirmation_waiting or explicit_preview_revision_requested,
            ),
            "description": PHASE_CHAIN[5][2],
        },
        {
            "id": "backend",
            "name": "后端实现与联调",
            "status": _stage_status(
                backend_done,
                running=running_phase == "delivery"
                and frontend_done
                and preview_confirmed
                and not backend_done,
            ),
            "description": PHASE_CHAIN[6][2],
        },
        {
            "id": "quality",
            "name": "质量门禁",
            "status": _stage_status(
                quality_done,
                running=running_phase in {"redteam", "qa"} and backend_done and not quality_done,
            ),
            "description": PHASE_CHAIN[7][2],
        },
        {
            "id": "delivery",
            "name": "交付与发布",
            "status": _stage_status(
                delivery_done,
                running=running_phase == "deployment" and quality_done and not delivery_done,
            ),
            "description": PHASE_CHAIN[8][2],
        },
    ]
    current_stage = next(
        (stage for stage in stages if stage["status"] in {"running", "waiting", "pending"}),
        stages[-1],
    )
    if all(stage["status"] == "completed" for stage in stages):
        current_stage = stages[-1]

    blocker = ""
    checkpoint_status = "ready"
    recommended_command = "在宿主里说“继续当前流程”"
    evidence = "未检测到更高优先级阻断项"
    if explicit_docs_revision_requested:
        blocker = "用户已要求修改三份核心文档，当前应先修正文档并再次提交确认。"
        checkpoint_status = "waiting_docs_confirmation"
        recommended_command = "在宿主里继续修正文档；确认后直接说“文档确认，可以继续”"
        evidence = "docs confirmation revision_requested"
    elif explicit_preview_revision_requested:
        blocker = "当前预览评审要求继续修改前端，应先更新 UI/前端实现并再次提交预览确认。"
        checkpoint_status = "waiting_preview_confirmation"
        recommended_command = "在宿主里继续修改前端；确认后直接说“前端预览确认，可以继续”"
        evidence = "preview confirmation revision_requested"
    elif explicit_ui_revision_requested:
        blocker = (
            "当前存在 UI 改版请求，应先更新 output/*-uiux.md，并重新执行前端运行验证与 UI review。"
        )
        checkpoint_status = "waiting_ui_revision"
        recommended_command = "在宿主里完成 UI 改版后直接说“UI 改版已完成，继续当前流程”"
        evidence = "ui revision requested"
    elif explicit_architecture_revision_requested:
        blocker = "当前存在架构返工请求，应先更新 output/*-architecture.md，并同步调整实现方案与任务拆解。"
        checkpoint_status = "waiting_architecture_revision"
        recommended_command = "在宿主里完成架构返工后直接说“架构调整已完成，继续当前流程”"
        evidence = "architecture revision requested"
    elif explicit_quality_revision_requested:
        blocker = "当前存在质量返工请求，应先修复质量/安全问题，并重新执行 quality gate 与 release proof-pack。"
        checkpoint_status = "waiting_quality_revision"
        recommended_command = "在宿主里完成质量整改后直接说“质量整改已完成，继续当前流程”"
        evidence = "quality revision requested"
    elif docs_confirmation_waiting:
        blocker = "三份核心文档已生成，当前必须等待用户确认或提出修改意见。"
        checkpoint_status = "waiting_docs_confirmation"
        recommended_command = "在宿主里确认三文档；如果通过，直接说“文档确认，可以继续”"
        evidence = "docs confirmation pending"
    elif preview_confirmation_waiting:
        blocker = "前端预览已可演示，当前必须先等待用户确认预览或提出继续修改。"
        checkpoint_status = "waiting_preview_confirmation"
        recommended_command = "在宿主里确认前端预览；如果通过，直接说“前端预览确认，可以继续”"
        evidence = "preview confirmation pending"
    elif not research_done:
        blocker = "当前尚未完成同类产品研究。"
        checkpoint_status = "missing_research"
        recommended_command = "在宿主里启动 Super Dev，先做 research，再产出三文档"
        evidence = "缺少 output/*-research.md"
    elif not docs_done:
        blocker = "当前尚未完成 PRD、架构、UIUX 三份核心文档。"
        checkpoint_status = "missing_core_docs"
        recommended_command = "在宿主里继续 Super Dev，先补齐 PRD、Architecture、UIUX"
        evidence = "缺少 output/*-prd.md / *-architecture.md / *-uiux.md"
    elif not spec_done:
        blocker = "当前尚未创建 Spec proposal 与 tasks.md。"
        checkpoint_status = "missing_spec"
        recommended_command = "在宿主里说“文档确认，可以继续，开始 Spec 与任务拆解”"
        evidence = "缺少 .super-dev/changes/*/proposal.md / tasks.md"
    elif not frontend_done:
        blocker = "当前尚未完成前端实现与运行验证。"
        checkpoint_status = "missing_frontend"
        if flow_variant == "seeai":
            recommended_command = "在宿主里说“继续当前 SEEAI 流程，开始一体化快速开发”"
        else:
            recommended_command = "在宿主里说“继续当前流程，进入前端实现与运行验证”"
        evidence = "缺少通过的 output/*-frontend-runtime.json"
    elif not backend_done:
        blocker = "当前尚未完成后端实现与联调。"
        checkpoint_status = "missing_backend"
        if flow_variant == "seeai":
            recommended_command = "在宿主里说“继续当前 SEEAI 流程，补齐必要后端并统一 polish”"
        else:
            recommended_command = "在宿主里说“前端预览已确认，继续后端实现与联调”"
        evidence = "缺少 backend 实现证据"
    elif not quality_done:
        blocker = "当前尚未完成红队 / UI / 质量门禁。"
        checkpoint_status = "missing_quality"
        if flow_variant == "seeai":
            recommended_command = "在宿主里说“继续当前 SEEAI 流程，做最终 polish 和演示检查”"
        else:
            recommended_command = "在宿主里说“继续当前流程，进入质量门禁与发布前检查”"
        evidence = "缺少 quality gate / ui review 证据"
    elif not delivery_done:
        checkpoint_status = "missing_delivery"
        recommended_command = "在宿主里说“继续当前流程，补齐交付证据和发布产物”"
        if not delivery_manifest_ready:
            blocker = "当前交付包仍未达到 ready 状态。"
            evidence = "delivery manifest not ready"
        elif not rehearsal_report_passed:
            blocker = "当前尚未通过发布演练验证。"
            evidence = "rehearsal report not passed"
        else:
            blocker = "当前尚未完成交付包与部署产物。"
            evidence = "delivery artifacts incomplete"
    elif run_status in {
        "failed",
        "running",
        "waiting_confirmation",
        "waiting_ui_revision",
        "waiting_architecture_revision",
        "waiting_quality_revision",
    }:
        checkpoint_status = run_status
        blocker = "当前仓库存在运行态、确认门或返工门，需要先沿当前流程继续。"
        recommended_command = "在宿主里说“继续当前流程，不要重新开题”"
        evidence = f"run_status={run_status}"

    action_card = _build_action_card(
        workflow_status=checkpoint_status,
        recommended_command=recommended_command,
        blocker=blocker,
    )

    summary = {
        "current_stage_id": current_stage["id"],
        "current_stage_name": current_stage["name"],
        "blocker": blocker,
        "completed_count": len([stage for stage in stages if stage["status"] == "completed"]),
        "total_count": len(stages),
        "stages": stages,
        "artifacts": {
            "research": research_done,
            "prd": prd_done,
            "architecture": architecture_done,
            "uiux": uiux_done,
            "spec": spec_done,
            "frontend": frontend_done,
            "frontend_runtime_report": frontend_runtime_path,
            "backend": backend_done,
            "quality": quality_done,
            "delivery": delivery_done,
            "delivery_manifest_ready": delivery_manifest_ready,
            "delivery_manifest_path": delivery_manifest_path,
            "rehearsal_report_passed": rehearsal_report_passed,
            "rehearsal_report_path": rehearsal_report_path,
        },
        "knowledge": knowledge_summary,
        "docs_confirmation": docs_confirmation,
        "preview_confirmation": preview_confirmation,
        "ui_revision": ui_revision,
        "architecture_revision": architecture_revision,
        "quality_revision": quality_revision,
        "phase_results_count": len(run_results) if isinstance(run_results, list) else 0,
        "workflow_status": checkpoint_status,
        "workflow_mode": str(action_card.get("mode", "")).strip() or "continue",
        "flow_variant": flow_variant,
        "recommended_command": recommended_command,
        "evidence": evidence,
        "action_card": action_card,
    }
    summary["scenario_cards"] = build_workflow_scenario_cards(summary)
    return summary
