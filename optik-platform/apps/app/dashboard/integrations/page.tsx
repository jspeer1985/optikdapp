'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import Link from 'next/link';
import { optikApi, Integration } from '@/lib/api';

export default function IntegrationsHub() {
    const [integrations, setIntegrations] = useState<Integration[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const apiDocsUrl = `${process.env.NEXT_PUBLIC_API_URL || ''}/api/docs`;

    useEffect(() => {
        loadIntegrations();
    }, []);

    const loadIntegrations = async () => {
        try {
            const data = await optikApi.getIntegrations();
            setIntegrations(data);
        } catch (error) {
            console.error(error);
            setError('Failed to load integrations.');
        } finally {
            setLoading(false);
        }
    };

    const handleToggle = async (app: Integration) => {
        try {
            if (app.status === 'Connected') {
                if (confirm(`Disconnect ${app.name}?`)) {
                    await optikApi.disconnectIntegration(app.id);
                } else {
                    return;
                }
            } else {
                // In real app, this would open OAuth flow
                await optikApi.connectIntegration(app.id);
            }
            loadIntegrations();
        } catch {
            setError('Action failed. Please try again.');
        }
    };

    return (
        <div className="pb-20 px-8 py-10">
            <div className="max-w-7xl mx-auto space-y-12">
                <div className="flex justify-between items-center text-left">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2">Integrations <span className="gradient-text">Hub</span></h1>
                        <p className="text-gray-400">Bridge your decentralized empire with the world&apos;s leading e-commerce tools.</p>
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-20 text-gray-500">Loading integrations...</div>
                ) : (
                    <>
                        {error && <p className="text-red-400">{error}</p>}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {integrations.map((app) => (
                                <div key={app.id} className="glass p-10 rounded-[3rem] border-white/5 flex flex-col md:flex-row gap-8 items-start md:items-center group hover:border-blue-500/30 transition-all text-left">
                                <div className="w-20 h-20 bg-white/5 rounded-3xl flex items-center justify-center text-4xl group-hover:scale-105 transition-transform">
                                    {app.icon}
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-center mb-2">
                                        <h3 className="text-2xl font-black text-white">{app.name}</h3>
                                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${app.status === 'Connected' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 text-gray-500'}`}>
                                            {app.status}
                                        </span>
                                    </div>
                                    <p className="text-gray-500 text-sm mb-6 leading-relaxed">{app.detail}</p>
                                    <div className="flex gap-4">
                                        {app.status === 'Connected' ? (
                                            <Link href={`/dashboard/integrations/${app.id}/configure`}>
                                                <Button size="sm" variant="outline" className="h-10 px-8">Configure</Button>
                                            </Link>
                                        ) : (
                                            <Button size="sm" variant="primary" className="h-10 px-8" onClick={() => handleToggle(app)}>
                                                Install App
                                            </Button>
                                        )}
                                        {app.status === 'Connected' && (
                                            <button className="text-[10px] text-red-500 font-bold uppercase hover:underline" onClick={() => handleToggle(app)}>Disconnect</button>
                                        )}
                                    </div>
                                </div>
                            </div>
                            ))}
                        </div>
                    </>
                )}

                <div className="glass p-12 rounded-[3.5rem] border-blue-500/20 bg-blue-500/5 text-center">
                    <h3 className="text-2xl font-bold mb-4 italic">Custom Webhooks & API</h3>
                    <p className="text-gray-400 mb-8 max-w-xl mx-auto">Build your own custom tools using the Optik Enterprise SDK. Direct access to on-chain event streams and merchant settlement APIs.</p>
                    <a href={apiDocsUrl} target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" className="border-blue-500/50 text-blue-400">View Developer Documentation</Button>
                    </a>
                </div>
            </div>
        </div>
    );
}
