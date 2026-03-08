'use client';
/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：Hero 主视觉区组件
 * 作用：品牌标题、核心价值主张、CTA 按钮组、终端演示
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { ArrowRight, Github } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { CopyCommand } from '@/components/ui/CopyCommand';
import { formatStarCount, GITHUB_REPO_URL } from '@/lib/github';
import { useGithubStars } from '@/lib/useGithubStars';

const TerminalWindow = dynamic(
  () => import('@/components/ui/TerminalWindow').then((mod) => mod.TerminalWindow),
  { ssr: false }
);

export function HeroSection() {
  const stars = useGithubStars();

  return (
    <section
      className="relative min-h-screen flex items-center pt-14 overflow-hidden"
      aria-labelledby="hero-title"
    >
      {/* 背景：中心径向渐变光晕 */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
      >
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-accent-blue/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border-default to-transparent" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-20 lg:py-28 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* 左侧：文案区 */}
          <div className="flex flex-col gap-6">
            {/* 版本徽章 */}
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="version">v2.0.8</Badge>
              <span className="text-text-muted text-sm">·</span>
              <Badge variant="certified">MIT 开源</Badge>
              <span className="text-text-muted text-sm">·</span>
              <a
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-sm text-text-muted hover:text-text-secondary transition-colors"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                {formatStarCount(stars)} Stars
              </a>
            </div>

            {/* 主标题 */}
            <h1
              id="hero-title"
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-text-primary leading-[1.1] tracking-tight"
            >
              AI 能写代码，
              <br />
              <span className="text-gradient-blue">Super Dev</span>{' '}
              让代码能交付。
            </h1>

            {/* 副标题 */}
            <p className="text-lg text-text-secondary leading-relaxed max-w-xl">
              AI 编码工具的流程治理层。12 阶段流水线、商业级质量门禁、可审计交付产物——
              兼容你正在使用的任意 AI 工具。
            </p>

            {/* CTA 区域 */}
            <div id="get-started" className="flex flex-col sm:flex-row gap-3 pt-2">
              <CopyCommand command="pip install super-dev" className="sm:w-auto" />
              <Link
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-medium text-text-secondary border border-border-default hover:border-border-emphasis hover:text-text-primary transition-all duration-150"
              >
                <Github size={16} aria-hidden="true" />
                查看文档
                <ArrowRight size={14} aria-hidden="true" />
              </Link>
            </div>

            {/* 小字说明 */}
            <p className="text-xs text-text-muted">
              支持 Python 3.10+，或使用{' '}
              <code className="font-mono text-text-secondary bg-bg-secondary px-1.5 py-0.5 rounded">
                uv tool install super-dev
              </code>
            </p>
          </div>

          {/* 右侧：终端演示 */}
          <div className="relative">
            <TerminalWindow className="w-full" />
            {/* 装饰：右下角光晕 */}
            <div
              className="absolute -bottom-8 -right-8 w-48 h-48 bg-accent-blue/10 rounded-full blur-2xl pointer-events-none"
              aria-hidden="true"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
