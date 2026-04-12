"""Extracted host report rendering functions — pure data formatting."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .catalogs import host_display_name

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _runtime_status_label(status: str) -> str:
    mapping = {
        "pending": "待真人验收",
        "passed": "已真人通过",
        "failed": "真人验收失败",
    }
    return mapping.get(status, "待真人验收")


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------

def render_host_compatibility_markdown(
    payload: dict[str, Any],
    *,
    host_label_fn: Callable[[str], str] = host_display_name,
) -> str:
    compatibility = payload.get("compatibility", {})
    report = payload.get("report", {})
    selected_targets = payload.get("selected_targets", [])
    detected_hosts = payload.get("detected_hosts", [])
    if not isinstance(compatibility, dict):
        compatibility = {}
    if not isinstance(report, dict):
        report = {}
    if not isinstance(selected_targets, list):
        selected_targets = []
    if not isinstance(detected_hosts, list):
        detected_hosts = []

    lines = [
        "# Host Compatibility Report",
        "",
        f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Project Dir: {payload.get('project_dir', '')}",
        f"- Detected Hosts: {', '.join(host_label_fn(str(item)) for item in detected_hosts) if detected_hosts else '(none)'}",
        f"- Selected Targets: {', '.join(host_label_fn(str(item)) for item in selected_targets) if selected_targets else '(none)'}",
        "",
        "## Summary",
        f"- Overall Score: {compatibility.get('overall_score', 0)}/100",
        f"- Ready Hosts: {compatibility.get('ready_hosts', 0)}/{compatibility.get('total_hosts', 0)}",
        f"- Enabled Checks: {', '.join(str(item) for item in compatibility.get('enabled_checks', []))}",
        "",
        "## Per-Host Scores",
        "",
        "| Host | Certification | Score | Ready | Passed/Total |",
        "|---|---|---:|---|---:|",
    ]

    host_scores = compatibility.get("hosts", {})
    if isinstance(host_scores, dict):
        for target in selected_targets:
            info = host_scores.get(target, {}) if isinstance(target, str) else {}
            if not isinstance(info, dict):
                info = {}
            usage_profiles = payload.get("usage_profiles", {})
            certification = "-"
            if isinstance(usage_profiles, dict):
                usage = usage_profiles.get(target, {})
                if isinstance(usage, dict):
                    certification = str(usage.get("certification_label", "-"))
            score = info.get("score", 0)
            ready = "yes" if bool(info.get("ready", False)) else "no"
            passed = int(info.get("passed", 0))
            possible = int(info.get("possible", 0))
            lines.append(
                f"| {host_label_fn(target)} | {certification} | {score} | {ready} | {passed}/{possible} |"
            )

    lines.extend(["", "## Usage Guidance", ""])
    usage_profiles = payload.get("usage_profiles", {})
    if isinstance(usage_profiles, dict):
        for target in selected_targets:
            usage = usage_profiles.get(target, {}) if isinstance(target, str) else {}
            if not isinstance(usage, dict):
                usage = {}
            lines.append(f"### {target}")
            lines.append(
                f"- Certification: {usage.get('certification_label', '-')} ({usage.get('certification_level', '-')})"
            )
            reason = usage.get("certification_reason", "")
            if isinstance(reason, str) and reason.strip():
                lines.append(f"- Certification Reason: {reason}")
            evidence = usage.get("certification_evidence", [])
            if isinstance(evidence, list) and evidence:
                lines.append("- Certification Evidence:")
                for item in evidence:
                    lines.append(f"  - {item}")
            lines.append(f"- Primary Entry: {usage.get('primary_entry', '-')}")
            lines.append(f"- Usage Mode: {usage.get('usage_mode', '-')}")
            lines.append(f"- Trigger Command: {usage.get('trigger_command', '-')}")
            lines.append(f"- Trigger Context: {usage.get('trigger_context', '-')}")
            lines.append(f"- Restart Required: {usage.get('restart_required_label', '-')}")
            precondition_label = usage.get("precondition_label", "")
            if isinstance(precondition_label, str) and precondition_label.strip():
                lines.append(f"- Host Preconditions: {precondition_label}")
            precondition_items = usage.get("precondition_items", [])
            if isinstance(precondition_items, list) and precondition_items:
                lines.append("- Host Precondition Items:")
                for item in precondition_items:
                    if not isinstance(item, dict):
                        continue
                    item_label = str(item.get("label", "")).strip()
                    item_status = str(item.get("status", "")).strip()
                    item_text = item_label or item_status
                    if item_text:
                        lines.append(f"  - {item_text}")
            precondition_guidance = usage.get("precondition_guidance", [])
            if isinstance(precondition_guidance, list) and precondition_guidance:
                lines.append("- Host Precondition Guidance:")
                for item in precondition_guidance:
                    lines.append(f"  - {item}")
            steps = usage.get("post_onboard_steps", [])
            if isinstance(steps, list) and steps:
                lines.append("- Post Onboard Steps:")
                for step in steps:
                    lines.append(f"  - {step}")
            note = usage.get("notes", "")
            if isinstance(note, str) and note.strip():
                lines.append(f"- Notes: {note}")
            lines.append("")

    lines.extend(["## Missing Items", ""])
    hosts = report.get("hosts", {})
    if isinstance(hosts, dict):
        for target in selected_targets:
            host = hosts.get(target, {}) if isinstance(target, str) else {}
            if not isinstance(host, dict):
                continue
            missing = host.get("missing", [])
            if not isinstance(missing, list) or not missing:
                continue
            lines.append(f"### {target}")
            lines.append(f"- Missing: {', '.join(str(item) for item in missing)}")
            suggestions = host.get("suggestions", [])
            if isinstance(suggestions, list):
                for suggestion in suggestions:
                    lines.append(f"- Suggestion: `{suggestion}`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_host_surface_audit_markdown(
    payload: dict[str, Any],
    *,
    host_label_fn: Callable[[str], str] = host_display_name,
) -> str:
    report = payload.get("report", {})
    compatibility = payload.get("compatibility", {})
    selected_targets = payload.get("selected_targets", [])
    detected_hosts = payload.get("detected_hosts", [])
    usage_profiles = payload.get("usage_profiles", {})
    repair_actions = payload.get("repair_actions", {})
    if not isinstance(report, dict):
        report = {}
    if not isinstance(compatibility, dict):
        compatibility = {}
    if not isinstance(selected_targets, list):
        selected_targets = []
    if not isinstance(detected_hosts, list):
        detected_hosts = []
    if not isinstance(usage_profiles, dict):
        usage_profiles = {}
    if not isinstance(repair_actions, dict):
        repair_actions = {}

    lines = [
        "# Host Surface Audit Report",
        "",
        f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Project Dir: {payload.get('project_dir', '')}",
        f"- Detected Hosts: {', '.join(str(item) for item in detected_hosts) if detected_hosts else '(none)'}",
        f"- Selected Targets: {', '.join(str(item) for item in selected_targets) if selected_targets else '(none)'}",
        f"- Overall Score: {compatibility.get('overall_score', 0)}/100",
        "",
    ]
    if repair_actions:
        lines.extend(["## Repair Actions", ""])
        for target, actions in repair_actions.items():
            if isinstance(actions, dict):
                action_text = ", ".join(f"{key}={value}" for key, value in actions.items())
                lines.append(f"- {target}: {action_text}")
        lines.append("")

    hosts = report.get("hosts", {})
    if not isinstance(hosts, dict):
        hosts = {}

    for target in selected_targets:
        host = hosts.get(target, {}) if isinstance(target, str) else {}
        usage = usage_profiles.get(target, {}) if isinstance(target, str) else {}
        if not isinstance(host, dict):
            host = {}
        if not isinstance(usage, dict):
            usage = {}
        checks = host.get("checks", {})
        contract = checks.get("contract", {}) if isinstance(checks, dict) else {}
        surfaces = contract.get("surfaces", {}) if isinstance(contract, dict) else {}
        invalid_surfaces = (
            contract.get("invalid_surfaces", {}) if isinstance(contract, dict) else {}
        )
        lines.extend(
            [
                f"## {target}",
                "",
                f"- Ready: {'yes' if bool(host.get('ready', False)) else 'no'}",
                f"- Trigger: {usage.get('final_trigger', '-')}",
                f"- Protocol: {usage.get('host_protocol_summary', '-')}",
                "",
                "| Surface | Exists | Missing Markers | Path |",
                "|---|---|---|---|",
            ]
        )
        if isinstance(surfaces, dict):
            for surface_key, surface_info in surfaces.items():
                if not isinstance(surface_info, dict):
                    continue
                exists = "yes" if bool(surface_info.get("exists", False)) else "no"
                missing = surface_info.get("missing_markers", [])
                missing_text = (
                    ", ".join(str(item) for item in missing)
                    if isinstance(missing, list) and missing
                    else "-"
                )
                lines.append(
                    f"| {surface_key} | {exists} | {missing_text} | {surface_info.get('path', '-')} |"
                )
        suggestions = host.get("suggestions", [])
        if isinstance(invalid_surfaces, dict) and invalid_surfaces:
            lines.extend(["", "### Fix Guidance", ""])
            for surface_key, surface_info in invalid_surfaces.items():
                if not isinstance(surface_info, dict):
                    continue
                missing = surface_info.get("missing_markers", [])
                missing_text = (
                    ", ".join(str(item) for item in missing)
                    if isinstance(missing, list) and missing
                    else "-"
                )
                lines.append(f"- `{surface_key}` -> {missing_text}")
        if isinstance(suggestions, list) and suggestions:
            lines.extend(["", "### Suggested Commands", ""])
            for suggestion in suggestions:
                lines.append(f"- `{suggestion}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_host_runtime_validation_markdown(
    payload: dict[str, Any],
    *,
    host_label_fn: Callable[[str], str] = host_display_name,
) -> str:
    hosts = payload.get("hosts", [])
    if not isinstance(hosts, list):
        hosts = []
    lines = [
        "# Host Runtime Validation Matrix",
        "",
        f"- Generated At (UTC): {payload.get('generated_at', '')}",
        f"- Project Dir: {payload.get('project_dir', '')}",
        f"- Detected Hosts: {', '.join(str(item) for item in payload.get('detected_hosts', [])) or '(none)'}",
        "",
    ]
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        lines.extend(
            [
                "## Summary",
                "",
                f"- Overall Status: {summary.get('overall_status', '-')}",
                f"- Fully Ready: {summary.get('fully_ready_count', 0)}/{summary.get('total_hosts', 0)}",
                f"- Surface Ready: {summary.get('surface_ready_count', 0)}/{summary.get('total_hosts', 0)}",
                f"- Runtime Passed: {summary.get('runtime_passed_count', 0)}",
                f"- Runtime Failed: {summary.get('runtime_failed_count', 0)}",
                f"- Runtime Pending: {summary.get('runtime_pending_count', 0)}",
                "",
            ]
        )
    blockers = payload.get("blockers", [])
    if isinstance(blockers, list):
        lines.extend(["## Current Blockers", ""])
        if blockers:
            for item in blockers:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- **{item.get('host', '-')}** ({item.get('type', '-')}) {item.get('summary', '-')}"
                )
        else:
            lines.append("- 当前没有阻塞项。")
        lines.extend(["", "## Recommended Next Actions", ""])
        next_actions = summary.get("next_actions", []) if isinstance(summary, dict) else []
        if isinstance(next_actions, list) and next_actions:
            for item in next_actions:
                lines.append(f"- {item}")
        else:
            lines.append("- 当前宿主验收中心没有额外动作。")
        lines.append("")
    lines.extend(
        [
            "| Host | Surface Ready | Trigger | Protocol | Manual Runtime Status |",
            "|---|---|---|---|---|",
        ]
    )
    for host in hosts:
        if not isinstance(host, dict):
            continue
        lines.append(
            f"| {host.get('host', '-')} | {'yes' if bool(host.get('surface_ready', False)) else 'no'} | "
            f"{host.get('final_trigger', '-')} | {host.get('host_protocol_summary', '-')} | {host.get('manual_runtime_status_label', '-')} |"
        )

    for host in hosts:
        if not isinstance(host, dict):
            continue
        lines.extend(
            [
                "",
                f"## {host.get('host', '-')}",
                "",
                f"- Trigger: {host.get('final_trigger', '-')}",
                f"- Protocol: {host.get('host_protocol_summary', '-')}",
                f"- Surface Ready: {'yes' if bool(host.get('surface_ready', False)) else 'no'}",
                f"- Manual Runtime Status: {host.get('manual_runtime_status_label', '-')}",
                f"- Host Preconditions: {host.get('precondition_label', '-')}",
                f"- Smoke Prompt: {host.get('smoke_test_prompt', '-')}",
                f"- Smoke Success Signal: {host.get('smoke_success_signal', '-')}",
                "",
                "### Runtime Checklist",
                "",
            ]
        )
        resume_probe = host.get("resume_probe_prompt", "")
        if isinstance(resume_probe, str) and resume_probe.strip():
            lines.extend(["### Resume Probe Prompt", "", f"- {resume_probe.strip()}", ""])
        framework_playbook = host.get("framework_playbook", {})
        if isinstance(framework_playbook, dict) and framework_playbook:
            lines.extend(
                [
                    "### Framework Playbook",
                    "",
                    f"- Framework: {framework_playbook.get('framework', '-')}",
                ]
            )
            modules = framework_playbook.get("implementation_modules", [])
            if isinstance(modules, list) and modules:
                lines.append(
                    "- Implementation Modules: "
                    + "；".join(str(item) for item in modules[:3])
                )
            native_capabilities = framework_playbook.get("native_capabilities", [])
            if isinstance(native_capabilities, list) and native_capabilities:
                lines.append(
                    "- Native Capabilities: "
                    + "；".join(str(item) for item in native_capabilities[:3])
                )
            validation = framework_playbook.get("validation_surfaces", [])
            if isinstance(validation, list) and validation:
                lines.append(
                    "- Validation Surfaces: "
                    + "；".join(str(item) for item in validation[:3])
                )
            evidence = framework_playbook.get("delivery_evidence", [])
            if isinstance(evidence, list) and evidence:
                lines.append(
                    "- Delivery Evidence: "
                    + "；".join(str(item) for item in evidence[:3])
                )
            lines.append("")
        comment = host.get("manual_runtime_comment", "")
        if isinstance(comment, str) and comment.strip():
            lines.extend(["### Runtime Validation Note", "", f"- {comment.strip()}", ""])
        preconditions = host.get("precondition_guidance", [])
        if isinstance(preconditions, list) and preconditions:
            lines.extend(["", "### Host Precondition Guidance", ""])
            for item in preconditions:
                lines.append(f"- {item}")
        checklist = host.get("runtime_checklist", [])
        if isinstance(checklist, list):
            for item in checklist:
                lines.append(f"- {item}")
        lines.extend(["", "### Pass Criteria", ""])
        criteria = host.get("pass_criteria", [])
        if isinstance(criteria, list):
            for item in criteria:
                lines.append(f"- {item}")
        resume_checklist = host.get("resume_checklist", [])
        if isinstance(resume_checklist, list) and resume_checklist:
            lines.extend(["", "### Resume Checklist", ""])
            for item in resume_checklist:
                lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_host_hardening_markdown(
    payload: dict[str, Any],
    *,
    host_label_fn: Callable[[str], str] = host_display_name,
) -> str:
    compatibility = payload.get("compatibility", {})
    selected_targets = payload.get("selected_targets", [])
    hardening_results = payload.get("hardening_results", {})
    if not isinstance(compatibility, dict):
        compatibility = {}
    if not isinstance(selected_targets, list):
        selected_targets = []
    if not isinstance(hardening_results, dict):
        hardening_results = {}
    lines = [
        "# Host System Hardening Report",
        "",
        f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Project Dir: {payload.get('project_dir', '')}",
        f"- Selected Targets: {', '.join(str(item) for item in selected_targets) if selected_targets else '(none)'}",
        f"- Compatibility Score: {compatibility.get('overall_score', 0)}/100",
        f"- Flow Consistency: {compatibility.get('flow_consistency_score', 0)}/100",
        f"- Official Doc Alignment: {((payload.get('official_compare_summary', {}) or {}).get('score', 0))}/100",
        f"- Host Parity: {((payload.get('host_parity_summary', {}) or {}).get('score', 0))}/100",
        f"- Host Gate Parity: {((payload.get('host_gate_summary', {}) or {}).get('score', 0))}/100",
        f"- Host Runtime Script Parity: {((payload.get('host_runtime_script_summary', {}) or {}).get('score', 0))}/100",
        f"- Host Recovery Parity: {((payload.get('host_recovery_summary', {}) or {}).get('score', 0))}/100",
        "",
    ]
    for target in selected_targets:
        item = hardening_results.get(target, {}) if isinstance(target, str) else {}
        if not isinstance(item, dict):
            item = {}
        plan = item.get("plan", {})
        contract = item.get("contract", {})
        official_compare = item.get("official_compare", {})
        gate_hosts = (payload.get("host_gate_summary", {}) or {}).get("hosts", {})
        gate_info = gate_hosts.get(target, {}) if isinstance(gate_hosts, dict) else {}
        runtime_script_hosts = (payload.get("host_runtime_script_summary", {}) or {}).get(
            "hosts", {}
        )
        runtime_script_info = (
            runtime_script_hosts.get(target, {})
            if isinstance(runtime_script_hosts, dict)
            else {}
        )
        recovery_hosts = (payload.get("host_recovery_summary", {}) or {}).get("hosts", {})
        recovery_info = (
            recovery_hosts.get(target, {}) if isinstance(recovery_hosts, dict) else {}
        )
        lines.extend([f"## {target}", ""])
        lines.append(f"- Trigger: {plan.get('final_trigger', '-')}")
        lines.append(f"- Trigger Mode: {plan.get('trigger_mode', '-')}")
        lines.append(
            f"- Contract OK: {'yes' if bool((contract or {}).get('ok', False)) else 'no'}"
        )
        if isinstance(gate_info, dict) and gate_info:
            lines.append(
                f"- Gate Parity: {'yes' if bool(gate_info.get('passed', False)) else 'no'}"
            )
        if isinstance(runtime_script_info, dict) and runtime_script_info:
            lines.append(
                f"- Runtime Script Parity: {'yes' if bool(runtime_script_info.get('passed', False)) else 'no'}"
            )
        if isinstance(recovery_info, dict) and recovery_info:
            lines.append(
                f"- Recovery Parity: {'yes' if bool(recovery_info.get('passed', False)) else 'no'}"
            )
            commands = recovery_info.get("recommended_commands", [])
            if isinstance(commands, list) and commands:
                lines.append("- Recovery Commands:")
                for cmd in commands:
                    lines.append(f"  - {cmd}")
        if isinstance(official_compare, dict) and official_compare:
            lines.append(
                f"- Official Compare: {official_compare.get('status', 'unknown')} "
                f"({official_compare.get('reachable_urls', 0)}/{official_compare.get('checked_urls', 0)})"
            )
        written_files = item.get("written_files", [])
        if isinstance(written_files, list) and written_files:
            lines.append("- Updated Files:")
            for path in written_files:
                lines.append(f"  - {path}")
        required_steps = plan.get("required_steps", [])
        if isinstance(required_steps, list) and required_steps:
            lines.append("- Required Steps:")
            for step in required_steps:
                lines.append(f"  - {step}")
        skill_install = item.get("skill_install", {})
        if isinstance(skill_install, dict) and bool(skill_install.get("required", False)):
            lines.append(
                f"- Skill Install: {'ok' if bool(skill_install.get('installed', False)) else 'failed'}"
            )
            if skill_install.get("path"):
                lines.append(f"  - Path: {skill_install.get('path')}")
            if skill_install.get("error"):
                lines.append(f"  - Error: {skill_install.get('error')}")
        invalid = (contract or {}).get("invalid_surfaces", {})
        if isinstance(invalid, dict) and invalid:
            lines.append("- Invalid Surfaces:")
            for surface_key in invalid.keys():
                lines.append(f"  - {surface_key}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_host_parity_onepage_markdown(
    payload: dict[str, Any],
    *,
    host_label_fn: Callable[[str], str] = host_display_name,
) -> str:
    selected_targets = payload.get("selected_targets", [])
    if not isinstance(selected_targets, list):
        selected_targets = []
    hardening_results = payload.get("hardening_results", {})
    if not isinstance(hardening_results, dict):
        hardening_results = {}
    parity_index = payload.get("host_parity_index", {})
    if not isinstance(parity_index, dict):
        parity_index = {}
    lines = [
        "# Host Parity Onepage",
        "",
        f"- Generated At (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Project Dir: {payload.get('project_dir', '')}",
        f"- Host Parity Index: {parity_index.get('score', 0)}/100 "
        f"(threshold {parity_index.get('threshold', 95.0)}, "
        f"{'pass' if bool(parity_index.get('passed', False)) else 'fail'})",
        "",
        "| Host | Status | Failed Dimension | Next Command |",
        "|---|---|---|---|",
    ]
    official_hosts = (payload.get("official_compare_summary", {}) or {}).get("hosts", {})
    parity_hosts = (payload.get("host_parity_summary", {}) or {}).get("hosts", {})
    gate_hosts = (payload.get("host_gate_summary", {}) or {}).get("hosts", {})
    runtime_hosts = (payload.get("host_runtime_script_summary", {}) or {}).get("hosts", {})
    recovery_hosts = (payload.get("host_recovery_summary", {}) or {}).get("hosts", {})
    flow_hosts = (payload.get("compatibility", {}) or {}).get("hosts", {})
    for target in selected_targets:
        item = hardening_results.get(target, {}) if isinstance(target, str) else {}
        contract = item.get("contract", {}) if isinstance(item, dict) else {}
        recovery = recovery_hosts.get(target, {}) if isinstance(recovery_hosts, dict) else {}
        recovery_commands = (
            recovery.get("recommended_commands", []) if isinstance(recovery, dict) else []
        )
        dimensions: list[tuple[str, bool]] = []
        dimensions.append(
            ("official_compare", str((official_hosts or {}).get(target, "unknown")) == "passed")
        )
        dimensions.append(
            (
                "host_parity",
                bool(((parity_hosts or {}).get(target, {}) or {}).get("passed", False)),
            )
        )
        dimensions.append(
            ("host_gate", bool(((gate_hosts or {}).get(target, {}) or {}).get("passed", False)))
        )
        dimensions.append(
            (
                "runtime_script",
                bool(((runtime_hosts or {}).get(target, {}) or {}).get("passed", False)),
            )
        )
        dimensions.append(
            (
                "host_recovery",
                bool(((recovery_hosts or {}).get(target, {}) or {}).get("passed", False)),
            )
        )
        dimensions.append(
            (
                "flow_consistency",
                bool(((flow_hosts or {}).get(target, {}) or {}).get("flow_consistent", False)),
            )
        )
        contract_ok = bool((contract or {}).get("ok", False))
        status = "PASS" if contract_ok and all(ok for _, ok in dimensions) else "FAIL"
        failed = [name for name, ok in dimensions if not ok]
        failed_text = ", ".join(failed) if failed else "-"
        next_command = (
            recovery_commands[0]
            if isinstance(recovery_commands, list) and recovery_commands
            else "-"
        )
        lines.append(f"| {target} | {status} | {failed_text} | `{next_command}` |")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def write_host_surface_audit_report(
    *,
    project_dir: Path,
    payload: dict[str, Any],
    resolve_project_name_fn: Callable[[Path], str],
    render_surface_audit_fn: Callable[[dict[str, Any]], str],
) -> dict[str, Path]:
    project_name = resolve_project_name_fn(project_dir)
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / f"{project_name}-host-surface-audit.json"
    md_file = output_dir / f"{project_name}-host-surface-audit.md"
    json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_file.write_text(render_surface_audit_fn(payload), encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    history_dir = output_dir / "host-surface-audit-history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_json = history_dir / f"{project_name}-host-surface-audit-{stamp}.json"
    history_md = history_dir / f"{project_name}-host-surface-audit-{stamp}.md"
    history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    history_md.write_text(render_surface_audit_fn(payload), encoding="utf-8")

    return {
        "json": json_file,
        "markdown": md_file,
        "history_json": history_json,
        "history_markdown": history_md,
    }


def write_host_hardening_report(
    *,
    project_dir: Path,
    payload: dict[str, Any],
    resolve_project_name_fn: Callable[[Path], str],
    render_hardening_fn: Callable[[dict[str, Any]], str],
    render_parity_onepage_fn: Callable[[dict[str, Any]], str],
) -> dict[str, Path]:
    project_name = resolve_project_name_fn(project_dir)
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_file = output_dir / f"{project_name}-host-hardening.json"
    md_file = output_dir / f"{project_name}-host-hardening.md"
    onepage_file = output_dir / f"{project_name}-host-parity-onepage.md"
    json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_file.write_text(render_hardening_fn(payload), encoding="utf-8")
    onepage_file.write_text(render_parity_onepage_fn(payload), encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    history_dir = output_dir / "host-hardening-history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_json = history_dir / f"{project_name}-host-hardening-{stamp}.json"
    history_md = history_dir / f"{project_name}-host-hardening-{stamp}.md"
    history_onepage = history_dir / f"{project_name}-host-parity-onepage-{stamp}.md"
    history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    history_md.write_text(render_hardening_fn(payload), encoding="utf-8")
    history_onepage.write_text(render_parity_onepage_fn(payload), encoding="utf-8")
    return {
        "json": json_file,
        "markdown": md_file,
        "onepage_markdown": onepage_file,
        "history_json": history_json,
        "history_markdown": history_md,
        "history_onepage_markdown": history_onepage,
    }


def write_host_runtime_validation_report(
    *,
    project_dir: Path,
    payload: dict[str, Any],
    resolve_project_name_fn: Callable[[Path], str],
    render_runtime_validation_fn: Callable[[dict[str, Any]], str],
) -> dict[str, Path]:
    project_name = resolve_project_name_fn(project_dir)
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / f"{project_name}-host-runtime-validation.json"
    md_file = output_dir / f"{project_name}-host-runtime-validation.md"
    json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_file.write_text(render_runtime_validation_fn(payload), encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    history_dir = output_dir / "host-runtime-validation-history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_json = history_dir / f"{project_name}-host-runtime-validation-{stamp}.json"
    history_md = history_dir / f"{project_name}-host-runtime-validation-{stamp}.md"
    history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    history_md.write_text(render_runtime_validation_fn(payload), encoding="utf-8")

    return {
        "json": json_file,
        "markdown": md_file,
        "history_json": history_json,
        "history_markdown": history_md,
    }


def write_host_compatibility_report(
    *,
    project_dir: Path,
    payload: dict[str, Any],
    resolve_project_name_fn: Callable[[Path], str],
    render_compatibility_fn: Callable[[dict[str, Any]], str],
) -> dict[str, Path]:
    project_name = resolve_project_name_fn(project_dir)
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / f"{project_name}-host-compatibility.json"
    md_file = output_dir / f"{project_name}-host-compatibility.md"
    json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_file.write_text(render_compatibility_fn(payload), encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    history_dir = output_dir / "host-compatibility-history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_json = history_dir / f"{project_name}-host-compatibility-{stamp}.json"
    history_md = history_dir / f"{project_name}-host-compatibility-{stamp}.md"
    history_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    history_md.write_text(render_compatibility_fn(payload), encoding="utf-8")

    return {
        "json": json_file,
        "markdown": md_file,
        "history_json": history_json,
        "history_markdown": history_md,
    }
