export type SiteLocale = 'zh' | 'en';

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
