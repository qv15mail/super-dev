/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：宿主兼容性矩阵组件
 * 作用：展示 15+ 支持的 AI 宿主工具及兼容状态
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { HOSTS } from '@/lib/constants';
import { Badge } from '@/components/ui/Badge';
import type { HostStatus } from '@/lib/constants';

const STATUS_LABELS: Record<HostStatus, string> = {
  certified: '认证',
  compatible: '兼容',
  experimental: '实验性',
};

const STATUS_BADGE_VARIANT: Record<HostStatus, 'certified' | 'compatible' | 'experimental'> = {
  certified: 'certified',
  compatible: 'compatible',
  experimental: 'experimental',
};

const STATUS_DESCRIPTION: Record<HostStatus, string> = {
  certified: '经过完整测试，推荐使用',
  compatible: '基础功能可用，持续优化中',
  experimental: '实验性支持，欢迎反馈',
};

export function HostCompatSection() {
  return (
    <section
      id="hosts"
      className="py-20 lg:py-28 bg-bg-secondary"
      aria-labelledby="hosts-title"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        {/* 标题区 */}
        <div className="text-center mb-14">
          <p className="text-sm font-mono text-accent-blue mb-3 tracking-wider uppercase">
            跨平台兼容，不站队
          </p>
          <h2
            id="hosts-title"
            className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight"
          >
            支持 15+ AI 宿主工具
          </h2>
          <p className="text-text-secondary max-w-2xl mx-auto">
            你用什么 AI 工具，Super Dev 就在哪里工作。不需要切换工具，
            不需要放弃已有的工作流——即插即用。
          </p>
        </div>

        {/* 宿主卡片网格 */}
        <ul
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"
          role="list"
          aria-label="支持的宿主工具列表"
        >
          {HOSTS.map((host) => (
            <li key={host.name}>
              <div className="p-4 rounded-xl bg-bg-primary border border-border-default hover:border-accent-blue/30 transition-all duration-200 group">
                {/* 图标占位 */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 rounded-lg bg-bg-tertiary border border-border-muted flex items-center justify-center shrink-0">
                    <span className="text-xs font-mono font-bold text-text-muted">
                      {host.abbr}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-text-primary">{host.name}</p>
                </div>

                <Badge variant={STATUS_BADGE_VARIANT[host.status]}>
                  {STATUS_LABELS[host.status]}
                </Badge>
              </div>
            </li>
          ))}
        </ul>

        {/* 状态说明 */}
        <div
          className="mt-8 flex flex-wrap justify-center gap-6"
          aria-label="兼容状态说明"
        >
          {(Object.keys(STATUS_DESCRIPTION) as HostStatus[]).map((status) => (
            <div key={status} className="flex items-center gap-2 text-xs text-text-muted">
              <Badge variant={STATUS_BADGE_VARIANT[status]}>{STATUS_LABELS[status]}</Badge>
              <span>{STATUS_DESCRIPTION[status]}</span>
            </div>
          ))}
        </div>

        {/* 底部说明 */}
        <p className="text-center text-sm text-text-muted mt-8">
          更多宿主持续接入中。
          <a
            href="https://github.com/shangyankeji/super-dev/issues"
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent-blue hover:text-accent-blue-hover transition-colors ml-1"
          >
            提交 Issue 申请支持你的工具
          </a>
        </p>
      </div>
    </section>
  );
}
