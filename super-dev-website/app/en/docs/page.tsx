import type { Metadata } from 'next';
import { Nav } from '@/components/layout/Nav';
import { Footer } from '@/components/layout/Footer';
import { DocsPageContent } from '@/components/pages/DocsPageContent';

export const metadata: Metadata = {
  title: 'Documentation',
  description:
    'Standalone Super Dev documentation covering installation, host onboarding, trigger syntax, governed pipeline, knowledge base usage, quality gates, and delivery readiness.',
};

export default function DocsPageEn() {
  return (
    <>
      <Nav locale="en" />
      <DocsPageContent locale="en" />
      <Footer locale="en" />
    </>
  );
}
