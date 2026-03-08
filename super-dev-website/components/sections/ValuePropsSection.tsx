import { GitBranch, ShieldCheck, FileCheck } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { SiteLocale } from '@/lib/site-locale';

interface ValueProp {
  Icon: LucideIcon;
  title: string;
  titleEn: string;
  description: string;
  tags: string[];
}

const VALUE_PROPS: Record<SiteLocale, ValueProp[]> = {
  zh: [
    {
      Icon: GitBranch,
      title: '流程治理',
      titleEn: 'Pipeline Governance',
      description: '从研究到交付，每个阶段都有规范。研究 → 三文档 → 用户确认 → Spec → 实现 → 门禁 → 归档，不跳步，不走捷径。',
      tags: ['研究阶段', '需求文档', '编码实现', '交付归档'],
    },
    {
      Icon: ShieldCheck,
      title: '商业级门禁',
      titleEn: 'Commercial-Grade Quality Gates',
      description: '红队审查（安全 / 性能 / 架构三维度）+ 策略阈值双重校验 + 发布演练与回滚预案，让 AI 代码真正满足商业交付标准。',
      tags: ['红队审查', '策略阈值', '发布演练', '回滚预案'],
    },
    {
      Icon: FileCheck,
      title: '可审计交付',
      titleEn: 'Auditable Delivery',
      description: '每个阶段都产出证据。Pipeline 契约、交付清单、指标报告——AI 写的代码完整可溯源、可复盘、可合规审查。',
      tags: ['Pipeline 契约', '交付清单', '指标报告', '全流程可溯源'],
    },
  ],
  en: [
    {
      Icon: GitBranch,
      title: 'Pipeline Governance',
      titleEn: 'Pipeline Governance',
      description: 'Every stage is governed. Research → documents → user confirmation → spec → implementation → gates → archive. No skipped steps and no silent shortcuts.',
      tags: ['Research', 'Documents', 'Implementation', 'Delivery archive'],
    },
    {
      Icon: ShieldCheck,
      title: 'Commercial Gates',
      titleEn: 'Commercial-Grade Quality Gates',
      description: 'Red-team review across security, performance, and architecture, plus policy thresholds and release rehearsal, so AI output reaches an actual shipping standard.',
      tags: ['Red team', 'Policy thresholds', 'Release rehearsal', 'Rollback plan'],
    },
    {
      Icon: FileCheck,
      title: 'Auditable Delivery',
      titleEn: 'Auditable Delivery',
      description: 'Every stage produces evidence. Pipeline contract, delivery manifest, and metrics make AI output traceable, reviewable, and suitable for compliance review.',
      tags: ['Pipeline contract', 'Delivery manifest', 'Metrics', 'Traceability'],
    },
  ],
};

const SECTION_COPY = {
  zh: {
    eyebrow: '为什么选择 Super Dev',
    title: '三大核心能力',
    body: '你已经有最好的 AI 模型。Super Dev 确保它们的产出达到商业交付标准。',
  },
  en: {
    eyebrow: 'Why Super Dev',
    title: 'Three Core Capabilities',
    body: 'You already have strong AI models. Super Dev makes sure their output reaches a commercial delivery standard.',
  },
} as const;

export function ValuePropsSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = SECTION_COPY[locale];
  return (
    <section id="features" className="py-20 lg:py-28 bg-bg-primary" aria-labelledby="features-title">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-14">
          <p className="text-sm font-mono text-accent-blue mb-3 tracking-wider uppercase">{copy.eyebrow}</p>
          <h2 id="features-title" className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight">{copy.title}</h2>
          <p className="text-text-secondary max-w-2xl mx-auto text-lg">{copy.body}</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {VALUE_PROPS[locale].map(({ Icon, title, titleEn, description, tags }) => (
            <article key={title} className="group p-6 rounded-xl bg-bg-secondary border border-border-default hover:border-accent-blue/40 transition-all duration-200 hover:-translate-y-0.5">
              <div className="w-10 h-10 rounded-lg bg-accent-blue/10 flex items-center justify-center mb-4">
                <Icon size={20} className="text-accent-blue" aria-hidden="true" />
              </div>
              <h3 className="text-lg font-semibold text-text-primary mb-1">{title}</h3>
              <p className="text-xs font-mono text-text-muted mb-3">{titleEn}</p>
              <p className="text-sm text-text-secondary leading-relaxed mb-5">{description}</p>
              <div className="flex flex-wrap gap-1.5">
                {tags.map((tag) => (
                  <span key={tag} className="text-xs px-2 py-0.5 rounded-md bg-bg-tertiary text-text-muted border border-border-muted">{tag}</span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
