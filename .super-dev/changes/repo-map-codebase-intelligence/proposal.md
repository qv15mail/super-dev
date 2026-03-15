# Proposal

## Why

Super Dev currently understands process better than codebase context. For ongoing development, bugfixing, and takeover work, the host needs an explicit repository map before implementation.

## What

Add a formal Repo Map / Codebase Intelligence capability that:

1. Generates `output/*-repo-map.md` and `output/*-repo-map.json`
2. Summarizes entry points, module boundaries, integration surfaces, dependencies, and risk points
3. Exposes a direct CLI command (`super-dev repo-map`)
4. Includes Repo Map in the delivery evidence set when available

## Success Criteria

1. Users can generate a repo map with one command
2. The report is useful for both humans and hosts
3. Proof Pack includes repo map evidence when generated
4. Tests cover markdown/json outputs and CLI behavior
