/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：定价页
 * 作用：展示 Super Dev 开源免费策略和企业咨询入口
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import type { Metadata } from 'next';
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { CheckCircle2, Github } from 'lucide-react';
import { CopyCommand } from '@/components/ui/CopyCommand';

export const metadata: Metadata = {
  title: '定价',
  description: 'Super Dev CLI 工具完全开源免费（MIT）。企业级支持欢迎联系。',
};

const FREE_FEATURES = [
  '全部 12 阶段开发流水线',
  '15+ AI 宿主工具兼容',
  '商业级质量门禁',
  '可审计交付产物（pipeline-contract / delivery manifest）',
  'default / balanced 两档策略预设',
  '宿主检测与兼容性报告',
  'MIT 许可证，无使用限制',
  '源代码完全公开，无黑箱',
] as const;

const ENTERPRISE_FEATURES = [
  'enterprise 策略预设',
  '自定义策略 DSL 配置',
  '优先技术支持',
  '私有化部署协助',
  '团队规范接入咨询',
  '定制化宿主集成',
] as const;

export default function PricingPage() {
  return (
    <>
      <Nav />
      <main className="pt-14 min-h-screen" id="main-content">
        {/* Hero */}
        <section className="py-20 lg:py-28 bg-bg-primary text-center">
          <div className="max-w-3xl mx-auto px-4 sm:px-6">
            <h1 className="text-4xl sm:text-5xl font-bold text-text-primary mb-4 tracking-tight">
              开源免费，无限制
            </h1>
            <p className="text-lg text-text-secondary mb-10">
              Super Dev CLI 工具以 MIT 许可证完全开源，个人、团队、商业用途均可免费使用。
            </p>
          </div>
        </section>

        {/* 定价卡片 */}
        <section className="pb-24 bg-bg-primary" aria-label="定价方案">
          <div className="max-w-4xl mx-auto px-4 sm:px-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* 免费卡片 */}
              <div className="p-8 rounded-2xl bg-bg-secondary border-2 border-accent-blue/50 relative">
                <div className="absolute -top-3 left-8">
                  <span className="bg-accent-blue text-white text-xs font-bold px-3 py-1 rounded-full">
                    推荐
                  </span>
                </div>
                <div className="mb-6">
                  <h2 className="text-xl font-bold text-text-primary mb-1">开源版</h2>
                  <p className="text-text-muted text-sm">MIT · 永久免费</p>
                </div>
                <div className="mb-8">
                  <span className="text-5xl font-bold text-text-primary">¥0</span>
                  <span className="text-text-muted ml-2">/月</span>
                </div>

                <CopyCommand command="pip install super-dev" className="w-full mb-6" />

                <ul className="space-y-3" role="list" aria-label="开源版功能列表">
                  {FREE_FEATURES.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm text-text-secondary">
                      <CheckCircle2 size={16} className="text-status-green shrink-0 mt-0.5" aria-hidden="true" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {/* 企业卡片 */}
              <div className="p-8 rounded-2xl bg-bg-secondary border border-border-default">
                <div className="mb-6">
                  <h2 className="text-xl font-bold text-text-primary mb-1">企业咨询</h2>
                  <p className="text-text-muted text-sm">定制化支持</p>
                </div>
                <div className="mb-8">
                  <span className="text-2xl font-bold text-text-primary">联系我们</span>
                </div>

                <a
                  href="https://github.com/shangyankeji/super-dev/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg mb-6 border border-border-emphasis text-text-primary hover:bg-bg-tertiary transition-colors text-sm font-medium"
                >
                  <Github size={16} aria-hidden="true" />
                  提交咨询 Issue
                </a>

                <ul className="space-y-3" role="list" aria-label="企业版功能列表">
                  {ENTERPRISE_FEATURES.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm text-text-secondary">
                      <CheckCircle2 size={16} className="text-accent-blue shrink-0 mt-0.5" aria-hidden="true" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* 底部说明 */}
            <p className="text-center text-sm text-text-muted mt-10">
              MIT 许可证意味着你可以在任何项目中自由使用，包括商业项目，无需付费，无需注册。
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
