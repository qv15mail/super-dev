import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';
import type { SiteLocale } from '@/lib/site-locale';

const CHANGELOG = {
  zh: [
    { version: '2.3.4', date: '2026-04-10', type: 'patch' as const, changes: [
      '感谢 staruhub 提交并推动合入 PR #10，为编排系统补齐本次版本核心能力',
      '新增 Plan-Execute 执行引擎：支持结构化执行计划、拓扑排序、步骤级验证门、失败预算和持久化计划状态',
      '新增 Overseer 监督者角色：在阶段与步骤检查点持续观察偏差、质量下降和未解决的 Codex 审查结果，并可在关键问题出现时中止流水线',
      '新增 Claude Code + Codex 混合模式：允许 Claude Code 负责实现，Codex 负责独立审查，审查结果由 Overseer 统一跟踪',
      '扩展 orchestrator 配置：加入 execution_mode、overseer_enabled、codex_review_enabled 等控制项',
    ] },
    { version: '2.3.3', date: '2026-04-07', type: 'patch' as const, changes: [
      'Claude Code 统一为 super-dev 单一技能入口，消除 super-dev / super-dev-core 重复技能导致流水线不被遵循的问题',
      'super-dev update 升级后自动迁移所有宿主配置，super-dev 无参数入口自动检测旧版并迁移',
      'migrate.py 重写为全宿主迁移：自动检测所有已接入宿主，一键重建配置/Skill/slash/协议',
      '21 个宿主逐个对照官方文档深度适配：Roo Code/OpenCode 补齐 commands、Kilo Code 补齐 Skill、vscode-copilot 补齐认证',
      'commands 文件内容修复：之前 setup 写 .roo/commands/ 等文件时生成了错误的 rules 内容，现在正确生成 slash command 格式',
      '--auto 安装时同族宿主智能去重（cursor+cursor-cli 自动选 CLI 版）',
      '版本提示统一为 super-dev update，install.sh Skill 提示去除 super-dev-core 名称',
    ] },
    { version: '2.3.2', date: '2026-04-06', type: 'patch' as const, changes: [
      '21 个宿主口径继续收正：20 个统一接入宿主 + 1 个 OpenClaw 手动插件宿主，安装脚本、README、官网 Docs、能力审计页和站点矩阵统一到同一套真实模型',
      'Claude Code / Codex 继续深适配到官方协议：CLAUDE.md + skills + optional plugin enhancement、AGENTS.md + skills + repo plugin enhancement',
      'Kiro / Qoder / Cursor / Trae / CodeBuddy 等 IDE 宿主继续按真实 surface 深适配，避免代码、安装引导、文档和官网口径漂移',
      '恢复链继续产品化：resume / next / continue / doctor / validate / Web API 统一带现实场景卡，SESSION_BRIEF 直接告诉用户现实场景该怎么做',
      'workflow history、语义事件、hook history、workflow/framework/hook/operational harness、recent operational timeline 现在一起进入 proof-pack 与 release readiness',
      '跨平台框架 playbook 深化到 uni-app / Taro / React Native / Flutter / Desktop Web Shell，并接入脚手架、runtime、quality gate、release readiness 与 proof-pack',
      'UI 系统继续强化：emoji 被系统级禁止作为功能图标，UI 契约、token、图标库、组件生态、导航骨架、主题入口和 framework harness 全部进入交付门禁',
    ] },
    { version: '2.3.1', date: '2026-04-03', type: 'patch' as const, changes: [
      'Codex 深度适配升级为 AGENTS.md + Skills + repo plugin 双层模型，App/Desktop 与 CLI 统一进入同一条 Super Dev 流程',
      'Claude Code 深度适配升级为 CLAUDE.md + .claude/skills + ~/.claude/skills + optional plugin enhancement，并与安装引导、doctor、runtime 口径统一',
      '安装引导、Onboard、Doctor、Detect、Validate 改成当前真实宿主入口模型，不再用过期 slash/非 slash 二分法误导 Codex',
      '工作流动作卡、恢复链、Web API 决策卡继续统一，resume / next / continue / doctor / validate 语义进一步收口',
      'UI 契约、emoji 禁用、runtime 对齐、quality gate、release readiness 与 proof-pack 继续加固',
    ] },
    { version: '2.3.0', date: '2026-04-01', type: 'major' as const, changes: [
      '治理模式升级：从 Advisory（建议）到 Enforcement（执行），SKILL.md frontmatter hooks 自动注册 emoji 检查',
      '三层治理模型：CLAUDE.md 持久规则 + Hooks 运行时执行 + CLI 按需检查',
      'Agent Teams 协作支持：多位 Super Dev 专家可并行工作',
      '错误恢复 3 阶段策略：便宜恢复 → 上下文重建 → 暴露错误',
      'CLAUDE.md 知识文件引用：宿主自动加载对应技术栈 knowledge/ 文件',
      '编码前门禁 7 步强制确认：技术栈预研 → 配置 → 图标 → 组件 → API → token → 构建',
      'Enforcement 系统：super-dev enforce install/validate/status',
      '记忆系统：4 种记忆类型 + Dream 整合器',
      '组件脚手架 + API 契约类型 + Next.js 脚手架生成器',
      '对抗性验证专家 + 三 Agent 并行审查',
      '12 位 Markdown 专家 + 条件规则 + Pipeline 状态/成本追踪',
      '命令路由：所有命令在宿主内输入，终端只需 pip install + super-dev',
      '支持 21 个宿主：20 个统一接入宿主 + 1 个 OpenClaw 手动插件宿主，并持续完善项目模板与 Shell 补全',
      '统一错误处理 + E2E 测试 + 1671 单元测试通过',
    ] },
    { version: '2.2.0', date: '2026-03-29', type: 'major' as const, changes: [
      '系统级大升级：宿主接入、流程恢复、UI 系统、质量门禁、交付闭环整体重构',
      '工作流恢复链重构：新增 super-dev resume，裸跑 super-dev 自动进入恢复路由，SESSION_BRIEF.md 和 workflow-state.json 成为统一恢复真源',
      'preview confirmation 升级为正式一等门禁，next/continue/resume/start/doctor/detect/Web API 统一到同一套 workflow_state 语义',
      '宿主接入大幅强化：20 个统一接入宿主 + 1 个 OpenClaw 手动插件宿主，doctor/detect/start 统一决策卡引导',
      '宿主发现深度增强：PATH 检测 + 常见安装路径 + Windows App Paths + Windows shim + 自定义路径覆盖 SUPER_DEV_HOST_PATH_<HOST>',
      'UI 系统真正接入主流程：需求阶段即启动 UI 系统，生成并冻结视觉方向/字体/配色/图标/组件/Design Tokens',
      '新增 output/*-ui-contract.json 作为 UI 真源，前端骨架和实现骨架全程继承',
      'UI review 升级：检查图标系统/字体组合/组件生态/组件导入/token 接入/token 使用率/主题入口/导航骨架/反模式约束',
      '功能图标层面明确禁用 emoji，禁止紫/粉渐变主视觉，shadcn/ui + Radix + Tailwind 作为偏向主线',
      '知识推送引擎：每阶段自动推送相关知识约束（306 文件索引，7 阶段映射，L1/L2/L3 渐进式加载）',
      '知识自演化：SQLite 追踪使用效果，数据驱动权重优化',
      '可编程验证规则引擎：25 条 YAML 声明式规则（14 默认 + 11 红队），支持项目级自定义',
      '质量顾问：主动质量建议，Quick Wins 优先排序，不只说"不达标"还说"怎么修"',
      '专家系统四层武装：Profile + Knowledge + Rules + Protocol，11 个深度 Playbook（每个 350+ 行）',
      '交叉审查引擎：多专家视角自动审查交付物',
      'Spec-Code 一致性检测：防止代码偏离 Spec 描述',
      'Pipeline 效能度量：DORA 五指标 + Rework Rate + 等级评定（Elite/High/Medium/Low）',
      'ADR 自动生成：从架构配置自动生成架构决策记录',
      'Prompt 模板版本化：文档生成 Prompt 可迭代优化',
      '外部审查集成：支持 CodeRabbit/Qodo/GitHub PR 审查结果导入',
      'A2A 协议支持：5 个 Agent Cards，支持外部 Agent 调用',
      '结构化输出 Schema：5 个 JSON Schema 定义，确保治理输出可验证',
      'Web API 认证：X-Super-Dev-Key 环境变量控制',
      'OpenClaw 插件升级至 20 个 Tool，SKILL.md 精简为 145 行引导',
      '知识库扩展至 300+ 文件 / 15 万行，覆盖 23 个技术领域',
      '核心模块大幅增强：redteam(+686行)/code_review(+413行)/delivery(+661行)/ui_intelligence(+818行)/implementation_builder(+941行) 等 9 个模块',
      '质量门禁/proof-pack/release readiness/frontend runtime/delivery 全部接入 UI contract 检查',
      'P0 修复：resume 恢复上下文 / intelligence 真搜索 / 质量门禁深度检查 / API 认证 / 中英文知识匹配',
      '声明式红队规则/自定义规则/零源码场景等回归修复',
      '终端 UI 自适应：Table/Panel 随窗口大小自动调整，滚动窗口避免小窗口溢出',
      'Unicode 检测升级（Inquirer.js 风格），光标统一为纯 ASCII > 跨平台兼容',
      '全量测试：1600+ passed，Python 代码 76K+ 行',
    ] },
    { version: '2.1.6', date: '2026-03-27', type: 'patch' as const, changes: ['统一 Python 包、CLI、README、官网和宿主技能文案版本到 2.1.6', '修复宿主接入对旧版规则文件的自动刷新与自愈流程', '为全部 25 个宿主补齐 onboard/setup 隔离矩阵验证并全部通过', '避免质量审查可选依赖阻塞 host onboarding/start 入口'] },
    { version: '2.1.5', date: '2026-03-26', type: 'patch' as const, changes: ['修复 Windows 下 uv tool upgrade 文件锁定问题（自动重试 + 清晰提示）', '新增 super-dev clean 命令（清理历史产物，支持 --keep/--all/--dry-run）', '6 人 Agent 团队全项目深度审查，修复 37 个 bug（含 3 个 P0 崩溃、12 个 P1 逻辑错误）', '修复 proof-pack rehearsal 状态始终为 ready 的问题', '修复 Sequelize/Jenkins/TypeORM 生成代码的语法错误', '新增路径遍历安全防护（specs delete/change 操作）', '质量评分计算从整数截断改为四舍五入', '官网新增案例展示页（20+ 个真实项目）', '官网更新日志补全全部 18 个历史版本（1.0.0 ~ 2.1.5）'] },
    { version: '2.1.3', date: '2026-03-25', type: 'patch' as const, changes: ['OpenClaw 插件升级至 13 个 Tool（新增 deploy/analyze/doctor）', 'SKILL.md 全面重写至 481 行，完整覆盖 9 阶段执行指令、2 门禁交互模板、3 返工协议、resume 恢复智能', '修复 init 必填参数 name 缺失、quality --threshold 不存在、deploy --platform 应为 --cicd、pipeline --frontend 选项集错误等致命 CLI 映射问题', '新增 4 篇参考文档（commands/pipeline-stages/expert-roles/gate-interactions，共 883 行）', '补全 spec propose/scaffold 完整参数、domain 枚举（auth/content/saas）、review status 枚举（pending_review）', 'Skill 已发布至 ClawHub，用户可通过 clawhub install super-dev 安装'] },
    { version: '2.1.2', date: '2026-03-24', type: 'major' as const, changes: ['新增 OpenClaw 原生插件（@super-dev/openclaw-plugin），通过 Plugin SDK 注册 13 个专用 Tool', '宿主矩阵扩展至 21 个（新增 OpenClaw 为第 29 个宿主）', '修复 50+ 个 bug：delete_spec 删错目录、Prisma nullable 反转、TypeORM 语法错误、CLI console 崩溃等', '新增 backend/src/app.js 入口文件和 frontend/src/App.tsx 根组件', '补全 3 个缺失的后端路由（core/experience/operation）', '修复 7 个后端 repository 的 ID 覆盖漏洞和生成策略', '修复 HSL 色彩算法、asyncio 弃用 API、SQLAlchemy 迁移语法等'] },
    { version: '2.1.1', date: '2026-03-21', type: 'major' as const, changes: ['新增直接命令模式：super-dev "需求描述" 一行启动完整流水线', '新增 Expert Agent 专家智能体系统，根据项目领域自动激活领域专家', '新增阶段跳转指令 super-dev run <stage_number>，支持跳过已完成阶段直接推进', '质量门禁新增 A11y 无障碍检查（WCAG 2.1 AA），确保交付产物的可访问性', '升级流水线引擎，优化阶段间状态传递与恢复机制'] },
    { version: '2.1.1', date: '2026-03-20', type: 'patch' as const, changes: ['对外主推宿主矩阵收敛到 16 个热门宿主，减少实验宿主带来的不稳定预期', '新增显式 Bugfix Mode（super-dev fix），修复缺陷时走轻量补丁路径', '新增 Repo Map、Feature Checklist、Impact、Regression Guard、Dependency Graph，形成完整代码库理解与范围覆盖审计链路', '新增 Host Validation Center 能力：宿主前置条件诊断、运行时验收状态和交付就绪摘要', '新增 integrate harden、spec scaffold / quality、run --status / --phase / --jump / --confirm 等流程控制指令', '新增可直接输入的流程控制捷径：super-dev status、super-dev run research/prd/architecture/uiux/frontend/backend/quality、super-dev jump <stage>、super-dev confirm <phase>', '升级 Proof Pack 与 Release Readiness，加入 Scope Coverage，明确区分流程完成与范围完成'] },
    { version: '2.1.0', date: '2026-03-21', type: 'major' as const, changes: ['10 专家 Agent 系统：PM/ARCHITECT/UI/UX/SECURITY/CODE/DBA/QA/DEVOPS/RCA，每位专家含完整画像、思维框架与质量标准', '20 宿主完美适配：新增 Copilot CLI/Kilo Code/Cline/Roo Code，修正 Cursor .mdc/Windsurf rules/Kiro steering 格式', '119 种配色方案（含暗色模式自动生成）+ 39 个组件库 + 17 种字体预设', '新增直接命令模式 super-dev "需求" 和阶段跳转 super-dev run 1-9'] },
    { version: '2.0.12', date: '2026-03-23', type: 'patch' as const, changes: ['修复版本对齐和发布流程问题', '优化 PyPI 包构建和元数据'] },
    { version: '2.0.11', date: '2026-03-15', type: 'patch' as const, changes: ['UI Intelligence 大幅扩充：配色方案从 7 种扩至 84 种 + 35 种美学方向', '组件库推荐从 12 个扩至 39 个，覆盖 React/Vue/Angular/Svelte/小程序/RN/Flutter', '新增 17 种产品专属字体预设（Google Fonts 中国镜像）', '新增 12 项交付前检查清单、9 个行业信任规则', 'UIUX 文档新增色阶系统、语义色、组件 CSS 规格、阴影层级、动效规范'] },
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['新增显式 bootstrap 初始化产物（.super-dev/WORKFLOW.md 与 output/*-bootstrap.md）', '新增宿主运行时真人验收命令 integrate validate 与状态记录', '新增 release proof-pack 交付证据包，并在 Web 管理台展示完整度、阻塞项与关键证据', '修复 analyzer 将 .venv / site-packages 误纳入项目分析的问题', '恢复 bugfix 轻量路径、澄清问题与默认时序图输出'] },
    { version: '2.0.9', date: '2026-03-11', type: 'patch' as const, changes: ['新增 Impact Analysis 变更影响分析', '新增 Feature Checklist PRD 范围覆盖率审计', '优化流水线阶段间状态传递'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['修复宿主检测在特定环境下的兼容性问题', '优化 pipeline-contract 输出格式', '新增 Antigravity 宿主实验性支持'] },
    { version: '2.0.7', date: '2026-03-07', type: 'patch' as const, changes: ['修复 Skill 安装路径解析、slash 命令注册和宿主检测的多个边缘问题', '优化 CI/CD 配置生成的 YAML 格式'] },
    { version: '2.0.6', date: '2026-03-07', type: 'patch' as const, changes: ['修复 Windsurf rules 路径、Kiro steering frontmatter 格式', '优化宿主规则文件的内容一致性'] },
    { version: '2.0.5', date: '2026-03-07', type: 'patch' as const, changes: ['修复 Cursor .mdc frontmatter 格式兼容性', '优化 Codex CLI 的 Flow Contract 注入'] },
    { version: '2.0.4', date: '2026-03-07', type: 'patch' as const, changes: ['优化宿主适配器的检测逻辑和错误提示', '修复多个宿主的 slash 命令路径'] },
    { version: '2.0.3', date: '2026-03-05', type: 'patch' as const, changes: ['宿主适配器扩展：新增 Kilo Code、Cline、Roo Code 支持', 'Skill-only 模式：宿主仅安装 Skill 无需 slash 命令'] },
    { version: '2.0.2', date: '2026-03-05', type: 'patch' as const, changes: ['宿主级工作流隔离：每个宿主独立的协议面和状态', '修复多宿主并发接入时的文件冲突'] },
    { version: '2.0.1', date: '2026-03-02', type: 'patch' as const, changes: ['完善工作流文档和任务闭环逻辑', '修复 Spec 任务状态持久化问题'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['重构 12 阶段流水线引擎，支持全流程恢复（run --resume）', '新增 enterprise 策略预设', '新增 delivery archive 完整交付包生成', '新增宿主画像与兼容性评分系统', '新增红队审查三维度检查（安全 / 性能 / 架构）', '新增 UI Review 审查', '支持更多宿主'] },
    { version: '1.0.1', date: '2026-01-04', type: 'patch' as const, changes: ['新增完整工作流教程 (WORKFLOW_GUIDE.md)', '整合设计智能引擎（配色、字体、图表推荐）', '新增 Landing 页面模式生成器', '新增 UX 指南数据库'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['首次发布', '基础流水线框架（research / documents / spec / implement）', 'Spec-Driven Development 模块', '支持 Claude Code、Cursor、Windsurf 宿主', 'PyPI 正式发布'] },
  ],
  en: [
    { version: '2.3.4', date: '2026-04-10', type: 'patch' as const, changes: [
      'Thanks to staruhub for PR #10, which landed the core orchestration capabilities in this release',
      'Added the Plan-Execute engine with structured plans, topological wave sorting, step-level verification gates, failure budgets, and persisted plan state',
      'Added the Overseer role to monitor phase and step checkpoints, detect drift and quality drops, and halt the pipeline on critical issues',
      'Added a Claude Code + Codex hybrid mode so Claude can implement while Codex performs independent review tracked by the Overseer',
      'Expanded orchestrator configuration with execution_mode, overseer_enabled, codex_review_enabled, and related controls',
    ] },
    { version: '2.3.3', date: '2026-04-07', type: 'patch' as const, changes: [
      'Claude Code unified to a single super-dev skill entry, eliminating duplicate super-dev / super-dev-core skills that caused pipeline non-compliance',
      'super-dev update now auto-migrates all host configs after upgrade; super-dev (no args) auto-detects and migrates outdated projects',
      'migrate.py rewritten for all-host migration: auto-detects onboarded hosts and rebuilds configs/Skills/slash/protocols in one step',
      'All 21 hosts verified against official docs: Roo Code/OpenCode commands added, Kilo Code skill added, vscode-copilot certification added',
      'Fixed command file content bug: setup previously generated wrong rules content for .roo/commands/ etc., now correctly generates slash command format',
      'Auto-detect deduplicates same-family hosts (cursor+cursor-cli picks CLI variant)',
      'Version hint unified to super-dev update; install.sh skill prompt removed super-dev-core naming',
    ] },
    { version: '2.3.2', date: '2026-04-06', type: 'patch' as const, changes: [
      'Host product scope was hardened again: 20 unified integration hosts plus 1 manual OpenClaw plugin host, with install scripts, README, website docs, capability audit, and host matrices finally sharing one accurate model',
      'Claude Code and Codex moved further toward their official host contracts: CLAUDE.md + skills + optional plugin enhancement, and AGENTS.md + skills + repo plugin enhancement',
      'Kiro, Qoder, Cursor, Trae, and CodeBuddy family hosts were deepened around their real surfaces so code, onboarding, docs, and website no longer drift',
      'Recovery UX became more productized: resume / next / continue / doctor / validate / Web API now expose scenario cards, and SESSION_BRIEF directly tells users what to do in real situations',
      'workflow history, semantic events, hook history, workflow/framework/hook/operational harnesses, and the recent operational timeline now all feed proof-pack and release readiness',
      'Cross-platform framework playbooks for uni-app / Taro / React Native / Flutter / Desktop Web Shell now drive scaffolds, runtime checks, quality gates, release readiness, and proof-pack',
      'The UI system was tightened further: emoji are systemically banned as functional icons, and UI contracts, tokens, icon libraries, component ecosystems, navigation shells, theme entry points, and framework harness checks now all participate in delivery gates',
    ] },
    { version: '2.3.1', date: '2026-04-03', type: 'patch' as const, changes: [
      'Codex deep adaptation upgraded to the official AGENTS.md + Skills + repo plugin dual-layer model, with App/Desktop and CLI converging into one Super Dev flow',
      'Claude Code deep adaptation now follows a CLAUDE.md + .claude/skills + ~/.claude/skills + optional plugin enhancement model with unified onboarding, doctor, and runtime semantics',
      'Onboarding, doctor, detect, and validate now reflect the real host entry model instead of the old slash-vs-text simplification for Codex',
      'Workflow action cards, recovery chain, and Web API decision cards were unified further across resume / next / continue / doctor / validate',
      'UI contract enforcement, emoji blocking, runtime alignment, quality gate, release readiness, and proof-pack were hardened again',
    ] },
    { version: '2.3.0', date: '2026-04-01', type: 'major' as const, changes: [
      'Governance upgrade: Advisory → Enforcement mode with SKILL.md frontmatter hooks',
      'Three-layer governance: CLAUDE.md persistent rules + Hooks runtime enforcement + CLI on-demand checks',
      'Agent Teams support: parallel expert collaboration across pipeline phases',
      '3-stage error recovery: cheap recovery → context rebuild → surface error',
      'CLAUDE.md include directive: auto-load tech stack knowledge from knowledge/ files',
      'Pre-code gate: 7-step mandatory checklist (tech research → config → icons → components → API → tokens → build)',
      'Enforcement system: super-dev enforce install/validate/status',
      'Memory system: 4 types (user/feedback/project/reference) + Dream consolidator',
      'Code generators: component scaffold, API contract types, Next.js scaffold',
      'Adversarial verification agent + 4-way parallel review (reuse/quality/efficiency/security)',
      '12 Markdown expert definitions + conditional rules + pipeline state/cost tracking',
      'Command routing: all commands via /super-dev in host, terminal only for pip install + super-dev',
      'Support for 21 hosts: 20 unified integration hosts plus 1 manual OpenClaw plugin host, with continued improvements to project templates and shell completion',
      'Unified error handling + 22 E2E tests + 1671 unit tests passing',
    ] },
    { version: '2.2.0', date: '2026-03-29', type: 'major' as const, changes: [
      'System-level upgrade: host onboarding, workflow recovery, UI system, quality gates, delivery closure — all rebuilt',
      'Workflow recovery chain: new super-dev resume, bare super-dev auto-enters recovery route, SESSION_BRIEF.md as unified recovery source',
      'Preview confirmation upgraded to first-class gate; next/continue/resume/start/doctor/detect/Web API unified to workflow_state semantics',
      'Host onboarding: 20 unified hosts + 1 OpenClaw manual plugin host, doctor/detect/start with decision cards',
      'Deep host discovery: PATH + common install paths + Windows App Paths + Windows shim + custom SUPER_DEV_HOST_PATH_<HOST>',
      'UI system fully integrated into pipeline: UI contract frozen at requirement phase (visual direction, fonts, colors, icons, components, design tokens)',
      'New output/*-ui-contract.json as UI source of truth, inherited by frontend scaffolds and implementations',
      'UI review upgraded: icon system, font combos, component ecosystem, token adoption rate, theme entry, nav shell, anti-pattern constraints',
      'Emoji banned as functional icons, purple/pink gradients banned, shadcn/ui + Radix + Tailwind as preferred stack',
      'Knowledge Push Engine: per-phase auto-push (306 files indexed, 7 phases, L1/L2/L3 progressive loading)',
      'Knowledge Evolution: SQLite usage tracking with data-driven weight optimization',
      'Programmable Validation Rules: 25 YAML rules (14 default + 11 redteam), project-level customizable',
      'Quality Advisor: proactive suggestions with Quick Wins prioritization',
      'Expert System 4-layer: Profile + Knowledge + Rules + Protocol, 11 deep Playbooks (350+ lines each)',
      'Cross-Review Engine: multi-expert artifact validation',
      'Spec-Code Consistency Checker: detect code drift from spec',
      'Pipeline Metrics: DORA 5 indicators + Rework Rate + level rating (Elite/High/Medium/Low)',
      'ADR Auto-Generation from architecture config',
      'Prompt Template Versioning for iterative optimization',
      'External Review Integration: CodeRabbit/Qodo/GitHub PR import',
      'A2A Protocol: 5 Agent Cards for external agent interop',
      'Structured Output Schemas: 5 JSON Schema definitions',
      'Web API Authentication: X-Super-Dev-Key env var control',
      'OpenClaw plugin: 13 → 20 Tools, SKILL.md streamlined to 145 lines',
      'Knowledge base expanded to 270+ files / 150K lines across 23 domains',
      'P0 fixes: resume context restoration, real search API, quality gate depth, API auth',
      'Terminal UI responsive: Tables and Panels auto-adapt to window size',
      'Test coverage: 1600+ tests, 76K+ lines Python code',
    ] },
    { version: '2.1.6', date: '2026-03-27', type: 'patch' as const, changes: ['Aligned Python package, CLI, README, website, and host skill surfaces to version 2.1.6', 'Fixed self-healing refresh for stale host integration files during onboarding', 'Validated isolated onboard/setup matrices for all 25 hosts with full pass', 'Prevented optional quality-review dependencies from blocking host onboarding/start entrypoints'] },
    { version: '2.1.5', date: '2026-03-26', type: 'patch' as const, changes: ['Fixed Windows uv tool upgrade file lock issue (auto-retry + clear guidance)', 'Added super-dev clean command (clean historical artifacts with --keep/--all/--dry-run)', '6-agent team deep audit: fixed 37 bugs (3 P0 crashes, 12 P1 logic errors)', 'Fixed proof-pack rehearsal status always showing ready', 'Fixed Sequelize/Jenkins/TypeORM generated code syntax errors', 'Added path traversal security protection for specs delete/change operations', 'Quality scoring changed from integer truncation to rounding', 'Added showcase page with 20+ real project cases', 'Changelog now includes all 18 historical versions (1.0.0 ~ 2.1.5)'] },
    { version: '2.1.3', date: '2026-03-25', type: 'patch' as const, changes: ['OpenClaw plugin upgraded to 13 Tools (added deploy/analyze/doctor)', 'SKILL.md fully rewritten to 481 lines covering 9-stage execution instructions, 2 gate interaction templates, 3 rework protocols, and resume intelligence', 'Fixed critical CLI mapping bugs: init missing required name arg, quality --threshold nonexistent, deploy --platform should be --cicd, pipeline --frontend choices incorrect', 'Added 4 reference documents (commands/pipeline-stages/expert-roles/gate-interactions, 883 lines total)', 'Completed spec propose/scaffold params, domain enum (auth/content/saas), review status enum (pending_review)', 'Skill published to ClawHub, users can install via clawhub install super-dev'] },
    { version: '2.1.2', date: '2026-03-24', type: 'major' as const, changes: ['Added OpenClaw native plugin (@super-dev/openclaw-plugin) with 13 registered tools via Plugin SDK', 'Expanded host matrix to 21 (OpenClaw added as 29th host)', 'Fixed 50+ bugs: delete_spec wrong directory, Prisma nullable inverted, TypeORM syntax error, CLI console crash, etc.', 'Added missing backend/src/app.js entry and frontend/src/App.tsx root component', 'Added 3 missing backend routes (core/experience/operation)', 'Fixed ID override vulnerability and generation strategy in 7 backend repositories', 'Fixed HSL color algorithm, asyncio deprecated API, SQLAlchemy migration syntax, and more'] },
    { version: '2.1.1', date: '2026-03-21', type: 'major' as const, changes: ['Added direct command mode: super-dev "requirement" launches the full pipeline in one line', 'Added Expert Agent system that auto-activates domain specialists based on project context', 'Added stage jump command super-dev run <stage_number> to skip completed stages and advance directly', 'Quality gate now includes A11y accessibility checks (WCAG 2.1 AA) to ensure deliverable accessibility', 'Upgraded pipeline engine with improved inter-stage state transfer and recovery'] },
    { version: '2.1.1', date: '2026-03-20', type: 'patch' as const, changes: ['Focused the public host matrix on 16 primary hosts instead of advertising unstable lab adapters', 'Added explicit Bugfix Mode through super-dev fix so defect work follows a lightweight patch path', 'Added Repo Map, Feature Checklist, Impact, Regression Guard, and Dependency Graph as a complete codebase-intelligence and scope-audit chain', 'Added Host Validation Center capabilities for host prerequisites, runtime acceptance state, and delivery readiness summaries', 'Added workflow-control commands including integrate harden, spec scaffold / quality, and run --status / --phase / --jump / --confirm', 'Added direct workflow shortcuts: super-dev status, super-dev run research/prd/architecture/uiux/frontend/backend/quality, super-dev jump <stage>, and super-dev confirm <phase>', 'Upgraded Proof Pack and Release Readiness with Scope Coverage so pipeline completion is distinct from full scope completion'] },
    { version: '2.1.0', date: '2026-03-21', type: 'major' as const, changes: ['10 Expert Agent system: PM/ARCHITECT/UI/UX/SECURITY/CODE/DBA/QA/DEVOPS/RCA with full profiles, thinking frameworks, and quality standards', '20 host adapters: added Copilot CLI/Kilo Code/Cline/Roo Code, fixed Cursor .mdc/Windsurf rules/Kiro steering formats', '119 color schemes (with dark mode auto-generation) + 39 component libraries + 17 font presets', 'Added direct command mode super-dev "requirement" and stage jump super-dev run 1-9'] },
    { version: '2.0.12', date: '2026-03-23', type: 'patch' as const, changes: ['Fixed version alignment and release pipeline', 'Improved PyPI package build and metadata'] },
    { version: '2.0.11', date: '2026-03-15', type: 'patch' as const, changes: ['UI Intelligence major expansion: color schemes from 7 to 84 + 35 aesthetic directions', 'Component library recommendations expanded from 12 to 39 covering React/Vue/Angular/Svelte/Mini Programs/RN/Flutter', 'Added 17 product-specific font presets (Google Fonts China mirror)', 'Added 12 pre-delivery checklists and 9 industry trust rules', 'UIUX docs now include color scale system, semantic colors, component CSS specs, shadow levels, motion specs'] },
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['Added explicit bootstrap artifacts (.super-dev/WORKFLOW.md and output/*-bootstrap.md)', 'Added integrate validate for host runtime acceptance with persisted status', 'Added release proof-pack and surfaced completion, blockers, and key artifacts in the Web console', 'Fixed analyzer scope so .venv / site-packages are excluded from project analysis', 'Restored lightweight bugfix flow, clarification prompts, and default sequence diagrams'] },
    { version: '2.0.9', date: '2026-03-11', type: 'patch' as const, changes: ['Added Impact Analysis for change scope assessment', 'Added Feature Checklist for PRD coverage audit', 'Improved inter-stage state transfer in pipeline'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed host detection issues in edge environments', 'Improved pipeline-contract output format', 'Added experimental support for Antigravity'] },
    { version: '2.0.7', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed skill install path resolution, slash command registration, and host detection edge cases', 'Improved CI/CD YAML generation format'] },
    { version: '2.0.6', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed Windsurf rules path and Kiro steering frontmatter format', 'Improved host rule file content consistency'] },
    { version: '2.0.5', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed Cursor .mdc frontmatter compatibility', 'Improved Codex CLI Flow Contract injection'] },
    { version: '2.0.4', date: '2026-03-07', type: 'patch' as const, changes: ['Improved host adapter detection logic and error messages', 'Fixed slash command paths for multiple hosts'] },
    { version: '2.0.3', date: '2026-03-05', type: 'patch' as const, changes: ['Host adapter expansion: added Kilo Code, Cline, Roo Code', 'Skill-only mode: hosts can install skill without slash command'] },
    { version: '2.0.2', date: '2026-03-05', type: 'patch' as const, changes: ['Host-scoped workflow isolation: independent protocol surfaces per host', 'Fixed file conflicts during concurrent multi-host onboarding'] },
    { version: '2.0.1', date: '2026-03-02', type: 'patch' as const, changes: ['Finalized workflow documentation and task-closure hardening', 'Fixed spec task status persistence'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['Rebuilt the 12-stage pipeline engine with run --resume support', 'Added enterprise policy preset', 'Added full delivery archive packaging', 'Added host profile and compatibility scoring', 'Added three-dimensional red-team review', 'Added UI Review checks', 'Expanded host coverage'] },
    { version: '1.0.1', date: '2026-01-04', type: 'patch' as const, changes: ['Added complete workflow tutorial (WORKFLOW_GUIDE.md)', 'Integrated design intelligence engine (colors, fonts, charts)', 'Added landing page pattern generator', 'Added UX guideline database'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['Initial release', 'Base pipeline framework (research / documents / spec / implement)', 'Spec-Driven Development module', 'Support for Claude Code, Cursor, and Windsurf', 'Official PyPI release'] },
  ],
} as const;

const COPY = {
  zh: { title: '更新日志', body: 'Super Dev 版本历史。查看', link: 'GitHub 完整记录', major: '主版本', patch: '修复' },
  en: { title: 'Changelog', body: 'Version history for Super Dev. See the', link: 'full GitHub changelog', major: 'Major', patch: 'Patch' },
} as const;

export function ChangelogPageContent({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  const releases = CHANGELOG[locale];
  const typeBadge = { major: <Badge variant="certified">{copy.major}</Badge>, patch: <Badge variant="compatible">{copy.patch}</Badge> };
  return (
    <>
      <Nav locale={locale} />
      <main className="pt-14 min-h-screen" id="main-content">
        <section className="py-20 lg:py-24 bg-bg-primary">
          <div className="max-w-2xl mx-auto px-4 sm:px-6">
            <h1 className="text-4xl font-bold text-text-primary mb-2 tracking-tight">{copy.title}</h1>
            <p className="text-text-muted mb-12">{copy.body}{' '}<a href="https://github.com/shangyankeji/super-dev/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer" className="text-accent-blue hover:text-accent-blue-hover transition-colors">{copy.link}</a></p>
            <div className="space-y-10">
              {releases.map((release) => (
                <article key={release.version} className="relative pl-6 border-l border-border-default">
                  <div className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-accent-blue border-2 border-bg-primary" aria-hidden="true" />
                  <header className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-mono font-bold text-text-primary">v{release.version}</h2>
                    {typeBadge[release.type]}
                    <time dateTime={release.date} className="text-sm text-text-muted">{release.date}</time>
                  </header>
                  <ul className="space-y-2" role="list">
                    {release.changes.map((change) => <li key={change} className="text-sm text-text-secondary flex items-start gap-2"><span className="text-text-muted mt-0.5">-</span>{change}</li>)}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </>
  );
}
