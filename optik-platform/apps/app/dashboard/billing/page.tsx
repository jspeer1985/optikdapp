'use client';

import React, { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import Link from 'next/link';
import { api } from '@/lib/api';

type LedgerEntry = {
  id: string;
  gross_amount: number;
  platform_fee: number;
  merchant_payout: number;
  currency: string;
  status: string;
  created_at?: string;
};

export default function BillingCenter() {
  const [transactions, setTransactions] = useState<LedgerEntry[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [merchant, setMerchant] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadBilling = async () => {
      try {
        const [statsRes, txRes, merchantRes] = await Promise.all([
          api<any>('/api/v1/payments/merchant/stats'),
          api<LedgerEntry[]>('/api/v1/payments/merchant/transactions'),
          api<any>('/api/v1/connect/merchant/me'),
        ]);
        if (mounted) {
          setStats(statsRes);
          setTransactions(txRes || []);
          setMerchant(merchantRes.merchant || null);
        }
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load billing data.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    loadBilling();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="min-h-screen pt-24 pb-20 px-8">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">Billing & <span className="gradient-text">Settlements</span></h1>
            <p className="text-gray-400">View revenue distribution and settlement activity.</p>
          </div>
        </div>

        {error && <p className="text-red-400">{error}</p>}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 glass p-10 rounded-[3rem] border-white/5 space-y-10">
            <section>
              <h2 className="text-2xl font-bold mb-6">Payment History</h2>
              {loading ? (
                <div className="text-gray-500">Loading transactions...</div>
              ) : transactions.length === 0 ? (
                <div className="text-gray-500">No transactions found.</div>
              ) : (
                <div className="space-y-4">
                  {transactions.map((txn) => (
                    <div key={txn.id} className="flex items-center justify-between p-6 bg-white/5 rounded-2xl border border-white/5 hover:bg-white/10 transition-colors">
                      <div>
                        <p className="font-bold text-white">{txn.id}</p>
                        <p className="text-xs text-gray-500">{txn.created_at ? new Date(txn.created_at).toLocaleDateString() : '—'}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-black text-blue-400">{(txn.gross_amount / 100).toFixed(2)} {txn.currency.toUpperCase()}</p>
                        <p className="text-[10px] text-gray-500">Platform Fee: {(txn.platform_fee / 100).toFixed(2)} {txn.currency.toUpperCase()}</p>
                      </div>
                      <div className="text-right px-4">
                        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded-full">{txn.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
            <Link href="/dashboard/billing/history">
              <Button variant="outline" className="w-full">View Detailed Invoice History</Button>
            </Link>
          </div>

          <div className="space-y-8">
            <section className="glass p-8 rounded-[2.5rem] border-blue-500/20 bg-blue-500/5">
              <h3 className="text-xl font-bold mb-6">Current Subscription</h3>
              <div className="space-y-4">
                <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                  <p className="text-blue-400 font-black uppercase text-[10px] tracking-widest mb-1">Active Plan</p>
                  <p className="text-2xl font-black">{merchant?.tier ? merchant.tier.toUpperCase() : 'Not set'}</p>
                  <p className="text-gray-400 text-sm mt-2">
                    Revenue Share: {stats && stats.gross_revenue ? `${((stats.platform_fees / stats.gross_revenue) * 100).toFixed(2)}%` : '—'}
                  </p>
                </div>
                <Link href="/payments">
                  <Button size="sm" variant="outline" className="w-full">Modify Plan</Button>
                </Link>
              </div>
            </section>

            <section className="glass p-8 rounded-[2.5rem] border-white/5">
              <h3 className="text-xl font-bold mb-4">Payout Method</h3>
              <div className="flex items-center gap-4 p-4 bg-white/5 rounded-2xl border border-white/5">
                <div className="text-2xl">⚡</div>
                <div className="flex-1">
                  <p className="font-bold text-sm">Stripe Connect</p>
                  <p className="text-xs text-gray-500">Direct merchant payouts</p>
                </div>
              </div>
              <p className="text-[10px] text-gray-500 mt-4 px-2 italic">
                Funds are settled via Stripe Connect according to your payout schedule.
              </p>
            </section>
          </div>
        </div>

        <Link href="/dashboard/merchant" className="text-blue-400 font-bold flex items-center gap-2 hover:gap-3 transition-all">
          ← Back to Command Center
        </Link>
      </div>
    </div>
  );
}
