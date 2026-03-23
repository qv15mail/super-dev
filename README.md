# Super Dev

<div align="center">

<img src="docs/assets/super-dev-logo.png" alt="Super Dev - AI PIPELINE ORCHESTRATOR" width="600">

### 面向商业级交付的 AI 开发编排工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)

[English](README_EN.md) | 简体中文

</div>

---

## 版本

当前版本：`2.1.1`

---

## 演示视频

<video controls playsinline preload="metadata" src="https://shangyankeji.github.io/super-dev/demo.mp4" width="100%"></video>

- 在线播放：[观看演示视频](https://shangyankeji.github.io/super-dev/demo.mp4)
- 仓库文件：[demo.mp4](demo.mp4)

---

## 加入交流群

<div align="center">

<img src="qun.jpg" alt="微信交流群" width="300">

扫码加入 Super Dev 微信交流群，和开发者一起交流

</div>

---

## 项目介绍

`Super Dev` 是一个面向商业级交付的 AI 开发编排工具，用于把宿主里的模型能力组织成一套稳定、清晰、可审计的工程流水线。

产品定位：

- 宿主负责模型调用、联网搜索、代码产出、终端执行与文件修改
- `Super Dev` 负责流程治理、设计约束、质量门禁、审计产物与交付标准

它解决的是交付过程问题：

- 将需求沉淀为可落地工件：PRD、架构、UI/UX、Spec、任务清单与交付清单
- 将开发过程组织为标准化流水线：可追踪、可恢复、可审计、可复盘
- 将质量控制前置到每个阶段：策略治理、红队审查、质量门禁、发布演练
- 将多宿主协作统一到同一套工程规范：CLI 与 IDE 环境共享同一交付标准

---

## 快速开始

三条命令覆盖所有场景：

```bash
# 0-1 新项目：从需求描述走完整流水线
super-dev "做一个在线教育平台"

# 1-N+1 已有项目：分析现有代码库后接入流水线
super-dev init

# 跳转到任意阶段 / 从中断处继续 / 查看状态
super-dev run frontend       # 按名称跳转
super-dev run 6              # 按编号跳转（1-9）
super-dev run --resume       # 从中断处继续
super-dev run --status       # 查看当前流程状态
```

阶段编号对照：

| 编号 | 阶段 | 说明 |
|------|------|------|
| 1 | research | 同类产品研究 |
| 2 | prd | 产品需求文档 |
| 3 | architecture | 架构设计 |
| 4 | uiux | UI/UX 设计 |
| 5 | spec | 任务规格 |
| 6 | frontend | 前端实现 |
| 7 | backend | 后端实现 |
| 8 | quality | 质量门禁 |
| 9 | delivery | 交付打包 |

辅助命令：

```bash
super-dev onboard             # 宿主接入引导
super-dev onboard --dry-run   # 预览接入变更，不实际写入
super-dev onboard --stable-only  # 仅接入已认证宿主
super-dev doctor              # 诊断检查（显示认证等级）
```

常用交付证据命令：

```bash
super-dev integrate audit --auto --repair --force
super-dev integrate validate --auto
super-dev release proof-pack
super-dev release readiness
super-dev review architecture --status revision_requested --comment "技术方案需要重构"
super-dev review quality --status revision_requested --comment "质量门禁未通过，需要整改"
```

---

## 核心功能

### 1. 10 专家 Agent 架构

v2.1.1 引入 10 个领域专家 Agent，每个专家在对应阶段自动注入到 AI 提示词中，约束宿主按专业标准执行：

| 专家 | 角色 | 注入阶段 |
|------|------|----------|
| PM | 产品经理 | research, prd |
| ARCHITECT | 系统架构师 | architecture |
| UI | 界面设计师 | uiux, frontend |
| UX | 交互设计师 | uiux, frontend |
| SECURITY | 安全工程师 | architecture, backend, quality |
| CODE | 开发工程师 | frontend, backend |
| DBA | 数据库工程师 | architecture, backend |
| QA | 质量工程师 | quality |
| DEVOPS | 运维工程师 | delivery |
| RCA | 根因分析师 | quality, delivery |

每个专家具备：目标定义、背景故事、思维框架、质量标准。生成的 AI 提示词超过 600 行，确保每个阶段的输出符合该领域的专业基线。

### 2. UI 智能设计系统

内置完整的设计智能引擎，直接约束前端实现阶段的视觉质量：

- **119 套配色方案**：84 套产品配色 + 35 套美学配色，全部自动生成暗色模式
- **39 个组件库**：覆盖 11 个前端技术栈（React 15 / Vue 9 / Angular 4 / Svelte 2 / 其他）
- **17 套字体预设**：基于 Google Fonts 中国镜像，按产品调性分类
- **完整 Design Token 体系**：色阶、阴影、动效、排版、间距
- **12 项交付前检查清单**：A11y、响应式、暗色模式、加载态、空态、错误态等
- **10 个行业定制**：教育、医疗、电商、金融科技、SaaS、社交、内容、企业、工具、游戏

UI/UX 文档会自动给出组件生态、表单/表格/图表/动效/图标基线，直接约束实现阶段。宿主提示词与 Skill 会继承这些规则，输出更接近现代商业产品的界面结果。

支持 `super-dev quality --type ui-review` 对 `preview.html` / `output/frontend/index.html` 做结构级视觉审查。

### 3. 流水线编排引擎

- **9 阶段标准流水线**：research -> prd -> architecture -> uiux -> spec -> frontend -> backend -> quality -> delivery
- **检查点与中断续传**：流水线中断后可从断点恢复，不丢失进度
- **阶段超时保护**：每个阶段设有超时机制，防止无限等待
- **确认门控制**：三文档完成后必须等待用户确认，前端预览完成后必须等待用户确认
- **阶段跳转**：`super-dev run <阶段>` 可随时跳转到任意阶段
- **UI 改版回路**：UI 不满意时可发起正式改版回路（`review ui`），先更新 UIUX 文档再重做前端
- **适配 0-1 与 1-N+1**：新建项目走完整流水线，已有项目走增量分析路径

### 4. 文档生成引擎

Super Dev 为每个阶段生成初始文档框架，宿主大模型在此基础上结合用户需求、联网研究和专家知识进行深度完善：

| 文档 | 内容 |
|------|------|
| PRD | 用户画像、功能矩阵、验收标准、竞品对标、商业规则 |
| Architecture | 系统架构、数据模型、接口契约、安全策略、部署方案 |
| UIUX | 设计 Token、页面骨架、组件清单、交互状态、响应式策略 |

宿主根据需求深度生成文档内容，最终产出的文档规模取决于项目复杂度和需求范围。支持 10 个行业领域定制：教育、医疗、电商、金融科技、SaaS、社交、内容、企业、工具、游戏。

补充说明：

- 新功能开发默认走完整流水线：`research -> 三文档 -> 用户确认 -> Spec / tasks -> 前端运行验证 -> 后端 / 测试 / 交付`
- 缺陷修复同样不会直接跳过文档；会走轻量补丁路径，先整理问题现象、复现条件、影响范围和回归风险，再更新补丁文档与验证结果
- 分析阶段默认排除 `.venv`、`site-packages`、`node_modules` 等非项目源码目录

### 5. 质量门禁体系

- **A11y 无障碍检查**：自动验证页面的无障碍标准合规性
- **性能预算校验**：检查资源大小、加载时间等性能指标
- **红队审查**：从安全、性能、架构三个维度对系统进行攻防审查
- **修复命令建议**：检测到问题后直接给出可执行的修复指令
- **策略治理**：default / balanced / enterprise 三级预设
- **Spec 质量评分**：对任务规格进行结构化评分
- **发布就绪面板**：统一展示发布前所有门禁检查结果

### 6. 宿主接入治理

- 支持 20 个主流 CLI/IDE 宿主统一接入（9 CLI + 11 IDE）
- 自动生成宿主规则文件、`/super-dev` 映射、Skill 目录
- `detect / onboard / doctor / setup / install` 形成接入闭环
- 通过宿主能力边界建模，明确哪些宿主是 `Certified / Compatible / Experimental`
- `--dry-run` 预览模式与 `--stable-only` 稳定模式
- `--save-profile` 写入 `super-dev.yaml` 并用于质量门禁

### 7. 代码库理解与变更分析

- **repo-map**：生成代码库地图与建议阅读顺序
- **feature-checklist**：审计 PRD 功能范围覆盖率，区分流程完成与范围完成
- **dependency-graph**：输出模块依赖关系与关键路径
- **impact**：分析改动影响范围、风险等级和建议动作
- **regression-guard**：把影响分析转换成可执行回归清单

### 8. 可审计交付

- `pipeline-metrics` 指标报告
- `pipeline-contract` 阶段契约证据
- `resume-audit` 恢复执行审计
- `delivery manifest/report/archive` 交付包
- `proof-pack` 交付证据汇总与 executive summary
- `release readiness`、`Spec Quality`、`Scope Coverage` 统一发布评分面板

### 9. 知识库系统

Super Dev 内置结构化知识库（`knowledge/` 目录），覆盖 20+ 个技术领域：

- **架构**：微服务、API 网关、分布式事务、配置管理、服务治理
- **安全**：DevSecOps、SAST/DAST/SCA、容器安全、合规自动化、密钥管理
- **运维**：可观测性、AIOps 异常检测、容量规划、混沌工程、SLO/SLI
- **云原生**：容器编排、服务网格、无服务器架构
- **数据工程**：数据管线、流处理、数据治理
- **设计**：UI 全生命周期跨平台手册
- **移动端**：跨平台开发、原生性能优化
- **更多领域**：CI/CD、测试、产品、低代码、边缘/IoT、区块链、量子计算

知识增强机制：

- 宿主进入流水线后，Super Dev 会自动检索 `knowledge/` 下与当前需求相关的知识文件
- 匹配到的本地标准、场景包和检查清单作为硬约束注入到三文档、Spec 和实现阶段
- 如果已生成 `output/knowledge-cache/*-knowledge-bundle.json`，宿主会继承其中的本地知识命中结果
- 同时支持联网研究增强，将 Web 搜索结果与本地知识合并输出

### 10. 策略治理系统

通过 Policy DSL 实现流程治理的参数化控制：

- **default**：标准预设，适合个人和小团队
- **balanced**：平衡预设，适合中等规模团队
- **enterprise**：企业预设，更高质量阈值、宿主画像要求、可按项目配置关键宿主

策略控制维度：

- 强制红队 / 质量门禁开关
- 最低质量阈值设定
- CI/CD 平台白名单
- required hosts 与 ready+score 硬校验（按项目启用）
- 宿主画像自动探测与评分
- `host-compatibility` 报告与历史记录

---

## 安装方式

### 1. uv 安装（推荐）

```bash
uv tool install super-dev
```

升级：

```bash
uv tool upgrade super-dev
super-dev update
```

### 2. PyPI 安装

```bash
pip install -U super-dev
super-dev update
```

安装完成后，直接运行：

```bash
super-dev
```

默认会进入宿主安装引导：

- 顶部显示 `Super Dev` 安装入口
- `↑ / ↓` 选择宿主
- `Space` 勾选宿主
- `Enter` 开始安装
- `A` 全选
- `C` 仅选择 CLI 宿主
- `I` 仅选择 IDE 宿主
- `R` 清空选择
- `U` 升级已安装宿主

安装完成后，终端会直接给出该宿主的最终触发方式：

- slash 宿主：`/super-dev 你的需求`
- 非 slash 宿主：`super-dev: 你的需求`
- 需要真人验收时，可执行：`super-dev integrate validate --target <host>`

### 3. 指定版本安装

```bash
pip install super-dev==2.1.1
```

### 4. GitHub 指定标签安装

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.1.1
```

### 5. 源码开发安装

`uv` 开发环境：

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
uv sync
uv run super-dev --version
```

`pip` 开发环境：

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

---

## 依赖安装说明

当用户执行：

```bash
pip install -U super-dev
```

或：

```bash
uv tool install super-dev
```

安装器会自动安装 `pyproject.toml` 中声明的 Python 依赖，例如：

- `rich`
- `pyyaml`
- `ddgs`
- `requests`
- `beautifulsoup4`
- `fastapi`
- `uvicorn`

不会自动安装的内容：

- Claude Code / Codex CLI / Gemini CLI / Cursor / Trae / Windsurf 等宿主软件本身
- Node.js、npm、pnpm、Docker、数据库服务这类系统级运行环境
- 宿主账号登录状态、联网权限、浏览器能力
- 项目业务依赖以外的前后端运行时

一句话：

- `pip` / `uv` 会自动安装 **Super Dev 自己的 Python 依赖**
- 不会替用户安装 **宿主工具和系统环境**

如果你希望先显式初始化项目契约，再开始接入宿主：

```bash
super-dev bootstrap --name my-project --platform web --frontend next --backend node
```

这会显式生成：

- `.super-dev/WORKFLOW.md`
- `output/*-bootstrap.md`

用来固定初始化规范、触发方式和阶段顺序。

---

## 整个系统如何工作

`Super Dev` 的运行方式可以概括为一条固定链路：

1. 用户在项目目录执行 `super-dev` 或 `super-dev init`
2. 安装引导把 Super Dev 接入到目标宿主
3. 用户在宿主里输入 `/super-dev 需求` 或 `super-dev: 需求`
4. 宿主进入 Super Dev 流水线，10 个专家 Agent 按阶段注入
5. 宿主负责联网、推理、编码、运行与修改文件
6. Super Dev 负责流程、文档、门禁、审计和交付标准

标准流水线：`research -> prd -> architecture -> uiux -> 用户确认 -> spec -> frontend -> 预览确认 -> backend -> quality -> delivery`

补充说明：

- 新功能开发默认走完整流水线：`research -> 三文档 -> 用户确认 -> Spec / tasks -> 前端运行验证 -> 后端 / 测试 / 交付`
- 缺陷修复同样不会直接跳过文档；会走轻量补丁路径，先整理问题现象、复现条件、影响范围和回归风险，再更新补丁文档与验证结果
- 分析阶段默认排除 `.venv`、`site-packages`、`node_modules` 等非项目源码目录

宿主如何理解 Super Dev：

- `Super Dev` 是当前项目里的本地 Python CLI 工具，加上宿主里的规则文件 / Skill / slash 映射
- 宿主负责模型推理、联网搜索、编码、运行终端与修改文件
- `Super Dev` 负责把宿主拉进固定流水线：research、三文档、确认门、Spec、前端优先、后端联调、质量门禁、交付审计
- 当用户输入 `/super-dev 需求` 或 `super-dev: 需求` 时，宿主要切换到 Super Dev 流水线执行模式
- 需要生成或刷新文档、Spec、质量报告、交付产物时，宿主应优先调用本地 `super-dev` CLI
- 如果项目根目录存在 `knowledge/`，宿主必须优先读取与当前需求相关的知识文件
- 如果已生成 `output/knowledge-cache/*-knowledge-bundle.json`，宿主必须把其中命中的本地知识、研究摘要和场景约束继承到三文档、Spec 和实现阶段

---

## 架构概览

### 一、系统高阶流转架构

展示用户、宿主端工具、Super Dev 编排引擎与最终产物之间的流转关系。

![系统高阶流转架构](docs/assets/architecture/system-overview.png)

### 二、9 阶段核心工作流

详细描绘每次对话触发后，引擎在底层的流转经过。

![9 阶段核心工作流](docs/assets/architecture/pipeline-12-phase.png)

### 三、核心模块调用拓扑

展示 `super_dev` 下核心源码目录的职责边界和调用关系。

![核心模块调用拓扑](docs/assets/architecture/module-topology.png)

---

## 20 宿主支持

### CLI 宿主（9 个）

| 宿主 | 触发方式 | 安装命令 |
|------|----------|----------|
| Claude Code | `/super-dev 需求` | `super-dev onboard --host claude-code` |
| Codex CLI | `super-dev: 需求` | `super-dev onboard --host codex-cli` |
| Gemini CLI | `/super-dev 需求` | `super-dev onboard --host gemini-cli` |
| OpenCode | `/super-dev 需求` | `super-dev onboard --host opencode` |
| Kiro CLI | `/super-dev 需求` | `super-dev onboard --host kiro-cli` |
| Cursor CLI | `/super-dev 需求` | `super-dev onboard --host cursor-cli` |
| Qoder CLI | `/super-dev 需求` | `super-dev onboard --host qoder-cli` |
| Copilot CLI | `super-dev: 需求` | `super-dev onboard --host copilot-cli` |
| CodeBuddy CLI | `/super-dev 需求` | `super-dev onboard --host codebuddy-cli` |

### IDE 宿主（11 个）

| 宿主 | 触发方式 | 安装命令 |
|------|----------|----------|
| Antigravity | `/super-dev 需求` | `super-dev onboard --host antigravity` |
| Cursor | `/super-dev 需求` | `super-dev onboard --host cursor` |
| Windsurf | `/super-dev 需求` | `super-dev onboard --host windsurf` |
| Kiro | `super-dev: 需求` | `super-dev onboard --host kiro` |
| Qoder | `/super-dev 需求` | `super-dev onboard --host qoder` |
| Trae | `super-dev: 需求` | `super-dev onboard --host trae` |
| CodeBuddy | `/super-dev 需求` | `super-dev onboard --host codebuddy` |
| Copilot (VS Code) | `super-dev: 需求` | `super-dev onboard --host vscode-copilot` |
| Roo Code | `super-dev: 需求` | `super-dev onboard --host roo-code` |
| Kilo Code | `super-dev: 需求` | `super-dev onboard --host kilo-code` |
| Cline | `super-dev: 需求` | `super-dev onboard --host cline` |

---

### 每个宿主如何使用

#### 1. Claude Code

安装：
```bash
super-dev onboard --host claude-code --force --yes
```

触发位置：
在项目目录启动 Claude Code 当前会话后，直接在同一会话里触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 推荐作为首选 CLI 宿主。
2. 接入后可先执行 `super-dev doctor --host claude-code` 确认 slash 已生效。
3. Claude Code 官方已公开 `.claude/agents/` 与 `~/.claude/agents/`，Super Dev 会同步生成 `super-dev-core` subagent。

#### 2. Codex CLI

安装：
```bash
super-dev onboard --host codex-cli --force --yes
```

触发位置：
在项目目录完成接入后，重启 `codex`，然后在新的 Codex 会话里触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：是

补充说明：
1. Codex CLI 当前使用 `super-dev: 你的需求` 作为主触发方式。
2. 实际依赖 `AGENTS.md` 与官方用户级 Skill `~/.codex/skills/super-dev-core/SKILL.md`。
3. 如果旧会话没加载新 Skill，重启 `codex` 再试。

#### 3. Gemini CLI

安装：
```bash
super-dev onboard --host gemini-cli --force --yes
```

触发位置：
在项目目录启动 Gemini CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 优先在同一会话中完成 research -> 三文档 -> 用户确认 -> Spec -> 前端运行验证 -> 后端/交付。
2. 若宿主支持联网，先让它完成同类产品研究。

#### 4. OpenCode

安装：
```bash
super-dev onboard --host opencode --force --yes
```

触发位置：
在项目目录启动 OpenCode CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 按 CLI slash 模式使用。
2. 若你使用全局命令目录，也建议保留项目级接入文件。

#### 5. Kiro CLI

安装：
```bash
super-dev onboard --host kiro-cli --force --yes
```

触发位置：
在项目目录启动 Kiro CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. CLI 模式下直接使用 slash。
2. 如果项目规则未刷新，重新进入项目目录再启动 Kiro CLI。

#### 6. Cursor CLI

安装：
```bash
super-dev onboard --host cursor-cli --force --yes
```

触发位置：
在项目目录启动 Cursor CLI 当前会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 适合终端内连续执行研究、文档和编码。
2. 若命令列表未刷新，可重开一次 Cursor CLI 会话。

#### 7. Qoder CLI

安装：
```bash
super-dev onboard --host qoder-cli --force --yes
```

触发位置：
在项目目录启动 Qoder CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 适合命令行流水线开发。
2. 若 slash 未生效，先确认 `.qoder/commands/super-dev.md` 已生成。

#### 8. Copilot CLI

安装：
```bash
super-dev onboard --host copilot-cli --force --yes
```

触发位置：
在项目目录启动 Copilot CLI 会话后触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前使用 `super-dev: 你的需求` 作为主触发方式。
2. 建议先用 `super-dev doctor --host copilot-cli` 做一次确认。

#### 9. CodeBuddy CLI

安装：
```bash
super-dev onboard --host codebuddy-cli --force --yes
```

触发位置：
在项目目录启动 CodeBuddy CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 在当前 CLI 会话中直接输入即可。
2. 如果会话已提前打开，建议重新加载项目规则后再试。

#### 10. Antigravity

安装：
```bash
super-dev onboard --host antigravity --force --yes
```

触发位置：
打开 Antigravity 的 Agent Chat / Prompt 面板，并确保当前工作区就是目标项目。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：是

补充说明：
1. Antigravity 当前按 `GEMINI.md + .agent/workflows + /super-dev` 模式接入。
2. 接入会写入项目级 `GEMINI.md`、`.gemini/commands/super-dev.md`、`.agent/workflows/super-dev.md`。
3. 同时会写入用户级 `~/.gemini/GEMINI.md`、`~/.gemini/commands/super-dev.md` 与 `~/.gemini/skills/super-dev-core/SKILL.md`。
4. 完成接入后请重开 Antigravity 或至少新开一个 Agent Chat，再输入 `/super-dev 你的需求`。

#### 11. Cursor

安装：
```bash
super-dev onboard --host cursor --force --yes
```

触发位置：
打开 Cursor 的 Agent Chat，并确保当前工作区就是目标项目。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 建议固定在同一个 Agent Chat 会话里完成整条流水线。
2. 如果项目规则没加载，先重新打开工作区或重新发起聊天。

#### 12. Windsurf

安装：
```bash
super-dev onboard --host windsurf --force --yes
```

触发位置：
打开 Windsurf 的 Agent Chat / Workflow 入口，在项目上下文内触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前按 IDE slash/workflow 模式适配。
2. 更适合在同一个 Workflow 里连续完成研究、文档、Spec 和编码。

#### 13. Kiro

安装：
```bash
super-dev onboard --host kiro --force --yes
```

触发位置：
打开 Kiro IDE 的 Agent Chat / AI 面板，在项目上下文内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. Kiro IDE 当前使用 steering/rules 模式，触发词为 `super-dev: 你的需求`。
2. 接入会写入项目级 `.kiro/steering/super-dev.md`，并补充官方全局 steering `~/.kiro/steering/AGENTS.md`。
3. 如果 steering/rules 未加载，先重开项目窗口。

#### 14. Qoder

安装：
```bash
super-dev onboard --host qoder --force --yes
```

触发位置：
打开 Qoder IDE 的 Agent Chat，在当前项目内触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. Qoder IDE 当前优先使用项目级 commands + rules 模式，直接在 Agent Chat 输入 `/super-dev 你的需求`。
2. 若新增命令未出现，先确认 `.qoder/commands/super-dev.md` 已生成，再重新打开项目或新开一个 Agent Chat。

#### 15. Trae

安装：
```bash
super-dev onboard --host trae --force --yes
```

触发位置：
打开 Trae IDE 的 Agent Chat，在当前项目上下文内直接触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. Trae 当前使用 `super-dev: 你的需求` 作为主触发方式。
2. 接入一定会写入项目级 `.trae/project_rules.md`、`.trae/rules.md` 和用户级 `~/.trae/user_rules.md`、`~/.trae/rules.md`；如果检测到兼容技能目录，也会增强安装 `~/.trae/skills/super-dev-core/SKILL.md`。
3. 完成接入后建议重开 Trae 或至少新开一个 Agent Chat，使规则生效；如果兼容 Skill 已安装，也会一起生效。
4. 随后按 `output/*` 与 `.super-dev/changes/*/tasks.md` 推进开发。

#### 16. CodeBuddy

安装：
```bash
super-dev onboard --host codebuddy --force --yes
```

触发位置：
打开 CodeBuddy IDE 的 Agent Chat，在项目上下文内触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 建议在项目级 Agent Chat 中使用，不要脱离项目上下文。
2. 先让宿主完成 research，再继续文档和编码。
3. 当前按 `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` 接入。

#### 17. Copilot (VS Code)

安装：
```bash
super-dev onboard --host vscode-copilot --force --yes
```

触发位置：
打开 VS Code 的 Copilot Chat 面板，在项目上下文内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前使用 `super-dev: 你的需求` 作为主触发方式，通过项目规则文件驱动流程。
2. 建议先用 `super-dev doctor --host vscode-copilot` 做一次确认。
3. 在同一个 Copilot Chat 会话里完成整条流水线效果最佳。

#### 18. Roo Code

安装：
```bash
super-dev onboard --host roo-code --force --yes
```

触发位置：
打开 Roo Code 的 Agent Chat / AI 面板，在项目上下文内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前使用 `super-dev: 你的需求` 作为主触发方式。
2. 接入会写入项目级规则文件与用户级配置。
3. 建议先用 `super-dev doctor --host roo-code` 做一次确认。

#### 19. Kilo Code

安装：
```bash
super-dev onboard --host kilo-code --force --yes
```

触发位置：
打开 Kilo Code 的 Agent Chat / AI 面板，在项目上下文内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前使用 `super-dev: 你的需求` 作为主触发方式。
2. 接入会写入项目级规则文件与用户级配置。
3. 如果规则未加载，先重开项目窗口或新开一个 Agent Chat。

#### 20. Cline

安装：
```bash
super-dev onboard --host cline --force --yes
```

触发位置：
打开 Cline 的 Agent Chat 面板，在项目上下文内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前使用 `super-dev: 你的需求` 作为主触发方式。
2. 接入会写入项目级 `.clinerules/` 目录下的规则文件。
3. 建议先用 `super-dev doctor --host cline` 做一次确认。
4. 在同一个 Agent Chat 会话里完成整条流水线效果最佳。

---

## 关键文档

- [文档总览](docs/README.md)
- [快速开始](docs/QUICKSTART.md)
- [安装方式](docs/INSTALL_OPTIONS.md)
- [宿主使用指南](docs/HOST_USAGE_GUIDE.md)
- [宿主能力审计](docs/HOST_CAPABILITY_AUDIT.md)
- [宿主运行时验收矩阵](docs/HOST_RUNTIME_VALIDATION.md)
- [宿主接入面说明](docs/HOST_INSTALL_SURFACES.md)
- [工作流指南](docs/WORKFLOW_GUIDE.md)
- [集成指南](docs/INTEGRATION_GUIDE.md)
- [产品审查](docs/PRODUCT_AUDIT.md)

执行原则：

- 宿主负责"写代码"
- `Super Dev` 负责"把开发过程做对、做全、可审计"

---

## 关注我们

<div align="center">

<img src="wechat.png" alt="微信公众号" width="100%">

</div>

---

## License

[MIT](LICENSE)
