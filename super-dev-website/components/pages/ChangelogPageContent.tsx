import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';
import type { SiteLocale } from '@/lib/site-locale';

const CHANGELOG = {
  zh: [
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['新增显式 bootstrap 初始化产物（.super-dev/WORKFLOW.md 与 output/*-bootstrap.md）', '新增宿主运行时真人验收命令 integrate validate 与状态记录', '新增 release proof-pack 交付证据包，并在 Web 管理台展示完整度、阻塞项与关键证据', '修复 analyzer 将 .venv / site-packages 误纳入项目分析的问题', '恢复 bugfix 轻量路径、澄清问题与默认时序图输出'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['修复宿主检测在特定环境下的兼容性问题', '优化 pipeline-contract 输出格式', '新增 Antigravity 宿主实验性支持'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['重构 12 阶段流水线引擎，支持全流程恢复（run --resume）', '新增 enterprise 策略预设', '新增 delivery archive 完整交付包生成', '新增宿主画像与兼容性评分系统', '新增红队审查三维度检查（安全 / 性能 / 架构）', '新增 UI Review 审查', '支持更多宿主'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['首次发布', '基础流水线框架（research / documents / spec / implement）', '支持 Claude Code、Cursor、Windsurf 宿主', 'PyPI 正式发布'] },
  ],
  en: [
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['Added explicit bootstrap artifacts (.super-dev/WORKFLOW.md and output/*-bootstrap.md)', 'Added integrate validate for host runtime acceptance with persisted status', 'Added release proof-pack and surfaced completion, blockers, and key artifacts in the Web console', 'Fixed analyzer scope so .venv / site-packages are excluded from project analysis', 'Restored lightweight bugfix flow, clarification prompts, and default sequence diagrams'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed host detection issues in edge environments', 'Improved pipeline-contract output format', 'Added experimental support for Antigravity'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['Rebuilt the 12-stage pipeline engine with run --resume support', 'Added enterprise policy preset', 'Added full delivery archive packaging', 'Added host profile and compatibility scoring', 'Added three-dimensional red-team review', 'Added UI Review checks', 'Expanded host coverage'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['Initial release', 'Base pipeline framework (research / documents / spec / implement)', 'Support for Claude Code, Cursor, and Windsurf', 'Official PyPI release'] },
  ],
} as const;

const COPY = {
  zh: { title: '更新日志', body: 'Super Dev 版本历史。查看', link: 'GitHub 完整记录', major: '主版本', patch: '修复' },
  en: { title: 'Changelog', body: 'Version history for Super Dev. See the', link: 'full GitHub changelog', major: 'Major', patch: 'Patch' },
} as const;

export function ChangelogPageContent({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  const releases = CHANGELOG[locale];
  const typeBadge = { major: <Badge variant="certified">{copy.major}</Badge>, patch: <Badge variant="compatible">{copy.patch}</Badge> };
  return (
    <>
      <Nav locale={locale} />
      <main className="pt-14 min-h-screen" id="main-content">
        <section className="py-20 lg:py-24 bg-bg-primary">
          <div className="max-w-2xl mx-auto px-4 sm:px-6">
            <h1 className="text-4xl font-bold text-text-primary mb-2 tracking-tight">{copy.title}</h1>
            <p className="text-text-muted mb-12">{copy.body}{' '}<a href="https://github.com/shangyankeji/super-dev/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer" className="text-accent-blue hover:text-accent-blue-hover transition-colors">{copy.link}</a></p>
            <div className="space-y-10">
              {releases.map((release) => (
                <article key={release.version} className="relative pl-6 border-l border-border-default">
                  <div className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-accent-blue border-2 border-bg-primary" aria-hidden="true" />
                  <header className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-mono font-bold text-text-primary">v{release.version}</h2>
                    {typeBadge[release.type]}
                    <time dateTime={release.date} className="text-sm text-text-muted">{release.date}</time>
                  </header>
                  <ul className="space-y-2" role="list">
                    {release.changes.map((change) => <li key={change} className="text-sm text-text-secondary flex items-start gap-2"><span className="text-text-muted mt-0.5">-</span>{change}</li>)}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </>
  );
}
