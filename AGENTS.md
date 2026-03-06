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
