# Tasks

## 1. Planning

- [x] **1.1: 创建 host-validation-bugfix-proofpack change spec**
  - 固化宿主验收中心、显式 bugfix 模式、交付证据包升级的目标、边界与验收标准。
  - Refs: `host-validation::*`, `bugfix::*`, `proof-pack::*`

## 2. Core

- [x] **2.1: 显式化 Bugfix Mode**
  - 增加明确 CLI 入口与状态提示，让用户不必依赖隐式关键词识别。
  - Refs: `bugfix::cli`, `bugfix::workflow`

- [x] **2.2: 升级 Host Validation Center**
  - 输出宿主验收摘要、阻塞项、前置条件与下一步动作。
  - Refs: `host-validation::summary`, `host-validation::api`, `host-validation::web`

- [x] **2.3: 升级 Delivery Evidence Pack**
  - 增加执行摘要、阻塞项、关键证据与下一步动作。
  - Refs: `proof-pack::summary`, `proof-pack::artifacts`

## 3. Interface

- [x] **3.1: 更新 CLI / Web API / Web 管理台**
  - 让这三类能力都能被终端用户和管理台用户直接消费。
  - Refs: `bugfix::surface`, `host-validation::surface`, `proof-pack::surface`

## 4. Documentation & Quality

- [x] **4.1: 更新 README / Workflow / Host 文档**
  - 把新入口与新视图写成正式说明。
  - Refs: `docs::readme`, `docs::workflow`, `docs::hosts`

- [x] **4.2: 补齐测试并执行全量验证**
  - 包括 CLI、API、核心逻辑和 Web 视图依赖的数据回归。
  - Refs: `tests::cli`, `tests::api`, `tests::unit`
