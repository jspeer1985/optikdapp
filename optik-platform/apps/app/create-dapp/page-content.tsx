'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useWallet } from '@solana/wallet-adapter-react';
import ConnectWallet from '@/components/wallet/ConnectWallet';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

import { api, optikApi } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface ConversionResult {
  store: {
    name: string;
    url: string;
    platform: string;
  };
  products: Array<{
    id: string;
    title: string;
    price_sol: number;
    price: number;
    currency: string;
  }>;
}

export default function StoreConverter() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { connected, publicKey } = useWallet();
  const { user } = useAuth();
  const [storeUrl, setStoreUrl] = useState('');
  const [platform, setPlatform] = useState<'shopify' | 'woocommerce'>('shopify');
  const [email, setEmail] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'pending' | 'scraping' | 'analyzing' | 'converting' | 'generating_nfts' | 'completed' | 'failed' | 'deploying' | 'deployed'>('idle');
  const [deploymentStep, setDeploymentStep] = useState('');
  const [deploymentSys, setDeploymentSys] = useState('');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [deployedAddress, setDeployedAddress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [businessLogo, setBusinessLogo] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  const checkoutSuccess = searchParams.get('checkout') === 'success';
  const selectedTier = (searchParams.get('tier') || 'basic').toLowerCase();
  const hasPlan = checkoutSuccess || !!searchParams.get('tier');

  const tierConfigs: Record<string, { share: string, agents: string[] }> = {
    'basic': { share: '3%', agents: ['Core Optik AI'] },
    'growth': { share: '5%', agents: ['Marketing Agent', 'Product Agent'] },
    'global': { share: '9%', agents: ['Marketing Agent', 'Product Agent', 'UI Design Agent'] },
    'scale': { share: '12%', agents: ['Marketing Agent', 'Product Agent', 'UI Design Agent', 'Security Agent'] },
    'elite': { share: '15%', agents: ['Marketing Agent', 'Product Agent', 'UI Design Agent', 'Security Agent', 'NFT Assistant', 'Optik AI+'] }
  };

  const currentTier = tierConfigs[selectedTier] || tierConfigs.basic;

  useEffect(() => {
    if (user?.email) {
      setEmail(user.email);
    }
  }, [user]);

  const fetchPreview = async (id: string) => {
    const data = await api<any>(`/api/v1/convert/preview/${id}`);
    setResult({
      store: data.store,
      products: data.products || [],
    });
  };

  // Poll for status if we have a jobId
  useEffect(() => {
    let interval: any;
    if (jobId && !['completed', 'failed', 'deployed'].includes(status)) {
      interval = setInterval(async () => {
        try {
          const response = await optikApi.getConversionStatus(jobId);
          setStatus(response.status);
          setProgress(response.progress);
          setDeploymentStep(response.message);

          if (response.status === 'completed') {
            await fetchPreview(jobId);
            clearInterval(interval);
          } else if (response.status === 'failed') {
            setError(response.error || 'Conversion failed');
            clearInterval(interval);
          } else if (response.status === 'deployed') {
            setDeployedAddress(response.dapp_url || null);
            if (jobId) localStorage.setItem('optik_last_dapp_id', jobId);
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [jobId, status, storeUrl]);

  const handleConvert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!connected) return;
    if (!email) {
      setError('Email is required.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await optikApi.submitConversion({
        store_url: storeUrl,
        platform,
        tier: selectedTier,
        email,
        api_key: apiKey || undefined,
        api_secret: apiSecret || undefined,
      });
      setJobId(response.job_id);
      setStatus('scraping');
      setProgress(10);
    } catch (err: any) {
      setError(err.message || 'Failed to submit conversion');
    } finally {
      setLoading(false);
    }
  };

  const handleLaunch = async () => {
    if (!jobId) return;
    setStatus('deploying');
    setProgress(0);
    setError(null);

    try {
      await optikApi.startDeployment(jobId);
      // Status polling will take over from here
    } catch (err: any) {
      setError(err.message || 'Failed to start deployment');
      setStatus('failed');
    }
  };

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file is an image
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Logo file must be smaller than 5MB');
        return;
      }

      setBusinessLogo(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeLogo = () => {
    setBusinessLogo(null);
    setLogoPreview(null);
  };

  // If no plan selected, show the payment gate
  if (!hasPlan) {
    return (
      <div className="min-h-screen pt-32 pb-20 bg-transparent">
        <div className="container mx-auto px-4 max-w-2xl">
          <div className="text-center">
            <div className="w-24 h-24 bg-amber-500/20 text-amber-400 rounded-full flex items-center justify-center text-5xl mx-auto mb-8 shadow-[0_0_60px_rgba(245,158,11,0.3)]">
              💳
            </div>
            <h1 className="text-4xl md:text-5xl font-black mb-6 tracking-tight text-white">
              Select a <span className="gradient-text">Payment Plan</span>
            </h1>
            <p className="text-xl text-gray-400 mb-4 max-w-lg mx-auto leading-relaxed">
              Before you can create and deploy your Dapp, you need to choose a subscription plan that fits your needs.
            </p>
            <p className="text-sm text-gray-500 mb-12">
              Each plan includes different transaction fees, Dapp limits, and support tiers.
            </p>

            <div className="space-y-4">
              <Link
                href="/checkout"
                className="block w-full max-w-md mx-auto px-10 py-5 bg-blue-600 text-white rounded-2xl text-lg font-bold hover:opacity-90 transition-all shadow-xl shadow-blue-500/20 hover:-translate-y-1 text-center"
              >
                Choose Subscription Tier ($0 Setup)
              </Link>
              <Link
                href="/"
                className="block w-full max-w-md mx-auto px-10 py-5 bg-white/5 text-white rounded-2xl text-lg font-bold hover:bg-white/10 transition-all border border-white/5 text-center"
              >
                Return to Dashboard
              </Link>
            </div>

            <div className="mt-16 grid grid-cols-3 gap-4">
              {[
                { icon: '💎', label: 'Rev Share Model' },
                { icon: '🤖', label: 'AI Powered' },
                { icon: '🚀', label: 'Free Setup' },
              ].map((item, i) => (
                <div key={i} className="p-4 bg-white/5 rounded-2xl border border-white/10 text-center">
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <div className="text-xs text-gray-500 font-medium">{item.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-32 pb-20 bg-transparent">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-black mb-6 tracking-tight text-white">
            Convert your Store to <span className="gradient-text">Web3</span>
          </h1>
          <p className="text-xl text-gray-400">
            Current Tier: <span className="text-blue-400 font-bold uppercase">{selectedTier}</span> ({currentTier.share} Revenue Share)
          </p>
        </div>

        <div className="mb-12 flex flex-wrap justify-center gap-4">
          {currentTier.agents.map((agent, i) => (
            <div key={i} className="px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs font-bold text-blue-400 flex items-center gap-2 animate-pulse">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              {agent} ACTIVE
            </div>
          ))}
        </div>

        <Card className="p-8 md:p-12 border-white/10 glass shadow-2xl">
          {!connected ? (
            <div className="text-center py-12 text-white">
              <div className="text-5xl mb-6">🔒</div>
              <h2 className="text-2xl font-bold mb-4">Wallet Connection Required</h2>
              <p className="text-gray-400 mb-8">Connect your Solana wallet to start the conversion process.</p>
              <ConnectWallet />
            </div>
          ) : status === 'idle' ? (
            <form onSubmit={handleConvert} className="space-y-8">
              {error && (
                <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200 text-sm">
                  {error}
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
                    Contact Email
                  </label>
                  <Input
                    type="email"
                    placeholder="you@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-14 bg-white/5 border-white/10"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
                    Platform
                  </label>
                  <div className="flex gap-4">
                    <button
                      type="button"
                      onClick={() => setPlatform('shopify')}
                      className={`flex-1 py-4 rounded-2xl text-xs font-black uppercase tracking-widest ${platform === 'shopify' ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-400 border border-white/10'}`}
                    >
                      Shopify
                    </button>
                    <button
                      type="button"
                      onClick={() => setPlatform('woocommerce')}
                      className={`flex-1 py-4 rounded-2xl text-xs font-black uppercase tracking-widest ${platform === 'woocommerce' ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-400 border border-white/10'}`}
                    >
                      WooCommerce
                    </button>
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
                  Store URL
                </label>
                <div className="flex flex-col md:flex-row gap-4">
                  <Input
                    type="url"
                    placeholder="https://your-shopify-store.com"
                    value={storeUrl}
                    onChange={(e) => setStoreUrl(e.target.value)}
                    required
                    className="flex-1 h-16 text-lg bg-white/5 border-white/10"
                  />
                  <Button type="submit" className="h-16 px-12 text-lg font-bold group">
                    Convert Now
                    <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                  </Button>
                </div>
              </div>

              {platform === 'woocommerce' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
                      WooCommerce API Key
                    </label>
                    <Input
                      type="text"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="h-14 bg-white/5 border-white/10"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
                      WooCommerce API Secret
                    </label>
                    <Input
                      type="password"
                      value={apiSecret}
                      onChange={(e) => setApiSecret(e.target.value)}
                      className="h-14 bg-white/5 border-white/10"
                    />
                  </div>
                </div>
              )}

              {/* Business Logo Upload */}
              <div className="pt-8 border-t border-white/5">
                <div className="flex items-center justify-between mb-6">
                  <label className="block text-sm font-bold uppercase tracking-wider text-gray-400">
                    🎨 Business Branding
                  </label>
                  {businessLogo && (
                    <span className="text-xs text-green-400 font-bold">✓ Logo Added</span>
                  )}
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                  {/* Logo Preview */}
                  <div className="flex-shrink-0">
                    <div className="w-32 h-32 rounded-2xl border-2 border-dashed border-white/20 flex items-center justify-center bg-white/5 overflow-hidden">
                      {logoPreview ? (
                        <img
                          src={logoPreview}
                          alt="Business Logo"
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="text-center">
                          <div className="text-4xl mb-2">🏢</div>
                          <p className="text-xs text-gray-500">Logo Preview</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Upload Section */}
                  <div className="flex-1 flex flex-col justify-center">
                    <p className="text-sm text-gray-400 mb-4">
                      Add your business logo to brand the NFT and store. Supported formats: PNG, JPG, SVG (Max 5MB)
                    </p>
                    <div className="flex flex-col sm:flex-row gap-3">
                      <label className="relative flex-1">
                        <Button
                          type="button"
                          variant="outline"
                          className="w-full h-12 cursor-pointer hover:bg-white/10"
                          onClick={() => document.getElementById('logo-input')?.click()}
                        >
                          {businessLogo ? '✎ Change Logo' : '+ Add Logo Now'}
                        </Button>
                        <input
                          id="logo-input"
                          type="file"
                          accept="image/*"
                          onChange={handleLogoUpload}
                          className="hidden"
                        />
                      </label>
                      {businessLogo && (
                        <Button
                          type="button"
                          variant="outline"
                          className="h-12 px-6 hover:bg-red-500/10 hover:border-red-500/30"
                          onClick={removeLogo}
                        >
                          ✕ Remove
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 border-t border-white/5">
                <div className="flex items-center gap-3 text-sm text-gray-400">
                  <span className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold">1</span>
                  Scrape Products
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-400">
                  <span className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold">2</span>
                  AI Optimization
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-400">
                  <span className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold">3</span>
                  Deploy to Solana
                </div>
              </div>
            </form>
          ) : status === 'deploying' ? (
            <div className="py-12 text-center space-y-8 text-white">
              <div className="relative w-48 h-48 mx-auto">
                <div className="absolute inset-0 rounded-full border-4 border-green-500/20 animate-pulse"></div>
                <div className="absolute inset-0 rounded-full border-t-4 border-green-500 animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center text-3xl font-bold text-green-500">
                  {progress}%
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-bold mb-2">Deploying to Solana...</h2>
                <div className="flex flex-col items-center gap-2">
                  <p className="text-gray-400 font-mono text-sm">{deploymentStep}</p>
                  <span className="text-[10px] font-black text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded tracking-widest uppercase mb-1">
                    SYS CODE: {deploymentSys || 'PENDING'}
                  </span>
                </div>
              </div>
            </div>
          ) : status === 'deployed' ? (
            <div className="py-12 text-center space-y-8 animate-in fade-in zoom-in duration-700">
              <div className="w-24 h-24 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-5xl mx-auto mb-6 shadow-[0_0_50px_rgba(59,130,246,0.5)]">
                🚀
              </div>
              <h2 className="text-4xl font-black gradient-text">Dapp is Live!</h2>
              <p className="text-gray-400 max-w-md mx-auto">
                Your decentralized store has been successfully deployed to the Solana blockchain.
              </p>
              <div className="p-6 bg-white/5 rounded-2xl border border-white/10 text-left font-mono text-xs break-all text-white">
                <div className="text-blue-400 mb-2 uppercase font-bold text-[10px]">Storefront URL</div>
                {deployedAddress ? (
                  <a className="text-blue-300 underline" href={deployedAddress} target="_blank" rel="noreferrer">
                    {deployedAddress}
                  </a>
                ) : (
                  'Pending'
                )}
              </div>
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
                <Button
                  onClick={() => {
                    setStatus('idle');
                    setJobId(null);
                    setProgress(0);
                    setResult(null);
                    setDeployedAddress(null);
                  }}
                  variant="outline"
                  className="h-14 px-8"
                >
                  Create New Store
                </Button>
                <Button
                  onClick={() => {
                    window.scrollTo(0, 0);
                    router.push(`/dapps/${jobId}`);
                  }}
                  className="h-14 px-8 shadow-xl shadow-blue-500/20 hover:scale-105 transition-transform"
                >
                  View Live Simulation
                </Button>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-white">
              {status === 'failed' ? (
                <div className="space-y-6">
                  <div className="w-20 h-20 bg-red-500/20 text-red-400 rounded-full flex items-center justify-center text-4xl mx-auto">
                    !
                  </div>
                  <h2 className="text-2xl font-bold">Conversion Failed</h2>
                  <p className="text-gray-400">{error || 'We could not complete the conversion.'}</p>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setStatus('idle');
                      setJobId(null);
                      setProgress(0);
                      setResult(null);
                      setError(null);
                    }}
                    className="h-12 px-6"
                  >
                    Try Again
                  </Button>
                </div>
              ) : status !== 'completed' ? (
                <div className="space-y-8 text-white">
                  <div className="relative w-48 h-48 mx-auto">
                    <div className="absolute inset-0 rounded-full border-4 border-blue-500/20 animate-pulse"></div>
                    <div className="absolute inset-0 rounded-full border-t-4 border-blue-500 animate-spin"></div>
                    <div className="absolute inset-0 flex items-center justify-center text-3xl font-bold">
                      {progress}%
                    </div>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold mb-2 capitalize">{status}...</h2>
                    <p className="text-gray-400">
                      {status === 'scraping' ? 'Extracting products and images from your store.' : 'Our AI is optimizing your content for the Web3 ecosystem.'}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-8 animate-in fade-in zoom-in duration-500">
                  <div className="w-24 h-24 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center text-5xl mx-auto mb-6">
                    ✓
                  </div>
                  <h2 className="text-3xl font-bold text-white">Conversion Complete!</h2>
                  <p className="text-gray-400 max-w-md mx-auto">
                    We've successfully converted your <strong>{result?.store.platform}</strong> store. Your Web3-optimized products are ready for deployment.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
                    {result?.products.map((p, i) => (
                      <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10 text-left">
                        <div className="font-bold text-white">{p.title}</div>
                        <div className="text-blue-400 font-mono">{p.price_sol} SOL</div>
                      </div>
                    ))}
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setStatus('idle');
                        setJobId(null);
                        setProgress(0);
                        setResult(null);
                      }}
                      className="h-14 px-8"
                    >
                      Try Another
                    </Button>
                    <Button
                      onClick={handleLaunch}
                      className="h-14 px-8 bg-green-600 hover:bg-green-700"
                    >
                      Launch on Solana
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Info Section */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-2 gap-12 text-white">
          <div>
            <h3 className="text-2xl font-bold mb-4">Why convert to Web3?</h3>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <span className="text-blue-500 font-bold">✦</span>
                <span className="text-gray-400">Eliminate high transaction fees with Solana's fraction-of-a-cent costs.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-blue-500 font-bold">✦</span>
                <span className="text-gray-400">Every product becomes an NFT, enabling verifiable ownership and secondary markets.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-blue-500 font-bold">✦</span>
                <span className="text-gray-400">Instant global settlements. No more 30-day merchant holding periods.</span>
              </li>
            </ul>
          </div>
          <div className="bg-blue-500/5 rounded-3xl p-8 border border-blue-500/10 flex flex-col justify-center">
            <h3 className="text-2xl font-bold mb-4">Your Tier: <span className="uppercase text-blue-400">{selectedTier}</span></h3>
            <p className="text-gray-400 mb-6">You are giving <strong>{currentTier.share}</strong> revenue share in exchange for <strong>{currentTier.agents.length} AI Agents</strong> working for you.</p>
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
              <span className="font-bold text-lg text-white">Active Agents</span>
              <span className="text-2xl font-black text-blue-400">{currentTier.agents.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
