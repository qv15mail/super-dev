# @super-dev/openclaw-plugin

Super Dev pipeline governance plugin for [OpenClaw](https://openclaw.ai) -- research-first, commercial-grade AI coding delivery.

## Installation

```bash
# 1. Install super-dev CLI (required)
pip install super-dev

# 2. Install the OpenClaw plugin
openclaw plugins install @super-dev/openclaw-plugin
```

## Usage

In the OpenClaw Agent chat panel, type:

```
super-dev: Build an online education platform with Next.js and Node.js
```

or

```
/super-dev Build an online education platform
```

The agent will activate the Super Dev pipeline and walk through: research -> docs -> spec -> frontend -> backend -> quality -> delivery.

## Registered Tools (13)

| Tool | Purpose |
|------|---------|
| `super_dev_pipeline` | Run the full 9-stage pipeline from requirement description |
| `super_dev_init` | Initialize Super Dev in an existing project (creates super-dev.yaml) |
| `super_dev_status` | Check pipeline status, completed phases, and blocking gates |
| `super_dev_quality` | Run quality check by type: prd, architecture, ui, code, all |
| `super_dev_spec` | Manage specs: list, show, propose, scaffold, validate, archive |
| `super_dev_config` | View or modify project config: list, get, set |
| `super_dev_review` | Run review or confirm a gate: docs, ui, architecture, quality |
| `super_dev_release` | Check release readiness or generate proof-pack |
| `super_dev_expert` | Consult an expert: PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA |
| `super_dev_deploy` | Generate CI/CD config, Dockerfile, or release rehearsal |
| `super_dev_analyze` | Analyze project structure, tech stack, and dependencies |
| `super_dev_doctor` | Run health check and diagnostics for host integration |
| `super_dev_run` | Run any super-dev CLI command directly (optional, fallback) |

## Configuration

In your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "plugins": {
    "entries": {
      "super-dev": {
        "enabled": true,
        "config": {
          "projectDir": "",
          "superDevBin": "super-dev",
          "qualityThreshold": 80,
          "timeout": 300000,
          "language": "zh"
        }
      }
    }
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `projectDir` | `""` (cwd) | Project working directory |
| `superDevBin` | `"super-dev"` | Path to super-dev CLI |
| `qualityThreshold` | `80` | Quality gate threshold (0-100) |
| `timeout` | `300000` | CLI command timeout in ms |
| `language` | `"zh"` | Output language: `zh` or `en` |

## How It Works

```
OpenClaw Agent -> Plugin (TypeScript) -> child_process.execFile -> super-dev (Python CLI)
```

The plugin registers 13 tools that bridge OpenClaw to the `super-dev` Python CLI via subprocess. The built-in SKILL.md (481 lines) teaches the agent the complete pipeline protocol including:
- 9 pipeline stages with per-stage execution guidance
- 2 mandatory confirmation gates (DOC_CONFIRM_GATE + PREVIEW_CONFIRM_GATE)
- UI/architecture/quality rework protocols
- Resume/status/jump flow control
- First-response contract matching Claude Code experience

## Requirements

- Node.js >= 18
- Python >= 3.10
- `super-dev` CLI installed (`pip install super-dev`)
- OpenClaw >= 2026.1.0

## License

MIT
