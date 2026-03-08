import { HOSTS, STATS } from '@/lib/constants';
import type { SiteLocale } from '@/lib/site-locale';

function HostLogo({ name }: { name: string }) {
  const initial = name.trim().charAt(0).toUpperCase();
  return (
    <div className="flex shrink-0 items-center gap-2 rounded-lg border border-border-muted bg-bg-secondary/50 px-4 py-2 opacity-70 transition-opacity duration-200 hover:opacity-100" title={name}>
      <span className="flex h-6 w-6 items-center justify-center rounded bg-bg-tertiary text-xs font-mono font-bold text-text-muted">{initial}</span>
      <span className="whitespace-nowrap text-sm text-text-secondary">{name}</span>
    </div>
  );
}

const COPY = {
  zh: {
    hosts: '当前宿主覆盖',
    labels: STATS.zh,
  },
  en: {
    hosts: 'Current host coverage',
    labels: STATS.en,
  },
} as const;

export function SocialProofBand({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];

  return (
    <section className="border-y border-border-muted bg-bg-secondary py-10" aria-label="Site trust signals">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <dl className="mb-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {copy.labels.map((stat) => (
            <div key={stat.label} className="rounded-xl border border-border-default bg-bg-primary/60 px-5 py-4">
              <dt className="text-sm text-text-muted">{stat.label}</dt>
              <dd className="mt-2 text-2xl font-bold font-mono text-text-primary">{stat.value}</dd>
            </div>
          ))}
        </dl>

        <div className="mb-5 flex items-center gap-4">
          <div className="h-px flex-1 bg-border-muted" />
          <span className="text-xs uppercase tracking-wider text-text-muted">{copy.hosts}</span>
          <div className="h-px flex-1 bg-border-muted" />
        </div>

        <div className="relative overflow-hidden" aria-label={`${copy.hosts}: ${HOSTS.map((h) => h.name).join(', ')}`}>
          <div className="pointer-events-none absolute bottom-0 left-0 top-0 z-10 w-16 bg-gradient-to-r from-bg-secondary to-transparent" aria-hidden="true" />
          <div className="pointer-events-none absolute bottom-0 right-0 top-0 z-10 w-16 bg-gradient-to-l from-bg-secondary to-transparent" aria-hidden="true" />
          <div className="flex gap-3 [&:hover>div]:animation-play-state-paused">
            <div className="flex gap-3 animate-marquee" aria-hidden="true">
              {HOSTS.map((host) => <HostLogo key={`a-${host.name}`} name={host.name} />)}
            </div>
            <div className="flex gap-3 animate-marquee2" aria-hidden="true">
              {HOSTS.map((host) => <HostLogo key={`b-${host.name}`} name={host.name} />)}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
