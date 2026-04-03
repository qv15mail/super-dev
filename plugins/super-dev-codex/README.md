# Super Dev Codex Plugin

This is an optional local Codex plugin scaffold for repositories that want a richer Codex App/Desktop surface than `AGENTS.md + Skills` alone.

It does not replace the official Super Dev Codex integration surfaces:

- `AGENTS.md`
- `.agents/skills/super-dev/SKILL.md`
- `CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`)
- `~/.agents/skills/super-dev/SKILL.md`

Use this plugin scaffold as an advanced Codex App/Desktop enhancement when you want the repository to expose a repo-local plugin entry in addition to the official AGENTS/Skills model.

Plugin root:

- `.codex-plugin/plugin.json`
- `skills/super-dev/SKILL.md`
- `skills/super-dev-core/SKILL.md`

Marketplace entry:

- `.agents/plugins/marketplace.json`

The plugin skill should behave exactly like the main Codex Super Dev workflow:

- App/Desktop slash list entry: `super-dev`
- CLI explicit skill mention: `$super-dev`
- AGENTS fallback: `super-dev: <需求描述>`
