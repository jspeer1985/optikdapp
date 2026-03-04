'use client';

import dynamic from 'next/dynamic';
import { useWallet } from '@solana/wallet-adapter-react';
import { useWalletModal } from '@solana/wallet-adapter-react-ui';
import { useCallback, useMemo } from 'react';

// SSR-safe import of the modal trigger button
const WalletMultiButton = dynamic(
    async () => (await import('@solana/wallet-adapter-react-ui')).WalletMultiButton,
    { ssr: false }
);

interface ConnectWalletProps {
    className?: string;
    /** If true, renders a full custom-styled button; otherwise renders the default WalletMultiButton */
    custom?: boolean;
}

/**
 * ConnectWallet — renders a smart wallet connection button.
 *
 * When `custom` is false (default) it delegates to WalletMultiButton from
 * @solana/wallet-adapter-react-ui, which handles the full connect/disconnect
 * modal lifecycle automatically.
 *
 * When `custom` is true it renders a bespoke button that opens the wallet
 * modal or disconnects, with a short visible address while connected.
 */
export default function ConnectWallet({ className = '', custom = false }: ConnectWalletProps) {
    const { connected, publicKey, disconnect, connecting } = useWallet();
    const { setVisible } = useWalletModal();

    const shortAddress = useMemo(() => {
        if (!publicKey) return null;
        const addr = publicKey.toBase58();
        return `${addr.slice(0, 4)}…${addr.slice(-4)}`;
    }, [publicKey]);

    const handleClick = useCallback(() => {
        if (connected) {
            disconnect().catch(console.error);
        } else {
            setVisible(true);
        }
    }, [connected, disconnect, setVisible]);

    if (!custom) {
        // Default: use the upstream library button (handles Phantom, Solflare, etc.)
        return (
            <WalletMultiButton
                className={`!rounded-2xl !font-bold !h-12 !px-8 !transition-all ${className}`}
            />
        );
    }

    // Custom styled button
    return (
        <button
            onClick={handleClick}
            disabled={connecting}
            title={connected ? `Connected: ${publicKey?.toBase58()} — click to disconnect` : 'Connect Wallet'}
            className={`
                inline-flex items-center gap-2
                rounded-2xl px-6 py-3 font-bold text-sm
                transition-all duration-200
                ${connected
                    ? 'bg-emerald-500/15 border border-emerald-500/40 text-emerald-400 hover:bg-red-500/15 hover:border-red-500/40 hover:text-red-400'
                    : 'bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-600/30'
                }
                ${connecting ? 'opacity-60 cursor-wait' : 'cursor-pointer'}
                ${className}
            `}
        >
            {connecting ? (
                <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Connecting…
                </>
            ) : connected ? (
                <>
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    {shortAddress}
                    <span className="opacity-50 text-xs">(disconnect)</span>
                </>
            ) : (
                <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="2" y="7" width="20" height="14" rx="2" />
                        <path d="M16 14a2 2 0 1 1 0-0.001" />
                        <path d="M2 10h20" />
                        <path d="M6 7V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2" />
                    </svg>
                    Connect Wallet
                </>
            )}
        </button>
    );
}
