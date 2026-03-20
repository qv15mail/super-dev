# 开发：Excellent（11964948@qq.com）

## 项目全链路深度知识库

本目录是项目的长期知识资产中心，服务需求增强、方案设计、实现落地、测试验收、发布运维与复盘迭代。

### 目录分层
- `00-governance/`：知识分类、维护规范、评审机制
- `product/`：需求洞察、PRD方法、业务闭环
- `design/`：信息架构、交互原则、状态矩阵
  - `design/ui-full-lifecycle-cross-platform-playbook.md`：UI 全流程与五端落地手册
- `architecture/`：系统架构、演进路线、技术决策
- `development/`：工程规范、模块边界、实现基线
- `testing/`：测试策略、质量门禁、风险模型
- `security/`：安全基线、威胁模型、应急机制
- `cicd/`：流水线、发布策略、供应链安全
- `operations/`：SRE运行、监控告警、容量与成本
- `data/`：指标体系、数据建模、治理规范
- `incident/`：故障响应、复盘机制、持续改进
- `ai/`：LLM/Agent工程、评测与护栏

### 使用方式
- 每次新增需求前，先补齐对应环节知识条目，确保增强阶段命中关键规则。
- 每次上线后，把关键决策与问题复盘沉淀到对应环节文档。
- 每周进行一次知识健康检查：过期条目、失效链接、冲突规则、重复内容。

### 最小维护标准
- 每篇文档必须包含：目标、适用范围、执行清单、验收标准、常见失败模式。
- 每篇文档至少每月审查一次；有架构变更或事故后必须即时更新。

### 治理入口
- 知识地图：`00-governance/knowledge-map.md`
- 分类法：`00-governance/taxonomy.yaml`
- 领域索引：`00-governance/domain-index.yaml`
- 维护策略：`00-governance/maintenance-policy.md`
- 评审清单：`00-governance/review-checklist.md`
- 90天路线图：`00-governance/knowledge-roadmap-90days.md`

### 开发类完整内置入口
- 开发总索引：`development/DEVELOPMENT_KB_MASTER_INDEX.md`
- 前端总册：`development/frontend-engineering-complete.md`
- 后端总册：`development/backend-engineering-complete.md`
- API总册：`development/api-governance-complete.md`
- 数据库总册：`development/database-engineering-complete.md`
- 性能总册：`development/performance-capacity-complete.md`
- 并发总册：`development/concurrency-reliability-complete.md`
- 重构总册：`development/refactor-migration-complete.md`
- 评审总册：`development/code-review-quality-complete.md`
- 效能总册：`development/engineering-effectiveness-complete.md`
- 开发安全总册：`development/security-in-development-complete.md`
- 知识治理层：`development/00-governance/`
- 知识标准层：`development/01-standards/`
- 知识手册层：`development/02-playbooks/`
- 知识清单层：`development/03-checklists/`
- 反模式层：`development/04-antipatterns/`
- 实战案例层：`development/05-cases/`
- 术语与学习层：`development/06-glossary/`、`development/07-learning-path/`
- 机器索引层：`development/08-catalog/catalog.yaml`
- 成熟度评估层：`development/09-maturity/`
- 开发知识图谱层：`development/10-knowledge-graph/`
- UI卓越体系层：`development/11-ui-excellence/`
- 多业务场景层：`development/12-scenarios/`
- 落地资产与门禁层：`development/13-implementation-assets/`
- 端到端全流程层：`development/14-full-lifecycle/`
- 全流程交付模板层：`development/15-lifecycle-templates/`
- 自动审计脚本：`scripts/audit_development_kb.py`
- 知识门禁脚本：`scripts/check_knowledge_gates.py`

### AI开发类完整内置入口
- AI总索引：`ai/AI_KB_MASTER_INDEX.md`
- AI领域索引与清单：`ai/ai-domain-index-and-checklist.md`
- 模型选型与路由：`ai/ai-model-selection-and-routing-strategy.md`
- RAG工程：`ai/ai-rag-engineering-playbook.md`
- 上下文与记忆：`ai/ai-agent-memory-context-management.md`
- 数据安全与合规：`ai/ai-data-security-and-compliance-playbook.md`
- 红队与安全评测：`ai/ai-red-team-and-safety-evaluation.md`
- 发布门禁与回滚：`ai/ai-release-readiness-and-rollback-gate.md`
- 可观测与值班：`ai/ai-observability-and-oncall-runbook.md`
- 成本与容量优化：`ai/ai-cost-capacity-optimization-playbook.md`
- 治理成熟度：`ai/ai-governance-maturity-model.md`
- 阶段退出标准：`ai/ai-stage-exit-criteria.yaml`
- 机器索引：`ai/ai-catalog.yaml`
