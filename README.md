# Super Dev

<div align="center">

<img src="docs/assets/super-dev-logo.png" alt="Super Dev - AI PIPELINE ORCHESTRATOR" width="600">

### 面向商业级交付的 AI 开发编排工具 · 知识驱动 · 可编程治理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Lint](https://img.shields.io/badge/lint-ruff-success)](https://docs.astral.sh/ruff/)

[English](README_EN.md) | 简体中文

</div>

---

## 版本

当前版本：`2.3.2`

- 发布说明：[v2.3.2 更新内容](docs/releases/2.3.2.md)
- 官网更新历史：[superdev.goder.ai/changelog](https://superdev.goder.ai/changelog)

---

## 演示视频

<video controls playsinline preload="metadata" src="https://shangyankeji.github.io/super-dev/demo.mp4" width="100%"></video>

- 在线播放：[观看演示视频](https://shangyankeji.github.io/super-dev/demo.mp4)
- 仓库文件：[demo.mp4](demo.mp4)

---

## 联系开发者

<div align="center">

微信号：**Excellent_We**

<img src="wx.png" alt="开发者微信" width="200">

扫码或搜索微信号联系开发者

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
- 将知识库与验证规则自动推送到每个阶段：知识驱动治理，而非依赖人工检查

---

## 快速开始

先记住这 5 个入口，其中旧的直达写法仍然保留：

```bash
# 安装引导 / 已有项目下一步
super-dev

# 旧写法仍可用：直接从需求描述进入完整流水线
super-dev "做一个在线教育平台"

# 0-1：为当前机器选择宿主并给出第一句触发词
super-dev start --idea "做一个在线教育平台"

# 第二天回来 / 重开宿主：恢复当前流程
super-dev resume

# 已有流程：继续当前流程，而不是重新开始普通聊天
super-dev continue

# 状态不清楚时：只问系统“下一步”
super-dev next
```

使用方式：

- 当前目录还没接入时，裸跑 `super-dev` 会进入安装引导。
- 当前目录已经有 Super Dev 上下文时，裸跑 `super-dev` 会直接进入“恢复当前流程”路由。
- `super-dev "..."` 仍然是直达完整流水线的快捷入口，适合你已经明确要让 Super Dev 直接开工的场景。
- `super-dev start --idea "..."` 会自动检测宿主、给出推荐宿主、触发词、重开提示和第一句该发什么。
- `super-dev resume` 最适合下班回来、第二天继续、重开电脑、重开宿主后的真实恢复场景。
- `super-dev continue` / `super-dev next` 会直接告诉你当前动作、用户下一步、宿主第一句、机器侧动作。

现实场景怎么继续：

| 场景 | 先做什么 | 为什么 |
|------|----------|--------|
| 下班了，第二天回来继续开发 | `super-dev resume` | 直接恢复当前流程、当前动作、宿主第一句和机器侧下一步 |
| 宿主关了、电脑重启了、会话断了 | `super-dev resume` | 重新生成恢复卡，并提醒先看 `.super-dev/SESSION_BRIEF.md` |
| 只是不知道现在卡在哪一步 | `super-dev next` | 只输出当前仓库唯一推荐的下一步 |
| 流水线命令跑到一半被打断 | `super-dev run --resume` | 从上次中断阶段继续执行机器侧流水线 |
| 当前在确认门，想继续补 PRD / 架构 / UI | `super-dev resume` 后按提示继续说自然语言 | 会继续留在当前确认门，而不是开启普通聊天 |
| 明确要返工 UI | 先更新 `output/*-uiux.md`，再 `super-dev resume` | 先改 UI 真源，再让后续前端实现沿同一套 UI 契约继续 |
| 明确要返工架构 | 先更新 `output/*-architecture.md`，再 `super-dev resume` | 先改技术真源，再让 Spec / 实现重新对齐 |
| 只想离开当前流程，重新聊别的 | 明确说“取消当前流程”或“重新开始一条新流程” | 系统只在你明确退出时才离开当前 Super Dev 流程 |

如果你已经明确知道要从哪里接着做，再用这些命令：

```bash
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
super-dev detect              # 自动检测宿主与推荐默认宿主
super-dev detect --auto       # 自动检测并安装到所有宿主
super-dev doctor              # 诊断检查（显示认证等级、主修复动作和下一步）
```

快速接入（推荐）：

```bash
super-dev init my-project
super-dev init --template ecommerce   # 使用项目模板 (ecommerce/saas/dashboard/mobile/api/blog/miniapp)
super-dev detect --auto               # 自动检测并安装到所有宿主
# 然后按宿主模型触发: Claude 用 /super-dev，Codex App/Desktop 用 / 列表里的 super-dev，Codex CLI 用 $super-dev，其他非 slash 宿主用 super-dev:
```

治理与知识命令（2.2.0 新增）：

```bash
super-dev governance                  # 治理规则总览
super-dev spec trace                  # Spec-Code 追踪
super-dev spec consistency            # Spec-Code 一致性检测
super-dev spec acceptance             # Spec 验收检查
super-dev knowledge stats             # 知识库使用统计
super-dev knowledge evolve            # 知识权重自演化
```

治理与执行命令（2.3.0 新增）：

| 命令 | 功能 |
|------|------|
| `super-dev enforce install` | 安装宿主 hooks (emoji 检查等) |
| `super-dev enforce validate` | 运行约束验证脚本 |
| `super-dev enforce status` | 查看 enforcement 配置状态 |
| `super-dev memory list` | 查看项目记忆 |
| `super-dev memory consolidate` | 触发记忆整合 |
| `super-dev hooks list` | 查看已配置的 hooks |
| `super-dev hooks history` | 查看最近 hook 执行历史 |
| `super-dev harness status` | 汇总查看 workflow / framework / hook harness 状态，并显示最近关键时间线 |
| `super-dev harness operational` | 查看统一 operational harness 报告，并直接给出当前治理焦点与建议先做 |
| `super-dev harness timeline` | 查看 workflow 快照、语义事件与 hook 事件合并后的统一时间线 |
| `super-dev experts list` | 查看可用专家 |
| `super-dev compact list` | 查看上下文压缩摘要 |
| `super-dev generate scaffold` | 生成项目脚手架 |
| `super-dev generate components` | 生成 UI 组件 |
| `super-dev generate types` | 生成前后端共享类型 |

常用交付证据命令：

```bash
super-dev integrate audit --auto --repair --force
super-dev integrate validate --auto
super-dev feature-checklist
super-dev product-audit
super-dev release proof-pack
super-dev release readiness
super-dev review preview --status confirmed --comment "前端预览已确认"
super-dev review architecture --status revision_requested --comment "技术方案需要重构"
super-dev review quality --status revision_requested --comment "质量门禁未通过，需要整改"
```

---

## 核心功能

### 1. 11 专家 Agent 架构

当前内置 11 个领域专家 Agent，每个专家在对应阶段自动注入到 AI 提示词中，约束宿主按专业标准执行：

| 专家 | 角色 | 注入阶段 |
|------|------|----------|
| PRODUCT | 产品负责人 | research, prd, quality, delivery |
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

每个专家具备四层武装：Profile（目标定义、背景故事、思维框架、质量标准）+ Knowledge（阶段知识自动推送）+ Rules（验证规则绑定）+ Protocol（交叉审查协议）。每位专家配备 350+ 行深度 Playbook 操作手册，生成的 AI 提示词超过 600 行，确保每个阶段的输出符合该领域的专业基线。

### 2. UI 智能设计系统

内置完整的设计智能引擎，直接约束前端实现阶段的视觉质量：

- **119 套配色方案**：84 套产品配色 + 35 套美学配色，全部自动生成暗色模式
- **39 个组件库**：覆盖 11 个前端技术栈（React 15 / Vue 9 / Angular 4 / Svelte 2 / 其他）
- **17 套字体预设**：基于 Google Fonts 中国镜像，按产品调性分类
- **完整 Design Token 体系**：色阶、阴影、动效、排版、间距
- **12 项交付前检查清单**：A11y、响应式、暗色模式、加载态、空态、错误态等
- **10 个行业定制**：教育、医疗、电商、金融科技、SaaS、社交、内容、企业、工具、游戏

UI/UX 文档不再只是建议，而是会冻结成一份真正的 UI 契约：

- `output/*-uiux.md`
- `output/*-ui-contract.json`
- `output/frontend/design-tokens.css`
- `output/*-ui-contract-alignment.md`
- `output/*-ui-contract-alignment.json`

宿主提示词、前端骨架、后续实现、UI review、frontend runtime、quality gate、proof-pack、release readiness 都会围绕这份 UI 契约继续执行。

支持：

- `super-dev quality --type ui-review`
- `super-dev integrate validate --target <host_id>`
- `super-dev release proof-pack`

来持续检查 UI 契约有没有真的落到源码和交付结果中。

### 3. 流水线编排引擎

- **9 阶段标准流水线**：research -> prd -> architecture -> uiux -> spec -> frontend -> backend -> quality -> delivery
- **检查点与中断续传**：流水线中断后可从断点恢复，不丢失进度
- **阶段超时保护**：每个阶段设有超时机制，防止无限等待
- **确认门控制**：三文档完成后必须等待用户确认，前端预览完成后必须等待用户确认
- **阶段跳转**：`super-dev run <阶段>` 可随时跳转到任意阶段
- **UI 改版回路**：UI 不满意时可发起正式改版回路（`review ui`），先更新 UIUX 文档再重做前端
- **适配 0-1 与 1-N+1**：新建项目走完整流水线，已有项目走增量分析路径
- **继续当前流程路由**：`super-dev resume` / `super-dev continue` / `super-dev next` / `start --json` / `doctor --json` 都共享同一套 workflow state 与 action card
- **恢复状态卡**：`.super-dev/SESSION_BRIEF.md` 和 `.super-dev/workflow-state.json` 会沉淀“当前动作 / 宿主第一句 / 机器侧动作 / 连续性规则”
- **关键时间线**：流程快照、语义事件、Hook 事件会汇总成统一的 recent timeline，进入 `SESSION_BRIEF`、Workflow Harness、proof-pack 与 release readiness
- **返工优先级**：文档确认门、预览确认门、UI 改版、架构返工、质量整改都进入统一状态机，不再靠用户记命令

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

- **验证规则引擎**：25 条 YAML 声明式规则（14 默认 + 11 红队），支持项目级自定义覆盖
- **质量顾问**：不只说"不达标"，还给出具体修复建议（Quick Wins 优先排序）
- **Spec-Code 一致性检测**：自动比对 Spec 描述与实际代码实现，防止偏离
- **A11y 无障碍检查**：自动验证页面的无障碍标准合规性
- **性能预算校验**：检查资源大小、加载时间等性能指标
- **红队审查**：从安全、性能、架构三个维度对系统进行攻防审查
- **修复命令建议**：检测到问题后直接给出可执行的修复指令
- **策略治理**：default / balanced / enterprise 三级预设
- **Spec 质量评分**：对任务规格进行结构化评分
- **发布就绪面板**：统一展示发布前所有门禁检查结果
- **UI 契约执行检查**：质量门禁会检查 `ui-contract.json`、`design-tokens.css`、frontend runtime 与 UI 对齐报告是否一致

### 6. 宿主接入治理

- 支持 25+ 个主流 CLI/IDE 宿主统一接入（9 CLI + 11 IDE + 扩展宿主）
- OpenClaw 作为原生插件宿主单独接入，用户自行执行 `openclaw plugins install @super-dev/openclaw-plugin`
- 自动生成宿主规则文件、`/super-dev` 映射、Skill 目录
- `detect / onboard / doctor / setup / install / start` 形成接入闭环
- 通过宿主能力边界建模，明确哪些宿主是 `Certified / Compatible / Experimental`
- `--dry-run` 预览模式与 `--stable-only` 稳定模式
- `--save-profile` 写入 `super-dev.yaml` 并用于质量门禁
- `doctor`、`detect`、`start` 默认会输出决策卡：推荐宿主、推荐理由、第一步动作、候选宿主、路径覆盖修复提示
- 支持 Windows 注册信息、shim 目录、常见路径和 `SUPER_DEV_HOST_PATH_<HOST>` 自定义路径覆盖
- 显式指定宿主时，系统会围绕你指定的宿主给建议，不再被自动检测结果带偏

### 7. 代码库理解与变更分析

- **repo-map**：生成代码库地图与建议阅读顺序
- **feature-checklist**：审计 PRD 功能范围覆盖率，区分流程完成与范围完成
- **dependency-graph**：输出模块依赖关系与关键路径
- **impact**：分析改动影响范围、风险等级和建议动作
- **regression-guard**：把影响分析转换成可执行回归清单

### 8. 可审计交付

- `pipeline-metrics` 指标报告（2.2.0 新增 DORA 五指标 + Rework Rate）
- `pipeline-contract` 阶段契约证据
- `resume-audit` 恢复执行审计
- `delivery manifest/report/archive` 交付包
- `proof-pack` 交付证据汇总与 executive summary
- `release readiness`、`Spec Quality`、`Scope Coverage` 统一发布评分面板
- `UI Contract Alignment` 进入 proof-pack 与 release readiness，不再只是 UI review 内部提示
- `ADR 自动生成`：架构决策自动记录到交付证据中（2.2.0 新增）
- `Spec-Code Consistency Report`：一致性检测报告进入交付闭环（2.2.0 新增）
- `resume-audit`、`pipeline-contract`、治理快照、frontend runtime、knowledge tracking、validation report 会一起进入交付闭环

### 9. 知识库系统

Super Dev 内置结构化知识库（`knowledge/` 目录），270+ 个知识文件、15 万行深度内容，覆盖 23 个技术领域：

- **架构**：微服务、API 网关、分布式事务、配置管理、服务治理
- **安全**：DevSecOps、SAST/DAST/SCA、容器安全、合规自动化、密钥管理
- **运维**：可观测性、AIOps 异常检测、容量规划、混沌工程、SLO/SLI
- **云原生**：容器编排、服务网格、无服务器架构
- **数据工程**：数据管线、流处理、数据治理
- **设计**：UI 全生命周期跨平台手册
- **移动端**：跨平台开发、原生性能优化
- **更多领域**：CI/CD、测试、产品、低代码、边缘/IoT、区块链、量子计算

知识推送引擎（2.2.0 新增）：

- **阶段精准映射**：306 个知识文件建立索引，7 个 pipeline 阶段精准推送相关约束
- **渐进式加载**：L1 索引（目录级快速匹配）/ L2 详情（文件级内容推送）/ L3 深度引用（段落级精准引用），token 预算控制
- **知识自演化**：SQLite 追踪每条知识的使用效果（采纳率、命中率），数据驱动权重优化
- 宿主进入流水线后，Super Dev 会自动检索 `knowledge/` 下与当前需求相关的知识文件
- 匹配到的本地标准、场景包和检查清单作为硬约束注入到三文档、Spec 和实现阶段
- 如果已生成 `output/knowledge-cache/*-knowledge-bundle.json`，宿主会继承其中的本地知识命中结果
- 同时支持联网研究增强，将 Web 搜索结果与本地知识合并输出

### 10. 策略治理系统

通过 Policy DSL 和 YAML 声明式验证规则引擎实现流程治理的可编程控制：

- **default**：标准预设，适合个人和小团队
- **balanced**：平衡预设，适合中等规模团队
- **enterprise**：企业预设，更高质量阈值、宿主画像要求、可按项目配置关键宿主

策略控制维度：

- 25 条 YAML 声明式验证规则（14 默认 + 11 红队），支持项目级自定义覆盖
- 强制红队 / 质量门禁开关
- 最低质量阈值设定
- CI/CD 平台白名单
- required hosts 与 ready+score 硬校验（按项目启用）
- 宿主画像自动探测与评分
- `host-compatibility` 报告与历史记录
- Pipeline 效能度量（DORA 五指标 + Rework Rate）
- Prompt 模板版本化，文档生成 Prompt 可迭代优化

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
pip install super-dev==2.3.2
```

### 4. GitHub 指定标签安装

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.3.2
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

## 2.2.0 新功能亮点

### 知识驱动治理

- **知识推送引擎** — 每个 pipeline 阶段自动推送相关知识约束（306 个知识文件索引，7 阶段精准映射）
- **渐进式加载** — L1 索引 / L2 详情 / L3 深度引用，token 预算控制
- **知识自演化** — SQLite 追踪使用效果，数据驱动权重优化
- **270+ 知识文件** — 覆盖 23 个技术领域，15 万行深度内容

### 可编程治理

- **验证规则引擎** — 25 条 YAML 声明式规则（14 默认 + 11 红队），支持项目级自定义
- **质量顾问** — 不只说"不达标"，还给出具体修复建议（Quick Wins 优先）
- **Spec-Code 一致性检测** — 防止代码偏离 Spec 描述

### 专家系统升级

- **四层武装** — Profile + Knowledge + Rules + Protocol
- **11 个深度 Playbook** — 每个专家 350+ 行操作手册
- **交叉审查引擎** — 多专家视角自动审查交付物

### 效能度量

- **Pipeline 效能度量** — DORA 五指标 + Rework Rate
- **ADR 自动生成** — 架构决策自动记录
- **Prompt 模板版本化** — 文档生成 Prompt 可迭代优化

### OpenClaw 深度适配

- **20 个 Plugin Tool** — 覆盖全部核心命令
- **精简 SKILL.md** — 145 行引导，聚焦"调哪个 Tool"

---

## 2.3.0 新增能力

- **Enforcement 系统**: 自动配置宿主 hooks，实现编码时实时约束检查
- **编码前门禁**: 7 步强制确认（技术栈预研→配置→图标→组件→API→token→构建）
- **技术栈预研**: 通用机制，编码前强制读取 package.json 并查阅官方文档
- **知识库驱动**: 技术栈规则从 knowledge/ 文件动态加载，不写死在代码中
- **记忆系统**: 4 种记忆类型 (user/feedback/project/reference) + 自动提取
- **组件脚手架**: 生成可直接使用的 Button/Card/Input/Modal/Nav/Layout
- **API 契约生成**: 从架构文档生成前后端共享 TypeScript 类型
- **对抗性验证**: 独立验证专家，尝试打破实现而非确认有效
- **三 Agent 审查**: 复用 + 质量 + 效率 + 安全并行审查
- **Pipeline 品牌输出**: 每个阶段显示进度标识
- **Pipeline 状态文件**: 每阶段自动写入 `.super-dev/pipeline-state.json`，宿主可读取当前进度
- **Pipeline 成本追踪**: 每阶段耗时/文件数记录到 `.super-dev/metrics/pipeline-cost.json`，异常中断也会保存
- **状态变更事件系统**: phase_started / phase_completed / phase_failed / pipeline_completed 自动触发 SessionBrief 更新
- **CLAUDE.md 知识引用**: 生成的项目根 `CLAUDE.md` 与兼容 `.claude/CLAUDE.md` 会自动包含 `@./knowledge/...` 引用，宿主原生加载技术栈知识
- **条件规则系统**: `.super-dev/rules/*.md` 条件规则，支持 frontmatter `paths` 过滤和排除模式
- **项目模板**: `super-dev init --template ecommerce/saas/dashboard/mobile/api/blog/miniapp`
- **首次使用引导**: 3 步快速开始面板，最多显示 4 次后自动隐藏
- **Tips 提示系统**: 根据当前阶段显示上下文相关的操作建议
- **Shell 补全**: `super-dev completion bash/zsh/fish`
- **版本更新检查**: PyPI 24h 缓存，有新版时提示升级
- **`doctor --fix`**: 自动修复检测到的安装问题
- **`super-dev feedback`**: 快速打开 GitHub Issues 反馈
- **`super-dev migrate`**: 2.2.0 → 2.3.0 一键迁移
- **验证脚本增强**: 多级输出 (Level 1 阻塞 / Level 2 警告 / Level 3 建议)，新增 console.log / localhost / TODO 检查

---

## 整个系统如何工作

`Super Dev` 的运行方式可以概括为一条固定链路：

1. 用户在项目目录执行 `super-dev` 或 `super-dev init`
2. 安装引导把 Super Dev 接入到目标宿主
3. 用户在宿主里输入 `/super-dev 需求` 或 `super-dev: 需求`
4. 宿主进入 Super Dev 流水线，11 个专家 Agent 按阶段注入，知识推送引擎自动推送相关约束
5. 宿主负责联网、推理、编码、运行与修改文件
6. Super Dev 负责流程、文档、知识推送、验证规则、门禁、审计和交付标准

标准流水线：`research -> prd -> architecture -> uiux -> 用户确认 -> spec -> frontend -> 预览确认 -> backend -> quality -> delivery`

补充说明：

- 新功能开发默认走完整流水线：`research -> 三文档 -> 用户确认 -> Spec / tasks -> 前端运行验证 -> 后端 / 测试 / 交付`
- 缺陷修复同样不会直接跳过文档；会走轻量补丁路径，先整理问题现象、复现条件、影响范围和回归风险，再更新补丁文档与验证结果
- 分析阶段默认排除 `.venv`、`site-packages`、`node_modules` 等非项目源码目录

宿主如何理解 Super Dev：

- `Super Dev` 是当前项目里的本地 Python CLI 工具，加上宿主里的规则文件 / Skill / slash 映射
- 宿主负责模型推理、联网搜索、编码、运行终端与修改文件
- `Super Dev` 负责把宿主拉进固定流水线：research、三文档、确认门、Spec、前端优先、后端联调、质量门禁、交付审计，并在每个阶段自动推送相关知识约束与验证规则
- 当用户输入 `/super-dev 需求` 或 `super-dev: 需求` 时，宿主要切换到 Super Dev 流水线执行模式
- 需要生成或刷新文档、Spec、质量报告、交付产物时，宿主应优先调用本地 `super-dev` CLI
- 如果项目根目录存在 `knowledge/`，宿主必须优先读取与当前需求相关的知识文件
- 如果已生成 `output/knowledge-cache/*-knowledge-bundle.json`，宿主必须把其中命中的本地知识、研究摘要和场景约束继承到三文档、Spec 和实现阶段

---

## 架构概览

Super Dev 2.3.2 架构由四层组成：**宿主接入层**（20 个统一接入宿主 + 1 个 OpenClaw 手动插件宿主）、**知识治理层**（306 索引 / 渐进式加载 / 自演化）、**编排引擎层**（9 阶段流水线 / 11 专家 / 验证规则引擎）、**交付审计层**（DORA 度量 / ADR / 一致性检测 / proof-pack）。

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

## 20 个统一接入宿主 + 1 个手动插件宿主

正式产品口径：

- `20` 个统一接入宿主
- `OpenClaw` 单独作为原生插件宿主，走 npm / plugin 安装，不走统一 `onboard`

### 统一 CLI 宿主（9 个）

| 宿主 | 触发方式 | 安装命令 |
|------|----------|----------|
| Claude Code | `/super-dev 需求` | `super-dev onboard --host claude-code` |
| Codex | App/Desktop: `/super-dev`（skill 入口） / CLI: `$super-dev` / 回退: `super-dev: 需求` | `super-dev onboard --host codex-cli` |
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
| Kiro | `/super-dev 需求` | `super-dev onboard --host kiro` |
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
2. 接入后可先执行 `super-dev doctor --host claude-code`，确认项目根 `CLAUDE.md`、项目级 `.claude/skills/super-dev/`、用户级 `~/.claude/skills/`、兼容 slash 与可选 plugin enhancement 一起生效。
3. Claude Code 当前按 skills-first 收敛：主面是 `CLAUDE.md + .claude/skills + ~/.claude/skills`，`.claude/commands/` 与 `.claude/agents/` 仅作为兼容增强面保留。
4. 如需增强层，Super Dev 还会补齐 `.claude-plugin/marketplace.json` 与 `plugins/super-dev-claude/.claude-plugin/plugin.json`。

#### 2. Codex

安装：
```bash
super-dev onboard --host codex-cli --force --yes
```

触发位置：
在项目目录完成接入后，重启 `codex`，然后在新的 Codex 会话里触发。

触发命令：
```text
Codex App/Desktop: 在 `/` 列表里选择 super-dev
Codex CLI: $super-dev
回退入口: super-dev: 你的需求
```

接入后是否需要重启：是

补充说明：
1. Codex App/Desktop 优先从 `/` 列表里直接选择 `super-dev`；这是已启用 Skill 的官方入口，不是项目级自定义 slash 文件。
2. Codex CLI 优先显式输入 `$super-dev`。
3. 如果当前已经在自然语言上下文里继续流程，也可以直接输入 `super-dev: 你的需求`。
4. 基础接入面是项目根 `AGENTS.md`、项目级 `.agents/skills/super-dev/SKILL.md`、全局 `CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`），以及官方用户级 Skill `~/.agents/skills/super-dev/SKILL.md`。
5. 同时会额外生成可选的 repo plugin 增强层：`.agents/plugins/marketplace.json` + `plugins/super-dev-codex/.codex-plugin/plugin.json`，让 Codex App/Desktop 在 AGENTS + Skills 之外还能看到更完整的本地 plugin 面。
6. 为兼容旧安装，仍会保留 `super-dev-core` 作为兼容别名。
7. 如果旧会话没加载新 Skill，重启 `codex` 再试。
8. 无论使用 `/super-dev`、`$super-dev` 还是 `super-dev:`，都必须进入同一条 Super Dev 流程；长流程里继续修改、补充、确认或恢复时，优先沿用当前入口面。

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
在项目目录启动 OpenCode 会话后触发。

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

接入后是否需要重启：是

补充说明：
1. Kiro CLI 当前优先按官方 steering slash entry 触发；如果当前会话只接受自然语言，再回退到 `super-dev: 需求`。
2. 官方接入面是 `.kiro/steering/super-dev.md` + `.kiro/skills/super-dev-core/SKILL.md` + `~/.kiro/steering/super-dev.md` + `~/.kiro/skills/super-dev-core/SKILL.md`。
3. 完成接入后建议重开 Kiro CLI，让 steering slash entry 与 skills 在新会话里一起生效。

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
2. 若 slash 未生效，先确认 `AGENTS.md`、`.qoder/commands/super-dev.md` 已生成，并检查 `.qoder/rules/` 目录是否存在。
3. 官方接入面已切到 `AGENTS.md` + `.qoder/rules/super-dev.md` + `.qoder/commands/super-dev.md` + `.qoder/skills/` / `~/.qoder/AGENTS.md` + `~/.qoder/skills/`。

#### 8. Copilot CLI

安装：
```bash
super-dev onboard --host copilot-cli --force --yes
```

触发位置：
在项目目录启动 Copilot CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
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
2. 官方主面是 `CODEBUDDY.md` + `.codebuddy/commands/` + `.codebuddy/skills/`，并补充 `~/.codebuddy/CODEBUDDY.md`。
3. 如果会话已提前打开，建议重新加载项目规则后再试。

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
/super-dev 你的需求
```

接入后是否需要重启：是

补充说明：
1. Kiro IDE 当前优先使用官方 steering slash entry，直接在 Agent Chat 输入 `/super-dev 你的需求`；如果当前会话只接受自然语言，再回退到 `super-dev: 你的需求`。
2. 接入会写入项目级 `.kiro/steering/super-dev.md`、`.kiro/skills/super-dev-core/SKILL.md`，并补充全局 `~/.kiro/steering/super-dev.md` 与 `~/.kiro/skills/super-dev-core/SKILL.md`；旧 `~/.kiro/steering/AGENTS.md` 仍作为兼容面保留。
3. 如果 steering 或 skills 未加载，先重开项目窗口或新开一个 Agent Chat。

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
1. Qoder IDE 当前优先使用项目级 commands + rules + skills 模式，直接在 Agent Chat 输入 `/super-dev 你的需求`。
2. 若新增命令未出现，先确认 `AGENTS.md`、`.qoder/commands/super-dev.md` 已生成，并检查 `.qoder/rules/super-dev.md` 是否存在，再重新打开项目或新开一个 Agent Chat。
3. 官方接入面已切到 `AGENTS.md` + `.qoder/rules/super-dev.md` + `.qoder/commands/super-dev.md` + `.qoder/skills/` / `~/.qoder/AGENTS.md` + `~/.qoder/skills/`。

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
3. 当前按 `CODEBUDDY.md` + `.codebuddy/rules/super-dev/RULE.mdc` + `.codebuddy/commands/` + `.codebuddy/agents/` + `.codebuddy/skills/` 接入。

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

#### 21. OpenClaw（手动插件宿主）

OpenClaw 通过原生 Plugin SDK 集成，无需 `super-dev onboard`，直接安装 npm 插件即可。

安装：
```bash
# 第一步：安装 super-dev CLI
pip install super-dev

# 第二步：安装 OpenClaw 插件（二选一）
openclaw plugins install @super-dev/openclaw-plugin  # npm 插件（含 20 Tool）
clawhub install super-dev                            # ClawHub Skill（纯指令）
```

ClawHub 页面: https://clawhub.ai/shangyankeji/super-dev

触发位置：
在 OpenClaw Agent 对话面板中，确保当前工作区为目标项目后触发。

触发命令：
```text
super-dev: 你的需求
```
或
```text
/super-dev 你的需求
```

插件提供 20 个专用 Tool：

| Tool | 功能 |
|------|------|
| `super_dev_pipeline` | 启动完整流水线 |
| `super_dev_init` | 项目初始化 |
| `super_dev_status` | 查看流水线状态 |
| `super_dev_quality` | 质量检查（按类型） |
| `super_dev_spec` | Spec 管理（propose/list/show/scaffold/validate） |
| `super_dev_spec_trace` | Spec-Code 追踪 |
| `super_dev_spec_consistency` | Spec-Code 一致性检测 |
| `super_dev_spec_acceptance` | Spec 验收检查 |
| `super_dev_config` | 配置管理（list/get/set） |
| `super_dev_review` | 审查与门禁确认（docs/ui/architecture/quality） |
| `super_dev_release` | 发布就绪度 / 交付证明包 |
| `super_dev_expert` | 专家咨询 (11 角色) |
| `super_dev_deploy` | CI/CD 配置 / Dockerfile / 发布演练 |
| `super_dev_analyze` | 项目分析（技术栈/依赖/结构） |
| `super_dev_doctor` | 环境诊断 |
| `super_dev_governance` | 治理规则总览 |
| `super_dev_knowledge_stats` | 知识库使用统计 |
| `super_dev_knowledge_evolve` | 知识权重自演化 |
| `super_dev_metrics` | Pipeline 效能度量 |
| `super_dev_run` | 通用命令透传（可选） |

补充说明：
1. 插件通过 CLI subprocess 桥接调用 `super-dev`，因此必须先 `pip install super-dev`。
2. 安装后建议重启 OpenClaw Gateway 或新开会话，让 Plugin 和 Skill 生效。
3. 插件内嵌 SKILL.md，OpenClaw Agent 会自动理解流水线协议。
4. 使用 `super-dev doctor --host openclaw` 检查集成状态。

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
