# Super Dev

<div align="center">

# Super Dev Squad
### An AI delivery orchestration tool for commercial-grade outcomes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success)](.github/workflows/ci.yml)

[简体中文](README.md) | English

</div>

---

## Version

Current version: `2.0.3`

---

## Project Introduction

`Super Dev` is an AI delivery orchestration tool built for commercial-grade outcomes. Its core goal is to help teams turn project intent into executable engineering assets:

- Convert requirements into production artifacts: PRD, architecture, UI/UX, spec, task plans, and delivery manifests
- Run development through a standardized pipeline: traceable, resumable, auditable, and reviewable
- Enforce quality at every stage: policy governance, red-team checks, quality gates, and release rehearsals
- Unify collaboration across CLI and IDE hosts under one delivery standard

---

## Core Features

### 1. Host Onboarding Governance

- Unified onboarding for mainstream CLI/IDE hosts
- Auto generation of host rules, `/super-dev` mapping, and skill paths
- End-to-end onboarding loop with `detect/onboard/doctor/setup/install`

### 2. Pipeline-Oriented Delivery, Stage 0 to Stage 12

- Requirement enrichment -> docs -> spec -> scaffold -> red-team -> quality gate -> delivery
- Resume support for failed/interrupted runs (`run --resume`)
- Works for both greenfield and iterative delivery

### 3. Policy Governance (Policy DSL)

- `default / balanced / enterprise` presets
- Enforce red-team and quality gates
- Minimum quality threshold and CI/CD whitelist
- Required host and ready+score hard checks

### 4. Host Profile and Compatibility Gate

- Auto-detect available hosts and score readiness
- Emit compatibility report and history
- `--save-profile` writes host profile into `super-dev.yaml`

### 5. Auditable Delivery Assets

- `pipeline-metrics` telemetry
- `pipeline-contract` stage evidence
- `resume-audit` for resumed runs
- Delivery package: manifest/report/archive

### 6. Commercial-Grade Gate Chain

- Red-team checks (security/performance/architecture)
- Quality gate (scenario + policy thresholds)
- Release rehearsal and rollback playbooks

---

## Installation Options

### 1. PyPI (recommended)

```bash
pip install -U super-dev
```

### 2. Pin a specific version

```bash
pip install super-dev==2.0.3
```

### 3. Install from GitHub tag

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.3
```

### 4. Source install for development

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

---

## Simplest Usage (For End Users)

### CLI Hosts (Claude Code / CodeBuddy CLI / Codex CLI / Cursor CLI / Gemini CLI / iFlow CLI / Kimi CLI / Kiro CLI / OpenCode CLI / Qoder CLI)

1. Run `super-dev` in your project root to finish onboarding.  
2. In the host session, run: `/super-dev your requirement`.
3. Onboarding now installs both project-level and global `/super-dev` mapping so you can reuse it across directories.

### IDE Hosts (CodeBuddy / Cursor / Kiro / Qoder / Trae / Windsurf)

1. Run `super-dev` in your project root to finish onboarding.  
2. In IDE Agent Chat, try: `/super-dev your requirement`.  
3. IDEs with native slash support get project-level `/super-dev` mapping; Skill-only IDEs skip slash and install rules + skill only.

---

## Quick Start (Detailed)

### 1. Enter onboarding guide right after install

```bash
super-dev
```

Running `super-dev` without arguments opens the interactive installer guide with multi-select hosts.

### 2. One-command non-interactive install

Auto-detect and onboard installed hosts:

```bash
super-dev install --auto --force --yes
```

Onboard all hosts:

```bash
super-dev install --all --force --yes
```

### 3. Build host profile

```bash
super-dev detect --auto --save-profile
```

This generates compatibility artifacts and updates `super-dev.yaml`:

- `host_profile_targets`
- `host_profile_enforce_selected=true`

### 4. Initialize enterprise policy

```bash
super-dev policy init --preset enterprise --force
super-dev policy show
```

### 5. Start pipeline delivery

```bash
super-dev "Build an enterprise CRM with auth, RBAC, accounts, opportunities, and reporting"
```

Or explicit mode:

```bash
super-dev pipeline "Build an enterprise CRM" --platform web --frontend react --backend python --cicd github
```

Host hard gate is enabled by default: pipeline execution is blocked when no `ready` host is available.

### 6. Review key artifacts

Check `output/` after each run:

- `*-prd.md`
- `*-architecture.md`
- `*-uiux.md`
- `*-redteam.md`
- `*-quality-gate.md`
- `*-pipeline-metrics.json`
- `*-pipeline-contract.json`
- `delivery/*-delivery-manifest.json`
- `rehearsal/*-rehearsal-report.md`

### 7. Trigger from host sessions

If host supports slash command mapping:

```text
/super-dev your requirement
```

`/super-dev` enforces this sequence: generate PRD/Architecture/UIUX first -> create Spec/tasks -> then coding.  
Modern commercial UI/UX constraints are enforced at generation time (no purple/pink gradient-first themes, no emoji icons, no generic template output).

If slash mapping is unavailable, run the terminal entry in the same project root (local Super Dev orchestration only):

```bash
super-dev "your requirement"
```

- The terminal entry does not directly talk to the host model session
- Code generation and code edits must still happen inside the onboarded host tool

---

## Usage Scenarios

## 1. 0-to-1 (Greenfield)

Use when you only have requirements and no production repository.

### Recommended flow

1. Create workspace and onboard hosts
2. Run `detect --save-profile`
3. Initialize `enterprise` policy
4. Execute requirement-driven pipeline
5. Implement and iterate against `tasks.md`
6. Pass red-team, quality gate, and release rehearsal

### Example

```bash
mkdir crm-project && cd crm-project
pip install -U super-dev
super-dev
super-dev detect --auto --save-profile
super-dev policy init --preset enterprise --force
super-dev "Build an enterprise CRM with multi-tenant support, RBAC, leads, accounts, opportunities, and reporting"
```

---

## 2. 1-N+1 (Iterative Delivery on Existing System)

Use when you already have a product and need incremental capability rollout.

### Recommended flow

1. Analyze current repository
2. Create spec change
3. Execute tasks incrementally
4. Pass red-team and quality gate for each change
5. Merge and release in small batches

### Example

```bash
cd existing-project
super-dev analyze .
super-dev spec init
super-dev spec propose add-billing --title "Add Billing Center" --description "plans, subscriptions, invoices, payment callbacks"
super-dev task run add-billing
super-dev quality --type all
```

---

## Supported Hosts

### CLI Hosts

- `claude-code`
- `codebuddy-cli`
- `codex-cli`
- `cursor-cli`
- `gemini-cli`
- `iflow`
- `kimi-cli`
- `kiro-cli`
- `opencode`
- `qoder-cli`

### IDE / Extension Hosts

- `codebuddy`
- `cursor`
- `kiro`
- `qoder`
- `trae` (Skill-only)
- `windsurf`

### Host Adaptation Model (CLI/IDE)

- `CLI hosts`: trigger `/super-dev` inside the host session, and let the host model perform code work
- `IDE hosts (native slash)`: trigger `/super-dev` in Agent Chat, then enforce execution through rules + skill constraints
- `IDE hosts (Skill-only)`: trigger `super-dev-core` skill in Agent Chat, then execute by `output/*` and `tasks.md`
- `Terminal entry`: `super-dev "requirement"` only triggers local orchestration and does not directly call a host model session

Inspect host adaptation matrix (official docs links, adaptation mode, injection paths, detection strategy):

```bash
super-dev integrate matrix
super-dev integrate matrix --json
```

---

## Command Quick Reference

```bash
# onboarding
super-dev
super-dev install --auto --force --yes
super-dev detect --auto --save-profile
super-dev doctor --auto --repair --force
super-dev integrate matrix --target codex-cli

# pipeline delivery
super-dev "your requirement"
super-dev pipeline "your requirement" --platform web --frontend react --backend python --cicd github
super-dev run --resume

# policy governance
super-dev policy presets
super-dev policy init --preset enterprise --force
super-dev policy show

# spec and task flow
super-dev spec init
super-dev spec list
super-dev task run <change_id>

# quality and release
super-dev quality --type all
super-dev metrics --history --limit 20
super-dev deploy --cicd all --rehearsal --rehearsal-verify
```

---

## Pre-release Check

```bash
./scripts/preflight.sh
```

---

## Related Docs

- [Workflow Guide](docs/WORKFLOW_GUIDE_EN.md)
- [Quick Start](docs/QUICKSTART.md)
- [Publishing Guide](docs/PUBLISHING.md)
- [Install Options](docs/INSTALL_OPTIONS.md)

---

## WeChat Official Account

![Super Dev WeChat Official Account](wechat.png)

---

## License

MIT
