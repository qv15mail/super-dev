import { Briefcase, Rocket, UserRound } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    eyebrow: 'Who It Is For',
    title: '先服务最需要把 AI 开发拉回正轨的人。',
    body: '官网不应该泛泛地说“适合所有人”。Super Dev 最先服务的是那些已经在用 AI coding，但不希望结果停留在聊天记录和半成品上的用户。',
    cards: [
      {
        icon: UserRound,
        title: 'AI coding 重度个人开发者',
        body: '你已经大量使用 Claude Code、Cursor、Codex 或 Trae，但希望每次输出都更稳、更完整、更接近真实交付。',
      },
      {
        icon: Rocket,
        title: '小团队 / 创业团队',
        body: '你们要快速做 MVP、快速验证商业可行性，但不想让 AI 开发过程失控，也不想把代码和决策都埋进聊天记录里。',
      },
      {
        icon: Briefcase,
        title: '需要规范宿主开发流程的项目团队',
        body: '你们要让不同成员在不同宿主里保持同样的流程纪律、质量标准和交付证据，而不是各写各的。',
      },
    ],
  },
  en: {
    eyebrow: 'Who It Is For',
    title: 'Start with the users who already rely on AI coding and need the output to stay under control.',
    body: 'The homepage should not claim that this is for everyone. Super Dev is for people who already use AI coding heavily and do not want the outcome to stop at chat logs and partial code.',
    cards: [
      {
        icon: UserRound,
        title: 'Heavy AI coding individuals',
        body: 'You already use Claude Code, Cursor, Codex, or Trae a lot, and you want the output to be more stable, more complete, and closer to actual delivery.',
      },
      {
        icon: Rocket,
        title: 'Small teams and startup teams',
        body: 'You need to ship MVPs and test business viability fast, but you do not want the AI development process to drift or disappear into chat history.',
      },
      {
        icon: Briefcase,
        title: 'Project teams standardizing host workflows',
        body: 'You want different members using different hosts to follow the same process discipline, quality standards, and delivery evidence model.',
      },
    ],
  },
} as const;

export function WhoItsForSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section className="border-b border-border-muted bg-bg-primary py-20 lg:py-24" aria-labelledby="who-title">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="who-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          {copy.cards.map((card) => {
            const Icon = card.icon;
            return (
              <article key={card.title} className="rounded-2xl border border-border-default bg-bg-secondary/55 p-6">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-border-default bg-bg-primary text-accent-blue">
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
