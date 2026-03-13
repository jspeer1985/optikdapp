'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

type DappListing = {
  job_id: string;
  store_name: string;
  dapp_url?: string;
  platform?: string;
};

export default function DropsPage() {
  const [drops, setDrops] = useState<DappListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadDrops = async () => {
      try {
        const data = await api<{ dapps: DappListing[] }>('/api/v1/dapps/public');
        if (mounted) setDrops(data.dapps || []);
      } catch (err: unknown) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load drops.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    loadDrops();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-transparent text-white pt-28 pb-20">
      <div className="max-w-6xl mx-auto px-6 space-y-10">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black">Live Drops</h1>
            <p className="text-gray-400 mt-2">Browse storefronts deployed on Optik.</p>
          </div>
          <Link href="/create-dapp" className="text-blue-400 font-bold">Launch your store →</Link>
        </div>

        {error && <p className="text-red-400">{error}</p>}

        {loading ? (
          <p className="text-gray-500">Loading drops...</p>
        ) : drops.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-md">
            <p className="text-gray-400">No drops available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {drops.map((drop) => (
              <Link key={drop.job_id} href={`/dapps/${drop.job_id}`} className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-md p-6 hover:bg-white/10 transition-all">
                <p className="text-xs uppercase tracking-widest text-gray-500">{drop.platform || 'store'}</p>
                <h2 className="text-2xl font-bold mt-2">{drop.store_name}</h2>
                <p className="text-sm text-blue-400 mt-3">{drop.dapp_url || 'View storefront'}</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
