/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：更新日志页
 * 作用：展示 Super Dev 版本更新历史
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import type { Metadata } from 'next';
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';

export const metadata: Metadata = {
  title: '更新日志',
  description: 'Super Dev 版本更新历史',
};

const CHANGELOG = [
  {
    version: '2.0.8',
    date: '2026-03-07',
    type: 'patch' as const,
    changes: [
      '修复宿主检测在特定环境下的兼容性问题',
      '优化 pipeline-contract 输出格式',
      '新增 Antigravity 宿主实验性支持',
    ],
  },
  {
    version: '2.0.0',
    date: '2026-02-15',
    type: 'major' as const,
    changes: [
      '重构 12 阶段流水线引擎，支持全流程恢复（run --resume）',
      '新增 enterprise 策略预设',
      '新增 delivery archive 完整交付包生成',
      '新增宿主画像与兼容性评分系统',
      '新增红队审查三维度检查（安全 / 性能 / 架构）',
      '新增 super-dev quality --type ui-review UI 结构审查',
      '支持宿主列表扩展至 15+',
    ],
  },
  {
    version: '1.0.0',
    date: '2025-12-29',
    type: 'major' as const,
    changes: [
      '首次发布',
      '基础流水线框架（research / documents / spec / implement）',
      '支持 Claude Code、Cursor、Windsurf 宿主',
      'PyPI 正式发布',
    ],
  },
] as const;

const TYPE_BADGE: Record<'major' | 'patch', React.JSX.Element> = {
  major: <Badge variant="certified">主版本</Badge>,
  patch: <Badge variant="compatible">修复</Badge>,
};

export default function ChangelogPage() {
  return (
    <>
      <Nav />
      <main className="pt-14 min-h-screen" id="main-content">
        <section className="py-20 lg:py-24 bg-bg-primary">
          <div className="max-w-2xl mx-auto px-4 sm:px-6">
            <h1 className="text-4xl font-bold text-text-primary mb-2 tracking-tight">更新日志</h1>
            <p className="text-text-muted mb-12">
              Super Dev 版本历史。查看{' '}
              <a
                href="https://github.com/shangyankeji/super-dev/blob/main/CHANGELOG.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-blue hover:text-accent-blue-hover transition-colors"
              >
                GitHub 完整记录
              </a>
            </p>

            <div className="space-y-10">
              {CHANGELOG.map((release) => (
                <article key={release.version} className="relative pl-6 border-l border-border-default">
                  {/* 时间线圆点 */}
                  <div
                    className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-accent-blue border-2 border-bg-primary"
                    aria-hidden="true"
                  />

                  <header className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-mono font-bold text-text-primary">
                      v{release.version}
                    </h2>
                    {TYPE_BADGE[release.type]}
                    <time
                      dateTime={release.date}
                      className="text-sm text-text-muted"
                    >
                      {release.date}
                    </time>
                  </header>

                  <ul className="space-y-2" role="list">
                    {release.changes.map((change) => (
                      <li key={change} className="text-sm text-text-secondary flex items-start gap-2">
                        <span className="text-text-muted mt-0.5" aria-hidden="true">-</span>
                        {change}
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
