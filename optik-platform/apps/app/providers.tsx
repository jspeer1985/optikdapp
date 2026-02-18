'use client';

import { ReactNode } from 'react';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { AuthProvider } from './context/AuthContext';

// Cache wallet adapters to avoid recreating
const wallets = [
    new PhantomWalletAdapter(),
    new SolflareWalletAdapter(),
];

export default function Providers({
    children,
}: {
    children: ReactNode;
}) {
    return (
        <ConnectionProvider endpoint={process.env.NEXT_PUBLIC_SOLANA_RPC || 'https://api.devnet.solana.com'}>
            <WalletProvider wallets={wallets} autoConnect={false} onError={(error) => {
                console.error('Wallet error:', error);
                // Handle rate limiting gracefully
                if (error.name === 'WalletConnectionError') {
                    console.warn('Connection failed - possibly rate limited');
                }
            }}>
                <WalletModalProvider>
                    <AuthProvider>
                        {children}
                    </AuthProvider>
                </WalletModalProvider>
            </WalletProvider>
        </ConnectionProvider>
    );
}
