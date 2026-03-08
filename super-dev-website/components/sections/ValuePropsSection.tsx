import { Bot, FileCheck2, ShieldCheck } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    eyebrow: 'Why Super Dev',
    title: '它解决的不是“会不会写代码”，而是“能不能按商业级流程把项目做对”。',
    body: '首页先说明区别，再说明流程。用户已经有宿主和模型，真正缺的是一套能约束宿主工作的治理协议。',
    cards: [
      {
        icon: Bot,
        title: '宿主负责模型和编码',
        body: 'Claude Code、Cursor、Codex、Trae 这些宿主继续负责联网、调用工具、改代码和运行项目。',
      },
      {
        icon: ShieldCheck,
        title: 'Super Dev 负责流程治理',
        body: '需求进入后不会直接写代码，而是先 research、先三文档、先确认，再进入 Spec、实现、质量和交付。',
      },
      {
        icon: FileCheck2,
        title: '输出是可审计交付资产',
        body: 'PRD、架构、UI/UX、Spec、运行验证、质量报告、交付归档都会落成产物，而不是只留一段聊天记录。',
      },
    ],
  },
  en: {
    eyebrow: 'Why Super Dev',
    title: 'The real problem is not whether AI can write code. It is whether the work can follow a commercial delivery process.',
    body: 'The user already has hosts and models. What is missing is a governance layer that can force the host to work through a shippable path.',
    cards: [
      {
        icon: Bot,
        title: 'The host handles models and coding',
        body: 'Claude Code, Cursor, Codex, and Trae still handle browsing, tool calls, file edits, and runtime execution.',
      },
      {
        icon: ShieldCheck,
        title: 'Super Dev handles process governance',
        body: 'The host does not jump straight into coding. It must go through research, the three core docs, approval, spec, implementation, quality, and delivery.',
      },
      {
        icon: FileCheck2,
        title: 'The output is auditable delivery assets',
        body: 'PRD, architecture, UI/UX, spec, runtime validation, quality reports, and delivery archives are written as artifacts instead of being lost in chat.',
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
