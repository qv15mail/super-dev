import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';
import type { SiteLocale } from '@/lib/site-locale';

const CHANGELOG = {
  zh: [
    { version: '2.0.12', date: '2026-03-21', type: 'major' as const, changes: ['新增直接命令模式：super-dev "需求描述" 一行启动完整流水线', '新增 Expert Agent 专家智能体系统，根据项目领域自动激活领域专家', '新增阶段跳转指令 super-dev run <stage_number>，支持跳过已完成阶段直接推进', '质量门禁新增 A11y 无障碍检查（WCAG 2.1 AA），确保交付产物的可访问性', '升级流水线引擎，优化阶段间状态传递与恢复机制'] },
    { version: '2.0.12', date: '2026-03-20', type: 'patch' as const, changes: ['对外主推宿主矩阵收敛到 16 个热门宿主，减少实验宿主带来的不稳定预期', '新增显式 Bugfix Mode（super-dev fix），修复缺陷时走轻量补丁路径', '新增 Repo Map、Feature Checklist、Impact、Regression Guard、Dependency Graph，形成完整代码库理解与范围覆盖审计链路', '新增 Host Validation Center 能力：宿主前置条件诊断、运行时验收状态和交付就绪摘要', '新增 integrate harden、spec scaffold / quality、run --status / --phase / --jump / --confirm 等流程控制指令', '新增可直接输入的流程控制捷径：super-dev status、super-dev run research/prd/architecture/uiux/frontend/backend/quality、super-dev jump <stage>、super-dev confirm <phase>', '升级 Proof Pack 与 Release Readiness，加入 Scope Coverage，明确区分流程完成与范围完成'] },
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['新增显式 bootstrap 初始化产物（.super-dev/WORKFLOW.md 与 output/*-bootstrap.md）', '新增宿主运行时真人验收命令 integrate validate 与状态记录', '新增 release proof-pack 交付证据包，并在 Web 管理台展示完整度、阻塞项与关键证据', '修复 analyzer 将 .venv / site-packages 误纳入项目分析的问题', '恢复 bugfix 轻量路径、澄清问题与默认时序图输出'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['修复宿主检测在特定环境下的兼容性问题', '优化 pipeline-contract 输出格式', '新增 Antigravity 宿主实验性支持'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['重构 12 阶段流水线引擎，支持全流程恢复（run --resume）', '新增 enterprise 策略预设', '新增 delivery archive 完整交付包生成', '新增宿主画像与兼容性评分系统', '新增红队审查三维度检查（安全 / 性能 / 架构）', '新增 UI Review 审查', '支持更多宿主'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['首次发布', '基础流水线框架（research / documents / spec / implement）', '支持 Claude Code、Cursor、Windsurf 宿主', 'PyPI 正式发布'] },
  ],
  en: [
    { version: '2.0.12', date: '2026-03-21', type: 'major' as const, changes: ['Added direct command mode: super-dev "requirement" launches the full pipeline in one line', 'Added Expert Agent system that auto-activates domain specialists based on project context', 'Added stage jump command super-dev run <stage_number> to skip completed stages and advance directly', 'Quality gate now includes A11y accessibility checks (WCAG 2.1 AA) to ensure deliverable accessibility', 'Upgraded pipeline engine with improved inter-stage state transfer and recovery'] },
    { version: '2.0.12', date: '2026-03-20', type: 'patch' as const, changes: ['Focused the public host matrix on 16 primary hosts instead of advertising unstable lab adapters', 'Added explicit Bugfix Mode through super-dev fix so defect work follows a lightweight patch path', 'Added Repo Map, Feature Checklist, Impact, Regression Guard, and Dependency Graph as a complete codebase-intelligence and scope-audit chain', 'Added Host Validation Center capabilities for host prerequisites, runtime acceptance state, and delivery readiness summaries', 'Added workflow-control commands including integrate harden, spec scaffold / quality, and run --status / --phase / --jump / --confirm', 'Added direct workflow shortcuts: super-dev status, super-dev run research/prd/architecture/uiux/frontend/backend/quality, super-dev jump <stage>, and super-dev confirm <phase>', 'Upgraded Proof Pack and Release Readiness with Scope Coverage so pipeline completion is distinct from full scope completion'] },
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
