# Super Dev 宿主能力审计（2.3.1）

这份文档记录当前宿主矩阵的能力依据，只回答四件事：

1. 宿主官方公开了什么能力
2. Super Dev 当前采用哪种接入模型
3. 用户在宿主里应该输入什么
4. 当前结论属于什么级别

## 审计结论

| 宿主 | 当前接入模型 | 用户触发方式 | 官方依据 | 当前结论 |
| --- | --- | --- | --- | --- |
| Antigravity | native slash + GEMINI.md/workflow + official skills | `/super-dev 你的需求` | [Antigravity documentation](https://antigravity.im/documentation) | 当前按 `GEMINI.md + .gemini/commands + .agent/workflows + ~/.gemini/skills` 接入，本机安装面已验证，仍需更多公开定制文档支撑 |
| Claude Code | native slash + official `CLAUDE.md` + official skills + optional repo plugin enhancement | `/super-dev 你的需求` | [Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) / [Claude Code memory](https://docs.anthropic.com/en/docs/claude-code/settings#claude-md-memory) / [Claude Code hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) | 当前按项目根 `CLAUDE.md` + `.claude/skills/` + `~/.claude/skills/` 收敛，`.claude/commands/` 与 `.claude/agents/` 作为兼容增强面保留，repo plugin enhancement 作为可选增强层 |
| Cline | official rules + official skills + AGENTS compatibility | `super-dev: 你的需求` | [Cline documentation](https://docs.cline.bot/) | 当前按 `.clinerules/super-dev.md` + `.cline/skills/` / `~/.cline/skills/` 建模，`AGENTS.md` 作为兼容增强面保留 |
| CodeBuddy CLI | native slash + official skills | `/super-dev 你的需求` | [CodeBuddy CLI slash commands](https://www.codebuddy.ai/docs/cli/slash-commands) / [CodeBuddy skills](https://www.codebuddy.ai/docs/cli/skills) | slash 触发 + `.codebuddy/skills` / `~/.codebuddy/skills` 已公开 |
| CodeBuddy IDE | native slash + official commands/subagents/skills | `/super-dev 你的需求` | [CodeBuddy IDE integrations](https://www.codebuddy.ai/docs/cli/ide-integrations) / [CodeBuddy Subagents](https://www.codebuddy.ai/docs/ide/Features/Subagents) / [CodeBuddy skills](https://www.codebuddy.ai/docs/cli/skills) | IDE 命令映射可用，`.codebuddy/agents/` 与 `.codebuddy/skills/` 已公开 |
| Cursor CLI | native slash + AGENTS compatibility | `/super-dev 你的需求` | [Cursor CLI slash commands](https://docs.cursor.com/en/cli/reference/slash-commands) / [Cursor CLI using](https://docs.cursor.com/en/cli/using) | slash 模式成立，官方文档确认 `.cursor/rules/` 之外还会读取项目根 `AGENTS.md` / `CLAUDE.md` |
| Cursor IDE | native slash + AGENTS compatibility | `/super-dev 你的需求` | [Cursor Agent commands](https://docs.cursor.com/en/agent/chat/commands) / [Cursor rules](https://docs.cursor.com/en/context/rules) | Agent Chat 命令模式可用，官方 rules 面与 `AGENTS.md` compatibility 已补进仓库模型 |
| Gemini CLI | native slash + official commands/GEMINI.md | `/super-dev 你的需求` | [Gemini CLI docs](https://google-gemini.github.io/gemini-cli/docs/) / [Gemini commands](https://google-gemini.github.io/gemini-cli/docs/cli/commands.html) | 维持 slash 模式，项目级 `GEMINI.md` + `.gemini/commands/super-dev.md` 与用户级 `~/.gemini/commands/` 已纳入正式接入面 |
| Kiro CLI | steering-first + official skills | `super-dev: 你的需求` | [Kiro CLI](https://kiro.dev/docs/cli/) / [Kiro skills](https://kiro.dev/docs/cli/skills/) / [Kiro steering](https://kiro.dev/docs/steering/) | CLI 不再按 slash 建模，改为 `.kiro/steering/` + `.kiro/skills/` + `~/.kiro/skills/` |
| Kiro IDE | steering-first + official global skills | `super-dev: 你的需求` | [Kiro steering](https://kiro.dev/docs/steering/) / [Kiro skills](https://kiro.dev/docs/cli/skills/) | 不再按 slash 建模，改为 project steering + project/global skills + `~/.kiro/steering/AGENTS.md` |
| Kilo Code | official rules + compatibility skill | `super-dev: 你的需求` | [Kilo Code rules](https://kilocode.ai/docs/features/rules) | 规则面已收敛到 `.kilocode/rules/super-dev.md`，若检测到 `~/.kilocode/skills/` 则作为兼容增强路径协同生效 |
| OpenCode | native slash + official skills | `/super-dev 你的需求` | [OpenCode commands](https://opencode.ai/docs/commands/) / [OpenCode skills](https://opencode.ai/docs/skills/) | slash/commands 模式成立，skills 面已公开 |
| Qoder CLI | native slash + official rules/skills | `/super-dev 你的需求` | [Qoder CLI](https://docs.qoder.com/cli/using-cli) / [Qoder rules](https://docs.qoder.com/zh/user-guide/rules) / [Qoder CLI skills](https://docs.qoder.com/cli/skills) | CLI 模式可用，已改到 `.qoder/rules/` + `.qoder/commands/` + `.qoder/skills/` |
| Qoder IDE | native slash + official rules/skills | `/super-dev 你的需求` | [Qoder rules](https://docs.qoder.com/zh/user-guide/rules) / [Qoder commands](https://docs.qoder.com/user-guide/commands) / [Qoder skills](https://docs.qoder.com/user-guide/skills) | 项目级 `.qoder/commands/super-dev.md` + `.qoder/rules/super-dev.md` + `.qoder/skills/` 协同生效，`AGENTS.md` 作为官方兼容面 |
| Roo Code | native slash + official commands/rules | `/super-dev 你的需求` | [Roo Code slash commands](https://docs.roocode.com/features/slash-commands) / [Roo Code custom instructions](https://docs.roocode.com/features/custom-instructions) / [Roo Code custom modes](https://docs.roocode.com/features/custom-modes) | slash 与 `.roo/commands/`、`.roo/rules/` 都已按官方面建模，当前不再虚报未实际安装的 modes |
| VS Code Copilot | context/rules-first + text trigger | `super-dev: 你的需求` | [Copilot custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions) | 当前按 `.github/copilot-instructions.md + AGENTS.md` 建模，兼容 Copilot Chat |
| Windsurf | native slash / workflow + official rules/skills | `/super-dev 你的需求` | [Windsurf workflows](https://docs.windsurf.com/plugins/cascade/workflows) / [Windsurf skills](https://docs.windsurf.com/windsurf/cascade/memories#custom-skills) | workflow 命令模式成立，`.windsurf/rules/`、`.windsurf/workflows/` 与 skills 面已纳入正式接入面 |
| Codex CLI | official AGENTS.md + official skills | `super-dev: 你的需求` / `$super-dev` | [Codex CLI](https://developers.openai.com/codex/cli) / [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md) / [Codex Skills](https://developers.openai.com/codex/skills) / [Codex app commands](https://developers.openai.com/codex/app/commands) | 不支持项目级自定义 slash；当前收敛为项目 `AGENTS.md` + 全局 `CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`）+ 官方 skills。桌面端若在 `/` 列表里看到 `super-dev`，那是启用 Skill 的入口 |
| Trae | official project/user rules + compatibility rules/skill | `super-dev: 你的需求` | [Trae rules](https://docs.trae.ai/docs/what-is-trae-rules) | 公开文档确认 project rules 与 user rules；本机 `rules.md` 规则面与 `~/.trae/skills` 作为兼容增强路径协同生效 |

## 当前产品规则

1. 支持原生 slash 的宿主：
   - 直接输入 `/super-dev 你的需求`
2. 不支持 slash 的宿主：
   - 直接输入 `super-dev: 你的需求`
3. Antigravity 当前按 `GEMINI.md + .agent/workflows + ~/.gemini/skills` 收敛到 slash 模式；项目级 workflow 与 Gemini 全局上下文会一起生效。
4. CodeBuddy、Qoder、Windsurf、OpenCode 这些宿主，官方文档已经公开 skills 面；Super Dev 现在按“命令触发 + Skills 协议”建模。
5. Codex CLI 当前按 official AGENTS.md + official skills 协同，用户不需要手动激活 Skill。
6. Trae 当前收敛到 official project/user rules + compatibility skill；Cline 已补齐 project/user skills；Kiro IDE 仍走 steering/rules；Qoder IDE 已收正为 commands + rules + official skills。
7. 接入完成后可用 `super-dev integrate smoke --target <host_id>` 做标准化验收。

## 后续审计顺序

下一批继续做运行级收紧：

1. Claude Code
2. Codex CLI
3. Cursor / Cursor CLI
4. Qoder / Qoder CLI
5. VS Code Copilot / Trae

目标不是继续堆“支持列表”，而是把每个宿主都压到明确的真实入口模型：

- slash
- rules-first
- AGENTS + Skill
- workflow command

## 系统级适配执行规约（2.1.1）

为确保“不同宿主下体验一致”，当前仓库改为三层校验：

1. 声明层（Declared）
   - 每个宿主维护多条官方依据，而不是单 URL。
   - 通过 `super-dev integrate matrix --json` 可看到 `official_docs_references` 与 `capability_labels`。
2. 在线层（Live Verify）
   - 通过 `super-dev integrate matrix --verify-docs` 或 `super-dev integrate audit --verify-docs`，对每个官方链接做在线可达性核验。
   - 输出 `docs_checks`，包含 `status/checked/reachable/unreachable`。
   - 通过 `--official-compare` 逐宿主抓取官方文档内容并对照 `slash/rules/skills` 声明，输出 `official_compares`。
3. 运行层（Runtime）
   - 继续使用 `super-dev integrate smoke --target <host_id>` 与 `super-dev integrate validate --target <host_id> --status passed` 完成真人验收闭环。

4. 深适配层（System Harden）
   - 使用 `super-dev integrate harden --target <host_id> --official-compare` 对单宿主执行系统级深适配（规则文件、slash、全局协议、skill、契约审计、官方文档对照）。
   - 使用 `super-dev integrate harden --all --official-compare` 对所有已支持宿主逐一执行深适配，并输出 `output/*-host-hardening.{json,md}`。
   - 深适配报告同时输出 `host_parity_summary`，用于校验各宿主在触发格式、Smoke 语句、协议模式与能力标签上的一致体验。
   - 深适配报告同时输出 `host_gate_summary`，用于校验各宿主在 docs_confirm_gate 与 preview_confirm_gate 上的一致门禁行为。
   - 深适配报告同时输出 `host_runtime_script_summary`，用于校验各宿主在真人验收脚本（trigger + smoke prompt/signal + smoke steps）上的一致性。
   - 深适配报告同时输出 `host_recovery_summary`，用于校验各宿主在恢复命令模板（setup/skill/audit/onboard）上的一致性。
   - 深适配与审计同时输出 `host_parity_index`，并通过 `--parity-threshold` 执行总分门禁（默认 95.0，低于阈值即返回失败码）。
   - 深适配额外输出一页可读报告 `output/*-host-parity-onepage.md`，用于快速查看每个宿主的 PASS/FAIL、失败维度与下一条修复命令。

统一目标：

- 触发一致：支持 slash 的宿主统一 `/super-dev 需求`；不支持 slash 的宿主统一 `super-dev: 需求`。
- 协议一致：所有宿主都遵循 research → 三文档确认 → spec → 前端预览确认 → 后续交付。
- 能力一致：通过 `capability_labels` 统一表达 `slash/rules/skills/trigger`，避免宿主间语义漂移。
