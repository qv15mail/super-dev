# Tasks: Architecture Decoupling Foundation

## 1. Spec & Contracts
- [x] 1.1 落盘本次变更 proposal / tasks / spec
- [x] 1.2 建立标准流与 SEEAI 流的正式 workflow contract 模块
- [x] 1.3 让现有代码开始读取 contract，而不是散落硬编码

## 2. Host Registry
- [x] 2.1 建立宿主 registry 基础模块
- [x] 2.2 抽出宿主基础定义：类别、安装模式、触发方式、文档引用
- [x] 2.3 标准化手动宿主与自动宿主边界

## 3. Integration Wiring
- [x] 3.1 让 adapter/profile 输出开始依赖新 registry
- [x] 3.2 让 competition / standard mode 的公开 phase chain 依赖新 contract
- [x] 3.3 给后续 runtime evidence 层预留接口

## 4. Quality
- [x] 4.1 补齐与更新单元/集成测试
- [x] 4.2 执行定向回归验证

## 5. Delivery
- [x] 5.1 记录本轮基础重构范围和兼容策略
- [x] 5.2 标注后续阶段的拆分入口
