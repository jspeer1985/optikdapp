'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import { optikApi, Product } from '@/lib/api';

export default function ProductsManagement() {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadProducts();
    }, []);

    const loadProducts = async () => {
        try {
            const data = await optikApi.getProducts();
            setProducts(data);
        } catch (error) {
            console.error(error);
            setError('Failed to load products.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async () => {
        const name = window.prompt("Enter product name:");
        if (!name) return;
        const price = window.prompt("Enter price (e.g. 0.5 SOL):", "0.5 SOL");
        const supply = window.prompt("Enter supply:", "100");

        try {
            const newProduct = await optikApi.createProduct({
                name,
                price: price || "0 SOL",
                supply: supply || "Unlimited",
                status: "Draft",
                description: "New Product"
            });
            setProducts([...products, newProduct]);
        } catch {
            setError('Failed to create product.');
        }
    };

    const handleDelete = async (id: string) => {
        if (confirm("Are you sure you want to delete this product?")) {
            await optikApi.deleteProduct(id);
            setProducts(products.filter(p => p.id !== id));
        }
    };

    return (
        <div className="pb-20 px-8 py-10">
            <div className="max-w-7xl mx-auto space-y-8">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2">Product <span className="gradient-text">NFTs</span></h1>
                        <p className="text-gray-400">Manage your minted collections and secondary market royalties.</p>
                    </div>
                    <Button onClick={handleCreate}>+ Create Product</Button>
                </div>

                {error && <p className="text-red-400">{error}</p>}

                {loading ? (
                    <div className="text-center py-20 text-gray-500">Loading products...</div>
                ) : (
                    <div className="grid grid-cols-1 gap-6">
                        {products.map((p) => (
                            <div key={p.id} className="glass p-8 rounded-3xl flex items-center justify-between border-white/5 hover:border-blue-500/30 transition-all">
                                <div className="flex items-center gap-8">
                                    <div className="w-20 h-20 bg-gradient-to-br from-blue-500/20 to-emerald-500/20 rounded-2xl border border-white/10 flex items-center justify-center text-3xl">
                                        📦
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-white">{p.name}</h3>
                                        <div className="flex gap-4 mt-1">
                                            <span className="text-xs text-gray-500 font-mono uppercase">Supply: {p.supply}</span>
                                            <span className="text-xs text-gray-500 font-mono uppercase">Sold: {p.sold}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xl font-black text-blue-400 mb-2">{p.price}</div>
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${p.status === 'Live' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'}`}>
                                        {p.status}
                                    </span>
                                </div>
                                <div className="flex gap-2 ml-8">
                                    <Button size="sm" variant="outline" onClick={() => window.location.href = `/dashboard/products/${p.id}/edit`}>Edit</Button>
                                    <Button size="sm" variant="outline" className="text-red-400 hover:text-red-300 border-red-500/20 hover:bg-red-500/10" onClick={() => handleDelete(p.id)}>Delete</Button>
                                </div>
                            </div>
                        ))}
                        {products.length === 0 && (
                            <div className="text-center py-20 bg-white/5 rounded-3xl border border-white/10">
                                <p className="text-gray-400">No products found. Start by minting a collection.</p>
                            </div>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
}
