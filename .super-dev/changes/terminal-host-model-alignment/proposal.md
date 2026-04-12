# Proposal

## Proposal

## Description
将 Super Dev 的公开交互模型收敛为“终端两命令 + 宿主两触发”，并修复当前主路径上的越层副作用、宿主误识别和运行状态表达混淆。

## Motivation
当前实现把过多 CLI 命令、自动迁移、自动接入、共享 surface 误判和静态宿主等级暴露给最终用户，导致产品边界不清晰、接入副作用不可预期、宿主成熟度被高估。用户已经明确新的产品模型：

- 终端只保留 `super-dev`
- 终端只保留 `super-dev update`
- 宿主内正常使用只保留 `/super-dev` 与 `super-dev:`

系统需要围绕这个模型重新对齐入口、迁移、验证和对外文案。

## Impact
涉及 6 个主要模块：

1. CLI 主入口与安装/升级路由
2. 宿主接入与迁移识别
3. 宿主运行验证状态模型
4. 配置与版本一致性
5. README / README_EN
6. 官网首页 / Docs / Changelog 叙事
