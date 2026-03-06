# Super Dev 详细使用指南（2.0.5）

> 宿主详细试用方式、是否支持 `/super-dev`、各宿主正确入口，请优先查看：
> [HOST_USAGE_GUIDE.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_USAGE_GUIDE.md)

> 本文是项目级操作手册，覆盖：
> - 指令大全（命令怎么用）
> - 0-1 从零新建项目
> - 1-N+1 增量迭代项目（包含 1-1+N 场景）
> - 商业级质量门禁与交付流程

---

## 1. 概念与入口

### 1.1 推荐入口

默认推荐先在宿主内触发 `Super Dev`：

```text
/super-dev 你的功能需求
```

如果你不确定当前机器该用哪个宿主，先运行：

```bash
super-dev start --idea "你的功能需求"
```

终端 `super-dev "你的功能需求"` 只建议作为治理产物入口，不应理解为 Super Dev 自己替代宿主编码。

默认启用宿主硬门禁：若没有 `ready` 宿主，流水线会阻断并提示先接入宿主。

示例：

```bash
super-dev "做一个企业级项目管理系统，支持登录、RBAC、项目、任务、报表、审计日志"
```

这条命令会自动进入完整流水线（带确认门）：

1. 同类产品研究（优先使用宿主联网能力）
2. 文档生成（PRD / 架构 / UIUX / 执行计划 / 前端蓝图）
3. 文档确认门：先给用户看三文档并等待确认/修改
4. Spec 规范创建
5. 前端可演示骨架与运行验证
6. 后端实现与联调
7. 红队审查（安全/性能/架构）
8. 质量门禁（80+）
9. 代码审查指南
10. AI 提示词
11. CI/CD（5 平台）
12. 部署修复模板 + 迁移脚本 + 交付包

文档确认可以通过 Web 工作台操作，也可以直接在终端执行：

```bash
super-dev review docs
super-dev review docs --status revision_requested --comment "补充差异化方案与首页信息架构"
super-dev review docs --status confirmed --comment "三文档确认，进入 Spec 阶段"
```

### 1.2 高级入口（显式参数）

需要精细控制平台时再使用：

```bash
super-dev pipeline "你的功能需求" \
  --platform web \
  --frontend react \
  --backend python \
  --domain saas \
  --cicd all \
  --quality-threshold 85
```

---

## 2. 安装与初始化

### 2.1 安装

```bash
pip install -U super-dev
```

指定版本：

```bash
pip install super-dev==2.0.5
```

### 2.2 初始化（可选，但团队项目建议）

```bash
mkdir my-project && cd my-project
super-dev init my-project --platform web --frontend react --backend node --domain saas
```

初始化后可查看配置：

```bash
super-dev config list
```

可选：在 `super-dev.yaml` 中配置企业知识增强策略：

```yaml
knowledge_allowed_domains:
  - openai.com
  - python.org
knowledge_cache_ttl_seconds: 1800
language_preferences:
  - python
  - typescript
  - rust
host_compatibility_min_score: 80
host_compatibility_min_ready_hosts: 1
host_profile_targets:
  - codex-cli
  - claude-code
host_profile_enforce_selected: true
```

推荐在项目根目录维护 `knowledge/` 目录作为团队知识资产库（已被流水线自动扫描）：

```text
knowledge/
  high-quality-engineering-playbook.md
  official-knowledge-catalog.md
  security/
    baseline.yaml
  operations/
    runbook.txt
```

建议把权威链接、业务规则、交付检查清单、故障处理手册都放入 `knowledge/`，让需求增强阶段稳定命中团队经验与官方规范。

建议按全链路结构维护深度知识库：

```text
knowledge/
  00-governance/
  product/
  design/
  architecture/
  development/
  testing/
  security/
  cicd/
  operations/
  data/
  incident/
  ai/
```

这套结构可覆盖从需求、设计、研发、测试、安全、发布、运维到复盘的完整环节，让每次需求增强都能命中对应领域知识。

如果你希望“开发类知识库完整内置”，可直接使用：

```text
knowledge/development/DEVELOPMENT_KB_MASTER_INDEX.md
```

该索引已内置前端、后端、API、数据库、性能、并发、重构、评审、工程效能、开发安全，以及UI卓越、全场景开发、知识图谱、成熟度治理、端到端开发全流程与全流程模板专题入口。

开发知识库审计可直接运行：

```bash
python scripts/audit_development_kb.py
```

```bash
python scripts/check_knowledge_gates.py --project-dir .
```

如果你希望“AI开发类知识库完整内置”，可直接使用：

```text
knowledge/ai/AI_KB_MASTER_INDEX.md
```

可运行AI知识库审计：

```bash
python scripts/audit_ai_kb.py
```

---

## 3. 指令大全（命令速查）

### 3.1 核心流水线

```text
/super-dev 需求描述                    # 推荐：在宿主会话中触发
```

```bash
super-dev start --idea "需求描述"      # 推荐：自动选宿主并给出试用步骤
super-dev "需求描述"                   # 本地治理流水线入口，不替代宿主编码
super-dev pipeline "需求描述" ...       # 高级：显式参数模式
super-dev create "需求描述"             # 快速生成文档 + Spec
```

### 3.2 Spec 与任务闭环

```bash
super-dev spec init
super-dev spec list
super-dev spec show <change_id>
super-dev spec propose <change_id> --title "标题" --description "描述"
super-dev spec add-req <change_id> <spec_name> <req_name> "需求描述"
super-dev spec validate
super-dev spec archive <change_id>

super-dev task list
super-dev task status <change_id>
super-dev task run <change_id>
```

### 3.3 质量与审查

```bash
super-dev quality --type all
super-dev quality --type prd
super-dev quality --type architecture
super-dev quality --type uiux
super-dev policy init
super-dev policy init --preset enterprise --force
super-dev policy presets
super-dev policy show
```

### 3.4 部署与交付

```bash
super-dev deploy --cicd github
super-dev deploy --cicd all
super-dev deploy --docker
super-dev deploy --cicd all --rehearsal
super-dev deploy --cicd all --rehearsal --rehearsal-verify
super-dev pipeline "需求描述" --skip-rehearsal-verify   # 显式跳过发布演练门禁
super-dev metrics
super-dev metrics --history --limit 20
```

### 3.5 设计与专家

```bash
super-dev design search "modern dashboard"
super-dev design generate --product saas --industry fintech
super-dev design tokens --primary "#2563EB"

super-dev expert --list
super-dev expert ARCHITECT "评审当前系统拆分"
super-dev expert SECURITY "审查登录与会话安全"
```

### 3.6 集成与 Skill

```bash
super-dev integrate list
super-dev integrate setup --all --force
super-dev integrate setup --target qoder --force
super-dev integrate matrix
super-dev integrate matrix --json

super-dev skill targets
super-dev skill install super-dev --target codex-cli --name super-dev-core --force
super-dev skill list --target codex-cli
super-dev skill uninstall super-dev-core --target codex-cli
```

---

## 4. 0-1 场景：从零创建项目

> 适用于“还没有代码仓库，只有业务需求”的情况。

### 4.1 最短路径（推荐）

```bash
mkdir new-app && cd new-app
super-dev "做一个 B2B CRM，支持线索管理、客户管理、销售漏斗、权限管理"
```

### 4.2 产物检查

运行后重点看这些文件：

- `output/*-research.md`：需求增强报告（联网+知识）
- `output/*-prd.md`：产品需求文档
- `output/*-architecture.md`：架构文档
- `output/*-uiux.md`：UI/UX 文档
- `output/*-execution-plan.md`：执行路线图
- `.super-dev/changes/*/tasks.md`：Spec 任务清单
- `output/*-task-execution.md`：任务执行与自动修复记录
- `output/*-redteam.md`：红队审查报告
- `output/*-quality-gate.md`：质量门禁报告
- `output/delivery/*-delivery-manifest.json`：交付清单
- `output/delivery/*-delivery-report.md`：交付报告

### 4.3 开发推进建议

1. 先让前端骨架跑起来，做演示确认需求。
2. 再按 `tasks.md` 实现后端与数据层。
3. 最后修复红队和质量门禁阻断项。

### 4.4 常见 0-1 命令组合

```bash
super-dev "做一个内容平台，支持发布、审核、推荐"
super-dev task list
super-dev task run <change_id>
super-dev quality --type all
```

---

## 5. 1-N+1 场景：现有项目增量迭代（含 1-1+N）

> 适用于“已有线上/在研项目，需要继续增加能力”的情况。

### 5.1 场景定义

- `1-1+N`：基于一个已有主项目，持续增加 N 个能力模块。
- `1-N+1`：多个子域迭代到下一阶段（本质仍是增量迭代）。

在 Super Dev 中，这些都归类为增量开发路径，核心是：
- 先分析现状
- 再建立 Spec 变更
- 最后按任务闭环推进

### 5.2 标准流程

#### 步骤 1：分析现有项目

```bash
cd existing-project
super-dev analyze .
```

#### 步骤 2：初始化 Spec（仅首次）

```bash
super-dev spec init
```

#### 步骤 3：创建增量提案

```bash
super-dev spec propose add-billing \
  --title "新增计费中心" \
  --description "支持套餐、订阅、账单、发票、支付回调"
```

#### 步骤 4：补充关键需求

```bash
super-dev spec add-req add-billing billing subscription "系统 SHALL 支持订阅创建和续费"
super-dev spec add-req add-billing billing invoice "系统 SHALL 生成可追溯账单"
super-dev spec add-req add-billing billing webhook "系统 SHALL 幂等处理支付回调"
```

#### 步骤 5：执行增量实现收敛

```bash
super-dev task status add-billing
super-dev task run add-billing --backend python --frontend react
```

#### 步骤 6：质量门禁与交付

```bash
super-dev quality --type all
super-dev deploy --cicd all
```

### 5.3 迭代批次建议

对于 `1-1+N`，建议按“单批次单变更”推进：

1. 一个 `change_id` 只做一类功能（例如 billing）。
2. 每个变更都独立过红队与质量门禁。
3. 通过后再做下一个变更（reporting / audit / workflow）。

---

## 6. 商业级交付标准（必过）

发布前必须满足：

1. 红队审查无阻断（critical 为 0）。
2. 质量门禁总分 >= 80。
3. Spec 任务完成度达到可交付标准（建议全部完成）。
4. CI/CD 五平台配置已生成并可按目标平台落地。
5. 交付包状态为 `ready`。

建议执行：

```bash
./scripts/preflight.sh
```

如果本地环境限制可用：

```bash
./scripts/preflight.sh --allow-dirty --skip-benchmark --skip-package
```

---

## 7. 多工具安装与使用

### 7.1 安装向导（默认，支持多选）

```bash
./install.sh
super-dev install
```

说明：

- 默认进入交互式安装引导
- 可多选宿主（CLI/IDE）
- 自动执行 onboard + doctor

### 7.2 一键安装全部目标（非交互）

```bash
./install.sh --targets all
```

### 7.3 仅安装规则，不装 skill

```bash
./install.sh --targets all --no-skill
```

### 7.4 单平台安装

```bash
super-dev integrate setup --target qoder --force
super-dev skill install super-dev --target qoder --name super-dev-core --force
```

### 7.5 自动探测宿主并接入（推荐）

```bash
super-dev detect --json
super-dev detect --auto --save-profile
super-dev onboard --auto --yes --force
super-dev doctor --auto --repair --force
```

`detect` 会默认生成：

- `output/<project>-host-compatibility.json`
- `output/<project>-host-compatibility.md`
- `output/host-compatibility-history/*.json`
- `output/host-compatibility-history/*.md`

当使用 `--save-profile` 时，会自动更新 `super-dev.yaml`：

- `host_profile_targets`
- `host_profile_enforce_selected=true`

流水线每次运行会产出契约审计：

- `output/*-pipeline-contract.json`
- `output/*-pipeline-contract.md`

企业策略建议：

1. 使用 `super-dev policy init --preset enterprise --force`。
2. 先执行 `super-dev detect --auto --save-profile` 产出兼容报告。
3. 在策略中启用 `enforce_required_hosts_ready=true`，并设置 `min_required_host_score`。

支持目标：

- CLI: `claude-code`, `codex-cli`, `gemini-cli`, `kimi-cli`, `kiro-cli`, `qoder-cli`
- IDE: `qoder`

---

## 8. 常见问题

### Q1: 我只想用一句话驱动，能否不用 pipeline 参数？

可以。默认推荐就是：

```bash
super-dev "需求"
```

### Q2: 如何查看当前变更进度？

```bash
super-dev spec list
super-dev task status <change_id>
super-dev run --resume
```

### Q3: 质量门禁没过怎么办？

先看：

- `output/*-redteam.md`
- `output/*-quality-gate.md`
- `output/*-task-execution.md`

按报告里的 failed/critical 项逐条修复，再重新执行：

```bash
super-dev task run <change_id>
super-dev quality --type all
```

### Q4: 如何准备对外发布？

按顺序执行：

```bash
./scripts/preflight.sh
bash scripts/release.sh --version 2.0.2 --no-publish
bash scripts/publish.sh --repository pypi
```

---

## 9. 推荐日常操作模板

### 9.1 新项目模板

```bash
super-dev "需求"
super-dev task list
super-dev quality --type all
```

### 9.2 增量迭代模板

```bash
super-dev analyze .
super-dev spec propose <change_id> --title "标题" --description "描述"
super-dev spec add-req <change_id> <spec> <req> "描述"
super-dev task run <change_id>
super-dev quality --type all
```

---

## 10. 相关文档

- 快速开始：`docs/QUICKSTART.md`
- 集成指南：`docs/INTEGRATION_GUIDE.md`
- 发布指南：`docs/PUBLISHING.md`
- 发布作战手册：`docs/RELEASE_RUNBOOK.md`
