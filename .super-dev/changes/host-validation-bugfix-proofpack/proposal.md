# Proposal

## Proposal

## Description
把现有的宿主运行时验收、bugfix 轻量流程与 proof pack 交付证据能力，从“底层治理能力”升级成用户可见、可主动使用、可通过 CLI / Web 直接消费的正式产品功能。

## Motivation
当前项目已经有：

- `integrate audit`
- `integrate validate`
- bugfix 请求识别
- `release proof-pack`

但这些能力仍然偏工程化，用户需要知道太多内部概念才能用起来。需要把它们收成三个明确的产品模块：

1. Host Validation Center
2. Explicit Bugfix Mode
3. Delivery Evidence Pack

## Impact
涉及 5 个主要模块：

1. `.super-dev/changes/*` 变更体系
2. CLI 入口与运行状态提示
3. Web API 与 Web 管理台展示
4. 交付证据输出模型
5. README / Workflow / Host 文档说明
