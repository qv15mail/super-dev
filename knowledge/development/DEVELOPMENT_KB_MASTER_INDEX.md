# 开发：Excellent（11964948@qq.com）

## 开发类完整知识库总索引（内置版）

### 目标
- 把开发类知识从“零散经验”升级为“可执行、可审计、可复用”的内置资产。
- 覆盖前端、后端、API、数据库、性能、并发、重构、评审、工程效能全链路。

### 使用原则
- 先查索引，再进入专题文档执行检查清单。
- 需求评审、架构评审、发布评审必须引用至少一个相关专题。
- 每次事故或重大变更后，更新对应专题的失败模式与检查项。

### 130+内置主题地图
- 前端工程：分层架构、设计系统、状态管理、性能预算、错误监控。
- 后端工程：服务边界、分层与领域建模、容错机制、消息架构、多环境治理。
- API治理：契约设计、鉴权授权、幂等防重、文档自动化、网关治理。
- 数据库工程：索引与慢SQL、分库分表、事务一致性、缓存一致性、数据生命周期。
- 性能工程：容量评估、线程连接池调优、热点治理、异步化改造、运行时调优。
- 并发稳定性：锁与CAS、分布式锁、任务调度、混沌演练、高可用容灾。
- 重构治理：重构路线、门禁策略、坏味道清单、演进重构、兼容迁移。
- 代码评审：评审标准、PR模板、风险审查、安全审查、性能审查。
- 工程效能：CI/CD标准化、DORA指标、Git策略、环境一致性、复盘机制。

### 专题入口
- 前端总册：`frontend-engineering-complete.md`
- 后端总册：`backend-engineering-complete.md`
- API总册：`api-governance-complete.md`
- 数据库总册：`database-engineering-complete.md`
- 性能总册：`performance-capacity-complete.md`
- 并发总册：`concurrency-reliability-complete.md`
- 重构总册：`refactor-migration-complete.md`
- 评审总册：`code-review-quality-complete.md`
- 效能总册：`engineering-effectiveness-complete.md`
- 开发安全总册：`security-in-development-complete.md`

### 知识库级结构入口
- 治理层：`00-governance/`
- 标准层：`01-standards/`
- 作战手册层：`02-playbooks/`
- 检查清单层：`03-checklists/`
- 反模式层：`04-antipatterns/`
- 案例层：`05-cases/`
- 术语层：`06-glossary/`
- 学习路径层：`07-learning-path/`
- 目录索引层：`08-catalog/catalog.yaml`
- 成熟度层：`09-maturity/`
- 知识图谱层：`10-knowledge-graph/`
- UI卓越层：`11-ui-excellence/`
- 全场景层：`12-scenarios/`
- 落地资产层：`13-implementation-assets/`
- 全流程层：`14-full-lifecycle/`
- 全流程模板层：`15-lifecycle-templates/`

### 自动审计入口
- 运行：`python scripts/audit_development_kb.py`
- 输出：总文件数、分层覆盖、缺失分层、知识库级达标状态
- 门禁：`python scripts/check_knowledge_gates.py --project-dir .`
- 阶段包：`python scripts/generate_lifecycle_packet.py --project-dir . --name your-packet`

### 执行门禁
- 需求进入开发前，必须完成 API 与数据模型检查。
- 合并前，必须完成测试、评审、安全三类检查。
- 发布前，必须完成发布门禁、回滚验证与指标基线确认。
