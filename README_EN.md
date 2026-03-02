# Super Dev

<div align="center">

# God-Tier AI Development Team

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success)](.github/workflows/ci.yml)

English | [简体中文](README.md)

</div>

---

## Version

Current version: `2.0.0`

Current quality baseline (2026-03-01):

- `ruff check super_dev tests` passed
- `mypy super_dev` passed (55 source files)
- `pytest -q` passed (199 passed)
- `bandit -ll -r super_dev` passed (0 medium/high findings)
- `pip-audit .` passed (0 vulnerabilities)

---

## What Super Dev Does

`Super Dev` is an orchestration-first AI engineering tool for commercial-grade delivery. Starting from one requirement sentence, it generates production-ready project assets:

- requirement intelligence and enrichment
- PRD / architecture / UIUX / execution docs
- frontend demo scaffold + implementation scaffold
- red-team review + quality gate
- code review guide + AI prompts
- CI/CD + deploy remediation templates + DB migrations + delivery package (manifest/report/zip)

---

## Core Capabilities

### 1) 12-stage pipeline (Stage 0 to Stage 11)

`super-dev pipeline` currently executes:

| Stage | Description |
|:---|:---|
| Stage 0 | Requirement enrichment (local knowledge + optional web search) |
| Stage 1 | Professional docs generation |
| Stage 2 | Frontend demo scaffold generation |
| Stage 3 | Spec creation |
| Stage 4 | Frontend/backend implementation scaffold (optional) |
| Stage 5 | Red-team review (optional) |
| Stage 6 | Quality gate (optional threshold override) |
| Stage 7 | Code review guide |
| Stage 8 | AI prompt generation |
| Stage 9 | CI/CD config generation |
| Stage 10 | Deploy remediation templates |
| Stage 11 | Database migration scripts + delivery package |

### 2) Spec-Driven Development (SDD)

Built-in `.super-dev/specs`, `changes`, and `archive` workflow for proposal-driven development.

### 3) Expert Collaboration

PM / ARCHITECT / UI / UX / SECURITY / CODE / DBA / QA / DEVOPS / RCA expert roles are integrated.

### 4) Design Intelligence Engine

Supports design search, design system generation, tokens, landing patterns, chart recommendations, UX guidance, stack best practices, and code snippets.

### 5) Web API / Studio

FastAPI backend + Studio mode for workflow execution, status polling, config access, and deployment template export.

### 6) Cross-platform compatibility gate

CI includes a dedicated `Platform Compatibility` job that verifies Skill and integration paths for Claude Code / Codex CLI / OpenCode / Antigravity / Cursor / Qoder / Trae / CodeBuddy.

---

## Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install -U super-dev
super-dev --version
```

PyPI page:

- https://pypi.org/project/super-dev/

### Option 2: Install a pinned version (repro/rollback)

```bash
pip install super-dev==2.0.0
super-dev --version
```

### Option 3: Install from GitHub tag

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.0
super-dev --version
```

### Option 4: Developer install from source

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
super-dev --version
```

---

## Quick Start

### Mode A: Direct requirement mode (recommended)

```bash
super-dev "Build an ecommerce admin with auth, orders, and payments"
```

This command automatically routes to the full pipeline (requirement enrichment -> docs -> spec -> scaffold -> red-team -> quality gate -> CI/CD -> migration and delivery package).

### Mode B: Explicit pipeline (advanced)

```bash
super-dev pipeline "Build an ecommerce admin with auth, orders, and payments" --platform web --frontend react --backend python --domain ecommerce --cicd github
```

### Common commands

```bash
super-dev init my-project
super-dev analyze .
super-dev create "User authentication system"
super-dev "User authentication system"
super-dev spec init
super-dev spec list
super-dev quality --type all
super-dev deploy --cicd github
super-dev studio --port 8765
```

---

## Preflight and Release

Run this before release:

```bash
./scripts/preflight.sh
```

Preflight includes `ruff`, `mypy`, `pytest`, `delivery-smoke`, `bandit`, `pip-audit`, benchmark, build, and `twine check`.

Related docs:

- [Publishing Guide](docs/PUBLISHING.md)
- [Release Runbook](docs/RELEASE_RUNBOOK.md)
- [Quickstart](docs/QUICKSTART.md)

---

## Key Project Structure

```text
super_dev/                 # Core source code
output/                    # Generated artifacts
scripts/                   # Preflight / release scripts
docs/                      # Product and release docs
```

---

## License

MIT License
