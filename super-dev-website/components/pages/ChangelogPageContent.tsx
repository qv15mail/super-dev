import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';
import type { SiteLocale } from '@/lib/site-locale';

const CHANGELOG = {
  zh: [
    { version: '2.1.5', date: '2026-03-26', type: 'patch' as const, changes: ['修复 Windows 下 uv tool upgrade 文件锁定问题（自动重试 + 清晰提示）', '新增 super-dev clean 命令（清理历史产物，支持 --keep/--all/--dry-run）', '6 人 Agent 团队全项目深度审查，修复 37 个 bug（含 3 个 P0 崩溃、12 个 P1 逻辑错误）', '修复 proof-pack rehearsal 状态始终为 ready 的问题', '修复 Sequelize/Jenkins/TypeORM 生成代码的语法错误', '新增路径遍历安全防护（specs delete/change 操作）', '质量评分计算从整数截断改为四舍五入', '官网新增案例展示页（20+ 个真实项目）', '官网更新日志补全全部 18 个历史版本（1.0.0 ~ 2.1.5）'] },
    { version: '2.1.3', date: '2026-03-25', type: 'patch' as const, changes: ['OpenClaw 插件升级至 13 个 Tool（新增 deploy/analyze/doctor）', 'SKILL.md 全面重写至 481 行，完整覆盖 9 阶段执行指令、2 门禁交互模板、3 返工协议、resume 恢复智能', '修复 init 必填参数 name 缺失、quality --threshold 不存在、deploy --platform 应为 --cicd、pipeline --frontend 选项集错误等致命 CLI 映射问题', '新增 4 篇参考文档（commands/pipeline-stages/expert-roles/gate-interactions，共 883 行）', '补全 spec propose/scaffold 完整参数、domain 枚举（auth/content/saas）、review status 枚举（pending_review）', 'Skill 已发布至 ClawHub，用户可通过 clawhub install super-dev 安装'] },
    { version: '2.1.2', date: '2026-03-24', type: 'major' as const, changes: ['新增 OpenClaw 原生插件（@super-dev/openclaw-plugin），通过 Plugin SDK 注册 13 个专用 Tool', '宿主矩阵扩展至 21 个（新增 OpenClaw 为第 29 个宿主）', '修复 50+ 个 bug：delete_spec 删错目录、Prisma nullable 反转、TypeORM 语法错误、CLI console 崩溃等', '新增 backend/src/app.js 入口文件和 frontend/src/App.tsx 根组件', '补全 3 个缺失的后端路由（core/experience/operation）', '修复 7 个后端 repository 的 ID 覆盖漏洞和生成策略', '修复 HSL 色彩算法、asyncio 弃用 API、SQLAlchemy 迁移语法等'] },
    { version: '2.1.1', date: '2026-03-21', type: 'major' as const, changes: ['新增直接命令模式：super-dev "需求描述" 一行启动完整流水线', '新增 Expert Agent 专家智能体系统，根据项目领域自动激活领域专家', '新增阶段跳转指令 super-dev run <stage_number>，支持跳过已完成阶段直接推进', '质量门禁新增 A11y 无障碍检查（WCAG 2.1 AA），确保交付产物的可访问性', '升级流水线引擎，优化阶段间状态传递与恢复机制'] },
    { version: '2.1.1', date: '2026-03-20', type: 'patch' as const, changes: ['对外主推宿主矩阵收敛到 16 个热门宿主，减少实验宿主带来的不稳定预期', '新增显式 Bugfix Mode（super-dev fix），修复缺陷时走轻量补丁路径', '新增 Repo Map、Feature Checklist、Impact、Regression Guard、Dependency Graph，形成完整代码库理解与范围覆盖审计链路', '新增 Host Validation Center 能力：宿主前置条件诊断、运行时验收状态和交付就绪摘要', '新增 integrate harden、spec scaffold / quality、run --status / --phase / --jump / --confirm 等流程控制指令', '新增可直接输入的流程控制捷径：super-dev status、super-dev run research/prd/architecture/uiux/frontend/backend/quality、super-dev jump <stage>、super-dev confirm <phase>', '升级 Proof Pack 与 Release Readiness，加入 Scope Coverage，明确区分流程完成与范围完成'] },
    { version: '2.1.0', date: '2026-03-21', type: 'major' as const, changes: ['10 专家 Agent 系统：PM/ARCHITECT/UI/UX/SECURITY/CODE/DBA/QA/DEVOPS/RCA，每位专家含完整画像、思维框架与质量标准', '20 宿主完美适配：新增 Copilot CLI/Kilo Code/Cline/Roo Code，修正 Cursor .mdc/Windsurf rules/Kiro steering 格式', '119 种配色方案（含暗色模式自动生成）+ 39 个组件库 + 17 种字体预设', '新增直接命令模式 super-dev "需求" 和阶段跳转 super-dev run 1-9'] },
    { version: '2.0.12', date: '2026-03-23', type: 'patch' as const, changes: ['修复版本对齐和发布流程问题', '优化 PyPI 包构建和元数据'] },
    { version: '2.0.11', date: '2026-03-15', type: 'patch' as const, changes: ['UI Intelligence 大幅扩充：配色方案从 7 种扩至 84 种 + 35 种美学方向', '组件库推荐从 12 个扩至 39 个，覆盖 React/Vue/Angular/Svelte/小程序/RN/Flutter', '新增 17 种产品专属字体预设（Google Fonts 中国镜像）', '新增 12 项交付前检查清单、9 个行业信任规则', 'UIUX 文档新增色阶系统、语义色、组件 CSS 规格、阴影层级、动效规范'] },
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['新增显式 bootstrap 初始化产物（.super-dev/WORKFLOW.md 与 output/*-bootstrap.md）', '新增宿主运行时真人验收命令 integrate validate 与状态记录', '新增 release proof-pack 交付证据包，并在 Web 管理台展示完整度、阻塞项与关键证据', '修复 analyzer 将 .venv / site-packages 误纳入项目分析的问题', '恢复 bugfix 轻量路径、澄清问题与默认时序图输出'] },
    { version: '2.0.9', date: '2026-03-11', type: 'patch' as const, changes: ['新增 Impact Analysis 变更影响分析', '新增 Feature Checklist PRD 范围覆盖率审计', '优化流水线阶段间状态传递'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['修复宿主检测在特定环境下的兼容性问题', '优化 pipeline-contract 输出格式', '新增 Antigravity 宿主实验性支持'] },
    { version: '2.0.7', date: '2026-03-07', type: 'patch' as const, changes: ['修复 Skill 安装路径解析、slash 命令注册和宿主检测的多个边缘问题', '优化 CI/CD 配置生成的 YAML 格式'] },
    { version: '2.0.6', date: '2026-03-07', type: 'patch' as const, changes: ['修复 Windsurf rules 路径、Kiro steering frontmatter 格式', '优化宿主规则文件的内容一致性'] },
    { version: '2.0.5', date: '2026-03-07', type: 'patch' as const, changes: ['修复 Cursor .mdc frontmatter 格式兼容性', '优化 Codex CLI 的 Flow Contract 注入'] },
    { version: '2.0.4', date: '2026-03-07', type: 'patch' as const, changes: ['优化宿主适配器的检测逻辑和错误提示', '修复多个宿主的 slash 命令路径'] },
    { version: '2.0.3', date: '2026-03-05', type: 'patch' as const, changes: ['宿主适配器扩展：新增 Kilo Code、Cline、Roo Code 支持', 'Skill-only 模式：宿主仅安装 Skill 无需 slash 命令'] },
    { version: '2.0.2', date: '2026-03-05', type: 'patch' as const, changes: ['宿主级工作流隔离：每个宿主独立的协议面和状态', '修复多宿主并发接入时的文件冲突'] },
    { version: '2.0.1', date: '2026-03-02', type: 'patch' as const, changes: ['完善工作流文档和任务闭环逻辑', '修复 Spec 任务状态持久化问题'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['重构 12 阶段流水线引擎，支持全流程恢复（run --resume）', '新增 enterprise 策略预设', '新增 delivery archive 完整交付包生成', '新增宿主画像与兼容性评分系统', '新增红队审查三维度检查（安全 / 性能 / 架构）', '新增 UI Review 审查', '支持更多宿主'] },
    { version: '1.0.1', date: '2026-01-04', type: 'patch' as const, changes: ['新增完整工作流教程 (WORKFLOW_GUIDE.md)', '整合设计智能引擎（配色、字体、图表推荐）', '新增 Landing 页面模式生成器', '新增 UX 指南数据库'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['首次发布', '基础流水线框架（research / documents / spec / implement）', 'Spec-Driven Development 模块', '支持 Claude Code、Cursor、Windsurf 宿主', 'PyPI 正式发布'] },
  ],
  en: [
    { version: '2.1.5', date: '2026-03-26', type: 'patch' as const, changes: ['Fixed Windows uv tool upgrade file lock issue (auto-retry + clear guidance)', 'Added super-dev clean command (clean historical artifacts with --keep/--all/--dry-run)', '6-agent team deep audit: fixed 37 bugs (3 P0 crashes, 12 P1 logic errors)', 'Fixed proof-pack rehearsal status always showing ready', 'Fixed Sequelize/Jenkins/TypeORM generated code syntax errors', 'Added path traversal security protection for specs delete/change operations', 'Quality scoring changed from integer truncation to rounding', 'Added showcase page with 20+ real project cases', 'Changelog now includes all 18 historical versions (1.0.0 ~ 2.1.5)'] },
    { version: '2.1.3', date: '2026-03-25', type: 'patch' as const, changes: ['OpenClaw plugin upgraded to 13 Tools (added deploy/analyze/doctor)', 'SKILL.md fully rewritten to 481 lines covering 9-stage execution instructions, 2 gate interaction templates, 3 rework protocols, and resume intelligence', 'Fixed critical CLI mapping bugs: init missing required name arg, quality --threshold nonexistent, deploy --platform should be --cicd, pipeline --frontend choices incorrect', 'Added 4 reference documents (commands/pipeline-stages/expert-roles/gate-interactions, 883 lines total)', 'Completed spec propose/scaffold params, domain enum (auth/content/saas), review status enum (pending_review)', 'Skill published to ClawHub, users can install via clawhub install super-dev'] },
    { version: '2.1.2', date: '2026-03-24', type: 'major' as const, changes: ['Added OpenClaw native plugin (@super-dev/openclaw-plugin) with 13 registered tools via Plugin SDK', 'Expanded host matrix to 21 (OpenClaw added as 29th host)', 'Fixed 50+ bugs: delete_spec wrong directory, Prisma nullable inverted, TypeORM syntax error, CLI console crash, etc.', 'Added missing backend/src/app.js entry and frontend/src/App.tsx root component', 'Added 3 missing backend routes (core/experience/operation)', 'Fixed ID override vulnerability and generation strategy in 7 backend repositories', 'Fixed HSL color algorithm, asyncio deprecated API, SQLAlchemy migration syntax, and more'] },
    { version: '2.1.1', date: '2026-03-21', type: 'major' as const, changes: ['Added direct command mode: super-dev "requirement" launches the full pipeline in one line', 'Added Expert Agent system that auto-activates domain specialists based on project context', 'Added stage jump command super-dev run <stage_number> to skip completed stages and advance directly', 'Quality gate now includes A11y accessibility checks (WCAG 2.1 AA) to ensure deliverable accessibility', 'Upgraded pipeline engine with improved inter-stage state transfer and recovery'] },
    { version: '2.1.1', date: '2026-03-20', type: 'patch' as const, changes: ['Focused the public host matrix on 16 primary hosts instead of advertising unstable lab adapters', 'Added explicit Bugfix Mode through super-dev fix so defect work follows a lightweight patch path', 'Added Repo Map, Feature Checklist, Impact, Regression Guard, and Dependency Graph as a complete codebase-intelligence and scope-audit chain', 'Added Host Validation Center capabilities for host prerequisites, runtime acceptance state, and delivery readiness summaries', 'Added workflow-control commands including integrate harden, spec scaffold / quality, and run --status / --phase / --jump / --confirm', 'Added direct workflow shortcuts: super-dev status, super-dev run research/prd/architecture/uiux/frontend/backend/quality, super-dev jump <stage>, and super-dev confirm <phase>', 'Upgraded Proof Pack and Release Readiness with Scope Coverage so pipeline completion is distinct from full scope completion'] },
    { version: '2.1.0', date: '2026-03-21', type: 'major' as const, changes: ['10 Expert Agent system: PM/ARCHITECT/UI/UX/SECURITY/CODE/DBA/QA/DEVOPS/RCA with full profiles, thinking frameworks, and quality standards', '20 host adapters: added Copilot CLI/Kilo Code/Cline/Roo Code, fixed Cursor .mdc/Windsurf rules/Kiro steering formats', '119 color schemes (with dark mode auto-generation) + 39 component libraries + 17 font presets', 'Added direct command mode super-dev "requirement" and stage jump super-dev run 1-9'] },
    { version: '2.0.12', date: '2026-03-23', type: 'patch' as const, changes: ['Fixed version alignment and release pipeline', 'Improved PyPI package build and metadata'] },
    { version: '2.0.11', date: '2026-03-15', type: 'patch' as const, changes: ['UI Intelligence major expansion: color schemes from 7 to 84 + 35 aesthetic directions', 'Component library recommendations expanded from 12 to 39 covering React/Vue/Angular/Svelte/Mini Programs/RN/Flutter', 'Added 17 product-specific font presets (Google Fonts China mirror)', 'Added 12 pre-delivery checklists and 9 industry trust rules', 'UIUX docs now include color scale system, semantic colors, component CSS specs, shadow levels, motion specs'] },
    { version: '2.0.10', date: '2026-03-11', type: 'patch' as const, changes: ['Added explicit bootstrap artifacts (.super-dev/WORKFLOW.md and output/*-bootstrap.md)', 'Added integrate validate for host runtime acceptance with persisted status', 'Added release proof-pack and surfaced completion, blockers, and key artifacts in the Web console', 'Fixed analyzer scope so .venv / site-packages are excluded from project analysis', 'Restored lightweight bugfix flow, clarification prompts, and default sequence diagrams'] },
    { version: '2.0.9', date: '2026-03-11', type: 'patch' as const, changes: ['Added Impact Analysis for change scope assessment', 'Added Feature Checklist for PRD coverage audit', 'Improved inter-stage state transfer in pipeline'] },
    { version: '2.0.8', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed host detection issues in edge environments', 'Improved pipeline-contract output format', 'Added experimental support for Antigravity'] },
    { version: '2.0.7', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed skill install path resolution, slash command registration, and host detection edge cases', 'Improved CI/CD YAML generation format'] },
    { version: '2.0.6', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed Windsurf rules path and Kiro steering frontmatter format', 'Improved host rule file content consistency'] },
    { version: '2.0.5', date: '2026-03-07', type: 'patch' as const, changes: ['Fixed Cursor .mdc frontmatter compatibility', 'Improved Codex CLI Flow Contract injection'] },
    { version: '2.0.4', date: '2026-03-07', type: 'patch' as const, changes: ['Improved host adapter detection logic and error messages', 'Fixed slash command paths for multiple hosts'] },
    { version: '2.0.3', date: '2026-03-05', type: 'patch' as const, changes: ['Host adapter expansion: added Kilo Code, Cline, Roo Code', 'Skill-only mode: hosts can install skill without slash command'] },
    { version: '2.0.2', date: '2026-03-05', type: 'patch' as const, changes: ['Host-scoped workflow isolation: independent protocol surfaces per host', 'Fixed file conflicts during concurrent multi-host onboarding'] },
    { version: '2.0.1', date: '2026-03-02', type: 'patch' as const, changes: ['Finalized workflow documentation and task-closure hardening', 'Fixed spec task status persistence'] },
    { version: '2.0.0', date: '2026-02-15', type: 'major' as const, changes: ['Rebuilt the 12-stage pipeline engine with run --resume support', 'Added enterprise policy preset', 'Added full delivery archive packaging', 'Added host profile and compatibility scoring', 'Added three-dimensional red-team review', 'Added UI Review checks', 'Expanded host coverage'] },
    { version: '1.0.1', date: '2026-01-04', type: 'patch' as const, changes: ['Added complete workflow tutorial (WORKFLOW_GUIDE.md)', 'Integrated design intelligence engine (colors, fonts, charts)', 'Added landing page pattern generator', 'Added UX guideline database'] },
    { version: '1.0.0', date: '2025-12-29', type: 'major' as const, changes: ['Initial release', 'Base pipeline framework (research / documents / spec / implement)', 'Spec-Driven Development module', 'Support for Claude Code, Cursor, and Windsurf', 'Official PyPI release'] },
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
