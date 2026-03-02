# Super Dev

<div align="center">

# 顶级 AI 开发战队
### God-Tier AI Development Team

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success)](.github/workflows/ci.yml)

[English](README_EN.md) | 简体中文

</div>

---

## 版本

当前版本：`2.0.1`

当前分支质量基线（2026-03-02）：

- `ruff check super_dev tests` 通过
- `mypy super_dev` 通过（56 个源文件）
- `pytest -q` 通过（当前主分支全量测试通过）
- `bandit -ll -r super_dev` 通过（0 medium/high finding）
- `pip-audit .` 通过（0 vulnerability）

---

## 项目定位

`Super Dev` 是一个面向商业级交付的 AI 开发编排工具，核心目标是把「一句话需求」落地成可执行工程资产：

- 需求增强与情报补全
- PRD / 架构 / UIUX / 执行计划文档
- 前端可演示骨架 + 前后端模块实现包（路由/服务/仓储/测试/迁移）
- 红队审查 + 质量门禁（含 Spec 任务完成度）
- 代码审查指南 + AI 提示词
- CI/CD + 部署修复模板 + 数据库迁移脚本 + 交付打包（manifest/report/zip）

---

## 核心能力

### 1) 12 阶段流水线（第 0 到第 11 阶段）

`super-dev pipeline` 当前实际执行链路：

| 阶段 | 内容 |
|:---|:---|
| 第 0 阶段 | 需求增强（本地知识 + 联网检索，可离线） |
| 第 1 阶段 | 生成专业文档（PRD/架构/UIUX/执行路线图/前端蓝图） |
| 第 2 阶段 | 生成前端可演示骨架 |
| 第 3 阶段 | 创建 Spec 规范 |
| 第 4 阶段 | 生成前后端模块实现包（路由/服务/仓储/测试/迁移）并执行 Spec 任务闭环（含自动修复与任务报告） |
| 第 5 阶段 | 红队审查（可跳过） |
| 第 6 阶段 | 质量门禁（可跳过，支持阈值覆盖） |
| 第 7 阶段 | 代码审查指南 |
| 第 8 阶段 | AI 提示词 |
| 第 9 阶段 | CI/CD 配置生成 |
| 第 10 阶段 | 部署修复模板（环境变量/检查清单） |
| 第 11 阶段 | 数据库迁移脚本 + 项目交付包 |

### 2) Spec-Driven Development (SDD)

内置 `.super-dev/specs`、`changes`、`archive` 结构，支持提案、任务拆解、归档和规范更新。

### 3) 专家协作体系

内置 PM / ARCHITECT / UI / UX / SECURITY / CODE / DBA / QA / DEVOPS / RCA 专家角色。

### 4) 设计智能引擎

支持设计搜索、设计系统生成、tokens、Landing 模式、图表推荐、UX 指南、技术栈最佳实践、组件代码生成。

### 5) Web API / Studio

提供 FastAPI 接口和可视化工作台，支持工作流启动、状态查询、配置读取、部署模板导出等能力。

### 6) 跨平台兼容验收

CI 内置 `Platform Compatibility` 门禁，自动验证 Claude Code / Codex CLI / OpenCode / Antigravity / Cursor / Qoder / Trae / CodeBuddy 的 Skill 与规则集成路径。

---

## 安装

### 方式 1：PyPI 安装（推荐）

```bash
pip install -U super-dev
```

PyPI 页面：

- https://pypi.org/project/super-dev/

### 方式 2：安装指定版本（复现/回滚）

```bash
pip install super-dev==2.0.1
```

### 方式 3：GitHub 直装（源码发布分支）

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.1
```

### 方式 4：源码开发安装

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

---

## 快速开始

### 方式 A：需求直达模式（推荐）

```bash
super-dev "构建一个带登录、订单、支付的电商后台"
```

上面这条命令会自动进入完整流水线（需求增强 → 文档 → Spec → 骨架 → 红队 → 质量门禁 → CI/CD → 迁移与交付包）。

### 方式 B：显式 pipeline（高级用法）

```bash
super-dev pipeline "构建一个带登录、订单、支付的电商后台" --platform web --frontend react --backend python --domain ecommerce --cicd github
```

### 常用命令

```bash
# 项目初始化 / 分析
super-dev init my-project
super-dev analyze .

# 核心流水线
super-dev "用户认证系统"
super-dev pipeline "用户认证系统" --platform web --frontend react --backend node --cicd github

# 规范管理
super-dev spec init
super-dev spec list
super-dev spec show <change_id>
super-dev task run <change_id>

# 设计引擎
super-dev design search "glass" --domain style
super-dev design generate --product saas --industry fintech
super-dev design tokens --primary "#3B82F6"

# 质量与部署
super-dev quality --type all
super-dev deploy --cicd github

# API / Studio
super-dev studio --port 8765
```

---

## 场景化使用（0-1 / 1-N+1）

### 0-1：从零创建新项目

适用：只有需求，没有现成工程。

```bash
mkdir new-project && cd new-project
super-dev "做一个企业级任务管理系统，支持登录、RBAC、项目、任务、报表"
```

执行后重点查看：

- `output/*-prd.md`
- `output/*-architecture.md`
- `output/*-uiux.md`
- `.super-dev/changes/*/tasks.md`
- `output/*-task-execution.md`
- `output/*-redteam.md`
- `output/*-quality-gate.md`
- `output/delivery/*-delivery-manifest.json`

### 1-N+1（含 1-1+N）：在已有项目持续迭代

适用：已有项目，按批次持续新增能力模块。

```bash
cd your-existing-project
super-dev analyze .
super-dev spec init
super-dev spec propose add-billing --title "新增计费中心" --description "支持套餐、订阅、账单、发票、支付回调"
super-dev spec add-req add-billing billing subscription "系统 SHALL 支持订阅创建和续费"
super-dev task run add-billing
super-dev quality --type all
```

建议采用“单变更单批次”：

1. 一个 `change_id` 只做一类功能。
2. 每个变更独立通过红队和质量门禁。
3. 通过后再进入下一个变更批次。

### 商业级发布前检查

```bash
./scripts/preflight.sh
```

通过标准：

- 红队审查无阻断（critical = 0）
- 质量门禁总分 `>= 80`
- 交付包状态 `ready`

---

## 预检与发布

发布前建议始终执行：

```bash
./scripts/preflight.sh
```

预检覆盖：`ruff`、`mypy`、`pytest`、`delivery-smoke`、`bandit`、`pip-audit`、benchmark、build、twine check。

发布文档：

- [发布指南](docs/PUBLISHING.md)
- [Release Runbook](docs/RELEASE_RUNBOOK.md)
- [快速开始](docs/QUICKSTART.md)
- [详细使用指南](docs/WORKFLOW_GUIDE.md)

---

## 目录结构（关键）

```text
super_dev/                 # 核心源码
  cli.py                   # CLI 入口
  orchestrator/            # 工作流编排
  creators/                # 文档/提示词/骨架生成
  reviewers/               # 红队与质量门禁
  deployers/               # CI/CD 与迁移脚本生成
  design/                  # 设计智能引擎
  web/                     # FastAPI 服务

output/                    # 生成产物
scripts/                   # 发布与预检脚本
docs/                      # 使用与发布文档
```

---

## 兼容矩阵（当前）

- 平台：`web`, `mobile`, `wechat`, `desktop`
- 前端：`react`, `vue`, `angular`, `svelte`
- 后端：`node`, `python`, `go`, `java`
- 领域：`fintech`, `ecommerce`, `medical`, `social`, `iot`, `education`, `auth`, `content`
- CI/CD：`github`, `gitlab`, `jenkins`, `azure`, `bitbucket`
- ORM/迁移：`Prisma`, `TypeORM`, `Sequelize`, `SQLAlchemy`, `Django`, `Mongoose`

---

## 许可证

MIT License
