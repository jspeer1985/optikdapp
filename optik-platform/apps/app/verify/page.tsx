'use client';

import { useState } from 'react';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

type VerificationResult = {
  status: string;
  order_id?: string;
  transaction_id?: string;
  merchant_id?: string;
  amount?: number;
  currency?: string;
};

export default function VerifyPage() {
  const [value, setValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    if (!value.trim()) {
      setError('Enter an order ID or transaction ID.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api<VerificationResult>('/api/v1/verify', {
        method: 'POST',
        body: JSON.stringify({ value: value.trim() }),
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Verification failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white pt-28 pb-20 px-6">
      <div className="max-w-3xl mx-auto space-y-10">
        <div>
          <h1 className="text-4xl font-black">Verify Purchase</h1>
          <p className="text-gray-400 mt-2">Validate on-chain or Stripe transactions using a reference ID.</p>
        </div>

        <div className="glass p-8 rounded-3xl border border-white/10 space-y-4">
          <label className="text-xs uppercase tracking-widest text-gray-400 font-bold">Order ID or Transaction Hash</label>
          <input
            className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-blue-500 focus:outline-none"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="e.g. order_123 or pi_..."
          />
          <Button onClick={handleVerify} disabled={loading}>
            {loading ? 'Verifying...' : 'Verify'}
          </Button>
        </div>

        {error && <p className="text-red-400">{error}</p>}
        {result && (
          <div className="glass p-8 rounded-3xl border border-white/10 space-y-3">
            <p className="text-sm text-gray-400 uppercase tracking-widest">Status</p>
            <p className="text-2xl font-black text-emerald-400">{result.status}</p>
            {result.order_id && <p className="text-sm text-gray-400">Order: {result.order_id}</p>}
            {result.transaction_id && <p className="text-sm text-gray-400">Transaction: {result.transaction_id}</p>}
            {result.amount !== undefined && result.currency && (
              <p className="text-sm text-gray-400">Amount: {(result.amount / 100).toFixed(2)} {result.currency.toUpperCase()}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
