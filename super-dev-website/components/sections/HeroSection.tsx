'use client';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { ArrowRight, BookOpen } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { CopyCommand } from '@/components/ui/CopyCommand';
import { formatStarCount, GITHUB_REPO_URL } from '@/lib/github';
import { useGithubStars } from '@/lib/useGithubStars';
import { localizedPath, type SiteLocale } from '@/lib/site-locale';

const TerminalWindow = dynamic(
  () => import('@/components/ui/TerminalWindow').then((mod) => mod.TerminalWindow),
  { ssr: false }
);

const COPY = {
  zh: {
    openSource: 'MIT 开源',
    title: 'AI 能写代码，Super Dev 让项目能交付。',
    body: '辅助用户在 Claude Code、Cursor、Codex、Trae 等开发工具中，更标准地完成商业交付。接手项目时先看代码库地图、范围覆盖率、依赖图和改动影响范围，再按 research、三文档、确认门、Spec、前端验证、质量门禁和交付标准推进。',
    points: ['适配主流 CLI 与 IDE 宿主', '代码库理解、范围覆盖审计、影响分析与回归守卫一体化', '支持随时回到 docs、frontend、backend、quality 等阶段继续推进'],
    docs: '查看文档',
    installNote: '支持 pip 或 uv 安装，安装后终端输入 super-dev 进入宿主接入引导。',
  },
  en: {
    openSource: 'MIT Open Source',
    title: 'AI can write code. Super Dev helps teams ship it properly.',
    body: 'Use Super Dev inside Claude Code, Cursor, Codex, Trae, and similar tools to move from requirement to delivery through one governed path: repo map, scope coverage, dependency graph, impact analysis, research, the three core docs, approval, spec, frontend validation, quality gates, and delivery standards.',
    points: ['Works across major CLI and IDE hosts', 'Combines codebase intelligence, scope audit, impact analysis, and regression guard', 'Can return to docs, frontend, backend, and quality phases without restarting from zero'],
    docs: 'Read Docs',
    installNote: 'Install with pip or uv, then run super-dev in the terminal to open the host onboarding flow.',
  },
} as const;

export function HeroSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const stars = useGithubStars();
  const copy = COPY[locale];

  return (
    <section className="relative overflow-hidden border-b border-border-muted bg-bg-primary pt-24 lg:pt-28" aria-labelledby="hero-title">
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute left-1/2 top-0 h-[460px] w-[780px] -translate-x-1/2 rounded-full bg-accent-blue/6 blur-3xl" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border-default to-transparent" />
      </div>

      <div className="relative mx-auto flex w-full max-w-7xl flex-col gap-14 px-4 pb-20 sm:px-6 lg:grid lg:grid-cols-[minmax(0,1fr)_520px] lg:items-center lg:gap-16 lg:pb-24">
        <div className="flex flex-col gap-7">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="version">v2.1.1</Badge>
            <Badge variant="certified">{copy.openSource}</Badge>
            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-text-muted transition-colors hover:text-text-secondary"
            >
              {formatStarCount(stars)} Stars
            </a>
          </div>

          <h1 id="hero-title" className="max-w-3xl text-4xl font-bold leading-[1.06] tracking-tight text-text-primary sm:text-5xl lg:text-6xl">
            {locale === 'zh' ? (
              <>
                AI 能写代码，
                <span className="text-gradient-brand">Super Dev</span>
                让项目能交付。
              </>
            ) : (
              <>
                AI can write code. <span className="text-gradient-brand">Super Dev</span> helps teams ship it properly.
              </>
            )}
          </h1>

          <p className="max-w-2xl text-lg leading-8 text-text-secondary">{copy.body}</p>

          <ul className="grid gap-3 text-sm text-text-secondary sm:grid-cols-3">
            {copy.points.map((point) => (
              <li key={point} className="rounded-xl border border-border-default bg-bg-secondary/55 px-4 py-3 leading-6">
                {point}
              </li>
            ))}
          </ul>

          <div id="get-started" className="flex flex-col gap-3 pt-1 sm:flex-row sm:flex-wrap sm:items-center">
            <CopyCommand command="pip install -U super-dev" className="sm:w-auto" />
            <Link
              href={localizedPath(locale, '/docs')}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-border-default px-4 py-3 text-sm font-medium text-text-secondary transition-all duration-150 hover:border-border-emphasis hover:text-text-primary"
            >
              <BookOpen size={16} aria-hidden="true" />
              {copy.docs}
              <ArrowRight size={14} aria-hidden="true" />
            </Link>
          </div>

          <p className="text-sm text-text-muted">{copy.installNote}</p>
        </div>

        <div className="relative">
          <TerminalWindow className="w-full" locale={locale} />
          <div className="pointer-events-none absolute -bottom-10 -right-8 h-48 w-48 rounded-full bg-accent-blue/10 blur-2xl" aria-hidden="true" />
        </div>
      </div>
    </section>
  );
}
