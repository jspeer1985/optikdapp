'use client';

import { usePathname } from 'next/navigation';

export default function Footer() {
    const pathname = usePathname();
    const isStandalone = pathname?.startsWith('/dashboard') || pathname?.startsWith('/auth');
    const tokenMint = process.env.NEXT_PUBLIC_OPTIK_TOKEN_MINT;

    if (isStandalone) return null;

    return (
        <footer className="py-20 border-t border-white/5 bg-black/80 backdrop-blur-xl">
            <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row justify-between items-center gap-12">
                    <div className="flex flex-col items-center md:items-start">
                        <div className="text-3xl font-black tracking-tighter mb-4">
                            OPTIK <span className="gradient-text italic"></span>
                        </div>
                        <p className="text-slate-500 text-sm max-w-xs text-center md:text-left">
                            Building the next generation of decentralized commerce on Solana.
                        </p>

                        {tokenMint && (
                            <div className="mt-6 flex flex-col items-center md:items-start gap-2">
                                <span className="text-[10px] font-bold text-slate-600 tracking-widest uppercase">Official Contract</span>
                                <a
                                    href={`https://solscan.io/token/${tokenMint}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="font-mono text-xs text-slate-400 hover:text-primary transition-colors bg-white/5 px-3 py-2 rounded-lg border border-white/5 flex items-center gap-2 hover:bg-white/10 group"
                                >
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                    {`${tokenMint.slice(0, 6)}...${tokenMint.slice(-6)}`}
                                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-50 group-hover:opacity-100 transition-opacity"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                </a>
                            </div>
                        )}
                    </div>

                    <div className="flex flex-wrap justify-center gap-12 text-sm font-bold text-slate-400">
                        <a href="https://docs.optik.com" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">DOCS</a>
                        <a href="https://docs.optik.com/api" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">API REFERENCE</a>
                        <a href="https://x.com/OptikProtocol" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">TWITTER / X</a>
                        <a href="https://discord.gg/optik" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">DISCORD</a>
                    </div>
                    <div className="text-slate-500 text-xs font-mono">
                        © 2026 OPTIK ENTERPRISE. ALL RIGHTS SECURED.
                    </div>
                </div>
            </div>
        </footer>
    );
}
