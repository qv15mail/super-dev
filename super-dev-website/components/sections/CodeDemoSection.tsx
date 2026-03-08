'use client';
import { useState } from 'react';
import { ArrowRight, Download, FileText, Play } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import Link from 'next/link';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { cn } from '@/lib/utils';
import { localizedPath, type SiteLocale } from '@/lib/site-locale';

const TAB_ICONS: LucideIcon[] = [Download, Play, FileText];

const TABS = {
  zh: [
    {
      id: 'install',
      label: '安装与引导',
      filename: 'Terminal',
      code: `pip install -U super-dev
# 或
uv tool install super-dev

# 进入宿主安装引导
super-dev`,
    },
    {
      id: 'trigger',
      label: '触发宿主工作',
      filename: 'Host trigger',
      code: `# Slash 宿主
/super-dev 开发一个可交付的项目

# 非 slash 宿主
super-dev: 开发一个可交付的项目

# 宿主会先做 research，生成三文档，并等待确认。`,
    },
    {
      id: 'artifacts',
      label: '关键产物',
      filename: 'output/',
      code: `output/<project>-research.md
output/<project>-prd.md
output/<project>-architecture.md
output/<project>-uiux.md
.super-dev/changes/<change>/proposal.md
.super-dev/changes/<change>/tasks.md
output/<project>-frontend-runtime.json
output/<project>-quality-gate.md
output/delivery/manifest.json`,
    },
  ],
  en: [
    {
      id: 'install',
      label: 'Install and onboard',
      filename: 'Terminal',
      code: `pip install -U super-dev
# or
uv tool install super-dev

# open the host installer
super-dev`,
    },
    {
      id: 'trigger',
      label: 'Trigger the host',
      filename: 'Host trigger',
      code: `# Slash hosts
/super-dev Build a shippable product

# Non-slash hosts
super-dev: Build a shippable product

# The host should start with research, generate the three core docs, and wait for approval.`,
    },
    {
      id: 'artifacts',
      label: 'Key artifacts',
      filename: 'output/',
      code: `output/<project>-research.md
output/<project>-prd.md
output/<project>-architecture.md
output/<project>-uiux.md
.super-dev/changes/<change>/proposal.md
.super-dev/changes/<change>/tasks.md
output/<project>-frontend-runtime.json
output/<project>-quality-gate.md
output/delivery/manifest.json`,
    },
  ],
} as const;

const COPY = {
  zh: {
    eyebrow: 'How it works',
    title: '从安装到交付，入口始终很短。',
    body: '先安装并进入宿主引导，再在宿主里触发流程。后续的文档、门禁、运行验证和交付产物会沿着这条路径持续生成。',
    docs: '查看完整文档',
  },
  en: {
    eyebrow: 'How it works',
    title: 'From install to delivery, the entry path stays short.',
    body: 'Install and onboard first, then trigger the flow inside the host. The workflow keeps producing documents, gates, runtime validation, and delivery artifacts after that.',
    docs: 'Read full docs',
  },
} as const;

export function CodeDemoSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const [activeTab, setActiveTab] = useState(0);
  const tabs = TABS[locale];
  const copy = COPY[locale];

  return (
    <section className="border-b border-border-muted bg-bg-primary py-20 lg:py-24" aria-labelledby="workflow-demo-title">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mb-14 max-w-3xl">
          <p className="mb-3 text-sm font-mono uppercase tracking-wider text-accent-blue">{copy.eyebrow}</p>
          <h2 id="workflow-demo-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
        </div>

        <div className="rounded-2xl border border-border-default bg-bg-secondary/55 p-4 sm:p-6">
          <div className="mb-5 flex flex-wrap gap-2" role="tablist" aria-label="Workflow demo tabs">
            {tabs.map((tab, index) => {
              const Icon = TAB_ICONS[index];
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(index)}
                  className={cn(
                    'inline-flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors',
                    activeTab === index
                      ? 'border-accent-blue/40 bg-accent-blue/10 text-text-primary'
                      : 'border-border-default bg-bg-primary/70 text-text-secondary hover:text-text-primary'
                  )}
                  role="tab"
                  aria-selected={activeTab === index}
                >
                  <Icon size={15} aria-hidden="true" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <CodeBlock code={tabs[activeTab].code} filename={tabs[activeTab].filename} />
        </div>

        <div className="mt-8">
          <Link href={localizedPath(locale, '/docs')} className="inline-flex items-center gap-2 text-sm font-medium text-accent-blue transition-colors hover:text-accent-blue-hover">
            {copy.docs}
            <ArrowRight size={14} aria-hidden="true" />
          </Link>
        </div>
      </div>
    </section>
  );
}
