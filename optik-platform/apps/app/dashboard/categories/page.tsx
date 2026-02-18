'use client';

import React from 'react';
import Button from '@/components/ui/Button';
import Link from 'next/link';

export default function CategoryManagement() {

    return (
        <div className="min-h-screen pt-24 pb-20 px-8">
            <div className="max-w-7xl mx-auto space-y-12">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2">Product <span className="gradient-text">Categories</span></h1>
                        <p className="text-gray-400">Organize your decentralized storefront with metadata-driven taxonomies.</p>
                    </div>
                    <Link href="/dashboard/products">
                        <Button>Manage Products</Button>
                    </Link>
                </div>

                <div className="glass p-10 rounded-[2.5rem] border-white/5 text-center">
                    <p className="text-gray-400">Category management is driven by product metadata. Update categories from the product editor.</p>
                </div>

                <Link href="/dashboard/merchant" className="text-blue-400 font-bold flex items-center gap-2 hover:gap-3 transition-all pt-8">
                    ← Back to Command Center
                </Link>
            </div>
        </div>
    );
}
