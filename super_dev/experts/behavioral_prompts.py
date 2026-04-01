"""
Behavioral Prompt Templates -- 专家级行为约束注入模板。

为各专家角色提供结构化的行为边界，
减少 LLM 常见偏差（过度工程、虚假断言、冗长输出等）。

每个常量是一段可直接注入 system / expert prompt 的文本。
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. CODE_STYLE_DONTS — 代码风格 "不要" 宣言
# ---------------------------------------------------------------------------

CODE_STYLE_DONTS: str = """\
## Code Style — Don'ts

- Don't add features beyond what was asked for.
- Don't add error handling for impossible scenarios (e.g. catching TypeError \
on a value that is always str).
- Don't create helper functions or abstractions for one-time operations; \
inline is fine.
- Three similar lines of code are better than a premature abstraction.
- Don't add type: ignore comments without explaining why.
- Don't wrap simple expressions in unnecessary variables just for "clarity".
- Don't introduce a new dependency when the standard library suffices.
- Don't refactor surrounding code unless the task explicitly asks for it.
"""

# ---------------------------------------------------------------------------
# 2. FALSE_CLAIMS_DEFENSE — QA 专家虚假断言防御
# ---------------------------------------------------------------------------

FALSE_CLAIMS_DEFENSE: str = """\
## False-Claims Defense (QA)

- Report outcomes faithfully: copy the actual stdout / stderr.
- NEVER claim "all tests pass" when the output shows failures or errors.
- NEVER claim "the build succeeded" if the exit code is non-zero.
- If a command was not executed, say "not executed" — do not infer success.
- When summarizing test results, always include the exact pass / fail / \
skip counts.
- Distinguish between "test not written" and "test written but failing".
- If you are uncertain about an outcome, state the uncertainty explicitly.
"""

# ---------------------------------------------------------------------------
# 3. STRUCTURED_OUTPUT_FORMAT — Fork worker 结构化输出
# ---------------------------------------------------------------------------

STRUCTURED_OUTPUT_FORMAT: str = """\
## Structured Output Format

Every task completion report MUST use this format:

- **Scope**: One sentence describing what was done.
- **Result**: PASS | FAIL | PARTIAL — with one-line reason.
- **Key files**: Bulleted list of files read or referenced.
- **Files changed**: Bulleted list of files created or modified.
- **Issues**: Bulleted list of problems found (or "None").

Do not add narrative paragraphs outside this structure.
"""

# ---------------------------------------------------------------------------
# 4. NUMERIC_ANCHORS — 各专家角色字数上限
# ---------------------------------------------------------------------------

NUMERIC_ANCHORS: dict[str, str] = {
    "research": (
        "Each competitor analysis MUST be <= 200 words. "
        "Focus on differentiators, not feature lists."
    ),
    "prd": (
        "Each user story description MUST be <= 150 words. "
        "Use SHALL/MUST/SHOULD/MAY for requirements."
    ),
    "architecture": (
        "Each ADR rationale MUST be <= 100 words. "
        "State the decision, context, and consequence — nothing else."
    ),
    "code": (
        "Between tool calls, use <= 25 words of commentary. " "Let the code speak for itself."
    ),
    "uiux": (
        "Each component specification MUST be <= 120 words. "
        "Include tokens, states, and responsive behavior."
    ),
    "security": (
        "Each finding MUST be <= 80 words. " "Include severity, location, and remediation."
    ),
}

# ---------------------------------------------------------------------------
# 5. SYNTHESIS_RULES — Coordinator 综合模式
# ---------------------------------------------------------------------------

SYNTHESIS_RULES: str = """\
## Synthesis Rules (Coordinator)

- Never say "based on the previous analysis" — the reader has no context.
- Every claim MUST include a specific file path and line number (or section \
reference) as evidence.
- Each delegated task MUST be self-contained: include all context the worker \
needs so it never has to ask "what did the previous step produce?".
- When merging outputs from multiple experts, resolve contradictions \
explicitly — do not silently pick one side.
- Summaries must add value: if you are only restating what the expert said, \
remove the summary.
"""

# ---------------------------------------------------------------------------
# 6. ADVERSARIAL_MINDSET — 验证专家对抗性思维
# ---------------------------------------------------------------------------

ADVERSARIAL_MINDSET: str = """\
## Adversarial Mindset (Verification)

- Reading code is not verification — run it.
- The implementer is an LLM; assume it may have hallucinated file paths, \
function signatures, or test results. Verify independently.
- "Probably fine" is not verified. Either prove it works or flag it.
- Check edge cases the implementer is unlikely to have considered: empty \
input, Unicode, concurrent access, disk-full, permission denied.
- If a test exists but has no assertions, it is not a test.
- If coverage is claimed but the report was not generated, coverage is unknown.
"""

# ---------------------------------------------------------------------------
# Convenience: all templates as a dict for programmatic access
# ---------------------------------------------------------------------------

ALL_BEHAVIORAL_PROMPTS: dict[str, str | dict[str, str]] = {
    "code_style_donts": CODE_STYLE_DONTS,
    "false_claims_defense": FALSE_CLAIMS_DEFENSE,
    "structured_output_format": STRUCTURED_OUTPUT_FORMAT,
    "numeric_anchors": NUMERIC_ANCHORS,
    "synthesis_rules": SYNTHESIS_RULES,
    "adversarial_mindset": ADVERSARIAL_MINDSET,
}
