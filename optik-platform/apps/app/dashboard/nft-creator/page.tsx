'use client';

import { useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import Button from '@/components/ui/Button';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function NFTCreator() {
  const { publicKey } = useWallet();
  const [name, setName] = useState('');
  const [symbol, setSymbol] = useState('OPTK');
  const [description, setDescription] = useState('');
  const [royaltyBps, setRoyaltyBps] = useState(500);
  const [backingAmount, setBackingAmount] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [nftImage, setNftImage] = useState<string | null>(null);
  const [nftImageFile, setNftImageFile] = useState<File | null>(null);
  const [metadataUrl, setMetadataUrl] = useState<string | null>(null);

  const handleNftImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be smaller than 10MB.');
      return;
    }
    setError(null);
    setNftImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setNftImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handlePrepare = async () => {
    if (!name || !description) {
      setError('Name and description are required.');
      return;
    }
    if (!nftImageFile) {
      setError('Upload an image to continue.');
      return;
    }

    setProcessing(true);
    setStatus('Uploading assets and generating metadata...');
    setError(null);
    setMetadataUrl(null);

    try {
      const form = new FormData();
      form.append('name', name);
      form.append('symbol', symbol);
      form.append('description', description);
      form.append('seller_fee_basis_points', String(royaltyBps));
      form.append('backing_amount', String(backingAmount));
      form.append('image', nftImageFile);

      const response = await fetch(`${API_BASE_URL}/api/v1/nft/prepare`, {
        method: 'POST',
        body: form,
        credentials: 'include',
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to prepare NFT');
      }

      const data = await response.json();
      setMetadataUrl(data.metadata_url || null);
      setStatus('NFT metadata prepared successfully.');
    } catch (err: any) {
      setError(err.message || 'Failed to prepare NFT.');
      setStatus(null);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="container mx-auto max-w-6xl pb-20">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-black text-white mb-2">NFT Studio</h1>
          <p className="text-gray-400">Create NFT metadata and publish assets to IPFS.</p>
        </div>
        <div className="text-xs text-gray-500 font-mono">
          Wallet: {publicKey ? publicKey.toBase58() : 'Not connected'}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div className="space-y-8">
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10">
            <div className="mb-6">
              <label className="block text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">Asset Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-4 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">Symbol</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                className="w-full px-4 py-4 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            <div className="mb-8">
              <label className="block text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-4 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors min-h-[150px]"
              />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-8">
              <div>
                <label className="block text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">Royalties (bps)</label>
                <input
                  type="number"
                  value={royaltyBps}
                  onChange={(e) => setRoyaltyBps(Number(e.target.value))}
                  className="w-full px-4 py-4 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">Backing (OPTIK)</label>
                <input
                  type="number"
                  value={backingAmount}
                  onChange={(e) => setBackingAmount(Number(e.target.value))}
                  className="w-full px-4 py-4 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            {status && (
              <div className="mb-6 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-200 text-sm">
                {status}
              </div>
            )}
            {error && (
              <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handlePrepare}
              disabled={processing || !name}
              className="w-full py-5 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-2xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-widest text-sm shadow-xl shadow-blue-600/20"
            >
              {processing ? 'Preparing...' : 'Prepare NFT Metadata'}
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-8">
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10 flex flex-col items-center justify-center text-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>
            <div className="w-full max-w-sm aspect-square bg-gradient-to-br from-gray-900 to-black rounded-3xl mb-8 flex items-center justify-center border border-dashed border-white/20 relative overflow-hidden group shadow-2xl hover:border-blue-500/50 transition-all cursor-pointer">
              <label className="absolute inset-0 flex items-center justify-center cursor-pointer z-10">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleNftImageUpload}
                  className="hidden"
                />
                <div className="text-center">
                  {nftImage ? (
                    <img
                      src={nftImage}
                      alt="NFT Preview"
                      className="w-full h-full object-cover rounded-3xl"
                    />
                  ) : (
                    <div className="space-y-4">
                      <span className="text-6xl block group-hover:scale-125 transition-transform duration-500 drop-shadow-2xl">📸</span>
                      <div className="space-y-2">
                        <p className="text-sm font-bold text-white">Click to Upload NFT Image</p>
                        <p className="text-xs text-gray-400">PNG, JPG, or GIF (Max 10MB)</p>
                      </div>
                    </div>
                  )}
                </div>
              </label>
            </div>
            <div className="w-full max-w-sm text-left px-2">
              <h3 className="text-2xl font-bold text-white mb-2">{name || 'Asset Name'}</h3>
              <p className="text-sm text-gray-400 line-clamp-3 leading-relaxed">{description || 'Asset description will appear here.'}</p>
              {metadataUrl && (
                <a className="text-blue-400 text-xs font-bold uppercase tracking-widest mt-4 inline-block" href={metadataUrl} target="_blank" rel="noreferrer">
                  View metadata
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
