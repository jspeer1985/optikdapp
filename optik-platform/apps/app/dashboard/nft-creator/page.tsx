'use client';

import { useState, useCallback } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { Connection, Transaction } from '@solana/web3.js';
import { shortenAddress } from '@/lib/solana';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const RPC_ENDPOINT = process.env.NEXT_PUBLIC_RPC_ENDPOINT || 'https://api.devnet.solana.com';

type MintResult = {
  mint: string;
  metadata_url: string;
  name: string;
  tx_signature?: string;
};

type Phase = 'form' | 'preparing' | 'sign' | 'minting' | 'done' | 'error';

export default function NFTCreator() {
  const { publicKey, sendTransaction, connected } = useWallet();

  // Form fields
  const [name, setName] = useState('');
  const [symbol, setSymbol] = useState('OPTK');
  const [description, setDescription] = useState('');
  const [royaltyBps, setRoyaltyBps] = useState(500);
  const [backingAmount, setBackingAmount] = useState(0);
  const [supply, setSupply] = useState(1);
  const [collection, setCollection] = useState('');
  const [nftImage, setNftImage] = useState<string | null>(null);
  const [nftImageFile, setNftImageFile] = useState<File | null>(null);

  // Attributes
  const [attrs, setAttrs] = useState<{ trait_type: string; value: string }[]>([]);
  const [attrKey, setAttrKey] = useState('');
  const [attrVal, setAttrVal] = useState('');

  // Mint state
  const [phase, setPhase] = useState<Phase>('form');
  const [error, setError] = useState<string | null>(null);
  const [mintResult, setMintResult] = useState<MintResult | null>(null);
  const [metadataUrl, setMetadataUrl] = useState<string | null>(null);
  const [mintTx, setMintTx] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const handleImageUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) { setError('Upload an image file.'); return; }
    if (file.size > 10 * 1024 * 1024) { setError('Image must be under 10MB.'); return; }
    setError(null);
    setNftImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setNftImage(reader.result as string);
    reader.readAsDataURL(file);
  }, []);

  const addAttr = () => {
    if (!attrKey.trim() || !attrVal.trim()) return;
    setAttrs(prev => [...prev, { trait_type: attrKey.trim(), value: attrVal.trim() }]);
    setAttrKey('');
    setAttrVal('');
  };

  const removeAttr = (i: number) => setAttrs(prev => prev.filter((_, idx) => idx !== i));

  const handleMint = async () => {
    if (!name || !description) { setError('Name and description are required.'); return; }
    if (!nftImageFile) { setError('Upload an image to continue.'); return; }
    if (!connected || !publicKey) { setError('Connect your wallet first.'); return; }

    setError(null);
    setPhase('preparing');
    setProgress(10);

    try {
      // Step 1: Upload image + generate metadata on IPFS
      const form = new FormData();
      form.append('name', name);
      form.append('symbol', symbol);
      form.append('description', description);
      form.append('seller_fee_basis_points', String(royaltyBps));
      form.append('backing_amount', String(backingAmount));
      form.append('supply', String(supply));
      form.append('wallet', publicKey.toBase58());
      if (collection) form.append('collection', collection);
      if (attrs.length) form.append('attributes', JSON.stringify(attrs));
      form.append('image', nftImageFile);

      setProgress(25);
      const prepRes = await fetch(`${API_BASE_URL}/api/v1/nft/prepare`, {
        method: 'POST',
        body: form,
        credentials: 'include',
      });

      if (!prepRes.ok) {
        const txt = await prepRes.text();
        throw new Error(txt || 'Prepare failed');
      }

      const prepData = await prepRes.json() as {
        metadata_url: string;
        mint_tx?: string;
        mint?: string;
        unsigned_tx?: string;
      };

      setMetadataUrl(prepData.metadata_url);
      setProgress(50);

      // Step 2: If backend returned an unsigned transaction, sign & submit it
      if (prepData.unsigned_tx) {
        setPhase('sign');
        const connection = new Connection(RPC_ENDPOINT, 'confirmed');
        const txBuffer = Buffer.from(prepData.unsigned_tx, 'base64');
        const tx = Transaction.from(txBuffer);
        tx.feePayer = publicKey;

        setProgress(65);
        const sig = await sendTransaction(tx, connection);
        setMintTx(sig);
        setProgress(80);

        // Step 3: Confirm on-chain
        setPhase('minting');
        const confirmation = await connection.confirmTransaction(sig, 'confirmed');
        if (confirmation.value.err) throw new Error('On-chain confirmation failed');

        setProgress(95);
        setMintResult({
          mint: prepData.mint || '',
          metadata_url: prepData.metadata_url,
          name,
          tx_signature: sig,
        });
      } else {
        // Backend handled minting (custodial mode)
        setMintResult({
          mint: prepData.mint || '',
          metadata_url: prepData.metadata_url,
          name,
        });
      }

      setProgress(100);
      setPhase('done');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Minting failed.');
      setPhase('error');
    }
  };

  const reset = () => {
    setPhase('form');
    setError(null);
    setMintResult(null);
    setMetadataUrl(null);
    setMintTx(null);
    setProgress(0);
    setName('');
    setDescription('');
    setRoyaltyBps(500);
    setBackingAmount(0);
    setSupply(1);
    setCollection('');
    setAttrs([]);
    setNftImage(null);
    setNftImageFile(null);
  };

  const isProcessing = phase === 'preparing' || phase === 'sign' || phase === 'minting';
  const royaltyPct = (royaltyBps / 100).toFixed(1);

  // ── Success screen ──────────────────────────────────────────────────────────
  if (phase === 'done' && mintResult) {
    return (
      <div className="container mx-auto max-w-2xl pb-20 pt-10">
        <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-10 border border-emerald-500/30 text-center space-y-6">
          <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto">
            <span className="text-4xl">✅</span>
          </div>
          <h2 className="text-3xl font-black text-white">NFT Minted!</h2>
          <p className="text-gray-400">Your NFT <span className="text-white font-bold">{mintResult.name}</span> is live on Solana.</p>

          {mintResult.mint && (
            <div className="bg-black/30 rounded-2xl p-4 text-left space-y-2">
              <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Mint Address</p>
              <p className="font-mono text-sm text-blue-300 break-all">{mintResult.mint}</p>
            </div>
          )}
          {mintResult.tx_signature && (
            <div className="bg-black/30 rounded-2xl p-4 text-left space-y-2">
              <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Transaction</p>
              <a
                href={`https://explorer.solana.com/tx/${mintResult.tx_signature}?cluster=devnet`}
                target="_blank"
                rel="noreferrer"
                className="font-mono text-xs text-blue-400 hover:underline break-all"
              >
                {mintResult.tx_signature}
              </a>
            </div>
          )}
          {mintResult.metadata_url && (
            <a
              href={mintResult.metadata_url}
              target="_blank"
              rel="noreferrer"
              className="inline-block text-xs text-purple-400 hover:underline"
            >
              View IPFS Metadata →
            </a>
          )}

          <div className="flex gap-4 justify-center pt-4">
            <button
              onClick={reset}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-2xl hover:scale-[1.02] transition-all"
            >
              Mint Another
            </button>
            <a
              href="/dashboard/products"
              className="px-8 py-3 bg-white/10 text-white font-bold rounded-2xl hover:bg-white/20 transition-all"
            >
              View Collection
            </a>
          </div>
        </div>
      </div>
    );
  }

  // ── Main form ───────────────────────────────────────────────────────────────
  return (
    <div className="container mx-auto max-w-6xl pb-20">
      {/* Header */}
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-black text-white mb-2">NFT Studio</h1>
          <p className="text-gray-400">Mint NFTs on Solana, backed by OPTIK token.</p>
        </div>
        <div className="flex items-center gap-4">
          {connected && publicKey ? (
            <div className="text-xs text-gray-400 font-mono bg-white/5 px-3 py-2 rounded-xl border border-white/10">
              {shortenAddress(publicKey.toBase58())}
            </div>
          ) : (
            <WalletMultiButton className="!bg-blue-600 !rounded-2xl !text-sm !font-bold" />
          )}
        </div>
      </div>

      {/* Progress bar during minting */}
      {isProcessing && (
        <div className="mb-8 bg-white/5 rounded-2xl p-6 border border-white/10 space-y-3">
          <div className="flex justify-between text-sm font-bold">
            <span className="text-white">
              {phase === 'preparing' && 'Uploading to IPFS...'}
              {phase === 'sign' && 'Waiting for wallet signature...'}
              {phase === 'minting' && 'Confirming on-chain...'}
            </span>
            <span className="text-blue-400">{progress}%</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          {mintTx && (
            <p className="text-xs text-gray-500 font-mono">TX: {mintTx.slice(0, 20)}...</p>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Left column — form */}
        <div className="space-y-6">

          {/* Core metadata */}
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10 space-y-5">
            <h2 className="text-sm font-black uppercase tracking-widest text-gray-400">Asset Info</h2>

            <div>
              <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Name *</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Optik Genesis #1"
                className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Symbol</label>
                <input
                  type="text"
                  value={symbol}
                  onChange={e => setSymbol(e.target.value.toUpperCase())}
                  className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Supply</label>
                <input
                  type="number"
                  min={1}
                  max={10000}
                  value={supply}
                  onChange={e => setSupply(Math.max(1, Number(e.target.value)))}
                  className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Description *</label>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Describe your NFT..."
                rows={3}
                className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Collection Address (optional)</label>
              <input
                type="text"
                value={collection}
                onChange={e => setCollection(e.target.value)}
                placeholder="Verified Metaplex collection mint"
                className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors font-mono text-sm"
              />
            </div>
          </div>

          {/* OPTIK Economics */}
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10 space-y-5">
            <h2 className="text-sm font-black uppercase tracking-widest text-gray-400">OPTIK Economics</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">
                  Royalties — {royaltyPct}%
                </label>
                <input
                  type="range"
                  min={0}
                  max={2000}
                  step={50}
                  value={royaltyBps}
                  onChange={e => setRoyaltyBps(Number(e.target.value))}
                  className="w-full accent-blue-500"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0%</span><span>20%</span>
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">OPTIK Backing</label>
                <input
                  type="number"
                  min={0}
                  value={backingAmount}
                  onChange={e => setBackingAmount(Math.max(0, Number(e.target.value)))}
                  className="w-full px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white focus:border-blue-500 focus:outline-none transition-colors"
                />
                <p className="text-xs text-gray-600 mt-1">OPTIK tokens locked in NFT</p>
              </div>
            </div>

            {/* Economics summary */}
            <div className="bg-black/30 rounded-2xl p-4 grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-gray-500 mb-1">Royalty</p>
                <p className="font-bold text-blue-400">{royaltyPct}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Backing</p>
                <p className="font-bold text-purple-400">{backingAmount} OPTK</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Supply</p>
                <p className="font-bold text-white">{supply.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Attributes */}
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10 space-y-4">
            <h2 className="text-sm font-black uppercase tracking-widest text-gray-400">Traits / Attributes</h2>

            {attrs.length > 0 && (
              <div className="space-y-2">
                {attrs.map((a, i) => (
                  <div key={i} className="flex items-center gap-2 bg-black/20 rounded-xl px-4 py-2">
                    <span className="text-xs text-gray-400 flex-1">{a.trait_type}</span>
                    <span className="text-xs text-white font-bold flex-1">{a.value}</span>
                    <button onClick={() => removeAttr(i)} className="text-red-400 hover:text-red-300 text-xs px-2">✕</button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Trait"
                value={attrKey}
                onChange={e => setAttrKey(e.target.value)}
                className="flex-1 px-3 py-2 rounded-xl bg-black/20 border border-white/10 text-white text-sm focus:border-blue-500 focus:outline-none"
              />
              <input
                type="text"
                placeholder="Value"
                value={attrVal}
                onChange={e => setAttrVal(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addAttr()}
                className="flex-1 px-3 py-2 rounded-xl bg-black/20 border border-white/10 text-white text-sm focus:border-blue-500 focus:outline-none"
              />
              <button
                onClick={addAttr}
                className="px-4 py-2 bg-blue-600/30 border border-blue-500/30 text-blue-300 rounded-xl text-sm font-bold hover:bg-blue-600/50 transition-colors"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Right column — preview + mint */}
        <div className="flex flex-col gap-6">

          {/* Image upload / preview */}
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10">
            <div className="relative w-full aspect-square bg-gradient-to-br from-gray-900 to-black rounded-3xl flex items-center justify-center border-2 border-dashed border-white/20 hover:border-blue-500/50 transition-all cursor-pointer overflow-hidden group shadow-2xl">
              <label className="absolute inset-0 flex items-center justify-center cursor-pointer z-10">
                <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                {nftImage ? (
                  <img src={nftImage} alt="NFT Preview" className="w-full h-full object-cover rounded-3xl" />
                ) : (
                  <div className="text-center space-y-3">
                    <span className="text-5xl block group-hover:scale-110 transition-transform">🖼️</span>
                    <p className="text-sm font-bold text-white">Click to Upload Image</p>
                    <p className="text-xs text-gray-500">PNG, JPG, GIF — Max 10MB</p>
                  </div>
                )}
              </label>
              {nftImage && (
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-3xl">
                  <p className="text-white text-sm font-bold">Change Image</p>
                </div>
              )}
            </div>

            {/* NFT card preview */}
            <div className="mt-6 p-5 bg-black/30 rounded-2xl border border-white/5">
              <h3 className="text-xl font-bold text-white mb-1">{name || 'Asset Name'}</h3>
              <p className="text-xs text-gray-400 mb-3 line-clamp-2">{description || 'Description preview'}</p>
              {attrs.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {attrs.slice(0, 4).map((a, i) => (
                    <span key={i} className="text-xs px-2 py-1 bg-blue-500/10 border border-blue-500/20 text-blue-300 rounded-lg">
                      {a.trait_type}: {a.value}
                    </span>
                  ))}
                  {attrs.length > 4 && <span className="text-xs text-gray-500">+{attrs.length - 4} more</span>}
                </div>
              )}
            </div>
          </div>

          {/* Wallet + Mint CTA */}
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 border border-white/10 space-y-4">
            {!connected && (
              <div className="mb-2">
                <p className="text-xs text-yellow-400 mb-3 font-bold uppercase tracking-wider">Wallet Required to Mint</p>
                <WalletMultiButton className="!w-full !justify-center !bg-white/10 !rounded-2xl !text-sm !font-bold !border !border-white/20" />
              </div>
            )}

            {error && (
              <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
                {error}
              </div>
            )}

            {metadataUrl && phase !== 'done' && (
              <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 p-3 text-xs">
                <p className="text-gray-400 mb-1">Metadata uploaded:</p>
                <a href={metadataUrl} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline break-all font-mono">
                  {metadataUrl}
                </a>
              </div>
            )}

            <button
              onClick={handleMint}
              disabled={isProcessing || !name || !nftImageFile}
              className="w-full py-5 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-black rounded-2xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100 uppercase tracking-widest text-sm shadow-xl shadow-blue-600/20"
            >
              {isProcessing ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {phase === 'preparing' && 'Preparing...'}
                  {phase === 'sign' && 'Sign in Wallet...'}
                  {phase === 'minting' && 'Confirming...'}
                </span>
              ) : connected ? 'Mint NFT on Solana' : 'Connect Wallet to Mint'}
            </button>

            <p className="text-xs text-gray-600 text-center">
              Powered by Metaplex · OPTIK-backed royalties · Devnet
            </p>
          </div>

          {/* OPTIK info card */}
          <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/20 rounded-3xl p-6 border border-purple-500/20 space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🔷</span>
              <div>
                <p className="font-bold text-white text-sm">OPTIK Token Integration</p>
                <p className="text-xs text-gray-400">Lock OPTIK as economic backing in your NFT</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="bg-black/30 rounded-xl p-3">
                <p className="text-gray-500 mb-1">On-Chain</p>
                <p className="text-white font-bold">Solana</p>
              </div>
              <div className="bg-black/30 rounded-xl p-3">
                <p className="text-gray-500 mb-1">Storage</p>
                <p className="text-white font-bold">IPFS</p>
              </div>
              <div className="bg-black/30 rounded-xl p-3">
                <p className="text-gray-500 mb-1">Standard</p>
                <p className="text-white font-bold">Metaplex</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
