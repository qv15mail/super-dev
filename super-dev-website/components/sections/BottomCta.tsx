import { Github } from 'lucide-react';
import { CopyCommand } from '@/components/ui/CopyCommand';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    title: '先接入宿主，再开始按流程开发。',
    body: '安装 Super Dev，运行 super-dev 完成宿主接入，然后在宿主里输入 /super-dev 或 super-dev:。从 research 到交付的关键门禁会接管后续流程。',
    installNote: '也可以使用',
    github: '在 GitHub 查看源代码',
  },
  en: {
    title: 'Connect the host first, then build through the governed flow.',
    body: 'Install Super Dev, run super-dev to onboard the host, then trigger /super-dev or super-dev: inside the host. The workflow gates take over from research through delivery.',
    installNote: 'You can also use',
    github: 'View source on GitHub',
  },
} as const;

export function BottomCta({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section className="relative overflow-hidden bg-bg-primary py-24 lg:py-28" aria-labelledby="bottom-cta-title">
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute left-1/2 top-1/2 h-[360px] w-[720px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-blue/6 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <h2 id="bottom-cta-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl lg:text-5xl">{copy.title}</h2>
        <p className="mx-auto mt-5 max-w-3xl text-lg leading-8 text-text-secondary">{copy.body}</p>

        <div className="mt-10 flex justify-center">
          <CopyCommand command="pip install -U super-dev" className="sm:w-auto" />
        </div>

        <p className="mt-4 text-sm text-text-muted">
          {copy.installNote}{' '}
          <code className="rounded bg-bg-secondary px-1.5 py-0.5 font-mono text-text-secondary">uv tool install super-dev</code>
        </p>

        <a
          href="https://github.com/shangyankeji/super-dev"
          target="_blank"
          rel="noopener noreferrer"
          className="mt-8 inline-flex items-center gap-2 text-text-secondary transition-colors duration-150 hover:text-text-primary"
        >
          <Github size={16} aria-hidden="true" />
          <span>{copy.github}</span>
        </a>
      </div>
    </section>
  );
}
