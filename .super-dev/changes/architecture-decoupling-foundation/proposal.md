# Proposal

## Proposal

## Description
为 Super Dev 启动一轮“架构解耦基础层”重构，先把当前高耦合的宿主定义、流程合同、运行验证和展示层拆出清晰边界，并以兼容方式逐步接入现有 CLI / Web / 宿主适配链路。

## Motivation
当前能力已经很强，但核心元数据与行为分散在 `catalogs.py`、`integrations/manager.py`、`web/api.py`、CLI mixins 和技能模板中，导致：

- 加一个宿主需要同时修改多份真源
- 标准流与 SEEAI 流主要靠字符串和条件分支维持
- “已接入”和“已验证”仍容易在产品层被混淆
- CLI / API / 文档存在重复定义，维护成本持续走高

本次不是推翻重来，而是先搭出两个基础层：

1. Workflow Contract Layer
2. Host Registry Layer

并让现有系统开始逐步消费它们。

## Scope

### In scope

- 新建标准流与 SEEAI 流的正式 contract 模块
- 新建宿主 registry 基础模块，承载安装模式、触发面、分类、文档入口等基础定义
- 让现有部分路径开始读新 contract / registry，而不是继续硬编码散落
- 为后续 runtime evidence layer 留出结构接口

### Out of scope

- 本轮不一次性拆完全部宿主适配逻辑
- 本轮不删除旧字段和旧实现，只做兼容迁移
- 本轮不重做全部官网和 README 文案
- 本轮不把 runtime evidence 完整产品化

## Impact
涉及 5 个主要模块：

1. `.super-dev/changes/*` 变更体系
2. `super_dev/integrations/*`
3. `super_dev/workflow*`
4. `super_dev/web/api.py`
5. 受影响测试与基础文档

## Delivery Strategy

### Batch 1

- 建立 `WorkflowContract`
- 建立 `HostDefinition`
- 让 SEEAI / standard 的 phase chain 脱离零散字符串

### Batch 2

- 让 Web/API、CLI 概览、宿主 profile 开始读 registry / contract
- 明确手动宿主与自动宿主边界

### Batch 3

- 在后续 change 中继续接入 runtime evidence registry 和评分体系

## Compatibility Notes

- 旧的 `catalogs.py`、`manager.py`、CLI mixin 和 Web API 字段全部保留，避免现有宿主接入和官网消费面回归。
- 新增的 `workflow_contract.py`、`host_registry.py`、`runtime_evidence.py` 先作为真源基础层存在，由现有 façade 渐进读取。
- `supports_slash`、`host_protocol_mode`、`host_protocol_summary` 等高频字段开始优先读 registry，但旧映射仍保留为 fallback。
- runtime validation 现有文件格式不改，新增的是结构化 `runtime_evidence` 输出字段，用于后续完全迁移。

## Next Split Points

下一阶段的拆分入口已经明确：

1. `integrations/manager.py`
   继续把 protocol / surfaces / usage profile 的基础元数据迁到 `host_registry.py`
2. `cli_host_ops_mixin.py` 与 `web/api.py`
   继续把 runtime validation / compatibility matrix 改成消费 `runtime_evidence.py`
3. `catalogs.py`
   逐步降级为展示层 catalog，而不是宿主元数据真源
4. 宿主专项 adapter
   为 `CodeBuddy / OpenClaw / WorkBuddy` 这类差异较大的宿主建立独立 adapter 模块
