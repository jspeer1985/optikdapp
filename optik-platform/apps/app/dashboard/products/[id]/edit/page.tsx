'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { optikApi, Product } from '../../../../lib/api';
import Button from '../../../../components/ui/Button';

export default function EditProductPage({ params }: { params: { id: string } }) {
    const router = useRouter();
    const [product, setProduct] = useState<Product | null>(null);
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({ name: '', price: '', supply: '' });
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        optikApi.getProducts().then(products => {
            const p = products.find(p => p.id === params.id);
            if (p) {
                setProduct(p);
                setFormData({ name: p.name, price: p.price, supply: p.supply });
            }
            setLoading(false);
        });
    }, [params.id]);

    const handleSave = async () => {
        if (!product) return;
        try {
            await optikApi.updateProduct(product.id, formData);
            router.push('/dashboard/products');
        } catch (e) {
            setError('Failed to update product.');
        }
    };

    if (loading) return <div className="p-10 text-white text-center">Loading...</div>;
    if (!product) return <div className="p-10 text-white text-center">Product not found</div>;

    return (
        <div className="p-10 text-white max-w-2xl mx-auto pb-20">
            <h1 className="text-3xl font-black mb-8">Edit <span className="gradient-text">{product.name}</span></h1>
            {error && <p className="text-red-400 mb-4">{error}</p>}
            <div className="glass p-8 space-y-6 rounded-3xl border border-white/10">
                <div>
                    <label className="block text-sm mb-2 text-gray-400 font-bold uppercase tracking-wider">Product Name</label>
                    <input
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm mb-2 text-gray-400 font-bold uppercase tracking-wider">Price (SOL)</label>
                    <input
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
                        value={formData.price}
                        onChange={e => setFormData({ ...formData, price: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm mb-2 text-gray-400 font-bold uppercase tracking-wider">Supply</label>
                    <input
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
                        value={formData.supply}
                        onChange={e => setFormData({ ...formData, supply: e.target.value })}
                    />
                </div>
                <div className="flex gap-4 pt-4">
                    <Button onClick={handleSave}>Save Changes</Button>
                    <Button variant="outline" onClick={() => router.back()}>Cancel</Button>
                </div>
            </div>
        </div>
    );
}
