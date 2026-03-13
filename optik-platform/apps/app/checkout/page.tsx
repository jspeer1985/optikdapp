'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

export default function CheckoutPage() {
    const router = useRouter();
    const [checkoutCancelled, setCheckoutCancelled] = useState(false);
    const [loading, setLoading] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState('elite');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const params = new URLSearchParams(window.location.search);
        setCheckoutCancelled(params.get('cancel') === 'true');
    }, []);

    const tiers = [
        { id: 'basic', name: 'Basic', fee: '3', agents: '1 Agent', perks: 'Essential Tools', color: 'border-slate-800' },
        { id: 'growth', name: 'Growth', fee: '5', agents: '2 Agents', perks: 'Automation Core', color: 'border-blue-900/40' },
        { id: 'global', name: 'Global', fee: '9', agents: '3 Agents', perks: 'Multi-Region Upsell', color: 'border-emerald-900/40' },
        { id: 'scale', name: 'Scale', fee: '12', agents: '4 Agents', perks: 'Security Suite+', color: 'border-purple-900/40' },
        { id: 'elite', name: 'Elite', fee: '15', agents: '6 Agents', perks: 'Full Autonomy', color: 'border-blue-500' },
    ];

    const handleCheckout = async () => {
        setLoading(true);
        setError(null);
        const plan = tiers.find(t => t.id === selectedPlan);
        const fee = plan?.fee || '0';
        const successPath = `/create-dapp?tier=${encodeURIComponent(selectedPlan)}&fee=${encodeURIComponent(`${fee}%`)}&checkout=success`;
        try {
            const data = await api<{ checkout_url?: string }>('/api/v1/payments/checkout', {
                method: 'POST',
                body: JSON.stringify({
                    plan_id: selectedPlan,
                    success_url: `${window.location.origin}${successPath}`,
                    cancel_url: `${window.location.origin}/checkout?cancel=true`,
                }),
            });
            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else {
                // Development fallback for environments without hosted checkout.
                router.push(successPath);
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Unable to start checkout. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen pt-32 pb-20 px-4 bg-transparent">
            <div className="max-w-7xl mx-auto space-y-16">

                {/* Value Prop Header */}
                <div className="text-center space-y-6 max-w-3xl mx-auto">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-[10px] font-black uppercase tracking-widest">
                        Zero Upfront Costs • Pay as you Grow
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black text-white leading-tight">
                        Choose your <span className="gradient-text italic">Partnership</span>
                    </h1>
                    <p className="text-gray-400 text-lg leading-relaxed">
                        Optik doesn&apos;t charge subscription fees. We succeed when you succeed. Select an AI labor tier based on your required workforce.
                    </p>
                    {checkoutCancelled && (
                        <p className="text-sm text-amber-400">Checkout canceled. Choose a plan to continue.</p>
                    )}
                    {error && (
                        <p className="text-sm text-red-400">{error}</p>
                    )}
                </div>

                {/* Pricing Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
                    {tiers.map((tier) => (
                        <div
                            key={tier.id}
                            onClick={() => setSelectedPlan(tier.id)}
                            className={`relative p-8 rounded-[2.5rem] border-2 transition-all cursor-pointer group flex flex-col justify-between ${selectedPlan === tier.id
                                ? 'bg-blue-500/5 border-blue-500 scale-105 shadow-[0_0_50px_rgba(59,130,246,0.15)]'
                                : 'bg-white/5 border-white/5 grayscale opacity-60 hover:grayscale-0 hover:opacity-100 hover:border-white/20'
                                }`}
                        >
                            <div className="space-y-4">
                                <h3 className="text-xl font-bold text-white">{tier.name}</h3>
                                <div className="space-y-1">
                                    <div className="text-4xl font-black text-white">{tier.fee}%</div>
                                    <div className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Revenue Share</div>
                                </div>
                                <div className="pt-6 border-t border-white/5 space-y-3">
                                    <div className="flex items-center gap-2 text-sm font-bold text-blue-400">
                                        <span>🤖</span> {tier.agents}
                                    </div>
                                    <div className="text-xs text-gray-400">{tier.perks}</div>
                                </div>
                            </div>

                            <div className={`mt-8 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${selectedPlan === tier.id ? 'border-blue-500 bg-blue-500' : 'border-white/10'
                                }`}>
                                {selectedPlan === tier.id && <span className="text-xs text-white">✓</span>}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Settlement Proof & Call to Action */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center pt-20">
                    <div className="space-y-8 text-left">
                        <div className="space-y-4">
                            <h2 className="text-3xl font-bold text-white">Trust is Built into the <span className="text-blue-500">Protocol</span></h2>
                            <p className="text-gray-400 leading-relaxed">
                                Every transaction on your Dapp is split automatically at the smart contract level. No manual billing, no hidden fees, and absolute transparency on the Solana ledger.
                            </p>
                        </div>
                        <div className="grid grid-cols-2 gap-6">
                            {[
                                { label: 'Instant Settlement', desc: 'Fees routed in real-time' },
                                { label: 'Audit Ready', desc: 'Full on-chain history' },
                            ].map((item, i) => (
                                <div key={i} className="p-4 bg-white/5 rounded-2xl border border-white/5">
                                    <div className="font-bold text-white text-sm mb-1">{item.label}</div>
                                    <div className="text-xs text-gray-500">{item.desc}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="glass p-12 rounded-[3.5rem] border-blue-500/20 text-center space-y-8">
                        <div className="space-y-2">
                            <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest">Configuration Ready</p>
                            <h3 className="text-3xl font-bold text-white capitalize">{selectedPlan} Partnership</h3>
                        </div>

                        <Button
                            onClick={handleCheckout}
                            disabled={loading}
                            className="w-full py-6 rounded-3xl text-xl font-black bg-blue-500 hover:bg-blue-400 shadow-2xl shadow-blue-500/30 transition-all hover:-translate-y-1"
                        >
                            {loading ? 'Securing Protocol...' : 'Confirm & Start Onboarding'}
                        </Button>

                        <div className="flex justify-center gap-6 text-[10px] font-bold text-gray-600 uppercase tracking-widest">
                            <span>Admin Wallet Required</span>
                            <span>•</span>
                            <span>Audit Verified</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
