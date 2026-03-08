import { Boxes, RefreshCw, Rocket, ShieldAlert } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    eyebrow: 'Use Cases',
    title: '四类最常见的落地场景。',
    body: 'Super Dev 更适合真实项目推进，而不是一次性演示。下面这些场景最能体现它的价值。',
    cards: [
      { icon: Rocket, title: '从 0 到 1 做 MVP', body: '输入需求后，先研究同类产品，再生成三文档、Spec 和前端验证，快速做出可演示、可验证的 MVP。'},
      { icon: RefreshCw, title: '接手已有项目继续开发', body: '先理解现有项目和相似产品，再补文档和约束，让宿主不是直接改代码，而是按流水线接手。'},
      { icon: Boxes, title: '统一团队里的 AI 开发流程', body: '不同成员可以继续使用各自习惯的宿主，但 Super Dev 统一触发方式、协议面、质量门禁和交付产物。'},
      { icon: ShieldAlert, title: '把宿主从直接写代码拉回商业交付路径', body: '当宿主倾向于直接开始开发时，Super Dev 强制它先 research、先三文档、先确认，再进入实现。'},
    ],
  },
  en: {
    eyebrow: 'Use Cases',
    title: 'Four common ways teams actually use it.',
    body: 'Super Dev fits real project execution more than one-off demos. These scenarios show where it adds the most value.',
    cards: [
      { icon: Rocket, title: 'Build an MVP from zero to one', body: 'Start with similar-product research, then generate the three core docs, the spec, and frontend validation to ship a demoable MVP fast.'},
      { icon: RefreshCw, title: 'Take over an existing project', body: 'Understand the existing codebase and comparable products first, then rebuild constraints and docs before the host starts changing code.'},
      { icon: Boxes, title: 'Standardize AI development across a team', body: 'Different members can keep their preferred hosts while Super Dev standardizes triggers, protocol surfaces, quality gates, and delivery outputs.'},
      { icon: ShieldAlert, title: 'Pull the host back from direct coding into a delivery path', body: 'When the host wants to jump into implementation, Super Dev forces research, the three core docs, approval, and only then implementation.'},
    ],
  },
} as const;

export function UseCasesSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section className="border-b border-border-muted bg-bg-secondary py-20 lg:py-24" aria-labelledby="use-cases-title">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="use-cases-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {copy.cards.map((card) => {
            const Icon = card.icon;
            return (
              <article key={card.title} className="rounded-2xl border border-border-default bg-bg-primary/70 p-6">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-border-default bg-bg-secondary text-accent-blue">
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
