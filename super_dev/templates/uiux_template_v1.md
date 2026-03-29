---
id: uiux-generator
name: UIUX 文档生成模板
version: "1.0.0"
phase: docs
description: UI/UX 设计文档生成 Prompt 模板，覆盖设计系统、页面结构、交互规范、响应式方案等
variables: [name, description, platform, frontend, ui_library, style_solution, domain, knowledge_summary]
author: Super Dev
quality_score: 0
usage_count: 0
created_at: "2026-03-28"
---

# {name} - UI/UX 设计文档

## 项目信息

项目名称: {name}
项目描述: {description}
目标平台: {platform}
所属领域: {domain}

## 技术栈

前端框架: {frontend}
UI 组件库: {ui_library}
样式方案: {style_solution}

## 领域知识摘要

{knowledge_summary}

## 生成要求

请根据以上信息生成一份完整的 UI/UX 设计文档，包含以下章节:

### 1. 设计原则
- 核心设计理念
- 品牌调性与视觉语言
- 可用性优先级

### 2. 设计系统 (Design Tokens)
- 排版系统 (Typography): 字体家族/字号阶梯/行高/字重
- 色彩系统: 主色/辅助色/中性色/语义色/暗色模式
- 间距系统: 基础间距单位/间距阶梯
- 圆角/阴影/边框规范
- 断点定义 (mobile/tablet/desktop/wide)

### 3. 页面层级与信息架构
- 站点地图
- 页面层级结构
- 导航模式
- 面包屑/路由规范

### 4. 核心页面设计
- 每页包含: 布局网格/组件列表/交互说明/状态变化
- 页面之间的跳转关系
- 空状态/加载态/错误态设计

### 5. 组件规范
- 原子组件 (Button/Input/Badge)
- 分子组件 (Form/Card/Modal)
- 有机组件 (Header/Sidebar/Table)
- 组件状态: default/hover/active/disabled/focus/error

### 6. 交互规范
- 动画与过渡 (duration/easing)
- 手势交互 (如移动端)
- 键盘导航
- 焦点管理

### 7. 响应式方案
- 移动端优先策略
- 各断点布局差异
- 触摸目标尺寸

### 8. 可访问性 (Accessibility)
- WCAG 2.1 AA 合规
- 对比度要求
- ARIA 标注规范
- 屏幕阅读器兼容

### 9. 反模式清单
- 禁止: 紫色渐变英雄区
- 禁止: Emoji 作为功能图标
- 禁止: 无层级的纯文字堆砌
- 禁止: 默认字体无排版系统
