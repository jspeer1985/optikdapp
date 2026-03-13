'use client';

import React from 'react';

export default function OptikCoinPage() {
    return (
        <div className="min-h-screen bg-black text-white selection:bg-blue-500/30">
            {/* 1. HERO SECTION */}
            <section className="relative pt-32 pb-20 overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] -z-10"></div>
                <div className="container mx-auto px-4 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-bold text-sm mb-8">
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                        Official Utility Token of the Optik Ecosystem
                    </div>
                    <h1 className="text-6xl md:text-8xl font-black mb-8 tracking-tighter">
                        $OPTIK <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">COIN</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed mb-12">
                        Powering the decentralized commerce revolution. Eliminate fees, unlock revenue streams, and govern the future of retail.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-6 justify-center">
                        <a
                            href="/whitepaper"
                            className="px-10 py-5 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-2xl text-lg font-bold hover:scale-105 transition-transform shadow-lg shadow-blue-600/20 inline-block text-center"
                        >
                            Read Whitepaper
                        </a>
                        <a
                            href="https://solscan.io/token/EGBboNXbvfqK9sUHAsx8wwwUHTm1QDuKDjpsXN1YoPnJ"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-10 py-5 bg-white/5 border border-white/10 text-white rounded-2xl text-lg font-bold hover:bg-white/10 transition-colors inline-block text-center"
                        >
                            View Contract
                        </a>
                    </div>
                </div>
            </section>

            {/* 2. PROBLEM & SOLUTION */}
            <section className="py-24 bg-white/5">
                <div className="container mx-auto px-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
                        <div>
                            <h2 className="text-4xl font-black mb-8">The Commerce <span className="text-red-400">Problem</span></h2>
                            <div className="space-y-8">
                                <div className="p-6 border-l-4 border-red-500 bg-red-500/5">
                                    <h3 className="text-xl font-bold mb-2">Platform Tax</h3>
                                    <p className="text-gray-400">Merchants pay 2-5% + 30¢ on every transaction to payment processors and platform fees (Shopify, Stripe, etc).</p>
                                </div>
                                <div className="p-6 border-l-4 border-red-500 bg-red-500/5">
                                    <h3 className="text-xl font-bold mb-2">Rent-Seeking Middlemen</h3>
                                    <p className="text-gray-400">Your data is sold, your customers are targeted by competitors, and you ownership is limited.</p>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h2 className="text-4xl font-black mb-8">The Optik <span className="text-emerald-400">Solution</span></h2>
                            <div className="space-y-8">
                                <div className="p-6 border-l-4 border-emerald-500 bg-emerald-500/5">
                                    <h3 className="text-xl font-bold mb-2">Zero Third-Party Fees</h3>
                                    <p className="text-gray-400">
                                        By transacting in $OPTIK, you eliminate Shopify fees and Stripe cuts. Keep 100% of your revenue or reinvest it automatically.
                                    </p>
                                </div>
                                <div className="p-6 border-l-4 border-emerald-500 bg-emerald-500/5">
                                    <h3 className="text-xl font-bold mb-2">Owner Sovereignty</h3>
                                    <p className="text-gray-400">
                                        You own your dApp, your customer data, and your smart contract. The DApp Converter bridges your Web2 store to Web3 instantly.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 3. DAPP CONVERTER SIGNIFICANCE */}
            <section className="py-24">
                <div className="container mx-auto px-4 text-center">
                    <div className="max-w-4xl mx-auto mb-16">
                        <span className="text-blue-500 font-bold uppercase tracking-widest text-sm">The Bridge to Web3</span>
                        <h2 className="text-5xl font-black mt-4 mb-6">Why the DApp Converter Matters</h2>
                        <p className="text-xl text-gray-400">
                            Our proprietary AI agent pipeline doesn&apos;t just copy your store—it evolves it.
                            It strips away the &quot;platform tax&quot; and injects decentralized utility into every product.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
                        <div className="p-8 rounded-3xl bg-gradient-to-b from-gray-900 to-black border border-white/10">
                            <div className="text-4xl mb-6">🔄</div>
                            <h3 className="text-xl font-bold mb-4">Seamless Migration</h3>
                            <p className="text-gray-400">One-click import from Shopify/WooCommerce. No coding required. We handle the smart contract deployment.</p>
                        </div>
                        <div className="p-8 rounded-3xl bg-gradient-to-b from-gray-900 to-black border border-white/10">
                            <div className="text-4xl mb-6">💸</div>
                            <h3 className="text-xl font-bold mb-4">Fee Elimination</h3>
                            <p className="text-gray-400">Stop paying monthly subscriptions and transaction % fees. Pay only for what you use on the blockchain (fractions of a cent).</p>
                        </div>
                        <div className="p-8 rounded-3xl bg-gradient-to-b from-gray-900 to-black border border-white/10">
                            <div className="text-4xl mb-6">🚀</div>
                            <h3 className="text-xl font-bold mb-4">Liquidity Injection</h3>
                            <p className="text-gray-400">Every converted product is auto-paired with $OPTIK, creating instant market depth and trading volume.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* 4. 8 REVENUE STREAMS */}
            <section className="py-24 bg-gradient-to-br from-blue-900/20 to-purple-900/20 relative overflow-hidden">
                <div className="container mx-auto px-4 relative z-10">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-6xl font-black mb-6">Unlock <span className="text-blue-400">8+ New Revenue Streams</span></h2>
                        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                            By converting your store, you don&apos;t just sell products. You participate in a decentralized economy.
                            Keep your Web2 sales if you choose, but ADD these Web3 engines:
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[
                            { title: "Direct Sales (No Fees)", desc: "100% margin retention on crypto payments." },
                            { title: "Secondary Royalties", desc: "Earn 5-10% every time your product NFT is resold." },
                            { title: "Staking Yield", desc: "Earn APY by providing liquidity with $OPTIK." },
                            { title: "Transaction Rebates", desc: "Get paid back for volume generated by your dApp." },
                            { title: "Data Monetization", desc: "Opt-in to sell anonymized shopping data to protocols." },
                            { title: "Referral On-Chain", desc: "Smart contract affiliate payouts for every referral." },
                            { title: "Governance Rewards", desc: "Earn $OPTIK for voting on platform upgrades." },
                            { title: "Sub-Leasing Access", desc: "Rent out 'access pass' NFTs for temporary utility." },
                        ].map((stream, i) => (
                            <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:bg-blue-600/20 transition-colors group">
                                <div className="text-blue-500 font-black text-xl mb-2 group-hover:text-white transition-colors">0{i + 1}.</div>
                                <h3 className="font-bold text-lg text-white mb-2">{stream.title}</h3>
                                <p className="text-sm text-gray-400">{stream.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* 5. ROADMAP */}
            <section className="py-24">
                <div className="container mx-auto px-4">
                    <h2 className="text-4xl font-black text-center mb-16">Ecosystem <span className="gradient-text">Roadmap</span></h2>

                    <div className="relative border-l border-white/20 ml-4 md:ml-auto md:mr-auto md:w-2/3 space-y-12">
                        <div className="relative pl-8 md:pl-12">
                            <div className="absolute left-[-5px] top-2 w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_10px_#3b82f6]"></div>
                            <h3 className="text-2xl font-bold text-white mb-2">Phase 1: Foundation (Q1 2026)</h3>
                            <ul className="list-disc list-inside text-gray-400 space-y-2">
                                <li>Launch DApp Converter Agent</li>
                                <li>$OPTIK Token Generation Event (TGE)</li>
                                <li>Onboard first 100 Merchants</li>
                            </ul>
                        </div>
                        <div className="relative pl-8 md:pl-12">
                            <div className="absolute left-[-5px] top-2 w-3 h-3 rounded-full bg-gray-600 border border-gray-400"></div>
                            <h3 className="text-2xl font-bold text-gray-300 mb-2">Phase 2: Expansion (Q3 2026)</h3>
                            <ul className="list-disc list-inside text-gray-500 space-y-2">
                                <li>Mobile App Studio Launch</li>
                                <li>Cross-Chain Bridges (ETH, BASE)</li>
                                <li>Decentralized Ad Network Beta</li>
                            </ul>
                        </div>
                        <div className="relative pl-8 md:pl-12">
                            <div className="absolute left-[-5px] top-2 w-3 h-3 rounded-full bg-gray-600 border border-gray-400"></div>
                            <h3 className="text-2xl font-bold text-gray-300 mb-2">Phase 3: Sovereignty (2027)</h3>
                            <ul className="list-disc list-inside text-gray-500 space-y-2">
                                <li>Full DAO Governance Handover</li>
                                <li>Optik Chain (L3 on Solana)</li>
                                <li>1 Million Active DApps</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* 6. FOOTER / SOCIALS */}
            <section className="py-20 border-t border-white/10 bg-black">
                <div className="container mx-auto px-4 text-center">
                    <h2 className="text-3xl font-bold mb-8">Join the Community</h2>
                    <div className="flex justify-center gap-8 mb-12">
                        <a href="https://x.com/OptikProtocol" target="_blank" rel="noopener noreferrer" className="p-4 rounded-full bg-white/5 hover:bg-blue-500 hover:text-white transition-all text-2xl">🐦 Twitter</a>
                        <a href="https://discord.gg/optik" target="_blank" rel="noopener noreferrer" className="p-4 rounded-full bg-white/5 hover:bg-indigo-500 hover:text-white transition-all text-2xl">💬 Discord</a>
                        <a href="https://t.me/OptikProtocol" target="_blank" rel="noopener noreferrer" className="p-4 rounded-full bg-white/5 hover:bg-blue-700 hover:text-white transition-all text-2xl">✈️ Telegram</a>
                        <a href="https://github.com/OptikProtocol" target="_blank" rel="noopener noreferrer" className="p-4 rounded-full bg-white/5 hover:bg-gray-700 hover:text-white transition-all text-2xl">🐙 GitHub</a>
                    </div>
                    <div className="text-gray-500 text-sm">
                        &copy; 2026 Optik Protocol. All rights reserved.
                    </div>
                </div>
            </section>
        </div>
    );
}
