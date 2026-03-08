import { Github } from 'lucide-react';
import { CopyCommand } from '@/components/ui/CopyCommand';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    title: '立即开始',
    body: '让 AI 产出达到商业级标准。一行命令，接入你现有的工具链。',
    installNote: '或使用',
    github: '在 GitHub 查看源代码',
  },
  en: {
    title: 'Start Now',
    body: 'Raise AI output to a commercial-grade standard. One command connects it to the toolchain you already use.',
    installNote: 'Or use',
    github: 'View source on GitHub',
  },
} as const;

export function BottomCta({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <section className="relative py-24 lg:py-32 bg-bg-secondary overflow-hidden" aria-labelledby="bottom-cta-title">
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-accent-blue/8 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-3xl mx-auto px-4 sm:px-6 text-center">
        <h2 id="bottom-cta-title" className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary mb-4 tracking-tight">{copy.title}</h2>
        <p className="text-lg text-text-secondary mb-10 max-w-xl mx-auto">{copy.body}</p>

        <div className="flex justify-center mb-6">
          <CopyCommand command="pip install super-dev" className="sm:w-auto" />
        </div>

        <p className="text-sm text-text-muted mb-10">
          {copy.installNote}{' '}
          <code className="font-mono text-text-secondary bg-bg-tertiary px-1.5 py-0.5 rounded">uv tool install super-dev</code>
        </p>

        <a
          href="https://github.com/shangyankeji/super-dev"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors duration-150"
        >
          <Github size={16} aria-hidden="true" />
          <span>{copy.github}</span>
        </a>
      </div>
    </section>
  );
}
