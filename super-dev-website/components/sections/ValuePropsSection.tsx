import { Bot, FileCheck2, ShieldCheck } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    eyebrow: 'Why Super Dev',
    title: '宿主继续写代码，Super Dev 负责把流程拉直。',
    body: '接入后，宿主会按统一的研发顺序、门禁和交付要求工作。',
    cards: [
      {
        icon: Bot,
        title: '宿主负责模型和编码',
        body: 'Claude Code、Cursor、Codex、Trae 这些宿主继续负责联网、调用工具、改代码和运行项目。',
      },
      {
        icon: ShieldCheck,
        title: 'Super Dev 负责流程治理',
        body: '需求进入后先做 research、三文档和确认，再进入 Spec、实现、质量和交付。',
      },
      {
        icon: FileCheck2,
        title: '输出是可审计交付资产',
        body: 'PRD、架构、UI/UX、Spec、运行验证、质量报告和交付归档都会落成产物。',
      },
    ],
  },
  en: {
    eyebrow: 'Why Super Dev',
    title: 'Keep the host coding. Let Super Dev straighten the workflow.',
    body: 'Once installed, the host follows one governed path from research to delivery.',
    cards: [
      {
        icon: Bot,
        title: 'The host handles models and coding',
        body: 'Claude Code, Cursor, Codex, and Trae still handle browsing, tool calls, file edits, and runtime execution.',
      },
      {
        icon: ShieldCheck,
        title: 'Super Dev handles process governance',
        body: 'The host moves through research, the three core docs, approval, spec, implementation, quality, and delivery.',
      },
      {
        icon: FileCheck2,
        title: 'The output is auditable delivery assets',
        body: 'PRD, architecture, UI/UX, spec, runtime validation, quality reports, and delivery archives are written as artifacts.',
      },
    ],
  },
} as const;

export function ValuePropsSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section id="features" className="border-b border-border-muted bg-bg-secondary py-20 lg:py-24" aria-labelledby="why-title">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="why-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          {copy.cards.map((card) => {
            const Icon = card.icon;
            return (
              <article key={card.title} className="rounded-2xl border border-border-default bg-bg-primary/70 p-6">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-accent-blue/25 bg-accent-blue/10 text-accent-blue">
                  <Icon size={20} aria-hidden="true" />
                </div>
                <h3 className="mb-3 text-xl font-semibold text-text-primary">{card.title}</h3>
                <p className="text-sm leading-7 text-text-secondary">{card.body}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
