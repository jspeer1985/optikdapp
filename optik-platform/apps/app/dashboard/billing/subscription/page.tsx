'use client';

import React, { useEffect, useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';




export default function SubscriptionPage() {
    const [subscriptions, setSubscriptions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        api('/api/v1/payments/subscriptions')
            .then((data) => {
                setSubscriptions(data as any[]);
                setError(null);
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to fetch subscriptions', err);
                setError('Failed to load subscriptions.');
                setLoading(false);
            });
    }, []);

    const handleCancel = async (id: string) => {
        if (!confirm('Are you sure you want to cancel this subscription?')) return;

        try {
            await api(`/api/v1/payments/cancel/${id}`, { method: 'POST' });
            setStatus('Subscription cancelled.');
            setError(null);
            setSubscriptions(subscriptions.map(s => s.id === id ? { ...s, status: 'canceled' } : s));
        } catch (err) {
            setError('Cancellation failed.');
        }
    };

    if (loading) return <div className="p-8 text-white">Loading subscriptions...</div>;

    return (
        <div className="p-8 text-white">
            <h1 className="text-3xl font-bold mb-8">My Subscriptions</h1>
            {status && <p className="text-emerald-400 mb-4">{status}</p>}
            {error && <p className="text-red-400 mb-4">{error}</p>}

            {subscriptions.length === 0 ? (
                <Card className="p-12 text-center bg-gray-900/50 border-gray-800">
                    <p className="text-gray-400 mb-6">You don't have any active subscriptions.</p>
                    <Button onClick={() => window.location.href = '/checkout'}>View Plans</Button>
                </Card>
            ) : (
                <div className="grid gap-6">
                    {subscriptions.map((sub) => (
                        <Card key={sub.id} className="p-6 bg-gray-900/50 border-gray-800 flex justify-between items-center">
                            <div>
                                <h3 className="text-xl font-bold">{sub.plan?.nickname || 'Optik Pro Plan'}</h3>
                                <p className="text-gray-400">Status: <span className={sub.status === 'active' ? 'text-green-500' : 'text-red-500'}>{sub.status}</span></p>
                                <p className="text-sm text-gray-500">Billed: Monthly</p>
                            </div>
                            <div className="text-right">
                                <p className="text-2xl font-bold mb-4">${(sub.plan?.amount / 100).toFixed(2)}</p>
                                {sub.status === 'active' && (
                                    <Button variant="outline" className="border-red-500/50 text-red-400 hover:bg-red-500/10" onClick={() => handleCancel(sub.id)}>
                                        Cancel Subscription
                                    </Button>
                                )}
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
