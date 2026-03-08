/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：按钮组件
 * 作用：主 CTA、次要描边、最小化三种变体
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { cn } from '@/lib/utils';
import type { ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'ghost' | 'minimal';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'bg-accent-blue text-white hover:bg-accent-blue-hover active:scale-[0.98] shadow-sm',
  ghost:
    'bg-transparent text-text-primary border border-border-emphasis hover:bg-bg-tertiary active:scale-[0.98]',
  minimal:
    'bg-transparent text-text-secondary hover:text-text-primary',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-md',
  md: 'px-4 py-2 text-sm rounded-lg',
  lg: 'px-6 py-3 text-base rounded-lg',
};

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium',
        'transition-all duration-150',
        'focus-visible:outline-2 focus-visible:outline-accent-blue focus-visible:outline-offset-2',
        'disabled:opacity-40 disabled:cursor-not-allowed',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
