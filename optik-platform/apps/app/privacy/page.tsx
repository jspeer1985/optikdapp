'use client';

import Link from 'next/link';
import Button from '@/components/ui/Button';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-black text-white pt-28 pb-20">
      <div className="max-w-4xl mx-auto px-6 space-y-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black">Privacy Policy</h1>
            <p className="text-gray-400 mt-2">Effective date: {new Date().getFullYear()}</p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">1. Data We Collect</h2>
          <p>We collect account details, store metadata, transaction records, and usage analytics required to operate the Optik platform.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">2. How We Use Data</h2>
          <p>Data is used to deliver conversion services, process payments, improve performance, and provide support. We do not sell customer data.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">3. Data Sharing</h2>
          <p>We share data with payment processors, infrastructure providers, and blockchain networks only as required to fulfill the service.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">4. Data Retention</h2>
          <p>We retain data while accounts are active and for a limited period afterward to meet legal, tax, and security requirements.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">5. Your Rights</h2>
          <p>You can request access, correction, or deletion of your data by contacting Optik support.</p>
        </section>
      </div>
    </div>
  );
}
