---
id: architecture-generator
name: 架构文档生成模板
version: "1.0.0"
phase: docs
description: 架构设计文档生成 Prompt 模板，覆盖系统架构、技术选型、部署架构、安全架构等
variables: [name, description, platform, frontend, backend, database, deployment, domain, knowledge_summary]
author: Super Dev
quality_score: 0
usage_count: 0
created_at: "2026-03-28"
---

# {name} - 架构设计文档

## 项目信息

项目名称: {name}
项目描述: {description}
目标平台: {platform}
所属领域: {domain}

## 技术栈

前端框架: {frontend}
后端框架: {backend}
数据库: {database}
部署方式: {deployment}

## 领域知识摘要

{knowledge_summary}

## 生成要求

请根据以上信息生成一份完整的架构设计文档，包含以下章节:

### 1. 架构概述
- 架构风格 (微服务/单体/混合)
- 设计原则
- 系统边界与上下文图

### 2. 逻辑架构
- 分层架构图
- 核心模块划分
- 模块间依赖关系
- 领域模型

### 3. 技术选型与 ADR
- 各技术栈选型理由
- 关键架构决策记录 (ADR)
- 技术风险评估

### 4. 数据架构
- 数据库 Schema 设计
- 缓存策略
- 数据迁移方案
- 数据备份与恢复

### 5. 接口架构
- API 设计规范 (RESTful/GraphQL)
- 接口版本化策略
- 错误处理规范
- 认证与鉴权流程

### 6. 部署架构
- 部署拓扑图
- 容器化策略
- CI/CD 流水线
- 环境管理 (dev/staging/prod)

### 7. 安全架构
- 威胁模型
- 安全控制措施
- 数据加密方案
- 审计日志

### 8. 可观测性
- 日志规范
- 监控指标
- 告警策略
- 链路追踪

### 9. 扩展性设计
- 水平扩展方案
- 性能瓶颈预判
- 容量规划

### 10. 灾备与高可用
- 高可用方案
- 故障恢复流程
- SLA 目标
