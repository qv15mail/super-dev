import type { Metadata } from 'next';
import { ShowcasePageContent } from '@/components/pages/ShowcasePageContent';

export const metadata: Metadata = {
  title: 'Showcase',
  description: 'Real projects delivered with the Super Dev pipeline',
};

export default function ShowcasePage() {
  return <ShowcasePageContent locale="en" />;
}
