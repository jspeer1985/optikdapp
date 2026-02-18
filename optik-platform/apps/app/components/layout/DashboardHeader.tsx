'use client';

import React from 'react';
import Link from 'next/link';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function DashboardHeader() {
    const [dappId, setDappId] = React.useState<string | null>(null);
    const { user } = useAuth();

    React.useEffect(() => {
        let mounted = true;
        const loadLatest = async () => {
            if (!user) {
                setDappId(null);
                return;
            }
            try {
                const response = await api<{ job_id?: string }>('/api/v1/dapps/latest');
                if (mounted) {
                    setDappId(response.job_id || null);
                }
            } catch {
                if (mounted) {
                    setDappId(null);
                }
            }
        };

        loadLatest();
        return () => {
            mounted = false;
        };
    }, [user]);

    return (
        <header className="fixed top-0 w-full z-50 border-b border-white/5 bg-black/40 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-4 md:px-8 h-20 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center group-hover:rotate-12 transition-transform shadow-xl border border-blue-500/20 relative">
                        {/* Subtle glow */}
                        <div className="absolute inset-0 bg-blue-500/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        {/* Optik Bird Logo */}
                        <img
                            src="/optik_bird.svg"
                            alt="Optik"
                            className="w-8 h-8 relative z-10"
                        />
                    </div>
                    <span className="text-xl font-bold tracking-tighter text-white">OPTIK <span className="text-blue-400">ENTERPRISE</span></span>
                </Link>

                <div className="flex items-center gap-6">
                    <Button
                        onClick={() => window.location.href = dappId ? `/dapps/${dappId}` : "/create-dapp?tier=scale"}
                        className="hidden md:block px-5 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-500/20 transition-all"
                    >
                        {dappId ? 'View Live Dapp' : 'New Dapp'}
                    </Button>
                    <Button
                        onClick={() => window.location.href = '/payments'}
                        className="px-5 py-2 bg-green-500/10 text-green-400 border border-green-500/20 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-green-500/20 transition-all"
                    >
                        Payments
                    </Button>
                    <WalletMultiButton className="!bg-blue-600 !text-white !rounded-xl !h-10 !px-6 !font-black !text-[10px] !uppercase !tracking-widest" />
                </div>
            </div>
        </header>
    );
}
