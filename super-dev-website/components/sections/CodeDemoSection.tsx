'use client';
/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：代码演示区组件
 * 作用：多 Tab 切换展示安装、触发和产物示例
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { useState } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { CODE_DEMO_TABS } from '@/lib/constants';
import { Download, Play, FileText } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const TAB_ICONS: LucideIcon[] = [Download, Play, FileText];

export function CodeDemoSection() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <section
      className="py-20 lg:py-28 bg-bg-primary"
      aria-labelledby="demo-title"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        {/* 标题区 */}
        <div className="text-center mb-14">
          <p className="text-sm font-mono text-accent-blue mb-3 tracking-wider uppercase">
            一行命令开始
          </p>
          <h2
            id="demo-title"
            className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight"
          >
            极简接入，零配置
          </h2>
          <p className="text-text-secondary max-w-2xl mx-auto">
            安装 super-dev，在你的 AI 工具中输入 /super-dev，
            完整的商业级开发流水线立即启动。
          </p>
        </div>

        {/* Tab 切换 + 代码块 */}
        <div className="max-w-3xl mx-auto">
          {/* Tab 列表 */}
          <div
            className="flex gap-1 p-1 bg-bg-secondary rounded-xl border border-border-default mb-4"
            role="tablist"
            aria-label="代码示例标签页"
          >
            {CODE_DEMO_TABS.map((tab, index) => {
              const Icon = TAB_ICONS[index];
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={activeTab === index}
                  aria-controls={`tab-panel-${tab.id}`}
                  id={`tab-${tab.id}`}
                  onClick={() => setActiveTab(index)}
                  className={cn(
                    'flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-150',
                    activeTab === index
                      ? 'bg-bg-primary text-text-primary shadow-sm'
                      : 'text-text-muted hover:text-text-secondary'
                  )}
                >
                  <Icon size={14} aria-hidden="true" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* 代码内容 */}
          {CODE_DEMO_TABS.map((tab, index) => (
            <div
              key={tab.id}
              role="tabpanel"
              id={`tab-panel-${tab.id}`}
              aria-labelledby={`tab-${tab.id}`}
              hidden={activeTab !== index}
            >
              <CodeBlock
                code={tab.code}
                language={tab.language}
                filename={tab.filename}
              />
            </div>
          ))}
        </div>

        {/* 底部操作链接 */}
        <div className="flex flex-wrap justify-center gap-6 mt-8 text-sm text-text-muted">
          <Link
            href="/docs"
            className="hover:text-text-secondary transition-colors"
          >
            查看完整文档
          </Link>
          <span className="hidden sm:block text-border-default" aria-hidden="true">|</span>
          <a
            href="https://github.com/shangyankeji/super-dev"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-text-secondary transition-colors"
          >
            GitHub 仓库
          </a>
          <span className="hidden sm:block text-border-default" aria-hidden="true">|</span>
          <a
            href="https://pypi.org/project/super-dev/"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-text-secondary transition-colors"
          >
            PyPI 页面
          </a>
        </div>
      </div>
    </section>
  );
}
