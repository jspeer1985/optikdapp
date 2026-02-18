'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function MerchantDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [merchant, setMerchant] = useState<any>(null);
  const [dapps, setDapps] = useState<any[]>([]);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  
  // Default platform fee percentage
  const fee = merchant?.fee ? `${merchant.fee}%` : '15%';

  // Real-time Ledger Sync
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [merchantRes, statsRes, txRes, dappsRes] = await Promise.all([
          api<any>(`/api/v1/connect/merchant/me`),
          api<any>(`/api/v1/payments/merchant/stats`),
          api<any[]>(`/api/v1/payments/merchant/transactions`),
          api<{ dapps: any[] }>(`/api/v1/dapps`)
        ]);

        setMerchant(merchantRes.merchant || null);
        setData({
          totalRevenue: statsRes.gross_revenue || 0,
          netEarnings: statsRes.net_payouts || 0,
          platformFees: statsRes.platform_fees || 0,
          totalTransactions: statsRes.order_count || 0,
        });
        setTransactions(
          (txRes || []).map((entry: any) => ({
            ...entry,
            amount: (entry.merchant_payout ?? entry.gross_amount ?? 0) / 100,
          }))
        );
        setDapps(dappsRes.dapps || []);
        setLastSync(new Date());
      } catch (err) {
        console.error("Ledger Sync Failed:", err);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchStats();
      const interval = setInterval(fetchStats, 10000);
      return () => clearInterval(interval);
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center space-y-8 max-w-md">
          <div className="text-6xl animate-bounce">🔑</div>
          <h1 className="text-4xl font-black text-white">Merchant Access Restricted</h1>
          <p className="text-gray-400">Sign in to access the Optik Control Center.</p>
          <div className="flex justify-center">
            <Link href="/auth">
              <Button>Sign In</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-400">Loading merchant dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-20 px-4 md:px-8 py-10">
      <div className="max-w-7xl mx-auto space-y-12">

        {/* Dynamic Context Header */}
        <div className="flex items-center justify-between border-b border-white/5 pb-8">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-2xl shadow-inner">📊</div>
            <div>
              <h1 className="text-3xl font-black text-white">Merchant <span className="gradient-text">Overview</span></h1>
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-1">
                System Hub <span className="mx-2 text-white/10">|</span> {(merchant?.tier || 'unassigned').toUpperCase()} Tier <span className="mx-2 text-white/10">|</span> Ledger Verified
              </p>
            </div>
          </div>
          <div className="hidden md:flex gap-4">
            <div className="text-right">
              <p className="text-[10px] text-gray-500 font-black uppercase mb-1">Vault Status</p>
              <p className="text-sm font-bold text-emerald-400">{(merchant?.status || 'pending').toUpperCase()}</p>
            </div>
          </div>
        </div>

        {/* Stats Grid - Live Ledger Data */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: 'Gross Revenue', value: data ? `$${data.totalRevenue.toLocaleString()}` : '$0.00', icon: '💰', trend: 'Active' },
            { label: 'Net Payouts', value: data ? `$${data.netEarnings.toLocaleString()}` : '$0.00', icon: '💎', trend: 'Audit Verified' },
            { label: 'Order Count', value: data?.totalTransactions || '0', icon: '🛒', trend: 'Total Volume' },
            { label: 'Platform Fees', value: data ? `$${data.platformFees.toLocaleString()}` : '$0.00', icon: '🛡️', trend: 'Optik Share' },
          ].map((s, i) => (
            <div key={i} className="glass p-8 rounded-[2.5rem] border-white/5 relative overflow-hidden group hover:border-blue-500/30 transition-all text-left">
              <div className="absolute top-0 right-0 p-6 text-2xl opacity-10 group-hover:opacity-100 transition-opacity">
                {s.icon}
              </div>
              <p className="text-gray-500 text-[10px] font-black uppercase tracking-[.2em] mb-4">{s.label}</p>
              <h2 className="text-3xl font-black text-white mb-2">{s.value}</h2>
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 text-[10px] font-bold px-2 py-0.5 bg-emerald-400/10 rounded-full">{s.trend}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 text-left">

          {/* Main Visualizer & Reporting */}
          <div className="lg:col-span-2 space-y-8">
            <div className="flex justify-between items-center px-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <span className="w-2 h-8 bg-blue-500 rounded-full"></span>
                Instant Settlement Protocol
              </h2>
              <div className="flex gap-2">
                <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-black rounded-full border border-blue-500/20">REAL-TIME PAYOUTS</span>
              </div>
            </div>

            <div className="glass-card rounded-[3.5rem] p-10 border-white/5 space-y-8 shadow-xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div className="space-y-6">
                  <div>
                    <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Settled for Withdrawal</p>
                    <h3 className="text-5xl font-black text-white">
                      {data ? data.netEarnings.toFixed(2) : '0.00'} <span className="text-blue-400">USD</span>
                    </h3>
                    <p className="text-sm text-gray-500 mt-2 font-mono">Funds secured via Stripe Connect</p>
                  </div>
                  <div className="flex gap-4">
                    <Link href="/dashboard/billing/history" className="flex-1">
                      <Button disabled={!data || data.netEarnings === 0} className="w-full py-4 rounded-2xl shadow-xl shadow-blue-500/20">
                        View Payouts
                      </Button>
                    </Link>
                    <Link href="/dashboard/analytics" className="flex-1">
                      <Button variant="outline" className="w-full py-4 rounded-2xl border-white/10">Audit Logs</Button>
                    </Link>
                  </div>
                </div>
                <div className="space-y-6 bg-white/5 p-8 rounded-[2.5rem] border border-white/5">
                  <h4 className="font-bold text-sm flex items-center gap-2 text-white">
                    <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                    Recent Ledger Activity
                  </h4>
                  <div className="space-y-3">
                    {transactions.length > 0 ? (
                      transactions.slice(0, 3).map((tx, i) => (
                        <div key={i} className="flex justify-between items-center text-xs font-mono">
                          <span className="text-gray-500">{tx.id}</span>
                          <div className="flex gap-3">
                            <span className="text-emerald-400">+${tx.amount.toFixed(2)}</span>
                            <span className="text-gray-400">Net</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-gray-600 italic">No transactions found in ledger.</p>
                    )}
                  </div>
                  <p className="text-[8px] text-gray-600 uppercase font-black text-center pt-2">
                    Ledger sync {lastSync ? lastSync.toLocaleTimeString() : 'pending'}
                  </p>
                </div>
              </div>
            </div>

            {/* Dapp Infrastructure List */}
            <div className="space-y-6">
              <h3 className="text-xl font-bold px-4 text-white">Managed Dapp Fleet</h3>
              <div className="p-6 bg-white/5 rounded-[2.5rem] border border-white/5 divide-y divide-white/5">
                {dapps.length > 0 ? dapps.map((dapp, i) => (
                  <div key={i} className="py-6 flex justify-between items-center first:pt-0 last:pb-0">
                    <div className="flex items-center gap-6">
                      <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center text-xl">🌐</div>
                      <div>
                        <p className="font-bold text-white text-lg">{dapp.store_name || dapp.job_id}</p>
                        <p className="text-xs text-gray-500 font-mono">{dapp.dapp_url || dapp.store_url}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-emerald-400 text-xs font-black uppercase tracking-widest mb-1">{(dapp.status || 'active').toUpperCase()}</p>
                      <p className="text-sm font-bold text-gray-400">{dapp.order_count || 0} Total Sales</p>
                    </div>
                  </div>
                )) : (
                  <div className="py-6 text-center text-sm text-gray-500">No deployed dapps yet.</div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column Intelligence */}
          <div className="space-y-8">
            <section>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold flex items-center gap-3">
                  <span className="w-2 h-8 bg-purple-500 rounded-full"></span>
                  Labor Status
                </h2>
                <span className="text-[10px] text-gray-500 font-bold uppercase">Workforce Running</span>
              </div>
              <div className="glass p-6 rounded-[2.5rem] space-y-4">
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-4">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
                  <div className="flex-1">
                    <p className="text-xs font-bold text-white uppercase tracking-widest">Autonomous Auditor</p>
                    <p className="text-[10px] text-gray-500 truncate">Verifying Ledger Integrity</p>
                  </div>
                </div>
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-4">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
                  <div className="flex-1">
                    <p className="text-xs font-bold text-white uppercase tracking-widest">Logistics Bridge</p>
                    <p className="text-[10px] text-gray-500 truncate">Carrier API Polling Active</p>
                  </div>
                </div>
                <Button variant="outline" className="w-full py-4 rounded-2xl text-xs font-bold mt-2">Scale AI Workforce</Button>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-3 text-white">
                <span className="w-2 h-8 bg-cyan-500 rounded-full"></span>
                Partnership Scope
              </h2>
              <div className="glass p-10 rounded-[2.8rem] space-y-6 bg-gradient-to-br from-cyan-500/5 to-transparent">
                <div className="space-y-4">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Optik Rev Share</span>
                    <span className="font-bold text-blue-400">{fee}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Merchant Margin</span>
                    <span className="font-bold text-emerald-400">{100 - parseInt(fee)}%</span>
                  </div>
                  <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden flex">
                    <div className={`h-full bg-blue-500 ${fee === '3%' ? 'w-[3%]' : fee === '5%' ? 'w-[5%]' : fee === '9%' ? 'w-[9%]' : fee === '12%' ? 'w-[12%]' : fee === '15%' ? 'w-[15%]' : 'w-[15%]'}`}></div>
                    <div className="h-full bg-emerald-500 flex-1"></div>
                  </div>
                </div>
                <div className="p-5 bg-black/40 rounded-2xl border border-white/5 space-y-2">
                  <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Protocol Trust</p>
                  <p className="text-xs text-gray-400 leading-relaxed italic">
                    "Optik settlements are processed on-chain. We never hold your funds. Revenue is split instantly per transaction."
                  </p>
                </div>
              </div>
            </section>

          </div>
        </div>

        {/* Global Control Matrix - Point 10 Strategic Anchor */}
        <section className="pt-16 border-t border-white/5">
          <div className="flex justify-between items-center mb-10 px-4">
            <h2 className="text-3xl font-black text-white">Platform <span className="gradient-text">Categories</span></h2>
            <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest px-4 py-2 bg-white/5 rounded-full border border-white/5">Full System Access</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: 'Inventory', icon: '📦', link: '/dashboard/products', desc: 'Managed SKU Registry' },
              { name: 'Logistics', icon: '🚚', link: '/dashboard/logistics', desc: '3PL & Shipping Bridge' },
              { name: 'Marketing', icon: '📣', link: '/dashboard/marketing', desc: 'Autonomous Growth' },
              { name: 'Security', icon: '🛡️', link: '/dashboard/security', desc: 'Audit & Guardrails' },
            ].map((btn, i) => (
              <Link href={btn.link} key={i}>
                <div className="glass p-8 rounded-[2rem] text-left hover:border-blue-500/30 transition-all cursor-pointer group relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-6 text-4xl opacity-5 group-hover:opacity-20 transition-opacity translate-x-2 -translate-y-2">
                    {btn.icon}
                  </div>
                  <div className="text-3xl mb-4 group-hover:scale-110 transition-transform origin-left">{btn.icon}</div>
                  <div className="text-sm font-black uppercase tracking-widest text-white mb-1">{btn.name}</div>
                  <div className="text-[10px] text-gray-500 font-bold">{btn.desc}</div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
