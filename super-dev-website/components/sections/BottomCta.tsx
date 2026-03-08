/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：底部 CTA 组件
 * 作用：最终转化区，大号标题 + 安装命令 + GitHub 链接
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { Github } from 'lucide-react';
import { CopyCommand } from '@/components/ui/CopyCommand';

export function BottomCta() {
  return (
    <section
      className="relative py-24 lg:py-32 bg-bg-secondary overflow-hidden"
      aria-labelledby="bottom-cta-title"
    >
      {/* 背景光晕 */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-accent-blue/8 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-3xl mx-auto px-4 sm:px-6 text-center">
        {/* 标题 */}
        <h2
          id="bottom-cta-title"
          className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary mb-4 tracking-tight"
        >
          立即开始
        </h2>
        <p className="text-lg text-text-secondary mb-10 max-w-xl mx-auto">
          让 AI 产出达到商业级标准。一行命令，接入你现有的工具链。
        </p>

        {/* 安装命令 */}
        <div className="flex justify-center mb-6">
          <CopyCommand command="pip install super-dev" className="sm:w-auto" />
        </div>

        {/* 或 uv */}
        <p className="text-sm text-text-muted mb-10">
          或使用{' '}
          <code className="font-mono text-text-secondary bg-bg-tertiary px-1.5 py-0.5 rounded">
            uv tool install super-dev
          </code>
        </p>

        {/* GitHub 链接 */}
        <a
          href="https://github.com/shangyankeji/super-dev"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors duration-150"
        >
          <Github size={16} aria-hidden="true" />
          <span>在 GitHub 查看源代码</span>
        </a>
      </div>
    </section>
  );
}
