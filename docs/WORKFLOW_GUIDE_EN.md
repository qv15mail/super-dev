# Super Dev Workflow Guide (2.0.1)

This is the practical handbook for running Super Dev in real projects. It covers:

- command usage and operator flow
- greenfield delivery (0 to 1)
- iterative delivery on existing systems (1 to N+1, including 1-to-1+N rollouts)
- commercial release gates and handoff standards

---

## 1. Start Here

### Recommended entrypoint

Use natural language as the default interface:

```bash
super-dev "Build an enterprise project management platform with auth, RBAC, projects, tasks, and analytics"
```

That single command triggers the full pipeline end to end.

### Advanced entrypoint

Use explicit flags only when you need strict control over stack and platform:

```bash
super-dev pipeline "Build an enterprise project management platform with auth, RBAC, projects, tasks, and analytics" \
  --platform web \
  --frontend react \
  --backend python \
  --domain saas \
  --cicd all \
  --quality-threshold 85
```

---

## 2. Command Map

### Core orchestration

```bash
super-dev "<requirement>"            # recommended default
super-dev pipeline "<requirement>"   # advanced explicit mode
super-dev create "<requirement>"     # docs + spec focused path
```

### Spec and task execution loop

```bash
super-dev spec init
super-dev spec list
super-dev spec show <change_id>
super-dev spec propose <change_id> --title "<title>" --description "<description>"
super-dev spec add-req <change_id> <spec_name> <req_name> "<requirement text>"
super-dev spec validate
super-dev spec archive <change_id>

super-dev task list
super-dev task status <change_id>
super-dev task run <change_id>
```

### Quality, risk, and release prep

```bash
super-dev quality --type all
super-dev deploy --cicd all
super-dev deploy --docker
```

### Expert and design tooling

```bash
super-dev expert --list
super-dev expert ARCHITECT "Review service boundaries and API contracts"
super-dev expert SECURITY "Assess auth, session, and token risk"

super-dev design search "fintech dashboard"
super-dev design generate --product saas --industry fintech
super-dev design tokens --primary "#2563EB"
```

### Integration and skills

```bash
super-dev integrate list
super-dev integrate setup --all --force
super-dev skill targets
super-dev skill install super-dev --target codex-cli --name super-dev-core --force
```

---

## 3. 0-to-1 Delivery (Greenfield)

Use this path when you have requirements but no production codebase yet.

### Step-by-step flow

```bash
mkdir new-product && cd new-product
super-dev "Build a B2B CRM with leads, accounts, opportunities, role-based access, and audit trail"
```

### What to inspect after generation

- `output/*-research.md` (enriched requirement context)
- `output/*-prd.md` (product contract)
- `output/*-architecture.md` (technical contract)
- `output/*-uiux.md` (design contract)
- `.super-dev/changes/*/tasks.md` (implementation queue)
- `output/*-task-execution.md` (execution and auto-repair trace)
- `output/*-redteam.md` (security/performance/architecture risk report)
- `output/*-quality-gate.md` (delivery score and blockers)
- `output/delivery/*-delivery-manifest.json` (delivery readiness state)

### Recommended execution rhythm

1. Validate generated docs with product and architecture owners.
2. Land frontend demo paths first for requirement validation.
3. Implement backend/data tasks from Spec in order.
4. Resolve red-team blockers and quality gate failures.
5. Package and hand off using `output/delivery/` artifacts.

---

## 4. 1-to-N+1 Delivery (Existing Project Iteration)

Use this when your system already exists and you are adding capabilities in controlled increments.

This includes the common `1-to-1+N` pattern: one established product, multiple staged capability rollouts.

### Step-by-step flow

```bash
cd existing-project
super-dev analyze .
super-dev spec init
super-dev spec propose add-billing --title "Introduce Billing Center" --description "Plans, subscriptions, invoices, callbacks"
super-dev spec add-req add-billing billing subscription "The system SHALL support subscription lifecycle management"
super-dev spec add-req add-billing billing webhook "The system SHALL process payment callbacks idempotently"
super-dev task run add-billing
super-dev quality --type all
```

### Increment strategy that scales

1. Keep each `change_id` narrowly scoped to one capability area.
2. Require independent quality pass for each change.
3. Merge and release in small slices instead of multi-domain bundles.
4. Treat red-team and quality outputs as hard release gates.

---

## 5. Commercial Readiness Gates

A change is considered release-ready only if all are true:

1. No red-team critical blockers remain.
2. Quality gate score is `>= 80`.
3. Spec execution status is complete or explicitly waived with rationale.
4. CI/CD assets are generated and mapped to the target platform.
5. Delivery manifest reports `ready`.

Run full preflight before tagging:

```bash
./scripts/preflight.sh
```

If you need a local constrained run:

```bash
./scripts/preflight.sh --allow-dirty --skip-benchmark --skip-package
```

---

## 6. Platform Integration Targets

Supported AI coding environments:

- CLI: `claude-code`, `codex-cli`, `opencode`
- IDE: `antigravity`, `cursor`, `qoder`, `trae`, `codebuddy`

One-command setup:

```bash
./install.sh --targets all
```

---

## 7. Troubleshooting

### Pipeline stops at red-team

Read `output/*-redteam.md`, fix critical/high findings first, then rerun.

### Quality gate fails

Read `output/*-quality-gate.md`, then rerun task closure and quality checks:

```bash
super-dev task run <change_id>
super-dev quality --type all
```

### Need to inspect current execution state

```bash
super-dev spec list
super-dev task status <change_id>
```

---

## 8. Daily Playbooks

### Greenfield quick playbook

```bash
super-dev "<requirement>"
super-dev task list
super-dev quality --type all
```

### Iteration quick playbook

```bash
super-dev analyze .
super-dev spec propose <change_id> --title "<title>" --description "<description>"
super-dev task run <change_id>
super-dev quality --type all
```

---

## 9. Related Docs

- Chinese workflow guide: `docs/WORKFLOW_GUIDE.md`
- Integration guide: `docs/INTEGRATION_GUIDE.md`
- Quickstart: `docs/QUICKSTART.md`
- Publishing: `docs/PUBLISHING.md`
- Release runbook: `docs/RELEASE_RUNBOOK.md`
