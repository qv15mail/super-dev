# Spec

## Title
Architecture Decoupling Foundation

## Objective
先把 Super Dev 当前最混乱的两层显式对象化：

- Workflow Contract
- Host Registry

目标不是一次性替换所有旧逻辑，而是先建立可以被现有系统逐步消费的新真源。

## Problem Statement
当前系统存在三个结构性问题：

1. 流程定义分散  
   标准流与 SEEAI 流分散在技能模板、宿主说明、API payload、测试断言中。

2. 宿主定义分散  
   宿主 ID、类别、安装模式、surface、协议摘要、手动宿主边界分散在 `catalogs.py`、`manager.py`、CLI、Web API。

3. 接入状态与展示耦合  
   多个消费面直接读取散落字段，后续加 runtime evidence 很难收敛。

## Design

### A. Workflow Contract Layer

新增统一 contract 模块，至少包含：

- `WorkflowPhase`
- `WorkflowContract`
- `STANDARD_WORKFLOW_CONTRACT`
- `SEEAI_WORKFLOW_CONTRACT`

字段最少包括：

- `id`
- `label`
- `phase_chain`
- `docs_confirmation_required`
- `preview_confirmation_required`
- `quality_style`
- `artifact_style`

第一轮接入目标：

- Web API 的 `competition_mode.phase_chain`
- 后续 CLI / 宿主说明的 phase chain 文案

### B. Host Registry Layer

新增统一 registry 模块，至少包含：

- `HostInstallMode`
- `HostDefinition`
- `HOST_REGISTRY`

字段最少包括：

- `id`
- `display_name`
- `category`
- `install_mode`
- `supports_slash`
- `supports_skill_surface`
- `preferred_standard_trigger`
- `preferred_seeai_trigger`
- `docs_urls`

第一轮接入目标：

- 手动宿主与自动宿主边界
- catalog / profile 的基础字段
- CLI 安装器简介与 Web host catalog 的部分真源

### C. Compatibility Strategy

本轮采用 façade 兼容：

- `catalogs.py` 仍保留旧常量
- `integrations/manager.py` 仍保留旧 profile 输出
- 但新增路径开始读 registry / contract
- `review_state` 的宿主真人验收文件格式先保持不变
- CLI / Web 的 runtime validation 报告新增结构化 `runtime_evidence` 字段，作为后续迁移锚点

这样可以避免一次性大重构导致宿主回归。

## Execution Plan

### Slice 1: Workflow Contracts

- 新建模块
- 定义标准流与 SEEAI 流
- 写最小测试
- 接入 Web API 的比赛模式 phase chain

### Slice 2: Host Registry

- 新建模块
- 先纳入重点宿主和手动宿主
- 抽出 install mode / trigger / docs 真源
- 写最小测试

### Slice 3: Integration Wiring

- `manager.py` / `web/api.py` 优先读新对象
- 手动宿主说明统一
- 为 runtime evidence 层预留入口

### Slice 4: Runtime Evidence Foundation

- 新建 `runtime_evidence.py`
- 显式拆分 integration status 与 runtime status
- 先接入 CLI / Web runtime validation payload
- 暂不改写现有 review-state 文件格式

## Risks

- 旧常量与新 registry 并存期间可能出现双真源漂移
- 如果一次迁太多宿主，回归面会过大
- 部分测试仍默认假设“每个宿主都有项目级规则文件”，需要逐步修正

## Acceptance

1. 仓库内存在正式 workflow contract 模块
2. 仓库内存在正式 host registry 模块
3. 现有至少一个消费面开始读新 contract
4. 现有至少一个消费面开始读新 registry
5. 手动宿主与自动宿主边界在代码和测试中都被显式表达
6. runtime validation 输出开始显式区分 integration evidence 与 runtime evidence
