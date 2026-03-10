# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.9] - 2026-03-11

### Added

- Added explicit `bootstrap` flow that generates `.super-dev/WORKFLOW.md` and `output/*-bootstrap.md`.
- Added `integrate validate` runtime-validation state recording for host真人验收。
- Added `release proof-pack` to aggregate delivery evidence into a single report.

### Changed

- Unified the active project version to `2.0.9` across package metadata, runtime metadata, docs, examples, release scripts, tests, and website copy.
- Strengthened host contracts so non-slash hosts must also落盘 research / PRD / architecture / UIUX artifacts instead of only describing the workflow in chat.
- Improved website structure and docs center, including bilingual routes and a simplified documentation layout.

### Fixed

- Fixed analyzer scope so `.venv`, `site-packages`, and similar dependency directories are excluded from project analysis.
- Fixed bugfix-mode regression by restoring lightweight patch workflow, clarification prompts, and default sequence diagrams.
- Fixed proof-pack visibility by surfacing progress, blockers, and key artifacts in the Web management UI.

## [2.0.8] - 2026-03-07

### Added

- Added architecture image assets for README and synchronized the Chinese and English overview sections to use image-first diagrams.
- Added project-tracked Codex skill directory content under `.codex/skills/super-dev-core/`.
- Added lockfiles for the example frontend/backend workspaces to keep dependency snapshots reproducible.

### Changed

- Unified the active project version to `2.0.8` across package metadata, runtime metadata, docs, examples, release scripts, and tests.
- Refined repository tracking boundaries so project integration assets are versioned while local runtime artifacts remain ignored.
- Updated README and README_EN with clearer dependency-install behavior, system workflow explanation, and architecture visuals.

### Fixed

- Fixed repository completeness gaps around tracked host integration assets and release documentation consistency.

## [2.0.2] - 2026-03-05

### Added

- `super-dev install` command added for PyPI users (host installation wizard in CLI).
- `super-dev` without arguments now enters installer guide by default.
- Interactive installer (`install.sh`) upgraded with multi-select host onboarding.
- Policy presets (`default` / `balanced` / `enterprise`) with stronger governance controls.
- Required-host readiness gate (`enforce_required_hosts_ready` + `min_required_host_score`).
- Pipeline contract artifacts (`*-pipeline-contract.json/md`) integrated into delivery flow.

### Changed

- Unified product version to `2.0.2` across package metadata, runtime metadata, generated artifacts, and docs.
- Rewritten `README.md` with updated onboarding, installation, host-governance, and usage flows.
- Updated workflow/install docs for new default behavior (`super-dev` -> installer guide).
- Host support matrix consistency checks added (catalog/integration/skill alignment).

### Fixed

- Fixed command routing edge case where `policy` could be misinterpreted as direct requirement input.
- Improved type stability and strict coercion in host-compatibility quality gate paths.
- Reduced red-team false positives by ignoring vulnerability patterns in test fixture files.
- Added stronger regression coverage for installer, policy, host profile, and contract reporting.

### Security

- Replaced XML parsing with `defusedxml` in quality gate.
- Added URL scheme guards for outbound HTTP utility calls.
- Tightened subprocess and git-source handling in skill installation flow.
- Security baseline validated with `bandit` and `pip-audit` (no findings at release time).

## [1.0.1] - 2025-01-04

### Added

- Workflow and design generation improvements.
- Documentation and installation guides expansion.

## [1.0.0] - 2025-01-03

### Added

- Initial public release with CLI pipeline, expert system, and SDD foundations.
