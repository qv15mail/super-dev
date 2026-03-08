/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：根布局组件
 * 作用：全局字体、元数据、主题提供
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import '@/styles/globals.css';

const siteUrl = 'https://shangyankeji.github.io/super-dev/';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
  display: 'swap',
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'Super Dev — AI 编码工具的流程治理层',
    template: '%s | Super Dev',
  },
  description:
    'Super Dev 是宿主内的 AI 开发治理层。它把 research、三文档、确认门、前端运行验证、质量门禁和交付标准接到你正在使用的 AI 宿主里。',
  keywords: [
    'AI 编程',
    'Claude Code',
    'Cursor',
    'Windsurf',
    'AI 开发流程',
    '代码质量门禁',
    '商业级交付',
    'super-dev',
  ],
  authors: [{ name: 'shangyankeji' }],
  openGraph: {
    type: 'website',
    locale: 'zh_CN',
    url: siteUrl,
    siteName: 'Super Dev',
    title: 'Super Dev — AI 编码工具的流程治理层',
    description: '宿主继续负责编码与执行，Super Dev 负责完整开发流程和交付门禁。',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Super Dev — AI 编码工具的流程治理层',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Super Dev — AI 编码工具的流程治理层',
    description: '宿主继续负责编码与执行，Super Dev 负责完整开发流程和交付门禁。',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-bg-primary text-text-primary antialiased">
        {children}
      </body>
    </html>
  );
}
