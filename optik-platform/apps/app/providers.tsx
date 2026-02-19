'use client';

import { ReactNode, useMemo } from 'react';
import {
    WalletAdapterNetwork,
    WalletConnectionError,
    WalletNotReadyError,
    WalletReadyState,
    type Adapter,
} from '@solana/wallet-adapter-base';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { clusterApiUrl } from '@solana/web3.js';
import { AuthProvider } from './context/AuthContext';

const WALLET_STORAGE_KEY = 'optik_wallet_name';

function resolveNetwork(): WalletAdapterNetwork {
    const configuredNetwork = (process.env.NEXT_PUBLIC_SOLANA_NETWORK || '').toLowerCase();

    if (configuredNetwork === 'mainnet' || configuredNetwork === WalletAdapterNetwork.Mainnet) {
        return WalletAdapterNetwork.Mainnet;
    }

    if (configuredNetwork === WalletAdapterNetwork.Testnet) {
        return WalletAdapterNetwork.Testnet;
    }

    return WalletAdapterNetwork.Devnet;
}

function resolveRpcEndpoint(network: WalletAdapterNetwork): string {
    return process.env.NEXT_PUBLIC_RPC_ENDPOINT || process.env.NEXT_PUBLIC_SOLANA_RPC || clusterApiUrl(network);
}

async function shouldAutoConnect(adapter: Adapter): Promise<boolean> {
    return (
        adapter.readyState === WalletReadyState.Installed ||
        adapter.readyState === WalletReadyState.Loadable
    );
}

export default function Providers({
    children,
}: {
    children: ReactNode;
}) {
    const network = useMemo(resolveNetwork, []);
    const endpoint = useMemo(() => resolveRpcEndpoint(network), [network]);
    const wallets = useMemo(
        () => [
            new PhantomWalletAdapter(),
            new SolflareWalletAdapter({ network }),
        ],
        [network]
    );

    return (
        <ConnectionProvider endpoint={endpoint}>
            <WalletProvider
                wallets={wallets}
                autoConnect={shouldAutoConnect}
                localStorageKey={WALLET_STORAGE_KEY}
                onError={(error, adapter) => {
                    const adapterName = adapter?.name || 'unknown';
                    console.error(`[wallet:${adapterName}]`, error);

                    if (
                        error instanceof WalletNotReadyError ||
                        error instanceof WalletConnectionError
                    ) {
                        if (typeof window !== 'undefined') {
                            window.localStorage.removeItem(WALLET_STORAGE_KEY);
                        }
                    }
                }}
            >
                <WalletModalProvider>
                    <AuthProvider>
                        {children}
                    </AuthProvider>
                </WalletModalProvider>
            </WalletProvider>
        </ConnectionProvider>
    );
}
