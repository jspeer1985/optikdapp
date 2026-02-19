'use client';

import { FormEvent, Suspense, useEffect, useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useRouter, useSearchParams } from 'next/navigation';
import bs58 from 'bs58';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

function parseApiErrorMessage(error: unknown, fallback: string) {
    if (!(error instanceof Error)) return fallback;

    const apiErrorMatch = error.message.match(/^API \d+:\s*([\s\S]+)$/);
    if (!apiErrorMatch) return error.message || fallback;

    const payload = apiErrorMatch[1]?.trim();
    if (!payload) return error.message || fallback;

    try {
        const parsed = JSON.parse(payload) as { detail?: string };
        return parsed.detail || error.message || fallback;
    } catch {
        return payload;
    }
}

function AuthPageContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { connected, publicKey, signMessage, connecting } = useWallet();
    const { setUser } = useAuth();
    const [mode, setMode] = useState<'merchant' | 'customer'>('merchant');
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [walletError, setWalletError] = useState<string | null>(null);

    useEffect(() => {
        const token = searchParams.get('token');
        if (!token) return;
        setLoading(true);
        api<{ user: any }>('/api/v1/auth/magic-link/verify', {
            method: 'POST',
            body: JSON.stringify({ token }),
        }).then((res) => {
            setUser(res.user);
            router.push('/dashboard/merchant');
        }).catch((err) => {
            setStatus(err.message || 'Magic link failed');
        }).finally(() => setLoading(false));
    }, [searchParams, router, setUser]);

    useEffect(() => {
        if (connected) setWalletError(null);
    }, [connected, publicKey]);

    const handleEmailSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setStatus(null);
        try {
            const res = await api<{ verification_url?: string }>('/api/v1/auth/magic-link', {
                method: 'POST',
                body: JSON.stringify({ email }),
            });
            if (res.verification_url) {
                setStatus(`Check your inbox or use: ${res.verification_url}`);
            } else {
                setStatus('Magic link sent. Check your email.');
            }
        } catch (err: any) {
            setStatus(err.message || 'Failed to send magic link');
        } finally {
            setLoading(false);
        }
    };

    const handleWalletLogin = async () => {
        setWalletError(null);
        setStatus(null);
        
        if (connecting) {
            setWalletError('Wallet is still connecting. Please wait a moment and try again.');
            return;
        }

        if (!connected || !publicKey) {
            setWalletError('Wallet not connected. Please connect your wallet first.');
            return;
        }
        
        if (!signMessage) {
            setWalletError('Wallet does not support message signing. Please try a different wallet.');
            return;
        }
        
        setLoading(true);
        try {
            const nonceRes = await api<{ nonce: string; message: string }>('/api/v1/auth/wallet/nonce', {
                method: 'POST',
                body: JSON.stringify({ wallet_address: publicKey.toBase58() }),
            });

            const messageBytes = new TextEncoder().encode(nonceRes.message);
            const signatureBytes = await signMessage(messageBytes);
            const signature = bs58.encode(signatureBytes);

            const verifyRes = await api<{ user: any }>('/api/v1/auth/wallet/verify', {
                method: 'POST',
                body: JSON.stringify({
                    wallet_address: publicKey.toBase58(),
                    signature,
                    nonce: nonceRes.nonce,
                    email: email || undefined,
                }),
            });

            setUser(verifyRes.user);
            
            // Route based on mode
            const redirectPath = mode === 'merchant' ? '/dashboard/merchant' : '/dashboard/customer';
            router.push(redirectPath);
            
        } catch (err: unknown) {
            const errorMessage = parseApiErrorMessage(err, 'Wallet sign-in failed');
            setWalletError(errorMessage);
            setStatus(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen pt-32 pb-20 px-8 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full animate-pulse"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/10 blur-[120px] rounded-full animate-pulse delay-700"></div>
            </div>

            <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
                <div className="hidden lg:block space-y-12">
                    <div className="space-y-6">
                        <div className="w-20 h-2 bg-blue-500 rounded-full"></div>
                        <h1 className="text-6xl font-black text-white leading-tight">
                            One Portal. <br />
                            <span className="gradient-text italic">Total Control.</span>
                        </h1>
                        <p className="text-xl text-gray-400 max-w-md leading-relaxed">
                            Access your autonomous commerce empire or manage your decentralized collections from any device.
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="glass p-6 rounded-3xl border-white/5">
                            <div className="text-2xl mb-2">⚡</div>
                            <h3 className="font-bold text-sm mb-1 uppercase tracking-wider">Fast</h3>
                            <p className="text-xs text-gray-500">Atomic settlements on Solana.</p>
                        </div>
                        <div className="glass p-6 rounded-3xl border-white/5">
                            <div className="text-2xl mb-2">🛡️</div>
                            <h3 className="font-bold text-sm mb-1 uppercase tracking-wider">Secure</h3>
                            <p className="text-xs text-gray-500">Non-custodial infrastructure.</p>
                        </div>
                    </div>
                </div>

                <div className="glass-card p-10 md:p-14 rounded-[3.5rem] border-white/10 shadow-2xl relative">
                    <div className="flex bg-white/5 p-2 rounded-2xl mb-12 border border-white/5">
                        <button
                            onClick={() => setMode('merchant')}
                            className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all ${mode === 'merchant' ? 'bg-primary text-primary-foreground shadow-lg' : 'text-gray-500 hover:text-white'}`}
                        >
                            Merchant Portal
                        </button>
                        <button
                            onClick={() => setMode('customer')}
                            className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all ${mode === 'customer' ? 'bg-primary text-primary-foreground shadow-lg' : 'text-gray-500 hover:text-white'}`}
                        >
                            Customer App
                        </button>
                    </div>

                    {mode === 'merchant' ? (
                        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="text-center space-y-3">
                                <h2 className="text-3xl font-black text-white">Merchant Login</h2>
                                <p className="text-gray-500">Connect your Solana Administrative wallet.</p>
                            </div>

                            <div className="flex justify-center flex-col items-center gap-6">
                                <div className="p-1 rounded-[1.2rem] bg-gradient-to-r from-blue-500 to-emerald-500 shadow-xl shadow-blue-500/20">
                                    <WalletMultiButton className="!bg-slate-900 !rounded-2xl !h-16 !px-10 !text-xl !font-bold hover:!opacity-90 transition-all" />
                                </div>

                                {connected && (
                                    <Button 
                                        type="button"
                                        className="w-full h-16 text-lg font-bold" 
                                        onClick={handleWalletLogin} 
                                        loading={loading}
                                        disabled={!publicKey || !signMessage || connecting}
                                    >
                                        Sign In with Wallet →
                                    </Button>
                                )}
                                
                                {walletError && (
                                    <div className="w-full p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                                        <p className="text-red-400 text-sm text-center">{walletError}</p>
                                    </div>
                                )}
                            </div>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-white/5"></div>
                                </div>
                                <div className="relative flex justify-center text-xs uppercase tracking-widest px-4">
                                    <span className="bg-background text-gray-600 px-4">Admin Authentication</span>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <form onSubmit={handleEmailSubmit} className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="text-center space-y-3">
                                <h2 className="text-3xl font-black text-white">Customer Sign In</h2>
                                <p className="text-gray-500">Track your decentralized orders and NFT collections.</p>
                            </div>

                            <div className="space-y-4">
                                <Input
                                    type="email"
                                    placeholder="your@email.com"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="h-16 bg-white/5 border-white/10 text-lg rounded-2xl"
                                />
                                <Button type="submit" className="w-full h-16 text-lg font-bold" loading={loading}>
                                    Sign In with Magic Link
                                </Button>
                            </div>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-white/5"></div>
                                </div>
                                <div className="relative flex justify-center text-xs uppercase tracking-widest px-4">
                                    <span className="bg-background text-gray-600 px-4">Or Connect Wallet</span>
                                </div>
                            </div>

                            <div className="flex justify-center">
                                <WalletMultiButton className="!bg-white/5 !border !border-white/10 !rounded-2xl !h-14 !px-8 !text-sm !font-bold hover:!bg-white/10 transition-all" />
                            </div>
                            
                            {connected && (
                                <div className="flex justify-center mt-4">
                                    <Button 
                                        type="button"
                                        className="w-full h-14 text-base font-bold" 
                                        onClick={handleWalletLogin} 
                                        loading={loading}
                                        disabled={!publicKey || !signMessage || connecting}
                                    >
                                        Authenticate with Wallet
                                    </Button>
                                </div>
                            )}
                            
                            {walletError && (
                                <div className="w-full p-3 bg-red-500/10 border border-red-500/20 rounded-xl mt-4">
                                    <p className="text-red-400 text-sm text-center">{walletError}</p>
                                </div>
                            )}
                        </form>
                    )}

                    {status && (
                        <div className="mt-6 text-center text-xs text-gray-400">
                            {status}
                        </div>
                    )}

                    <div className="mt-12 text-center">
                        <p className="text-gray-600 text-[10px] uppercase tracking-widest font-bold">
                            Powered by Optik Autonomous Infrastructure
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function AuthPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <AuthPageContent />
        </Suspense>
    );
}
