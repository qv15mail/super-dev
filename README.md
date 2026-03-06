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

当前版本：`2.0.5`

---

## 项目介绍

`Super Dev` 是一个面向商业级交付的 AI 开发编排工具，核心目标是辅助用户将项目落地成可执行工程资产：

- 它不提供自己的大模型能力，也不替代宿主的编码能力
- 宿主负责调用模型、工具与实际编码
- `Super Dev` 负责流程治理、设计约束、质量门禁、审计产物与交付标准

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
- 通过宿主能力边界建模，明确哪些宿主是 `Certified / Compatible / Experimental`

### 2. 流水线式开发编排（0-12 阶段）

- 同类产品研究 -> 需求增强 -> 文档 -> Spec -> 实现骨架 -> 红队 -> 质量门禁 -> 交付
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

### 7. 商业级 UI Intelligence

- 内置 UI/UX 知识库：产品类型、行业语气、信任模块、页面骨架、反模式、信息密度
- 内置主流组件生态推荐：React/Next、Vue、Angular、Svelte 等按宿主和场景输出首选与备选方案
- UI/UX 文档会自动给出组件生态、表单/表格/图表/动效/图标基线，而不是只写风格描述
- 宿主提示词与 Skill 会继承这些规则，优先生成现代商业产品界面而不是 AI 模板页面
- 新增 `super-dev quality --type ui-review`，可对 `preview.html` / `output/frontend/index.html` 做结构级视觉审查

---

## 安装方式

### 1. uv 安装（推荐）

```bash
uv tool install super-dev
```

升级：

```bash
uv tool upgrade super-dev
```

### 2. PyPI 安装

```bash
pip install -U super-dev
```

### 3. 指定版本安装

```bash
pip install super-dev==2.0.5
```

### 4. GitHub 指定标签安装

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.5
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

## 最简单使用（给最终用户）

### CLI 宿主（Claude Code / CodeBuddy CLI / Codex CLI / Cursor CLI / Gemini CLI / iFlow CLI / Kimi CLI / Kiro CLI / OpenCode CLI / Qoder CLI）

1. 进入项目目录执行 `super-dev` 完成接入。  
2. Claude Code / Gemini CLI / Kiro CLI / Qoder CLI / CodeBuddy CLI 等支持原生映射的宿主，可直接输入：`/super-dev 你的需求`。
3. Codex CLI、Kimi CLI 当前不使用 `/super-dev`；在宿主会话里输入 `super-dev: 你的需求`。
4. 宿主会先被约束执行“同类产品研究 -> 三文档 -> 等待用户确认 -> Spec -> 前端运行验证 -> 后端/测试/交付”，不会直接跳到写代码。

### 宿主如何理解 Super Dev

- `Super Dev` 是当前项目里的本地 Python CLI 工具，加上宿主里的规则文件 / Skill / slash 映射。
- 宿主负责模型推理、联网搜索、编码、运行终端与修改文件。
- `Super Dev` 负责把宿主拉进固定流水线：research、三文档、确认门、Spec、前端优先、后端联调、质量门禁、交付审计。
- 当用户输入 `/super-dev 需求` 或 `super-dev: 需求` 时，宿主要把它视为“进入 Super Dev 流水线”，而不是普通聊天。
- 需要生成或刷新文档、Spec、质量报告、交付产物时，宿主应优先调用本地 `super-dev` CLI。
- 如果项目根目录存在 `knowledge/`，宿主必须优先读取与当前需求相关的知识文件。
- 如果已生成 `output/knowledge-cache/*-knowledge-bundle.json`，宿主必须把其中命中的本地知识、研究摘要和场景约束继承到三文档、Spec 和实现阶段。

### IDE 宿主（CodeBuddy / Cursor / Kiro / Qoder / Trae / Windsurf）

1. 进入项目目录执行 `super-dev` 完成接入。  
2. 打开 IDE 的 Agent Chat 后，按宿主真实入口触发。  
3. 支持 slash 的 IDE 使用 `/super-dev 你的需求`；不支持 slash 的 IDE 使用 `super-dev: 你的需求`。
4. 非 slash 宿主仍会通过项目规则、AGENTS 或 Skill 进入同样的 research-first 流程，而不是绕开流水线。

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

#### 2. CodeBuddy CLI

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

#### 3. CodeBuddy IDE

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

#### 4. Cursor CLI

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

#### 5. Cursor IDE

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

#### 6. Gemini CLI

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

#### 7. iFlow CLI

安装：
```bash
super-dev onboard --host iflow --force --yes
```

触发位置：
在项目目录启动 iFlow CLI 会话后触发。

触发命令：
```text
/super-dev 你的需求
```

接入后是否需要重启：否

补充说明：
1. 当前按 slash 宿主适配。
2. 如果 slash 未出现，先检查项目级命令文件是否已写入。

#### 8. Kimi CLI

安装：
```bash
super-dev onboard --host kimi-cli --force --yes
```

触发位置：
在项目目录启动 Kimi CLI 会话后触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. 不要输入 `/super-dev`，Kimi CLI 当前优先按 `.kimi/AGENTS.md + 文本触发` 工作。
2. 建议先用 `super-dev doctor --host kimi-cli` 做一次确认。
3. 尽量保持同一会话完成完整开发流程。

#### 9. Kiro CLI

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

#### 10. Kiro IDE

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
1. Kiro IDE 当前优先按 steering/rules 模式触发，不走 `/super-dev`。
2. 如果 steering/rules 未加载，先重开项目窗口。

#### 11. OpenCode

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

#### 12. Qoder CLI

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

#### 13. Qoder IDE

安装：
```bash
super-dev onboard --host qoder --force --yes
```

触发位置：
打开 Qoder IDE 的 Agent Chat，在当前项目内触发。

触发命令：
```text
super-dev: 你的需求
```

接入后是否需要重启：否

补充说明：
1. Qoder IDE 当前优先按 project rules 模式触发，不走 `/super-dev`。
2. 若规则未生效，重新打开项目或重新创建聊天。

#### 14. Windsurf

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

#### 15. Codex CLI

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
1. 不要输入 `/super-dev`，Codex 当前不走自定义 slash。
2. 实际依赖 `.codex/AGENTS.md` 和 `.codex/skills/super-dev-core/SKILL.md`。
3. 如果旧会话没加载新 Skill，重启 `codex` 再试。

#### 16. Trae

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
1. 不要输入 `/super-dev`。
2. Trae 当前默认按项目 rules 模式工作，无需手动开启 Skill。
3. 随后按 `output/*` 与 `.super-dev/changes/*/tasks.md` 推进开发。

## 快速开始（详细使用说明）

宿主详细使用方式、是否支持 `/super-dev`、各宿主的正确触发方式，请看：

- [docs/HOST_USAGE_GUIDE.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_USAGE_GUIDE.md)
- [docs/HOST_CAPABILITY_AUDIT.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_CAPABILITY_AUDIT.md)

### 宿主触发矩阵

认证等级说明：

- `Certified`：已按该宿主真实能力做专门适配，当前是优先推荐使用的宿主。
- `Compatible`：接入链路完整，可以稳定使用，但还缺更长期的真机回归认证。
- `Experimental`：已接入并可尝试使用，但仍需要更多真实项目验证，不建议作为唯一生产宿主。

| 宿主 | 类型 | 认证等级 | 是否支持 `/super-dev` | 正确触发方式 | 接入后是否需要重启 |
| --- | --- | --- | --- | --- | --- |
| Claude Code | CLI | Certified | 支持 | 在 Claude Code 会话中输入 `/super-dev 你的需求` | 否 |
| CodeBuddy CLI | CLI | Compatible | 支持 | 在 CodeBuddy CLI 会话中输入 `/super-dev 你的需求` | 否 |
| CodeBuddy IDE | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Cursor CLI | CLI | Compatible | 支持 | 在 Cursor CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Cursor IDE | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Gemini CLI | CLI | Compatible | 支持 | 在 Gemini CLI 会话中输入 `/super-dev 你的需求` | 否 |
| iFlow CLI | CLI | Experimental | 支持 | 在 iFlow CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Kimi CLI | CLI | Experimental | 不支持 | 在 Kimi CLI 会话中输入 `super-dev: 你的需求`（由 `.kimi/AGENTS.md` 生效） | 否 |
| Kiro CLI | CLI | Compatible | 支持 | 在 Kiro CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Kiro IDE | IDE | Experimental | 不支持 | 在 Kiro IDE Agent Chat 中输入 `super-dev: 你的需求`（由 `.kiro/steering/super-dev.md` 生效） | 否 |
| OpenCode CLI | CLI | Experimental | 支持 | 在 OpenCode CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Qoder CLI | CLI | Compatible | 支持 | 在 Qoder CLI 会话中输入 `/super-dev 你的需求` | 否 |
| Qoder IDE | IDE | Experimental | 不支持 | 在 Qoder IDE Agent Chat 中输入 `super-dev: 你的需求`（由 `.qoder/rules.md` 生效） | 否 |
| Windsurf | IDE | Experimental | 支持 | 在 Agent Chat 中输入 `/super-dev 你的需求` | 否 |
| Codex CLI | CLI | Certified | 不支持 | 重启 Codex 后输入 `super-dev: 你的需求`，由 `.codex/AGENTS.md` + `super-dev-core` Skill 生效 | 是 |
| Trae | IDE | Certified | 不支持 | 在 Trae Agent Chat 中输入 `super-dev: 你的需求`（由 `.trae/rules.md` 生效） | 否 |

### 1. 安装后直接进入引导

```bash
super-dev
```

`super-dev` 无参数默认进入安装引导，可多选宿主。

如果通过 `uv tool install` 安装，也可以直接运行：

```bash
uv tool run super-dev
```

如果你不懂宿主差异，直接用：

```bash
super-dev start --idea "你的需求"
```

它会自动：

1. 探测本机已安装宿主
2. 优先选择认证等级更高、触发更简单的宿主
3. 自动完成接入并保存宿主画像
4. 直接告诉你下一步该去哪个宿主、输入什么

如果要确认宿主是否真的已经按 Super Dev 规则生效，继续执行：

```bash
super-dev integrate smoke --target <host_id>
```

它会输出该宿主的标准验收语句、验收步骤和通过标准。

### 2. 非交互一键安装（CI/脚本友好）

自动探测本机宿主并安装：

```bash
super-dev install --auto --force --yes
```

安装全部宿主：

```bash
super-dev install --all --force --yes
```

检查或升级最新版本：

```bash
super-dev update --check
super-dev update
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

执行时的默认顺序是：

1. 宿主先联网研究同类产品，生成 `output/*-research.md`
2. 生成 `output/*-prd.md`
3. 生成 `output/*-architecture.md`
4. 生成 `output/*-uiux.md`
5. 停在文档确认门，等待用户确认或提出修改意见
6. 用户确认后再生成 Spec 与 `tasks.md`
7. 先前端实现与运行验证，再进入后端、测试、门禁、交付

终端也可以直接管理这一步确认状态：

```bash
super-dev review docs
super-dev review docs --status revision_requested --comment "补充竞品差异化与首页信息架构"
super-dev review docs --status confirmed --comment "三文档已确认，进入 Spec 阶段"
```

### 6. 查看关键产物

运行后重点看 `output/`：

- `*-research.md`
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

`/super-dev` 会强制执行：先 research -> 再三文档（PRD/架构/UIUX）-> 等待用户确认 -> 再 Spec 与 tasks -> 再编码实现。  
编码阶段默认遵循商业级 UI/UX 规范，禁止紫/粉渐变主视觉、emoji 功能图标、模板化页面直出，并要求先定义字体系统、token、栅格和组件状态矩阵。

Codex CLI 当前不使用 `/super-dev`，而是依赖 `.codex/AGENTS.md` + `super-dev-core` Skill。在 Codex 会话中输入 `super-dev: 你的需求` 即可。

若宿主不支持 slash 命令映射，可在同一项目根目录执行终端入口（仅触发 Super Dev 本地流水线编排）：

```bash
super-dev "你的需求"
```

注意：

1. 终端入口本身不替代宿主模型能力。
2. 真正的编码仍然应在已接入的宿主中完成。
3. 如果宿主具备联网能力，Super Dev 会优先要求宿主先做同类产品研究。

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
- `codebuddy-cli`
- `codex-cli`
- `cursor-cli`
- `gemini-cli`
- `iflow`
- `kimi-cli`
- `kiro-cli`
- `opencode`
- `qoder-cli`

### IDE / 扩展宿主

- `codebuddy`
- `cursor`
- `kiro`
- `qoder`
- `trae`（Rules-first）
- `windsurf`

### 宿主适配方式（CLI/IDE）

- `CLI 宿主（原生 slash）`：在宿主会话内触发 `/super-dev`，由宿主模型执行编码
- `CLI 宿主（非 slash）`：在宿主会话内输入 `super-dev: 你的需求`，由 AGENTS / 规则文件驱动执行
- `IDE 宿主（原生 slash）`：在 Agent Chat 触发 `/super-dev`，由规则文件与 Skill 约束执行流程
- `IDE 宿主（非 slash）`：在 Agent Chat 输入 `super-dev: 你的需求`，由项目规则驱动执行
- `终端入口`：`super-dev "需求"` 仅触发本地流水线编排，不直接调用宿主模型会话

查看宿主适配矩阵（官方文档链接、适配模式、注入路径、探测策略）：

```bash
super-dev integrate matrix
super-dev integrate matrix --json
```

---

## 常用命令速查

```bash
# uv
uv tool install super-dev
uv tool upgrade super-dev
uv sync
uv run super-dev --version

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
super-dev release readiness
super-dev deploy --cicd all --rehearsal --rehearsal-verify
```

---

## 开发与发布（uv）

```bash
# 同步依赖
uv sync

# 本地检查
uv run pytest -q
uv run ruff check super_dev tests
uv run mypy super_dev

# 构建
uv build

# 发布
UV_PUBLISH_TOKEN="<your-token>" uv publish
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
