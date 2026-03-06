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

Current version: `2.0.4`

---

## Project Introduction

`Super Dev` is an AI delivery orchestration tool built for commercial-grade outcomes. Its core goal is to help teams turn project intent into executable engineering assets:

- It does not provide its own model layer and does not replace the host's coding ability
- The host is responsible for model execution, tools, and actual code generation
- `Super Dev` is responsible for workflow governance, design constraints, quality gates, audit artifacts, and delivery standards

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
- Capability-aware host grading with `Certified / Compatible / Experimental`

### 2. Pipeline-Oriented Delivery, Stage 0 to Stage 12

- Similar-product research -> requirement enrichment -> three core docs -> user confirmation gate -> spec -> frontend runtime validation -> backend integration -> quality gate -> delivery
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

### 7. Commercial UI Intelligence

- Built-in UI/UX knowledge base for product type, industry tone, trust modules, page skeletons, anti-patterns, and information density
- Built-in mainstream component ecosystem recommendations across React/Next, Vue, Angular, and Svelte
- The generated UI/UX document now outputs component, form, table, chart, motion, and icon baselines instead of generic style-only guidance
- Host prompts and skills inherit the same rules so the host generates modern commercial interfaces instead of generic AI-looking pages
- `super-dev quality --type ui-review` now performs structure-level visual review against `preview.html` / `output/frontend/index.html`

---

## Installation Options

### 1. uv (recommended)

```bash
uv tool install super-dev
```

Upgrade:

```bash
uv tool upgrade super-dev
```

### 2. PyPI

```bash
pip install -U super-dev
```

### 3. Pin a specific version

```bash
pip install super-dev==2.0.4
```

### 4. Install from GitHub tag

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.4
```

### 5. Source install for development

`uv` development environment:

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
uv sync
uv run super-dev --version
```

`pip` development environment:

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

---

## Simplest Usage (For End Users)

### CLI Hosts (Claude Code / CodeBuddy CLI / Codex CLI / Cursor CLI / Gemini CLI / iFlow CLI / Kimi CLI / Kiro CLI / OpenCode CLI / Qoder CLI)

1. Run `super-dev` in your project root to finish onboarding.  
2. Hosts with native mapping support can run `/super-dev your requirement`.
3. Codex CLI and Kimi CLI currently do not use `/super-dev`; type `super-dev: your requirement` inside the host session.
4. The host is constrained to execute `research -> docs -> user confirmation -> spec -> frontend runtime validation -> backend/testing/delivery`, not jump straight into implementation.

### How the Host Should Understand Super Dev

- `Super Dev` is the local Python CLI in the project plus the host-side rules, skills, and slash mappings.
- The host is responsible for model inference, web research, coding, terminal execution, and file edits.
- `Super Dev` is responsible for the fixed delivery protocol: research, three core docs, confirmation gate, spec, frontend-first execution, backend integration, quality gates, and delivery audit.
- When the user types `/super-dev ...` or `super-dev: ...`, the host should treat it as “enter the Super Dev pipeline,” not as ordinary chat.
- When documents, spec artifacts, quality reports, or delivery outputs need to be generated or refreshed, the host should call the local `super-dev` CLI.
- If the project contains a `knowledge/` directory, the host must read the relevant local knowledge files before drafting documents.
- If `output/knowledge-cache/*-knowledge-bundle.json` exists, the host must inherit its matched local knowledge, research summary, and scenario constraints into the documents, spec, and implementation.

### IDE Hosts (CodeBuddy / Cursor / Kiro / Qoder / Trae / Windsurf)

1. Run `super-dev` in your project root to finish onboarding.  
2. Open the IDE Agent Chat and trigger according to the real host entry.  
3. IDEs with slash support use `/super-dev your requirement`; non-slash IDEs use `super-dev: your requirement`.
4. Non-slash hosts still follow the same research-first pipeline through project rules, AGENTS, or skills instead of bypassing the workflow.

### Host Trigger Matrix

Certification levels:

- `Certified`: host-specific integration model is aligned with the real host capability and is the recommended production path.
- `Compatible`: the integration path is complete and usable, but still needs more long-running real-world certification.
- `Experimental`: integration exists and can be tried, but it still needs broader production validation.

| Host | Type | Certification | Supports `/super-dev` | Correct Trigger | Restart Required After Onboard |
| --- | --- | --- | --- | --- | --- |
| Claude Code | CLI | Certified | Yes | Run `/super-dev your requirement` inside the Claude Code session | No |
| CodeBuddy CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the CodeBuddy CLI session | No |
| CodeBuddy IDE | IDE | Experimental | Yes | Run `/super-dev your requirement` in Agent Chat | No |
| Cursor CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Cursor CLI session | No |
| Cursor IDE | IDE | Experimental | Yes | Run `/super-dev your requirement` in Agent Chat | No |
| Gemini CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Gemini CLI session | No |
| iFlow CLI | CLI | Experimental | Yes | Run `/super-dev your requirement` inside the iFlow CLI session | No |
| Kimi CLI | CLI | Experimental | No | Type `super-dev: your requirement` inside the Kimi CLI session (governed by `.kimi/AGENTS.md`) | No |
| Kiro CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Kiro CLI session | No |
| Kiro IDE | IDE | Experimental | No | Type `super-dev: your requirement` inside Kiro IDE Agent Chat (governed by `.kiro/steering/super-dev.md`) | No |
| OpenCode CLI | CLI | Experimental | Yes | Run `/super-dev your requirement` inside the OpenCode CLI session | No |
| Qoder CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Qoder CLI session | No |
| Qoder IDE | IDE | Experimental | No | Type `super-dev: your requirement` inside Qoder IDE Agent Chat (governed by `.qoder/rules.md`) | No |
| Windsurf | IDE | Experimental | Yes | Run `/super-dev your requirement` in Agent Chat | No |
| Codex CLI | CLI | Certified | No | Restart Codex, then type `super-dev: your requirement`; `.codex/AGENTS.md` + `super-dev-core` Skill will govern execution | Yes |
| Trae | IDE | Certified | No | Type `super-dev: your requirement` inside Trae Agent Chat (governed by `.trae/rules.md`) | No |

If you do not want to reason about host differences yourself, run:

```bash
super-dev start --idea "your requirement"
```

It will:

1. Detect installed hosts on the machine
2. Prefer the highest-certification host with the simplest trigger path
3. Run onboarding automatically and save the host profile
4. Print the exact next step and host trigger you should use

To confirm that the host really loaded Super Dev after onboarding, run:

```bash
super-dev integrate smoke --target <host_id>
```

It prints the host-specific smoke prompt, checklist, and success signal.

### Host-by-Host Usage

#### 1. Claude Code

Install:
```bash
super-dev onboard --host claude-code --force --yes
```

Where to trigger:
Open Claude Code in the project directory and trigger inside the same session.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. This is the recommended primary CLI host.
2. Run `super-dev doctor --host claude-code` if you want to confirm the slash mapping.

#### 2. CodeBuddy CLI

Install:
```bash
super-dev onboard --host codebuddy-cli --force --yes
```

Where to trigger:
Open a CodeBuddy CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Use it directly in the active CLI session.
2. If the session was already open before onboarding, reload project rules and retry.

#### 3. CodeBuddy IDE

Install:
```bash
super-dev onboard --host codebuddy --force --yes
```

Where to trigger:
Open CodeBuddy IDE Agent Chat in the target project and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Use the project-scoped Agent Chat, not a detached generic chat.
2. Let the host finish research before docs and coding.

#### 4. Cursor CLI

Install:
```bash
super-dev onboard --host cursor-cli --force --yes
```

Where to trigger:
Open a Cursor CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Good fit for running research, docs, and coding in one terminal session.
2. If the command list is stale, reopen the Cursor CLI session.

#### 5. Cursor IDE

Install:
```bash
super-dev onboard --host cursor --force --yes
```

Where to trigger:
Open Cursor Agent Chat and make sure the active workspace is the target project.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Keep the full pipeline inside one chat when possible.
2. If rules were not loaded, reopen the workspace or start a new chat.

#### 6. Gemini CLI

Install:
```bash
super-dev onboard --host gemini-cli --force --yes
```

Where to trigger:
Open a Gemini CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Prefer to keep research -> three core docs -> user confirmation -> spec -> frontend runtime validation -> backend/delivery in one continuous session.
2. If the host supports browsing, let it perform competitor research first.

#### 7. iFlow CLI

Install:
```bash
super-dev onboard --host iflow --force --yes
```

Where to trigger:
Open an iFlow CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Currently adapted as a slash-capable CLI host.
2. If slash does not appear, verify that the project command file was written.

#### 8. Kimi CLI

Install:
```bash
super-dev onboard --host kimi-cli --force --yes
```

Where to trigger:
Open a Kimi CLI session in the project directory and trigger there.

Trigger command:
```text
super-dev: your requirement
```

Restart required after onboard: No

Notes:
1. Do not type `/super-dev`; Kimi CLI currently prefers `.kimi/AGENTS.md + text trigger`.
2. Running `super-dev doctor --host kimi-cli` once is recommended.
3. Keep the whole workflow in the same session when possible.

#### 9. Kiro CLI

Install:
```bash
super-dev onboard --host kiro-cli --force --yes
```

Where to trigger:
Open a Kiro CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Use slash directly in CLI mode.
2. If project rules are stale, reopen Kiro CLI from the project root.

#### 10. Kiro IDE

Install:
```bash
super-dev onboard --host kiro --force --yes
```

Where to trigger:
Open Kiro IDE Agent Chat / AI panel in the target project and trigger there.

Trigger command:
```text
super-dev: your requirement
```

Restart required after onboard: No

Notes:
1. Kiro IDE currently prefers steering/rules mode instead of `/super-dev`.
2. If steering or rules did not load, reopen the project window.

#### 11. OpenCode

Install:
```bash
super-dev onboard --host opencode --force --yes
```

Where to trigger:
Open an OpenCode CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Uses the CLI slash path.
2. Even if you also use a global command directory, keep the project-level integration files.

#### 12. Qoder CLI

Install:
```bash
super-dev onboard --host qoder-cli --force --yes
```

Where to trigger:
Open a Qoder CLI session in the project directory and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Suitable for terminal-first pipeline execution.
2. If slash does not work, verify that `.qoder/commands/super-dev.md` exists.

#### 13. Qoder IDE

Install:
```bash
super-dev onboard --host qoder --force --yes
```

Where to trigger:
Open Qoder IDE Agent Chat in the current project and trigger there.

Trigger command:
```text
super-dev: your requirement
```

Restart required after onboard: No

Notes:
1. Qoder IDE currently prefers project rules mode instead of `/super-dev`.
2. If rules are missing, reopen the project or start a new chat thread.

#### 14. Windsurf

Install:
```bash
super-dev onboard --host windsurf --force --yes
```

Where to trigger:
Open Windsurf Agent Chat / Workflow in the current project and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Currently adapted through the IDE slash/workflow path.
2. Best used when research, docs, spec, and coding stay in one workflow.

#### 15. Codex CLI

Install:
```bash
super-dev onboard --host codex-cli --force --yes
```

Where to trigger:
Finish onboarding in the project directory, restart `codex`, then trigger in a new Codex session.

Trigger command:
```text
super-dev: your requirement
```

Restart required after onboard: Yes

Notes:
1. Do not type `/super-dev`; Codex does not use a custom slash entry here.
2. Execution relies on `.codex/AGENTS.md` and `.codex/skills/super-dev-core/SKILL.md`.
3. If the old session did not reload the Skill, restart `codex` and retry.

#### 16. Trae

Install:
```bash
super-dev onboard --host trae --force --yes
```

Where to trigger:
Open Trae Agent Chat in the target project and trigger there.

Trigger command:
```text
super-dev: your requirement
```

Restart required after onboard: No

Notes:
1. Do not type `/super-dev`.
2. Trae is currently rules-first: just open Trae Agent Chat in the project and use the trigger phrase.
3. Then continue delivery from `output/*` and `.super-dev/changes/*/tasks.md`.

## Quick Start (Detailed)

For the host-by-host usage matrix and exact trigger method, see:

- [docs/HOST_USAGE_GUIDE.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_USAGE_GUIDE.md)
- [docs/HOST_CAPABILITY_AUDIT.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_CAPABILITY_AUDIT.md)

### 1. Enter onboarding guide right after install

```bash
super-dev
```

Running `super-dev` without arguments opens the interactive installer guide with multi-select hosts.

If you installed with `uv tool install`, you can also run:

```bash
uv tool run super-dev
```

### 2. One-command non-interactive install

Auto-detect and onboard installed hosts:

```bash
super-dev install --auto --force --yes
```

Onboard all hosts:

```bash
super-dev install --all --force --yes
```

Check or upgrade to the latest version:

```bash
super-dev update --check
super-dev update
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

Default execution order:

1. Host researches similar products and writes `output/*-research.md`
2. Generate `output/*-prd.md`
3. Generate `output/*-architecture.md`
4. Generate `output/*-uiux.md`
5. Stop at the document confirmation gate and wait for user approval or revision requests
6. Only after approval, generate spec and `tasks.md`
7. Implement frontend first with runtime validation, then proceed to backend, testing, gates, and delivery

You can also manage document approval from the terminal:

```bash
super-dev review docs
super-dev review docs --status revision_requested --comment "Add clearer differentiation and improve hero information architecture"
super-dev review docs --status confirmed --comment "Core documents approved, proceed to Spec"
```

### 6. Review key artifacts

Check `output/` after each run:

- `*-research.md`
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

`/super-dev` enforces this sequence: research first -> generate PRD/Architecture/UIUX -> wait for document approval -> create Spec/tasks -> then coding.  
Modern commercial UI/UX constraints are enforced at generation time: no purple/pink gradient-first themes, no emoji icons, no generic template output, and typography/tokens/grid/state matrices must be defined before page implementation.

Codex CLI currently does not use `/super-dev`; it relies on `.codex/AGENTS.md` and the loaded `super-dev-core` Skill. Use `super-dev: your requirement` as the text trigger.

If slash mapping is unavailable, run the terminal entry in the same project root (local Super Dev orchestration only):

```bash
super-dev "your requirement"
```

Notes:

1. The terminal entry does not replace host model capability.
2. Actual coding should still happen inside an onboarded host session.
3. If the host supports web/browse/search, Super Dev requires similar-product research first.

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
- `trae` (Rules-first)
- `windsurf`

### Host Adaptation Model (CLI/IDE)

- `CLI hosts (native slash)`: trigger `/super-dev` inside the host session, and let the host model perform code work
- `CLI hosts (non-slash)`: type `super-dev: your requirement` inside the host session and let AGENTS / rules drive execution
- `IDE hosts (native slash)`: trigger `/super-dev` in Agent Chat, then enforce execution through rules + skill constraints
- `IDE hosts (non-slash)`: type `super-dev: your requirement` in Agent Chat and let project rules drive execution
- `Terminal entry`: `super-dev "requirement"` only triggers local orchestration and does not directly call a host model session

Inspect host adaptation matrix (official docs links, adaptation mode, injection paths, detection strategy):

```bash
super-dev integrate matrix
super-dev integrate matrix --json
```

---

## Command Quick Reference

```bash
# uv
uv tool install super-dev
uv tool upgrade super-dev
uv sync
uv run super-dev --version

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
super-dev release readiness
super-dev deploy --cicd all --rehearsal --rehearsal-verify
```

---

## Development And Release With uv

```bash
# sync dependencies
uv sync

# local checks
uv run pytest -q
uv run ruff check super_dev tests
uv run mypy super_dev

# build
uv build

# publish
UV_PUBLISH_TOKEN="<your-token>" uv publish
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
