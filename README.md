# Super Dev

<div align="center">

# 超级开发战队
### 面向商业级交付的 AI 开发编排工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success)](.github/workflows/ci.yml)

[English](README_EN.md) | 简体中文

</div>

---

## 版本

当前版本：`2.0.2`

---

## 项目介绍

`Super Dev` 是一个面向商业级交付的 AI 开发编排工具，核心目标是辅助用户将项目落地成可执行工程资产：

- 将需求沉淀为可落地工件：PRD、架构、UI/UX、Spec、任务清单与交付清单
- 将开发过程组织为标准化流水线：可追踪、可恢复、可审计、可复盘
- 将质量控制前置到每个阶段：策略治理、红队审查、质量门禁、发布演练
- 将多宿主协作统一到同一套工程规范：CLI 与 IDE 环境共享同一交付标准

---

## 核心功能

### 1. 宿主接入治理

- 支持主流 CLI/IDE 宿主统一接入
- 自动生成宿主规则文件、`/super-dev` 映射、Skill 目录
- `detect/onboard/doctor/setup/install` 形成接入闭环

### 2. 流水线式开发编排（0-12 阶段）

- 需求增强 -> 文档 -> Spec -> 实现骨架 -> 红队 -> 质量门禁 -> 交付
- 全流程可恢复执行（`run --resume`）
- 适配 0-1 新建与 1-N+1 增量场景

### 3. 策略治理（Policy DSL）

- `default / balanced / enterprise` 预设
- 强制红队/质量门禁
- 最低质量阈值、CI/CD 白名单
- required hosts 与 ready+score 硬校验

### 4. 宿主画像与兼容性门禁

- 自动探测宿主并评分
- 输出 `host-compatibility` 报告与历史
- `--save-profile` 写入 `super-dev.yaml` 并用于质量门禁

### 5. 可审计交付

- `pipeline-metrics` 指标报告
- `pipeline-contract` 阶段契约证据
- `resume-audit` 恢复执行审计
- `delivery manifest/report/archive` 交付包

### 6. 商业级门禁链路

- 红队审查（安全/性能/架构）
- 质量门禁（场景阈值与策略阈值）
- 发布演练与回滚预案

---

## 安装方式

### 1. PyPI 安装（推荐）

```bash
pip install -U super-dev
```

### 2. 指定版本安装

```bash
pip install super-dev==2.0.2
```

### 3. GitHub 指定标签安装

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.2
```

### 4. 源码开发安装

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

---

## 最简单使用（给最终用户）

### CLI 宿主（Claude Code / Codex CLI / Gemini CLI / Kimi CLI / Kiro CLI / Qoder CLI）

1. 进入项目目录执行 `super-dev` 完成接入。  
2. 在宿主会话里直接输入：`/super-dev 你的需求`。

### IDE 宿主（Qoder）

1. 进入项目目录执行 `super-dev` 完成接入。  
2. 在 IDE Agent Chat 里先试：`/super-dev 你的需求`。  
3. 如果该 IDE 当前不支持 slash 命令，改用：
   `super-dev "你的需求"`（终端编排）+ 在 IDE Chat 按 `output/*` 与 `tasks.md` 执行实现。

---

## 快速开始（详细使用说明）

### 1. 安装后直接进入引导

```bash
super-dev
```

`super-dev` 无参数默认进入安装引导，可多选宿主。

### 2. 非交互一键安装（CI/脚本友好）

自动探测本机宿主并安装：

```bash
super-dev install --auto --force --yes
```

安装全部宿主：

```bash
super-dev install --all --force --yes
```

### 3. 建立宿主画像

```bash
super-dev detect --auto --save-profile
```

这一步会生成兼容性报告并写入 `super-dev.yaml`：

- `host_profile_targets`
- `host_profile_enforce_selected=true`

### 4. 初始化企业策略（推荐）

```bash
super-dev policy init --preset enterprise --force
super-dev policy show
```

### 5. 启动流水线开发

```bash
super-dev "构建一个企业级 CRM，支持登录、RBAC、客户、商机、报表"
```

或显式模式：

```bash
super-dev pipeline "构建一个企业级 CRM" --platform web --frontend react --backend python --cicd github
```

默认启用宿主硬门禁：如果没有 `ready` 宿主，流水线会直接阻断并提示先完成接入。

### 6. 查看关键产物

运行后重点看 `output/`：

- `*-prd.md`
- `*-architecture.md`
- `*-uiux.md`
- `*-redteam.md`
- `*-quality-gate.md`
- `*-pipeline-metrics.json`
- `*-pipeline-contract.json`
- `delivery/*-delivery-manifest.json`
- `rehearsal/*-rehearsal-report.md`

### 7. 在宿主里直接触发

支持 slash 命令映射的宿主可直接输入：

```text
/super-dev 你的需求
```

若宿主不支持 slash 命令映射，可在同一项目根目录执行终端入口（仅触发 Super Dev 本地流水线编排）：

```bash
super-dev "你的需求"
```

- 终端入口不会直接调用宿主模型会话
- 代码生成与修改仍在已接入的宿主工具中完成

---

## 使用场景

## 1. 从 0-1（新项目）

适用：你只有需求，没有现成工程。

### 推荐流程

1. 新建目录并安装接入
2. 执行 `detect --save-profile`
3. 初始化 `enterprise` 策略
4. 运行需求直达流水线
5. 依据 `tasks.md` 推进实现和联调
6. 完成红队、质量门禁、发布演练后交付

### 示例

```bash
mkdir crm-project && cd crm-project
pip install -U super-dev
super-dev
super-dev detect --auto --save-profile
super-dev policy init --preset enterprise --force
super-dev "做一个企业级 CRM，支持多租户、RBAC、线索、客户、商机、报表"
```

---

## 2. 从 1-N+1（存量项目增量迭代）

适用：已有项目，持续增加业务能力模块。

### 推荐流程

1. 先分析现有代码与技术栈
2. 建立 Spec 变更
3. 按任务闭环执行
4. 每个变更独立通过红队与质量门禁
5. 小批次合并与发布

### 示例

```bash
cd existing-project
super-dev analyze .
super-dev spec init
super-dev spec propose add-billing --title "新增计费中心" --description "支持套餐、订阅、账单、支付回调"
super-dev task run add-billing
super-dev quality --type all
```

---

## 支持的宿主

### CLI 宿主

- `claude-code`
- `codex-cli`
- `gemini-cli`
- `kimi-cli`
- `kiro-cli`
- `qoder-cli`

### IDE / 扩展宿主

- `qoder`

### 宿主适配方式（CLI/IDE）

- `CLI 宿主`：在宿主会话内触发 `/super-dev`，由宿主模型执行编码
- `IDE 宿主`：在 Agent Chat 触发 `/super-dev`，由规则文件与 Skill 约束执行流程
- `终端入口`：`super-dev "需求"` 仅触发本地流水线编排，不直接调用宿主模型会话

查看宿主适配矩阵（官方文档链接、适配模式、注入路径、探测策略）：

```bash
super-dev integrate matrix
super-dev integrate matrix --json
```

---

## 常用命令速查

```bash
# 安装接入
super-dev
super-dev install --auto --force --yes
super-dev detect --auto --save-profile
super-dev doctor --auto --repair --force
super-dev integrate matrix --target codex-cli

# 流水线开发
super-dev "你的需求"
super-dev pipeline "你的需求" --platform web --frontend react --backend python --cicd github
super-dev run --resume

# 策略治理
super-dev policy presets
super-dev policy init --preset enterprise --force
super-dev policy show

# 规范任务
super-dev spec init
super-dev spec list
super-dev task run <change_id>

# 质量与交付
super-dev quality --type all
super-dev metrics --history --limit 20
super-dev deploy --cicd all --rehearsal --rehearsal-verify
```

---

## 发布前检查

```bash
./scripts/preflight.sh
```

---

## 相关文档

- [详细工作流指南](docs/WORKFLOW_GUIDE.md)
- [快速开始](docs/QUICKSTART.md)
- [发布指南](docs/PUBLISHING.md)
- [安装方式说明](docs/INSTALL_OPTIONS.md)

---

## 微信公众号

![Super Dev 微信公众号](wechat.png)

---

## License

MIT
