import { CheckCircle2, FileCheck2, MonitorPlay, PackageCheck, Search, ShieldCheck, UserCheck } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    eyebrow: 'Pipeline',
    title: '从需求到交付，固定走同一条路径。',
    body: '入口很短，流程很固定。宿主接到需求后按研究、文档、确认、实现、验证、交付推进。',
    stages: [
      {
        icon: Search,
        title: 'Research 与需求增强',
        body: '先读取本地知识库，再联网研究同类产品，补全边界条件、异常路径和验收口径。',
      },
      {
        icon: FileCheck2,
        title: '三文档与 Spec',
        body: '先生成 PRD、Architecture、UI/UX，再让用户确认，确认通过后才创建 Spec 与任务清单。',
      },
      {
        icon: MonitorPlay,
        title: '前端优先与后端联调',
        body: '先把前端做出来并运行验证，再进入后端与联调，避免在不可见状态下盲目堆代码。',
      },
      {
        icon: PackageCheck,
        title: '质量与交付',
        body: 'UI Review、红队检查、交付包、发布演练和 release readiness 一起定义是否能交付。',
      },
    ],
    gatesTitle: '关键门禁',
    gates: [
      { icon: UserCheck, title: '三文档确认门', body: '没有用户确认，不允许创建 Spec，也不允许开始编码。', tone: 'yellow' },
      { icon: CheckCircle2, title: '前端运行验证门', body: '没有 frontend runtime 通过证据，不允许进入后端与中后段。', tone: 'blue' },
      { icon: ShieldCheck, title: '交付 ready / rehearsal passed 门', body: '交付包未 ready 或发布演练未通过，不能宣称完成交付。', tone: 'green' },
    ],
  },
  en: {
    eyebrow: 'Pipeline',
    title: 'From requirement to delivery, the path stays fixed.',
    body: 'The trigger is short and the workflow is fixed. The host moves through research, documentation, approval, implementation, verification, and delivery.',
    stages: [
      {
        icon: Search,
        title: 'Research and requirement hardening',
        body: 'Read local knowledge first, research similar products online, and close gaps in scope, edge cases, and acceptance criteria.',
      },
      {
        icon: FileCheck2,
        title: 'Three core docs and spec',
        body: 'Generate PRD, Architecture, and UI/UX first. After approval, create the spec and task breakdown.',
      },
      {
        icon: MonitorPlay,
        title: 'Frontend first, then backend integration',
        body: 'Build the frontend and verify it runs before moving into backend implementation and end-to-end wiring.',
      },
      {
        icon: PackageCheck,
        title: 'Quality and delivery',
        body: 'UI review, red-team checks, delivery packaging, release rehearsal, and release readiness determine whether the work can actually ship.',
      },
    ],
    gatesTitle: 'Critical gates',
    gates: [
      { icon: UserCheck, title: 'Three-doc approval gate', body: 'Without explicit approval, the host cannot create the spec or start implementation.', tone: 'yellow' },
      { icon: CheckCircle2, title: 'Frontend runtime gate', body: 'Without a passing frontend runtime report, the host cannot continue into backend and later stages.', tone: 'blue' },
      { icon: ShieldCheck, title: 'Delivery ready / rehearsal passed gate', body: 'If the delivery package is not ready or the rehearsal did not pass, the project is not done.', tone: 'green' },
    ],
  },
} as const;

const toneStyles = {
  yellow: 'border-status-yellow/35 bg-status-yellow/6',
  blue: 'border-accent-blue/30 bg-accent-blue/6',
  green: 'border-status-green/35 bg-status-green/6',
} as const;

export function PipelineSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section className="border-b border-border-muted bg-bg-primary py-20 lg:py-24" aria-labelledby="pipeline-title">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="pipeline-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          {copy.stages.map((stage) => {
            const Icon = stage.icon;
            return (
              <article key={stage.title} className="rounded-2xl border border-border-default bg-bg-secondary/55 p-6">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-border-default bg-bg-primary text-accent-blue">
                  <Icon size={20} aria-hidden="true" />
                </div>
                <h3 className="mb-3 text-xl font-semibold text-text-primary">{stage.title}</h3>
                <p className="text-sm leading-7 text-text-secondary">{stage.body}</p>
              </article>
            );
          })}
        </div>

        <div className="mt-12">
          <h3 className="mb-5 text-xl font-semibold text-text-primary">{copy.gatesTitle}</h3>
          <div className="grid gap-4 lg:grid-cols-3">
            {copy.gates.map((gate) => {
              const Icon = gate.icon;
              return (
                <article key={gate.title} className={`rounded-2xl border p-5 ${toneStyles[gate.tone]}`}>
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-current/15 text-current">
                    <Icon size={18} aria-hidden="true" />
                  </div>
                  <h4 className="mb-2 text-lg font-semibold text-text-primary">{gate.title}</h4>
                  <p className="text-sm leading-7 text-text-secondary">{gate.body}</p>
                </article>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
