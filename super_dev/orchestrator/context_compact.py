"""
Pipeline 阶段间上下文压缩引擎 — 9 段结构化摘要

每个阶段结束时，将阶段输出压缩为结构化摘要（CompactSummary），
后续阶段仅读取前序阶段的压缩摘要而非完整上下文，大幅降低 token 消耗。

摘要以 JSON + Markdown 双格式持久化到 .super-dev/checkpoints/compact/。
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_logger = logging.getLogger("super_dev.context_compact")

# Token 预算：上下文注入的最大 token 数（约 4K tokens ≈ 16K 字符）
_DEFAULT_TOKEN_BUDGET = 4000


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数（粗略：1 token ≈ 4 字符英文 / 2 字符中文）。"""
    if not text:
        return 0
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    non_ascii_chars = len(text) - ascii_chars
    return (ascii_chars // 4) + (non_ascii_chars // 2)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CompactSummary:
    """结构化压缩摘要 — 9 段信息"""

    phase: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    primary_request: str = ""
    key_concepts: list[str] = field(default_factory=list)
    files_and_code: list[dict[str, Any]] = field(default_factory=list)  # [{path, summary, changes}]
    errors_and_fixes: list[dict[str, Any]] = field(default_factory=list)  # [{error, fix, feedback}]
    problem_solving: str = ""
    user_messages: list[str] = field(default_factory=list)
    pending_tasks: list[str] = field(default_factory=list)
    current_work: str = ""
    next_step: str = ""

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompactSummary:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Phase-specific extraction helpers
# ---------------------------------------------------------------------------

_PHASE_CONCEPT_KEYS: dict[str, list[str]] = {
    "discovery": ["requirements", "goals", "scope", "constraints"],
    "intelligence": ["competitors", "tools", "trends", "insights"],
    "drafting": ["architecture", "decisions", "patterns", "api_design"],
    "redteam": ["vulnerabilities", "risks", "mitigations", "findings"],
    "qa": ["test_coverage", "quality_score", "issues", "regressions"],
    "delivery": ["artifacts", "deployment", "release_notes", "checklist"],
    "deployment": ["targets", "rollout", "monitoring", "rollback"],
}


def _safe_str(value: Any, max_len: int = 500) -> str:
    """Safely convert a value to a bounded string."""
    text = str(value) if value else ""
    return text[:max_len] if len(text) > max_len else text


def _extract_files_from_documents(documents: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract file references from a documents dict."""
    files: list[dict[str, Any]] = []
    for key, value in documents.items():
        if isinstance(value, dict):
            path = value.get("path", key)
            summary = _safe_str(value.get("summary", value.get("title", "")), 200)
        elif isinstance(value, str):
            path = key
            summary = _safe_str(value, 200)
        else:
            continue
        files.append({"path": str(path), "summary": summary, "changes": ""})
    return files


def _extract_errors(quality_reports: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract error/fix pairs from quality reports."""
    errors: list[dict[str, Any]] = []
    for _name, report in quality_reports.items():
        if isinstance(report, dict):
            for issue in report.get("issues", []):
                if isinstance(issue, dict):
                    errors.append(
                        {
                            "error": _safe_str(issue.get("message", issue.get("error", "")), 300),
                            "fix": _safe_str(issue.get("fix", issue.get("suggestion", "")), 300),
                            "feedback": _safe_str(issue.get("feedback", ""), 200),
                        }
                    )
                elif isinstance(issue, str):
                    errors.append({"error": issue[:300], "fix": "", "feedback": ""})
        elif isinstance(report, list):
            for item in report:
                errors.append({"error": _safe_str(item, 300), "fix": "", "feedback": ""})
    return errors


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class CompactEngine:
    """阶段间上下文压缩引擎"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.compact_dir = project_dir / ".super-dev" / "checkpoints" / "compact"

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def compact_phase_output(self, phase: str, context: dict[str, Any]) -> CompactSummary:
        """将阶段输出压缩为结构化摘要。

        *context* 应至少包含 WorkflowContext 的关键字段:
        user_input, research_data, documents, quality_reports, results, metadata.
        """
        user_input: dict[str, Any] = context.get("user_input", {})
        research_data: dict[str, Any] = context.get("research_data", {})
        documents: dict[str, Any] = context.get("documents", {})
        quality_reports: dict[str, Any] = context.get("quality_reports", {})
        results: dict[str, Any] = context.get("results", {})
        metadata: dict[str, Any] = context.get("metadata", {})

        # --- primary_request ---
        primary_request = _safe_str(
            user_input.get("description", user_input.get("request", "")), 500
        )

        # --- key_concepts ---
        concept_keys = _PHASE_CONCEPT_KEYS.get(phase, [])
        key_concepts: list[str] = []
        for ck in concept_keys:
            for src in (research_data, documents, results, metadata):
                val = src.get(ck)
                if val:
                    if isinstance(val, list):
                        key_concepts.extend(_safe_str(v, 200) for v in val[:10])
                    else:
                        key_concepts.append(_safe_str(val, 200))
                    break
        # Deduplicate while preserving order
        seen: set[str] = set()
        deduped: list[str] = []
        for c in key_concepts:
            if c and c not in seen:
                seen.add(c)
                deduped.append(c)
        key_concepts = deduped[:20]

        # --- files_and_code ---
        files_and_code = _extract_files_from_documents(documents)

        # --- errors_and_fixes ---
        errors_and_fixes = _extract_errors(quality_reports)

        # --- problem_solving ---
        problem_solving = _safe_str(
            results.get("problem_solving", results.get("approach", "")), 500
        )

        # --- user_messages ---
        user_messages: list[str] = []
        raw_msgs = user_input.get("messages", [])
        if isinstance(raw_msgs, list):
            user_messages = [_safe_str(m, 300) for m in raw_msgs[:10]]

        # --- pending_tasks ---
        pending_tasks: list[str] = []
        raw_tasks = metadata.get("pending_tasks", results.get("pending_tasks", []))
        if isinstance(raw_tasks, list):
            pending_tasks = [_safe_str(t, 200) for t in raw_tasks[:20]]

        # --- current_work / next_step ---
        current_work = _safe_str(metadata.get("current_work", ""), 300)
        next_step = _safe_str(metadata.get("next_step", results.get("next_step", "")), 300)

        summary = CompactSummary(
            phase=phase,
            primary_request=primary_request,
            key_concepts=key_concepts,
            files_and_code=files_and_code,
            errors_and_fixes=errors_and_fixes,
            problem_solving=problem_solving,
            user_messages=user_messages,
            pending_tasks=pending_tasks,
            current_work=current_work,
            next_step=next_step,
        )

        _logger.info(
            "Compacted phase '%s': %d concepts, %d files",
            phase,
            len(key_concepts),
            len(files_and_code),
        )
        return summary

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_compact(self, summary: CompactSummary) -> Path:
        """保存压缩摘要到 JSON + Markdown 文件。返回 JSON 路径。"""
        self.compact_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.compact_dir / f"{summary.phase}.json"
        md_path = self.compact_dir / f"{summary.phase}_compact.md"

        json_path.write_text(
            json.dumps(summary.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        md_path.write_text(self.render_summary_markdown(summary), encoding="utf-8")

        _logger.info("Saved compact for phase '%s' -> %s", summary.phase, json_path)
        return json_path

    def load_compact(self, phase: str) -> CompactSummary | None:
        """加载指定阶段的压缩摘要。"""
        json_path = self.compact_dir / f"{phase}.json"
        if not json_path.exists():
            return None
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            return CompactSummary.from_dict(data)
        except (json.JSONDecodeError, TypeError, KeyError) as exc:
            _logger.warning("Failed to load compact for phase '%s': %s", phase, exc)
            return None

    # ------------------------------------------------------------------
    # Context builder
    # ------------------------------------------------------------------

    def build_context_for_phase(
        self,
        target_phase: str,
        previous_phases: list[str],
    ) -> str:
        """为目标阶段构建上下文（从前序阶段的压缩摘要中提取）。

        返回一段 Markdown 文本，可直接作为 prompt context 注入。
        """
        sections: list[str] = []
        sections.append(f"# Compact Context for Phase: {target_phase}\n")

        loaded_count = 0
        for phase in previous_phases:
            summary = self.load_compact(phase)
            if summary is None:
                continue
            loaded_count += 1
            sections.append(f"## From Phase: {phase} ({summary.timestamp[:19]})\n")

            if summary.primary_request:
                sections.append(f"**Primary Request:** {summary.primary_request}\n")

            if summary.key_concepts:
                sections.append("**Key Concepts:**")
                for concept in summary.key_concepts:
                    sections.append(f"- {concept}")
                sections.append("")

            if summary.files_and_code:
                sections.append("**Files:**")
                for f in summary.files_and_code:
                    line = f"- `{f.get('path', '?')}`"
                    if f.get("summary"):
                        line += f" — {f['summary']}"
                    sections.append(line)
                sections.append("")

            if summary.errors_and_fixes:
                sections.append("**Issues Found:**")
                for ef in summary.errors_and_fixes:
                    err = ef.get("error", "")
                    fix = ef.get("fix", "")
                    line = f"- {err}"
                    if fix:
                        line += f" → Fix: {fix}"
                    sections.append(line)
                sections.append("")

            if summary.pending_tasks:
                sections.append("**Pending Tasks:**")
                for t in summary.pending_tasks:
                    sections.append(f"- [ ] {t}")
                sections.append("")

            if summary.next_step:
                sections.append(f"**Next Step:** {summary.next_step}\n")

            sections.append("---\n")

        if loaded_count == 0:
            sections.append("_No compact summaries available from previous phases._\n")

        context = "\n".join(sections)

        # 智能截断：如果上下文超出 token 预算，逐级压缩
        estimated_tokens = estimate_tokens(context)
        if estimated_tokens > _DEFAULT_TOKEN_BUDGET:
            _logger.info(
                "Context for '%s' exceeds budget (%d > %d tokens), truncating...",
                target_phase,
                estimated_tokens,
                _DEFAULT_TOKEN_BUDGET,
            )
            context = self._truncate_context(context, _DEFAULT_TOKEN_BUDGET)

        return context

    def _truncate_context(self, context: str, budget: int) -> str:
        """逐级压缩上下文直到 token 预算内。

        策略（优先级从低到高，先砍最不重要的）：
        1. 砍 Files 详情（保留路径，去掉 summary）
        2. 砍 Issues 详情（保留条目数）
        3. 砍 Key Concepts（保留前 5 个）
        4. 砍 Pending Tasks（保留前 3 个）
        5. 砍旧阶段（只保留最近 2 个阶段）
        """
        lines = context.split("\n")
        result = lines

        # Level 1: 截断文件摘要
        if estimate_tokens("\n".join(result)) > budget:
            result = [
                line if not (line.startswith("- `") and " — " in line) else line.split(" — ")[0]
                for line in result
            ]

        # Level 2: 截断 Issues
        if estimate_tokens("\n".join(result)) > budget:
            in_issues = False
            issue_count = 0
            truncated: list[str] = []
            for line in result:
                if "**Issues Found:**" in line:
                    in_issues = True
                    truncated.append(line)
                    continue
                if in_issues:
                    if line.startswith("- "):
                        issue_count += 1
                        if issue_count <= 3:
                            truncated.append(line)
                        continue
                    else:
                        if issue_count > 3:
                            truncated.append(f"_...and {issue_count - 3} more issues_")
                        in_issues = False
                        issue_count = 0
                truncated.append(line)
            result = truncated

        # Level 3: 截断 Concepts 到前 5 个
        if estimate_tokens("\n".join(result)) > budget:
            in_concepts = False
            concept_count = 0
            truncated = []
            for line in result:
                if "**Key Concepts:**" in line:
                    in_concepts = True
                    truncated.append(line)
                    continue
                if in_concepts and line.startswith("- "):
                    concept_count += 1
                    if concept_count <= 5:
                        truncated.append(line)
                    continue
                elif in_concepts:
                    in_concepts = False
                truncated.append(line)
            result = truncated

        # Level 4: 只保留最近 2 个阶段
        if estimate_tokens("\n".join(result)) > budget:
            phase_starts = [i for i, line in enumerate(result) if line.startswith("## From Phase:")]
            if len(phase_starts) > 2:
                keep_from = phase_starts[-2]
                result = result[:1] + result[keep_from:]

        return "\n".join(result)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_summary_markdown(self, summary: CompactSummary) -> str:
        """渲染为 Markdown 格式（人类可读）。"""
        lines: list[str] = [
            f"# Phase Compact: {summary.phase}",
            "",
            f"**Timestamp:** {summary.timestamp}",
            "",
        ]

        if summary.primary_request:
            lines += ["## Primary Request", "", summary.primary_request, ""]

        if summary.key_concepts:
            lines += ["## Key Concepts", ""]
            for c in summary.key_concepts:
                lines.append(f"- {c}")
            lines.append("")

        if summary.files_and_code:
            lines += ["## Files & Code", ""]
            for f in summary.files_and_code:
                path = f.get("path", "?")
                summary_text = f.get("summary", "")
                changes = f.get("changes", "")
                lines.append(f"### `{path}`")
                if summary_text:
                    lines.append(f"- Summary: {summary_text}")
                if changes:
                    lines.append(f"- Changes: {changes}")
                lines.append("")

        if summary.errors_and_fixes:
            lines += ["## Errors & Fixes", ""]
            for ef in summary.errors_and_fixes:
                lines.append(f"- **Error:** {ef.get('error', '')}")
                if ef.get("fix"):
                    lines.append(f"  - **Fix:** {ef['fix']}")
                if ef.get("feedback"):
                    lines.append(f"  - **Feedback:** {ef['feedback']}")
            lines.append("")

        if summary.problem_solving:
            lines += ["## Problem Solving", "", summary.problem_solving, ""]

        if summary.user_messages:
            lines += ["## User Messages", ""]
            for m in summary.user_messages:
                lines.append(f"- {m}")
            lines.append("")

        if summary.pending_tasks:
            lines += ["## Pending Tasks", ""]
            for t in summary.pending_tasks:
                lines.append(f"- [ ] {t}")
            lines.append("")

        if summary.current_work:
            lines += ["## Current Work", "", summary.current_work, ""]

        if summary.next_step:
            lines += ["## Next Step", "", summary.next_step, ""]

        return "\n".join(lines) + "\n"
