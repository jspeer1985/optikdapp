'use client';

import React, { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import { api } from '@/lib/api';

export default function MarketingControl() {
    const [loading, setLoading] = useState('');
    const [status, setStatus] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [logs, setLogs] = useState<string[]>([]);

    useEffect(() => {
        let mounted = true;
        const loadLogs = async () => {
            try {
                const data = await api<{ logs: string[] }>('/api/v1/marketing/logs');
                if (mounted) {
                    setLogs(data.logs || []);
                }
            } catch (err) {
                if (mounted) {
                    setLogs([]);
                }
            }
        };
        loadLogs();
        return () => {
            mounted = false;
        };
    }, []);

    const runAirdrop = async () => {
        setLoading('airdrop');
        try {
            await api('/api/v1/marketing/airdrop', {
                method: 'POST',
                body: JSON.stringify({ criteria: 'active_traders', amount: 50 })
            });
            setStatus('Airdrop campaign queued successfully.');
            setError(null);
        } catch (e) {
            console.error(e);
            setError('Connection error to Marketing Agent.');
        } finally {
            setLoading('');
        }
    };

    const startStaking = async () => {
        setLoading('staking');
        try {
            await api('/api/v1/marketing/staking', {
                method: 'POST',
                body: JSON.stringify({ apy: 15.0, lock_period_days: 30 })
            });
            setStatus('Staking pool initialized successfully.');
            setError(null);
        } catch (e) {
            console.error(e);
            setError('Error contacting agent.');
        } finally {
            setLoading('');
        }
    };

    return (
        <div className="pb-20 px-8 py-10">
            <div className="max-w-7xl mx-auto space-y-12">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2">AI <span className="gradient-text">Marketing</span> Agent</h1>
                        <p className="text-gray-400">Autonomous growth, staking rewards, and airdrop campaigns.</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="glass p-10 rounded-[3rem] space-y-8 h-fit">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-blue-500 rounded-full animate-pulse shadow-[0_0_20px_rgba(59,130,246,0.5)]"></div>
                            <h2 className="text-2xl font-bold text-white">Agent Active</h2>
                        </div>

                        <div className="space-y-6">
                            {status && (
                                <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-200 text-sm">
                                    {status}
                                </div>
                            )}
                            {error && (
                                <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
                                    {error}
                                </div>
                            )}
                            <div className="p-6 bg-white/5 rounded-2xl border border-white/5">
                                <p className="text-gray-500 text-xs font-black uppercase mb-3">Live Campaign Status</p>
                                <p className="text-lg font-bold text-white">Active marketing automation</p>
                                <div className="mt-4 flex gap-4">
                                    <span className="text-xs text-emerald-400 font-bold">ROI: On request</span>
                                    <span className="text-xs text-blue-400 font-bold">CTR: On request</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <button
                                    onClick={runAirdrop}
                                    disabled={loading !== ''}
                                    className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl hover:bg-purple-500/20 transition-all text-left group"
                                >
                                    <span className="text-2xl mb-2 block group-hover:scale-110 transition-transform">🪂</span>
                                    <h4 className="text-white font-bold text-sm">Launch Airdrop</h4>
                                    <p className="text-xs text-gray-400 mt-1">Target active wallets</p>
                                    {loading === 'airdrop' && <span className="text-xs text-purple-400 animate-pulse mt-2 block">Initializing...</span>}
                                </button>

                                <button
                                    onClick={startStaking}
                                    disabled={loading !== ''}
                                    className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl hover:bg-blue-500/20 transition-all text-left group"
                                >
                                    <span className="text-2xl mb-2 block group-hover:scale-110 transition-transform">🔒</span>
                                    <h4 className="text-white font-bold text-sm">Start Staking</h4>
                                    <p className="text-xs text-gray-400 mt-1">15% APY Rewards</p>
                                    {loading === 'staking' && <span className="text-xs text-blue-400 animate-pulse mt-2 block">Deploying Pool...</span>}
                                </button>
                            </div>

                            <div className="space-y-4">
                                <label htmlFor="ad-spend" className="block text-sm font-bold text-gray-400">AD SPEND (DAILY)</label>
                                <input id="ad-spend" type="range" title="Adjust daily ad spend" className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-blue-500" />
                                <div className="flex justify-between text-xs font-mono text-gray-500">
                                    <span>1 SOL</span>
                                    <span>50 SOL</span>
                                </div>
                            </div>
                        </div>

                        <Button className="w-full py-6">Deploy New Campaign Strategy</Button>
                    </div>

                    <div className="space-y-6">
                        <h3 className="text-xl font-bold px-4 text-white">Autonomous Activity Logs</h3>
                        <div className="glass rounded-[2rem] overflow-hidden">
                            {logs.length === 0 ? (
                                <div className="p-6 text-sm font-mono text-gray-500">No marketing activity logged yet.</div>
                            ) : (
                                logs.map((log, i) => (
                                    <div key={i} className="p-6 border-b border-white/5 text-sm font-mono text-gray-400 hover:bg-white/5 transition-colors">
                                        {log}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
