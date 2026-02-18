'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';

export default function RoyaltiesPage({ params }: { params: { id: string } }) {
    const router = useRouter();
    const [royalty, setRoyalty] = useState(5);

    const handleSave = () => {
        // In a real implementation, this would update the on-chain metadata or database config
        alert(`Royalties for product ${params.id} updated to ${royalty}%`);
        router.back();
    };

    return (
        <div className="p-10 text-white max-w-2xl mx-auto pb-20">
            <h1 className="text-3xl font-black mb-8">Manage <span className="gradient-text">Royalties</span></h1>
            <p className="mb-8 text-gray-400">Set secondary market fees for this collection. These are enforced on-chain.</p>

            <div className="glass p-8 space-y-6 rounded-3xl border border-white/10">
                <div>
                    <label className="block text-sm mb-2 text-gray-400 font-bold uppercase tracking-wider">Royalty Percentage (%)</label>
                    <div className="flex items-center gap-4">
                        <input
                            type="range"
                            title="Royalty percentage"
                            min="0"
                            max="15"
                            value={royalty}
                            onChange={(e) => setRoyalty(Number(e.target.value))}
                            className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer"
                        />
                        <span className="text-2xl font-bold w-16 text-right">{royalty}%</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">Recommended: 5-10%</p>
                </div>

                <div className="bg-blue-500/10 p-4 rounded-xl border border-blue-500/20 text-blue-400 text-sm">
                    <span className="font-bold">Note:</span> Royalties are paid automatically to your treasury wallet on every secondary sale.
                </div>

                <div className="flex gap-4 pt-4">
                    <Button onClick={handleSave}>Save Configuration</Button>
                    <Button variant="outline" onClick={() => router.back()}>Cancel</Button>
                </div>
            </div>
        </div>
    );
}
