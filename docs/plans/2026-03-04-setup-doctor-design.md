# Super Dev Setup + Doctor 设计说明（2026-03-04）

## 背景

`onboard` 已支持宿主接入，但商业化落地还缺少两个关键入口：

- 非技术用户一步完成接入与验证；
- 一键诊断“是否真的能用”。

## 目标

新增两个命令：

- `super-dev setup`：执行 onboard 并自动做诊断
- `super-dev doctor`：诊断宿主接入状态并给出修复建议

覆盖宿主：全球与国内主流 CLI/IDE 工具（含 Claude/Codex/OpenCode/Aider/Cursor/Windsurf/Cline/Continue/Copilot/JetBrains/Qoder/Trae/CodeBuddy/Antigravity/通义灵码/CodeGeeX）。

## 命令设计

### setup

- `--host` / `--all`
- `--skill-name`
- `--skip-integrate` / `--skip-skill` / `--skip-slash`
- `--skip-doctor`
- `--force`
- `--yes`

行为：先执行 onboard，成功后默认执行 doctor。

### doctor

- `--host` / `--all`（默认全部）
- `--skill-name`（默认 `super-dev-core`）
- `--skip-integrate` / `--skip-skill` / `--skip-slash`
- `--json`

检查维度：

1. 集成规则文件是否存在；
2. Skill 是否已安装；
3. `/super-dev` 映射文件是否存在。

当检查失败时，输出直接可执行的修复命令。

## 验收

- `setup --host <target> --force` 能完成接入并诊断通过；
- `doctor --host <target>` 在未接入时返回失败、接入后返回成功；
- 覆盖集成测试与回归测试。
