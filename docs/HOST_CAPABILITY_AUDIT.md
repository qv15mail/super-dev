# Super Dev 宿主能力审计（2.0.6）

这份文档记录当前宿主矩阵的能力依据，只回答四件事：

1. 宿主官方公开了什么能力
2. Super Dev 当前采用哪种接入模型
3. 用户在宿主里应该输入什么
4. 当前结论属于什么级别

## 审计结论

| 宿主 | 当前接入模型 | 用户触发方式 | 官方依据 | 当前结论 |
| --- | --- | --- | --- | --- |
| Claude Code | native slash | `/super-dev 你的需求` | [Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) | slash 模式成立 |
| CodeBuddy CLI | native slash | `/super-dev 你的需求` | [CodeBuddy CLI slash commands](https://www.codebuddy.ai/docs/cli/slash-commands) | slash 模式成立 |
| CodeBuddy IDE | native slash | `/super-dev 你的需求` | [CodeBuddy IDE integrations](https://www.codebuddy.ai/docs/cli/ide-integrations) | IDE 内命令映射可用，持续验证中 |
| Cursor CLI | native slash | `/super-dev 你的需求` | [Cursor CLI slash commands](https://docs.cursor.com/en/cli/reference/slash-commands) | slash 模式成立 |
| Cursor IDE | native slash | `/super-dev 你的需求` | [Cursor Agent commands](https://docs.cursor.com/en/agent/chat/commands) | Agent Chat 命令模式可用，持续验证中 |
| Gemini CLI | native slash | `/super-dev 你的需求` | [Gemini CLI docs](https://google-gemini.github.io/gemini-cli/docs/) | 维持 slash 模式 |
| iFlow CLI | native slash | `/super-dev 你的需求` | [iFlow slash commands](https://platform.iflow.cn/en/cli/examples/slash-commands) | slash 模式成立 |
| Kimi CLI | rules-first / AGENTS | `super-dev: 你的需求` | [Kimi CLI interaction](https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html) / [Kimi CLI agents](https://www.kimi.com/code/docs/en/kimi-cli/guides/agents.html) | 当前更适合 `/init` 生成 AGENTS.md + 文本触发，不再按自定义 slash 建模 |
| Kiro CLI | native slash | `/super-dev 你的需求` | [Kiro CLI](https://kiro.dev/docs/cli/) | CLI 模式可用 |
| Kiro IDE | rules-first | `super-dev: 你的需求` | [Kiro steering](https://kiro.dev/docs/steering/) | 不再按 slash 建模，改为 steering/rules |
| OpenCode | native slash | `/super-dev 你的需求` | [OpenCode commands](https://opencode.ai/docs/commands/) | slash/commands 模式成立 |
| Qoder CLI | native slash | `/super-dev 你的需求` | [Qoder CLI](https://docs.qoder.com/cli/using-cli) | CLI 模式可用 |
| Qoder IDE | rules-first | `super-dev: 你的需求` | [Qoder rules](https://docs.qoder.com/user-guide/rules) | 不再按 slash 建模，改为 project rules |
| Windsurf | native slash / workflow | `/super-dev 你的需求` | [Windsurf workflows](https://docs.windsurf.com/plugins/cascade/workflows) | workflow 命令模式成立 |
| Codex CLI | AGENTS + Skill | `super-dev: 你的需求` | [OpenAI Codex docs](https://platform.openai.com/docs/codex) | 不支持自定义 slash，维持 AGENTS + Skill |
| Trae | rules-first | `super-dev: 你的需求` | [Trae rules](https://www.traeide.com/docs/what-is-trae-rules) | 不再要求手动 Skill，改为 rules-first |

## 当前产品规则

1. 支持原生 slash 的宿主：
   - 直接输入 `/super-dev 你的需求`
2. 不支持 slash 的宿主：
   - 直接输入 `super-dev: 你的需求`
3. Codex CLI 仍需要 AGENTS + Skill 协同，但用户不需要手动激活 Skill。
4. Kimi CLI 当前按 AGENTS + 文本触发建模，不再继续假设项目级自定义 slash。
5. Trae、Kiro IDE、Qoder IDE 当前都收敛到 rules-first，不再要求用户手动寻找“开技能”的入口。
6. 接入完成后可用 `super-dev integrate smoke --target <host_id>` 做标准化验收。

## 后续审计顺序

下一批继续做运行级收紧：

1. CodeBuddy IDE
2. Cursor IDE
3. Gemini CLI
4. Windsurf
5. OpenCode

目标不是继续堆“支持列表”，而是把每个宿主都压到明确的真实入口模型：

- slash
- rules-first
- AGENTS + Skill
- workflow command
