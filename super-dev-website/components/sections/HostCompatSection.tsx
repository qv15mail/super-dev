import { Badge } from '@/components/ui/Badge';
import { HOSTS, SLASH_HOSTS, TEXT_TRIGGER_HOSTS, type HostStatus } from '@/lib/constants';
import type { SiteLocale } from '@/lib/site-locale';

const STATUS_BADGE_VARIANT: Record<HostStatus, 'certified' | 'compatible' | 'experimental'> = {
  certified: 'certified',
  compatible: 'compatible',
  experimental: 'experimental',
};

const COPY = {
  zh: {
    eyebrow: 'Host Support',
    title: '先看怎么触发，再看宿主协议类型。',
    body: '官网先给用户一个能立刻执行的答案：哪些宿主用 /super-dev，哪些宿主用 super-dev:。文档页再展开 commands、AGENTS、steering、rules、skills 这些接入面。',
    slash: 'Slash 宿主',
    text: 'Text-trigger 宿主',
    slashBody: '这些宿主直接输入 /super-dev 你的需求。',
    textBody: '这些宿主使用 super-dev: 你的需求。',
    matrixTitle: '宿主矩阵',
    protocol: '协议面',
    trigger: '触发',
    maturity: '成熟度',
    labels: { certified: '认证', compatible: '兼容', experimental: '实验性' },
  },
  en: {
    eyebrow: 'Host Support',
    title: 'Show the trigger first, then the protocol type.',
    body: 'The homepage should answer the practical question first: which hosts use /super-dev and which hosts use super-dev:. The docs page can expand the underlying protocol surfaces later.',
    slash: 'Slash hosts',
    text: 'Text-trigger hosts',
    slashBody: 'These hosts accept /super-dev your requirement.',
    textBody: 'These hosts use super-dev: your requirement.',
    matrixTitle: 'Host matrix',
    protocol: 'Protocol surface',
    trigger: 'Trigger',
    maturity: 'Maturity',
    labels: { certified: 'Certified', compatible: 'Compatible', experimental: 'Experimental' },
  },
} as const;

function HostChip({ label }: { label: string }) {
  return <span className="rounded-lg border border-border-default bg-bg-primary px-3 py-2 font-mono text-sm text-text-primary">{label}</span>;
}

export function HostCompatSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];

  return (
    <section id="hosts" className="border-b border-border-muted bg-bg-secondary py-20 lg:py-24" aria-labelledby="hosts-title">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="hosts-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <article className="rounded-2xl border border-border-default bg-bg-primary/70 p-6">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h3 className="text-xl font-semibold text-text-primary">{copy.slash}</h3>
              <code className="rounded-md bg-bg-secondary px-2.5 py-1 font-mono text-sm text-accent-blue">/super-dev</code>
            </div>
            <p className="mb-5 text-sm leading-7 text-text-secondary">{copy.slashBody}</p>
            <div className="flex flex-wrap gap-2">
              {SLASH_HOSTS.map((host) => (
                <HostChip key={host.name} label={host.name} />
              ))}
            </div>
          </article>

          <article className="rounded-2xl border border-border-default bg-bg-primary/70 p-6">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h3 className="text-xl font-semibold text-text-primary">{copy.text}</h3>
              <code className="rounded-md bg-bg-secondary px-2.5 py-1 font-mono text-sm text-accent-blue">super-dev:</code>
            </div>
            <p className="mb-5 text-sm leading-7 text-text-secondary">{copy.textBody}</p>
            <div className="flex flex-wrap gap-2">
              {TEXT_TRIGGER_HOSTS.map((host) => (
                <HostChip key={host.name} label={host.name} />
              ))}
            </div>
          </article>
        </div>

        <div className="mt-12 rounded-2xl border border-border-default bg-bg-primary/70 p-6">
          <div className="mb-5 flex items-center justify-between gap-3">
            <h3 className="text-xl font-semibold text-text-primary">{copy.matrixTitle}</h3>
            <div className="flex flex-wrap gap-2">
              {(Object.keys(copy.labels) as HostStatus[]).map((status) => (
                <Badge key={status} variant={STATUS_BADGE_VARIANT[status]}>{copy.labels[status]}</Badge>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-y-3 text-left text-sm">
              <thead>
                <tr className="text-text-muted">
                  <th className="px-3 py-2 font-medium">Host</th>
                  <th className="px-3 py-2 font-medium">{copy.trigger}</th>
                  <th className="px-3 py-2 font-medium">{copy.protocol}</th>
                  <th className="px-3 py-2 font-medium">{copy.maturity}</th>
                </tr>
              </thead>
              <tbody>
                {HOSTS.map((host) => (
                  <tr key={host.name} className="rounded-xl border border-border-default bg-bg-secondary/45">
                    <td className="rounded-l-xl px-3 py-3 font-mono text-text-primary">{host.name}</td>
                    <td className="px-3 py-3 font-mono text-accent-blue">{host.trigger === 'slash' ? '/super-dev' : 'super-dev:'}</td>
                    <td className="px-3 py-3 text-text-secondary">{host.protocol}</td>
                    <td className="rounded-r-xl px-3 py-3"><Badge variant={STATUS_BADGE_VARIANT[host.status]}>{copy.labels[host.status]}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
