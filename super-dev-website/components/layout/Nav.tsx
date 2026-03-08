'use client';
/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：顶部导航栏
 * 作用：固定导航、响应式汉堡菜单、GitHub Star 数显示、多语言切换
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Github, Menu, X, Star } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { LocaleSwitch } from '@/components/ui/LocaleSwitch';
import { formatStarCount, GITHUB_REPO_URL } from '@/lib/github';
import { useGithubStars } from '@/lib/useGithubStars';
import { localizedPath, type SiteLocale } from '@/lib/site-locale';

interface NavProps {
  locale?: SiteLocale;
}

const COPY = {
  zh: {
    nav: [
      { label: '功能', href: '/#features' },
      { label: '宿主', href: '/#hosts' },
      { label: '文档', href: '/docs' },
    ],
    start: '开始使用',
    mobileOpen: '打开菜单',
    mobileClose: '关闭菜单',
    ariaHome: 'Super Dev 首页',
    ariaNav: '主导航',
    github: 'GitHub',
  },
  en: {
    nav: [
      { label: 'Features', href: '/#features' },
      { label: 'Hosts', href: '/#hosts' },
      { label: 'Docs', href: '/docs' },
    ],
    start: 'Get Started',
    mobileOpen: 'Open menu',
    mobileClose: 'Close menu',
    ariaHome: 'Super Dev home',
    ariaNav: 'Main navigation',
    github: 'GitHub',
  },
} as const;

export function Nav({ locale = 'zh' }: NavProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const stars = useGithubStars();
  const copy = COPY[locale];
  const navLinks = copy.nav.map((link) => ({ ...link, href: localizedPath(locale, link.href) }));

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 20);
    }
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  function handleMobileClose() {
    setMobileOpen(false);
  }

  function handleGetStarted() {
    const homePath = localizedPath(locale, '/');
    if (pathname === homePath || pathname === `${homePath}/`) {
      document.getElementById('get-started')?.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    router.push(localizedPath(locale, '/#get-started'));
  }

  return (
    <>
      <header
        className={cn(
          'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
          scrolled
            ? 'backdrop-blur-md bg-bg-primary/80 border-b border-border-muted'
            : 'bg-transparent'
        )}
      >
        <nav
          className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14"
          aria-label={copy.ariaNav}
        >
          <Link
            href={localizedPath(locale, '/')}
            className="flex items-center gap-2.5 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue rounded-md"
            aria-label={copy.ariaHome}
          >
            <span
              className="w-2.5 h-6 bg-accent-blue rounded-sm group-hover:bg-accent-blue-hover transition-colors duration-150"
              aria-hidden="true"
            />
            <span className="font-mono font-bold text-text-primary text-base tracking-tight">
              super-dev
            </span>
          </Link>

          <ul className="hidden md:flex items-center gap-1" role="list">
            {navLinks.map((link) => (
              <li key={link.label}>
                <Link
                  href={link.href}
                  className="px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary transition-colors duration-150 rounded-md"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>

          <div className="hidden md:flex items-center gap-3">
            <LocaleSwitch />
            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm',
                'border border-border-default text-text-secondary',
                'hover:border-border-emphasis hover:text-text-primary',
                'transition-all duration-150'
              )}
              aria-label={`GitHub repository, ${stars} stars`}
            >
              <Github size={14} aria-hidden="true" />
              <Star size={12} aria-hidden="true" />
              <span className="font-mono">{formatStarCount(stars)}</span>
            </a>
            <Button variant="primary" size="sm" onClick={handleGetStarted}>
              {copy.start}
            </Button>
          </div>

          <button
            className="md:hidden p-2 text-text-secondary hover:text-text-primary transition-colors rounded-md"
            onClick={() => setMobileOpen((prev) => !prev)}
            aria-expanded={mobileOpen}
            aria-controls="mobile-menu"
            aria-label={mobileOpen ? copy.mobileClose : copy.mobileOpen}
          >
            {mobileOpen ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
          </button>
        </nav>
      </header>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-bg-primary/95 backdrop-blur-sm pt-14"
          id="mobile-menu"
          role="dialog"
          aria-label={copy.ariaNav}
        >
          <nav className="flex flex-col p-6 gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                onClick={handleMobileClose}
                className="py-3 px-4 text-lg text-text-secondary hover:text-text-primary rounded-lg hover:bg-bg-secondary transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <div className="mt-4 pt-4 border-t border-border-muted flex flex-col gap-3">
              <LocaleSwitch className="justify-center" />
              <a
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 py-3 px-4 text-text-secondary hover:text-text-primary"
              >
                <Github size={16} aria-hidden="true" />
                {copy.github} (★{formatStarCount(stars)})
              </a>
              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={() => {
                  handleMobileClose();
                  handleGetStarted();
                }}
              >
                {copy.start}
              </Button>
            </div>
          </nav>
        </div>
      )}
    </>
  );
}
