import Link from 'next/link';
import type { LucideIcon } from 'lucide-react';
import {
  ArrowRight,
  BookOpen,
  Boxes,
  Command,
  FolderTree,
  LifeBuoy,
  Package,
  RefreshCw,
  Search,
  Sparkles,
  Terminal,
  Workflow,
  Zap,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { CopyCommand } from '@/components/ui/CopyCommand';
import { localizedPath, type SiteLocale } from '@/lib/site-locale';

const SLASH_HOSTS = [
  'claude-code',
  'codebuddy',
  'codebuddy-cli',
  'cursor',
  'cursor-cli',
  'gemini-cli',
  'kiro-cli',
  'opencode',
  'qoder',
  'qoder-cli',
  'windsurf',
  'antigravity',
] as const;

const TEXT_TRIGGER_HOSTS = ['codex-cli', 'kiro', 'trae', 'vscode-copilot'] as const;

type SectionLink = { id: string; label: string; icon: LucideIcon };
type SurfaceGroup = { title: string; body: string; points: string[] };
type TriggerCard = { title: string; command: string; hosts: readonly string[]; note: string; variant: 'certified' | 'compatible' };
type PipelineStep = { step: string; title: string; body: string };
type Content = {
  heroKicker: string;
  heroTitle: string;
  heroBody: string;
  heroStats: { label: string; value: string }[];
  sections: SectionLink[];
  governanceTitle: string;
  governanceBody: string;
  governanceCards: { title: string; body: string }[];
  installTitle: string;
  installBody: string;
  installBullets: string[];
  installCode: string;
  surfacesTitle: string;
  surfacesBody: string;
  surfaces: SurfaceGroup[];
  triggerTitle: string;
  triggerBody: string;
  triggerCards: TriggerCard[];
  matrixTitle: string;
  matrixBody: string;
  matrixGroups: { category: string; items: { host: string; protocol: string; grade: string; trigger: string }[] }[];
  pipelineTitle: string;
  pipelineBody: string;
  pipelineSteps: PipelineStep[];
  controlTitle: string;
  controlBody: string;
  controlCards: { title: string; body: string; code: string }[];
  operationsTitle: string;
  operationsBody: string;
  operationsCards: { title: string; body: string; bullets: string[] }[];
  commandsTitle: string;
  commandsBody: string;
  commands: { title: string; code: string; filename: string }[];
  troubleshootingTitle: string;
  troubleshootingBody: string;
  troubleshootingSteps: string[];
  smokeTitle: string;
  smokeCode: string;
  highlightsTitle: string;
  highlightsBody: string;
  highlightsCards: { title: string; body: string }[];
};

function gradeVariant(grade: string) {
  if (grade === 'Certified') return 'certified';
  if (grade === 'Compatible') return 'compatible';
  return 'experimental';
}

const zhContent: Content = {
  heroKicker: 'Documentation Center',
  heroTitle: '安装、接入、触发、流水线和交付，都从这里开始。',
  heroBody:
    '这份文档说明安装方式、宿主接入、触发方式、流水线、代码库理解、回归守卫、知识库、门禁和交付要求。',
  heroStats: [
    { label: '适配宿主', value: '20' },
    { label: '专家 Agent', value: '10' },
    { label: '核心阶段', value: '9 段' },
  ],
  sections: [
    { id: 'highlights', label: 'v2.3.1 新功能', icon: Zap },
    { id: 'governance', label: '产品定位', icon: BookOpen },
    { id: 'install', label: '安装方式', icon: Package },
    { id: 'surfaces', label: '接入面', icon: Boxes },
    { id: 'triggers', label: '触发方式', icon: Command },
    { id: 'hosts', label: '宿主矩阵', icon: Terminal },
    { id: 'pipeline', label: '流水线', icon: Workflow },
    { id: 'control', label: '流程控制', icon: RefreshCw },
    { id: 'operations', label: '知识与门禁', icon: FolderTree },
    { id: 'commands', label: '常用命令', icon: Package },
    { id: 'troubleshooting', label: '排障', icon: LifeBuoy },
  ],
  governanceTitle: 'Super Dev 负责规范宿主里的 AI 开发过程。',
  governanceBody:
    '宿主负责模型推理、联网检索、终端调用和真实编码。Super Dev 负责 research、三文档、确认门、Spec、前端验证、质量门禁和交付标准，把整个开发过程拉回同一条流水线。',
  governanceCards: [
    { title: '宿主负责执行', body: '模型、工具、联网、改代码、运行项目，这些都由宿主完成。' },
    { title: 'Super Dev 负责治理', body: '强制 research、三文档、确认门、前端运行验证、质量门禁和交付标准。' },
    { title: '项目产物可审计', body: 'research、PRD、Architecture、UI/UX、Spec、运行验证、交付报告都会落到文件。' },
  ],
  installTitle: '安装方式',
  installBody:
    '先把工具装好，再进入宿主接入引导。安装阶段只需要弄清三件事：会安装什么、不会安装什么、下一步怎么触发宿主开始工作。',
  installBullets: [
    'pip 或 uv 会自动安装 Super Dev 的 Python 依赖。',
    '不会自动安装 Claude Code、Cursor、Trae、Gemini CLI、VS Code Copilot 等宿主本体。',
    '终端输入 super-dev 后，会进入宿主安装引导，并把 21 个适配宿主的对应协议面写入宿主和项目。',
  ],
  installCode:
    'pip install -U super-dev\n# 或\nuv tool install super-dev\n\n# 打开安装引导\nsuper-dev\n\n# OpenClaw 用户额外安装\nopenclaw plugins install @super-dev/openclaw-plugin\n# 或安装 ClawHub Skill\nclawhub install super-dev\n\n# 更新到最新版\nsuper-dev update',
  surfacesTitle: '宿主接入面',
  surfacesBody:
    '不同宿主会读取不同的官方接入面。安装引导会把这些面写到项目级和用户级路径里，让宿主知道何时进入 Super Dev 流水线。',
  surfaces: [
    {
      title: 'Python CLI',
      body: '这是治理内核，负责安装、修复、状态、质量门禁、发布检查和交付逻辑。',
      points: ['super-dev', 'doctor / detect / update', 'review / quality / release readiness'],
    },
    {
      title: '宿主协议面',
      body: '宿主通过 commands、rules、AGENTS、steering、subagents、skills 这些官方机制读懂 Super Dev。',
      points: ['slash / text trigger', 'project-level surfaces', 'user-level surfaces'],
    },
    {
      title: '项目产物面',
      body: '知识库、三文档、Spec、运行验证、交付报告共同构成流水线状态。',
      points: ['knowledge/', 'output/*', '.super-dev/changes/*'],
    },
  ],
  triggerTitle: '触发方式',
  triggerBody: '只记住两种触发方式即可。协议细节放在宿主矩阵和接入面一节展开。',
  triggerCards: [
    {
      title: 'Slash 宿主',
      command: '/super-dev 你的需求',
      hosts: SLASH_HOSTS,
      note: '宿主会通过 commands / workflows / subagents / rules 进入 Super Dev 流水线。',
      variant: 'certified',
    },
    {
      title: '文本触发宿主',
      command: 'super-dev: 你的需求',
      hosts: TEXT_TRIGGER_HOSTS,
      note: '宿主会通过 AGENTS / project rules / steering / compatibility skill 理解这句文本触发词。',
      variant: 'compatible',
    },
  ],
  matrixTitle: '宿主矩阵',
  matrixBody: '这张矩阵列出每个宿主的触发方式、协议面和成熟度，方便在接入、排障和团队规范时统一判断。',
  matrixGroups: [
    {
      category: 'CLI',
      items: [
        { host: 'claude-code', protocol: '官方 commands + subagents', grade: 'Certified', trigger: '/super-dev' },
        { host: 'codex-cli', protocol: '官方 AGENTS.md + 官方 Skills', grade: 'Certified', trigger: 'super-dev:' },
        { host: 'opencode', protocol: '官方 commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'gemini-cli', protocol: '官方 commands + GEMINI.md', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro-cli', protocol: '官方 commands + AGENTS.md', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'cursor-cli', protocol: '官方 commands + rules', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'qoder-cli', protocol: '官方 commands + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'codebuddy-cli', protocol: '官方 commands + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'openclaw', protocol: 'Plugin SDK + ClawHub Skill', grade: 'Compatible', trigger: '/super-dev' },
      ],
    },
    {
      category: 'IDE',
      items: [
        { host: 'cursor', protocol: '官方 commands + rules', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'antigravity', protocol: '官方 commands + GEMINI.md + workflows', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro', protocol: '官方 project steering + global steering', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'qoder', protocol: '官方 commands + rules + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'trae', protocol: '官方 project rules + 兼容 Skill', grade: 'Compatible', trigger: 'super-dev:' },
        { host: 'vscode-copilot', protocol: '官方 copilot-instructions + AGENTS', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'codebuddy', protocol: '官方 commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'windsurf', protocol: '官方 workflows + skills', grade: 'Experimental', trigger: '/super-dev' },
      ],
    },
  ],
  pipelineTitle: '流水线',
  pipelineBody: '入口命令很短，真正重要的是后面的阶段纪律。宿主接到需求后会按研究、文档、确认、实现、验证和交付推进。',
  pipelineSteps: [
    { step: '01', title: '同类产品研究', body: '先使用宿主联网能力研究同类产品、交互模式、差异化机会和商业信号。' },
    { step: '02', title: '需求增强', body: '把边界条件、异常路径、验收口径和优先级补足，避免模糊需求直接进编码。' },
    { step: '03', title: '三份核心文档', body: '生成 PRD、Architecture、UI/UX 三文档，形成可审计的执行基线。' },
    { step: '04', title: '用户确认门', body: '三文档完成后强制暂停，用户确认前不得创建 Spec 或继续编码。' },
    { step: '05', title: 'Spec / Tasks', body: '确认通过后生成变更提案与任务清单，收紧范围和顺序。' },
    { step: '06', title: '前端优先', body: '先做前端、先跑起来、先可审查，再进入后端和联调。' },
    { step: '07', title: '后端与联调', body: '完成 API、服务、数据层和真实交互闭环。' },
    { step: '08', title: '质量门禁', body: '执行 UI Review、红队、安全、性能和架构阈值检查。' },
    { step: '09', title: '交付与发布演练', body: '交付包 ready、演练 passed、release readiness 通过后才算完成。' },
  ],
  controlTitle: '流程控制',
  controlBody: '如果项目已经进入中后段，不需要从头再跑。你可以查看当前状态，回到某个阶段，直接跳到某个阶段，或者手动确认关键门后继续推进。',
  controlCards: [
    {
      title: '回到三文档阶段',
      body: '用户补需求、业务范围变化、或者需要重做方案时，直接回到 docs 阶段更新三文档，再继续后续流程。',
      code: 'super-dev run prd\nsuper-dev run architecture\nsuper-dev run uiux\n# 或直接回到三文档阶段\nsuper-dev jump docs',
    },
    {
      title: '回到前端 / 后端 / 质量阶段',
      body: 'UI 重做、接口调整、交付前复检，都可以从对应阶段重新顺序推进，不必从 research 再跑一遍。',
      code: 'super-dev run frontend\nsuper-dev run backend\nsuper-dev run quality',
    },
    {
      title: '跳转与确认',
      body: '如果你已经明确目标阶段，可以直接 jump；如果只是要清掉某个关键门，则使用 confirm。',
      code: 'super-dev status\nsuper-dev jump quality\nsuper-dev confirm docs --comment "三文档已确认"\nsuper-dev confirm preview --comment "前端预览已确认"\nsuper-dev run --resume',
    },
  ],
  operationsTitle: '知识库与门禁',
  operationsBody: '本地知识库、确认门、运行验证和交付标准决定了这条流水线如何执行。',
  operationsCards: [
    {
      title: '知识库优先',
      body: '当 knowledge/ 和 knowledge-bundle 存在时，宿主必须先读本地知识，再做外部研究。',
      bullets: ['research 前置知识读取', 'PRD / Architecture / UI/UX 阶段化映射', 'quality / delivery 继续复用基线'],
    },
    {
      title: '改动前先看影响范围',
      body: '接手旧仓库、修改登录流、重构 API 或动关键状态流前，先跑 repo-map、feature-checklist 和 impact，把范围覆盖率、受影响模块和回归重点确认清楚。',
      bullets: ['super-dev repo-map', 'super-dev feature-checklist', 'super-dev impact "变更描述" --files ...'],
    },
    {
      title: '代码库理解与回归守卫',
      body: '复杂仓库不要靠宿主临场猜结构。先生成依赖图，再把影响分析转换成可执行的回归清单。',
      bullets: ['super-dev dependency-graph', 'super-dev regression-guard "变更描述" --files ...', '先补回归重点再修改关键路径'],
    },
    {
      title: '前端运行验证门',
      body: '必须有 frontend-runtime 报告通过，中后段才允许继续。',
      bullets: ['preview.html', 'frontend-runtime.json', '运行通过后再进后端'],
    },
    {
      title: '质量与交付门',
      body: 'UI Review、Spec Quality、交付包、发布演练和 release readiness 共同定义“是否可交付”。',
      bullets: ['UI Review', 'Spec Quality', 'Proof Pack / release readiness'],
    },
  ],
  commandsTitle: '常用命令',
  commandsBody: '这里整理最常用的命令组：安装与引导、宿主接入、范围覆盖审计、代码库理解、影响分析、回归守卫、缺陷修复、确认门、质量检查、发布检查和更新。',
  commands: [
    {
      title: '安装与引导',
      code: 'pip install -U super-dev\n# 或\nuv tool install super-dev\n\n# 进入宿主安装引导\nsuper-dev',
      filename: 'Terminal',
    },
    {
      title: '宿主接入与修复',
      code: 'super-dev onboard --host claude-code --force --yes\nsuper-dev doctor --host trae --repair --force\nsuper-dev integrate validate --auto\nsuper-dev detect --json',
      filename: 'Host Operations',
    },
    {
      title: '代码库理解与影响分析',
      code: 'super-dev repo-map\nsuper-dev feature-checklist\nsuper-dev dependency-graph\nsuper-dev impact "修改登录流程" --files services/auth.py\nsuper-dev regression-guard "修改登录流程" --files services/auth.py',
      filename: 'Codebase Intelligence',
    },
    {
      title: '缺陷修复路径',
      code: 'super-dev fix "修复登录接口 500 并补充回归验证"',
      filename: 'Bugfix Mode',
    },
    {
      title: 'Spec 质量与脚手架',
      code: 'super-dev spec propose add-billing --title "..." --description "..." --no-scaffold\nsuper-dev spec scaffold add-billing\nsuper-dev spec quality add-billing\nsuper-dev spec quality add-billing --json',
      filename: 'Spec Quality',
    },
    {
      title: '确认与恢复',
      code: 'super-dev review docs --status confirmed --comment "三文档已确认"\nsuper-dev run --resume',
      filename: 'Pipeline Gates',
    },
    {
      title: '流程控制',
      code: 'super-dev status\nsuper-dev run research\nsuper-dev run prd\nsuper-dev run architecture\nsuper-dev run uiux\nsuper-dev run frontend\nsuper-dev run backend\nsuper-dev run quality\nsuper-dev jump docs\nsuper-dev jump quality\nsuper-dev confirm docs --comment "三文档已确认"',
      filename: 'Workflow Control',
    },
    {
      title: '质量 / 发布 / 更新',
      code: 'super-dev quality --type all\nsuper-dev release proof-pack\nsuper-dev release readiness --verify-tests\nsuper-dev update --check\nsuper-dev update',
      filename: 'Quality & Release',
    },
  ],
  troubleshootingTitle: '排障',
  troubleshootingBody: '大多数问题都出在宿主没有真正读取接入面。排障时优先确认 commands、rules、AGENTS、steering 或 skills 是否已被宿主加载。',
  troubleshootingSteps: [
    '执行 super-dev doctor --host <host> --repair --force。',
    '确认安装引导输出的项目级与用户级接入面真实存在。',
    '完全关闭宿主，重新打开项目，并新建一个会话。',
    '先用 smoke 触发语句。',
    '如果宿主直接开始开发，优先判断当前会话没有重新加载规则。',
  ],
  highlightsTitle: 'v2.3.1 新功能亮点',
  highlightsBody: '2.3.1 继续把 Codex 深度适配、宿主安装引导、恢复链和 UI 契约治理打磨到同一套真实入口与交付闭环。',
  highlightsCards: [
    { title: '知识推送引擎', body: '每阶段自动推送相关知识约束，306文件索引，7阶段映射，L1/L2/L3渐进式加载。' },
    { title: '知识自演化', body: 'SQLite追踪使用效果，数据驱动权重优化，知识库扩展至270+文件/15万行，覆盖23个技术领域。' },
    { title: '可编程验证规则', body: '25条YAML声明式规则（14默认+11红队），支持自定义扩展。' },
    { title: '质量顾问', body: '主动质量建议，Quick Wins优先排序，Spec-Code一致性检测防止代码偏离Spec。' },
    { title: '专家系统四层武装', body: 'Profile+Knowledge+Rules+Protocol，11个深度Playbook，交叉审查引擎多专家视角自动审查。' },
    { title: 'Pipeline效能度量', body: 'DORA五指标+Rework Rate，ADR自动生成，Prompt模板版本化。' },
    { title: '跨系统集成', body: 'A2A协议5个Agent Cards，外部审查集成（CodeRabbit/Qodo），结构化输出5个JSON Schema。' },
    { title: '基础设施强化', body: 'Web API认证，OpenClaw插件升级至20个Tool，终端UI自适应，1600+测试覆盖。' },
  ],
  smokeTitle: 'Smoke 验收',
  smokeCode:
    '# slash 宿主\n/super-dev "请先不要开始编码，只回复 SMOKE_OK，并说明你会先做 research、再写三文档并等待确认。"\n\n# 非 slash 宿主\nsuper-dev: 请先不要开始编码，只回复 SMOKE_OK，并说明你会先做 research、再写三文档并等待确认。',
};

const enContent: Content = {
  heroKicker: 'Documentation Center',
  heroTitle: 'Start with install, host onboarding, triggers, pipeline, and delivery.',
  heroBody:
    'This documentation covers installation, host onboarding, triggers, pipeline stages, codebase intelligence, regression guard, local knowledge, workflow gates, and delivery requirements.',
  heroStats: [
    { label: 'Primary hosts', value: '16' },
    { label: 'Trigger modes', value: '2' },
    { label: 'Core phases', value: '9' },
  ],
  sections: [
    { id: 'highlights', label: 'v2.3.1 Highlights', icon: Zap },
    { id: 'governance', label: 'Positioning', icon: BookOpen },
    { id: 'install', label: 'Installation', icon: Package },
    { id: 'surfaces', label: 'Integration Surfaces', icon: Boxes },
    { id: 'triggers', label: 'Trigger Model', icon: Command },
    { id: 'hosts', label: 'Host Matrix', icon: Terminal },
    { id: 'pipeline', label: 'Pipeline', icon: Workflow },
    { id: 'control', label: 'Workflow Control', icon: RefreshCw },
    { id: 'operations', label: 'Knowledge & Gates', icon: FolderTree },
    { id: 'commands', label: 'Commands', icon: Package },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: LifeBuoy },
  ],
  governanceTitle: 'Super Dev governs the AI development process inside the host.',
  governanceBody:
    'The host handles model reasoning, browsing, tool execution, and real coding. Super Dev governs research, the three core docs, approval gates, spec creation, frontend validation, quality thresholds, and delivery standards.',
  governanceCards: [
    { title: 'Host executes', body: 'Reasoning, browsing, code edits, terminal commands, and runtime execution stay inside the host.' },
    { title: 'Super Dev governs', body: 'Research-first flow, the three core docs, confirmation gates, frontend verification, quality gates, and delivery readiness.' },
    { title: 'Artifacts stay auditable', body: 'Research, PRD, Architecture, UI/UX, Spec, runtime reports, and delivery outputs remain inspectable.' },
  ],
  installTitle: 'Installation',
  installBody:
    'Install the tool first, then enter the host onboarding flow. This section covers what gets installed and what to run next.',
  installBullets: [
    'pip or uv automatically install Super Dev and its Python dependencies.',
    'They do not install Claude Code, Cursor, Trae, Gemini CLI, VS Code Copilot, or any host application.',
    'Running super-dev opens the host installer and writes the required protocol surfaces for the 16 primary host profiles.',
  ],
  installCode:
    'pip install -U super-dev\n# or\nuv tool install super-dev\n\n# open the installer\nsuper-dev\n\n# OpenClaw users: install plugin or skill\nopenclaw plugins install @super-dev/openclaw-plugin\n# or\nclawhub install super-dev\n\n# update later\nsuper-dev update',
  surfacesTitle: 'Integration surfaces',
  surfacesBody:
    'The installer writes the required project-level and user-level surfaces so the host can recognize and execute the Super Dev workflow.',
  surfaces: [
    {
      title: 'Python CLI',
      body: 'The governance core. It handles installation, repair, state, quality gates, release checks, and delivery logic.',
      points: ['super-dev', 'doctor / detect / update', 'review / quality / release readiness'],
    },
    {
      title: 'Host protocol surfaces',
      body: 'Hosts consume Super Dev through commands, rules, AGENTS, steering, subagents, and skills depending on the official model.',
      points: ['slash / text trigger', 'project-level surfaces', 'user-level surfaces'],
    },
    {
      title: 'Project artifacts',
      body: 'Knowledge bundles, the three core docs, Spec, runtime verification, and delivery outputs define the actual workflow state.',
      points: ['knowledge/', 'output/*', '.super-dev/changes/*'],
    },
  ],
  triggerTitle: 'Trigger model',
  triggerBody: 'There are only two trigger syntaxes. Learn those first, then inspect the host protocol surfaces when needed.',
  triggerCards: [
    {
      title: 'Slash hosts',
      command: '/super-dev your requirement',
      hosts: SLASH_HOSTS,
      note: 'The host enters the Super Dev pipeline through official commands, workflows, rules, or subagents.',
      variant: 'certified',
    },
    {
      title: 'Text-trigger hosts',
      command: 'super-dev: your requirement',
      hosts: TEXT_TRIGGER_HOSTS,
      note: 'The host maps the text trigger through AGENTS, project rules, steering, or a compatibility skill surface.',
      variant: 'compatible',
    },
  ],
  matrixTitle: 'Host matrix',
  matrixBody: 'This matrix lists trigger style, protocol surface, and maturity for each supported host.',
  matrixGroups: [
    {
      category: 'CLI',
      items: [
        { host: 'claude-code', protocol: 'official commands + subagents', grade: 'Certified', trigger: '/super-dev' },
        { host: 'codex-cli', protocol: 'official AGENTS.md + official Skills', grade: 'Certified', trigger: 'super-dev:' },
        { host: 'opencode', protocol: 'official commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'gemini-cli', protocol: 'official commands + GEMINI.md', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro-cli', protocol: 'official commands + AGENTS.md', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'cursor-cli', protocol: 'official commands + rules', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'qoder-cli', protocol: 'official commands + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'codebuddy-cli', protocol: 'official commands + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'openclaw', protocol: 'Plugin SDK + ClawHub Skill', grade: 'Compatible', trigger: '/super-dev' },
      ],
    },
    {
      category: 'IDE',
      items: [
        { host: 'cursor', protocol: 'official commands + rules', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'antigravity', protocol: 'official commands + GEMINI.md + workflows', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro', protocol: 'official project steering + global steering', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'qoder', protocol: 'official commands + rules + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'trae', protocol: 'official project rules + compatibility skill', grade: 'Compatible', trigger: 'super-dev:' },
        { host: 'vscode-copilot', protocol: 'official copilot-instructions + AGENTS', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'codebuddy', protocol: 'official commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'windsurf', protocol: 'official workflows + skills', grade: 'Experimental', trigger: '/super-dev' },
      ],
    },
  ],
  pipelineTitle: 'Pipeline',
  pipelineBody: 'The trigger is short. The actual value is the enforced flow behind it: research, documentation, approval, implementation, verification, quality, and delivery.',
  pipelineSteps: [
    { step: '01', title: 'Comparable-product research', body: 'Use the host web tools first to study adjacent products, interaction patterns, differentiation, and commercial signals.' },
    { step: '02', title: 'Requirement expansion', body: 'Fill in boundaries, edge cases, acceptance criteria, and priorities before any implementation starts.' },
    { step: '03', title: 'Three core docs', body: 'Generate PRD, Architecture, and UI/UX as the auditable execution baseline.' },
    { step: '04', title: 'User confirmation gate', body: 'Pause after the docs. No Spec and no coding until the user confirms or requests revisions.' },
    { step: '05', title: 'Spec / Tasks', body: 'Create the proposal and task breakdown only after approval.' },
    { step: '06', title: 'Frontend first', body: 'Build the frontend first, make it runnable and reviewable, then move deeper into implementation.' },
    { step: '07', title: 'Backend & integration', body: 'Complete the APIs, service layers, data flows, and real end-to-end interactions.' },
    { step: '08', title: 'Quality gates', body: 'Run UI review, red-team review, security, performance, and architecture threshold checks.' },
    { step: '09', title: 'Delivery & release rehearsal', body: 'Only finish after the delivery package is ready and release rehearsal passes.' },
  ],
  controlTitle: 'Workflow control',
  controlBody: 'If the project is already in a later stage, you do not need to restart from zero. Inspect the current state, return to a phase, jump to a phase, or manually clear a gate and continue.',
  controlCards: [
    {
      title: 'Return to the three core docs',
      body: 'When scope changes or the user adds requirements, move back to docs and update the PRD / Architecture / UI/UX set before continuing.',
      code: 'super-dev run prd\nsuper-dev run architecture\nsuper-dev run uiux\n# or return to the docs stage\nsuper-dev jump docs',
    },
    {
      title: 'Return to frontend / backend / quality',
      body: 'Use phase control when the UI needs another pass, APIs must be realigned, or quality checks must be rerun before release.',
      code: 'super-dev run frontend\nsuper-dev run backend\nsuper-dev run quality',
    },
    {
      title: 'Jump and confirm',
      body: 'Use jump when you already know the target phase. Use confirm when a workflow gate must be cleared manually.',
      code: 'super-dev status\nsuper-dev jump quality\nsuper-dev confirm docs --comment "core docs approved"\nsuper-dev confirm preview --comment "preview approved"\nsuper-dev run --resume',
    },
  ],
  operationsTitle: 'Knowledge and gates',
  operationsBody: 'Local knowledge, approval gates, runtime verification, and delivery standards define how the workflow runs.',
  operationsCards: [
    {
      title: 'Knowledge-first execution',
      body: 'When knowledge/ and a knowledge bundle exist, the host reads them before external research.',
      bullets: ['knowledge before research', 'phase-based mapping into PRD / Architecture / UI/UX', 'continued reuse in quality and delivery'],
    },
    {
      title: 'Inspect impact before changing critical flows',
      body: 'Before refactoring a mature repo, changing auth, reshaping APIs, or touching major state flows, run repo-map, feature-checklist, and impact analysis so the host starts with scope truth instead of guesses.',
      bullets: ['super-dev repo-map', 'super-dev feature-checklist', 'super-dev impact "change description" --files ...'],
    },
    {
      title: 'Codebase intelligence and regression guard',
      body: 'Do not let the host guess its way through a large repo. Generate the dependency graph first, then turn impact analysis into an executable regression checklist.',
      bullets: ['super-dev dependency-graph', 'super-dev regression-guard "change description" --files ...', 'lock the regression focus before modifying critical paths'],
    },
    {
      title: 'Frontend runtime gate',
      body: 'A page file existing is not enough. A passing frontend runtime report is required before later stages continue.',
      bullets: ['preview.html', 'frontend-runtime.json', 'backend starts after runtime verification'],
    },
    {
      title: 'Quality & delivery gates',
      body: 'UI review, Spec Quality, delivery packaging, release rehearsal, and release readiness define completion.',
      bullets: ['UI Review', 'Spec Quality', 'Proof Pack / release readiness'],
    },
  ],
  commandsTitle: 'Commands',
  commandsBody: 'Keep the critical commands visible: install, onboarding, scope coverage audit, codebase intelligence, impact analysis, regression guard, bugfix, approval, quality, release checks, and update.',
  commands: [
    {
      title: 'Install & bootstrap',
      code: 'pip install -U super-dev\n# or\nuv tool install super-dev\n\n# open the host installer\nsuper-dev',
      filename: 'Terminal',
    },
    {
      title: 'Onboarding & repair',
      code: 'super-dev onboard --host claude-code --force --yes\nsuper-dev doctor --host trae --repair --force\nsuper-dev integrate validate --auto\nsuper-dev detect --json',
      filename: 'Host Operations',
    },
    {
      title: 'Codebase intelligence & impact',
      code: 'super-dev repo-map\nsuper-dev feature-checklist\nsuper-dev dependency-graph\nsuper-dev impact "Change the login flow" --files services/auth.py\nsuper-dev regression-guard "Change the login flow" --files services/auth.py',
      filename: 'Codebase Intelligence',
    },
    {
      title: 'Bugfix mode',
      code: 'super-dev fix "Fix login 500 and add regression verification"',
      filename: 'Bugfix Mode',
    },
    {
      title: 'Spec quality and scaffolding',
      code: 'super-dev spec propose add-billing --title "..." --description "..." --no-scaffold\nsuper-dev spec scaffold add-billing\nsuper-dev spec quality add-billing\nsuper-dev spec quality add-billing --json',
      filename: 'Spec Quality',
    },
    {
      title: 'Approve & resume',
      code: 'super-dev review docs --status confirmed --comment "core docs approved"\nsuper-dev run --resume',
      filename: 'Pipeline Gates',
    },
    {
      title: 'Workflow control',
      code: 'super-dev status\nsuper-dev run research\nsuper-dev run prd\nsuper-dev run architecture\nsuper-dev run uiux\nsuper-dev run frontend\nsuper-dev run backend\nsuper-dev run quality\nsuper-dev jump docs\nsuper-dev jump quality\nsuper-dev confirm docs --comment "core docs approved"',
      filename: 'Workflow Control',
    },
    {
      title: 'Quality / release / update',
      code: 'super-dev quality --type all\nsuper-dev release proof-pack\nsuper-dev release readiness --verify-tests\nsuper-dev update --check\nsuper-dev update',
      filename: 'Quality & Release',
    },
  ],
  troubleshootingTitle: 'Troubleshooting',
  troubleshootingBody: 'Most failures happen because the host did not load commands, rules, AGENTS, steering, or skills. Check the integration surface before you blame the trigger.',
  troubleshootingSteps: [
    'Run super-dev doctor --host <host> --repair --force.',
    'Verify that the project-level and user-level surfaces reported by onboarding actually exist.',
    'Close the host completely, reopen the project, and start a fresh chat.',
    'Use a smoke prompt before trying the real requirement.',
    'If the host starts coding immediately, assume the current session did not reload the rules.',
  ],
  highlightsTitle: 'v2.3.1 Highlights',
  highlightsBody: 'Version 2.3.1 continues hardening Codex deep adaptation, host onboarding, recovery flows, and UI contract governance into one coherent delivery system.',
  highlightsCards: [
    { title: 'Knowledge Push Engine', body: 'Auto-push relevant knowledge per pipeline phase. 306 files indexed, 7-phase mapping, L1/L2/L3 progressive loading.' },
    { title: 'Knowledge Evolution', body: 'SQLite-based usage tracking with data-driven weight optimization. Knowledge base expanded to 270+ files / 150K lines across 23 domains.' },
    { title: 'Programmable Validation Rules', body: '25 YAML declarative rules (14 default + 11 redteam), fully customizable.' },
    { title: 'Quality Advisor', body: 'Proactive quality suggestions with Quick Wins prioritization. Spec-Code consistency checker prevents code drift.' },
    { title: 'Expert System 4-Layer Upgrade', body: 'Profile+Knowledge+Rules+Protocol, 11 deep Playbooks, cross-review engine for multi-expert artifact validation.' },
    { title: 'Pipeline Metrics', body: 'DORA 5 indicators + Rework Rate, ADR auto-generation, prompt template versioning.' },
    { title: 'Cross-System Integration', body: 'A2A protocol with 5 Agent Cards, external review integration (CodeRabbit/Qodo), 5 structured output JSON Schemas.' },
    { title: 'Infrastructure Hardening', body: 'Web API authentication, OpenClaw plugin upgraded to 20 Tools, responsive terminal UI, 1600+ test coverage.' },
  ],
  smokeTitle: 'Smoke validation',
  smokeCode:
    '# slash hosts\n/super-dev "Do not start coding. Reply only with SMOKE_OK and explain that you will do research first, then generate the three core docs, then wait for confirmation."\n\n# non-slash hosts\nsuper-dev: Do not start coding. Reply only with SMOKE_OK and explain that you will do research first, then generate the three core docs, then wait for confirmation.',
};

function SectionShell({
  id,
  icon: Icon,
  label,
  title,
  body,
  children,
}: {
  id: string;
  icon: LucideIcon;
  label: string;
  title: string;
  body: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 border-b border-border-default/70 pb-10 last:border-b-0 last:pb-0">
      <div className="mb-6 flex items-start gap-4">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-accent-blue/25 bg-accent-blue/8 text-accent-blue">
          <Icon size={20} />
        </div>
        <div className="max-w-4xl">
          <p className="mb-2 text-xs font-mono uppercase tracking-[0.22em] text-accent-blue">{label}</p>
          <h2 className="mb-3 text-2xl font-bold tracking-tight text-text-primary sm:text-[2rem]">{title}</h2>
          <p className="text-[15px] leading-8 text-text-secondary">{body}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

export function DocsPageContent({ locale = 'zh' }: { locale?: SiteLocale }) {
  const content = locale === 'en' ? enContent : zhContent;
  const homeHref = localizedPath(locale, '/');

  return (
    <main className="min-h-screen bg-bg-primary pt-14" id="main-content">
      <section className="relative overflow-hidden border-b border-border-muted bg-bg-primary">
        <div className="absolute inset-0 opacity-70 [background-image:radial-gradient(circle_at_top_left,rgba(37,99,235,0.22),transparent_32%),radial-gradient(circle_at_80%_12%,rgba(59,130,246,0.12),transparent_24%)]" />
        <div className="absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(59,130,246,0.65),transparent)]" />
        <div className="relative mx-auto w-full max-w-[1380px] px-4 py-14 sm:px-6 lg:px-8 lg:py-16">
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="max-w-[860px]">
              <div className="mb-5 flex flex-wrap items-center gap-2">
                <Badge variant="version">{content.heroKicker}</Badge>
                <Badge variant="certified">v2.3.1</Badge>
                <Badge variant="compatible">{locale === 'en' ? 'Bilingual' : '中英双语'}</Badge>
              </div>
              <h1 className="max-w-[900px] text-4xl font-bold leading-[1.08] tracking-tight text-text-primary sm:text-5xl lg:text-[3.5rem]">
                {content.heroTitle}
              </h1>
              <p className="mt-5 max-w-[760px] text-lg leading-8 text-text-secondary">{content.heroBody}</p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link
                  href="#install"
                  className="inline-flex items-center gap-2 rounded-xl bg-accent-blue px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-accent-blue-hover"
                >
                  {locale === 'en' ? 'Open install guide' : '查看安装方式'}
                  <ArrowRight size={16} />
                </Link>
                <Link
                  href="#commands"
                  className="inline-flex items-center gap-2 rounded-xl border border-border-emphasis px-5 py-3 text-sm font-semibold text-text-primary transition-colors hover:bg-bg-tertiary"
                >
                  {locale === 'en' ? 'Command reference' : '命令参考'}
                </Link>
                <Link
                  href={homeHref}
                  className="inline-flex items-center gap-2 rounded-xl border border-border-default px-5 py-3 text-sm font-semibold text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary"
                >
                  {locale === 'en' ? 'Back to website' : '返回官网'}
                </Link>
              </div>
            </div>

            <div className="rounded-[24px] border border-border-default bg-[linear-gradient(180deg,rgba(45,51,59,0.92),rgba(22,27,34,0.96))] p-5 glow-blue">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-text-primary">
                  <Sparkles size={16} className="text-accent-blue" />
                  {locale === 'en' ? 'Install command' : '安装指令'}
                </div>
                <Badge variant="default">{locale === 'en' ? 'First step' : '第一步'}</Badge>
              </div>
              <p className="mb-5 text-sm leading-7 text-text-secondary">
                {locale === 'en'
                  ? 'Install the CLI first. Then run super-dev in the terminal to open the host installer and write the required protocol surfaces.'
                  : '先安装 CLI。然后在终端输入 super-dev，进入宿主安装引导并写入所需接入面。'}
              </p>
              <div className="rounded-2xl border border-border-default bg-bg-primary/80 p-4">
                <CopyCommand command="pip install -U super-dev" className="w-full" />
                <div className="mt-3">
                  <CodeBlock
                    code={`pip install -U super-dev\n# or\nuv tool install super-dev\n\nsuper-dev`}
                    filename={locale === 'en' ? 'Install' : '安装'}
                    className="bg-bg-primary"
                  />
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <section className="mx-auto w-full max-w-[1380px] px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
        <div className="grid gap-8 xl:grid-cols-[220px_minmax(0,860px)]">
          <aside className="hidden xl:block">
            <div className="sticky top-24 rounded-[24px] border border-border-default bg-bg-secondary/55 p-4 backdrop-blur-sm">
              <div className="mb-3 text-xs font-mono uppercase tracking-[0.18em] text-text-muted">
                {locale === 'en' ? 'Path' : '路径'}
              </div>
              <nav className="space-y-1.5">
                {content.sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <a
                      key={section.id}
                      href={`#${section.id}`}
                      className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary"
                    >
                      <Icon size={15} className="text-accent-blue" />
                      <span>{section.label}</span>
                    </a>
                  );
                })}
              </nav>
            </div>
          </aside>

          <div className="space-y-8">
            <SectionShell id="highlights" icon={Zap} label={content.sections[0].label} title={content.highlightsTitle} body={content.highlightsBody}>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {content.highlightsCards.map((card) => (
                  <div key={card.title} className="rounded-2xl border border-accent-blue/25 bg-accent-blue/5 p-5">
                    <h3 className="mb-2 text-base font-semibold text-text-primary">{card.title}</h3>
                    <p className="text-sm leading-7 text-text-secondary">{card.body}</p>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="governance" icon={BookOpen} label={content.sections[1].label} title={content.governanceTitle} body={content.governanceBody}>
              <div className="grid gap-4 lg:grid-cols-2">
                {content.governanceCards.map((item) => (
                  <div key={item.title} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <h3 className="mb-2 text-base font-semibold text-text-primary">{item.title}</h3>
                    <p className="text-sm leading-7 text-text-secondary">{item.body}</p>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="install" icon={Package} label={content.sections[2].label} title={content.installTitle} body={content.installBody}>
              <div className="grid gap-4 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
                <div className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                  <h3 className="mb-4 text-lg font-semibold text-text-primary">{locale === 'en' ? 'Installation notes' : '安装说明'}</h3>
                  <ul className="space-y-3 text-sm leading-7 text-text-secondary">
                    {content.installBullets.map((bullet) => (
                      <li key={bullet} className="flex gap-3">
                        <span className="mt-2 h-1.5 w-1.5 rounded-full bg-accent-blue" />
                        <span>{bullet}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <CodeBlock code={content.installCode} filename={locale === 'en' ? 'Install Flow' : '安装流程'} />
              </div>
            </SectionShell>

            <SectionShell id="surfaces" icon={Boxes} label={content.sections[3].label} title={content.surfacesTitle} body={content.surfacesBody}>
              <div className="grid gap-4 lg:grid-cols-2">
                {content.surfaces.map((surface) => (
                  <div key={surface.title} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <h3 className="mb-3 text-lg font-semibold text-text-primary">{surface.title}</h3>
                    <p className="mb-4 text-sm leading-7 text-text-secondary">{surface.body}</p>
                    <ul className="space-y-2 text-sm text-text-secondary">
                      {surface.points.map((point) => (
                        <li key={point} className="flex gap-2">
                          <span className="mt-2 h-1.5 w-1.5 rounded-full bg-accent-blue" />
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="triggers" icon={Command} label={content.sections[4].label} title={content.triggerTitle} body={content.triggerBody}>
              <div className="space-y-4">
                {content.triggerCards.map((card) => (
                  <div key={card.title} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <h3 className="text-lg font-semibold text-text-primary">{card.title}</h3>
                      <Badge variant={card.variant}>{card.variant === 'certified' ? 'Slash' : locale === 'en' ? 'Text trigger' : '文本触发'}</Badge>
                    </div>
                    <div className="mb-4 rounded-xl border border-border-default bg-bg-primary px-4 py-3 font-mono text-sm text-accent-blue">{card.command}</div>
                    <p className="mb-4 text-sm leading-7 text-text-secondary">{card.note}</p>
                    <div className="flex flex-wrap gap-2">
                      {card.hosts.map((host) => (
                        <Badge key={host} variant="default" className="font-mono">{host}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="hosts" icon={Terminal} label={content.sections[5].label} title={content.matrixTitle} body={content.matrixBody}>
              <div className="space-y-4">
                {content.matrixGroups.map((group) => (
                  <div key={group.category} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <div className="mb-5 flex items-center justify-between gap-3">
                      <h3 className="text-lg font-semibold text-text-primary">{group.category}</h3>
                      <Badge variant="version">{group.items.length}</Badge>
                    </div>
                    <div className="space-y-3">
                      {group.items.map((item) => (
                        <div key={item.host} className="rounded-xl border border-border-default bg-bg-primary/70 p-4">
                          <div className="mb-2 flex items-center justify-between gap-3">
                            <div className="font-mono text-sm text-text-primary">{item.host}</div>
                            <Badge variant={gradeVariant(item.grade)}>{item.grade}</Badge>
                          </div>
                          <div className="mb-2 font-mono text-xs text-accent-blue">{item.trigger}</div>
                          <div className="text-sm leading-6 text-text-secondary">{item.protocol}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="pipeline" icon={Workflow} label={content.sections[6].label} title={content.pipelineTitle} body={content.pipelineBody}>
              <div className="space-y-4">
                {content.pipelineSteps.map((step, index) => (
                  <div key={step.step} className="grid gap-4 rounded-2xl border border-border-default bg-bg-elevated/80 p-5 lg:grid-cols-[88px_minmax(0,1fr)]">
                    <div className="flex items-center gap-3 lg:block">
                      <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-accent-blue/35 bg-accent-blue/10 font-mono text-sm text-accent-blue">
                        {step.step}
                      </div>
                      {index < content.pipelineSteps.length - 1 ? <div className="hidden h-10 w-px translate-x-6 bg-border-default lg:block" /> : null}
                    </div>
                    <div>
                      <h3 className="mb-2 text-lg font-semibold text-text-primary">{step.title}</h3>
                      <p className="text-sm leading-7 text-text-secondary">{step.body}</p>
                    </div>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="control" icon={RefreshCw} label={content.sections[7].label} title={content.controlTitle} body={content.controlBody}>
              <div className="grid gap-4 lg:grid-cols-3">
                {content.controlCards.map((card) => (
                  <div key={card.title} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <h3 className="mb-3 text-lg font-semibold text-text-primary">{card.title}</h3>
                    <p className="mb-4 text-sm leading-7 text-text-secondary">{card.body}</p>
                    <CodeBlock code={card.code} filename={locale === 'en' ? 'Control' : '控制'} />
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="operations" icon={FolderTree} label={content.sections[8].label} title={content.operationsTitle} body={content.operationsBody}>
              <div className="space-y-4">
                {content.operationsCards.map((card) => (
                  <div key={card.title} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <h3 className="mb-3 text-lg font-semibold text-text-primary">{card.title}</h3>
                    <p className="mb-4 text-sm leading-7 text-text-secondary">{card.body}</p>
                    <ul className="space-y-2 text-sm text-text-secondary">
                      {card.bullets.map((bullet) => (
                        <li key={bullet} className="flex gap-2">
                          <Search size={16} className="mt-1 text-accent-blue" />
                          <span>{bullet}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="commands" icon={Package} label={content.sections[9].label} title={content.commandsTitle} body={content.commandsBody}>
              <div className="space-y-4">
                {content.commands.map((command) => (
                  <div key={command.title} className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                    <h3 className="mb-4 text-lg font-semibold text-text-primary">{command.title}</h3>
                    <CodeBlock code={command.code} filename={command.filename} />
                  </div>
                ))}
              </div>
            </SectionShell>

            <SectionShell id="troubleshooting" icon={LifeBuoy} label={content.sections[10].label} title={content.troubleshootingTitle} body={content.troubleshootingBody}>
              <div className="space-y-4">
                <div className="rounded-2xl border border-border-default bg-bg-elevated/80 p-5">
                  <h3 className="mb-4 text-lg font-semibold text-text-primary">{locale === 'en' ? 'Troubleshooting order' : '排查顺序'}</h3>
                  <ol className="space-y-3 text-sm leading-7 text-text-secondary">
                    {content.troubleshootingSteps.map((step, index) => (
                      <li key={step} className="flex gap-3">
                        <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent-blue/35 bg-accent-blue/10 font-mono text-xs text-accent-blue">
                          {index + 1}
                        </span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ol>
                  <div className="mt-6 border-t border-border-default pt-6">
                    <h3 className="mb-4 text-lg font-semibold text-text-primary">{content.smokeTitle}</h3>
                    <CodeBlock code={content.smokeCode} filename="Smoke" />
                  </div>
                </div>
              </div>
            </SectionShell>
          </div>
        </div>
      </section>
    </main>
  );
}
