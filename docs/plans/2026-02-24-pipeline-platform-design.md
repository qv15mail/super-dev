# Super Dev 流水线平台化设计

> 日期: 2026-02-24
> 目标: 构建跨 CLI/IDE 的流水线式 AI Coding 辅助工具

## 1. 目标边界

核心目标是将 `super-dev "功能需求"` 打造成统一入口，完成以下能力链路：

1. 需求增强（联网检索 + 本地知识库）
2. 专业文档生成（PRD + 架构 + UI/UX）
3. Spec 规范生成
4. 前端优先实现（可演示骨架）
5. 后端 + 数据库迁移
6. 红队审查（安全 + 性能 + 架构）
7. 质量门禁（80+）
8. CI/CD 自动化交付

并支持技能安装与平台集成，覆盖：
- CLI: Claude Code / Codex CLI / OpenCode
- IDE: Cursor / Antigravity / Qoder / Trae / CodeBuddy

## 2. 架构方案对比

### 方案 A：单体命令分支（不推荐）
- 优点: 实现快
- 缺点: 命令膨胀，后期难维护

### 方案 B：核心流水线 + 适配层（推荐）
- 优点: pipeline 核心稳定，平台扩展解耦
- 缺点: 初期模块数量增加

### 方案 C：全插件化（暂缓）
- 优点: 扩展最灵活
- 缺点: 复杂度过高，不适合当前阶段

最终选择方案 B。

## 3. 组件设计

1. `KnowledgeAugmenter`
- 输入: 原始需求 + 领域
- 输出: 增强需求 + 研究报告
- 数据源: 本地 docs/spec/data + 联网搜索

2. `SkillManager`
- 能力: list/install/uninstall/targets
- 安装源: 本地目录、git 仓库、内置 skill
- 安装目标: 各平台对应目录

3. `IntegrationManager`
- 能力: list/setup/setup-all
- 输出: 各平台规则文件与适配提示

4. `Pipeline`
- 新增 Stage 0（需求增强）
- 维持前端先行 + 质量门禁 + 发布链路

## 4. 错误处理策略

1. 联网失败不阻断流水线（回退到本地知识）
2. skill 安装失败返回明确错误来源（路径、git、权限）
3. integrate 默认不覆盖，需 `--force`

## 5. 测试策略

1. 单元测试覆盖：
- 知识增强
- skill 安装/卸载
- integration 文件生成

2. 集成测试覆盖：
- CLI `skill targets`
- CLI `integrate setup`

3. 全量回归：
- `compileall`
- `pytest`

## 6. 后续扩展

1. 用 MCP / 向量库替换纯文本本地知识检索
2. 增加平台专用适配格式（非仅规则文件）
3. 增加 skill 远端目录索引与签名校验
