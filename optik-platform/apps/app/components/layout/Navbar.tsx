'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import ConnectWallet from '@/components/wallet/ConnectWallet';

export default function Navbar() {
    const pathname = usePathname();
    const isStandalone = pathname?.startsWith('/dashboard') || pathname?.startsWith('/auth');

    if (isStandalone) return null;

    return (
        <nav className="fixed top-0 w-full z-50 glass border-b border-white/10 bg-gradient-to-r from-blue-950/30 to-transparent">
            <div className="container mx-auto px-4 h-20 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-3 group hover:scale-105 transition-transform duration-300">
                    <div className="relative w-12 h-12 flex items-center justify-center">
                        {/* Glow effect behind the bird */}
                        <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-lg group-hover:bg-blue-500/40 transition-all duration-300"></div>
                        {/* Bird logo */}
                        <img
                            src="/optik_bird.svg"
                            className="w-11 h-11 relative z-10 drop-shadow-lg group-hover:drop-shadow-[0_0_12px_rgba(59,130,246,0.6)] transition-all duration-300"
                        />
                    </div>
                    <div>
                        <span className="text-2xl font-black tracking-tight bg-gradient-to-r from-blue-400 to-blue-200 bg-clip-text text-transparent">
                            OPTIK
                        </span>
                        <span className="block text-[10px] font-bold text-blue-400 tracking-widest -mt-1">PLATFORM</span>
                    </div>
                </Link>
                <div className="hidden md:flex items-center gap-8">
                    <Link href="/#features" className="text-sm font-medium hover:text-primary transition-colors">Features</Link>
                    <Link href="/#pricing" className="text-sm font-medium hover:text-primary transition-colors">Pricing</Link>
                    <Link href="/payments" className="text-sm font-medium hover:text-primary transition-colors">Payments</Link>
                    <Link href="/dashboard/merchant" className="text-sm font-medium hover:text-primary transition-colors">Dashboard</Link>
                    <Link href="/auth" className="px-5 py-2 bg-white/5 border border-white/10 rounded-xl text-sm font-bold hover:bg-white/10 transition-all">Sign In</Link>
                    <ConnectWallet />
                </div>
            </div>
        </nav>
    );
}
