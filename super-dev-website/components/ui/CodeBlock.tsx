'use client';
/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：代码块组件
 * 作用：展示带语法高亮的代码，支持一键复制
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CodeBlockProps {
  code: string;
  language?: string;
  filename?: string;
  className?: string;
}

export function CodeBlock({ code, filename, className }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {
      // clipboard API 不可用时静默失败
    });
  }

  return (
    <div
      className={cn(
        'rounded-xl border border-border-default bg-bg-elevated overflow-hidden',
        className
      )}
    >
      {/* 文件名标题栏 */}
      {filename && (
        <div className="flex items-center justify-between px-4 py-2.5 bg-bg-secondary border-b border-border-default">
          <span className="text-xs text-text-muted font-mono">{filename}</span>
          <button
            onClick={handleCopy}
            aria-label={copied ? '已复制' : '复制代码'}
            className={cn(
              'flex items-center gap-1.5 text-xs px-2 py-1 rounded-md transition-all duration-150',
              'hover:bg-bg-tertiary',
              copied ? 'text-status-green' : 'text-text-muted hover:text-text-secondary'
            )}
          >
            {copied ? (
              <Check size={12} aria-hidden="true" />
            ) : (
              <Copy size={12} aria-hidden="true" />
            )}
            {copied ? '已复制' : '复制'}
          </button>
        </div>
      )}

      {/* 代码内容 */}
      <div className="overflow-x-auto">
        <pre className="p-5 text-sm font-mono leading-relaxed text-text-secondary">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
}
