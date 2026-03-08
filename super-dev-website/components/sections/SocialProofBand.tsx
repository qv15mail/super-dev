/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：社会证明带组件
 * 作用：展示统计数字和宿主工具 Logo 无限滚动带
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { HOSTS, STATS } from '@/lib/constants';

function HostLogo({ abbr, name }: { abbr: string; name: string }) {
  return (
    <div
      className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border-muted bg-bg-secondary/50 opacity-60 hover:opacity-100 transition-opacity duration-200 shrink-0"
      title={name}
    >
      <span className="w-6 h-6 rounded bg-bg-tertiary flex items-center justify-center text-xs font-mono font-bold text-text-muted">
        {abbr}
      </span>
      <span className="text-sm text-text-secondary whitespace-nowrap">{name}</span>
    </div>
  );
}

export function SocialProofBand() {
  return (
    <section className="bg-bg-secondary border-y border-border-muted py-10" aria-label="统计数字与支持的工具">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        {/* 统计数字行 */}
        <dl className="flex flex-wrap justify-center gap-8 sm:gap-16 mb-10">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <dt className="text-sm text-text-muted">{stat.label}</dt>
              <dd className="text-2xl font-bold font-mono text-text-primary mt-1">{stat.value}</dd>
            </div>
          ))}
        </dl>

        {/* 分割线 */}
        <div className="flex items-center gap-4 mb-8">
          <div className="flex-1 h-px bg-border-muted" />
          <span className="text-xs text-text-muted tracking-wider uppercase">兼容的 AI 宿主工具</span>
          <div className="flex-1 h-px bg-border-muted" />
        </div>

        {/* Logo 滚动带 */}
        <div
          className="overflow-hidden relative"
          aria-label={`支持的宿主工具列表：${HOSTS.map((h) => h.name).join('、')}`}
        >
          {/* 左右渐变遮罩 */}
          <div
            className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-bg-secondary to-transparent z-10 pointer-events-none"
            aria-hidden="true"
          />
          <div
            className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-bg-secondary to-transparent z-10 pointer-events-none"
            aria-hidden="true"
          />

          {/* 滚动容器 */}
          <div className="flex gap-3 [&:hover>div]:animation-play-state-paused">
            <div className="flex gap-3 animate-marquee" aria-hidden="true">
              {HOSTS.map((host) => (
                <HostLogo key={`a-${host.name}`} abbr={host.abbr} name={host.name} />
              ))}
            </div>
            <div className="flex gap-3 animate-marquee2" aria-hidden="true">
              {HOSTS.map((host) => (
                <HostLogo key={`b-${host.name}`} abbr={host.abbr} name={host.name} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
