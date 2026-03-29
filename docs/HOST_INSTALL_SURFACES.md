# Host Install Surfaces

这份文档描述各宿主的安装面、触发词和接入检查命令，避免 README 只给入口不解释差异。

## Core Rule

不同宿主的安装方式和触发词不同，但审查命令应该收敛到同一套：

- `super-dev integrate audit --auto`
- `super-dev doctor`
- `super-dev onboard`

## Common Hosts

### Codex CLI

- 触发词：`super-dev:`
- 审查命令：`super-dev integrate audit --auto`

### Claude Code

- 触发词：`/super-dev`
- 审查命令：`super-dev integrate audit --auto`

### Trae / Kiro / Copilot Chat

- 触发词：`super-dev:`
- 审查命令：`super-dev integrate audit --auto`

## 建议顺序

1. 先确认当前宿主对应的触发词
2. 再运行 `super-dev integrate audit --auto`
3. 如有缺口，再执行 `super-dev onboard` 或 `super-dev doctor`
4. 通过后再开始正式流水线

## 自定义安装路径

如果宿主没有装在默认目录，自动检测除了命令名和常见安装路径，还支持显式路径覆盖。

- `SUPER_DEV_HOST_PATH_CODEX_CLI=<安装路径>`
- `SUPER_DEV_HOST_PATH_OPENCODE=<安装路径>`
- `SUPER_DEV_HOST_PATH_CURSOR=<安装路径>`

设置后重新执行 `super-dev onboard --auto`、`super-dev doctor --auto` 或 `super-dev start` 即可。

## 为什么需要这份文档

如果只告诉用户“输入 super-dev”，但不说明当前宿主到底该用 `/super-dev` 还是 `super-dev:`，安装成功也会在第一步就卡住。
