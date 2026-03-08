import type { Metadata } from 'next';
import { PricingPageContent } from '@/components/pages/PricingPageContent';

export const metadata: Metadata = {
  title: 'Pricing',
  description: 'Super Dev is fully open source under MIT. Enterprise support is available separately.',
};

export default function PricingPageEn() {
  return <PricingPageContent locale="en" />;
}
