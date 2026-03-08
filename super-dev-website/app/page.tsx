/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：首页
 * 作用：Super Dev 官网首页，完整 Landing Page
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { HeroSection } from '@/components/sections/HeroSection';
import { SocialProofBand } from '@/components/sections/SocialProofBand';
import { ValuePropsSection } from '@/components/sections/ValuePropsSection';
import { PipelineSection } from '@/components/sections/PipelineSection';
import { HostCompatSection } from '@/components/sections/HostCompatSection';
import { CodeDemoSection } from '@/components/sections/CodeDemoSection';
import { FaqSection } from '@/components/sections/FaqSection';
import { BottomCta } from '@/components/sections/BottomCta';

export default function HomePage() {
  return (
    <>
      <Nav />
      <main id="main-content">
        <HeroSection />
        <SocialProofBand />
        <ValuePropsSection />
        <PipelineSection />
        <HostCompatSection />
        <CodeDemoSection />
        <FaqSection />
        <BottomCta />
      </main>
      <Footer />
    </>
  );
}
