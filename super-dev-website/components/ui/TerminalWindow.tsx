'use client';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { TERMINAL_LINES } from '@/lib/constants';
import type { SiteLocale } from '@/lib/site-locale';

type LineType = 'input' | 'output' | 'success' | 'blank' | 'brand' | 'info' | 'certified';

function getLineStyle(type: string): string {
  const styles: Record<LineType, string> = {
    input: 'text-text-primary',
    output: 'text-text-secondary',
    success: 'text-status-green',
    blank: '',
    brand: 'text-accent-blue-hover font-medium',
    info: 'text-text-muted',
    certified: 'text-status-green',
  };
  return styles[type as LineType] ?? 'text-text-secondary';
}

function getLinePrefix(type: string): string {
  if (type === 'input') return '$ ';
  return '  ';
}

interface TerminalWindowProps {
  className?: string;
  locale?: SiteLocale;
}

export function TerminalWindow({ className, locale = 'zh' }: TerminalWindowProps) {
  const [visibleLines, setVisibleLines] = useState(0);
  const lines = TERMINAL_LINES[locale];

  useEffect(() => {
    setVisibleLines(0);
  }, [locale]);

  useEffect(() => {
    if (visibleLines >= lines.length) return;
    const delay = lines[visibleLines].type === 'blank' ? 80 : 120;
    const timer = setTimeout(() => setVisibleLines((prev) => prev + 1), delay);
    return () => clearTimeout(timer);
  }, [visibleLines, lines]);

  return (
    <div
      className={cn(
        'rounded-xl border border-border-default bg-[#0D1117] overflow-hidden',
        'shadow-2xl shadow-black/50',
        className
      )}
    >
      <div className="flex items-center gap-2 px-4 py-3 bg-bg-secondary border-b border-border-default">
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#FF5F56]" aria-hidden="true" />
          <span className="w-3 h-3 rounded-full bg-[#FFBD2E]" aria-hidden="true" />
          <span className="w-3 h-3 rounded-full bg-[#27C93F]" aria-hidden="true" />
        </div>
        <span className="text-xs text-text-muted font-mono ml-2">Terminal</span>
      </div>

      <div className="p-5 font-mono text-sm leading-relaxed min-h-[320px]">
        {lines.slice(0, visibleLines).map((line, index) => (
          <div key={index} className={cn('whitespace-pre', getLineStyle(line.type))}>
            {line.type === 'blank' ? (
              <span>&nbsp;</span>
            ) : (
              <>
                <span className="text-text-muted">{getLinePrefix(line.type)}</span>
                {line.text}
              </>
            )}
          </div>
        ))}
        {visibleLines < lines.length && (
          <span className="inline-block w-2 h-4 bg-text-primary animate-blink" aria-hidden="true" />
        )}
      </div>
    </div>
  );
}
