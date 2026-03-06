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

Current version: `2.0.8`

---

## Project Introduction

`Super Dev` is an AI delivery orchestration tool for commercial-grade execution. It turns host-side model capability into a governed engineering pipeline with clear artifacts, review gates, and delivery standards.

Product role:

- the host handles model execution, browsing, coding, terminal actions, and file edits
- `Super Dev` handles workflow governance, design constraints, quality gates, audit artifacts, and delivery standards

It is built to solve delivery-process problems:

- convert requirements into production artifacts: PRD, architecture, UI/UX, spec, task plans, and delivery manifests
- run development through a standardized pipeline: traceable, resumable, auditable, and reviewable
- enforce quality at every stage: policy governance, red-team checks, quality gates, and release rehearsals
- unify collaboration across CLI and IDE hosts under one delivery standard

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
- The generated UI/UX document now outputs component, form, table, chart, motion, and icon baselines that directly constrain implementation
- Host prompts and skills inherit the same rules so the host produces interfaces closer to modern commercial products
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
super-dev update
```

### 2. PyPI

```bash
pip install -U super-dev
super-dev update
```

After installation, run:

```bash
super-dev
```

By default this opens the host onboarding guide:

- the top panel shows the `Super Dev` install entry
- `↑ / ↓` moves through hosts
- `Space` toggles a host
- `Enter` installs the selected hosts
- `A` selects all
- `C` selects CLI hosts only
- `I` selects IDE hosts only
- `R` clears the selection

After onboarding, the terminal prints the final trigger for each selected host:

- slash hosts: `/super-dev your requirement`
- text-trigger hosts: `super-dev: your requirement`

### 3. Pin a specific version

```bash
pip install super-dev==2.0.8
```

### 4. Install from GitHub tag

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.8
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

## Dependency Installation Behavior

When a user runs:

```bash
pip install -U super-dev
```

or:

```bash
uv tool install super-dev
```

the installer will automatically install the Python dependencies declared in `pyproject.toml`, such as:

- `rich`
- `pyyaml`
- `ddgs`
- `requests`
- `beautifulsoup4`
- `fastapi`
- `uvicorn`

It will not automatically install:

- host applications themselves, such as Claude Code, Codex CLI, Gemini CLI, Cursor, Trae, or Windsurf
- system-level runtimes such as Node.js, npm, pnpm, Docker, or database services
- host login state, browsing permissions, or web access capabilities
- project-specific frontend/backend runtime dependencies outside Super Dev itself

In short:

- `pip` / `uv` automatically install **Super Dev's own Python dependencies**
- they do not install **host tools or system environments**

---

## How The System Works

`Super Dev` runs through a fixed operating path:

1. the user runs `super-dev` inside the project
2. onboarding connects Super Dev to the chosen host
3. the user types `/super-dev requirement` or `super-dev: requirement` inside the host
4. the host enters the Super Dev pipeline
5. the host handles browsing, reasoning, coding, execution, and file edits
6. Super Dev governs the workflow, documents, gates, audit artifacts, and delivery standards

Operating principle:

- the host is responsible for "writing code"
- `Super Dev` is responsible for "making the delivery process correct, complete, and auditable"

### 1. System Overview

This view shows how users, host-side tools, the Super Dev orchestration engine, and final artifacts connect.

![System Overview](docs/assets/architecture/system-overview.png)

### 2. The 12-Phase Pipeline

This view shows the internal execution flow after each host-side trigger.

![The 12-Phase Pipeline](docs/assets/architecture/pipeline-12-phase.png)

### 3. Core Module Topology

This view shows the main source directories under `super_dev` and their dependency boundaries.

![Core Module Topology](docs/assets/architecture/module-topology.png)

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
- When the user types `/super-dev ...` or `super-dev: ...`, the host should switch into Super Dev pipeline mode.
- When documents, spec artifacts, quality reports, or delivery outputs need to be generated or refreshed, the host should call the local `super-dev` CLI.
- If the project contains a `knowledge/` directory, the host must read the relevant local knowledge files before drafting documents.
- If `output/knowledge-cache/*-knowledge-bundle.json` exists, the host must inherit its matched local knowledge, research summary, and scenario constraints into the documents, spec, and implementation.

### IDE Hosts (Antigravity / CodeBuddy / Cursor / Kiro / Qoder / Trae / Windsurf)

1. Run `super-dev` in your project root to finish onboarding.  
2. Open the IDE Agent Chat and trigger according to the real host entry.  
3. IDEs with slash support use `/super-dev your requirement`; non-slash IDEs use `super-dev: your requirement`.
4. Non-slash hosts follow the same research-first pipeline through project rules, AGENTS, or skills.

### Host Trigger Matrix

Certification levels:

- `Certified`: host-specific integration model is aligned with the real host capability and is the recommended production path.
- `Compatible`: the integration path is complete and usable, but still needs more long-running real-world certification.
- `Experimental`: integration exists and can be tried, but it still needs broader production validation.

| Host | Type | Certification | Supports `/super-dev` | Correct Trigger | Restart Required After Onboard |
| --- | --- | --- | --- | --- | --- |
| Antigravity | IDE | Experimental | Yes | Run `/super-dev your requirement` in Antigravity Agent Chat (governed by `GEMINI.md` + `.gemini/commands/` + `.agent/workflows/` + `~/.gemini/skills/`) | Yes |
| Claude Code | CLI | Certified | Yes | Run `/super-dev your requirement` inside the Claude Code session (governed by `.claude/commands/` + `.claude/agents/` / `~/.claude/agents/`) | No |
| CodeBuddy CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the CodeBuddy CLI session (governed by `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` / `~/.codebuddy/agents/` + `~/.codebuddy/skills/`) | No |
| CodeBuddy IDE | IDE | Experimental | Yes | Run `/super-dev your requirement` in Agent Chat (governed by `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` / `~/.codebuddy/agents/` + `~/.codebuddy/skills/`) | No |
| Cursor CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Cursor CLI session | No |
| Cursor IDE | IDE | Experimental | Yes | Run `/super-dev your requirement` in Agent Chat | No |
| Gemini CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Gemini CLI session | No |
| iFlow CLI | CLI | Experimental | Yes | Run `/super-dev your requirement` inside the iFlow CLI session | No |
| Kimi CLI | CLI | Experimental | No | Type `super-dev: your requirement` inside the Kimi CLI session (governed by `.kimi/AGENTS.md`) | No |
| Kiro CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Kiro CLI session | No |
| Kiro IDE | IDE | Experimental | No | Type `super-dev: your requirement` inside Kiro IDE Agent Chat (governed by `.kiro/steering/super-dev.md` + `~/.kiro/steering/AGENTS.md`) | No |
| OpenCode CLI | CLI | Experimental | Yes | Run `/super-dev your requirement` inside the OpenCode CLI session (governed by `.opencode/commands/` + `.opencode/skills/` / `~/.config/opencode/skills/`) | No |
| Qoder CLI | CLI | Compatible | Yes | Run `/super-dev your requirement` inside the Qoder CLI session (governed by `.qoder/commands/` + `.qoder/skills/` / `~/.qoder/skills/`) | No |
| Qoder IDE | IDE | Experimental | Yes | Type `/super-dev your requirement` inside Qoder IDE Agent Chat (governed by `.qoder/commands/super-dev.md` + `.qoder/rules.md` + `.qoder/skills/` / `~/.qoderwork/skills/`) | No |
| Windsurf | IDE | Experimental | Yes | Run `/super-dev your requirement` in Agent Chat (governed by `.windsurf/workflows/` + `.windsurf/skills/` / `~/.codeium/windsurf/skills/`) | No |
| Codex CLI | CLI | Certified | No | Restart Codex, then type `super-dev: your requirement`; `.codex/AGENTS.md` + the compatibility skill will govern execution | Yes |
| Trae | IDE | Compatible | No | Type `super-dev: your requirement` inside Trae Agent Chat (governed by `.trae/project_rules.md` + `~/.trae/user_rules.md`; it also writes `.trae/rules.md` + `~/.trae/rules.md` as compatibility rule surfaces, and `~/.trae/skills/super-dev-core/SKILL.md` adds extra enhancement when available) | Yes |

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
3. Claude Code officially exposes `.claude/agents/` and `~/.claude/agents/`; Super Dev writes a `super-dev-core` subagent there.

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
3. The current integration model is `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/`.


#### 5. Cursor CLI

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

#### 6. Cursor IDE

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

#### 7. Antigravity

Install:
```bash
super-dev onboard --host antigravity --force --yes
```

Where to trigger:
Open Antigravity Agent Chat / Prompt panel and make sure the current workspace is the target project.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: Yes

Notes:
1. Antigravity currently integrates through `GEMINI.md + .agent/workflows + /super-dev`.
2. Onboarding writes project-level `GEMINI.md`, `.gemini/commands/super-dev.md`, and `.agent/workflows/super-dev.md`.
3. It also writes user-level `~/.gemini/GEMINI.md`, `~/.gemini/commands/super-dev.md`, and `~/.gemini/skills/super-dev-core/SKILL.md`.
4. Restart Antigravity or open a fresh Agent Chat before typing `/super-dev your requirement`.

#### 8. Gemini CLI

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

#### 9. iFlow CLI

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

#### 10. Kimi CLI

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

#### 11. Kiro CLI

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

#### 12. Kiro IDE

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
1. Kiro IDE currently uses steering/rules mode with `super-dev: your requirement`.
2. Onboarding writes project-level `.kiro/steering/super-dev.md` and also installs the official global steering file at `~/.kiro/steering/AGENTS.md`.
3. If steering or rules did not load, reopen the project window.

#### 13. OpenCode

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

#### 14. Qoder CLI

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

#### 15. Qoder IDE

Install:
```bash
super-dev onboard --host qoder --force --yes
```

Where to trigger:
Open Qoder IDE Agent Chat in the current project and trigger there.

Trigger command:
```text
/super-dev your requirement
```

Restart required after onboard: No

Notes:
1. Qoder IDE now uses project-level commands + rules, so trigger `/super-dev your requirement` in Agent Chat.
2. If the command does not appear, verify that `.qoder/commands/super-dev.md` exists, then reopen the project or start a fresh chat.

#### 16. Windsurf

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

#### 17. Codex CLI

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
1. Codex CLI currently uses `super-dev: your requirement` as the primary trigger.
2. Execution relies on `.codex/AGENTS.md` plus the official user-level skill at `~/.codex/skills/super-dev-core/SKILL.md`.
3. If the old session did not reload the Skill, restart `codex` and retry.

#### 18. Trae

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

Restart required after onboard: Yes

Notes:
1. Trae currently uses `super-dev: your requirement` as the primary trigger.
2. Onboarding always writes project-level `.trae/project_rules.md` + `.trae/rules.md` and user-level `~/.trae/user_rules.md` + `~/.trae/rules.md`; if a compatible host skill directory is detected, it also enhances `~/.trae/skills/super-dev-core/SKILL.md`.
3. After onboarding, restart Trae or at least open a fresh Agent Chat so the rule file loads; if the compatibility skill exists it will load together.
4. Then continue delivery from `output/*` and `.super-dev/changes/*/tasks.md`.

