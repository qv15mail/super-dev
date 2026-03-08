'use client';
/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：命令复制组件
 * 作用：显示可一键复制的命令行，用于 Hero CTA
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CopyCommandProps {
  command: string;
  className?: string;
}

export function CopyCommand({ command, className }: CopyCommandProps) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(command).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {
      // 静默失败
    });
  }

  return (
    <button
      onClick={handleCopy}
      aria-label={copied ? '已复制命令' : '复制安装命令'}
      className={cn(
        'group flex items-center gap-3 px-4 py-3 rounded-lg',
        'bg-bg-secondary border border-border-default',
        'hover:border-border-emphasis transition-all duration-200',
        'text-left w-full sm:w-auto',
        className
      )}
    >
      <span className="text-text-muted font-mono text-sm select-none">$</span>
      <span className="font-mono text-sm text-text-primary flex-1">{command}</span>
      <span
        className={cn(
          'flex items-center gap-1 text-xs transition-colors duration-150',
          copied ? 'text-status-green' : 'text-text-muted group-hover:text-text-secondary'
        )}
      >
        {copied ? (
          <Check size={14} aria-hidden="true" />
        ) : (
          <Copy size={14} aria-hidden="true" />
        )}
      </span>
    </button>
  );
}
