# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New delivery packager: `output/delivery/*` now includes manifest, report, and versioned zip bundle.
- New release gate script: `scripts/check_delivery_ready.py` (supports manifest check and `--smoke` end-to-end verification).
- Knowledge augmenter now has dual web-search path (DDGS primary + DuckDuckGo Instant API fallback).

### Changed

- Stabilized release workflow around `scripts/preflight.sh` and release runbook.
- Pipeline Stage 11 now performs both database migration generation and delivery packaging.
- Preflight/release/publish scripts now enforce delivery gate smoke before packaging/release.
- Repository CI/CD workflows rebuilt for production use (quality gate, security scan, package checks, tag-based release pipeline).
- Cross-platform integration/skill acceptance coverage expanded to all supported CLI/IDE targets in automated tests.
- Added dedicated CI `Platform Compatibility` job for multi-target integration visibility.
- Tag-based CD publishing now hard-fails when `PYPI_API_TOKEN` is missing (no silent skip).

## [2.0.0] - 2026-03-01

### Added

- New release preflight script: `scripts/preflight.sh`.
- New release operations document: `docs/RELEASE_RUNBOOK.md`.
- Deployment remediation export templates and checklist generation in pipeline.

### Changed

- Unified product version to `2.0.0` across package metadata, runtime metadata, API version, docs, and examples.
- Rewritten `README.md` and `README_EN.md` to match current real capabilities.
- Rewritten publishing/install/quickstart docs to align with current CLI behavior.
- Pipeline documentation aligned to actual Stage `0`~`11` execution.

### Fixed

- End-to-end static quality cleanup: Ruff and mypy full-pass baseline.
- Runtime workflow quality-score compatibility for `WorkflowContext.config` variants.
- API run-state sanitization and type-stable serialization.
- Multiple quality gate and orchestration edge cases in production flow.

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
