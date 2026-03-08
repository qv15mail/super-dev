/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：流水线可视化组件
 * 作用：S 型双行布局展示 12 阶段开发流水线，完整可见，带关键节点标注
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import {
  Search, ListChecks, FileText, UserCheck, Code2,
  Monitor, Server, Link2, ShieldCheck, PlayCircle,
  Archive, CheckCircle2
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { PIPELINE_PHASES } from '@/lib/constants';
import type { PhaseType } from '@/lib/constants';
import { cn } from '@/lib/utils';

const PHASE_ICONS: LucideIcon[] = [
  Search, ListChecks, FileText, UserCheck, Code2,
  Monitor, Server, Link2, ShieldCheck, PlayCircle,
  Archive, CheckCircle2,
];

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

interface PhaseNodeProps {
  id: number;
  name: string;
  nameEn: string;
  desc: string;
  type: PhaseType;
}

function PhaseNode({ id, name, nameEn, desc, type }: PhaseNodeProps) {
  const Icon = PHASE_ICONS[id - 1];

  return (
    <div
      className="group relative flex-1 min-w-0"
      title={desc}
    >
      {/* 门禁徽章 */}
      {(type === 'gate-confirm' || type === 'gate-quality') && (
        <div className="absolute -top-5 left-1/2 -translate-x-1/2 whitespace-nowrap z-10">
          <span
            className={cn(
              'text-[9px] font-bold px-2 py-0.5 rounded-full',
              type === 'gate-confirm'
                ? 'bg-status-yellow/15 text-status-yellow border border-status-yellow/40'
                : 'bg-status-green/15 text-status-green border border-status-green/40'
            )}
          >
            {type === 'gate-confirm' ? '确认门' : '质量门'}
          </span>
        </div>
      )}

      <div
        className={cn(
          'relative p-3 rounded-xl border transition-colors duration-200 cursor-default',
          'flex flex-col items-center text-center gap-1.5',
          cardStyles[type]
        )}
        role="listitem"
        aria-label={`阶段 ${id}：${name}。${desc}`}
      >
        {/* 序号 */}
        <span className={cn('text-[10px] font-mono leading-none', numberStyles[type])}>
          {String(id).padStart(2, '0')}
        </span>

        {/* 图标 */}
        <div className={cn('w-7 h-7 rounded-lg flex items-center justify-center', iconBgStyles[type])}>
          <Icon size={14} aria-hidden="true" />
        </div>

        {/* 名称 */}
        <p className="text-[11px] font-medium text-text-primary leading-tight">{name}</p>
        <p className="text-[9px] text-text-muted leading-tight hidden sm:block">{nameEn}</p>
      </div>

      {/* 悬停 tooltip */}
      <div
        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 hidden group-hover:block z-20 pointer-events-none"
        role="tooltip"
      >
        <div className="bg-bg-elevated border border-border-default rounded-lg px-3 py-2 text-xs text-text-secondary max-w-[180px] text-center shadow-2xl shadow-black/50 leading-relaxed">
          {desc}
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-border-default" aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}

/** 水平连接箭头 */
function ArrowH() {
  return (
    <div className="flex items-center self-center shrink-0 px-1" aria-hidden="true">
      <div className="w-3 sm:w-5 h-px bg-border-default" />
      <div className="w-0 h-0 border-t-[3px] border-b-[3px] border-l-[4px] border-t-transparent border-b-transparent border-l-border-default" />
    </div>
  );
}


export function PipelineSection() {
  const row1 = PIPELINE_PHASES.slice(0, 6);
  const row2 = PIPELINE_PHASES.slice(6, 12);

  return (
    <section
      className="py-20 lg:py-28 bg-bg-primary"
      aria-labelledby="pipeline-title"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* 标题区 */}
        <div className="text-center mb-16">
          <p className="text-sm font-mono text-accent-blue mb-3 tracking-wider uppercase">
            从想法到交付
          </p>
          <h2
            id="pipeline-title"
            className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight"
          >
            12 阶段开发流水线
          </h2>
          <p className="text-text-secondary max-w-2xl mx-auto">
            每个阶段都有输入、输出和证据。关键节点设有人工确认门和质量门禁，
            阻断不达标的产出。
          </p>
        </div>

        {/* 流水线：桌面 S 型双行，移动端纵向列表 */}

        {/* 桌面 / 平板：S 型双行 */}
        <div
          className="hidden sm:block"
          role="list"
          aria-label="12 阶段开发流水线"
        >
          {/* 第一行：阶段 01-06，从左到右 */}
          <div className="relative flex items-center mb-2 pt-6">
            {row1.map((phase, index) => (
              <div key={phase.id} className="flex items-center flex-1 min-w-0">
                <PhaseNode
                  id={phase.id}
                  name={phase.name}
                  nameEn={phase.nameEn}
                  desc={phase.desc}
                  type={phase.type}
                />
                {index < row1.length - 1 && <ArrowH />}
              </div>
            ))}

            {/* 右侧折返：竖向连接线从第一行末尾到第二行 */}
            <div className="shrink-0 w-5 flex flex-col items-center self-stretch ml-1" aria-hidden="true">
              <div className="flex-1 w-px bg-border-default" />
              <div className="w-0 h-0 border-l-[3px] border-r-[3px] border-t-[4px] border-l-transparent border-r-transparent border-t-border-default mb-0.5" />
            </div>
          </div>

          {/* 折返分隔 + 向左箭头指示 */}
          <div className="flex justify-end pr-5 mb-2" aria-hidden="true">
            <div className="flex items-center gap-1.5 text-[9px] text-text-muted font-mono">
              <div className="w-0 h-0 border-t-[3px] border-b-[3px] border-r-[4px] border-t-transparent border-b-transparent border-r-border-default" />
              <div className="w-3 h-px bg-border-default" />
              继续
              <div className="w-3 h-px bg-border-default" />
            </div>
          </div>

          {/* 第二行：阶段 07-12，从左到右 */}
          <div className="flex items-center pb-6">
            {/* 左侧折返竖线占位 */}
            <div className="shrink-0 w-5 mr-1" aria-hidden="true" />

            {row2.map((phase, index) => (
              <div key={phase.id} className="flex items-center flex-1 min-w-0">
                <PhaseNode
                  id={phase.id}
                  name={phase.name}
                  nameEn={phase.nameEn}
                  desc={phase.desc}
                  type={phase.type}
                />
                {index < row2.length - 1 && <ArrowH />}
              </div>
            ))}
          </div>
        </div>

        {/* 移动端：紧凑纵向列表 */}
        <ol
          className="sm:hidden space-y-2"
          aria-label="12 阶段开发流水线"
        >
          {PIPELINE_PHASES.map((phase) => {
            const Icon = PHASE_ICONS[phase.id - 1];
            return (
              <li
                key={phase.id}
                className={cn(
                  'flex items-start gap-3 p-3 rounded-xl border',
                  cardStyles[phase.type]
                )}
              >
                {/* 序号 + 图标 */}
                <div className="flex flex-col items-center gap-1 shrink-0">
                  <span className={cn('text-[10px] font-mono font-bold', numberStyles[phase.type])}>
                    {String(phase.id).padStart(2, '0')}
                  </span>
                  <div className={cn('w-7 h-7 rounded-lg flex items-center justify-center', iconBgStyles[phase.type])}>
                    <Icon size={14} aria-hidden="true" />
                  </div>
                </div>

                {/* 文字 */}
                <div className="min-w-0 pt-0.5">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="text-sm font-medium text-text-primary">{phase.name}</p>
                    {(phase.type === 'gate-confirm' || phase.type === 'gate-quality') && (
                      <span
                        className={cn(
                          'text-[9px] font-bold px-1.5 py-0.5 rounded-full',
                          phase.type === 'gate-confirm'
                            ? 'bg-status-yellow/15 text-status-yellow'
                            : 'bg-status-green/15 text-status-green'
                        )}
                      >
                        {phase.type === 'gate-confirm' ? '确认门' : '质量门'}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-text-muted leading-relaxed">{phase.desc}</p>
                </div>
              </li>
            );
          })}
        </ol>

        {/* 图例 */}
        <div
          className="flex flex-wrap justify-center gap-x-6 gap-y-3 mt-10 pt-8 border-t border-border-muted"
          aria-label="图例说明"
        >
          {[
            { dot: 'bg-text-muted', label: '常规阶段' },
            { dot: 'bg-accent-blue', label: '产物输出' },
            { dot: 'bg-status-yellow', label: '用户确认门（第 4 阶段）' },
            { dot: 'bg-status-green', label: '质量门禁（第 9 阶段）' },
          ].map(({ dot, label }) => (
            <div key={label} className="flex items-center gap-2 text-xs text-text-muted">
              <span className={cn('w-2 h-2 rounded-full shrink-0', dot)} aria-hidden="true" />
              {label}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
