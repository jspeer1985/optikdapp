'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { LAMPORTS_PER_SOL, PublicKey, SystemProgram, Transaction } from '@solana/web3.js';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

type DappStore = {
  name: string;
  url: string;
  platform: string;
  currency: string;
  merchant_wallet?: string;
  merchant_id?: string;
};

type DappProduct = {
  id: string;
  title: string;
  description?: string;
  price: number;
  currency: string;
  price_sol: number;
  image_url?: string;
};

type DappResponse = {
  job_id: string;
  store: DappStore;
  products: DappProduct[];
};

export default function DappView() {
  const params = useParams();
  const dappId = useMemo(() => String(params.id || ''), [params.id]);
  const { connection } = useConnection();
  const { publicKey, sendTransaction } = useWallet();
  const [data, setData] = useState<DappResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchDapp = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api<DappResponse>(`/api/v1/dapps/${dappId}`);
        if (mounted) setData(response);
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load storefront');
      } finally {
        if (mounted) setLoading(false);
      }
    };

    if (dappId) {
      fetchDapp();
    }
    return () => {
      mounted = false;
    };
  }, [dappId]);

  const handleSolanaPay = async (product: DappProduct) => {
    if (!data) return;
    if (!publicKey) {
      setError('Connect a wallet to continue');
      return;
    }

    setProcessing(true);
    setError(null);
    try {
      const destination = new PublicKey(
        data.store.merchant_wallet || process.env.NEXT_PUBLIC_PLATFORM_WALLET || ''
      );
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
      const signature = await sendTransaction(transaction, connection);
      await connection.confirmTransaction(signature, 'confirmed');
    } catch (err: any) {
      setError(err.message || 'Solana payment failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleStripeCheckout = async (product: DappProduct) => {
    if (!data) return;
    setProcessing(true);
    setError(null);

    try {
      const { checkout_url } = await api<{ checkout_url?: string }>('/api/v1/payments/dapp-payment', {
        method: 'POST',
        body: JSON.stringify({
          amount_cents: Math.round(product.price * 100),
          currency: product.currency.toLowerCase(),
          merchant_id: data.store.merchant_id,
          product_name: product.title,
          order_id: `order_${data.job_id}_${product.id}`,
          success_url: window.location.origin + `/dapps/${data.job_id}?status=success`,
          cancel_url: window.location.origin + `/dapps/${data.job_id}?status=cancelled`,
        }),
      });
      if (checkout_url) {
        window.location.href = checkout_url;
      } else {
        throw new Error('Stripe checkout URL missing');
      }
    } catch (err: any) {
      setError(err.message || 'Card payment failed');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-32 pb-20 bg-black text-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-400">Loading storefront...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen pt-32 pb-20 bg-black text-white flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <h1 className="text-3xl font-black">Storefront unavailable</h1>
          <p className="text-gray-400">{error || 'The requested dapp could not be found.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-32 pb-20 bg-black text-white">
      <div className="container mx-auto px-4 max-w-6xl space-y-10">
        <div className="flex flex-col md:flex-row justify-between items-end gap-6">
          <div>
            <div className="inline-block px-3 py-1 bg-green-500/10 border border-green-500/20 text-green-500 text-xs font-bold rounded-full mb-4">
              LIVE ON SOLANA
            </div>
            <h1 className="text-4xl font-black mb-2">{data.store.name}</h1>
            <p className="text-muted-foreground font-mono text-xs opacity-60">
              Store ID: {data.job_id}
            </p>
          </div>
          <WalletMultiButton className="!bg-blue-600 !text-white !rounded-xl !h-10 !px-6 !font-black !text-[10px] !uppercase !tracking-widest" />
        </div>

        {error && (
          <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-200">
            {error}
          </div>
        )}

        {data.products.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
            <p className="text-gray-400">No products available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {data.products.map((product) => (
              <Card key={product.id} className="group overflow-hidden border-white/5 bg-white/5 hover:border-primary/50 transition-all duration-500">
                <div className="aspect-square bg-white/5 flex items-center justify-center text-7xl group-hover:scale-110 transition-transform duration-700">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.title} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-sm text-gray-500">No image</span>
                  )}
                </div>
                <div className="p-6 space-y-4">
                  <div>
                    <h3 className="text-xl font-bold mb-2">{product.title}</h3>
                    <p className="text-xs text-gray-500 line-clamp-2">{product.description}</p>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-lg font-black text-primary">{product.price_sol.toFixed(3)} SOL</div>
                    <div className="text-xs text-gray-500">{product.currency} {product.price.toFixed(2)}</div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" className="flex-1" disabled={processing} onClick={() => handleSolanaPay(product)}>
                      Pay SOL
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1" disabled={processing} onClick={() => handleStripeCheckout(product)}>
                      Pay Card
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full border border-white/10 text-sm text-muted-foreground">
            <img src="/optik_bird.svg" alt="Optik" className="w-5 h-5 opacity-50" />
            Powered by <span className="text-white font-bold opacity-100">Optik Platform</span>
          </div>
        </div>
      </div>
    </div>
  );
}
