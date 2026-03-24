# Super Dev 9 阶段流水线详解

## 阶段 0: Research（需求增强）

- 解析用户需求，检测场景（新功能/Bug 修复）
- 读取本地知识库 `knowledge/`
- 加载知识缓存 `output/knowledge-cache/*-knowledge-bundle.json`
- 联网研究同类产品（如果非离线模式）
- 输出: `output/*-research.md`

## 阶段 1: PRD（产品需求文档）

- PM 专家生成完整 PRD
- 包含: 产品愿景、目标用户、功能需求、非功能需求、验收标准
- 输出: `output/*-prd.md`

## 阶段 2: Architecture（架构设计）

- ARCHITECT 专家生成系统架构
- 包含: 技术栈选型、模块划分、API 设计、数据库建模、部署架构
- 输出: `output/*-architecture.md`

## 阶段 3: UIUX（UI/UX 设计）

- UI + UX 专家生成设计规范
- 包含: 设计系统、组件规范、页面蓝图、交互流程、色彩方案
- 输出: `output/*-uiux.md`

## DOC_CONFIRM_GATE（文档确认门禁）

- 三份核心文档（PRD + Architecture + UIUX）完成后必须暂停
- 等待用户明确确认后才能继续
- 未经确认不得创建 Spec 或开始编码

## 阶段 4: Spec（任务拆解）

- 将需求拆解为可执行的 Task
- 按优先级排序，前端优先
- 输出: `.super-dev/changes/*/proposal.md` + `.super-dev/changes/*/tasks.md`

## 阶段 5: Frontend（前端实现）

- 先交付前端，做到可预览
- 运行时验证
- UI 质量审查
- 输出: `frontend/` 目录下的实现代码

## PREVIEW_CONFIRM_GATE（预览确认门禁）

- 前端预览完成后必须暂停
- 等待用户确认前端效果
- 确认后才继续后端实现

## 阶段 6: Backend（后端实现）

- API 开发、数据库迁移、单元测试、集成测试
- 输出: `backend/` 目录下的实现代码

## 阶段 7: Quality（质量门禁）

- 红队审查: 安全 / 性能 / 架构三维度
- 质量评分: 0-100，必须达到阈值（默认 80）
- 输出: `output/*-quality-gate.md`, `output/*-redteam.md`

## 阶段 8: Delivery（交付与部署）

- CI/CD 配置生成
- 部署演练
- 交付证明包
- 发布就绪度检查
- 输出: CI/CD 配置文件 + `output/*-proof-pack.*`
