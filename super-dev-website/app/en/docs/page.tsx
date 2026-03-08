import type { Metadata } from 'next';
import Link from 'next/link';
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Command,
  FolderTree,
  Layers3,
  LifeBuoy,
  Package,
  Rocket,
  Search,
  ShieldCheck,
  Sparkles,
  Terminal,
  Workflow,
} from 'lucide-react';
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { Badge } from '@/components/ui/Badge';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { CopyCommand } from '@/components/ui/CopyCommand';

export const metadata: Metadata = {
  title: 'Docs',
  description: 'Standalone Super Dev docs covering installation, host compatibility, trigger model, governed pipeline, knowledge base, quality gates, and release readiness.',
};

const DOC_SECTIONS = [
  { id: 'overview', label: 'Overview', icon: BookOpen },
  { id: 'quickstart', label: 'Quick Start', icon: Rocket },
  { id: 'install', label: 'Installation', icon: Package },
  { id: 'hosts', label: 'Host Matrix', icon: Layers3 },
  { id: 'triggers', label: 'Trigger Model', icon: Command },
  { id: 'pipeline', label: 'Pipeline', icon: Workflow },
  { id: 'knowledge', label: 'Knowledge Base', icon: FolderTree },
  { id: 'quality', label: 'Quality & Delivery', icon: ShieldCheck },
  { id: 'commands', label: 'Commands', icon: Terminal },
  { id: 'troubleshooting', label: 'Troubleshooting', icon: LifeBuoy },
] as const;

const HOST_PROTOCOLS = [
  {
    category: 'CLI Hosts',
    items: [
      { host: 'claude-code', trigger: '/super-dev', protocol: 'official commands + subagents', grade: 'Certified' },
      { host: 'codex-cli', trigger: 'super-dev:', protocol: 'official AGENTS.md + official Skills', grade: 'Certified' },
      { host: 'opencode', trigger: '/super-dev', protocol: 'official commands + skills', grade: 'Experimental' },
      { host: 'gemini-cli', trigger: '/super-dev', protocol: 'official commands + GEMINI.md', grade: 'Compatible' },
      { host: 'kiro-cli', trigger: '/super-dev', protocol: 'official commands + AGENTS.md', grade: 'Compatible' },
      { host: 'kimi-cli', trigger: 'super-dev:', protocol: 'official AGENTS.md + text trigger', grade: 'Compatible' },
      { host: 'iflow', trigger: '/super-dev', protocol: 'official commands + skills', grade: 'Experimental' },
      { host: 'cursor-cli', trigger: '/super-dev', protocol: 'official commands + rules', grade: 'Compatible' },
      { host: 'qoder-cli', trigger: '/super-dev', protocol: 'official commands + skills', grade: 'Compatible' },
      { host: 'codebuddy-cli', trigger: '/super-dev', protocol: 'official commands + skills', grade: 'Compatible' },
    ],
  },
  {
    category: 'IDE Hosts',
    items: [
      { host: 'cursor', trigger: '/super-dev', protocol: 'official commands + rules', grade: 'Experimental' },
      { host: 'antigravity', trigger: '/super-dev', protocol: 'official commands + GEMINI.md + workflows', grade: 'Compatible' },
      { host: 'kiro', trigger: 'super-dev:', protocol: 'official project steering + global steering', grade: 'Experimental' },
      { host: 'qoder', trigger: '/super-dev', protocol: 'official commands + rules + skills', grade: 'Experimental' },
      { host: 'trae', trigger: 'super-dev:', protocol: 'official project rules + compatibility skill', grade: 'Compatible' },
      { host: 'codebuddy', trigger: '/super-dev', protocol: 'official commands + skills', grade: 'Experimental' },
      { host: 'windsurf', trigger: '/super-dev', protocol: 'official workflows + skills', grade: 'Experimental' },
    ],
  },
] as const;

const PIPELINE_STEPS = [
  ['01. Research', 'Use the host web tools first to study comparable products, patterns, and differentiation.'],
  ['02. Requirements', 'Expand the raw request with constraints, edge cases, and acceptance criteria.'],
  ['03. PRD + Architecture + UI/UX', 'Generate the three core documents that define the execution baseline.'],
  ['04. User Confirmation Gate', 'Pause and wait for explicit confirmation or revision requests before any coding continues.'],
  ['05. Spec / Tasks', 'Create the proposal and task breakdown only after the docs are approved.'],
  ['06. Frontend First', 'Build the frontend first, verify it runs, and make it reviewable before backend work.'],
  ['07. Backend & Integration', 'Implement APIs, services, and integration until the product works end to end.'],
  ['08. Quality Gate', 'Run UI review, security, performance, architecture, and policy threshold checks.'],
  ['09. Delivery & Rehearsal', 'Produce delivery artifacts, run release rehearsal, and confirm readiness to ship.'],
] as const;

const SLASH_HOSTS = ['claude-code', 'codebuddy', 'codebuddy-cli', 'cursor', 'cursor-cli', 'gemini-cli', 'iflow', 'kiro-cli', 'opencode', 'qoder', 'qoder-cli', 'windsurf', 'antigravity'] as const;
const TEXT_TRIGGER_HOSTS = ['codex-cli', 'kimi-cli', 'kiro', 'trae'] as const;

const CORE_COMMANDS = [
  {
    title: 'Install & bootstrap',
    code: `pip install -U super-dev\n# or\nuv tool install super-dev\n\n# open the host installer\nsuper-dev`,
    filename: 'Terminal',
  },
  {
    title: 'Host onboarding & repair',
    code: `super-dev onboard --host claude-code --force --yes\nsuper-dev doctor --host trae --repair --force\nsuper-dev detect --json`,
    filename: 'Host Operations',
  },
  {
    title: 'Confirm docs & resume',
    code: `super-dev review docs --status confirmed --comment "core docs approved"\nsuper-dev run --resume`,
    filename: 'Pipeline Gates',
  },
  {
    title: 'Quality, release, update',
    code: `super-dev quality --type all\nsuper-dev release readiness --verify-tests\nsuper-dev update --check\nsuper-dev update`,
    filename: 'Quality & Release',
  },
] as const;

function gradeVariant(grade: string) {
  if (grade === 'Certified') return 'certified';
  if (grade === 'Compatible') return 'compatible';
  return 'experimental';
}

function SectionCard({ id, eyebrow, title, description, children }: { id: string; eyebrow: string; title: string; description: string; children: React.ReactNode; }) {
  return (
    <section id={id} className="scroll-mt-24 rounded-2xl border border-border-default bg-bg-secondary/60 p-6 sm:p-8 lg:p-10">
      <div className="mb-8 max-w-3xl">
        <p className="mb-3 text-xs font-mono uppercase tracking-[0.22em] text-accent-blue">{eyebrow}</p>
        <h2 className="mb-3 text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">{title}</h2>
        <p className="text-base leading-7 text-text-secondary">{description}</p>
      </div>
      {children}
    </section>
  );
}

export default function DocsPageEn() {
  return (
    <>
      <Nav locale="en" />
      <main className="min-h-screen bg-bg-primary pt-14" id="main-content">
        <section className="border-b border-border-muted bg-bg-primary">
          <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:py-20">
            <div className="grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_360px] lg:items-end">
              <div>
                <div className="mb-4 flex flex-wrap items-center gap-2">
                  <Badge variant="version">Documentation</Badge>
                  <Badge variant="certified">v2.0.8</Badge>
                  <Badge variant="compatible">Standalone docs</Badge>
                </div>
                <h1 className="max-w-4xl text-4xl font-bold leading-tight tracking-tight text-text-primary sm:text-5xl">Super Dev Documentation</h1>
                <p className="mt-5 max-w-3xl text-lg leading-8 text-text-secondary">This is not a README mirror. It is the dedicated docs center for installation, host onboarding, trigger syntax, the governed pipeline, local knowledge base usage, quality gates, delivery standards, and operational commands.</p>
              </div>
              <div className="rounded-2xl border border-border-default bg-bg-elevated p-5 glow-blue">
                <div className="mb-4 flex items-center gap-2 text-sm font-medium text-text-primary"><Sparkles size={16} className="text-accent-blue" />Fastest path</div>
                <div className="space-y-3 text-sm text-text-secondary">
                  <div className="rounded-xl border border-border-default bg-bg-secondary p-4"><div className="mb-2 text-xs uppercase tracking-[0.18em] text-text-muted">Install</div><CopyCommand command="pip install -U super-dev" className="w-full" /></div>
                  <div className="rounded-xl border border-border-default bg-bg-secondary p-4"><div className="mb-2 text-xs uppercase tracking-[0.18em] text-text-muted">Bootstrap</div><CodeBlock code="super-dev" filename="Installer" /></div>
                  <div className="rounded-xl border border-border-default bg-bg-secondary p-4"><div className="mb-3 text-xs uppercase tracking-[0.18em] text-text-muted">Trigger</div><div className="space-y-2"><div className="rounded-lg border border-border-default bg-bg-primary px-3 py-2 font-mono text-text-primary">/super-dev your requirement</div><div className="rounded-lg border border-border-default bg-bg-primary px-3 py-2 font-mono text-text-primary">super-dev: your requirement</div></div></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:py-14">
          <div className="grid gap-8 xl:grid-cols-[220px_minmax(0,1fr)_280px]">
            <aside className="hidden xl:block">
              <div className="sticky top-24 rounded-2xl border border-border-default bg-bg-secondary/60 p-4">
                <div className="mb-3 text-xs font-mono uppercase tracking-[0.18em] text-text-muted">Sections</div>
                <nav className="space-y-1">
                  {DOC_SECTIONS.map((section) => {
                    const Icon = section.icon;
                    return (
                      <a key={section.id} href={`#${section.id}`} className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary">
                        <Icon size={15} className="text-accent-blue" />
                        {section.label}
                      </a>
                    );
                  })}
                </nav>
              </div>
            </aside>

            <div className="space-y-8">
              <SectionCard id="overview" eyebrow="Overview" title="Super Dev governs how the host AI builds the project" description="Spec-driven tools mainly standardize what the project should become. Super Dev goes one layer deeper: it standardizes how the host AI should execute the full delivery process, from research and documents to quality gates and release readiness.">
                <div className="grid gap-4 md:grid-cols-3">
                  {[
                    ['The host executes', 'Model reasoning, web search, terminal calls, file edits, and runtime execution.'],
                    ['Super Dev governs', 'Pipeline stages, document confirmation gates, quality rules, delivery contracts, and release standards.'],
                    ['Artifacts stay auditable', 'Docs, state files, quality reports, and delivery outputs make the workflow inspectable and reproducible.'],
                  ].map(([title, body]) => (
                    <div key={title} className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-2 text-base font-semibold text-text-primary">{title}</h3><p className="text-sm leading-7 text-text-secondary">{body}</p></div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard id="quickstart" eyebrow="Quick Start" title="From install to execution in four steps" description="Install the Python CLI, open the host installer, connect the host, and trigger the pipeline inside the host. From there the host should enter the governed Super Dev workflow instead of acting like a generic coding chat.">
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5">
                    <h3 className="mb-4 text-base font-semibold text-text-primary">Standard path</h3>
                    <ol className="space-y-3 text-sm leading-7 text-text-secondary">
                      {['Install super-dev.', 'Run super-dev to enter the host installer.', 'Select one or more hosts and install the required commands, rules, agents, steering, or skills.', 'Open the host and trigger /super-dev ... or super-dev: ... depending on that host.'].map((item, index) => (
                        <li key={item} className="flex gap-3"><span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent-blue/40 bg-accent-blue/10 font-mono text-xs text-accent-blue">{index + 1}</span><span>{item}</span></li>
                      ))}
                    </ol>
                  </div>
                  <CodeBlock filename="Terminal" code={`pip install -U super-dev\n# or\nuv tool install super-dev\n\n# launch the host installer\nsuper-dev\n\n# slash hosts\n/super-dev Build a commercial website\n\n# non-slash hosts\nsuper-dev: Build a commercial website`} />
                </div>
              </SectionCard>

              <SectionCard id="install" eyebrow="Installation" title="pip and uv install Super Dev's Python dependencies, not your host software" description="Installing Super Dev gives you the CLI and the Python dependencies it declares. It does not install Claude Code, Cursor, Trae, Node.js, Docker, databases, login state, or web permissions. Those stay outside the package boundary.">
                <div className="grid gap-4 lg:grid-cols-2">
                  <CodeBlock filename="pip / uv" code={`pip install -U super-dev\n\n# recommended uv path\nuv tool install super-dev\n\n# update later\nsuper-dev update\nsuper-dev update --check`} />
                  <div className="grid gap-4">
                    <div className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-2 text-base font-semibold text-text-primary">Installed automatically</h3><ul className="space-y-2 text-sm leading-7 text-text-secondary">{['Super Dev CLI code', 'Declared Python dependencies', 'Host onboarding, doctor, quality, and release-readiness capabilities'].map((item) => <li key={item} className="flex gap-2"><CheckCircle2 size={16} className="mt-1 text-status-green" />{item}</li>)}</ul></div>
                    <div className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-2 text-base font-semibold text-text-primary">Not installed automatically</h3><ul className="space-y-2 text-sm leading-7 text-text-secondary">{['Claude Code, Cursor, Trae, Gemini CLI, and other hosts', 'Node.js, Docker, database services, or system-level runtime tools', 'Account logins, browsing permissions, or host-specific capabilities'].map((item) => <li key={item} className="flex gap-2"><ChevronRight size={16} className="mt-1 text-text-muted" />{item}</li>)}</ul></div>
                  </div>
                </div>
              </SectionCard>

              <SectionCard id="hosts" eyebrow="Host Matrix" title="Every host has its own official protocol surface" description="Do not model hosts as one generic integration shape. Some rely on commands, some on AGENTS, some on steering, some on subagents, and some on a host-level or compatibility skill. The install flow exists to write the right surfaces automatically.">
                <div className="space-y-6">
                  {HOST_PROTOCOLS.map((group) => (
                    <div key={group.category} className="rounded-xl border border-border-default bg-bg-elevated p-5"><div className="mb-4 flex items-center justify-between gap-3"><h3 className="text-base font-semibold text-text-primary">{group.category}</h3><Badge variant="version">{group.items.length}</Badge></div><div className="overflow-x-auto"><table className="min-w-full border-collapse text-sm"><thead><tr className="border-b border-border-default text-left text-text-muted"><th className="pb-3 pr-4 font-medium">Host</th><th className="pb-3 pr-4 font-medium">Trigger</th><th className="pb-3 pr-4 font-medium">Protocol</th><th className="pb-3 font-medium">Status</th></tr></thead><tbody>{group.items.map((item) => <tr key={item.host} className="border-b border-border-muted/60 align-top last:border-b-0"><td className="py-3 pr-4 font-mono text-text-primary">{item.host}</td><td className="py-3 pr-4 font-mono text-accent-blue">{item.trigger}</td><td className="py-3 pr-4 text-text-secondary">{item.protocol}</td><td className="py-3"><Badge variant={gradeVariant(item.grade)}>{item.grade}</Badge></td></tr>)}</tbody></table></div></div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard id="triggers" eyebrow="Trigger Model" title="There are only two trigger syntaxes: slash and text trigger" description="Documentation, install output, doctor/detect output, and the website should all present the same final answer. That consistency matters more than having more trigger variants.">
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5"><div className="mb-3 flex items-center gap-2"><Badge variant="certified">Slash</Badge><span className="text-sm text-text-muted">Enter /super-dev ...</span></div><div className="mb-4 rounded-lg border border-border-default bg-bg-primary px-4 py-3 font-mono text-sm text-text-primary">/super-dev your requirement</div><div className="flex flex-wrap gap-2">{SLASH_HOSTS.map((host) => <Badge key={host} variant="default" className="font-mono">{host}</Badge>)}</div></div>
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5"><div className="mb-3 flex items-center gap-2"><Badge variant="compatible">Text Trigger</Badge><span className="text-sm text-text-muted">Enter super-dev: ...</span></div><div className="mb-4 rounded-lg border border-border-default bg-bg-primary px-4 py-3 font-mono text-sm text-text-primary">super-dev: your requirement</div><div className="flex flex-wrap gap-2">{TEXT_TRIGGER_HOSTS.map((host) => <Badge key={host} variant="default" className="font-mono">{host}</Badge>)}</div></div>
                </div>
              </SectionCard>

              <SectionCard id="pipeline" eyebrow="Pipeline" title="The real product is the governed pipeline, not the slash command itself" description="The command is only the entry point. The value sits in the enforced workflow behind it: research-first, document-first, explicit confirmation, frontend-first verification, backend completion, quality gates, and release readiness.">
                <div className="grid gap-4 lg:grid-cols-2">{PIPELINE_STEPS.map(([title, detail], index) => <div key={title} className="rounded-xl border border-border-default bg-bg-elevated p-5"><div className="mb-2 flex items-center gap-3"><span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-accent-blue/40 bg-accent-blue/10 font-mono text-xs text-accent-blue">{index + 1}</span><h3 className="text-base font-semibold text-text-primary">{title}</h3></div><p className="text-sm leading-7 text-text-secondary">{detail}</p></div>)}</div>
              </SectionCard>

              <SectionCard id="knowledge" eyebrow="Knowledge Base" title="The local knowledge base is a pipeline input, not an optional appendix" description="When knowledge/ and output/knowledge-cache/*-knowledge-bundle.json exist, the host should read them first and carry the matched baselines, anti-patterns, and checklists into research, the three core docs, spec, implementation, and quality gates.">
                <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
                  <CodeBlock filename="Knowledge Layout" code={`knowledge/\n  design/\n  development/\n  security/\n  testing/\n  cicd/\n\noutput/knowledge-cache/\n  <project>-knowledge-bundle.json`} />
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-3 text-base font-semibold text-text-primary">Phase mapping</h3><ul className="space-y-2 text-sm leading-7 text-text-secondary">{['Research: read local knowledge before external web study.', 'PRD: favor product, business, and process knowledge.', 'Architecture: favor architecture, development, security, and data baselines.', 'UI/UX: favor design systems and anti-pattern libraries.', 'Quality & delivery: favor testing, CI/CD, release, and incident knowledge.'].map((item) => <li key={item} className="flex gap-2"><Search size={16} className="mt-1 text-accent-blue" />{item}</li>)}</ul></div>
                </div>
              </SectionCard>

              <SectionCard id="quality" eyebrow="Quality & Delivery" title="A project is not done when code exists. It is done when gates pass." description="Super Dev drives explicit evidence through runtime verification, UI review, red-team review, delivery packaging, release rehearsal, and release readiness. Completion is tied to those outcomes, not just to the existence of source files.">
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{[['Document confirmation', 'The three core docs must be approved before Spec and coding continue.'], ['Frontend runtime verification', 'A frontend runtime report must pass before backend work and later stages can proceed.'], ['Quality gate', 'UI review, red-team checks, security, performance, architecture, and policy thresholds all matter.'], ['Delivery & rehearsal', 'Delivery package ready, rehearsal passed, and release readiness green is the real finish line.']].map(([title, body]) => <div key={title} className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-2 text-base font-semibold text-text-primary">{title}</h3><p className="text-sm leading-7 text-text-secondary">{body}</p></div>)}</div>
              </SectionCard>

              <SectionCard id="commands" eyebrow="Commands" title="Keep the important commands visible and copyable" description="Most users do not need the full CLI reference. They need the few commands that move a real project from install, to onboarding, to confirmation, to quality, to release.">
                <div className="grid gap-4 xl:grid-cols-2">{CORE_COMMANDS.map((item) => <div key={item.title} className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-4 text-base font-semibold text-text-primary">{item.title}</h3><CodeBlock code={item.code} filename={item.filename} /></div>)}</div>
              </SectionCard>

              <SectionCard id="troubleshooting" eyebrow="Troubleshooting" title="Check whether the host loaded the integration surface before blaming the prompt" description="Most “it did not work” problems come from the host not reading commands, rules, AGENTS, steering, or skills—not from the trigger syntax itself. Diagnose the integration surface first, then the session refresh state, then the host capability boundaries.">
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-border-default bg-bg-elevated p-5"><h3 className="mb-3 text-base font-semibold text-text-primary">Recommended order</h3><ol className="space-y-2 text-sm leading-7 text-text-secondary">{['Run super-dev doctor --host <host> --repair --force.', 'Verify that the install flow wrote the project-level and user-level surfaces it reported.', 'Close the host completely, reopen the project, and start a fresh conversation.', 'Use a smoke prompt first instead of the real requirement.', 'If the host starts coding immediately, the current session likely did not load the rules.'].map((item) => <li key={item} className="flex gap-2"><ChevronRight size={16} className="mt-1 text-text-muted" />{item}</li>)}</ol></div>
                  <CodeBlock filename="Smoke" code={`# slash hosts\n/super-dev "Do not start coding. Reply only with SMOKE_OK and explain that you will do research first, then generate the three core docs, then wait for confirmation."\n\n# non-slash hosts\nsuper-dev: Do not start coding. Reply only with SMOKE_OK and explain that you will do research first, then generate the three core docs, then wait for confirmation.`} />
                </div>
              </SectionCard>
            </div>

            <aside>
              <div className="sticky top-24 space-y-4">
                <div className="rounded-2xl border border-border-default bg-bg-secondary/60 p-5">
                  <div className="mb-3 flex items-center gap-2 text-sm font-medium text-text-primary"><Terminal size={16} className="text-accent-blue" />Quick actions</div>
                  <div className="space-y-3">
                    <CopyCommand command="pip install -U super-dev" className="w-full" />
                    <CopyCommand command="uv tool install super-dev" className="w-full" />
                    <CopyCommand command="super-dev update" className="w-full" />
                  </div>
                </div>
                <div className="rounded-2xl border border-border-default bg-bg-secondary/60 p-5">
                  <div className="mb-3 flex items-center gap-2 text-sm font-medium text-text-primary"><Workflow size={16} className="text-accent-blue" />Doc destinations</div>
                  <div className="space-y-2 text-sm text-text-secondary">
                    <Link href="/en/pricing" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">Pricing<ArrowRight size={14} /></Link>
                    <Link href="/en/changelog" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">Changelog<ArrowRight size={14} /></Link>
                    <a href="https://github.com/shangyankeji/super-dev" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">GitHub<ArrowRight size={14} /></a>
                    <a href="https://pypi.org/project/super-dev/" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between rounded-lg border border-border-default bg-bg-elevated px-3 py-2 hover:border-border-emphasis hover:text-text-primary">PyPI<ArrowRight size={14} /></a>
                  </div>
                </div>
                <div className="rounded-2xl border border-accent-blue/20 bg-accent-blue/5 p-5"><div className="mb-2 text-sm font-medium text-text-primary">Recommended operating model</div><p className="text-sm leading-7 text-text-secondary">Do not make users guess the host protocol. Let the install flow detect the host, write the correct integration surfaces, and then tell the user the single final trigger they should enter.</p></div>
              </div>
            </aside>
          </div>
        </section>
      </main>
      <Footer locale="en" />
    </>
  );
}
