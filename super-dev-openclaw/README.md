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

The agent will activate the Super Dev pipeline and walk through: research -> PRD -> architecture -> UIUX -> spec -> frontend -> backend -> quality -> delivery.

## Registered Tools

| Tool | Purpose |
|------|---------|
| `super_dev_pipeline` | Run the full 9-stage pipeline |
| `super_dev_init` | Initialize Super Dev in an existing project |
| `super_dev_status` | Check pipeline status and outputs |
| `super_dev_quality` | Run quality gate check (0-100 score) |
| `super_dev_spec` | Manage specs: list, show, propose, scaffold, validate |
| `super_dev_config` | View or modify project config (super-dev.yaml) |
| `super_dev_review` | Run targeted review: docs, ui, architecture, quality |
| `super_dev_release` | Check release readiness or generate proof-pack |
| `super_dev_expert` | Consult an expert: PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA |
| `super_dev_run` | Run any super-dev CLI command directly |

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

The plugin registers 10 tools that bridge OpenClaw to the `super-dev` Python CLI via subprocess. The built-in SKILL.md teaches the agent the pipeline protocol (phase chain, confirmation gates, knowledge contracts).

## Requirements

- Node.js >= 18
- Python >= 3.10
- `super-dev` CLI installed (`pip install super-dev`)
- OpenClaw >= 2026.1.0

## License

MIT
