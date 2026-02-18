'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function DashboardTabs() {
    const pathname = usePathname();

    const tabs = [
        { name: 'Overview', href: '/dashboard/merchant', icon: '📊' },
        { name: 'Products', href: '/dashboard/products', icon: '📦' },
        { name: 'Shipping', href: '/dashboard/logistics', icon: '🚚' },
        { name: 'Integrations', href: '/dashboard/integrations', icon: '🔌' },
        { name: 'Analytics', href: '/dashboard/analytics', icon: '📈' },
        { name: 'Security', href: '/dashboard/security', icon: '🛡️' },
        { name: 'NFT Studio', href: '/dashboard/nft-creator', icon: '🎨' },
        { name: 'Mobile App', href: '/dashboard/mobile-app', icon: '📱' },
        { name: 'Agents', href: '/orchestrator', icon: '🤖' },
    ];

    return (
        <div className="w-full border-b border-white/5 bg-black/40 backdrop-blur-md sticky top-20 z-40">
            <div className="max-w-7xl mx-auto px-4 md:px-8">
                <div className="flex overflow-x-auto no-scrollbar gap-8">
                    {tabs.map((tab) => {
                        const isActive = pathname === tab.href;
                        return (
                            <Link
                                key={tab.href}
                                href={tab.href}
                                className={`flex items-center gap-2 py-4 px-2 border-b-2 transition-all whitespace-nowrap text-xs font-black uppercase tracking-widest ${isActive
                                    ? 'border-blue-400 text-white'
                                    : 'border-transparent text-gray-400 hover:text-white'
                                    }`}
                            >
                                <span>{tab.icon}</span>
                                {tab.name}
                            </Link>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
