'use client';

import React from 'react';
import Button from '@/components/ui/Button';
import Link from 'next/link';

export default function LogisticsManagement() {
    return (
        <div className="pb-20 px-4 md:px-8 py-10">
            <div className="max-w-7xl mx-auto space-y-12">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2">Global <span className="gradient-text">Logistics</span></h1>
                        <p className="text-gray-400">Connect your preferred carriers and fulfillment providers to enable shipping workflows.</p>
                    </div>
                    <Link href="/dashboard/integrations">
                        <Button>Connect Carrier</Button>
                    </Link>
                </div>

                <div className="glass p-10 rounded-[3rem] border-white/5 text-center">
                    <p className="text-gray-400">Shipping integrations are managed through the Integrations hub. Connect a carrier to enable labels, tracking, and 3PL workflows.</p>
                </div>
            </div>
        </div>
    );
}
