/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：页脚组件
 * 作用：四栏链接布局 + 版权信息
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import Link from 'next/link';
import { Github } from 'lucide-react';

const FOOTER_SECTIONS = [
  {
    title: '产品',
    links: [
      { label: '功能特性', href: '#features' },
      { label: '宿主兼容性', href: '#hosts' },
      { label: '定价', href: '/pricing' },
      { label: '更新日志', href: '/changelog' },
    ],
  },
  {
    title: '资源',
    links: [
      { label: '文档', href: 'https://github.com/shangyankeji/super-dev', external: true },
      { label: 'README', href: 'https://github.com/shangyankeji/super-dev#readme', external: true },
      { label: 'PyPI', href: 'https://pypi.org/project/super-dev/', external: true },
    ],
  },
  {
    title: '项目',
    links: [
      { label: 'GitHub', href: 'https://github.com/shangyankeji/super-dev', external: true },
      { label: 'Issues', href: 'https://github.com/shangyankeji/super-dev/issues', external: true },
      { label: 'MIT 许可证', href: 'https://github.com/shangyankeji/super-dev/blob/main/LICENSE', external: true },
    ],
  },
  {
    title: '联系',
    links: [
      { label: '贡献指南', href: 'https://github.com/shangyankeji/super-dev/blob/main/CONTRIBUTING.md', external: true },
      { label: 'shangyankeji', href: 'https://github.com/shangyankeji', external: true },
    ],
  },
] as const;

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-bg-primary border-t border-border-muted" role="contentinfo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12 lg:py-16">
        {/* 主区域 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 lg:gap-12">
          {/* 品牌列 */}
          <div className="col-span-2 md:col-span-1">
            <Link
              href="/"
              className="flex items-center gap-2 mb-3 group w-fit"
              aria-label="Super Dev 首页"
            >
              <span
                className="w-2.5 h-6 bg-accent-blue rounded-sm group-hover:bg-accent-blue-hover transition-colors duration-150"
                aria-hidden="true"
              />
              <span className="font-mono font-bold text-text-primary text-base">super-dev</span>
            </Link>
            <p className="text-sm text-text-muted leading-relaxed max-w-[200px]">
              AI 编码工具的流程治理层
            </p>
            <a
              href="https://github.com/shangyankeji/super-dev"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 mt-4 text-sm text-text-muted hover:text-text-secondary transition-colors"
              aria-label="在 GitHub 查看源代码"
            >
              <Github size={14} aria-hidden="true" />
              MIT 开源
            </a>
          </div>

          {/* 链接列 */}
          {FOOTER_SECTIONS.map((section) => (
            <div key={section.title}>
              <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
                {section.title}
              </h3>
              <ul className="space-y-3" role="list">
                {section.links.map((link) => (
                  <li key={link.label}>
                    {'external' in link ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-text-secondary hover:text-text-primary transition-colors duration-150"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <Link
                        href={link.href}
                        className="text-sm text-text-secondary hover:text-text-primary transition-colors duration-150"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* 底部版权 */}
        <div className="mt-12 pt-6 border-t border-border-muted flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-text-muted">
            &copy; {currentYear} shangyankeji. MIT License.
          </p>
          <p className="text-xs text-text-muted">
            Built with{' '}
            <a
              href="https://github.com/shangyankeji/super-dev"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-blue hover:text-accent-blue-hover transition-colors"
            >
              super-dev
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
