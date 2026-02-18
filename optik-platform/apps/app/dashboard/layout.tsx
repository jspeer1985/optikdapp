'use client';

import React from 'react';
import DashboardTabs from '@/components/layout/DashboardTabs';
import DashboardHeader from '@/components/layout/DashboardHeader';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-[#030303]">
            <DashboardHeader />
            <div className="pt-20">
                <DashboardTabs />
                <div className="animate-in fade-in duration-700">
                    {children}
                </div>
            </div>
        </div>
    );
}
