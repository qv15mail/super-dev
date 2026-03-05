# 2026-03-04 Web Dashboard Host Threshold Design

## Goal

Make host compatibility gate configuration usable for non-technical users directly in the Dashboard, while keeping API/CLI behavior consistent and auditable.

## Options Considered

1. API-only configuration (no UI changes)
- Pros: minimal frontend work.
- Cons: non-technical users still blocked; poor discoverability.

2. Workflow-run-only temporary fields
- Pros: fast run-time override.
- Cons: parameters are hidden from initialization and easy to drift from project config.

3. Unified UI fields in Init + Workflow (chosen)
- Pros: one mental model, visible defaults, run-time and persisted config stay aligned.
- Cons: slightly larger form surface.

## Final Design

- Dashboard header copy is aligned with product positioning:
  - "超级开发战队 一个流水线式的AiCoding辅助工具".
- Init form includes:
  - `host_compatibility_min_score`
  - `host_compatibility_min_ready_hosts`
- Workflow form includes:
  - `quality_gate`
  - `host_compatibility_min_score`
  - `host_compatibility_min_ready_hosts`
- Added `读取项目配置` action:
  - fetches `/api/config`
  - hydrates Init and Workflow threshold fields
- Workflow execution payload now sends all three thresholds to `/api/workflow/run`, so backend can persist and execute with the same values.

## Data Flow

1. User opens Dashboard; app attempts to load current project config.
2. User can adjust threshold inputs in UI.
3. On run, frontend posts thresholds with selected phases.
4. Backend updates `super-dev.yaml` and runs pipeline with these values.

## Validation and Risk

- Numeric input constraints are enforced in UI (`min/max` for scores, `min` for ready hosts).
- Existing users remain compatible: defaults stay `80/1`.
- Main risk is stale config when `project_dir` changes; mitigated by manual `读取项目配置`.
