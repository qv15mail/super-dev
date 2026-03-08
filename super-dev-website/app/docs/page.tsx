import type { Metadata } from 'next';
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { DocsPageContent } from '@/components/pages/DocsPageContent';

export const metadata: Metadata = {
  title: '文档中心',
  description:
    'Super Dev 独立文档中心，覆盖安装方式、宿主矩阵、触发模型、治理流水线、知识库、质量门禁与交付标准。',
};

export default function DocsPage() {
  return (
    <>
      <Nav locale="zh" />
      <DocsPageContent locale="zh" />
      <Footer locale="zh" />
    </>
  );
}
