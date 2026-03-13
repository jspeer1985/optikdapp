'use client';

export const dynamic = 'force-dynamic';

import dynamicImport from 'next/dynamic';

const CreateDappContent = dynamicImport(() => import('./page-content'), {
  ssr: false,
});

export default function CreateDappPage() {
  return <CreateDappContent />;
}
