export const dynamic = 'force-dynamic';

import dynamicImport from 'next/dynamic';

const MerchantContent = dynamicImport(() => import('./page-content'), {
  ssr: false,
});

export default function MerchantPage() {
  return <MerchantContent />;
}
