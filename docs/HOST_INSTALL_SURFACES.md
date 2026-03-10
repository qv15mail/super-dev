# 宿主接入面说明

## 1. 角色分层

Super Dev 的宿主接入由三层组成：

1. Python CLI
- 负责安装、检测、修复、状态、质量门禁和交付命令。

2. Host Skill
- 负责让宿主理解什么是 Super Dev、何时进入流水线、第一次响应应该说什么、何时暂停等待用户确认。

3. Project Context Files
- 负责把当前项目的规则、知识库、命令触发、AGENTS、steering、tasks 和输出路径注入给宿主。

## 2. 触发模型

### slash / command 宿主
- 用户输入 `/super-dev ...`
- slash/command 文件负责触发
- host-level skill 负责让宿主理解完整流水线协议
- project-level rules / AGENTS / commands 负责提供当前项目上下文

### 非 slash 宿主
- 用户输入 `super-dev: ...`
- rules / AGENTS / steering 负责将文本触发映射到 Super Dev 流水线
- host-level skill 负责让宿主理解完整流水线协议

## 3. 安装面分类

不要把所有宿主都当成同一种安装模型。当前应按三类看：

1. 项目级接入面
- 例如 `.qoder/rules.md`
- 例如 `.qoder/commands/super-dev.md`
- 例如 `AGENTS.md`
- 例如 `.trae/project_rules.md`

2. 宿主级接入面
- 例如 `~/.codex/skills/super-dev-core/SKILL.md`
- 例如 `~/.trae/skills/super-dev-core/SKILL.md`
- 例如 `~/.qoder/commands/super-dev.md`

3. 兼容增强面
- 当宿主官方文档没有明确文件路径，但本机已存在宿主约定目录时，可作为兼容增强处理。
- 这类路径不能冒充“官方明确路径”。

## 4. 检测策略

宿主检测不再只依赖固定 macOS `.app` 路径。

当前检测顺序：

1. `PATH` 中的可执行文件
2. macOS 常见应用目录
- `~/Applications`
- `/Applications`
3. Windows 常见目录
- `%LOCALAPPDATA%/Programs/...`
- `%PROGRAMFILES%/...`
- `%PROGRAMFILES(X86)%/...`
4. 其他已知用户级路径候选

## 5. 当前工程约束

1. 不允许凭“命名习惯”猜测宿主官方 skill 路径。
2. 如果官方文档明确的是 commands / rules / AGENTS，就按官方机制接入。
3. host-level skill 只有在以下情况下才应作为默认路径：
- 官方文档明确
- 或当前产品明确标注为本机兼容增强

## 6. 当前重点宿主

### Antigravity
- 触发：`/super-dev 你的需求`
- 项目级：`GEMINI.md` + `.gemini/commands/super-dev.md` + `.agent/workflows/super-dev.md`
- 用户级：`~/.gemini/GEMINI.md` + `~/.gemini/commands/super-dev.md`
- 用户级 Skill：`~/.gemini/skills/super-dev-core/SKILL.md`
- 说明：当前按 Gemini 上下文面 + Antigravity workflow 面建模。slash 负责触发，宿主级 Skill 负责让宿主理解 Super Dev 流水线协议。

### CodeBuddy
- 触发：`/super-dev 你的需求`
- 项目级：`.codebuddy/rules.md` 或 `.codebuddy/AGENTS.md` + `.codebuddy/commands/super-dev.md` + `.codebuddy/agents/super-dev-core.md`
- 项目级 Skill：`.codebuddy/skills/super-dev-core/SKILL.md`
- 用户级：`~/.codebuddy/commands/super-dev.md` + `~/.codebuddy/agents/super-dev-core.md`
- 用户级 Skill：`~/.codebuddy/skills/super-dev-core/SKILL.md`
- 说明：官方文档已公开项目级 commands、subagents、skills 与用户级 agents/skills，slash/command 负责触发，agent/skill 负责让宿主理解 Super Dev 流水线。

- 触发：`/super-dev 你的需求`
- 项目级：`.codebuddy/rules.md` + `.codebuddy/commands/super-dev.md` + `.codebuddy/agents/super-dev-core.md`
- 项目级 Skill：`.codebuddy/skills/super-dev-core/SKILL.md`
- 用户级：`~/.codebuddy/commands/super-dev.md` + `~/.codebuddy/agents/super-dev-core.md`
- 用户级 Skill：`~/.codebuddy/skills/super-dev-core/SKILL.md`

### Claude Code
- 触发：`/super-dev 你的需求`
- 项目级：`.claude/CLAUDE.md` + `.claude/commands/super-dev.md` + `.claude/agents/super-dev-core.md`
- 用户级：`~/.claude/agents/super-dev-core.md`
- 说明：Claude Code 官方公开的是 commands + subagents，而不是 `.claude/skills/`。当前应按 slash + subagent 协议建模。

### Qoder IDE
- 触发：`/super-dev 你的需求`
- 项目级：`.qoder/rules.md` + `.qoder/commands/super-dev.md`
- 项目级 Skill：`.qoder/skills/super-dev-core/SKILL.md`
- 用户级：`~/.qoder/commands/super-dev.md`
- 用户级 Skill：`~/.qoderwork/skills/super-dev-core/SKILL.md`
- 说明：官方文档已公开 commands 与 skills，当前应按 commands + rules + skill 的组合模型处理。

### Qoder CLI
- 触发：`/super-dev 你的需求`
- 项目级：`.qoder/AGENTS.md` + `.qoder/commands/super-dev.md`
- 项目级 Skill：`.qoder/skills/super-dev-core/SKILL.md`
- 用户级：`~/.qoder/commands/super-dev.md`
- 用户级 Skill：`~/.qoder/skills/super-dev-core/SKILL.md`
- 说明：CLI 与 IDE 的 command 入口一致，但 user-level skill 目录不同。

### Windsurf
- 触发：`/super-dev 你的需求`
- 项目级：`.windsurf/rules.md` + `.windsurf/workflows/super-dev.md`
- 项目级 Skill：`.windsurf/skills/super-dev-core/SKILL.md`
- 用户级 Skill：`~/.codeium/windsurf/skills/super-dev-core/SKILL.md`
- 说明：官方文档已公开 project/user skills，workflow 负责触发，Skill 负责长期协议。

### OpenCode
- 触发：`/super-dev 你的需求`
- 项目级：`.opencode/AGENTS.md` + `.opencode/commands/super-dev.md`
- 项目级 Skill：`.opencode/skills/super-dev-core/SKILL.md`
- 用户级：`~/.config/opencode/commands/super-dev.md`
- 用户级 Skill：`~/.config/opencode/skills/super-dev-core/SKILL.md`
- 说明：官方文档同时公开 commands 与 skills，项目级和用户级都应视为正式接入面。

### iFlow
- 触发：`/super-dev 你的需求`
- 项目级：`.iflow/AGENTS.md` + `.iflow/commands/super-dev.toml`
- 项目级 Skill：`.iflow/skills/super-dev-core/SKILL.md`
- 用户级 Skill：`~/.iflow/skills/super-dev-core/SKILL.md`
- 说明：官方文档已公开 skills，CLI 侧适合 “command 触发 + skill 协议” 模型。

### Trae
- 触发：`super-dev: 你的需求`
- 项目级：`.trae/project_rules.md`
- 用户级：`~/.trae/user_rules.md`
- 兼容增强：`.trae/rules.md`、`~/.trae/rules.md`、`~/.trae/skills/super-dev-core/SKILL.md`
- 说明：目前公开文档能确认的是 project rules / user rules；同时本机已观测到 `rules.md` 规则面可协同生效，`~/.trae/skills` 仍只作为兼容增强路径。

- 触发：`super-dev: 你的需求`
- 项目级：`.trae/project_rules.md`
- 用户级：`~/.trae/user_rules.md`
- 兼容增强：`.trae/rules.md`、`~/.trae/rules.md`、`~/.trae/skills/super-dev-core/SKILL.md`

### Gemini CLI
- 触发：`/super-dev 你的需求`
- 项目级：`GEMINI.md` + `.gemini/commands/super-dev.md`
- 用户级：`~/.gemini/GEMINI.md`
- 兼容增强：`~/.gemini/skills/super-dev-core/SKILL.md`
- 说明：Gemini CLI 官方公开 `GEMINI.md` 作为上下文文件，当前应按 commands + GEMINI.md 建模；skills 仍只作为兼容增强。

### Codex CLI
- 触发：`super-dev: 你的需求`
- 项目级：`AGENTS.md`
- 用户级：`~/.codex/skills/super-dev-core/SKILL.md`
- 说明：Codex 当前按项目级 AGENTS.md + 官方用户级 Skills 目录建模，不走自定义 slash。

### Kiro IDE
- 触发：`super-dev: 你的需求`
- 项目级：`.kiro/AGENTS.md` + `.kiro/steering/super-dev.md`
- 用户级：`~/.kiro/steering/AGENTS.md`
- 兼容增强：`~/.kiro/skills/super-dev-core/SKILL.md`
- 说明：Kiro 官方明确公开 steering；当前以 project steering + global steering 为正式接入面，skills 仍只作为兼容增强。
