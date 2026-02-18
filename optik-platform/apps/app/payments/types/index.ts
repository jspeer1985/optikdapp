export interface Dapp {
  id: string;
  name: string;
  description: string;
  category: string;
  tier: TierType;
  walletAddress: string;
  createdAt: Date;
}

export type TierType = 'starter' | 'growth' | 'pro' | 'enterprise' | 'premium' | 'platinum';

export interface NFTMetadata {
  name: string;
  description: string;
  image: string;
  attributes: Array<{ trait_type: string; value: string }>;
}

export interface MerchantData {
  id: string;
  tier: TierType;
  revenue: number;
  transactions: number;
  fees: number;
  optikBalance: number;
}
