'use client';

import Link from 'next/link';
import Button from '@/components/ui/Button';

export default function WhitepaperPage() {
  return (
    <div className="min-h-screen bg-black text-white pt-32 pb-20">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-12">
          <Link href="/optik-coin">
            <Button variant="outline" className="mb-8">← Back to OptikCoin</Button>
          </Link>
          <h1 className="text-5xl md:text-6xl font-black mb-4">OptikCoin Whitepaper</h1>
          <p className="text-xl text-gray-400">Decentralized Commerce Infrastructure and dApp Conversion Platform</p>
        </div>

        {/* Content */}
        <article className="prose prose-invert max-w-none space-y-8 text-gray-300">
          {/* Executive Summary */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">1. Executive Summary</h2>
            <p className="leading-relaxed">
              OptikCoin is a decentralized commerce infrastructure designed to enable merchants to convert traditional online stores into fully functional decentralized applications (dApps) with integrated tokenized payments, NFT-backed products, and automated settlement.
            </p>
            <p className="leading-relaxed mt-4">
              The OptikCoin dApp Converter is a platform that automates the transformation of Web2 commerce workflows into Web3-native systems, reducing technical barriers and enabling merchants to participate in decentralized marketplaces without requiring blockchain engineering expertise.
            </p>
            <p className="leading-relaxed mt-4">
              The system solves key limitations in current e-commerce:
            </p>
            <ul className="list-disc list-inside space-y-2 mt-4 text-gray-400">
              <li>High platform fees</li>
              <li>Payment processing delays</li>
              <li>Chargeback risks</li>
              <li>Limited ownership of customer and store infrastructure</li>
              <li>Lack of programmable financial automation</li>
            </ul>
          </section>

          {/* Problem Statement */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">2. Problem Statement</h2>
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold text-blue-400 mb-2">Platform Dependency</h3>
                <p>Merchants rely on centralized platforms that control store availability, payment processing, and impose fixed fee structures.</p>
              </div>
              <div>
                <h3 className="text-xl font-bold text-blue-400 mb-2">Fragmented Financial Infrastructure</h3>
                <p>Payments, analytics, inventory, and settlement operate across multiple systems, increasing operational complexity and cost.</p>
              </div>
              <div>
                <h3 className="text-xl font-bold text-blue-400 mb-2">Limited Digital Ownership</h3>
                <p>Merchants do not fully control customer data, transaction infrastructure, or store logic.</p>
              </div>
              <div>
                <h3 className="text-xl font-bold text-blue-400 mb-2">Barriers to Web3 Adoption</h3>
                <p>Existing blockchain tooling is technically complex, fragmented, and difficult for non-developers to deploy.</p>
              </div>
            </div>
          </section>

          {/* Solution */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">3. The OptikCoin Solution</h2>
            <p className="leading-relaxed mb-4">The OptikCoin platform introduces a modular system composed of:</p>
            <ol className="list-decimal list-inside space-y-3 text-gray-400">
              <li>dApp Converter Engine</li>
              <li>Tokenized Payment Layer</li>
              <li>NFT Product Infrastructure</li>
              <li>Automated Fee and Settlement Routing</li>
              <li>Merchant Dashboard and Analytics Layer</li>
            </ol>
            <p className="leading-relaxed mt-6">This enables merchants to:</p>
            <ul className="list-disc list-inside space-y-2 mt-4 text-gray-400">
              <li>Deploy decentralized storefronts automatically</li>
              <li>Accept tokenized payments</li>
              <li>Track orders and revenue transparently</li>
              <li>Retain control of digital assets and infrastructure</li>
            </ul>
          </section>

          {/* Token Utility */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">5. OptikCoin Token Utility</h2>
            <p className="leading-relaxed mb-4">OptikCoin functions as the core utility token and is used for:</p>
            <ul className="list-disc list-inside space-y-2 text-gray-400">
              <li>Transaction settlement within the platform</li>
              <li>Merchant service fees</li>
              <li>Staking for network participation</li>
              <li>Incentive rewards</li>
              <li>Governance participation (future phase)</li>
            </ul>
          </section>

          {/* Tokenomics */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">6. Tokenomics Framework</h2>
            <p className="leading-relaxed mb-6">Token Allocation Model:</p>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <span>Ecosystem Growth & Rewards</span>
                <span className="font-bold text-blue-400">40%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <span>Merchant Incentives & Airdrops</span>
                <span className="font-bold text-blue-400">20%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <span>Development & Infrastructure</span>
                <span className="font-bold text-blue-400">20%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <span>Treasury & Liquidity</span>
                <span className="font-bold text-blue-400">15%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <span>Early Supporters</span>
                <span className="font-bold text-blue-400">5%</span>
              </div>
            </div>
          </section>

          {/* Roadmap */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">11. Development Roadmap</h2>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4 py-2">
                <h3 className="font-bold text-blue-400">Phase 1 – Core Infrastructure</h3>
                <p className="text-sm text-gray-400 mt-1">Token deployment, smart contracts, dashboard prototype</p>
              </div>
              <div className="border-l-4 border-blue-500 pl-4 py-2">
                <h3 className="font-bold text-blue-400">Phase 2 – dApp Converter Release</h3>
                <p className="text-sm text-gray-400 mt-1">Automated storefronts, NFT pipeline, payment routing</p>
              </div>
              <div className="border-l-4 border-blue-500 pl-4 py-2">
                <h3 className="font-bold text-blue-400">Phase 3 – Merchant Expansion</h3>
                <p className="text-sm text-gray-400 mt-1">Scalable indexing, UI/UX enhancement, staking features</p>
              </div>
              <div className="border-l-4 border-blue-500 pl-4 py-2">
                <h3 className="font-bold text-blue-400">Phase 4 – Ecosystem Growth</h3>
                <p className="text-sm text-gray-400 mt-1">Merchant incentives, marketplace discovery, API toolkit</p>
              </div>
              <div className="border-l-4 border-blue-500 pl-4 py-2">
                <h3 className="font-bold text-blue-400">Phase 5 – Network Maturity</h3>
                <p className="text-sm text-gray-400 mt-1">Governance, integrations, enterprise onboarding</p>
              </div>
            </div>
          </section>

          {/* Competitive Differentiation */}
          <section className="bg-white/5 p-8 rounded-2xl border border-white/10">
            <h2 className="text-3xl font-black text-white mb-6">12. Competitive Differentiation</h2>
            <ul className="list-disc list-inside space-y-3 text-gray-400">
              <li>Automated conversion from traditional stores to decentralized storefronts</li>
              <li>Integrated token and NFT infrastructure</li>
              <li>Unified merchant dashboard</li>
              <li>Automated settlement logic</li>
              <li>Reduced technical complexity for merchants</li>
            </ul>
          </section>

          {/* Vision */}
          <section className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 p-8 rounded-2xl border border-blue-500/20">
            <h2 className="text-3xl font-black text-white mb-6">14. Long-Term Vision</h2>
            <p className="leading-relaxed mb-4">
              Establish a decentralized commerce infrastructure that enables:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-400">
              <li>Merchant-owned digital storefronts</li>
              <li>Automated financial workflows</li>
              <li>Global tokenized commerce</li>
              <li>Open participation in digital economies</li>
            </ul>
            <p className="leading-relaxed mt-6 text-blue-300 italic">
              The guiding principle is to lower barriers to entry while preserving transparency and control.
            </p>
          </section>

          {/* Disclaimer */}
          <section className="bg-red-500/5 p-8 rounded-2xl border border-red-500/20">
            <h2 className="text-2xl font-bold text-red-400 mb-4">15. Disclaimer</h2>
            <p className="text-sm text-gray-400">
              This document describes a conceptual framework and development direction. It does not constitute financial advice, an offer of securities, or a guarantee of performance or returns.
            </p>
          </section>
        </article>

        {/* Footer CTA */}
        <div className="mt-16 pt-8 border-t border-white/10 text-center">
          <p className="text-gray-400 mb-6">Ready to revolutionize your commerce?</p>
          <Link href="/optik-coin">
            <Button className="px-10 py-4 bg-gradient-to-r from-blue-600 to-blue-500">
              View OptikCoin Token
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
