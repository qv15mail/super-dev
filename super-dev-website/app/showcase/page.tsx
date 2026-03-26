import type { Metadata } from 'next';
import { ShowcasePageContent } from '@/components/pages/ShowcasePageContent';

export const metadata: Metadata = {
  title: '案例展示',
  description: '使用 Super Dev 流水线交付的真实项目案例',
};

export default function ShowcasePage() {
  return <ShowcasePageContent locale="zh" />;
}
