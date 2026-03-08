import type { Metadata } from 'next';
import Link from 'next/link';
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Command,
  FolderTree,
  Layers3,
  LifeBuoy,
  Package,
  Rocket,
  Search,
  ShieldCheck,
  Sparkles,
  Terminal,
  Workflow,
} from 'lucide-react';
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { CopyCommand } from '@/components/ui/CopyCommand';

export const metadata: Metadata = {
  title: '文档',
  description:
    'Super Dev 独立文档页面。覆盖安装、宿主矩阵、触发方式、12 阶段流水线、本地知识库、质量门禁、交付标准与常用命令。',
};

const DOC_SECTIONS = [
  { id: 'overview', label: '总览', icon: BookOpen },
  { id: 'quickstart', label: '快速开始', icon: Rocket },
  { id: 'install', label: '安装方式', icon: Package },
  { id: 'hosts', label: '宿主矩阵', icon: Layers3 },
  { id: 'triggers', label: '触发方式', icon: Command },
  { id: 'pipeline', label: '流水线', icon: Workflow },
  { id: 'knowledge', label: '知识库', icon: FolderTree },
  { id: 'quality', label: '质量与交付', icon: ShieldCheck },
  { id: 'commands', label: '常用命令', icon: Terminal },
  { id: 'troubleshooting', label: '故障排查', icon: LifeBuoy },
] as const;

const SLASH_HOSTS = [
  'claude-code',
  'codebuddy',
  'codebuddy-cli',
  'cursor',
  'cursor-cli',
  'gemini-cli',
  'iflow',
  'kiro-cli',
  'opencode',
  'qoder',
  'qoder-cli',
  'windsurf',
  'antigravity',
] as const;

const TEXT_TRIGGER_HOSTS = ['codex-cli', 'kimi-cli', 'kiro', 'trae'] as const;

const HOST_PROTOCOLS = [
  {
    category: 'CLI',
    items: [
      { host: 'claude-code', trigger: '/super-dev', protocol: '官方 commands + subagents', grade: 'Certified' },
      { host: 'codex-cli', trigger: 'super-dev:', protocol: '官方 AGENTS.md + 官方 Skills', grade: 'Certified' },
      { host: 'opencode', trigger: '/super-dev', protocol: '官方 commands + skills', grade: 'Experimental' },
      { host: 'gemini-cli', trigger: '/super-dev', protocol: '官方 commands + GEMINI.md', grade: 'Compatible' },
      { host: 'kiro-cli', trigger: '/super-dev', protocol: '官方 commands + AGENTS.md', grade: 'Compatible' },
      { host: 'kimi-cli', trigger: 'super-dev:', protocol: '官方 AGENTS.md + 文本触发', grade: 'Compatible' },
      { host: 'iflow', trigger: '/super-dev', protocol: '官方 commands + skills', grade: 'Experimental' },
      { host: 'cursor-cli', trigger: '/super-dev', protocol: '官方 commands + rules', grade: 'Compatible' },
      { host: 'qoder-cli', trigger: '/super-dev', protocol: '官方 commands + skills', grade: 'Compatible' },
      { host: 'codebuddy-cli', trigger: '/super-dev', protocol: '官方 commands + skills', grade: 'Compatible' },
    ],
  },
  {
    category: 'IDE',
    items: [
      { host: 'cursor', trigger: '/super-dev', protocol: '官方 commands + rules', grade: 'Experimental' },
      { host: 'antigravity', trigger: '/super-dev', protocol: '官方 commands + GEMINI.md + workflows', grade: 'Compatible' },
      { host: 'kiro', trigger: 'super-dev:', protocol: '官方 project steering + global steering', grade: 'Experimental' },
      { host: 'qoder', trigger: '/super-dev', protocol: '官方 commands + rules + skills', grade: 'Experimental' },
      { host: 'trae', trigger: 'super-dev:', protocol: '官方 project rules + 兼容 Skill', grade: 'Compatible' },
      { host: 'codebuddy', trigger: '/super-dev', protocol: '官方 commands + skills', grade: 'Experimental' },
      { host: 'windsurf', trigger: '/super-dev', protocol: '官方 workflows + skills', grade: 'Experimental' },
    ],
  },
] as const;

const PIPELINE_STEPS = [
  {
    title: '01. 同类产品研究',
    detail: '先使用宿主联网能力研究同类产品、交互模式、差异化机会与商业信号。',
  },
  {
    title: '02. 需求增强',
    detail: '补足边界条件、异常路径、验收口径、风险与优先级，避免模糊需求直接进入编码。',
  },
  {
    title: '03. 三份核心文档',
    detail: '输出 PRD、Architecture、UI/UX 三文档，形成可讨论、可审计的执行基线。',
  },
  {
    title: '04. 用户确认门',
    detail: '三文档完成后必须暂停，等待用户确认或要求修改。未确认不得进入 Spec 与编码。',
  },
  {
    title: '05. Spec / Tasks',
    detail: '在确认通过后生成变更提案、任务清单和分工顺序，控制实现范围。',
  },
  {
    title: '06. 前端优先',
    detail: '先完成前端结构与可运行预览，并通过前端运行验证，再进入后端。',
  },
  {
    title: '07. 后端与联调',
    detail: '完成 API、数据层、服务层与联调，保证交互闭环而不是仅有静态页面。',
  },
  {
    title: '08. 质量门禁',
    detail: '执行 UI Review、红队审查、安全、性能、架构与策略阈值检查。',
  },
  {
    title: '09. 交付与发布演练',
    detail: '生成交付包、发布演练报告和 release readiness 结果，确保项目可以上线和复盘。',
  },
] as const;

const CORE_COMMANDS = [
  {
    title: '安装与引导',
    code: `pip install -U super-dev\n# 或\nuv tool install super-dev\n\n# 进入宿主安装引导\nsuper-dev`,
    filename: 'Terminal',
  },
  {
    title: '宿主接入与诊断',
    code: `super-dev onboard --host claude-code --force --yes\nsuper-dev doctor --host trae --repair --force\nsuper-dev detect --json`,
    filename: 'Host Operations',
  },
  {
    title: '文档确认与恢复',
    code: `super-dev review docs --status confirmed --comment "三文档已确认"\nsuper-dev run --resume`,
    filename: 'Pipeline Gates',
  },
  {
    title: '质量 / 发布 / 更新',
    code: `super-dev quality --type all\nsuper-dev release readiness --verify-tests\nsuper-dev update --check\nsuper-dev update`,
    filename: 'Quality & Release',
  },
] as const;

function gradeVariant(grade: string) {
  if (grade === 'Certified') return 'certified';
  if (grade === 'Compatible') return 'compatible';
  return 'experimental';
}

function SectionCard({
  id,
  eyebrow,
  title,
  description,
  children,
}: {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 rounded-2xl border border-border-default bg-bg-secondary/60 p-6 sm:p-8 lg:p-10">
      <div className="mb-8 max-w-3xl">
        <p className="mb-3 text-xs font-mono uppercase tracking-[0.22em] text-accent-blue">{eyebrow}</p>
        <h2 className="mb-3 text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">{title}</h2>
        <p className="text-base leading-7 text-text-secondary">{description}</p>
      </div>
      {children}
    </section>
  );
}

export default function DocsPage() {
  return (
    <>
      <Nav />
      <main className="min-h-screen bg-bg-primary pt-14" id="main-content">
        <section className="border-b border-border-muted bg-bg-primary">
          <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:py-20">
            <div className="grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_360px] lg:items-end">
              <div>
                <div className="mb-4 flex flex-wrap items-center gap-2">
                  <Badge variant="version">Documentation</Badge>
                  <Badge variant="certified">v2.0.8</Badge>
                  <Badge variant="compatible">独立文档页</Badge>
                </div>
                <h1 className="max-w-4xl text-4xl font-bold leading-tight tracking-tight text-text-primary sm:text-5xl">
                  Super Dev 文档中心
                </h1>
                <p className="mt-5 max-w-3xl text-lg leading-8 text-text-secondary">
                  这不是 README 的镜像页，而是站内独立文档。它覆盖安装、宿主适配、触发方式、12 阶段流水线、知识库、质量门禁、交付标准和常用命令，方便直接查、直接用、直接对照执行。
                </p>
              </div>

              <div className="rounded-2xl border border-border-default bg-bg-elevated p-5 glow-blue">
                <div className="mb-4 flex items-center gap-2 text-sm font-medium text-text-primary">
                  <Sparkles size={16} className="text-accent-blue" />
                  最短路径
                </div>
                <div className="space-y-3 text-sm text-text-secondary">
                  <div className="rounded-xl border border-border-default bg-bg-secondary p-4">
                    <div className="mb-2 text-xs uppercase tracking-[0.18em] text-text-muted">Install</div>
                    <CopyCommand command="pip install -U super-dev" className="w-full" />
                  </div>
                  <div className="rounded-xl border border-border-default bg-bg-secondary p-4">
                    <div className="mb-2 text-xs uppercase tracking-[0.18em] text-text-muted">Bootstrap</div>
                    <CodeBlock code="super-dev" filename="Installer" />
                  </div>
                  <div className="rounded-xl border border-border-default bg-bg-secondary p-4">
                    <div className="mb-3 text-xs uppercase tracking-[0.18em] text-text-muted">Trigger</div>
                    <div className="space-y-2">
                      <div className="rounded-lg border border-border-default bg-bg-primary px-3 py-2 font-mono text-text-primary">/super-dev 你的需求</div>
                      <div className="rounded-lg border border-border-default bg-bg-primary px-3 py-2 font-mono text-text-primary">super-dev: 你的需求</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:py-14">
          <div className="grid gap-8 xl:grid-cols-[220px_minmax(0,1fr)_280px]">
            <aside className="hidden xl:block">
              <div className="sticky top-24 rounded-2xl border border-border-default bg-bg-secondary/60 p-4">
                <div className="mb-3 text-xs font-mono uppercase tracking-[0.18em] text-text-muted">目录</div>
                <nav className="space-y-1">
                  {DOC_SECTIONS.map((section) => {
                    const Icon = section.icon;
                    return (
                      <a
                        key={section.id}
                        href={`#${section.id}`}
                        className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary"
                      >
                        <Icon size={15} className="text-accent-blue" />
                        {section.label}
                      </a>
                    );
                  })}
                </nav>
              </div>
            </aside>

            <div className="space-y-8">
              <SectionCard
                id="overview"
                eyebrow="Overview"
                title="它解决的不是写代码本身，而是宿主 AI 的交付纪律"
                description="Super Dev 的核心作用，是把 Claude Code、Codex CLI、Cursor、Trae、Qoder、Windsurf 这类宿主工具拉进一套研究优先、文档先行、质量门禁和交付可审计的工程流程里。宿主负责模型推理、工具调用和真实编码，Super Dev 负责让它按商业项目的方式做对、做全、做得可复盘。"
              >
                <div className="grid gap-4 md:grid-cols-3">
                  {[
                    {
                      title: '宿主负责执行',
                      body: '模型推理、联网检索、终端调用、改代码、运行项目。',
                    },
                    {
                      title: 'Super Dev 负责治理',
                      body: '流程阶段、文档确认门、质量门禁、交付标准、状态与审计。',
                    },
                    {
                      title: '项目产物可追溯',
                      body: '每个阶段都有文档、状态文件、质量报告与交付物，不靠口头约束。',
                    },
                  ].map((item) => (
                    <div key={item.title} className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <h3 className="mb-2 text-base font-semibold text-text-primary">{item.title}</h3>
                      <p className="text-sm leading-7 text-text-secondary">{item.body}</p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                id="quickstart"
                eyebrow="Quick Start"
                title="从安装到开始工作，只需要四步"
                description="推荐先装 Python 工具，再进入宿主安装引导。完成接入后，用户只需要在宿主里输入统一触发词，宿主就会按照 Super Dev 流水线开始工作。"
              >
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                    <h3 className="mb-4 text-base font-semibold text-text-primary">标准路径</h3>
                    <ol className="space-y-3 text-sm leading-7 text-text-secondary">
                      {[
                        '安装 super-dev。',
                        '终端输入 super-dev，进入宿主安装引导。',
                        '选择宿主并安装规则、commands、skills、agents 或 steering。',
                        '打开宿主，输入 /super-dev 需求 或 super-dev: 需求。',
                      ].map((item, index) => (
                        <li key={item} className="flex gap-3">
                          <span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent-blue/40 bg-accent-blue/10 font-mono text-xs text-accent-blue">{index + 1}</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                  <CodeBlock
                    filename="Terminal"
                    code={`pip install -U super-dev\n# 或\nuv tool install super-dev\n\n# 进入安装引导\nsuper-dev\n\n# Slash 宿主\n/super-dev 打造一个商业官网\n\n# 非 slash 宿主\nsuper-dev: 打造一个商业官网`}
                  />
                </div>
              </SectionCard>

              <SectionCard
                id="install"
                eyebrow="Installation"
                title="安装会自动装 Super Dev 的 Python 依赖，不会替你安装宿主软件"
                description="pip 和 uv 安装的，是 Super Dev 这个 Python CLI 工具以及它声明的 Python 依赖。它不会替用户安装 Claude Code、Cursor、Trae、Gemini CLI、Node.js、Docker 或宿主登录状态。宿主软件和系统级环境仍需用户自己准备。"
              >
                <div className="grid gap-4 lg:grid-cols-2">
                  <CodeBlock
                    filename="pip / uv"
                    code={`pip install -U super-dev\n\n# 推荐的 uv 方式\nuv tool install super-dev\n\n# 更新到最新版本\nsuper-dev update\nsuper-dev update --check`}
                  />
                  <div className="grid gap-4">
                    <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <h3 className="mb-2 text-base font-semibold text-text-primary">会自动安装</h3>
                      <ul className="space-y-2 text-sm leading-7 text-text-secondary">
                        {['rich / pyyaml / requests / fastapi 等 Python 依赖', 'Super Dev 自身 CLI 代码', '宿主适配、质量门禁、release readiness 等能力'].map((item) => (
                          <li key={item} className="flex gap-2"><CheckCircle2 size={16} className="mt-1 text-status-green" />{item}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <h3 className="mb-2 text-base font-semibold text-text-primary">不会自动安装</h3>
                      <ul className="space-y-2 text-sm leading-7 text-text-secondary">
                        {['Claude Code / Cursor / Trae / Gemini CLI 等宿主本体', 'Node.js、Docker、数据库服务等系统环境', '宿主账号登录、联网权限与浏览器能力'].map((item) => (
                          <li key={item} className="flex gap-2"><ChevronRight size={16} className="mt-1 text-text-muted" />{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </SectionCard>

              <SectionCard
                id="hosts"
                eyebrow="Host Matrix"
                title="宿主不是一刀切。每个宿主都有自己的接入协议和触发方式"
                description="Super Dev 既有 Python 主程序，也有宿主侧的协议面。具体协议会因宿主不同而不同：有的依赖 commands，有的依赖 AGENTS，有的依赖 steering，有的依赖 skills 或 subagents。安装引导的职责，就是把这些面正确写到宿主和项目里。"
              >
                <div className="space-y-6">
                  {HOST_PROTOCOLS.map((group) => (
                    <div key={group.category} className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <div className="mb-4 flex items-center justify-between gap-3">
                        <h3 className="text-base font-semibold text-text-primary">{group.category} 宿主</h3>
                        <Badge variant="version">{group.items.length} 个</Badge>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full border-collapse text-sm">
                          <thead>
                            <tr className="border-b border-border-default text-left text-text-muted">
                              <th className="pb-3 pr-4 font-medium">宿主</th>
                              <th className="pb-3 pr-4 font-medium">触发</th>
                              <th className="pb-3 pr-4 font-medium">协议</th>
                              <th className="pb-3 font-medium">状态</th>
                            </tr>
                          </thead>
                          <tbody>
                            {group.items.map((item) => (
                              <tr key={item.host} className="border-b border-border-muted/60 align-top last:border-b-0">
                                <td className="py-3 pr-4 font-mono text-text-primary">{item.host}</td>
                                <td className="py-3 pr-4 font-mono text-accent-blue">{item.trigger}</td>
                                <td className="py-3 pr-4 text-text-secondary">{item.protocol}</td>
                                <td className="py-3"><Badge variant={gradeVariant(item.grade)}>{item.grade}</Badge></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                id="triggers"
                eyebrow="Trigger Model"
                title="触发只有两种：slash 或文本触发"
                description="站内文档、安装引导、doctor/detect 输出和官网说明，都应该保持同一份结论。不要让用户在不同入口看到不同说法。"
              >
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                    <div className="mb-3 flex items-center gap-2">
                      <Badge variant="certified">Slash</Badge>
                      <span className="text-sm text-text-muted">输入 /super-dev 需求</span>
                    </div>
                    <div className="mb-4 rounded-lg border border-border-default bg-bg-primary px-4 py-3 font-mono text-sm text-text-primary">/super-dev 你的需求</div>
                    <div className="flex flex-wrap gap-2">
                      {SLASH_HOSTS.map((host) => (
                        <Badge key={host} variant="default" className="font-mono">{host}</Badge>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                    <div className="mb-3 flex items-center gap-2">
                      <Badge variant="compatible">Text Trigger</Badge>
                      <span className="text-sm text-text-muted">输入 super-dev: 需求</span>
                    </div>
                    <div className="mb-4 rounded-lg border border-border-default bg-bg-primary px-4 py-3 font-mono text-sm text-text-primary">super-dev: 你的需求</div>
                    <div className="flex flex-wrap gap-2">
                      {TEXT_TRIGGER_HOSTS.map((host) => (
                        <Badge key={host} variant="default" className="font-mono">{host}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </SectionCard>

              <SectionCard
                id="pipeline"
                eyebrow="Pipeline"
                title="真正的价值不在 slash 命令本身，而在这条被强制执行的流水线"
                description="Super Dev 不靠一句 prompt 解决问题，而是靠阶段化治理把宿主 AI 限制在正确路径里：先研究、先文档、先确认、先前端验证、再后端、再质量和交付。"
              >
                <div className="grid gap-4 lg:grid-cols-2">
                  {PIPELINE_STEPS.map((step, index) => (
                    <div key={step.title} className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <div className="mb-2 flex items-center gap-3">
                        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-accent-blue/40 bg-accent-blue/10 font-mono text-xs text-accent-blue">{index + 1}</span>
                        <h3 className="text-base font-semibold text-text-primary">{step.title}</h3>
                      </div>
                      <p className="text-sm leading-7 text-text-secondary">{step.detail}</p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                id="knowledge"
                eyebrow="Knowledge Base"
                title="本地 knowledge 不是附件，而是整个流水线的约束输入"
                description="当项目里存在 knowledge/ 和 output/knowledge-cache/*-knowledge-bundle.json 时，宿主必须先读取并把命中的清单、基线、反模式、场景包带进 research、三文档、Spec、实现与质量门禁。它不是锦上添花，而是优先级高于普通外部搜索的约束输入。"
              >
                <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
                  <CodeBlock
                    filename="Knowledge Layout"
                    code={`knowledge/\n  design/\n  development/\n  security/\n  testing/\n  cicd/\n\noutput/knowledge-cache/\n  <project>-knowledge-bundle.json`}
                  />
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                    <h3 className="mb-3 text-base font-semibold text-text-primary">阶段应用规则</h3>
                    <ul className="space-y-2 text-sm leading-7 text-text-secondary">
                      {[
                        'research 阶段：先读本地知识，再联网研究同类产品。',
                        'PRD：优先吸收 product / business / process 类知识。',
                        'Architecture：吸收 architecture / development / security / data 基线。',
                        'UI/UX：吸收 design 与交互反模式库。',
                        'quality / delivery：吸收 testing / cicd / release / incident 基线。',
                      ].map((item) => (
                        <li key={item} className="flex gap-2"><Search size={16} className="mt-1 text-accent-blue" />{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </SectionCard>

              <SectionCard
                id="quality"
                eyebrow="Quality & Delivery"
                title="真正交付完成，不是代码写完，而是门禁全部通过"
                description="Super Dev 会在中后段持续生成运行验证、UI Review、红队审查、交付包和发布演练结果。只有这些门禁都通过，项目才进入真正意义上的可交付状态。"
              >
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {[
                    ['文档确认门', '三文档完成后必须人工确认，未确认不得进入 Spec 与编码。'],
                    ['前端运行验证', '必须存在并通过 frontend-runtime 报告，后端和联调才允许继续。'],
                    ['质量门禁', 'UI Review、红队审查、安全、性能、架构和策略阈值一并检查。'],
                    ['交付与发布演练', '交付包 ready、演练 passed、release readiness 通过，才算真正完成。'],
                  ].map(([title, body]) => (
                    <div key={title} className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <h3 className="mb-2 text-base font-semibold text-text-primary">{title}</h3>
                      <p className="text-sm leading-7 text-text-secondary">{body}</p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                id="commands"
                eyebrow="Commands"
                title="常用命令分成四类：安装、接入、门禁、发布"
                description="用户不需要记全所有命令，但官网应该把最关键的命令集中展示，方便直接复制。"
              >
                <div className="grid gap-4 xl:grid-cols-2">
                  {CORE_COMMANDS.map((item) => (
                    <div key={item.title} className="rounded-xl border border-border-default bg-bg-elevated p-5">
                      <h3 className="mb-4 text-base font-semibold text-text-primary">{item.title}</h3>
                      <CodeBlock code={item.code} filename={item.filename} />
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                id="troubleshooting"
                eyebrow="Troubleshooting"
                title="先确认宿主有没有真正吃到接入面，再谈 prompt 是否正确"
                description="大部分“Super Dev 没工作”的问题，不是触发词错了，而是宿主没有加载规则、commands、AGENTS、steering 或 skills。排查顺序应该先看接入面，再看会话刷新，再看宿主能力本身。"
              >
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                    <h3 className="mb-3 text-base font-semibold text-text-primary">推荐排查顺序</h3>
                    <ol className="space-y-2 text-sm leading-7 text-text-secondary">
                      {[
                        '执行 super-dev doctor --host <host> --repair --force。',
                        '检查安装引导输出的项目级与用户级接入面是否真实存在。',
                        '完全关闭宿主，重新打开项目，新建一个对话。',
                        '先用 smoke 语句验证首轮响应，而不是直接发正式需求。',
                        '如果宿主直接开始开发，说明当前会话没有吃到规则。',
                      ].map((item) => (
                        <li key={item} className="flex gap-2"><ChevronRight size={16} className="mt-1 text-text-muted" />{item}</li>
                      ))}
                    </ol>
                  </div>
                  <CodeBlock
                    filename="Smoke"
                    code={`# Slash 宿主\n/super-dev "请先不要开始编码，只回复 SMOKE_OK，并说明你会先做 research、再写三文档并等待确认。"\n\n# 非 slash 宿主\nsuper-dev: 请先不要开始编码，只回复 SMOKE_OK，并说明你会先做 research、再写三文档并等待确认。`}
                  />
                </div>
              </SectionCard>
            </div>

            <aside>
              <div className="sticky top-24 space-y-4">
                <div className="rounded-2xl border border-border-default bg-bg-secondary/60 p-5">
                  <div className="mb-3 flex items-center gap-2 text-sm font-medium text-text-primary">
                    <Terminal size={16} className="text-accent-blue" />
                    快捷操作
                  </div>
                  <div className="space-y-3">
                    <CopyCommand command="pip install -U super-dev" className="w-full" />
                    <CopyCommand command="uv tool install super-dev" className="w-full" />
                    <CopyCommand command="super-dev update" className="w-full" />
                  </div>
                </div>

                <div className="rounded-2xl border border-border-default bg-bg-secondary/60 p-5">
                  <div className="mb-3 flex items-center gap-2 text-sm font-medium text-text-primary">
                    <Workflow size={16} className="text-accent-blue" />
                    文档入口
                  </div>
                  <div className="space-y-2 text-sm text-text-secondary">
                    <Link href="/pricing" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">
                      定价
                      <ArrowRight size={14} />
                    </Link>
                    <Link href="/changelog" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">
                      更新日志
                      <ArrowRight size={14} />
                    </Link>
                    <a href="https://github.com/shangyankeji/super-dev" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">
                      GitHub 仓库
                      <ArrowRight size={14} />
                    </a>
                    <a href="https://pypi.org/project/super-dev/" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">
                      PyPI 页面
                      <ArrowRight size={14} />
                    </a>
                  </div>
                </div>

                <div className="rounded-2xl border border-accent-blue/20 bg-accent-blue/5 p-5">
                  <div className="mb-2 text-sm font-medium text-text-primary">适合的使用方式</div>
                  <p className="text-sm leading-7 text-text-secondary">
                    如果用户只想快速开始，让他先安装、先运行 <code className="rounded bg-bg-primary px-1.5 py-0.5 font-mono text-text-primary">super-dev</code>、选宿主，再在宿主里用统一触发词启动。把复杂的协议面交给安装引导处理，不要让用户自己猜。
                  </p>
                </div>
              </div>
            </aside>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
