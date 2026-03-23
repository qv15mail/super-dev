# Super Dev 宿主使用指南（2.1.1）

## 目标

这份文档只回答一件事：

- 安装完 `Super Dev` 之后，在不同宿主里到底怎么用
- 哪些宿主可以直接 `/super-dev`
- 哪些宿主不能 `/super-dev`，应改用 Skill / 规则 / AGENTS

当前版本默认主推 `16` 个宿主适配配置。这台机器当前自动检测到 `17` 个已安装宿主，其中包含额外的实验宿主。

---

## 先看矩阵

认证等级说明：

- `Certified`：已按宿主真实能力完成专门适配，当前优先推荐。
- `Compatible`：接入链路完整，可以稳定使用，但还缺更长期的运行级认证。
- `Experimental`：已接入并可试用，但仍需更多真实项目验证。

| 宿主 | 类型 | 认证等级 | 是否支持 `/super-dev` | 正确触发方式 | 接入后是否需要重启 |
| --- | --- | --- | --- | --- | --- |
| Antigravity | IDE | Experimental | 支持 | 在 Antigravity Agent Chat 中输入 `/super-dev 你的需求`（由 `GEMINI.md` + `.gemini/commands/` + `.agent/workflows/` + `~/.gemini/skills/` 生效） | 是 |
| Claude Code | CLI | Certified | 支持 | 在 Claude Code 会话中输入 `/super-dev 你的需求` | 否 |
| CodeBuddy CLI | CLI | Compatible | 支持 | 在 CodeBuddy CLI 会话中输入 `/super-dev 你的需求`（由 `.codebuddy/commands/super-dev.md` + `.codebuddy/skills/` / `~/.codebuddy/skills/` 生效） | 否 |
| CodeBuddy IDE | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求`（由 `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` / `~/.codebuddy/agents/` + `~/.codebuddy/skills/` 生效） | 否 |
| Cursor CLI | CLI | Compatible | 支持 | 在 Cursor CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Cursor IDE | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Gemini CLI | CLI | Compatible | 支持 | 在 Gemini CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Kiro CLI | CLI | Compatible | 支持 | 在 Kiro CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Kiro IDE | IDE | Experimental | 不支持 | 在 Kiro IDE Agent Chat 中输入 `super-dev: 你的需求`（由 `.kiro/steering/super-dev.md` 生效） | 否 |
| OpenCode CLI | CLI | Experimental | 支持 | 在 OpenCode CLI 会话中输入 `/super-dev 你的需求`（由 `.opencode/commands/super-dev.md` + `.opencode/skills/` / `~/.config/opencode/skills/` 生效） | 否 |
| Qoder CLI | CLI | Compatible | 支持 | 在 Qoder CLI 会话中输入 `/super-dev 你的需求`（由 `.qoder/commands/super-dev.md` + `.qoder/skills/` / `~/.qoder/skills/` 生效） | 否 |
| Qoder IDE | IDE | Experimental | 支持 | 在 Qoder IDE Agent Chat 中输入 `/super-dev 你的需求`（由 `.qoder/commands/super-dev.md` + `.qoder/rules.md` + `.qoder/skills/` / `~/.qoderwork/skills/` 生效） | 否 |
| VS Code Copilot | IDE | Experimental | 不支持 | 在 Copilot Chat 中输入 `super-dev: 你的需求` 或 `super-dev：你的需求`（由 `.github/copilot-instructions.md` + `AGENTS.md` 生效） | 否 |
| Windsurf | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求`（由 `.windsurf/workflows/super-dev.md` + `.windsurf/skills/` / `~/.codeium/windsurf/skills/` 生效） | 否 |
| Codex CLI | CLI | Certified | 不支持 | 重启 Codex 后输入 `super-dev: 你的需求`，由 `AGENTS.md` + 兼容 Skill 生效 | 是 |
| Trae | IDE | Compatible | 不支持 | 在 Trae Agent Chat 中输入 `super-dev: 你的需求`（由 `.trae/project_rules.md` + `~/.trae/user_rules.md` 生效；同时兼容写入 `.trae/rules.md` + `~/.trae/rules.md`，若检测到兼容 Skill `~/.trae/skills/super-dev-core/SKILL.md` 会额外增强） | 是 |

### 最简判断

1. 如果你的宿主在表格里标记为“支持”，直接用 `/super-dev 你的需求`。
2. 优先选择 `Certified` 宿主，其次是 `Compatible`。
3. 如果是 `Codex CLI`，不要试 `/super-dev`，重启 Codex 后输入 `super-dev: 你的需求`。
4. 如果是 `Trae`，不要试 `/super-dev`，直接在 Trae Agent Chat 输入 `super-dev: 你的需求`。
5. 如果是 `Kiro IDE`、`Trae` 或 `VS Code Copilot`，优先用 `super-dev: 你的需求` 或 `super-dev：你的需求`。

---

## 总体原则

无论宿主是哪一种，Super Dev 的目标都一样：

1. 先研究同类产品
2. 再生成 `research / PRD / architecture / UIUX`
3. 再生成 Spec 与 `tasks.md`
4. 最后才进入编码、质量门禁与交付

如果宿主支持联网能力，优先由宿主自己完成 research 阶段。

如果你不确定该选哪个宿主，可以先运行：

```bash
super-dev start --idea "你的需求"
```

它会自动选择当前机器上最合适的宿主，并给出完整试用步骤。

---

## 安装后通用检查

先在项目根目录执行：

```bash
super-dev onboard --host <host_id> --force --yes
```

或者交互式：

```bash
super-dev
```

接入完成后建议执行：

```bash
super-dev doctor --host <host_id>
```

它现在会直接告诉你：

1. 该宿主的主入口
2. 是否应该使用 `/super-dev`
3. 是否需要重启宿主
4. 接入后还要做什么
5. 如何做 Smoke 验收

接着建议执行：

```bash
super-dev integrate smoke --target <host_id>
```

它会输出：

1. 该宿主的标准验收语句
2. 该宿主的验收步骤
3. 看到什么结果才算接入真正生效

如果你要记录真人会话验收结果，再执行：

```bash
super-dev integrate validate --target <host_id>
super-dev integrate validate --target <host_id> --status passed --comment "首轮先进入 research，三文档已真实落盘"
```

这样会把该宿主的真人验收状态写入：

- `.super-dev/review-state/host-runtime-validation.json`

另外，`super-dev doctor --host <host_id>`、`integrate audit`、`integrate validate` 现在会显示该宿主的前置条件项，例如：

- 是否需要先在宿主内完成鉴权
- 是否需要关闭旧会话后重开宿主
- 是否必须绑定到目标项目/工作区

---

## 每个宿主怎么用


#### 1. Claude Code

安装：
```bash
super-dev onboard --host claude-code --force --yes
```

触发位置：
在项目目录启动 Claude Code 当前会话后，直接在同一会话里触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 推荐作为首选 CLI 宿主。
2. 接入后可先执行 `super-dev doctor --host claude-code` 确认 slash 已生效。
3. Claude Code 官方已公开 `.claude/agents/` 与 `~/.claude/agents/`，Super Dev 会同步生成 `super-dev-core` subagent。

#### 2. CodeBuddy CLI

安装：
```bash
super-dev onboard --host codebuddy-cli --force --yes
```

触发位置：
在项目目录启动 CodeBuddy CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 在当前 CLI 会话中直接输入即可。
2. 如果会话已提前打开，建议重新加载项目规则后再试。

#### 3. CodeBuddy IDE

安装：
```bash
super-dev onboard --host codebuddy --force --yes
```

触发位置：
打开 CodeBuddy IDE 的 Agent Chat，在项目上下文内触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 建议在项目级 Agent Chat 中使用，不要脱离项目上下文。
2. 先让宿主完成 research，再继续文档和编码。
3. 当前按 `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` 接入。


#### 4. Cursor CLI

安装：
```bash
super-dev onboard --host cursor-cli --force --yes
```

触发位置：
在项目目录启动 Cursor CLI 当前会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 适合终端内连续执行研究、文档和编码。
2. 若命令列表未刷新，可重开一次 Cursor CLI 会话。

#### 5. Cursor IDE

安装：
```bash
super-dev onboard --host cursor --force --yes
```

触发位置：
打开 Cursor 的 Agent Chat，并确保当前工作区就是目标项目。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 建议固定在同一个 Agent Chat 会话里完成整条流水线。
2. 如果项目规则没加载，先重新打开工作区或重新发起聊天。

#### 6. Antigravity

安装：
```bash
super-dev onboard --host antigravity --force --yes
```

触发位置：
打开 Antigravity 的 Agent Chat / Prompt 面板，并确保当前工作区就是目标项目。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：是

补充说明：
1. Antigravity 当前按 `GEMINI.md + .agent/workflows + /super-dev` 模式接入。
2. 接入会写入项目级 `GEMINI.md`、`.gemini/commands/super-dev.md`、`.agent/workflows/super-dev.md`。
3. 同时会写入用户级 `~/.gemini/GEMINI.md`、`~/.gemini/commands/super-dev.md` 与 `~/.gemini/skills/super-dev-core/SKILL.md`。
4. 完成接入后请重开 Antigravity 或至少新开一个 Agent Chat，再输入 `/super-dev 你的需求`。

#### 7. Gemini CLI

安装：
```bash
super-dev onboard --host gemini-cli --force --yes
```

触发位置：
在项目目录启动 Gemini CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 优先在同一会话中完成 research -> 三文档 -> 用户确认 -> Spec -> 前端运行验证 -> 后端/交付。
2. 若宿主支持联网，先让它完成同类产品研究。

#### 8. Kiro CLI

安装：
```bash
super-dev onboard --host kiro-cli --force --yes
```

触发位置：
在项目目录启动 Kiro CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. CLI 模式下直接使用 slash。
2. 如果项目规则未刷新，重新进入项目目录再启动 Kiro CLI。

#### 9. Kiro IDE

安装：
```bash
super-dev onboard --host kiro --force --yes
```

触发位置：
打开 Kiro IDE 的 Agent Chat / AI 面板，在项目上下文内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. Kiro IDE 当前优先按 steering/rules 模式触发，不走 `/super-dev`。
2. 接入会写入项目级 `.kiro/steering/super-dev.md`，并补充官方全局 steering `~/.kiro/steering/AGENTS.md`。
3. 如果 steering/rules 未加载，先重开项目窗口。

#### 10. OpenCode

安装：
```bash
super-dev onboard --host opencode --force --yes
```

触发位置：
在项目目录启动 OpenCode CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 按 CLI slash 模式使用。
2. 若你使用全局命令目录，也建议保留项目级接入文件。

#### 11. Qoder CLI

安装：
```bash
super-dev onboard --host qoder-cli --force --yes
```

触发位置：
在项目目录启动 Qoder CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 适合命令行流水线开发。
2. 若 slash 未生效，先确认 `.qoder/commands/super-dev.md` 已生成。
3. 官方文档已公开 `.qoder/skills/` 与 `~/.qoder/skills/`，Super Dev 会同时安装命令与 Skill。

#### 12. Qoder IDE

安装：
```bash
super-dev onboard --host qoder --force --yes
```

触发位置：
打开 Qoder IDE 的 Agent Chat，在当前项目内触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. Qoder IDE 当前优先使用项目级 commands + rules + skill 模式，直接在 Agent Chat 输入 `/super-dev 你的需求`。
2. 若新增命令未出现，先确认 `.qoder/commands/super-dev.md` 已生成，再重新打开项目或新开一个 Agent Chat。
3. 官方文档已公开 `.qoder/skills/` 与 `~/.qoderwork/skills/`，Super Dev 会同步安装 `super-dev-core`。

#### 13. Windsurf

安装：
```bash
super-dev onboard --host windsurf --force --yes
```

触发位置：
打开 Windsurf 的 Agent Chat / Workflow 入口，在项目上下文内触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前按 IDE slash/workflow 模式适配。
2. 更适合在同一个 Workflow 里连续完成研究、文档、Spec 和编码。
3. 官方文档已公开 `.windsurf/skills/` 与 `~/.codeium/windsurf/skills/`。

#### 14. Codex CLI

安装：
```bash
super-dev onboard --host codex-cli --force --yes
```

触发位置：
在项目目录完成接入后，重启 `codex`，然后在新的 Codex 会话里触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：是

补充说明：
1. 不要输入 `/super-dev`，Codex 当前不走自定义 slash。
2. 实际依赖 `AGENTS.md` 和 `.codex/skills/super-dev-core/SKILL.md`。
3. 如果旧会话没加载新 Skill，重启 `codex` 再试。

#### 15. Trae

安装：
```bash
super-dev onboard --host trae --force --yes
```

触发位置：
打开 Trae IDE 的 Agent Chat，在当前项目上下文内直接触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：是

补充说明：
1. 不要输入 `/super-dev`。
2. 接入一定会写入项目级 `.trae/project_rules.md`、`.trae/rules.md` 和用户级 `~/.trae/user_rules.md`、`~/.trae/rules.md`；如果检测到兼容技能目录，也会增强安装 `~/.trae/skills/super-dev-core/SKILL.md`。
3. 完成接入后建议重开 Trae 或至少新开一个 Agent Chat，使规则生效；如果兼容 Skill 已安装，也会一起生效。
4. 随后按 `output/*` 与 `.super-dev/changes/*/tasks.md` 推进开发。

#### 16. VS Code Copilot

安装：
```bash
super-dev onboard --host vscode-copilot --force --yes
```

触发位置：
打开 VS Code 的 Copilot Chat，并确保当前工作区就是目标项目。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. VS Code Copilot 当前按 `.github/copilot-instructions.md` + `AGENTS.md` 工作。
2. 不使用 `/super-dev`，直接在 Copilot Chat 输入 `super-dev:` 或 `super-dev：`。
3. 如果当前聊天没有重新加载规则，先重开工作区或新开一个 Copilot Chat。
