# Super Dev Continuous Execution Policy

This project uses a pipeline-first workflow.

## Operating Mode

- Default to continuous execution: do not stop after a partial step waiting for "continue" or "next step".
- Keep working until the requested outcome is fully implemented and validated in the current turn.
- Only pause when truly blocked:
  - missing external credentials or permissions,
  - destructive action requires explicit user authorization,
  - requirement conflict that cannot be safely inferred.

## Delivery Rules

- Always implement, then verify (lint/tests/smoke), then report remaining gaps.
- Prefer fixing the next known gap automatically instead of asking for confirmation.
- Treat "continue / 继续 / 下一步" as a command to advance to the next unfinished milestone immediately.

## Super Dev Priority

- Follow generated artifacts as source of truth:
  - `output/*-prd.md`
  - `output/*-architecture.md`
  - `output/*-uiux.md`
  - `.super-dev/changes/*/tasks.md`
- Trigger command:
  - `/super-dev "<需求描述>"`
  - fallback: `super-dev "<需求描述>"`

<!-- BEGIN SUPER DEV CODEX -->
# Super Dev for Codex CLI

When a user message starts with `super-dev:` or `super-dev：`, enter Super Dev pipeline mode immediately.

## Required execution
1. First reply: state that Super Dev pipeline mode is active and the current phase is `research`.
2. Read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` when available.
3. Use Codex native web/search/edit/terminal capabilities to perform similar-product research and write `output/*-research.md` into the repository workspace.
4. Draft `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` in the same Codex session and save them as actual project files.
5. Stop after the three core documents, summarize them, and wait for explicit confirmation.
6. Only after confirmation, create `.super-dev/changes/*/proposal.md` and `.super-dev/changes/*/tasks.md`, then continue with frontend-first implementation.

## Constraints
- Do not start coding directly after `super-dev:` or `super-dev：`.
- Do not create Spec before document confirmation.
- If a required artifact is only described in chat and not written into the repository, treat the step as incomplete.
- Codex remains the execution host; Super Dev is the local governance workflow.
- Use local `super-dev` CLI only for governance actions such as doctor, review, quality, release readiness, or update; do not outsource the main coding workflow to the CLI.
<!-- END SUPER DEV CODEX -->

