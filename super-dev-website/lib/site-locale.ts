export type SiteLocale = 'zh' | 'en';

export const SITE_BASE_PATH = process.env.NODE_ENV === 'production' ? '/super-dev' : '';
export const SITE_URL = 'https://shangyankeji.github.io/super-dev/';

export function assetPath(path: string): string {
  if (!path) return SITE_BASE_PATH || '/';
  if (/^https?:\/\//.test(path)) return path;
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${SITE_BASE_PATH}${normalized}`;
}

export function localizedPath(locale: SiteLocale, path: string): string {
  if (!path) return locale === 'en' ? '/en' : '/';
  if (/^https?:\/\//.test(path)) return path;
  if (path.startsWith('/en')) return path;
  if (locale === 'en') {
    return path === '/' ? '/en' : `/en${path}`;
  }
  return path;
}

export function detectLocaleFromPathname(pathname: string): SiteLocale {
  return pathname === '/en' || pathname.startsWith('/en/') ? 'en' : 'zh';
}

export function alternateLocalePath(pathname: string): string {
  if (pathname === '/en') return '/';
  if (pathname.startsWith('/en/')) return pathname.slice(3) || '/';
  if (pathname === '/') return '/en';
  return `/en${pathname}`;
}
