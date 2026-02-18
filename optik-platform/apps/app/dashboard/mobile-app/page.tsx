'use client';

import { useState } from 'react';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

export default function MobileAppBuilder() {
    const [platform, setPlatform] = useState<'ios' | 'android' | 'both'>('both');
    const [appName, setAppName] = useState('');
    const [building, setBuilding] = useState(false);
    const [status, setStatus] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleBuild = async () => {
        if (!appName) {
            setError('App name is required.');
            return;
        }
        setBuilding(true);
        setError(null);
        setStatus(null);
        try {
            await api('/api/v1/marketing/mobile-app', {
                method: 'POST',
                body: JSON.stringify({
                    app_name: appName,
                    platform,
                }),
            });
            setStatus('Build request submitted. Our team will follow up with next steps.');
        } catch (err: any) {
            setError(err.message || 'Failed to submit build request.');
        } finally {
            setBuilding(false);
        }
    };

    return (
        <div className="container mx-auto max-w-5xl pb-20">
            <div className="flex justify-between items-end mb-12">
                <div>
                    <h1 className="text-4xl font-black text-white mb-2">Mobile App <span className="gradient-text">Studio</span></h1>
                    <p className="text-gray-400">Convert your decentralized store into a native iOS & Android application.</p>
                </div>
                <div className="bg-green-500/10 px-4 py-2 rounded-full border border-green-500/20 flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-500 text-xs font-bold uppercase tracking-wider">$OPTIK TOKEN LIVE</span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Configurator */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-white/5 backdrop-blur-xl p-8 rounded-3xl border border-white/10">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-2xl">📱</div>
                            <div>
                                <h3 className="text-xl font-bold text-white">App Configuration</h3>
                                <p className="text-sm text-gray-400">We use your existing store schema to generate native code.</p>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">App Name</label>
                                <input
                                    type="text"
                                    value={appName}
                                    onChange={(e) => setAppName(e.target.value)}
                                    placeholder="e.g. My Brand Store"
                                    className="w-full px-4 py-4 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider">Target Platforms</label>
                                <div className="grid grid-cols-3 gap-4">
                                    <button
                                        onClick={() => setPlatform('ios')}
                                        className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition-all ${platform === 'ios' ? 'bg-blue-600 border-blue-500' : 'bg-black/20 border-white/10 hover:bg-white/5'}`}
                                    >
                                        <span className="text-2xl">🍎</span>
                                        <span className="text-xs font-bold text-white">iOS Only</span>
                                    </button>
                                    <button
                                        onClick={() => setPlatform('android')}
                                        className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition-all ${platform === 'android' ? 'bg-blue-600 border-blue-500' : 'bg-black/20 border-white/10 hover:bg-white/5'}`}
                                    >
                                        <span className="text-2xl">🤖</span>
                                        <span className="text-xs font-bold text-white">Android Only</span>
                                    </button>
                                    <button
                                        onClick={() => setPlatform('both')}
                                        className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition-all ${platform === 'both' ? 'bg-blue-600 border-blue-500' : 'bg-black/20 border-white/10 hover:bg-white/5'}`}
                                    >
                                        <span className="text-2xl">Unite</span>
                                        <span className="text-xs font-bold text-white">Both (Best Value)</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                        {status && (
                            <div className="mt-6 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-200 text-sm">
                                {status}
                            </div>
                        )}
                        {error && (
                            <div className="mt-6 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
                                {error}
                            </div>
                        )}
                    </div>

                    {/* Process Explanation */}
                    <div className="bg-black/40 backdrop-blur-xl p-8 rounded-3xl border border-white/10">
                        <h3 className="text-lg font-bold text-white mb-6">How It Works</h3>
                        <div className="space-y-6 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-white/10">
                            <div className="relative pl-12">
                                <div className="absolute left-0 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xs z-10">1</div>
                                <h4 className="text-white font-bold text-sm">Schema Sync</h4>
                                <p className="text-gray-400 text-xs mt-1">We verify your product catalog and user data structure.</p>
                            </div>
                            <div className="relative pl-12">
                                <div className="absolute left-0 top-0 w-8 h-8 bg-black border border-white/20 rounded-full flex items-center justify-center text-white font-bold text-xs z-10">2</div>
                                <h4 className="text-white font-bold text-sm">Code Generation</h4>
                                <p className="text-gray-400 text-xs mt-1">Our engine writes Swift (iOS) and Kotlin (Android) code tailored to your brand.</p>
                            </div>
                            <div className="relative pl-12">
                                <div className="absolute left-0 top-0 w-8 h-8 bg-black border border-white/20 rounded-full flex items-center justify-center text-white font-bold text-xs z-10">3</div>
                                <h4 className="text-white font-bold text-sm">Managed Submission</h4>
                                <p className="text-gray-400 text-xs mt-1">We handle the strict Apple/Google review process. We pay the developer fees directly.</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Pricing & Checkout */}
                <div className="space-y-8">
                    <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 backdrop-blur-xl p-8 rounded-3xl border border-white/10 sticky top-32">
                        <h3 className="text-xl font-bold text-white mb-6">Pricing Summary</h3>

                        <div className="space-y-4 mb-8">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">App Development</span>
                                <span className="text-white font-bold">$399.00</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">Apple Developer Fee</span>
                                <span className="text-green-400 font-bold">INCLUDED</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">Google Play Fee</span>
                                <span className="text-green-400 font-bold">INCLUDED</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-400">Optik Token Discount</span>
                                <span className="text-blue-400 font-bold">- $50.00</span>
                            </div>
                            <div className="border-t border-white/10 pt-4 flex justify-between items-end">
                                <span className="text-gray-400 font-bold">Total One-Time</span>
                                <span className="text-3xl font-black text-white">$349</span>
                            </div>
                        </div>

                        <div className="bg-blue-500/10 p-4 rounded-xl border border-blue-500/20 mb-6">
                            <p className="text-xs text-blue-200 text-center">
                                *We charge you once, then we pay Apple ($99/yr) and Google ($25) on your behalf.
                            </p>
                        </div>

                        <button
                            onClick={handleBuild}
                            disabled={building || !appName}
                            className="w-full py-5 bg-white text-black font-black rounded-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-widest text-sm"
                        >
                            {building ? 'Processing...' : 'Start Build'}
                        </button>

                        <button
                            onClick={async () => {
                                setError(null);
                                try {
                                    const data = await api<{ checkout_url?: string }>('/api/v1/payments/payment-link', {
                                        method: 'POST',
                                        body: JSON.stringify({
                                            amount_cents: 34900,
                                            currency: 'usd',
                                            product_name: `Mobile App Build: ${appName || 'New App'}`,
                                            success_url: window.location.href + '?payment=success',
                                            cancel_url: window.location.href + '?payment=cancelled'
                                        }),
                                    });
                                    if (data.checkout_url) {
                                        window.open(data.checkout_url, '_blank', 'noopener,noreferrer');
                                    } else {
                                        setError('Failed to create payment link. Please try again.');
                                    }
                                } catch (error) {
                                    console.error("Payment error:", error);
                                    setError('Could not connect to payment server.');
                                }
                            }}
                            className="w-full py-4 bg-white/5 text-white font-bold rounded-xl hover:bg-white/10 transition-all border border-white/10 uppercase tracking-widest text-xs mt-3 flex items-center justify-center gap-2 group"
                        >
                            <span>🔗</span> Pay via Payment Link
                        </button>

                        <div className="mt-4 flex items-center justify-center gap-2 opacity-50">
                            <span className="text-xs text-gray-500">Secured by Stripe & Solana</span>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    );
}
