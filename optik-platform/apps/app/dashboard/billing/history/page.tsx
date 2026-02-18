'use client';

import { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

type Invoice = {
  id: string;
  status: string;
  amount_paid: number;
  currency: string;
  created: number;
  invoice_pdf?: string;
};

export default function BillingHistoryPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadInvoices = async () => {
      if (!user) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await api<{ invoices: Invoice[] }>('/api/v1/payments/invoices');
        if (mounted) {
          setInvoices(data.invoices || []);
        }
      } catch (err: any) {
        if (mounted) {
          setError(err.message || 'Failed to load invoices');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadInvoices();
    return () => {
      mounted = false;
    };
  }, [user]);

  if (!user) {
    return (
      <div className="p-8 text-white">
        <h1 className="text-3xl font-bold mb-4">Billing History</h1>
        <p className="text-gray-400 mb-6">Sign in to view invoice history.</p>
        <Link href="/auth">
          <Button>Sign In</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="p-8 text-white">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Billing History</h1>
        <Link href="/dashboard/billing">
          <Button variant="outline">Back to Billing</Button>
        </Link>
      </div>

      {error && <p className="text-red-400 mb-4">{error}</p>}

      <Card className="bg-gray-900/50 border-gray-800 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-800/50">
            <tr>
              <th className="p-4">Invoice ID</th>
              <th className="p-4">Date</th>
              <th className="p-4">Amount</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {loading ? (
              <tr>
                <td className="p-4 text-gray-400" colSpan={5}>Loading invoices...</td>
              </tr>
            ) : invoices.length === 0 ? (
              <tr>
                <td className="p-4 text-gray-500" colSpan={5}>No invoices available.</td>
              </tr>
            ) : (
              invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-white/5 transition-colors">
                  <td className="p-4 font-mono text-sm">{inv.id}</td>
                  <td className="p-4 text-gray-400">{new Date(inv.created * 1000).toLocaleDateString()}</td>
                  <td className="p-4 font-bold">
                    {(inv.amount_paid / 100).toFixed(2)} {inv.currency.toUpperCase()}
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded text-xs">
                      {inv.status}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    {inv.invoice_pdf ? (
                      <a className="text-blue-400 hover:underline" href={inv.invoice_pdf} target="_blank" rel="noreferrer">
                        Download PDF
                      </a>
                    ) : (
                      <span className="text-gray-500 text-sm">Unavailable</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
