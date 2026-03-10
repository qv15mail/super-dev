# Super Dev 宿主能力审计（2.0.9）

这份文档记录当前宿主矩阵的能力依据，只回答四件事：

1. 宿主官方公开了什么能力
2. Super Dev 当前采用哪种接入模型
3. 用户在宿主里应该输入什么
4. 当前结论属于什么级别

## 审计结论

| 宿主 | 当前接入模型 | 用户触发方式 | 官方依据 | 当前结论 |
| --- | --- | --- | --- | --- |
| Antigravity | native slash + GEMINI.md/workflow + official skills | `/super-dev 你的需求` | [Antigravity documentation](https://antigravity.im/documentation) | 当前按 `GEMINI.md + .gemini/commands + .agent/workflows + ~/.gemini/skills` 接入，本机安装面已验证，仍需更多公开定制文档支撑 |
| Claude Code | native slash + official subagents | `/super-dev 你的需求` | [Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) / [Claude Code subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) | slash 模式成立，`.claude/agents/` 与 `~/.claude/agents/` 已公开 |
| CodeBuddy CLI | native slash + official skills | `/super-dev 你的需求` | [CodeBuddy CLI slash commands](https://www.codebuddy.ai/docs/cli/slash-commands) / [CodeBuddy skills](https://www.codebuddy.ai/docs/cli/skills) | slash 触发 + `.codebuddy/skills` / `~/.codebuddy/skills` 已公开 |
| CodeBuddy IDE | native slash + official commands/subagents/skills | `/super-dev 你的需求` | [CodeBuddy IDE integrations](https://www.codebuddy.ai/docs/cli/ide-integrations) / [CodeBuddy Subagents](https://www.codebuddy.ai/docs/ide/Features/Subagents) / [CodeBuddy skills](https://www.codebuddy.ai/docs/cli/skills) | IDE 命令映射可用，`.codebuddy/agents/` 与 `.codebuddy/skills/` 已公开 |
| Cursor CLI | native slash | `/super-dev 你的需求` | [Cursor CLI slash commands](https://docs.cursor.com/en/cli/reference/slash-commands) | slash 模式成立 |
| Cursor IDE | native slash | `/super-dev 你的需求` | [Cursor Agent commands](https://docs.cursor.com/en/agent/chat/commands) | Agent Chat 命令模式可用，持续验证中 |
| Gemini CLI | native slash + official commands/GEMINI.md | `/super-dev 你的需求` | [Gemini CLI docs](https://google-gemini.github.io/gemini-cli/docs/) | 维持 slash 模式，项目级 `GEMINI.md` + `.gemini/commands/super-dev.md` 为官方接入面，宿主级 skill 仍按兼容增强处理 |
| iFlow CLI | native slash + official skills | `/super-dev 你的需求` | [iFlow slash commands](https://platform.iflow.cn/en/cli/examples/slash-commands) / [iFlow skills](https://platform.iflow.cn/en/cli/examples/skill) | slash 模式成立，skills 面已公开；宿主鉴权仍需用户在 iFlow 内完成 |
| Kimi CLI | official AGENTS.md + text trigger | `super-dev: 你的需求` | [Kimi CLI interaction](https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html) / [Kimi CLI agents](https://www.kimi.com/code/docs/en/kimi-cli/guides/agents.html) | 当前更适合 `/init` 生成 AGENTS.md + 文本触发，不再按自定义 slash 建模 |
| Kiro CLI | native slash + official commands/AGENTS.md | `/super-dev 你的需求` | [Kiro CLI](https://kiro.dev/docs/cli/) | CLI 模式可用，项目级 `.kiro/AGENTS.md` + `.kiro/commands/super-dev.md` 为正式接入面 |
| Kiro IDE | rules-first + official global steering | `super-dev: 你的需求` | [Kiro steering](https://kiro.dev/docs/steering/) | 不再按 slash 建模，改为 project steering + `~/.kiro/steering/AGENTS.md` |
| OpenCode | native slash + official skills | `/super-dev 你的需求` | [OpenCode commands](https://opencode.ai/docs/commands/) / [OpenCode skills](https://opencode.ai/docs/agents/skills/) | slash/commands 模式成立，skills 面已公开 |
| Qoder CLI | native slash + official skills | `/super-dev 你的需求` | [Qoder CLI](https://docs.qoder.com/cli/using-cli) / [Qoder CLI skills](https://docs.qoder.com/cli/skills) | CLI 模式可用，skills 面已公开 |
| Qoder IDE | native slash + rules + official skills | `/super-dev 你的需求` | [Qoder commands](https://docs.qoder.com/user-guide/commands) / [Qoder skills](https://docs.qoder.com/user-guide/skills) | 项目级 `.qoder/commands/super-dev.md` + `.qoder/rules.md` + `.qoder/skills/` 协同生效 |
| Windsurf | native slash / workflow + official skills | `/super-dev 你的需求` | [Windsurf workflows](https://docs.windsurf.com/plugins/cascade/workflows) / [Windsurf skills](https://docs.windsurf.com/windsurf/cascade/memories#custom-skills) | workflow 命令模式成立，skills 面已公开 |
| Codex CLI | official AGENTS.md + text trigger | `super-dev: 你的需求` | [OpenAI Codex docs](https://platform.openai.com/docs/codex) | 不支持自定义 slash，当前维持 official AGENTS.md + official skills |
| Trae | official project/user rules + compatibility rules/skill | `super-dev: 你的需求` | [Trae rules](https://www.traeide.com/docs/what-is-trae-rules) | 公开文档确认 project rules 与 user rules；本机 `rules.md` 规则面与 `~/.trae/skills` 作为兼容增强路径协同生效 |

## 当前产品规则

1. 支持原生 slash 的宿主：
   - 直接输入 `/super-dev 你的需求`
2. 不支持 slash 的宿主：
   - 直接输入 `super-dev: 你的需求`
3. Antigravity 当前按 `GEMINI.md + .agent/workflows + ~/.gemini/skills` 收敛到 slash 模式；项目级 workflow 与 Gemini 全局上下文会一起生效。
4. CodeBuddy、Qoder、Windsurf、OpenCode、iFlow 这些宿主，官方文档已经公开 skills 面；Super Dev 现在按“命令触发 + Skills 协议”建模。
5. Codex CLI 当前按 official AGENTS.md + official skills 协同，用户不需要手动激活 Skill。
6. Kimi CLI 当前按 official AGENTS.md + text trigger / 文本触发建模，不再继续假设项目级自定义 slash。
7. Trae 当前收敛到 official project/user rules + compatibility skill；Kiro IDE 仍走 steering/rules；Qoder IDE 已收正为 commands + rules + official skills。
8. 接入完成后可用 `super-dev integrate smoke --target <host_id>` 做标准化验收。

## 后续审计顺序

下一批继续做运行级收紧：

1. Cursor IDE
2. Gemini CLI
3. Claude Code
4. Kiro IDE
5. Trae

目标不是继续堆“支持列表”，而是把每个宿主都压到明确的真实入口模型：

- slash
- rules-first
- AGENTS + Skill
- workflow command
