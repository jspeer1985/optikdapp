'use client';

import React, { useEffect, useMemo, useState, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { LAMPORTS_PER_SOL, PublicKey, SystemProgram, Transaction } from '@solana/web3.js';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

type PreviewStore = {
  name: string;
  url: string;
  platform: string;
  currency: string;
  merchant_id?: string;
  merchant_wallet?: string;
};

type PreviewProduct = {
  id: string;
  title: string;
  description?: string;
  price: number;
  currency: string;
  price_sol: number;
  image_url?: string;
  metadata_url?: string;
};

type PreviewResponse = {
  job_id: string;
  status: string;
  store: PreviewStore;
  products: PreviewProduct[];
};

type JobSummary = {
  id: string;
  status: string;
  store_url?: string;
  platform?: string;
  created_at?: string;
};

function StorefrontPreviewContent() {
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { connection } = useConnection();
  const { publicKey, sendTransaction } = useWallet();
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const jobId = useMemo(() => {
    return (
      searchParams.get('job') ||
      searchParams.get('jobId') ||
      searchParams.get('job_id') ||
      ''
    );
  }, [searchParams]);
  const checkoutStatus = useMemo(() => searchParams.get('status') || '', [searchParams]);

  useEffect(() => {
    if (checkoutStatus === 'success') {
      setError(null);
      setStatusMessage('Card payment completed successfully.');
      return;
    }
    if (checkoutStatus === 'cancelled') {
      setStatusMessage('Card checkout was canceled. You can try again.');
    }
  }, [checkoutStatus]);

  useEffect(() => {
    let isMounted = true;

    const fetchPreview = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        if (jobId) {
          const data = await api<PreviewResponse>(`/api/v1/convert/preview/${jobId}`);
          if (isMounted) {
            setPreview(data);
            setJobs([]);
          }
        } else {
          const data = await api<{ jobs: JobSummary[] }>('/api/v1/convert');
          if (isMounted) {
            setJobs(data.jobs || []);
            setPreview(null);
          }
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load preview data');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchPreview();
    return () => {
      isMounted = false;
    };
  }, [jobId, user]);

  const handleStripeCheckout = async (product: PreviewProduct) => {
    if (!preview) return;
    setProcessing(true);
    setError(null);
    setStatusMessage(null);

    try {
      const { checkout_url } = await api<{ checkout_url?: string }>('/api/v1/payments/dapp-payment', {
        method: 'POST',
        body: JSON.stringify({
          amount_cents: Math.round(product.price * 100),
          currency: product.currency.toLowerCase(),
          merchant_id: preview.store.merchant_id,
          product_name: product.title,
          order_id: `order_${preview.job_id}_${product.id}`,
          success_url: window.location.origin + `/store-preview?job_id=${preview.job_id}&status=success`,
          cancel_url: window.location.origin + `/store-preview?job_id=${preview.job_id}&status=cancelled`,
        }),
      });

      if (checkout_url) {
        window.location.href = checkout_url;
      } else {
        throw new Error('Stripe checkout URL missing');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start Stripe checkout');
    } finally {
      setProcessing(false);
    }
  };

  const handleSolanaPay = async (product: PreviewProduct) => {
    if (!preview) return;
    if (!publicKey) {
      setError('Connect a wallet to continue');
      return;
    }

    setProcessing(true);
    setError(null);
    setStatusMessage('Preparing transaction...');

    try {
      const destinationAddress = preview.store.merchant_wallet || process.env.NEXT_PUBLIC_PLATFORM_WALLET;
      if (!destinationAddress) {
        throw new Error('Merchant wallet is not configured. Please use card payment or contact support.');
      }
      const destination = new PublicKey(destinationAddress);
      const lamports = Math.round(product.price_sol * LAMPORTS_PER_SOL);
      if (!lamports || lamports <= 0) {
        throw new Error('Invalid SOL price');
      }

      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: publicKey,
          toPubkey: destination,
          lamports,
        })
      );

      setStatusMessage('Confirm transaction in your wallet...');
      const signature = await sendTransaction(transaction, connection);
      setStatusMessage('Confirming on-chain...');
      await connection.confirmTransaction(signature, 'confirmed');

      setStatusMessage('Payment confirmed on-chain');
    } catch (err: any) {
      setError(err.message || 'Solana payment failed');
      setStatusMessage(null);
    } finally {
      setProcessing(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white px-6">
        <div className="max-w-md text-center space-y-6">
          <h1 className="text-3xl font-black">Sign in to view store previews</h1>
          <p className="text-gray-400">Authenticate to access conversion previews and live Dapp storefronts.</p>
          <Link href="/auth">
            <Button>Sign In</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-400">Loading preview...</p>
        </div>
      </div>
    );
  }

  if (!preview) {
    return (
      <div className="min-h-screen bg-black text-white px-6 py-24">
        <div className="max-w-4xl mx-auto space-y-10">
          <div>
            <h1 className="text-4xl font-black">Select a conversion to preview</h1>
            <p className="text-gray-400 mt-3">Choose a recent conversion to view its storefront and product catalog.</p>
          </div>
          {error && <p className="text-red-400">{error}</p>}
          {jobs.length === 0 ? (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
              <p className="text-gray-400">No conversions found yet.</p>
              <Link href="/create-dapp" className="text-blue-400 font-bold mt-4 inline-block">
                Start a conversion
              </Link>
            </div>
          ) : (
            <div className="grid gap-4">
              {jobs.map((job) => (
                <Link
                  key={job.id}
                  href={`/store-preview?job_id=${job.id}`}
                  className="border border-white/10 rounded-2xl p-5 bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-widest text-gray-500">{job.platform || 'Store'}</p>
                      <p className="text-lg font-bold text-white">{job.store_url || job.id}</p>
                    </div>
                    <span className="text-xs font-bold uppercase text-emerald-400">
                      {job.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  const heroProduct = preview.products[0];

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <nav className="h-24 border-b border-white/5 backdrop-blur-md bg-black/50 fixed top-0 w-full z-50 flex items-center justify-between px-10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg shadow-white/20 relative group">
            <div className="absolute inset-0 bg-blue-400/30 rounded-full blur opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <img src="/optik_bird.svg" alt="Optik" className="w-9 h-9 relative z-10" />
          </div>
          <span className="text-xl font-bold tracking-tighter">
            {preview.store.name} <span className="text-blue-500">PREVIEW</span>
          </span>
        </div>
        <div className="flex items-center gap-10">
          <div className="hidden md:flex gap-8 text-[11px] font-black tracking-widest uppercase">
            <Link href="/drops" className="hover:text-blue-500 transition-colors">Drops</Link>
            <Link href="/whitepaper" className="hover:text-blue-500 transition-colors">Manifesto</Link>
            <Link href="/verify" className="hover:text-blue-500 transition-colors">Verify</Link>
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-20 px-4 md:px-12 max-w-[1400px] mx-auto space-y-16">
        {error && (
          <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-200">
            {error}
          </div>
        )}
        {statusMessage && (
          <div className="rounded-2xl border border-blue-500/40 bg-blue-500/10 p-4 text-blue-200">
            {statusMessage}
          </div>
        )}

        {heroProduct ? (
          <section className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            <div className="relative group">
              <div className="aspect-[4/5] bg-gradient-to-br from-slate-900 via-blue-900/20 to-slate-900 rounded-[3rem] border border-white/10 flex items-center justify-center overflow-hidden shadow-2xl">
                {heroProduct.image_url ? (
                  <img
                    src={heroProduct.image_url}
                    alt={heroProduct.title}
                    className="absolute inset-0 w-full h-full object-cover opacity-70"
                  />
                ) : (
                  <div className="z-10 text-center space-y-4">
                    <span className="px-4 py-2 bg-blue-500/20 backdrop-blur-md border border-blue-500/30 rounded-full text-[10px] font-black uppercase tracking-widest text-blue-400">No Image</span>
                    <h4 className="text-2xl font-black italic">IMAGE UNAVAILABLE</h4>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-10">
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <span className="text-xs font-mono text-emerald-400">STATUS: READY</span>
                  <div className="h-px bg-white/5 flex-1"></div>
                </div>
                <h1 className="text-5xl md:text-6xl font-black leading-tight">{heroProduct.title}</h1>
                <div className="flex items-baseline gap-4">
                  <span className="text-4xl font-black">{heroProduct.price_sol.toFixed(3)} SOL</span>
                  <span className="text-gray-500 font-bold">
                    / {heroProduct.currency} {heroProduct.price.toFixed(2)}
                  </span>
                </div>
              </div>

              <p className="text-gray-400 leading-relaxed text-lg">
                {heroProduct.description || 'No product description available yet.'}
              </p>

              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => handleSolanaPay(heroProduct)}
                  disabled={processing}
                  className={`py-4 rounded-3xl font-black text-sm transition-all ${processing ? 'bg-blue-700' : 'bg-blue-500 hover:bg-blue-400 shadow-2xl shadow-blue-500/20'}`}
                >
                  Pay with SOL
                </button>
                <button
                  onClick={() => handleStripeCheckout(heroProduct)}
                  disabled={processing}
                  className={`py-4 rounded-3xl font-black text-sm transition-all ${processing ? 'bg-white/40 text-black' : 'bg-white text-black hover:bg-gray-200 shadow-2xl shadow-white/10'}`}
                >
                  Pay with Card
                </button>
              </div>
            </div>
          </section>
        ) : (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
            <p className="text-gray-400">No products available in this preview.</p>
          </div>
        )}

        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Full Catalog</h2>
            <Link href={`/dapps/${preview.job_id}`} className="text-blue-400 font-bold text-sm">View live storefront →</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {preview.products.map((product) => (
              <div key={product.id} className="rounded-3xl border border-white/10 bg-white/5 overflow-hidden">
                <div className="aspect-square bg-white/5 flex items-center justify-center">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.title} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-xs text-gray-500">No image</span>
                  )}
                </div>
                <div className="p-6 space-y-3">
                  <h3 className="text-lg font-bold">{product.title}</h3>
                  <p className="text-xs text-gray-500 line-clamp-2">{product.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{product.price_sol.toFixed(3)} SOL</span>
                    <span className="text-gray-500">{product.currency} {product.price.toFixed(2)}</span>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={() => handleSolanaPay(product)} disabled={processing} className="flex-1 text-xs">
                      Pay SOL
                    </Button>
                    <Button onClick={() => handleStripeCheckout(product)} disabled={processing} variant="outline" className="flex-1 text-xs">
                      Pay Card
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="py-16 border-t border-white/5 mt-24 text-center space-y-4">
        <div className="text-[10px] font-black tracking-[.3em] text-gray-500 uppercase">
          Powered by Optik Autonomous Commerce
        </div>
        <div className="flex justify-center gap-8 text-xs font-bold text-gray-600">
          <Link href="/terms" className="hover:text-white">Terms</Link>
          <Link href="/privacy" className="hover:text-white">Privacy</Link>
          <Link href="/shipping" className="hover:text-white">Shipping</Link>
        </div>
      </footer>
    </div>
  );
}

export default function StorefrontPreview() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <StorefrontPreviewContent />
    </Suspense>
  );
}
