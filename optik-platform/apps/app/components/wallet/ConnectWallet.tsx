'use client';

import dynamic from 'next/dynamic';
import { useWallet } from '@solana/wallet-adapter-react';
import { useMemo } from 'react';

const WalletMultiButton = dynamic(
    async () => (await import('@solana/wallet-adapter-react-ui')).WalletMultiButton,
    { ssr: false }
);

export default function ConnectWallet() {
    const { wallet, connected } = useWallet();
    const walletName = useMemo(() => wallet?.adapter.name, [wallet]);

    return (
        <div className="flex items-center justify-center">
            <WalletMultiButton className="!bg-blue-600 !text-white !rounded-xl !h-12 !font-bold !px-8 hover:opacity-90 transition-all shadow-lg shadow-blue-600/20" />
            {connected && walletName && (
                <span className="ml-4 text-sm text-green-600">
                    ✓ {walletName}
                </span>
            )}
        </div>
    );
}
