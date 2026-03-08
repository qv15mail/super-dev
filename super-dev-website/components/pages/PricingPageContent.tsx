import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { CheckCircle2, Github } from 'lucide-react';
import { CopyCommand } from '@/components/ui/CopyCommand';
import type { SiteLocale } from '@/lib/site-locale';

const COPY = {
  zh: {
    title: '开源免费，无限制',
    body: 'Super Dev CLI 工具以 MIT 许可证完全开源，个人、团队、商业用途均可免费使用。',
    freeTitle: '开源版', freeSub: 'MIT · 永久免费', recommend: '推荐', enterpriseTitle: '企业咨询', enterpriseSub: '定制化支持', contact: '联系我们', cta: '提交咨询 Issue', footer: 'MIT 许可证意味着你可以在任何项目中自由使用，包括商业项目，无需付费，无需注册。',
    free: ['全部 12 阶段开发流水线','主流 AI 宿主兼容','商业级质量门禁','可审计交付产物','default / balanced 策略预设','宿主检测与兼容性报告','MIT 许可证，无使用限制','源代码完全公开，无黑箱'],
    enterprise: ['优先技术支持','私有化部署协助','团队规范接入咨询','定制化宿主集成','企业交付标准梳理','定制知识库接入'],
  },
  en: {
    title: 'Open source, fully free',
    body: 'Super Dev CLI is released under the MIT license and can be used freely by individuals, teams, and commercial projects.',
    freeTitle: 'Open Source', freeSub: 'MIT · Forever Free', recommend: 'Recommended', enterpriseTitle: 'Enterprise Support', enterpriseSub: 'Custom support', contact: 'Contact Us', cta: 'Open a consultation issue', footer: 'The MIT license means you can use Super Dev in any project, including commercial ones, without fees or registration.',
    free: ['Full 12-stage delivery pipeline','Mainstream AI host compatibility','Commercial-grade quality gates','Auditable delivery outputs','default / balanced policy presets','Host detection and compatibility report','MIT license with no usage restriction','Fully open source, no black box'],
    enterprise: ['Priority technical support','Private deployment assistance','Team governance consulting','Custom host integrations','Enterprise delivery standard alignment','Custom knowledge-base onboarding'],
  },
} as const;

export function PricingPageContent({ locale = 'zh' }: { locale?: SiteLocale }) {
  const copy = COPY[locale];
  return (
    <>
      <Nav locale={locale} />
      <main className="pt-14 min-h-screen" id="main-content">
        <section className="py-20 lg:py-28 bg-bg-primary text-center">
          <div className="max-w-3xl mx-auto px-4 sm:px-6">
            <h1 className="text-4xl sm:text-5xl font-bold text-text-primary mb-4 tracking-tight">{copy.title}</h1>
            <p className="text-lg text-text-secondary mb-10">{copy.body}</p>
          </div>
        </section>
        <section className="pb-24 bg-bg-primary" aria-label="Pricing plans">
          <div className="max-w-4xl mx-auto px-4 sm:px-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-8 rounded-2xl bg-bg-secondary border-2 border-accent-blue/50 relative">
                <div className="absolute -top-3 left-8"><span className="bg-accent-blue text-white text-xs font-bold px-3 py-1 rounded-full">{copy.recommend}</span></div>
                <div className="mb-6"><h2 className="text-xl font-bold text-text-primary mb-1">{copy.freeTitle}</h2><p className="text-text-muted text-sm">{copy.freeSub}</p></div>
                <div className="mb-8"><span className="text-5xl font-bold text-text-primary">¥0</span><span className="text-text-muted ml-2">/mo</span></div>
                <CopyCommand command="pip install super-dev" className="w-full mb-6" />
                <ul className="space-y-3" role="list">{copy.free.map((feature) => <li key={feature} className="flex items-start gap-3 text-sm text-text-secondary"><CheckCircle2 size={16} className="text-status-green shrink-0 mt-0.5" />{feature}</li>)}</ul>
              </div>
              <div className="p-8 rounded-2xl bg-bg-secondary border border-border-default">
                <div className="mb-6"><h2 className="text-xl font-bold text-text-primary mb-1">{copy.enterpriseTitle}</h2><p className="text-text-muted text-sm">{copy.enterpriseSub}</p></div>
                <div className="mb-8"><span className="text-2xl font-bold text-text-primary">{copy.contact}</span></div>
                <a href="https://github.com/shangyankeji/super-dev/issues" target="_blank" rel="noopener noreferrer" className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg mb-6 border border-border-emphasis text-text-primary hover:bg-bg-tertiary transition-colors text-sm font-medium"><Github size={16} />{copy.cta}</a>
                <ul className="space-y-3" role="list">{copy.enterprise.map((feature) => <li key={feature} className="flex items-start gap-3 text-sm text-text-secondary"><CheckCircle2 size={16} className="text-accent-blue shrink-0 mt-0.5" />{feature}</li>)}</ul>
              </div>
            </div>
            <p className="text-center text-sm text-text-muted mt-10">{copy.footer}</p>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </>
  );
}
