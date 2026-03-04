'use client';

import Link from 'next/link';

export default function Home() {
    const tokenMint = process.env.NEXT_PUBLIC_OPTIK_TOKEN_MINT;

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative overflow-hidden pt-32 pb-20 md:pt-48 md:pb-32 bg-transparent text-white">
                <div className="absolute inset-0 -z-10 hero-bg"></div>
                <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
                <div className="container mx-auto px-4">
                    <div className="max-w-5xl mx-auto text-center relative z-10">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6 animate-shimmer">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                            </span>
                            Now powering 10,000+ Solana Dapps
                        </div>
                        <h1 className="text-5xl md:text-7xl lg:text-8xl font-black mb-8 tracking-tight">
                            Scale your Web3 <br />
                            <span className="gradient-text">Dreams on Solana</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
                            The all-in-one Web3 infrastructure for building, launching, and scaling your decentralized applications.
                            Accept payments, mint NFTs, and manage your entire ecosystem.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center pointer-events-auto">
                            <Link href="/create-dapp" className="w-full sm:w-auto px-10 py-5 bg-primary text-primary-foreground rounded-2xl text-lg font-bold hover:opacity-90 transition-all shadow-xl shadow-primary/20 hover:-translate-y-1 block text-center">
                                Start Building
                            </Link>
                            <Link href="/optik-coin" className="w-full sm:w-auto px-10 py-5 bg-gradient-to-r from-emerald-500 to-teal-400 text-white rounded-2xl text-lg font-bold hover:scale-105 transition-all shadow-lg shadow-emerald-500/20 block text-center">
                                Discover $OPTIK
                            </Link>
                        </div>

                        {tokenMint && (
                            <div className="mt-8 flex items-center justify-center gap-2 text-sm text-muted-foreground animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300">
                                <span className="opacity-70">Official CA:</span>
                                <a
                                    href={`https://solscan.io/token/${tokenMint}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="font-mono text-primary hover:text-primary/80 transition-colors flex items-center gap-1.5 bg-primary/10 px-3 py-1.5 rounded-lg border border-primary/20 hover:bg-primary/20 group"
                                >
                                    {`${tokenMint.slice(0, 4)}...${tokenMint.slice(-4)}`}
                                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                                </a>
                            </div>
                        )}

                    </div>
                </div>
            </section>

            {/* Trust & Stats */}
            <section className="py-12 border-y border-white/5 bg-white/5 backdrop-blur-sm">
                <div className="container mx-auto px-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                        <div>
                            <div className="text-3xl font-bold mb-1">$2.5B+</div>
                            <div className="text-sm text-muted-foreground">Volume Processed</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-1">10k+</div>
                            <div className="text-sm text-muted-foreground">Active Dapps</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-1">0.1s</div>
                            <div className="text-sm text-muted-foreground">Settlement Time</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-1">99.9%</div>
                            <div className="text-sm text-muted-foreground">Uptime SLA</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* What is Optik Platform */}
            <section className="py-32 bg-transparent relative overflow-hidden">
                <div className="container mx-auto px-4">
                    <div className="flex flex-col lg:flex-row items-center gap-16 max-w-6xl mx-auto">
                        <div className="flex-1">
                            <h2 className="text-4xl md:text-5xl font-bold mb-8 tracking-tight">Powerful backend for modern <span className="text-primary italic">Web3 builders</span></h2>
                            <p className="text-lg text-muted-foreground leading-relaxed mb-8">
                                Optik Platform is a comprehensive Web3 infrastructure provider that enables developers and businesses to build,
                                deploy, and scale decentralized applications without the complexity of managing blockchain infrastructure.
                            </p>
                            <div className="space-y-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-blue-900/40 flex items-center justify-center text-primary">⚡</div>

                                    <div>
                                        <h3 className="font-bold text-lg">Instant Deployment</h3>
                                        <p className="text-muted-foreground">Launch your dapp in minutes with pre-built infrastructure.</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-blue-900/40 flex items-center justify-center text-blue-400">🔒</div>
                                    <div>
                                        <h3 className="font-bold text-lg">Enterprise Security</h3>
                                        <p className="text-muted-foreground">Audited smart contracts and military-grade encryption.</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-emerald-900/40 flex items-center justify-center text-emerald-400">📈</div>
                                    <div>
                                        <h3 className="font-bold text-lg">Scale Effortlessly</h3>
                                        <p className="text-muted-foreground">Millions of transactions with Solana infrastructure.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex-1 w-full lg:w-auto">
                            <div className="relative group">
                                <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 to-emerald-400 rounded-[2rem] opacity-20 blur-2xl group-hover:opacity-30 transition-opacity"></div>

                                <div className="relative bg-card border border-border p-8 rounded-[2rem] card-shadow">
                                    <div className="flex items-center justify-between mb-8">
                                        <div className="flex gap-2">
                                            <div className="w-3 h-3 rounded-full bg-red-400"></div>
                                            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                                            <div className="w-3 h-3 rounded-full bg-green-400"></div>
                                        </div>
                                        <div className="text-xs text-muted-foreground font-mono">Dapp Dashboard</div>
                                    </div>
                                    <div className="space-y-4">
                                        <div className="h-4 w-2/3 bg-muted rounded-full animate-pulse"></div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="h-24 bg-muted/50 rounded-xl"></div>
                                            <div className="h-24 bg-muted/50 rounded-xl"></div>
                                        </div>
                                        <div className="h-32 bg-primary/5 rounded-xl border border-primary/10 flex items-center justify-center text-primary font-bold">
                                            $42,069.69 Revenue
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Core Features */}
            <section className="py-32 relative">

                <div className="container mx-auto px-4">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl md:text-6xl font-black mb-6">Everything you need to <span className="text-primary italic">Succeed</span></h2>
                        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                            Our suite of tools is designed to handle the heavy lifting, so you can focus on building what matters.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
                        <div className="group p-10 bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 card-shadow-hover">

                            <div className="text-4xl mb-6">💳</div>
                            <h3 className="text-2xl font-bold mb-4">Payment Processing</h3>
                            <p className="text-muted-foreground leading-relaxed mb-6">
                                Accept 50+ SPL tokens and fiat payments instantly. Automatic fee routing and real-time settlements via Solana.
                            </p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> Multicurrency Support
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> Fiat-to-Crypto Rails
                                </li>
                            </ul>
                            <Link href="/dashboard/merchant" className="font-bold text-primary group-hover:translate-x-1 transition-transform inline-flex items-center gap-2">
                                Learn more <span>→</span>
                            </Link>
                        </div>

                        <div className="group p-10 bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 card-shadow-hover">

                            <div className="text-4xl mb-6">🎨</div>
                            <h3 className="text-2xl font-bold mb-4">NFT Infrastructure</h3>
                            <p className="text-muted-foreground leading-relaxed mb-6">
                                Launch and managing NFT collections with ease. Compressed NFTs support for ultra-low-cost minting.
                            </p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> cNFT Integration
                                </li>
                                <li className="flex items-center gap-3">
                                    <span className="text-primary">✓</span> Royalties Enforcement
                                </li>
                            </ul>
                            <Link href="/create-dapp" className="font-bold text-primary group-hover:translate-x-1 transition-transform inline-flex items-center gap-2">
                                Learn more <span>→</span>
                            </Link>
                        </div>

                        <div className="group p-10 bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 card-shadow-hover">

                            <div className="text-4xl mb-6">🪙</div>
                            <h3 className="text-2xl font-bold mb-4">Optik Token Pairing</h3>
                            <p className="text-muted-foreground leading-relaxed mb-6">
                                Incentivize your users with $OPTIK rewards. Unlock premium features and governance rights.
                            </p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> Yield Farming
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> Staking Rewards
                                </li>
                            </ul>
                            <Link href="/dashboard/merchant" className="font-bold text-primary group-hover:translate-x-1 transition-transform inline-flex items-center gap-2">
                                Learn more <span>→</span>
                            </Link>
                        </div>

                        <div className="group p-10 bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 card-shadow-hover">

                            <div className="text-4xl mb-6">🛠️</div>
                            <h3 className="text-2xl font-bold mb-4">Developer Ecosystem</h3>
                            <p className="text-muted-foreground leading-relaxed mb-6">
                                Comprehensive SDKs, APIs, and webhooks to integrate Optik into any application workflow.
                            </p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> REST & GraphQL
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-primary">✓</span> React Hooks SDK
                                </li>
                            </ul>
                            <Link href="/dashboard/merchant" className="font-bold text-primary group-hover:translate-x-1 transition-transform inline-flex items-center gap-2">
                                Learn more <span>→</span>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Pricing Tiers */}
            <section id="pricing" className="py-32">
                <div className="container mx-auto px-4">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl md:text-6xl font-black mb-6">Transparent <span className="gradient-text">Pricing</span></h2>
                        <p className="text-xl text-muted-foreground">Choose the plan that fits your growth stage.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
                        {[
                            { name: 'Elite', price: '0', fee: '15%', apps: 'Unlimited', agents: ['Marketing', 'Product', 'UI', 'Security', 'NFT', 'Optik AI+'] },
                            { name: 'Scale', price: '0', fee: '12%', apps: '25 Dapps', agents: ['Marketing', 'Product', 'UI', 'Security'] },
                            { name: 'Global', price: '0', fee: '9%', apps: '10 Dapps', agents: ['Marketing', 'Product', 'UI'] },
                            { name: 'Growth', price: '0', fee: '5%', apps: '3 Dapps', agents: ['Marketing', 'Product'] },
                            { name: 'Basic', price: '0', fee: '3%', apps: '1 Dapp', agents: ['Optik AI Core'] },
                        ].map((tier, idx) => (
                            <div key={idx} className={`p-10 rounded-[3rem] border border-border glass-card relative overflow-hidden group ${tier.name === 'Elite' ? 'blue-glow border-blue-500/50' : ''}`}>
                                <h3 className="text-2xl font-bold mb-4">{tier.name}</h3>
                                <div className="flex items-baseline gap-2 mb-2">
                                    <span className="text-5xl font-black text-primary">$0</span>
                                    <span className="text-muted-foreground font-medium">setup fee</span>
                                </div>
                                <div className="text-blue-400 font-bold mb-6">{tier.fee} transaction fee</div>
                                <ul className="space-y-4 mb-10 text-muted-foreground">
                                    <li className="flex items-center gap-3">✓ {tier.apps}</li>
                                    {tier.agents.map((agent, i) => (
                                        <li key={i} className="flex items-center gap-3 text-primary font-medium">✓ {agent}</li>
                                    ))}
                                    <li className="flex items-center gap-3 opacity-50">✓ Advanced Analytics</li>
                                </ul>
                                <Link href={`/checkout?tier=${tier.name.toLowerCase()}`} className={`block w-full py-4 text-center font-bold rounded-2xl transition-all ${tier.name === 'Elite' ? 'bg-primary text-primary-foreground shadow-lg shadow-blue-500/20 hover:opacity-90 ring-2 ring-white ring-offset-2 ring-offset-transparent' : 'border-2 border-primary text-primary hover:bg-primary/5'}`}>
                                    Get Started
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Revenue Streams */}
            <section className="py-32 overflow-hidden relative">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_rgba(0,186,255,0.1)_0%,transparent_70%)]"></div>
                <div className="container mx-auto px-4 relative z-10">
                    <div className="max-w-4xl mx-auto text-center mb-20">
                        <h2 className="text-4xl md:text-6xl font-black mb-8">Automated Revenue <span className="gradient-text italic">Distribution</span></h2>
                        <p className="text-xl text-slate-400">Optik automatically manages complex revenue splits and treasury allocations.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                        <div className="opaque-box p-10 rounded-[2.5rem]">
                            <div className="space-y-8">
                                <div className="flex justify-between items-center pb-4 border-b border-white/10">
                                    <span className="text-slate-400">Merchant Payout</span>
                                    <span className="text-2xl font-bold text-green-400">95.0%</span>
                                </div>
                                <div className="flex justify-between items-center pb-4 border-b border-white/10">
                                    <span className="text-slate-400">Optik Treasury</span>
                                    <span className="text-2xl font-bold text-blue-400">2.5%</span>
                                </div>
                                <div className="flex justify-between items-center pb-4 border-b border-white/10">
                                    <span className="text-slate-400">Staking Rewards</span>
                                    <span className="text-2xl font-bold text-cyan-400">1.0%</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-400">Ecosystem Fund</span>
                                    <span className="text-2xl font-bold text-blue-300">1.5%</span>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h3 className="text-3xl font-bold mb-6">Real-world Example</h3>
                            <p className="text-slate-400 mb-8 leading-relaxed">
                                A Growth Tier project processing $100k in monthly volume would generate $2,900 in transaction fees, distributed seamlessly across all ecosystem participants.
                            </p>
                            <div className="inline-flex items-center gap-6 p-6 glass rounded-2xl border border-white/10">
                                <div className="text-4xl">🚀</div>
                                <div>
                                    <div className="font-bold text-lg">Scalable Economy</div>
                                    <div className="text-slate-500 text-sm">Powered by $OPTIK tokenomics</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer CTA */}
            <section className="py-20">
                <div className="container mx-auto px-4">
                    <div className="bg-gradient-to-r from-blue-700 to-emerald-600 rounded-[3rem] p-12 md:p-24 text-center text-white relative overflow-hidden animate-pulse-blue">
                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-20"></div>
                        <div className="relative z-10">
                            <h2 className="text-4xl md:text-6xl font-black mb-8">Ready to build the future?</h2>
                            <p className="text-xl md:text-2xl mb-12 text-blue-100 max-w-2xl mx-auto">
                                Join the 10,000+ developers scaling their dreams on Optik Platform for $0 down.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-6 justify-center">
                                <button
                                    type="button"
                                    aria-label="Convert Now"
                                    onClick={() => (window.location.hash = 'pricing')}
                                    className="group inline-flex items-center justify-center h-16 px-12 text-lg font-semibold rounded-lg bg-white text-blue-700 hover:bg-slate-50 transition-all shadow-xl disabled:opacity-50"
                                >
                                    Convert Now
                                    <span className="ml-2 transform group-hover:translate-x-1 transition-transform">→</span>
                                </button>
                                <Link
                                    href="/drops"
                                    className="px-10 py-5 bg-blue-600 text-white rounded-2xl text-lg font-bold hover:bg-blue-700 transition-all border border-blue-500"
                                >
                                    View Live Dapps
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
