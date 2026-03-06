# Host Skill-First Integration Design

## Decision

Super Dev adopts a host skill-first integration model.

- Python CLI remains the governance kernel.
- Host-level `super-dev-core` Skill becomes the primary protocol contract for supported hosts.
- Project-level files remain mandatory context injectors:
  - rules
  - AGENTS
  - commands / slash mappings
  - steering
- Host trigger syntax stays host-native:
  - `/super-dev ...` for hosts with command/slash support
  - `super-dev: ...` for text-trigger hosts

## Responsibilities

### Python CLI

Owns:
- install / onboard / doctor / detect / update
- review state, quality gates, release readiness
- writing host integration artifacts
- writing project pipeline artifacts

### Host Skill

Owns:
- teaching the host what Super Dev is
- defining first-response contract
- enforcing research-first pipeline semantics
- mapping user trigger into the Super Dev workflow

### Project-Level Integration Files

Own:
- binding the host to the current repository
- exposing project-specific rules, paths, knowledge bundle usage, and delivery gates

## Installation Model

Every supported host should be modeled as:

1. host-level installation
- install `super-dev-core` into the host's official skills directory when supported

2. project-level installation
- install the host's repository-local rules / AGENTS / commands / steering files

This gives two stable layers:
- host understands the Super Dev protocol globally
- project injects the current repository's constraints locally

## Trigger Model

### Slash hosts

User enters `/super-dev ...`.

- slash/command file is the host-native trigger
- host-level skill provides semantic understanding of the Super Dev workflow
- project-level rules provide repository context

### Non-slash hosts

User enters `super-dev: ...`.

- text trigger enters the same workflow
- host-level skill and project-level rules/AGENTS interpret the trigger

## Consequences

- doctor/detect must check host-level skill directories, not just project-local skill folders
- onboard must write both host-level skill and project-level integration files
- docs must distinguish:
  - trigger syntax
  - host-level skill path
  - project-level integration files
