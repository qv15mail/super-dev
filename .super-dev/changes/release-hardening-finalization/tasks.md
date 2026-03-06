# Tasks

## 1. Planning

- [x] **1.1: 创建 release-hardening-finalization change spec**
  - 固化本轮发布收尾的目标、边界和验收标准。
  - Refs: `release::*`

## 2. Core

- [x] **2.1: 实现发布就绪度评估引擎**
  - 汇总版本一致性、宿主覆盖、关键文档、质量门禁、交付演练等信号。
  - Refs: `release::readiness`

- [x] **2.2: 输出 Markdown / JSON 报告**
  - 让发布就绪度既可供 CLI 阅读，也可供 API / Web 消费。
  - Refs: `release::artifacts`

## 3. Interface

- [x] **3.1: 新增 CLI 发布就绪度命令**
  - 提供终端内可直接查看的 readiness summary。
  - Refs: `release::cli`

- [x] **3.2: 新增 Web API 发布就绪度接口**
  - 让管理台或外部调用方能读取结构化 readiness 数据。
  - Refs: `release::api`

## 4. Documentation & Quality

- [x] **4.1: 更新 README / Workflow 文档**
  - 增加发布前如何执行 readiness 检查的说明。
  - Refs: `release::docs`

- [x] **4.2: 补齐测试并执行全量验证**
  - 包括 CLI、API、核心评估逻辑的回归。
  - Refs: `release::tests`
