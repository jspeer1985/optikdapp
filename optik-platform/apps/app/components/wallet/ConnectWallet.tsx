'use client';

import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { useWallet } from '@solana/wallet-adapter-react';

export default function ConnectWallet() {
    const { wallet, connecting, connected } = useWallet();

    return (
        <div className="flex items-center justify-center">
            <WalletMultiButton 
                className="!bg-blue-600 !text-white !rounded-xl !h-12 !font-bold !px-8 hover:opacity-90 transition-all shadow-lg shadow-blue-600/20"
                disabled={connecting}
            />
            {connected && wallet && (
                <span className="ml-4 text-sm text-green-600">
                    ✓ {wallet.adapter.name}
                </span>
            )}
        </div>
    );
}
