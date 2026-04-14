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
    '先记住终端里的两个命令，再回到宿主里的两个触发。其余流程都应该在宿主里完成，而不是靠用户记大量 CLI 命令。',
  heroStats: [
    { label: '宿主总数', value: '21+1' },
    { label: '专家 Agent', value: '10' },
    { label: '核心阶段', value: '9 段' },
  ],
  sections: [
    { id: 'highlights', label: 'v2.3.8 新功能', icon: Zap },
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
    '终端只负责接入和升级。安装阶段只需要弄清三件事：会写哪些协议面、不会安装哪些宿主本体、接入后在宿主里输入什么。',
  installBullets: [
    'pip 或 uv 会自动安装 Super Dev 的 Python 依赖。',
    '不会自动安装 Claude Code、Cursor、Trae、Gemini CLI、VS Code Copilot 等宿主本体。',
    '终端输入 super-dev 后，会进入宿主安装引导，并按宿主自动判断项目级与全局级协议面；OpenClaw 仍是单独的手动插件宿主。',
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
  triggerBody: '大多数宿主只需要记住 slash 或文本触发；Codex 属于三入口模型，宿主矩阵里会单独展开。',
  triggerCards: [
    {
      title: 'Slash 宿主',
      command: '/super-dev 你的需求',
      hosts: SLASH_HOSTS,
      note: '宿主会通过 commands / workflows / subagents / rules / steering slash entry 进入 Super Dev 流水线；Codex App/Desktop 也会把启用的 super-dev Skill 暴露进 `/` 列表。',
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
  matrixBody: '这张矩阵把接入完成度和运行成熟度分开展示，避免把“文件已落盘”误看成“宿主已真实跑通”。',
  matrixGroups: [
    {
      category: 'CLI',
      items: [
        { host: 'claude-code', protocol: '官方 CLAUDE.md + skills + optional plugin', grade: 'Certified', trigger: '/super-dev' },
        { host: 'codex-cli', protocol: '官方 AGENTS.md + 官方 Skills + repo plugin', grade: 'Certified', trigger: 'App/Desktop: /super-dev · CLI: $super-dev' },
        { host: 'opencode', protocol: '官方 commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'gemini-cli', protocol: '官方 commands + GEMINI.md', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro-cli', protocol: '官方 steering slash entry + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'cursor-cli', protocol: '官方 commands + rules', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'qoder-cli', protocol: '官方 AGENTS.md + rules + commands + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'copilot-cli', protocol: '官方 copilot-instructions + skills', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'codebuddy-cli', protocol: '官方 CODEBUDDY.md + commands + skills', grade: 'Compatible', trigger: '/super-dev' },
      ],
    },
    {
      category: 'IDE',
      items: [
        { host: 'cursor', protocol: '官方 commands + rules', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'antigravity', protocol: '官方 commands + GEMINI.md + workflows', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro', protocol: '官方 project steering + global steering + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'qoder', protocol: '官方 AGENTS.md + rules + commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'trae', protocol: '官方 project rules + 兼容 Skill', grade: 'Compatible', trigger: 'super-dev:' },
        { host: 'vscode-copilot', protocol: '官方 copilot-instructions + AGENTS', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'codebuddy', protocol: '官方 CODEBUDDY.md + rules + commands + agents + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'windsurf', protocol: '官方 workflows + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'roo-code', protocol: '官方 commands + rules + custom modes', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'kilo-code', protocol: '官方 rules + compatibility skill', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'cline', protocol: '官方 rules + skills + AGENTS compatibility', grade: 'Experimental', trigger: 'super-dev:' },
      ],
    },
    {
      category: '手动插件宿主',
      items: [
        { host: 'openclaw', protocol: 'Plugin SDK + ClawHub Skill', grade: 'Compatible', trigger: '/super-dev' },
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
  controlBody: '公开主路径里，不再要求用户记住一串终端治理命令。安装完成后，继续、返工、确认、补充，都优先在宿主里用自然语言推进。',
  controlCards: [
    {
      title: '继续改三文档',
      body: '用户补需求、业务范围变化、或者需要重做方案时，不用回终端跳阶段，直接在宿主里继续围绕三文档修改。',
      code: '/super-dev 这里补一下业务范围，先继续改 PRD / Architecture / UIUX，不要开始编码\n\nsuper-dev: 这个方案还不对，继续改三文档并等待我再次确认',
    },
    {
      title: '继续当前阶段',
      body: 'UI 重做、接口调整、交付前复检，都优先在宿主里继续当前流程，不再把普通用户赶回终端。',
      code: '/super-dev 继续当前流程\n/super-dev 现在下一步是什么\n\nsuper-dev: 继续当前流程，不要重新开题',
    },
    {
      title: '确认关键门',
      body: '文档确认、前端预览确认、UI 改版闭环、架构返工闭环、质量整改闭环，都优先在宿主里明确回复。',
      code: '/super-dev 文档确认，可以继续\n/super-dev 前端预览确认，可以继续\n\nsuper-dev: UI 改版已完成，继续当前流程\nsuper-dev: 质量整改已完成，继续当前流程',
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
  commandsBody: '公开主路径只保留终端的安装/升级入口，以及宿主内的继续与确认表达。其余 CLI 命令仍然存在，但属于维护/治理能力，不是普通用户日常操作面。',
  commands: [
    {
      title: '终端公开入口',
      code: 'pip install -U super-dev\n# 或\nuv tool install super-dev\n\nsuper-dev          # 进入宿主安装引导\nsuper-dev update   # 更新到最新版',
      filename: 'Terminal',
    },
    {
      title: '宿主内正常使用',
      code: '/super-dev 你的需求\n/super-dev 继续当前流程\n/super-dev 现在下一步是什么\n/super-dev 文档确认，可以继续\n\nsuper-dev: 你的需求\nsuper-dev: 继续当前流程\nsuper-dev: 质量整改已完成，继续当前流程',
      filename: 'Host Conversation',
    },
    {
      title: '维护 / 治理能力',
      code: 'super-dev onboard --host claude-code --force --yes\nsuper-dev doctor --host trae --repair --force\nsuper-dev integrate validate --auto\nsuper-dev feature-checklist\nsuper-dev product-audit\nsuper-dev release proof-pack\nsuper-dev release readiness',
      filename: 'Internal Maintenance',
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
  highlightsTitle: 'v2.3.8 新功能亮点',
  highlightsBody: '2.3.8 聚焦赛事模式与宿主生态：SEEAI 比赛验收升级为四段结构化证据（封堵假通过）、新增设计灵感工作流（PR #11，感谢 @staruhub 超哥贡献）、WorkBuddy 正式接入、安全防护增强、安装界面响应式优化、旧版残留自动修复、需求解析器增强。',
  highlightsCards: [
    { title: 'SEEAI 结构化证据闸门', body: 'first_response / runtime_checkpoint / fallback_decision / demo_path 四段缺一段就阻塞；每段最小 8 字符 + 模板关键词覆盖检查，passed 不再等于 ready。' },
    { title: '设计灵感工作流（PR #11）', body: '感谢 @staruhub 超哥贡献。新增 super-dev design list / recommend / apply <slug>，把内置设计灵感库（linear.app / vercel / stripe 等）一键写入项目并重生成 uiux/ui-contract。' },
    { title: '新增 SEEAI 赛事模式', body: '行动驱动的竞赛快速交付循环：需求→拆解→联网搜索→方案文档→Spec→写码→跑起来→反馈循环。' },
    { title: 'WorkBuddy 正式接入', body: 'WorkBuddy 从手动安装升级为统一安装宿主，Skill 自动安装到 ~/.workbuddy/skills/，21+1 宿主生态。' },
    { title: '安装界面响应式', body: '砍掉冗长的宿主协议列，三级窗口自适应（窄/标准/宽），交互选择器精简为 1 行快捷键。' },
    { title: '安全防护增强', body: '新增敏感文件读取守卫 hook、Web API Key 认证、运行存储自动淘汰。' },
    { title: '旧版残留自动修复', body: 'super-dev 和 super-dev update 检测到残留自动清理，不再需要手动操作。' },
    { title: 'rollback / replay / diff', body: '新增流水线回退、执行历史回放和阶段对比命令。' },
    { title: '需求解析器增强', body: '支持目标用户提取、核心功能推导、商业约束识别、技术栈偏好检测。' },
  ],
  smokeTitle: 'Smoke 验收',
  smokeCode:
    '# slash 宿主\n/super-dev "请先不要开始编码，只回复 SMOKE_OK，并说明你会先做 research、再写三文档并等待确认。"\n\n# 非 slash 宿主\nsuper-dev: 请先不要开始编码，只回复 SMOKE_OK，并说明你会先做 research、再写三文档并等待确认。',
};

const enContent: Content = {
  heroKicker: 'Documentation Center',
  heroTitle: 'Start with install, host onboarding, triggers, pipeline, and delivery.',
  heroBody:
    'Start with the two terminal commands, then move back to the two in-host triggers. The rest of the workflow should happen inside the host, not through a long CLI command catalog.',
  heroStats: [
    { label: 'Hosts', value: '21+1' },
    { label: 'Trigger modes', value: '2' },
    { label: 'Core phases', value: '9' },
  ],
  sections: [
    { id: 'highlights', label: 'v2.3.8 Highlights', icon: Zap },
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
    'The terminal only handles onboarding and upgrade. This section covers which protocol surfaces get written, which host apps are not installed for you, and what to type next inside the host.',
  installBullets: [
    'pip or uv automatically install Super Dev and its Python dependencies.',
    'They do not install Claude Code, Cursor, Trae, Gemini CLI, VS Code Copilot, or any host application.',
    'Running super-dev opens the installer and automatically decides the project-level and global protocol surfaces needed for each onboarded host; OpenClaw remains a separate manual plugin host.',
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
  triggerBody: 'Most hosts only need slash or text triggers. Codex is the notable three-entry exception and is expanded in the host matrix.',
  triggerCards: [
    {
      title: 'Slash hosts',
      command: '/super-dev your requirement',
      hosts: SLASH_HOSTS,
      note: 'The host enters the Super Dev pipeline through official commands, workflows, rules, subagents, or steering slash entry; Codex App/Desktop also exposes the enabled super-dev Skill in the `/` list.',
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
  matrixBody: 'This matrix separates integration readiness from runtime maturity so “files were written” is not confused with “the host is truly validated”.',
  matrixGroups: [
    {
      category: 'CLI',
      items: [
        { host: 'claude-code', protocol: 'official CLAUDE.md + skills + optional plugin', grade: 'Certified', trigger: '/super-dev' },
        { host: 'codex-cli', protocol: 'official AGENTS.md + official Skills + repo plugin', grade: 'Certified', trigger: 'App/Desktop: /super-dev · CLI: $super-dev' },
        { host: 'opencode', protocol: 'official commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'gemini-cli', protocol: 'official commands + GEMINI.md', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro-cli', protocol: 'official steering slash entry + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'cursor-cli', protocol: 'official commands + rules', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'qoder-cli', protocol: 'official AGENTS.md + rules + commands + skills', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'copilot-cli', protocol: 'official copilot-instructions + skills', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'codebuddy-cli', protocol: 'official CODEBUDDY.md + commands + skills', grade: 'Compatible', trigger: '/super-dev' },
      ],
    },
    {
      category: 'IDE',
      items: [
        { host: 'cursor', protocol: 'official commands + rules', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'antigravity', protocol: 'official commands + GEMINI.md + workflows', grade: 'Compatible', trigger: '/super-dev' },
        { host: 'kiro', protocol: 'official project steering + global steering + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'qoder', protocol: 'official AGENTS.md + rules + commands + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'trae', protocol: 'official project rules + compatibility skill', grade: 'Compatible', trigger: 'super-dev:' },
        { host: 'vscode-copilot', protocol: 'official copilot-instructions + AGENTS', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'codebuddy', protocol: 'official CODEBUDDY.md + rules + commands + agents + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'windsurf', protocol: 'official workflows + skills', grade: 'Experimental', trigger: '/super-dev' },
        { host: 'roo-code', protocol: 'official commands + rules + custom modes', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'kilo-code', protocol: 'official rules + compatibility skill', grade: 'Experimental', trigger: 'super-dev:' },
        { host: 'cline', protocol: 'official rules + skills + AGENTS compatibility', grade: 'Experimental', trigger: 'super-dev:' },
      ],
    },
    {
      category: 'Manual Plugin',
      items: [
        { host: 'openclaw', protocol: 'Plugin SDK + ClawHub Skill', grade: 'Compatible', trigger: '/super-dev' },
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
  controlBody: 'The public path no longer expects end users to memorize a long list of terminal workflow commands. After install, continue, revise, confirm, and recover primarily inside the host conversation.',
  controlCards: [
    {
      title: 'Keep revising the three core docs',
      body: 'When scope changes or the user adds requirements, keep the work inside the host and continue revising PRD / Architecture / UI/UX instead of bouncing back to terminal flow-control commands.',
      code: '/super-dev Add the missing scope and keep revising PRD / Architecture / UI/UX. Do not start coding.\n\nsuper-dev: The plan is still wrong. Keep revising the three core docs and wait for confirmation again.',
    },
    {
      title: 'Continue the current stage',
      body: 'When UI, APIs, or release checks need another pass, keep the user in the host conversation and continue the same Super Dev flow.',
      code: '/super-dev Continue the current flow\n/super-dev What is the next step right now?\n\nsuper-dev: Continue the current flow. Do not restart the project from scratch.',
    },
    {
      title: 'Clear the key gates in-host',
      body: 'Docs approval, preview approval, UI revision closure, architecture revision closure, and quality remediation closure should all be expressed inside the host first.',
      code: '/super-dev The core docs are approved. Continue.\n/super-dev The frontend preview is approved. Continue.\n\nsuper-dev: UI revision is finished. Continue the current flow.\nsuper-dev: Quality remediation is finished. Continue the current flow.',
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
  commandsBody: 'The public path keeps only terminal install/update plus in-host continuation and confirmation. The rest of the CLI still exists for maintenance and governance, but it is not the normal end-user operating surface.',
  commands: [
    {
      title: 'Public terminal entrypoints',
      code: 'pip install -U super-dev\n# or\nuv tool install super-dev\n\nsuper-dev          # open the host installer\nsuper-dev update   # update to the latest version',
      filename: 'Terminal',
    },
    {
      title: 'Normal usage inside the host',
      code: '/super-dev your requirement\n/super-dev Continue the current flow\n/super-dev What is the next step right now?\n/super-dev The core docs are approved. Continue.\n\nsuper-dev: your requirement\nsuper-dev: Continue the current flow\nsuper-dev: Quality remediation is finished. Continue the current flow.',
      filename: 'Host Conversation',
    },
    {
      title: 'Maintenance & governance',
      code: 'super-dev onboard --host claude-code --force --yes\nsuper-dev doctor --host trae --repair --force\nsuper-dev integrate validate --auto\nsuper-dev feature-checklist\nsuper-dev product-audit\nsuper-dev release proof-pack\nsuper-dev release readiness',
      filename: 'Internal Maintenance',
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
  highlightsTitle: 'v2.3.8 Highlights',
  highlightsBody: 'Version 2.3.8 focuses on competition mode and host ecosystem: SEEAI acceptance now requires four-section structured evidence with content-quality gates (no more fake passes); a new design inspiration workflow (PR #11, contributed by @staruhub — thanks!); WorkBuddy unified install; responsive install UI; security hardening; and auto-fix for stale installations.',
  highlightsCards: [
    { title: 'SEEAI Structured Evidence Gate', body: 'Acceptance now requires four sections (first_response / runtime_checkpoint / fallback_decision / demo_path); each must clear a length + template-keyword check. Passed no longer means ready.' },
    { title: 'Design Inspiration Workflow (PR #11)', body: 'Thanks to @staruhub. New super-dev design list / recommend / apply <slug> commands ship a curated inspiration library (linear.app, vercel, stripe...) that writes into the project and regenerates uiux/ui-contract.' },
    { title: 'SEEAI Competition Mode', body: 'New action-driven competition mode: Requirements > Decompose > Search > Solution Doc > Spec > Code > Run > Feedback Loop.' },
    { title: 'WorkBuddy Unified Install', body: 'WorkBuddy promoted from manual to unified install host. Skills auto-installed to ~/.workbuddy/skills/. 21+1 host ecosystem.' },
    { title: 'Responsive Install UI', body: 'Removed verbose protocol column, three-tier responsive layout for narrow/standard/wide terminals.' },
    { title: 'Security Hardening', body: 'New secret-read-guard hook, Web API Key auth, and run store auto-eviction.' },
    { title: 'Auto-Fix Stale Installs', body: 'super-dev and super-dev update automatically clean leftover pth/dist-info/package dirs.' },
    { title: 'rollback / replay / diff', body: 'New pipeline rollback to checkpoints, execution history replay, and stage diff commands.' },
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
                <Badge variant="certified">v2.3.8</Badge>
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
