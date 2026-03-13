'use client';

import { useState, useEffect } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { Connection, PublicKey, SystemProgram, Transaction } from '@solana/web3.js';

interface Plan {
  id: string;
  name: string;
  priceSol: number;
  priceUsd: number;
  features: string[];
}

export default function PaymentsPage() {
  const { publicKey, sendTransaction, connected } = useWallet();
  const [plans, setPlans] = useState<Record<string, Plan>>({});
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [txStatus, setTxStatus] = useState<string | null>(null);
  const connection = new Connection(process.env.NEXT_PUBLIC_SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com');

  useEffect(() => {
    // Static plans configuration for Solana payments
    setPlans({
      starter: {
        id: 'starter',
        name: 'DApp Starter',
        priceSol: 100,
        priceUsd: 14999,
        features: [
          'Complete DApp Architecture',
          'Smart Contract Templates',
          'Basic Token Integration',
          'Wallet Connection',
          '1 Month Support'
        ]
      },
      professional: {
        id: 'professional',
        name: 'DApp Professional',
        priceSol: 500,
        priceUsd: 74999,
        features: [
          'Everything in Starter',
          'Advanced Smart Contracts',
          'DeFi Integration',
          'NFT Marketplace',
          '3 Months Priority Support',
          'Custom Branding'
        ]
      },
      enterprise: {
        id: 'enterprise',
        name: 'DApp Enterprise',
        priceSol: 1500,
        priceUsd: 224999,
        features: [
          'Everything in Professional',
          'Custom Smart Contract Development',
          'Multi-Chain Deployment',
          'Advanced Security Audit',
          '1 Year Premium Support',
          'White-Label Solution',
          'Dedicated Team'
        ]
      }
    });
    setLoading(false);
  }, []);

  const handleSolanaPayment = async (planId: string) => {
    if (!connected || !publicKey) {
      setError('Please connect your wallet first');
      return;
    }

    setSelectedPlan(planId);
    setError(null);
    setTxStatus(null);

    try {
      const plan = plans[planId];
      const treasuryWallet = new PublicKey(process.env.NEXT_PUBLIC_SOLANA_TREASURY_WALLET || 'DM6Xg5gwCTz7MqSx9PJN7qc76wksTMhUHX7gxR4D6dTV');
      
      // Convert SOL to lamports (1 SOL = 1,000,000,000 lamports)
      const lamports = plan.priceSol * 1_000_000_000;

      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: publicKey,
          toPubkey: treasuryWallet,
          lamports,
        })
      );

      const signature = await sendTransaction(transaction, connection);
      
      setTxStatus(`Transaction sent! Signature: ${signature}`);
      
      // Wait for confirmation
      const confirmation = await connection.confirmTransaction(signature, 'confirmed');
      
      if (confirmation.value.err) {
        throw new Error('Transaction failed');
      }

      setTxStatus(`Payment successful! Redirecting...`);
      
      // Redirect to creation page after successful payment
      setTimeout(() => {
        window.location.href = `/create-dapp?tier=${encodeURIComponent(planId)}&payment=solana&tx=${signature}`;
      }, 2000);

    } catch (error) {
      console.error('Payment error:', error);
      setError(error instanceof Error ? error.message : 'Payment failed. Please try again.');
    } finally {
      setSelectedPlan(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading payment plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your DApp Plan - Pay with SOL
          </h1>
          <p className="text-xl text-gray-600">
            Transform your e-commerce store into a Web3 powerhouse
          </p>
          <p className="text-sm text-purple-600 mt-2 font-semibold">
            🔥 Pay with Solana - No fiat fees, instant settlement
          </p>
          {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
          {txStatus && <p className="text-sm text-green-600 mt-3">{txStatus}</p>}
        </div>

        {Object.keys(plans).length === 0 ? (
          <div className="max-w-2xl mx-auto rounded-2xl bg-white p-8 text-center shadow-lg">
            <p className="text-gray-700">No payment plans are available right now.</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {Object.entries(plans).map(([planId, plan]) => (
            <div
              key={planId}
              className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow border border-gray-100"
            >
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h2>
                <div className="text-4xl font-bold text-purple-600">
                  {plan.priceSol} SOL
                  <span className="text-lg text-gray-500 block">~${plan.priceUsd.toLocaleString()} USD</span>
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-gray-700">
                    <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSolanaPayment(planId)}
                disabled={selectedPlan === planId || !connected}
                className={`w-full py-3 px-6 rounded-xl font-semibold transition-colors disabled:cursor-not-allowed ${
                  !connected 
                    ? 'bg-gray-400 text-white cursor-not-allowed' 
                    : 'bg-purple-600 text-white hover:bg-purple-700 disabled:bg-gray-400'
                }`}
              >
                {!connected ? (
                  'Connect Wallet First'
                ) : selectedPlan === planId ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing Payment...
                  </span>
                ) : (
                  'Pay with SOL'
                )}
              </button>
            </div>
            ))}
          </div>
        )}

        <div className="mt-12 text-center">
          <div className="bg-white rounded-xl p-6 max-w-2xl mx-auto shadow-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              How to Pay with Solana
            </h3>
            <div className="text-sm text-gray-600 space-y-2">
              <p>1. Connect your Solana wallet (Phantom, Solflare, etc.)</p>
              <p>2. Select your desired DApp plan</p>
              <p>3. Click &quot;Pay with SOL&quot; and approve the transaction</p>
              <p>4. Your DApp creation access will be activated instantly</p>
            </div>
            <div className="mt-4 p-3 bg-purple-50 rounded-lg">
              <p className="text-xs text-purple-700">
                <strong>Treasury Address:</strong> DM6Xg5gwCTz7MqSx9PJN7qc76wksTMhUHX7gxR4D6dTV
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
