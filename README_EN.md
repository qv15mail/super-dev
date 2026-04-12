# Super Dev

<div align="center">

<img src="docs/assets/super-dev-logo.png" alt="Super Dev - AI PIPELINE ORCHESTRATOR" width="600">

### AI Pipeline Orchestrator for Commercial-Grade Delivery

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)

[简体中文](README.md) | English

</div>

---

## Version

Current version: `2.3.6`

- Release notes: [v2.3.6](docs/releases/2.3.6.md)
- Website changelog: [superdev.goder.ai/changelog](https://superdev.goder.ai/changelog)

## What's New in 2.3.0

### Pipeline Intelligence

- **Pipeline state file**: Each phase auto-writes `.super-dev/pipeline-state.json` so the host can read current progress.
- **Pipeline cost tracking**: Per-phase duration and file counts recorded to `.super-dev/metrics/pipeline-cost.json`, with finally-protection for crash safety.
- **State change events**: phase_started / phase_completed / phase_failed / pipeline_completed auto-trigger SessionBrief updates and memory extraction.

### CLAUDE.md include directive Knowledge References

- Generated project-root `CLAUDE.md` and the compatibility mirror `.claude/CLAUDE.md` now include `@./knowledge/...` references automatically.
- Host natively processes include directive to load technology-stack knowledge files.
- Frontend support: Next.js / React / Vue / Nuxt / Angular / Svelte.
- Backend support: FastAPI / Django / NestJS / Express / Spring Boot.
- Database support: PostgreSQL / MySQL / MongoDB / Redis.

### Conditional Rules System

- New module `super_dev/rules/` supporting `.super-dev/rules/*.md` conditional rules.
- Rules can specify `paths: ["src/**/*.tsx"]` in frontmatter to target specific files.
- Supports exclusion patterns like `!test/**`.

### User Experience Enhancements

- **First-use onboarding**: 3-step quick-start panel, auto-hidden after 4 displays.
- **Tips system**: Stage-aware contextual tips during pipeline execution.
- **Project templates**: `super-dev init --template ecommerce/saas/dashboard/mobile/api/blog/miniapp`.
- **`doctor --fix`**: Auto-repair detected installation issues.
- **Shell completion**: `super-dev completion bash/zsh/fish`.
- **Version update check**: PyPI 24h cache, prompts upgrade when a new version is available.
- **`super-dev feedback`**: Quick-open GitHub Issues for feedback.
- **`super-dev migrate`**: One-command migration from 2.2.0 to 2.3.0.

### Validation Script Enhancements

- **Multi-level output**: Level 1 (blocking) / Level 2 (warning) / Level 3 (suggestion).
- **New checks**: console.log / hardcoded localhost / TODO-FIXME / large files / package.json scripts.
- **Emoji hooks**: Reports specific emoji characters found and file types.

### Enforcement System

- `super-dev enforce install` — auto-configure host hooks (emoji checks, etc.).
- `super-dev enforce validate` — run constraint validation scripts.
- `super-dev enforce status` — view enforcement configuration status.
- `super-dev hooks history` — inspect recent hook execution history.
- `super-dev harness status` — inspect workflow/framework/hook harness status in one place, including the recent operational timeline.
- `super-dev harness operational` — inspect the unified operational harness report, including the current operational focus and the first recommended action.
- `super-dev harness timeline` — inspect the merged operational timeline across workflow snapshots, semantic events, and hook events.

### Memory System

- 4 memory types: user, feedback, project, reference.
- `super-dev memory list / show / forget / consolidate` commands.
- Dream consolidator: 4-phase background memory merge (dedup, aggregate, summarize, write-back).

### Code Generators

- `super-dev generate scaffold --frontend next` — Next.js App Router scaffold (16 files).
- `super-dev generate components` — UI component scaffold (Button/Card/Input/Modal/Nav/Layout).
- `super-dev generate types` — shared TypeScript types from architecture docs.

### Bug Fixes

- `detect --auto` now actually installs files (previously only generated reports).
- `detect` and `doctor` now use unified detection logic (no more contradictory results).
- SKILL.md: `config show` corrected to `config list`.
- Repository URL corrected to `shangyankeji/super-dev`.

---

## What Was New in 2.2.0

### Knowledge-Driven Governance

The pipeline now tracks which knowledge files are referenced at every stage. A Knowledge Tracker records hits, generates a knowledge reference report, and enforces a configurable minimum coverage threshold. This closes the loop between the `knowledge/` directory and actual pipeline consumption.

### Programmable Governance (Validation Rule Engine)

A YAML-driven validation rule engine ships with 14 built-in rules and supports project-level custom rules via `.super-dev/rules/custom_rules.yaml`. Rules are pluggable into any pipeline stage, with configurable severity (error / warning) and a `fail_on_warning` switch.

### Expert System Upgrade

The expert roster has been expanded to 11 domain specialists (PRODUCT, PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA). Each expert carries an objective definition, background story, thinking framework, and quality criteria. The generated AI prompts exceed 600 lines, ensuring professional baselines at every stage.

### Performance Metrics

A delivery-efficiency measurement system now tracks DORA four key metrics (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Mean Time to Recovery) plus Rework Rate. Metrics can be exported as JSON for external dashboards.

### ADR Generator

Architecture Decision Records are automatically generated from the architecture configuration. The generator extracts technology choices and produces ADR documents in MADR, Nygard, or custom templates.

### Prompt Template Versioning

Prompt templates are now stored as versioned Markdown files under `super_dev/templates/`. Templates support semver, date, or hash versioning strategies so prompt evolution is traceable.

### OpenClaw Native Plugin

OpenClaw integrates via its native Plugin SDK with 13 registered tools. Users install via `openclaw plugins install @super-dev/openclaw-plugin` or the ClawHub Skill at `clawhub install super-dev`.

### Governance CLI

```bash
super-dev governance status              # view governance capability status
super-dev governance rules list          # list all validation rules (built-in + custom)
super-dev governance rules validate      # run all validation rules against the current project
super-dev governance knowledge-report    # generate knowledge reference report and coverage analysis
super-dev governance adr generate        # generate ADR documents from architecture config
super-dev governance adr list            # list generated ADRs
super-dev governance metrics show        # show delivery efficiency metrics
super-dev governance metrics export      # export metrics data as JSON
super-dev governance templates list      # list prompt templates and versions
super-dev governance templates show <id> # view a specific template
```

---

## Demo Video

<video controls playsinline preload="metadata" src="https://shangyankeji.github.io/super-dev/demo.mp4" width="100%"></video>

- Stream online: [Watch the demo](https://shangyankeji.github.io/super-dev/demo.mp4)
- Repository file: [demo.mp4](super-dev-website/public/demo.mp4)

---

## What is Super Dev

`Super Dev` is an AI pipeline orchestrator for commercial-grade delivery. It organizes the model capabilities inside your host into a stable, transparent, and auditable engineering pipeline.

**Division of responsibility:**

- The host handles model inference, web research, code generation, terminal execution, and file modifications.
- `Super Dev` handles workflow governance, design constraints, quality gates, audit artifacts, and delivery standards.

**Problems it solves:**

- Converts requirements into production artifacts: PRD, architecture, UI/UX spec, task plans, and delivery manifests.
- Organizes development into a standardized pipeline: traceable, resumable, auditable, and reviewable.
- Enforces quality at every stage: policy governance, red-team review, quality gates, and release rehearsals.
- Unifies collaboration across 20 CLI and IDE hosts under one delivery standard.

---

## Quick Start

Regular users only need 2 terminal commands:

```bash
# Enter the host onboarding flow
super-dev

# Upgrade to the latest version and migrate onboarded hosts
super-dev update
```

After onboarding, regular use moves back into the host:

```text
/super-dev your requirement
super-dev: your requirement
/super-dev-seeai your competition brief
super-dev-seeai: your competition brief
```

Correct mental model:

- The terminal is only for onboarding and upgrading.
- The host is where research, the three core docs, approval gates, spec, implementation, quality gates, and delivery happen.
- Auto-judgement is allowed during onboarding and upgrade, not during normal development flow.
- `Integrated` and `runtime verified` are different states. Files existing does not prove the host actually follows the governed flow.

Recommended first run:

1. Run `super-dev` in the terminal.
2. Let the installer detect hosts and write the required project-level and global protocol surfaces.
3. Open the host and use `/super-dev` or `super-dev:`.
4. Let the host finish research, PRD, Architecture, and UI/UX first.
5. Only move to Spec and implementation after the docs are confirmed.

SEEAI competition fast mode:

- Entry: `/super-dev-seeai` or `super-dev-seeai:`
- It still keeps `research -> docs -> docs confirm -> spec`
- After Spec it goes straight into an integrated full-stack sprint, without a separate preview confirmation gate
- Best for 30-minute showcase builds such as a polished landing page, mini-game, or focused demo tool

Advanced/internal commands still exist, but they are no longer the public path:

```bash
super-dev init
super-dev onboard
super-dev detect
super-dev doctor
super-dev run --status
super-dev run frontend
super-dev review docs
```

Delivery and governance commands:

```bash
super-dev integrate audit --auto --repair --force
super-dev integrate validate --auto
super-dev feature-checklist
super-dev product-audit
super-dev release proof-pack
super-dev release readiness
super-dev review preview --status confirmed --comment "Frontend preview approved"
super-dev review architecture --status revision_requested --comment "Technical plan needs redesign"
super-dev review quality --status revision_requested --comment "Quality gate failed and needs remediation"
```

---

## Core Features

### 1. 11-Expert Agent Architecture

Super Dev currently ships with eleven domain-expert agents. Each expert is injected into prompts at the corresponding pipeline stage so the host stays constrained to professional-grade output:

| Expert | Role | Injection Stages |
|--------|------|-----------------|
| PRODUCT | Product Lead | research, prd, quality, delivery |
| PM | Product Manager | research, prd |
| ARCHITECT | System Architect | architecture |
| UI | Interface Designer | uiux, frontend |
| UX | Interaction Designer | uiux, frontend |
| SECURITY | Security Engineer | architecture, backend, quality |
| CODE | Software Engineer | frontend, backend |
| DBA | Database Architect | architecture, backend |
| QA | Quality Assurance | quality |
| DEVOPS | DevOps Engineer | delivery |
| RCA | Root Cause Analyst | quality, delivery |

Each expert carries: objective definition, background story, thinking framework, and quality criteria. The generated AI prompts ensure every stage meets domain-specific professional baselines.

### 2. UI Design Intelligence System

A built-in design intelligence engine that directly constrains visual quality during frontend implementation:

- **119 color palettes**: 84 product palettes + 35 aesthetic palettes, all with automatic dark mode generation.
- **39 component libraries**: covering 11 frontend stacks (React 15 / Vue 9 / Angular 4 / Svelte 2 / others).
- **17 typography presets**: based on Google Fonts, categorized by product tone and personality.
- **Complete design token system**: color scales, shadows, motion, typography, and spacing.
- **12-item pre-delivery checklist**: A11y, responsive design, dark mode, loading states, empty states, error states, and more.
- **10 industry customizations**: education, healthcare, e-commerce, fintech, SaaS, social, content, enterprise, utilities, and gaming.

The UI system is no longer only advisory. It is frozen into actual artifacts:

- `output/*-uiux.md`
- `output/*-ui-contract.json`
- `output/frontend/design-tokens.css`
- `output/*-ui-contract-alignment.md`
- `output/*-ui-contract-alignment.json`

Prompts, frontend scaffolds, implementation scaffolds, UI review, frontend runtime, quality gate, proof-pack, and release readiness all consume that same UI contract.

Key review commands:

- `super-dev quality --type ui-review`
- `super-dev integrate validate --target <host_id>`
- `super-dev release proof-pack`

### 3. Pipeline Orchestration Engine

- **9-stage standard pipeline**: research -> prd -> architecture -> uiux -> spec -> frontend -> backend -> quality -> delivery.
- **Checkpoint and resume**: interrupted pipelines resume from the last completed stage without losing progress.
- **Stage timeout protection**: each stage has a timeout mechanism to prevent indefinite stalling.
- **Confirmation gates**: mandatory user confirmation after core documents and after frontend preview.
- **Stage jumping**: `super-dev run <stage>` allows jumping to any stage at any time.
- **UI revision loop**: when the frontend needs another pass, a formal revision loop can be triggered.
- **Dual-mode delivery**: works for both greenfield (0-1) and iterative (1-N+1) projects.
- **Continuation routing**: internal recovery and status commands share the same workflow state and action card semantics.
- **Session recovery card**: `.super-dev/SESSION_BRIEF.md` and `.super-dev/workflow-state.json` persist the current action, host first sentence, machine action, and continuity rules.
- **Recent operational timeline**: workflow snapshots, semantic workflow events, and hook events are merged into one timeline that now surfaces in `SESSION_BRIEF`, Workflow Harness, proof-pack, and release readiness.
- **Rework-first state handling**: docs confirmation, preview confirmation, UI redesign, architecture rework, and quality remediation all stay inside one governed state machine.

### 4. Document Generation Engine

Super Dev generates an initial document framework for each stage. The host LLM then enriches it with user requirements, web research, and expert knowledge:

| Document | Content |
|----------|---------|
| PRD | User personas, feature matrix, acceptance criteria, competitive benchmarking, business rules |
| Architecture | System architecture, data models, API contracts, security strategy, deployment plan |
| UIUX | Design tokens, page skeletons, component inventory, interaction states, responsive strategy |

The host expands documents based on actual project needs. Final document scope depends on project complexity. Supports 10 industry-specific customizations: education, healthcare, e-commerce, fintech, SaaS, social, content, enterprise, utilities, and gaming.

### 5. Quality Gate System

- A11y accessibility checks.
- Performance budget enforcement.
- Red-team review (security / performance / architecture).
- Fix command suggestions (detected issues produce actionable repair instructions).
- Policy governance (`default` / `balanced` / `enterprise` presets).
- Spec quality scoring and release-readiness panel.
- UI contract execution checks (`ui-contract.json`, `design-tokens.css`, frontend runtime, and UI alignment evidence must stay consistent).

### 6. Host Onboarding Governance

- 20 hosts with unified onboarding (9 CLI + 11 IDE).
- OpenClaw is handled separately as a native plugin host via `openclaw plugins install @super-dev/openclaw-plugin`.
- Auto-generates host rule files, slash command mappings, and Skill directories.
- Host capability boundary modeling: Certified / Compatible / Experimental three-tier certification.
- `detect` / `onboard` / `doctor` / `setup` / `install` / `start` form a closed onboarding loop.
- `--dry-run` preview mode and `--stable-only` stable-only mode.
- `doctor`, `detect`, and `start` now emit decision cards: recommended host, recommendation reason, first action, folded candidate list, and path-override hints.
- Supports Windows registry hits, shim directories, common install paths, and `SUPER_DEV_HOST_PATH_<HOST>` explicit path overrides.
- If you explicitly choose a host, Super Dev centers guidance around that host instead of letting auto-detection override your intent.

### 7. Codebase Intelligence and Change Analysis

- `repo-map`: generates a codebase map with suggested reading order.
- `feature-checklist`: audits PRD feature coverage so pipeline completion is distinct from full scope completion.
- `dependency-graph`: outputs module dependencies and critical paths.
- `impact`: analyzes blast radius of changes, risk levels, and recommended actions.
- `regression-guard`: converts impact analysis into an executable regression checklist.

### 8. Auditable Delivery

- `pipeline-metrics`: telemetry and metrics report.
- `pipeline-contract`: stage-level contract evidence.
- `resume-audit`: resume execution audit trail.
- `delivery manifest/report/archive`: delivery package.
- `proof-pack`: delivery evidence bundle with executive summary.
- `release readiness`, `Spec Quality`, and `Scope Coverage`: unified release scoring panel.
- UI Contract Alignment is part of proof-pack and release readiness, not just an internal UI review detail.
- Governance snapshots, frontend runtime, validation reports, and knowledge tracking now participate in delivery closure.

### 9. Knowledge Base

- Project-level `knowledge/` directory for domain knowledge files.
- Knowledge bundle caching at `output/knowledge-cache/*-knowledge-bundle.json`.
- Matched local standards, scenario packs, and checklists are treated as hard constraints.
- Hosts must read relevant knowledge files before drafting PRD, architecture, and UIUX documents.
- Knowledge hits are inherited into Spec and implementation stages.

### 10. Policy Governance (Policy DSL)

Parameterized workflow governance through a Policy DSL:

- **default**: standard preset, suitable for individuals and small teams.
- **balanced**: balanced preset, suitable for medium-sized teams.
- **enterprise**: enterprise preset, higher quality thresholds, host profiling requirements, and configurable required hosts per project.

Governance control dimensions:

- Mandatory red-team / quality gate toggle.
- Minimum quality threshold enforcement.
- CI/CD platform whitelist.
- Required hosts and ready+score hard validation (enabled per project).
- Automatic host profiling and scoring.
- `host-compatibility` report with history tracking.

Configurable via `super-dev.yaml` policy section.

---

## How It Works

1. User runs `super-dev` in the project directory.
2. The onboarding wizard connects Super Dev to the target host.
3. User triggers Super Dev using the host's supported entry, such as `/super-dev requirement`, `super-dev: requirement`, Codex App/Desktop selecting `super-dev` from the `/` list, or Codex CLI typing `$super-dev`.
4. The host enters the Super Dev pipeline; 11 expert agents are injected by stage.
5. The host handles web research, inference, coding, execution, and file modifications.
6. Super Dev handles workflow, documents, gates, audit, and delivery standards.

Standard pipeline flow: `research -> prd -> architecture -> uiux -> user confirmation -> spec -> frontend -> preview confirmation -> backend -> quality -> delivery`

New features follow the full pipeline. Bug fixes follow a lightweight patch path (symptoms, reproduction, blast radius, regression risk) without skipping documentation. Analysis stages automatically exclude `.venv`, `site-packages`, `node_modules`, and other non-source directories.

### How Hosts Understand Super Dev

- `Super Dev` is a local Python CLI tool plus host-side rule files / Skills / slash mappings.
- The host handles inference, research, coding, and execution. `Super Dev` handles pipeline flow, gates, and audit.
- When the user uses the host-supported Super Dev entry (`/super-dev`, `super-dev:`, Codex App/Desktop `/`-list skill entry, or Codex CLI `$super-dev`), the host switches to pipeline mode.
- If a `knowledge/` directory exists, the host reads relevant knowledge files before drafting documents.
- If `output/knowledge-cache/*-knowledge-bundle.json` exists, its knowledge hits are inherited into all later stages.

---

## Installation

### 1. uv (recommended)

```bash
uv tool install super-dev
```

Upgrade:

```bash
uv tool upgrade super-dev
super-dev update
```

### 2. PyPI

```bash
pip install -U super-dev
super-dev update
```

After installation, run `super-dev` to launch the interactive host onboarding wizard (`Up/Down` to navigate, `Space` to select, `Enter` to install, `A` for all, `C` for CLI only, `I` for IDE only, `R` to reset). The terminal prints the exact trigger command for each selected host.

To explicitly initialize the project contract before onboarding:

```bash
super-dev bootstrap --name my-project --platform web --frontend next --backend node
```

This generates `.super-dev/WORKFLOW.md` and `output/*-bootstrap.md` to lock down initialization spec, trigger method, and stage sequence.

### 3. Pin a specific version

```bash
pip install super-dev==2.3.6
```

### 4. Install from GitHub tag

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.3.6
```

### 5. Source install for development

Using `uv`:

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
uv sync
uv run super-dev --version
```

Using `pip`:

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

### Dependency Notes

`pip` / `uv` automatically installs Super Dev's own Python dependencies (`rich`, `pyyaml`, `ddgs`, `requests`, `beautifulsoup4`, `fastapi`, `uvicorn`, etc.).

It does **not** install:

- Host applications (Claude Code, Codex CLI, Gemini CLI, Cursor, Trae, Windsurf, etc.)
- System runtimes (Node.js, npm, pnpm, Docker, database services)
- Host authentication state, browsing permissions, or API keys
- Project-specific frontend/backend runtime dependencies

In short: `pip` / `uv` installs **Super Dev's Python dependencies**. It does not install **host tools or system environments** on your behalf.

---

## Architecture Overview

### System Flow Architecture

Shows the relationship between users, host-side tools, the Super Dev orchestration engine, and final artifacts.

![System Overview](docs/assets/architecture/en/system-overview.png)

### Pipeline Stage Flow

Details the internal execution flow after each host-side trigger.

![Pipeline Stages](docs/assets/architecture/en/pipeline-12-phase.png)

### Core Module Topology

Shows the responsibility boundaries and call relationships of core source directories under `super_dev`.

![Module Topology](docs/assets/architecture/en/module-topology.png)

---

## 20 Unified Hosts + 1 Manual Plugin Host

Super Dev officially documents 20 unified onboarding hosts plus 1 manual plugin host:

- **Certified**: fully aligned integration model; recommended for production use.
- **Compatible**: complete integration path; awaiting extended real-world validation.
- **Experimental**: functional integration; needs broader production testing.

### Unified CLI Hosts (9)

| Host | Trigger | Terminal Entry |
|------|---------|-----------------|
| Claude Code | `/super-dev your requirement` | `super-dev` |
| Codex | App/Desktop: `/super-dev` (skill entry) / CLI: `$super-dev` / fallback: `super-dev: your requirement` | `super-dev` |
| Gemini CLI | `/super-dev your requirement` | `super-dev` |
| OpenCode | `/super-dev your requirement` | `super-dev` |
| Kiro CLI | `/super-dev your requirement` | `super-dev` |
| Cursor CLI | `/super-dev your requirement` | `super-dev` |
| Qoder CLI | `/super-dev your requirement` | `super-dev` |
| Copilot CLI | `super-dev: your requirement` | `super-dev` |
| CodeBuddy CLI | `/super-dev your requirement` | `super-dev` |

### IDE Hosts (11)

| Host | Trigger | Terminal Entry |
|------|---------|-----------------|
| Antigravity | `/super-dev your requirement` | `super-dev` |
| Cursor IDE | `/super-dev your requirement` | `super-dev` |
| Windsurf | `/super-dev your requirement` | `super-dev` |
| Kiro IDE | `/super-dev your requirement` | `super-dev` |
| Qoder IDE | `/super-dev your requirement` | `super-dev` |
| Trae | `super-dev: your requirement` | `super-dev` |
| CodeBuddy IDE | `/super-dev your requirement` | `super-dev` |
| Copilot (VS Code) | `super-dev: your requirement` | `super-dev` |
| Roo Code | `super-dev: your requirement` | `super-dev` |
| Kilo Code | `super-dev: your requirement` | `super-dev` |
| Cline | `super-dev: your requirement` | `super-dev` |

### Public Terminal Entry

```bash
super-dev
super-dev update
```

Run `super-dev` to open the installer and choose the target host there. `onboard --host`, `doctor`, and other CLI commands remain available for maintenance, but they are no longer the normal end-user path.

### Per-Host Usage Details

#### CLI Hosts

**Claude Code**

```bash
super-dev
```

Trigger location: launch Claude Code in the project directory, then trigger within the same session.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Recommended as the primary CLI host.
2. Run `super-dev doctor --host claude-code` after onboarding to confirm project-root `CLAUDE.md`, project `.claude/skills/super-dev/`, user `~/.claude/skills/`, the compatibility slash surface, and the optional plugin enhancement are all active.
3. Claude Code is now modeled skills-first: the primary surfaces are `CLAUDE.md + .claude/skills + ~/.claude/skills`; `.claude/commands/` and `.claude/agents/` remain compatibility enhancements only.
4. Super Dev can also install `.claude-plugin/marketplace.json` plus `plugins/super-dev-claude/.claude-plugin/plugin.json` as an optional repo-local Claude plugin enhancement.

**Codex**

```bash
super-dev
```

Trigger location: after onboarding, restart `codex`, then trigger in the new session.
Trigger command:
`Codex App/Desktop: choose super-dev from the / list`
`Codex CLI: $super-dev`
`Fallback: super-dev: your requirement`
Restart required after onboarding: Yes.

Notes:
1. In Codex app/desktop, prefer selecting `super-dev` directly from the `/` list; that is the enabled Skill entry, not a project-level custom slash command.
2. In Codex CLI, prefer explicit `$super-dev`.
3. If you are already continuing inside natural-language context, you can still use `super-dev: your requirement` as the AGENTS-driven fallback.
4. The base integration surfaces are project `AGENTS.md`, project `.agents/skills/super-dev/SKILL.md`, global `CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`), and the official user-level Skill at `~/.agents/skills/super-dev/SKILL.md`.
5. Super Dev also installs an optional repo-local Codex plugin enhancement at `.agents/plugins/marketplace.json` + `plugins/super-dev-codex/.codex-plugin/plugin.json` so Codex App/Desktop can expose a richer local plugin surface alongside AGENTS + Skills.
6. `super-dev-core` is still installed as a compatibility alias for older setups.
7. If a previous session did not load the new surfaces, restart `codex` and try again.

**Gemini CLI**

```bash
super-dev
```

Trigger location: launch Gemini CLI in the project directory.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Complete the full pipeline within a single session: research -> three documents -> user confirmation -> Spec -> frontend verification -> backend / delivery.
2. If the host supports web access, let it complete competitor research first.

**Cursor CLI**

```bash
super-dev
```

Trigger location: launch Cursor CLI in the project directory.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Suitable for continuous research, documentation, and coding within the terminal.
2. If the command list has not refreshed, reopen the Cursor CLI session.

**Kiro CLI**

```bash
super-dev
```

Trigger location: launch Kiro CLI in the project directory.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: Yes.

Notes:
1. Kiro CLI now prefers the official steering slash entry; if the current session only accepts natural language, fall back to `super-dev: your requirement`.
2. The official integration surfaces are `.kiro/steering/super-dev.md` + `.kiro/skills/super-dev-core/SKILL.md` + `~/.kiro/steering/super-dev.md` + `~/.kiro/skills/super-dev-core/SKILL.md`.
3. Relaunch Kiro CLI after onboarding so the steering slash entry and skills load in the new session.

**OpenCode**

```bash
super-dev
```

Trigger location: launch OpenCode in the project directory.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Uses CLI slash mode.
2. If you use a global command directory, keep the project-level onboarding files as well.

**Qoder CLI**

```bash
super-dev
```

Trigger location: launch Qoder CLI in the project directory.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Suitable for command-line pipeline development.
2. If slash is not active, confirm that `AGENTS.md` and `.qoder/commands/super-dev.md` exist and that the `.qoder/rules/` directory has been created.
3. The official surfaces now use `AGENTS.md` + `.qoder/rules/super-dev.md` + `.qoder/commands/super-dev.md` + `.qoder/skills/` / `~/.qoder/AGENTS.md` + `~/.qoder/skills/`.

**CodeBuddy CLI**

```bash
super-dev
```

Trigger location: launch CodeBuddy CLI in the project directory.
Trigger command: `/super-dev your requirement`
Competition mode: `/super-dev-seeai your competition brief`
Restart required after onboarding: No.

Notes:
1. Type the command directly in the current CLI session.
2. The primary official surfaces are `CODEBUDDY.md` + `.codebuddy/commands/` + `.codebuddy/skills/`, plus `~/.codebuddy/CODEBUDDY.md`.
3. If the session was opened before onboarding, reload project rules before triggering.
4. For hackathon-style work, prefer `/super-dev-seeai` so the host stays on the 30-minute fast path.

#### IDE Hosts

**Antigravity**

```bash
super-dev
```

Trigger location: open the Agent Chat / Prompt panel in Antigravity with the project workspace active.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: Yes.

Notes:
1. Uses the `GEMINI.md + .agent/workflows + /super-dev` integration model.
2. Onboarding writes project-level `GEMINI.md`, `.gemini/commands/super-dev.md`, and `.agent/workflows/super-dev.md`.
3. Also writes user-level `~/.gemini/GEMINI.md`, `~/.gemini/commands/super-dev.md`, and `~/.gemini/skills/super-dev-core/SKILL.md`.
4. After onboarding, reopen Antigravity or start a new Agent Chat before triggering.

**Cursor IDE**

```bash
super-dev
```

Trigger location: open Agent Chat in Cursor with the target project as the active workspace.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Complete the full pipeline within a single Agent Chat session.
2. If project rules did not load, reopen the workspace or start a new chat.

**Windsurf**

```bash
super-dev
```

Trigger location: open Agent Chat or the Workflow entry in Windsurf within the project context.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Uses IDE slash/workflow integration mode.
2. Best suited for completing research, documents, Spec, and coding within a single Workflow.

**Kiro IDE**

```bash
super-dev
```

Trigger location: open the Agent Chat / AI panel in Kiro IDE within the project context.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: Yes.

Notes:
1. Uses the official steering slash entry first; if the current session only accepts natural language, fall back to `super-dev: your requirement`.
2. Onboarding writes project-level `.kiro/steering/super-dev.md` and `.kiro/skills/super-dev-core/SKILL.md`, plus global `~/.kiro/steering/super-dev.md` and `~/.kiro/skills/super-dev-core/SKILL.md`; legacy `~/.kiro/steering/AGENTS.md` remains as a compatibility surface.
3. If steering or skills are not loaded, reopen the project window or start a new Agent Chat.

**Qoder IDE**

```bash
super-dev
```

Trigger location: open Agent Chat in Qoder IDE within the current project.
Trigger command: `/super-dev your requirement`
Restart required after onboarding: No.

Notes:
1. Uses the official project commands + rules + skills mode; type `/super-dev your requirement` directly in Agent Chat.
2. If the new command does not appear, confirm `AGENTS.md`, `.qoder/commands/super-dev.md`, and `.qoder/rules/super-dev.md` exist, then reopen the project or start a new Agent Chat.
3. The official surfaces now use `AGENTS.md` + `.qoder/rules/super-dev.md` + `.qoder/commands/super-dev.md` + `.qoder/skills/` / `~/.qoder/AGENTS.md` + `~/.qoder/skills/`.

**Trae**

```bash
super-dev
```

Trigger location: open Agent Chat in Trae IDE within the current project context.
Trigger command: `super-dev: your requirement`
Restart required after onboarding: No.

Notes:
1. Uses `super-dev: your requirement` as the primary trigger.
2. Onboarding writes project-level `.trae/project_rules.md`, `.trae/rules.md` and user-level `~/.trae/user_rules.md`, `~/.trae/rules.md`; if a compatible skill directory is detected, it also installs `~/.trae/skills/super-dev-core/SKILL.md`.
3. After onboarding, reopen Trae or start a new Agent Chat to activate rules; if the compatible Skill was installed, it activates as well.
4. Proceed using `output/*` and `.super-dev/changes/*/tasks.md`.

**CodeBuddy IDE**

```bash
super-dev
```

Trigger location: open Agent Chat in CodeBuddy IDE within the project context.
Trigger command: `/super-dev your requirement`
Competition mode: `/super-dev-seeai your competition brief`
Restart required after onboarding: No.

Notes:
1. Use within a project-level Agent Chat; do not leave the project context.
2. Let the host complete research before proceeding to documents and coding.
3. Uses `CODEBUDDY.md` + `.codebuddy/rules/super-dev/RULE.mdc` + `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` integration surfaces.
4. For competition sprints, keep the same Agent Chat alive and avoid unnecessary sub-session switching.

**Copilot (VS Code) / Roo Code / Kilo Code / Cline**

These IDE hosts all use the same pattern: run `super-dev` in the terminal, choose the target host in the installer, then trigger with `super-dev: your requirement` inside the IDE chat panel. No restart is required after onboarding.

```bash
super-dev
```

#### OpenClaw (Native Plugin)

OpenClaw integrates via its native Plugin SDK -- no `super-dev onboard` needed, just install the npm plugin.

**Installation:**
```bash
# Step 1: Install super-dev CLI
pip install super-dev

# Step 2: Install the OpenClaw plugin (pick one)
openclaw plugins install @super-dev/openclaw-plugin  # npm plugin (13 Tools)
clawhub install super-dev                            # ClawHub Skill (instructions only)
```

ClawHub page: https://clawhub.ai/shangyankeji/super-dev

**Trigger:**

In the OpenClaw Agent chat panel, make sure your working directory is the target project, then type:
```text
super-dev: your requirement
```
or
```text
/super-dev your requirement
```

Competition mode:
```text
super-dev-seeai: your competition brief
```
or
```text
/super-dev-seeai your competition brief
```

**13 registered tools:**

| Tool | Purpose |
|------|---------|
| `super_dev_pipeline` | Run the full pipeline |
| `super_dev_init` | Initialize project |
| `super_dev_status` | Check pipeline status |
| `super_dev_quality` | Quality check (by type) |
| `super_dev_spec` | Spec management (propose/list/show/scaffold/validate) |
| `super_dev_config` | Configuration management (list/get/set) |
| `super_dev_review` | Review and gate confirmation (docs/ui/architecture/quality) |
| `super_dev_release` | Release readiness / proof-pack |
| `super_dev_expert` | Expert consultation (10 roles) |
| `super_dev_deploy` | CI/CD config / Dockerfile / release rehearsal |
| `super_dev_analyze` | Project analysis (tech stack/deps/structure) |
| `super_dev_doctor` | Environment diagnostics |
| `super_dev_run` | Generic CLI passthrough (optional) |

**Notes:**
1. The plugin bridges to `super-dev` CLI via subprocess, so `pip install super-dev` is required.
2. Restart the OpenClaw Gateway or start a new session after installing for the plugin and skill to take effect.
3. The plugin ships a built-in SKILL.md so the agent understands the pipeline protocol automatically.
4. For hackathon-style work, prefer `super-dev-seeai:` or `/super-dev-seeai` to stay on the 30-minute competition contract.
5. Run `super-dev doctor --host openclaw` to verify integration status.

---

## Internal / Maintenance Commands

These commands still exist for support, governance, and advanced maintenance. They are not part of the normal end-user path, which stays at `super-dev`, `super-dev update`, `/super-dev`, and `super-dev:`.

```bash
# Pipeline stages
super-dev run research
super-dev run prd
super-dev run architecture
super-dev run uiux
super-dev run frontend
super-dev run backend
super-dev run quality

# Jump to a stage
super-dev jump docs
super-dev jump frontend

# Confirmations
super-dev confirm docs --comment "core docs approved"
super-dev confirm preview --comment "preview approved"

# Resume interrupted pipeline
super-dev run --resume

# Codebase analysis
super-dev repo-map
super-dev dependency-graph
super-dev impact "change description" --files services/auth.py
super-dev regression-guard "change description" --files services/auth.py

# Bugfix
super-dev fix "Fix login 500 error with regression verification"

# Spec management
super-dev spec propose add-billing --title "..." --description "..."
super-dev spec scaffold add-billing
super-dev spec quality add-billing

# Delivery
super-dev release proof-pack
super-dev release readiness

# Review
super-dev review architecture --status revision_requested --comment "Needs redesign"
super-dev review quality --status revision_requested --comment "Gate not met"

# Governance (2.2.0+)
super-dev governance status
super-dev governance rules list
super-dev governance rules validate
super-dev governance knowledge-report
super-dev governance adr generate
super-dev governance adr list
super-dev governance metrics show
super-dev governance metrics export
super-dev governance templates list
super-dev governance templates show <id>
```

---

## Documentation

- [Documentation overview](docs/README.md)
- [Quick start](docs/QUICKSTART.md)
- [Installation options](docs/INSTALL_OPTIONS.md)
- [Host usage guide](docs/HOST_USAGE_GUIDE.md)
- [Host capability audit](docs/HOST_CAPABILITY_AUDIT.md)
- [Host runtime validation matrix](docs/HOST_RUNTIME_VALIDATION.md)
- [Host install surfaces](docs/HOST_INSTALL_SURFACES.md)
- [Workflow guide](docs/WORKFLOW_GUIDE_EN.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)
- [Product audit](docs/PRODUCT_AUDIT.md)

**Execution principles:**

- The host is responsible for "writing code."
- `Super Dev` is responsible for "making the development process correct, complete, and auditable."

---

## License

[MIT](LICENSE)
