'use client';

import Link from 'next/link';
import Button from '@/components/ui/Button';

export default function ShippingPage() {
  return (
    <div className="min-h-screen bg-black text-white pt-28 pb-20">
      <div className="max-w-4xl mx-auto px-6 space-y-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black">Shipping Policy</h1>
            <p className="text-gray-400 mt-2">Merchant-specific fulfillment terms apply.</p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">1. Fulfillment Responsibility</h2>
          <p>Each merchant is responsible for fulfilling physical goods sold through their dapp. Shipping times, carriers, and tracking are managed by the merchant.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">2. Tracking Updates</h2>
          <p>Tracking information is provided by the merchant or their logistics partner. If you have questions about a shipment, contact the store directly.</p>
        </section>

        <section className="space-y-4 text-gray-300">
          <h2 className="text-2xl font-bold text-white">3. Digital Goods</h2>
          <p>NFTs and digital assets are delivered on-chain once payment is confirmed. On-chain delivery timing depends on network confirmation.</p>
        </section>
      </div>
    </div>
  );
}
