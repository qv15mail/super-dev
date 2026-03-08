import {
  Search, ListChecks, FileText, UserCheck, Code2,
  Monitor, Server, Link2, ShieldCheck, PlayCircle,
  Archive, CheckCircle2
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SiteLocale } from '@/lib/site-locale';

type PhaseType = 'normal' | 'gate-confirm' | 'gate-quality' | 'output';

const PHASE_ICONS: LucideIcon[] = [Search, ListChecks, FileText, UserCheck, Code2, Monitor, Server, Link2, ShieldCheck, PlayCircle, Archive, CheckCircle2];

const cardStyles: Record<PhaseType, string> = {
  normal: 'bg-bg-secondary border-border-default group-hover:border-accent-blue/50',
  'gate-confirm': 'bg-status-yellow/5 border-status-yellow/50',
  'gate-quality': 'bg-status-green/5 border-status-green/50',
  output: 'bg-accent-blue/5 border-accent-blue/40 group-hover:border-accent-blue/70',
};
const numberStyles: Record<PhaseType, string> = {
  normal: 'text-text-muted',
  'gate-confirm': 'text-status-yellow font-semibold',
  'gate-quality': 'text-status-green font-semibold',
  output: 'text-accent-blue',
};
const iconBgStyles: Record<PhaseType, string> = {
  normal: 'bg-bg-tertiary text-text-muted',
  'gate-confirm': 'bg-status-yellow/15 text-status-yellow',
  'gate-quality': 'bg-status-green/15 text-status-green',
  output: 'bg-accent-blue/15 text-accent-blue',
};

const PHASES = {
  zh: [
    { id: 1, name: '研究', nameEn: 'Research', desc: '同类产品研究，联网搜索对标产品、功能模式与差异化方向', type: 'normal' },
    { id: 2, name: '需求增强', nameEn: 'Requirements', desc: '分析原始需求，补全边界条件、边缘场景与验收标准', type: 'normal' },
    { id: 3, name: '三文档', nameEn: 'Documents', desc: '生成 PRD + 架构文档 + UI/UX 文档，建立完整设计基线', type: 'output' },
    { id: 4, name: '用户确认', nameEn: 'User Confirm', desc: '暂停流水线，等待用户确认三文档，未确认不得进入编码', type: 'gate-confirm' },
    { id: 5, name: 'Spec', nameEn: 'Spec', desc: '生成变更提案与任务清单，分解实现步骤', type: 'normal' },
    { id: 6, name: '前端实现', nameEn: 'Frontend', desc: '实现前端并运行验证，确保页面可演示、可审查', type: 'normal' },
    { id: 7, name: '后端实现', nameEn: 'Backend', desc: '实现后端逻辑、API 层与数据层', type: 'normal' },
    { id: 8, name: '联调', nameEn: 'Integration', desc: '前后端联调，端到端功能验证', type: 'normal' },
    { id: 9, name: '质量门禁', nameEn: 'Quality Gate', desc: '红队审查 + 策略阈值双重校验', type: 'gate-quality' },
    { id: 10, name: '发布演练', nameEn: 'Release Rehearsal', desc: '模拟生产环境发布，验证回滚预案', type: 'normal' },
    { id: 11, name: '交付归档', nameEn: 'Delivery Archive', desc: '生成交付清单、pipeline-contract、指标报告', type: 'output' },
    { id: 12, name: '完成', nameEn: 'Done', desc: '交付包就绪，可审计、可追溯、可复盘', type: 'normal' },
  ],
  en: [
    { id: 1, name: 'Research', nameEn: 'Research', desc: 'Study comparable products, interaction patterns, and positioning with the host web tools', type: 'normal' },
    { id: 2, name: 'Requirements', nameEn: 'Requirements', desc: 'Expand the raw request with boundaries, edge cases, and acceptance criteria', type: 'normal' },
    { id: 3, name: 'Docs', nameEn: 'Documents', desc: 'Generate PRD, Architecture, and UI/UX docs as the execution baseline', type: 'output' },
    { id: 4, name: 'Confirm', nameEn: 'User Confirm', desc: 'Pause for explicit user confirmation before any coding can continue', type: 'gate-confirm' },
    { id: 5, name: 'Spec', nameEn: 'Spec', desc: 'Create the proposal, task list, and implementation structure', type: 'normal' },
    { id: 6, name: 'Frontend', nameEn: 'Frontend', desc: 'Build the frontend first and verify that it runs and can be reviewed', type: 'normal' },
    { id: 7, name: 'Backend', nameEn: 'Backend', desc: 'Implement API, services, and data logic', type: 'normal' },
    { id: 8, name: 'Integration', nameEn: 'Integration', desc: 'Wire frontend and backend together and verify end-to-end behavior', type: 'normal' },
    { id: 9, name: 'Quality Gate', nameEn: 'Quality Gate', desc: 'Run UI review, red-team checks, and policy thresholds', type: 'gate-quality' },
    { id: 10, name: 'Rehearsal', nameEn: 'Release Rehearsal', desc: 'Simulate production release and validate rollback readiness', type: 'normal' },
    { id: 11, name: 'Delivery', nameEn: 'Delivery Archive', desc: 'Generate delivery manifest, pipeline contract, and audit outputs', type: 'output' },
    { id: 12, name: 'Done', nameEn: 'Done', desc: 'The package is ready to ship, audit, and review', type: 'normal' },
  ],
} as const;

const COPY = {
  zh: { eyebrow: '从想法到交付', title: '12 阶段开发流水线', body: '每个阶段都有输入、输出和证据。关键节点设有人工确认门和质量门禁，阻断不达标的产出。', continue: '继续', confirmGate: '确认门', qualityGate: '质量门' },
  en: { eyebrow: 'From idea to delivery', title: '12-stage delivery pipeline', body: 'Every stage has inputs, outputs, and evidence. Critical points are guarded by user confirmation and quality gates.', continue: 'Continue', confirmGate: 'Confirm Gate', qualityGate: 'Quality Gate' },
} as const;

function PhaseNode({ id, name, nameEn, desc, type, locale }: { id: number; name: string; nameEn: string; desc: string; type: PhaseType; locale: SiteLocale; }) {
  const Icon = PHASE_ICONS[id - 1];
  const copy = COPY[locale];
  return (
    <div className="group relative flex-1 min-w-0" title={desc}>
      {(type === 'gate-confirm' || type === 'gate-quality') && (
        <div className="absolute -top-5 left-1/2 -translate-x-1/2 whitespace-nowrap z-10">
          <span className={cn('text-[9px] font-bold px-2 py-0.5 rounded-full', type === 'gate-confirm' ? 'bg-status-yellow/15 text-status-yellow border border-status-yellow/40' : 'bg-status-green/15 text-status-green border border-status-green/40')}>
            {type === 'gate-confirm' ? copy.confirmGate : copy.qualityGate}
          </span>
        </div>
      )}
      <div className={cn('relative p-3 rounded-xl border transition-colors duration-200 cursor-default', 'flex flex-col items-center text-center gap-1.5', cardStyles[type])} role="listitem" aria-label={`阶段 ${id}：${name}。${desc}`}>
        <span className={cn('text-[10px] font-mono leading-none', numberStyles[type])}>{String(id).padStart(2, '0')}</span>
        <div className={cn('w-7 h-7 rounded-lg flex items-center justify-center', iconBgStyles[type])}><Icon size={14} aria-hidden="true" /></div>
        <p className="text-[11px] font-medium text-text-primary leading-tight">{name}</p>
        <p className="text-[9px] text-text-muted leading-tight hidden sm:block">{nameEn}</p>
      </div>
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 hidden group-hover:block z-20 pointer-events-none" role="tooltip">
        <div className="bg-bg-elevated border border-border-default rounded-lg px-3 py-2 text-xs text-text-secondary max-w-[180px] text-center shadow-2xl shadow-black/50 leading-relaxed">
          {desc}
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-border-default" aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}

function ArrowH() {
  return <div className="flex items-center self-center shrink-0 px-1" aria-hidden="true"><div className="w-3 sm:w-5 h-px bg-border-default" /><div className="w-0 h-0 border-t-[3px] border-b-[3px] border-l-[4px] border-t-transparent border-b-transparent border-l-border-default" /></div>;
}

export function PipelineSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const phases = PHASES[locale];
  const row1 = phases.slice(0, 6);
  const row2 = phases.slice(6, 12);
  const copy = COPY[locale];
  return (
    <section className="py-20 lg:py-28 bg-bg-primary" aria-labelledby="pipeline-title">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <p className="text-sm font-mono text-accent-blue mb-3 tracking-wider uppercase">{copy.eyebrow}</p>
          <h2 id="pipeline-title" className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight">{copy.title}</h2>
          <p className="text-text-secondary max-w-2xl mx-auto">{copy.body}</p>
        </div>

        <div className="hidden sm:block" role="list" aria-label={copy.title}>
          <div className="relative flex items-center mb-2 pt-6">
            {row1.map((phase, index) => (
              <div key={phase.id} className="flex items-center flex-1 min-w-0">
                <PhaseNode {...phase} locale={locale} />
                {index < row1.length - 1 && <ArrowH />}
              </div>
            ))}
            <div className="shrink-0 w-5 flex flex-col items-center self-stretch ml-1" aria-hidden="true"><div className="flex-1 w-px bg-border-default" /><div className="w-0 h-0 border-l-[3px] border-r-[3px] border-t-[4px] border-l-transparent border-r-transparent border-t-border-default mb-0.5" /></div>
          </div>
          <div className="flex justify-end pr-5 mb-2" aria-hidden="true"><div className="flex items-center gap-1.5 text-[9px] text-text-muted font-mono"><div className="w-0 h-0 border-t-[3px] border-b-[3px] border-r-[4px] border-t-transparent border-b-transparent border-r-border-default" /><div className="w-3 h-px bg-border-default" />{copy.continue}<div className="w-3 h-px bg-border-default" /></div></div>
          <div className="flex items-center pb-6"><div className="shrink-0 w-5 mr-1" aria-hidden="true" />{row2.map((phase, index) => (<div key={phase.id} className="flex items-center flex-1 min-w-0"><PhaseNode {...phase} locale={locale} />{index < row2.length - 1 && <ArrowH />}</div>))}</div>
        </div>

        <ol className="sm:hidden space-y-2" aria-label={copy.title}>
          {phases.map((phase) => {
            const Icon = PHASE_ICONS[phase.id - 1];
            return (
              <li key={phase.id} className={cn('flex items-start gap-3 p-3 rounded-xl border', cardStyles[phase.type])}>
                <div className="flex flex-col items-center gap-1 shrink-0">
                  <span className={cn('text-[10px] font-mono font-bold', numberStyles[phase.type])}>{String(phase.id).padStart(2, '0')}</span>
                  <div className={cn('w-7 h-7 rounded-lg flex items-center justify-center', iconBgStyles[phase.type])}><Icon size={14} aria-hidden="true" /></div>
                </div>
                <div className="min-w-0 pt-0.5">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="text-sm font-medium text-text-primary">{phase.name}</p>
                    {(phase.type === 'gate-confirm' || phase.type === 'gate-quality') && (
                      <span className={cn('text-[9px] font-bold px-1.5 py-0.5 rounded-full', phase.type === 'gate-confirm' ? 'bg-status-yellow/15 text-status-yellow' : 'bg-status-green/15 text-status-green')}>
                        {phase.type === 'gate-confirm' ? copy.confirmGate : copy.qualityGate}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-text-muted leading-relaxed">{phase.desc}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
