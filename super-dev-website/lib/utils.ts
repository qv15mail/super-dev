/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：通用工具函数
 * 作用：类名合并等基础工具
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
