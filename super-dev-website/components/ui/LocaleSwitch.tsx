'use client';

import Link from 'next/link';
import { Globe2 } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { alternateLocalePath, detectLocaleFromPathname } from '@/lib/site-locale';
import { cn } from '@/lib/utils';

interface LocaleSwitchProps {
  className?: string;
}

export function LocaleSwitch({ className }: LocaleSwitchProps) {
  const pathname = usePathname() || '/';
  const locale = detectLocaleFromPathname(pathname);
  const target = alternateLocalePath(pathname);

  return (
    <Link
      href={target}
      className={cn(
        'inline-flex items-center gap-2 rounded-lg border border-border-default px-3 py-1.5 text-sm text-text-secondary transition-all duration-150 hover:border-border-emphasis hover:text-text-primary',
        className
      )}
      aria-label={locale === 'zh' ? 'Switch to English' : '切换到中文'}
    >
      <Globe2 size={14} aria-hidden="true" />
      <span className="font-mono">{locale === 'zh' ? 'EN' : '中文'}</span>
    </Link>
  );
}
