import type { Metadata } from 'next';
import { PricingPageContent } from '@/components/pages/PricingPageContent';

export const metadata: Metadata = {
  title: '定价',
  description: 'Super Dev CLI 工具完全开源免费（MIT）。企业级支持欢迎联系。',
};

export default function PricingPage() {
  return <PricingPageContent locale="zh" />;
}
