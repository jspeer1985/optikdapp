'use client';

import React, { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

type AnalyticsSummary = {
  total_revenue: number;
  order_count: number;
  currency: string;
  volume_points: { date: string; amount: number }[];
  top_products: { name: string; revenue: number; orders: number }[];
};

export default function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadSummary = async () => {
      try {
        const data = await api<AnalyticsSummary>('/api/v1/analytics/summary');
        if (mounted) setSummary(data);
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load analytics.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    loadSummary();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="pb-20 px-8 py-10">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">Platform <span className="gradient-text">Analytics</span></h1>
            <p className="text-gray-400">Revenue and conversion performance for your live dapps.</p>
          </div>
          <div className="flex gap-4">
            <Button variant="outline">Export CSV</Button>
            <Button>Generate AI Report</Button>
          </div>
        </div>

        {error && <p className="text-red-400">{error}</p>}

        <div className="glass p-8 rounded-[3rem] border-white/5">
          {loading ? (
            <p className="text-gray-400">Loading analytics...</p>
          ) : !summary || summary.order_count === 0 ? (
            <div className="text-center space-y-4">
              <div className="text-5xl">📊</div>
              <h3 className="text-2xl font-bold text-white">No analytics data yet</h3>
              <p className="text-gray-500">Complete your first sale to populate analytics dashboards.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                <p className="text-xs text-gray-500 uppercase font-bold">Total Revenue</p>
                <p className="text-3xl font-black text-white mt-2">
                  {summary.total_revenue.toFixed(2)} {summary.currency.toUpperCase()}
                </p>
              </div>
              <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                <p className="text-xs text-gray-500 uppercase font-bold">Orders</p>
                <p className="text-3xl font-black text-white mt-2">{summary.order_count}</p>
              </div>
              <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                <p className="text-xs text-gray-500 uppercase font-bold">Average Order</p>
                <p className="text-3xl font-black text-white mt-2">
                  {(summary.total_revenue / summary.order_count).toFixed(2)} {summary.currency.toUpperCase()}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass p-8 rounded-3xl space-y-6">
            <h3 className="text-xl font-bold border-b border-white/5 pb-4 text-white">Revenue Over Time</h3>
            {summary && summary.volume_points.length > 0 ? (
              <div className="space-y-3">
                {summary.volume_points.map((point) => (
                  <div key={point.date} className="flex justify-between text-sm text-gray-400">
                    <span>{point.date}</span>
                    <span className="text-white font-bold">{point.amount.toFixed(2)} {summary.currency.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No revenue points available.</p>
            )}
          </div>

          <div className="glass p-8 rounded-3xl space-y-6">
            <h3 className="text-xl font-bold border-b border-white/5 pb-4">Top Converting Products</h3>
            {summary && summary.top_products.length > 0 ? (
              <div className="space-y-4">
                {summary.top_products.map((product) => (
                  <div key={product.name} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
                    <span className="font-bold">{product.name}</span>
                    <div className="text-right">
                      <div className="font-black text-emerald-400 text-sm">{product.revenue.toFixed(2)} {summary.currency.toUpperCase()}</div>
                      <div className="text-[10px] text-gray-500">{product.orders} orders</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No product sales yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
