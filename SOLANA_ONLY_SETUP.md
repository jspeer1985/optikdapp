# Solana-Only Payment Setup

This document outlines the startup procedure and requirements for running Optik Platform with Solana-only payments.

## Overview

The Optik Platform has been configured to accept Solana payments exclusively, disabling Stripe integration for简化启动流程. This reduces regulatory complexity and eliminates fiat payment processing fees.

## Environment Configuration

### Required Environment Variables

```bash
# Solana Configuration
NEXT_PUBLIC_SOLANA_NETWORK=mainnet
NEXT_PUBLIC_SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_TREASURY_WALLET=DM6Xg5gwCTz7MqSx9PJN7qc76wksTMhUHX7gxR4D6dTV
NEXT_PUBLIC_SOLANA_TREASURY_WALLET=DM6Xg5gwCTz7MqSx9PJN7qc76wksTMhUHX7gxR4D6dTV

# Pricing (SOL-based)
NEXT_PUBLIC_STARTER_PRICE_SOL=100
NEXT_PUBLIC_PROFESSIONAL_PRICE_SOL=500
NEXT_PUBLIC_ENTERPRISE_PRICE_SOL=1500
```

### Disabled Payment Gateways

```bash
# Stripe (Disabled)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
```

## Startup Procedure

### 1. Install Dependencies

```bash
cd optik-platform/apps
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local` and ensure:
- Solana treasury wallet is set
- Stripe keys are empty (disabled)
- Network is set to `mainnet` for production

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3003`

## Payment Flow

### User Experience

1. **Wallet Connection**: Users connect their Solana wallet (Phantom, Solflare, etc.)
2. **Plan Selection**: Choose from Starter (100 SOL), Professional (500 SOL), or Enterprise (1500 SOL)
3. **Payment**: Direct SOL transfer to treasury wallet
4. **Confirmation**: Transaction verified on-chain
5. **Access**: Immediate DApp creation access

### Technical Flow

1. Client creates Solana transaction using `@solana/web3.js`
2. Transaction sends SOL to treasury wallet address
3. Transaction confirmed on Solana network
4. User redirected to `/create-dapp` with payment verification
5. Backend validates transaction signature

## Security Considerations

### Treasury Wallet Security

- **Production**: Use hardware wallet or multi-sig
- **Private Key**: Never expose in frontend code
- **Monitoring**: Monitor treasury wallet for unauthorized transactions

### Transaction Verification

- Verify transaction signature on backend
- Confirm transaction is finalized on-chain
- Validate amount matches plan pricing
- Prevent replay attacks

## Benefits of Solana-Only Setup

### Advantages

1. **No Regulatory Compliance**: Crypto-to-crypto transactions
2. **Lower Fees**: No Stripe processing fees (2.9% + $0.30)
3. **Instant Settlement**: On-chain confirmation in seconds
4. **Web3 Native**: Aligns with decentralized ethos
5. **Global Access**: No fiat currency restrictions

### Trade-offs

1. **Limited Audience**: Only crypto users
2. **Price Volatility**: SOL price fluctuations
3. **Technical Barrier**: Requires wallet setup

## Future Expansion

### Adding Stripe Later

When ready to add fiat payments:

1. Configure Stripe keys in `.env.local`
2. Update payment page to show both options
3. Implement Stripe webhook handlers
4. Add subscription billing capabilities

### Multi-Chain Support

Potential future additions:
- Ethereum/USDC payments
- Other L1 blockchains
- Stable coin options

## Troubleshooting

### Common Issues

1. **Wallet Connection Failed**
   - Check wallet is installed and unlocked
   - Verify network configuration
   - Clear browser cache

2. **Transaction Failed**
   - Insufficient SOL balance
   - Network congestion
   - Incorrect treasury address

3. **Payment Not Recognized**
   - Transaction not yet confirmed
   - Backend verification error
   - Incorrect amount sent

### Debug Commands

```bash
# Check Solana balance
solana balance DM6Xg5gwCTz7MqSx9PJN7qc76wksTMhUHX7gxR4D6dTV

# Verify transaction
solana confirm <TRANSACTION_SIGNATURE>

# Check network status
solana cluster-version
```

## Monitoring

### Key Metrics

- Daily transaction volume
- Conversion rates by plan
- Treasury wallet balance
- Failed transaction rate

### Alerts

- Low treasury balance
- Unusual transaction patterns
- Network connectivity issues

## Support

For issues with Solana payments:
1. Check wallet connection
2. Verify transaction on Solscan
3. Contact support with transaction signature

---

*Last Updated: March 2026*
*Version: 1.0*
