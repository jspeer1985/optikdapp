'use client';

import React, { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import Link from 'next/link';
import { api } from '@/lib/api';

type LiquiditySummary = {
  backed_amount: number;
  backed_usd: number;
  apy: number;
  stability_ratio: number;
};

export default function LiquidityBacking() {
  const [summary, setSummary] = useState<LiquiditySummary | null>(null);
  const [amount, setAmount] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadSummary = async () => {
      try {
        const data = await api<LiquiditySummary>('/api/v1/liquidity/summary');
        if (mounted) setSummary(data);
      } catch (err: unknown) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load liquidity data');
      }
    };
    loadSummary();
    return () => {
      mounted = false;
    };
  }, []);

  const handleRequest = async () => {
    const parsed = Number(amount);
    if (!parsed || parsed <= 0) {
      setError('Enter a valid amount.');
      return;
    }
    setError(null);
    setStatus(null);
    try {
      await api('/api/v1/liquidity/request', {
        method: 'POST',
        body: JSON.stringify({ amount_sol: parsed }),
      });
      setStatus('Liquidity backing request submitted.');
      setAmount('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit request.');
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-20 px-8">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">Liquidity & <span className="gradient-text">Backing</span></h1>
            <p className="text-gray-400">Manage the $OPTIK token pairing that underpins your store&apos;s value floor.</p>
          </div>
        </div>

        {status && (
          <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-200 text-sm">
            {status}
          </div>
        )}
        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass p-8 rounded-3xl border-emerald-500/20 bg-emerald-500/5">
            <p className="text-gray-500 text-xs font-black uppercase mb-4">Total Value Backed</p>
            <h2 className="text-4xl font-black text-emerald-400 mb-2">
              {summary ? `${summary.backed_amount.toLocaleString()} $OPTIK` : 'Not configured'}
            </h2>
            <p className="text-xs text-gray-500 font-mono">
              {summary ? `≈ $${summary.backed_usd.toFixed(2)} USD Locked` : 'Connect liquidity source to calculate.'}
            </p>
          </div>

          <div className="glass p-8 rounded-3xl border-white/5">
            <p className="text-gray-500 text-xs font-black uppercase mb-4">Current Yield (APY)</p>
            <h2 className="text-4xl font-black text-blue-400 mb-2">
              {summary ? `${summary.apy.toFixed(2)}%` : 'Unavailable'}
            </h2>
            <p className="text-xs text-gray-400">Automatically compounded to backing.</p>
          </div>

          <div className="glass p-8 rounded-3xl border-white/5">
            <p className="text-gray-500 text-xs font-black uppercase mb-4">Floor Stability</p>
            <h2 className="text-4xl font-black text-white mb-2">
              {summary ? `${Math.round(summary.stability_ratio * 100)}%` : 'Unknown'}
            </h2>
            <p className="text-xs text-emerald-400">Backing coverage across supply.</p>
          </div>
        </div>

        <div className="glass p-12 rounded-[3.5rem] border-blue-500/20">
          <div className="max-w-2xl mx-auto text-center space-y-8">
            <h3 className="text-3xl font-bold">Increase $OPTIK Backing</h3>
            <p className="text-gray-400 leading-relaxed">
              Submit a liquidity request and our team will coordinate funding and on-chain allocation.
            </p>
            <div className="flex gap-4">
              <input
                type="number"
                placeholder="Amount in SOL"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-6 h-16 text-lg outline-none focus:border-blue-500/50 transition-all font-mono"
              />
              <Button className="px-12 h-16 text-lg" onClick={handleRequest}>Request Backing</Button>
            </div>
          </div>
        </div>

        <Link href="/dashboard/merchant" className="text-blue-400 font-bold flex items-center gap-2 hover:gap-3 transition-all pt-8">
          ← Back to Command Center
        </Link>
      </div>
    </div>
  );
}
