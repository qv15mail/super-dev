import { HOSTS, STATS } from '@/lib/constants';
import type { SiteLocale } from '@/lib/site-locale';

function HostLogo({ abbr, name }: { abbr: string; name: string }) {
  return (
    <div
      className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border-muted bg-bg-secondary/50 opacity-60 hover:opacity-100 transition-opacity duration-200 shrink-0"
      title={name}
    >
      <span className="w-6 h-6 rounded bg-bg-tertiary flex items-center justify-center text-xs font-mono font-bold text-text-muted">{abbr}</span>
      <span className="text-sm text-text-secondary whitespace-nowrap">{name}</span>
    </div>
  );
}

const STATS_LABELS = {
  zh: ['支持的 AI 宿主', '阶段开发流水线', '档策略预设', '开源许可'],
  en: ['Supported AI Hosts', 'Pipeline Stages', 'Policy Presets', 'Open Source License'],
} as const;

const COPY = {
  zh: '兼容的 AI 宿主工具',
  en: 'Compatible AI hosts',
} as const;

export function SocialProofBand({ locale = 'zh' }: { locale?: SiteLocale }) {
  const labels = STATS_LABELS[locale];
  return (
    <section className="bg-bg-secondary border-y border-border-muted py-10" aria-label="统计数字与支持的工具">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <dl className="flex flex-wrap justify-center gap-8 sm:gap-16 mb-10">
          {STATS.map((stat, index) => (
            <div key={`${stat.value}-${index}`} className="text-center">
              <dt className="text-sm text-text-muted">{labels[index]}</dt>
              <dd className="text-2xl font-bold font-mono text-text-primary mt-1">{stat.value}</dd>
            </div>
          ))}
        </dl>

        <div className="flex items-center gap-4 mb-8">
          <div className="flex-1 h-px bg-border-muted" />
          <span className="text-xs text-text-muted tracking-wider uppercase">{COPY[locale]}</span>
          <div className="flex-1 h-px bg-border-muted" />
        </div>

        <div className="overflow-hidden relative" aria-label={`${COPY[locale]}: ${HOSTS.map((h) => h.name).join('、')}`}>
          <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-bg-secondary to-transparent z-10 pointer-events-none" aria-hidden="true" />
          <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-bg-secondary to-transparent z-10 pointer-events-none" aria-hidden="true" />
          <div className="flex gap-3 [&:hover>div]:animation-play-state-paused">
            <div className="flex gap-3 animate-marquee" aria-hidden="true">
              {HOSTS.map((host) => <HostLogo key={`a-${host.name}`} abbr={host.abbr} name={host.name} />)}
            </div>
            <div className="flex gap-3 animate-marquee2" aria-hidden="true">
              {HOSTS.map((host) => <HostLogo key={`b-${host.name}`} abbr={host.abbr} name={host.name} />)}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
