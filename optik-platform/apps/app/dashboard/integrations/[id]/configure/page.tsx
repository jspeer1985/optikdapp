'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { optikApi, Integration } from '@/lib/api';
import Button from '@/components/ui/Button';

export default function ConfigureIntegrationPage({ params }: { params: { id: string } }) {
    const router = useRouter();
    const [integration, setIntegration] = useState<Integration | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        optikApi.getIntegrations().then(ints => {
            const i = ints.find(p => p.id === params.id);
            if (i) setIntegration(i);
            setLoading(false);
        });
    }, [params.id]);

    const handleDisconnect = async () => {
        if (!integration) return;
        if (confirm("Disconnect this integration?")) {
            try {
                await optikApi.disconnectIntegration(integration.id);
                router.push('/dashboard/integrations');
            } catch (e) {
                setError('Failed to disconnect integration.');
            }
        }
    };

    if (loading) return <div className="p-10 text-white text-center">Loading...</div>;
    if (!integration) return <div className="p-10 text-white text-center">Integration not found</div>;

    return (
        <div className="p-10 text-white max-w-2xl mx-auto pb-20">
            <h1 className="text-3xl font-black mb-8">Configure <span className="gradient-text">{integration.name}</span></h1>
            {error && <p className="text-red-400 mb-4">{error}</p>}

            <div className="glass p-8 space-y-6 rounded-3xl border border-white/10">
                <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl flex items-center gap-4">
                    <span className="text-2xl">✅</span>
                    <div>
                        <h3 className="font-bold text-emerald-400">Connected & Active</h3>
                        <p className="text-sm text-gray-400">Data synchronization is enabled.</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <h3 className="font-bold uppercase text-sm text-gray-400 tracking-wider">Settings</h3>
                    <div className="p-6 bg-white/5 rounded-xl border border-white/10 space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-300">Auto-Sync Inventory</span>
                            <div className="w-10 h-6 bg-emerald-500 rounded-full relative cursor-pointer"><div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div></div>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-300">Webhooks Enabled</span>
                            <div className="w-10 h-6 bg-emerald-500 rounded-full relative cursor-pointer"><div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div></div>
                        </div>
                    </div>
                </div>

                <div className="flex gap-4 pt-4 border-t border-white/10">
                    <Button variant="outline" className="text-red-400 hover:text-red-300 border-red-500/20 hover:bg-red-500/10" onClick={handleDisconnect}>Disconnect Integration</Button>
                    <Button variant="outline" onClick={() => router.back()}>Back</Button>
                </div>
            </div>
        </div>
    );
}
