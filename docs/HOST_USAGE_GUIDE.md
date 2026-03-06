# Super Dev 宿主使用指南（2.0.4）

## 目标

这份文档只回答一件事：

- 安装完 `Super Dev` 之后，在不同宿主里到底怎么用
- 哪些宿主可以直接 `/super-dev`
- 哪些宿主不能 `/super-dev`，应改用 Skill / 规则 / AGENTS

---

## 先看矩阵

认证等级说明：

- `Certified`：已按宿主真实能力完成专门适配，当前优先推荐。
- `Compatible`：接入链路完整，可以稳定使用，但还缺更长期的运行级认证。
- `Experimental`：已接入并可试用，但仍需更多真实项目验证。

| 宿主 | 类型 | 认证等级 | 是否支持 `/super-dev` | 正确触发方式 | 接入后是否需要重启 |
| --- | --- | --- | --- | --- | --- |
| Claude Code | CLI | Certified | 支持 | 在 Claude Code 会话中输入 `/super-dev 你的需求` | 否 |
| CodeBuddy CLI | CLI | Compatible | 支持 | 在 CodeBuddy CLI 会话中输入 `/super-dev 你的需求` | 否 |
| CodeBuddy IDE | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Cursor CLI | CLI | Compatible | 支持 | 在 Cursor CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Cursor IDE | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Gemini CLI | CLI | Compatible | 支持 | 在 Gemini CLI 会话中输入 `/super-dev 你的需求` | 否 |
| iFlow CLI | CLI | Experimental | 支持 | 在 iFlow CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Kimi CLI | CLI | Experimental | 不支持 | 在 Kimi CLI 会话中输入 `super-dev: 你的需求`（由 `.kimi/AGENTS.md` 生效） | 否 |
| Kiro CLI | CLI | Compatible | 支持 | 在 Kiro CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Kiro IDE | IDE | Experimental | 不支持 | 在 Kiro IDE Agent Chat 中输入 `super-dev: 你的需求`（由 `.kiro/steering/super-dev.md` 生效） | 否 |
| OpenCode CLI | CLI | Experimental | 支持 | 在 OpenCode CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Qoder CLI | CLI | Compatible | 支持 | 在 Qoder CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Qoder IDE | IDE | Experimental | 不支持 | 在 Qoder IDE Agent Chat 中输入 `super-dev: 你的需求`（由 `.qoder/rules.md` 生效） | 否 |
| Windsurf | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Codex CLI | CLI | Certified | 不支持 | 重启 Codex 后输入 `super-dev: 你的需求`，由 `.codex/AGENTS.md` + `super-dev-core` Skill 生效 | 是 |
| Trae | IDE | Certified | 不支持 | 在 Trae Agent Chat 中输入 `super-dev: 你的需求`（由 `.trae/rules.md` 生效） | 否 |

### 最简判断

1. 如果你的宿主在表格里标记为“支持”，直接用 `/super-dev 你的需求`。
2. 优先选择 `Certified` 宿主，其次是 `Compatible`。
3. 如果是 `Codex CLI`，不要试 `/super-dev`，重启 Codex 后输入 `super-dev: 你的需求`。
4. 如果是 `Kimi CLI`，不要试 `/super-dev`，直接在当前会话输入 `super-dev: 你的需求`。
5. 如果是 `Trae`，不要试 `/super-dev`，直接在 Trae Agent Chat 输入 `super-dev: 你的需求`。

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

#### 6. Gemini CLI

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

#### 7. iFlow CLI

安装：
```bash
super-dev onboard --host iflow --force --yes
```

触发位置：
在项目目录启动 iFlow CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前按 slash 宿主适配。
2. 如果 slash 未出现，先检查项目级命令文件是否已写入。

#### 8. Kimi CLI

安装：
```bash
super-dev onboard --host kimi-cli --force --yes
```

触发位置：
在项目目录启动 Kimi CLI 会话后触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 不要输入 `/super-dev`，Kimi CLI 当前优先按 `.kimi/AGENTS.md + 文本触发` 工作。
2. 建议先用 `super-dev doctor --host kimi-cli` 做一次确认。
3. 尽量保持同一会话完成完整开发流程。

#### 9. Kiro CLI

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

#### 10. Kiro IDE

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
2. 如果 steering/rules 未加载，先重开项目窗口。

#### 11. OpenCode

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

#### 12. Qoder CLI

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

#### 13. Qoder IDE

安装：
```bash
super-dev onboard --host qoder --force --yes
```

触发位置：
打开 Qoder IDE 的 Agent Chat，在当前项目内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. Qoder IDE 当前优先按 project rules 模式触发，不走 `/super-dev`。
2. 若规则未生效，重新打开项目或重新创建聊天。

#### 14. Windsurf

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

#### 15. Codex CLI

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
2. 实际依赖 `.codex/AGENTS.md` 和 `.codex/skills/super-dev-core/SKILL.md`。
3. 如果旧会话没加载新 Skill，重启 `codex` 再试。

#### 16. Trae

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

接入后是否需要重启：否

补充说明：
1. 不要输入 `/super-dev`。
2. Trae 当前默认按项目 rules 模式工作，无需手动开启 Skill。
3. 随后按 `output/*` 与 `.super-dev/changes/*/tasks.md` 推进开发。

## 推荐给最终用户的最简说法

### 原生 slash 宿主

直接说：

```text
/super-dev 你的需求
```

### Codex CLI

直接说：

```text
重启 codex，然后输入 `super-dev: 你的需求`，不要输入 /super-dev
```

### Trae

直接说：

```text
在 Trae Agent Chat 中直接输入 `super-dev: 你的需求`
```

---

## 为什么要区分这些宿主

因为 Super Dev 不是模型平台，而是宿主内治理层。

也就是说：

- 宿主负责“会写代码”
- Super Dev 负责“按商业级流程把事情做对、做全、可审计”

所以不同宿主的入口可以不同，但执行标准必须一致。

---

## 相关文档

- [README](/Users/weiyou/Documents/kaifa/super-dev/README.md)
- [README_EN](/Users/weiyou/Documents/kaifa/super-dev/README_EN.md)
- [INSTALL_OPTIONS](/Users/weiyou/Documents/kaifa/super-dev/docs/INSTALL_OPTIONS.md)
- [INTEGRATION_GUIDE](/Users/weiyou/Documents/kaifa/super-dev/docs/INTEGRATION_GUIDE.md)
