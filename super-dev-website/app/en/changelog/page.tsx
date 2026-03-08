import type { Metadata } from 'next';
import { ChangelogPageContent } from '@/components/pages/ChangelogPageContent';

export const metadata: Metadata = {
  title: 'Changelog',
  description: 'Version history for Super Dev',
};

export default function ChangelogPageEn() {
  return <ChangelogPageContent locale="en" />;
}
