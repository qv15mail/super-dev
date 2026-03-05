# Super Dev Onboard 宿主接入设计（2026-03-04）

## 目标

实现“一步式接入”体验：

- 安装后选择宿主工具（全球 + 国内主流）：
  - CLI：Claude Code / Codex CLI / OpenCode / Aider
  - IDE/插件：Cursor / Windsurf / Cline / Continue / VS Code Copilot / JetBrains AI / Qoder / Trae / CodeBuddy / Antigravity / 通义灵码 / CodeGeeX
- 自动完成规则集成 + Skill 安装
- 生成 `/super-dev` 命令映射文件

## 新增命令

- `super-dev onboard`
  - `--host <target>`：指定单个宿主
  - `--all`：接入全部宿主
  - `--yes`：非交互模式（未指定 host 时默认 all）
  - `--force`：覆盖配置并重装 Skill
  - `--skip-integrate` / `--skip-skill` / `--skip-slash`
  - `--skill-name`：默认 `super-dev-core`

## 执行流程

1. 解析宿主目标列表（host/all/交互选择）。
2. 对每个宿主执行：
   - `IntegrationManager.setup(...)` 写入规则文件
   - `SkillManager.install(source="super-dev", ...)` 安装内置 Skill
   - `IntegrationManager.setup_slash_command(...)` 生成 slash 映射文件
3. 输出逐宿主结果摘要和最终可用指令。

## Slash 映射

新增按宿主输出命令映射文件（`super-dev` 命令说明）：

- `.claude/commands/super-dev.md`
- `.codex/commands/super-dev.md`
- `.opencode/commands/super-dev.md`
- `.aider/commands/super-dev.md`
- `.cursor/commands/super-dev.md`
- `.windsurf/commands/super-dev.md`
- `.cline/commands/super-dev.md`
- `.continue/commands/super-dev.md`
- `.github/commands/super-dev.md`
- `.idea/commands/super-dev.md`
- `.qoder/commands/super-dev.md`
- `.trae/commands/super-dev.md`
- `.codebuddy/commands/super-dev.md`
- `.agents/commands/super-dev.md`
- `.lingma/commands/super-dev.md`
- `.codegeex/commands/super-dev.md`

> 注：若宿主不识别 slash 命令文件，退回终端命令 `super-dev "需求"`。

## 验收标准

- `onboard --host claude-code --force --yes` 后，规则/skill/slash 三类文件全部生成。
- `onboard --yes --force --skip-skill` 可对全部宿主批量接入。
- 单元测试覆盖 slash 文件生成；集成测试覆盖 onboard 命令行为。
