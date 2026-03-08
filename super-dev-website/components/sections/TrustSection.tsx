import { Archive, BadgeCheck, BookCopy, PackageCheck, ShieldCheck } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    eyebrow: 'Proof / Trust',
    title: '可信度来自可验证的证据。',
    body: '开源、已发布、多宿主、本地知识库、质量门禁和交付产物，都直接展示给用户。',
    items: [
      { icon: BadgeCheck, title: 'MIT 开源与 PyPI 发布', body: '代码可见、安装路径清晰、版本可追踪，版本升级和分发路径也足够明确。'},
      { icon: PackageCheck, title: '多宿主接入', body: '同一套治理逻辑可安装到 CLI 和 IDE 宿主，不要求用户迁移到新的开发工具。'},
      { icon: BookCopy, title: '本地知识库优先', body: 'knowledge/ 和 knowledge bundle 会优先进入 research、三文档、Spec、质量与交付。'},
      { icon: ShieldCheck, title: 'UI Review 与 Release Readiness', body: '运行验证、质量门禁和发布检查都会明确产出结果，方便判断项目是否达到交付标准。'},
      { icon: Archive, title: '交付产物可审计', body: '交付清单、质量报告、运行验证和 release readiness 都会落盘，便于复盘、交接和审查。'},
    ],
  },
  en: {
    eyebrow: 'Proof / Trust',
    title: 'Visible trust signals.',
    body: 'Open source, published packages, host coverage, local knowledge, quality gates, and delivery artifacts all appear directly on the page.',
    items: [
      { icon: BadgeCheck, title: 'MIT open source and PyPI release', body: 'The code is visible, the install path is clear, and versions are traceable. This is not a black-box hosted platform.'},
      { icon: PackageCheck, title: 'Multi-host integration', body: 'The same governance model installs into CLI and IDE hosts without forcing the user onto a new coding tool.'},
      { icon: BookCopy, title: 'Local knowledge first', body: 'knowledge/ and knowledge bundles are reused in research, the three core docs, spec generation, quality, and delivery.'},
      { icon: ShieldCheck, title: 'UI Review and Release Readiness', body: 'The work is not done when code is generated. It must pass runtime validation, quality gates, and release checks.'},
      { icon: Archive, title: 'Auditable delivery artifacts', body: 'Delivery manifests, quality reports, runtime validation, and release readiness are written to disk.'},
    ],
  },
} as const;

export function TrustSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section className="section-glow border-b border-border-muted bg-bg-primary py-20 lg:py-24" aria-labelledby="trust-title">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="trust-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
          {copy.items.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded-2xl border border-border-default bg-bg-secondary/55 p-6">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-border-default bg-bg-primary text-accent-blue">
                  <Icon size={20} aria-hidden="true" />
                </div>
                <h3 className="mb-3 text-xl font-semibold text-text-primary">{item.title}</h3>
                <p className="text-sm leading-7 text-text-secondary">{item.body}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
