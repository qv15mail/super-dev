---
id: prd-generator
name: PRD 文档生成模板
version: "1.0.0"
phase: docs
description: PRD 产品需求文档生成 Prompt 模板，覆盖项目概述、用户故事、功能需求、非功能需求等
variables: [name, description, platform, frontend, backend, domain, knowledge_summary]
author: Super Dev
quality_score: 0
usage_count: 0
created_at: "2026-03-28"
---

# {name} - 产品需求文档 (PRD)

## 项目概述

项目名称: {name}
项目描述: {description}
目标平台: {platform}
所属领域: {domain}

## 技术栈

前端框架: {frontend}
后端框架: {backend}

## 领域知识摘要

{knowledge_summary}

## 生成要求

请根据以上信息生成一份完整的 PRD 文档，包含以下章节:

### 1. 执行摘要
- 项目愿景与目标
- 核心价值主张
- 目标用户群体

### 2. 用户故事与场景
- 主要用户角色定义
- 关键用户故事 (INVEST 标准)
- 用户旅程地图

### 3. 功能需求
- 核心功能 (SHALL/MUST)
- 增强功能 (SHOULD)
- 可选功能 (MAY)
- 功能优先级矩阵

### 4. 非功能需求
- 性能指标 (响应时间/吞吐量/并发)
- 安全要求 (认证/授权/数据保护)
- 可用性目标 (SLA/RTO/RPO)
- 可访问性要求 (WCAG 级别)

### 5. 数据需求
- 核心数据实体
- 数据流向
- 数据保留策略

### 6. 集成需求
- 第三方服务集成
- API 契约概述

### 7. 约束与假设
- 技术约束
- 业务约束
- 关键假设

### 8. 成功指标
- KPI 定义
- 验收标准
