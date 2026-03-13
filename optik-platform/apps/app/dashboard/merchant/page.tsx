'use client';

import dynamic from 'next/dynamic';

const MerchantContent = dynamic(() => import('./page-content'), {
  ssr: false,
  loading: () => <div className="p-8">Loading dashboard...</div>
});

export default function MerchantPage() {
  return <MerchantContent />;
}
