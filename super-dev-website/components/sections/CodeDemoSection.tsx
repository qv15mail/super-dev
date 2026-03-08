'use client';
import { useState } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { Download, Play, FileText } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { localizedPath, type SiteLocale } from '@/lib/site-locale';

const TAB_ICONS: LucideIcon[] = [Download, Play, FileText];

const TABS = {
  zh: [
    { id: 'install', label: '安装', filename: 'Terminal', code: `# 安装 super-dev\npip install super-dev\n\n# 或使用 uv（推荐）\nuv tool install super-dev\n\n# 检查版本\nsuper-dev --version\n# super-dev 2.0.8` },
    { id: 'trigger', label: '触发流水线', filename: 'Claude Code / Cursor / Windsurf', code: `# 在任意支持的 AI 宿主中输入：\n/super-dev 开发一个用户管理系统，包含注册登录、权限控制\n\n# 非 slash 宿主则输入：\nsuper-dev: 开发一个用户管理系统，包含注册登录、权限控制\n\n# Super Dev 将自动启动完整流水线` },
    { id: 'contract', label: '交付产物', filename: '.super-dev/pipeline-contract.yaml', code: `version: "2.0.8"\npipeline_id: "user-mgmt-20260308-001"\nstatus: completed\n\nphases:\n  - id: 9\n    name: quality-gate\n    status: passed\n\ndelivery:\n  manifest: ".super-dev/delivery/manifest.json"\n  archive: ".super-dev/delivery/archive-20260308.tar.gz"` },
  ],
  en: [
    { id: 'install', label: 'Install', filename: 'Terminal', code: `# Install super-dev\npip install super-dev\n\n# Or use uv (recommended)\nuv tool install super-dev\n\n# Check version\nsuper-dev --version\n# super-dev 2.0.8` },
    { id: 'trigger', label: 'Trigger', filename: 'Claude Code / Cursor / Windsurf', code: `# In any supported AI host, enter:\n/super-dev Build a user management system with auth and roles\n\n# For non-slash hosts, enter:\nsuper-dev: Build a user management system with auth and roles\n\n# Super Dev will start the full governed pipeline` },
    { id: 'contract', label: 'Artifacts', filename: '.super-dev/pipeline-contract.yaml', code: `version: "2.0.8"\npipeline_id: "user-mgmt-20260308-001"\nstatus: completed\n\nphases:\n  - id: 9\n    name: quality-gate\n    status: passed\n\ndelivery:\n  manifest: ".super-dev/delivery/manifest.json"\n  archive: ".super-dev/delivery/archive-20260308.tar.gz"` },
  ],
} as const;

const COPY = {
  zh: { eyebrow: '一行命令开始', title: '极简接入，零配置', body: '安装 super-dev，在你的 AI 工具中输入 /super-dev，完整的商业级开发流水线立即启动。', docs: '查看完整文档', github: 'GitHub 仓库', pypi: 'PyPI 页面' },
  en: { eyebrow: 'Start in one command', title: 'Minimal setup, zero ceremony', body: 'Install super-dev, trigger it inside your AI host, and the commercial-grade delivery pipeline starts immediately.', docs: 'Read full docs', github: 'GitHub repository', pypi: 'PyPI package' },
} as const;

export function CodeDemoSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const [activeTab, setActiveTab] = useState(0);
  const tabs = TABS[locale];
  const copy = COPY[locale];
  return (
    <section className="py-20 lg:py-28 bg-bg-primary" aria-labelledby="demo-title">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-14">
          <p className="text-sm font-mono text-accent-blue mb-3 tracking-wider uppercase">{copy.eyebrow}</p>
          <h2 id="demo-title" className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight">{copy.title}</h2>
          <p className="text-text-secondary max-w-2xl mx-auto">{copy.body}</p>
        </div>

        <div className="max-w-3xl mx-auto">
          <div className="flex gap-1 p-1 bg-bg-secondary rounded-xl border border-border-default mb-4" role="tablist" aria-label="Code demo tabs">
            {tabs.map((tab, index) => {
              const Icon = TAB_ICONS[index];
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={activeTab === index}
                  aria-controls={`tab-panel-${tab.id}`}
                  id={`tab-${tab.id}`}
                  onClick={() => setActiveTab(index)}
                  className={cn('flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-150', activeTab === index ? 'bg-bg-primary text-text-primary shadow-sm' : 'text-text-muted hover:text-text-secondary')}
                >
                  <Icon size={14} aria-hidden="true" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {tabs.map((tab, index) => (
            <div key={tab.id} role="tabpanel" id={`tab-panel-${tab.id}`} aria-labelledby={`tab-${tab.id}`} hidden={activeTab !== index}>
              <CodeBlock code={tab.code} filename={tab.filename} />
            </div>
          ))}
        </div>

        <div className="flex flex-wrap justify-center gap-6 mt-8 text-sm text-text-muted">
          <Link href={localizedPath(locale, '/docs')} className="hover:text-text-secondary transition-colors">{copy.docs}</Link>
          <span className="hidden sm:block text-border-default" aria-hidden="true">|</span>
          <a href="https://github.com/shangyankeji/super-dev" target="_blank" rel="noopener noreferrer" className="hover:text-text-secondary transition-colors">{copy.github}</a>
          <span className="hidden sm:block text-border-default" aria-hidden="true">|</span>
          <a href="https://pypi.org/project/super-dev/" target="_blank" rel="noopener noreferrer" className="hover:text-text-secondary transition-colors">{copy.pypi}</a>
        </div>
      </div>
    </section>
  );
}
