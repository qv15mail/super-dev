# Super Dev Workflow Guide (2.0.11)

This is the practical handbook for running Super Dev in real projects. It covers:

- command usage and operator flow
- greenfield delivery (0 to 1)
- iterative delivery on existing systems (1 to N+1, including 1-to-1+N rollouts)
- commercial release gates and handoff standards

---

## 1. Start Here

### Recommended entrypoint

The preferred path is to trigger Super Dev inside the host session:

```text
/super-dev Build an enterprise project management platform with auth, RBAC, projects, tasks, and analytics
```

If you are unsure which host to use on the current machine, run:

```bash
super-dev start --idea "Build an enterprise project management platform with auth, RBAC, projects, tasks, and analytics"
```

The terminal form `super-dev "<requirement>"` should be treated as a local governance-orchestration entry, not as Super Dev replacing host-side coding.

Host hard gate is enabled by default. If no `ready` host is available, pipeline execution is blocked until onboarding is complete.

That single command triggers the full pipeline end to end:

1. Similar-product research using the host's native web/search capability
2. Three core documents: PRD, architecture, UI/UX
3. Confirmation gate: stop and wait for the user to confirm or revise the three documents
4. Spec/tasks creation
5. Frontend-first implementation and runtime validation
6. Backend integration, testing, gates, and delivery

Additional rules:

- Bugfix work does not skip documentation; it follows a lighter patch path that captures symptoms, reproduction steps, impact scope, and regression risk before implementation.
- The analysis stage excludes non-project source directories such as `.venv`, `site-packages`, and `node_modules`.
- When the requirement is ambiguous, PRD should surface clarification questions first, and architecture should include a key sequence diagram by default.

The document confirmation gate can be handled in the Web console or directly from the terminal:

```bash
super-dev review docs
super-dev review docs --status revision_requested --comment "Add differentiation and improve hero information architecture"
super-dev review docs --status confirmed --comment "Core documents approved, proceed to Spec"
```

If the frontend visual quality is unsatisfactory, start a formal UI revision loop instead of making ad hoc CSS edits:

```bash
super-dev review ui
super-dev review ui --status revision_requested --comment "Hero feels empty and lacks brand presence; redesign the first screen"
super-dev review ui --status confirmed --comment "UI revision approved"
```

The required order for UI revision is:

1. Update `output/*-uiux.md`
2. Redo the frontend implementation
3. Rerun frontend runtime and UI review
4. Continue delivery only after the revision is approved

If the user says the technical plan, module boundaries, or API design are wrong, start a formal architecture revision loop:

```bash
super-dev review architecture
super-dev review architecture --status revision_requested --comment "Service boundaries are too coarse and the API contract must be redesigned"
super-dev review architecture --status confirmed --comment "Architecture revision approved"
```

The required order for architecture revision is:

1. Update `output/*-architecture.md`
2. Realign Spec / tasks and the implementation plan
3. Continue only after the architecture revision is approved

If the user says quality, security, or delivery evidence is still unacceptable, start a formal quality revision loop:

```bash
super-dev review quality
super-dev review quality --status revision_requested --comment "Quality gate still fails and security issues remain"
super-dev review quality --status confirmed --comment "Quality revision approved"
```

The required order for quality revision is:

1. Fix the quality / security issues
2. Rerun the quality gate and `super-dev release proof-pack`
3. Continue delivery or resume execution only after the revision is approved

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

Optional: set enterprise knowledge controls in `super-dev.yaml`:

```yaml
knowledge_allowed_domains:
  - openai.com
  - python.org
knowledge_cache_ttl_seconds: 1800
language_preferences:
  - python
  - typescript
  - rust
host_compatibility_min_score: 80
host_compatibility_min_ready_hosts: 1
host_profile_targets:
  - codex-cli
  - claude-code
host_profile_enforce_selected: true
```

---

## 2. Command Map

### Core orchestration

```text
/super-dev <requirement>             # recommended inside the host session
```

### Explicit bootstrap

```bash
super-dev bootstrap --name my-project --platform web --frontend next --backend node
```

This explicitly generates:

- `.super-dev/WORKFLOW.md`
- `output/*-bootstrap.md`

so the initialization contract remains visible before host execution begins.

```bash
super-dev start --idea "<requirement>"  # recommended machine-side bootstrap
super-dev "<requirement>"               # local governance entry, not host replacement
super-dev pipeline "<requirement>"      # advanced explicit mode
super-dev repo-map                      # generate a codebase map before working on an existing repo
super-dev dependency-graph              # generate the dependency graph and critical paths before large refactors
super-dev impact "Change the login flow" --files services/auth.py   # inspect impact before touching critical flows
super-dev regression-guard "Change the login flow" --files services/auth.py   # turn impact into an executable regression checklist
super-dev fix "<bug description>"       # explicit bugfix path
super-dev create "<requirement>"        # docs + spec focused path
```

### Spec and task execution loop

```bash
super-dev spec init
super-dev spec list
super-dev spec show <change_id>
super-dev spec propose <change_id> --title "<title>" --description "<description>"
super-dev spec propose <change_id> --title "<title>" --description "<description>" --no-scaffold
super-dev spec add-req <change_id> <spec_name> <req_name> "<requirement text>"
super-dev spec scaffold <change_id>
super-dev spec validate
super-dev spec quality <change_id>
super-dev spec quality <change_id> --json
super-dev spec archive <change_id>

super-dev task list
super-dev task status <change_id>
super-dev task run <change_id>
```

#### Spec quality score and remediation plan

`spec quality` evaluates six dimensions (proposal/spec/plan/tasks/checklist/validation) and returns an `action_plan` with priority and executable commands.

```bash
super-dev spec quality add-billing
super-dev spec quality add-billing --json > output/add-billing-spec-quality.json
```

Recommended CI gate:

```bash
super-dev spec quality add-billing --json > /tmp/spec-quality.json
python - <<'PY'
import json,sys
p=json.load(open('/tmp/spec-quality.json'))
ok = p.get('score', 0) >= 75
print('spec_quality_score=', p.get('score'), 'ok=', ok)
sys.exit(0 if ok else 1)
PY
```

### Quality, risk, and release prep

```bash
super-dev quality --type all
super-dev deploy --cicd all
super-dev deploy --docker
super-dev deploy --cicd all --rehearsal
super-dev deploy --cicd all --rehearsal --rehearsal-verify
super-dev pipeline "<requirement>" --skip-rehearsal-verify
super-dev policy init
super-dev policy init --preset enterprise --force
super-dev policy presets
super-dev policy show
super-dev metrics
super-dev metrics --history --limit 20
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
super-dev integrate matrix
super-dev integrate matrix --json
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
6. `super-dev release proof-pack` aggregates the delivery evidence set.

`release proof-pack` and `release readiness` also ingest the active change's `spec quality` result so the unified release panel includes proposal/spec/plan/tasks/checklist/validation maturity.

To confirm that a host really completed research, wrote the three core docs to disk, and stopped at the confirmation gate, run:

```bash
super-dev integrate validate --auto
```

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

- CLI: `claude-code`, `codebuddy-cli`, `codex-cli`, `cursor-cli`, `gemini-cli`, `kiro-cli`, `opencode`, `qoder-cli`
- IDE: `antigravity`, `codebuddy`, `cursor`, `kiro`, `qoder`, `trae`, `vscode-copilot`, `windsurf`

Recommended auto-detect flow:

```bash
super-dev detect --json
super-dev detect --auto --save-profile
super-dev onboard --auto --yes --force
super-dev doctor --auto --repair --force
```

`detect` generates by default:

- `output/<project>-host-compatibility.json`
- `output/<project>-host-compatibility.md`
- `output/host-compatibility-history/*.json`
- `output/host-compatibility-history/*.md`

With `--save-profile`, Super Dev also updates `super-dev.yaml`:

- `host_profile_targets`
- `host_profile_enforce_selected=true`

Each pipeline run emits contract-audit artifacts:

- `output/*-pipeline-contract.json`
- `output/*-pipeline-contract.md`

Recommended enterprise flow:

1. Initialize policy with `super-dev policy init --preset enterprise --force`.
2. Run `super-dev detect --auto --save-profile` before pipeline execution.
3. Keep `enforce_required_hosts_ready=true` and set `min_required_host_score` based on team baseline.

Interactive installer (default, multi-select hosts):

```bash
./install.sh
super-dev install
```

Non-interactive all-target setup:

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
super-dev run --resume
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
