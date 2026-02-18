'use client';

import Link from 'next/link';
import Button from '@/components/ui/Button';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-black text-white pt-28 pb-20">
      <div className="max-w-4xl mx-auto px-6 space-y-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black">Terms of Service</h1>
            <p className="text-gray-400 mt-2">Effective date: {new Date().getFullYear()}</p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">1. Service Scope</h2>
          <p>Optik provides tools to convert Web2 commerce data into Web3-ready storefronts, NFT metadata, and payment workflows. Merchants are responsible for the accuracy of input data and compliance with applicable laws.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">2. Payments & Fees</h2>
          <p>Platform fees are disclosed at checkout and may vary by plan tier. Payment processing is handled by Stripe and Solana networks. Optik does not store card data.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">3. Content & IP</h2>
          <p>Merchants retain ownership of their content. By using Optik, you grant Optik a limited license to process and store data needed to deliver the service.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">4. Acceptable Use</h2>
          <p>Use of the platform for illegal activity, fraud, or infringement is prohibited. Optik may suspend or terminate accounts that violate these terms.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">5. Limitation of Liability</h2>
          <p>Optik is not liable for losses arising from third-party services, blockchain network interruptions, or merchant configuration errors. Services are provided “as is.”</p>
        </section>
      </div>
    </div>
  );
}
