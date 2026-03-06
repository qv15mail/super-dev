# 开发：Excellent（11964948@qq.com）

## AI开发类完整知识库总索引（内置版）

### 目标
- 把AI开发知识从单点经验升级为可执行、可审计、可门禁的体系化资产。
- 覆盖模型选型、RAG、Agent、评测、安全、发布、运维、成本、治理全链路。

### 使用原则
- 先读本索引，再进入专题文档执行清单与验收标准。
- 每次模型、提示词、工具链变更都必须进行回归评测与风险复核。
- 每次生产事故后必须补齐失败模式、回滚策略和预防动作。

### 专题入口
- 基础架构：`llm-agent-engineering-deep-dive.md`
- 评测基准：`agent-evaluation-benchmark.md`
- 提示词与工具护栏：`prompt-and-tool-guardrails.md`
- 领域索引与清单：`ai-domain-index-and-checklist.md`
- 模型选型与路由：`ai-model-selection-and-routing-strategy.md`
- RAG工程：`ai-rag-engineering-playbook.md`
- 上下文与记忆：`ai-agent-memory-context-management.md`
- 数据安全合规：`ai-data-security-and-compliance-playbook.md`
- 红队与安全评测：`ai-red-team-and-safety-evaluation.md`
- 发布门禁与回滚：`ai-release-readiness-and-rollback-gate.md`
- 可观测与值班：`ai-observability-and-oncall-runbook.md`
- 成本与容量优化：`ai-cost-capacity-optimization-playbook.md`
- 成熟度模型：`ai-governance-maturity-model.md`
- 阶段退出标准：`ai-stage-exit-criteria.yaml`
- 机器索引：`ai-catalog.yaml`

### 最小落地门禁
- 上线前必须通过准确性、安全性、延迟、成本四类指标门禁。
- 高风险能力必须配置人工确认、最小权限和完整审计链路。
- 生产变更必须具备灰度策略、回滚触发条件和演练记录。
