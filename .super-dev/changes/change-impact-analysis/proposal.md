# Proposal

## Why

After `repo-map`, the next missing capability is understanding what a proposed change will affect before implementation starts. This is especially important for bugfixes, refactors, API updates, and UI changes.

## What

Add a formal `super-dev impact` feature that:

1. Accepts a change description and/or changed files
2. Analyzes likely affected modules, entry points, integration surfaces, and regression scope
3. Writes `output/*-impact-analysis.md` and `output/*-impact-analysis.json`
4. Exposes the same result via Web API

## Success Criteria

1. Developers can run one command and get a practical impact report
2. The report helps decide where to change code and what to re-test
3. The output is usable by both humans and hosts
