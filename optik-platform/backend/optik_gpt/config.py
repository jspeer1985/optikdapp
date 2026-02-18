"""
Configuration for Optik GPT - The Smartest DApp Creation Assistant
"""

# System prompts and knowledge base
OPTIK_GPT_SYSTEM_PROMPT = """You are Optik GPT, the world's leading AI assistant for decentralized application (DApp) creation powered by Anthropic's Claude.

## Your Core Values:
- **Accuracy First**: Every response is verified and never contains false information
- **DApp Expertise**: Deep knowledge of blockchain, smart contracts, tokenomics, and DApp ecosystems
- **Revenue Minded**: Help merchants build profitable, sustainable DApps with monetization strategies
- **Passionate Educator**: Share enthusiasm for decentralized technology and Web3 innovation
- **Action Oriented**: Provide actionable steps, not just theories

## Your Areas of Excellence:
1. **Smart Contract Development**: Solidity, Solana programs, contract architecture
2. **Tokenomics Design**: Fair token distribution, incentive mechanisms, sustainability
3. **DApp Architecture**: Full-stack design, scalability, security best practices
4. **Merchant Tools**: Store deployment, payment integration, sales optimization
5. **Community Building**: Launch strategies, user acquisition, engagement tactics
6. **Compliance & Security**: Legal considerations, auditing, security protocols
7. **Fundraising & Pitch**: Investor narratives, tokenomics for VCs, financial modeling

## Response Guidelines:
- Always cite specific protocols/standards when referencing blockchain tech
- Provide code examples in Solidity, JavaScript/TypeScript, or Python as appropriate
- Estimate gas costs, transaction fees, and financial implications
- Suggest revenue streams: transaction fees, staking rewards, governance tokens
- When unsure, explicitly state knowledge limitations and suggest verification sources
- Format responses with clear structure: Context → Analysis → Actionable Steps → Revenue Opportunity

## Response Format:
For complex questions, use this structure:
1. **Understanding** - Show you grasped the question
2. **Technical Details** - Provide accurate, specific information
3. **Implementation** - Step-by-step guidance
4. **Revenue Model** - How to monetize this feature
5. **Risks & Mitigation** - Be thorough about gotchas
6. **Next Steps** - Concrete actions to take

You are deployed in Optik, a platform that enables merchants to build sustainable DApps with integrated payment processing, staking, and token economics. Every suggestion should consider this ecosystem.
"""

DApp_KNOWLEDGE_BASE = {
    "smart_contracts": {
        "ethereum": {
            "standards": ["ERC-20 (fungible tokens)", "ERC-721 (NFTs)", "ERC-1155 (multi-token)", "ERC-4626 (tokenized vaults)"],
            "best_practices": [
                "Always use OpenZeppelin contracts for battle-tested implementations",
                "Implement access control (Ownable, AccessControl)",
                "Use SafeMath or Solidity 0.8+ checked math",
                "Separate logic from storage for upgradeability",
                "Implement reentrancy guards for external calls"
            ],
            "gas_optimization": "Use assembly for critical loops, minimize storage reads, batch operations"
        },
        "solana": {
            "standards": ["SPL Token (fungible)", "SPL Token 2022 (extensions)", "Metaplex (NFTs/digital assets)"],
            "best_practices": [
                "Use Anchor framework for secure contract development",
                "Implement proper signer verification",
                "Handle PDAs (Program Derived Addresses) correctly",
                "Minimize CPI (Cross-Program Invocation) calls",
                "Validate all account ownership and data"
            ],
            "cost_advantage": "Sub-cent transaction costs, no gas limits like Ethereum"
        }
    },
    "tokenomics": {
        "distribution": {
            "fair_launch": "5% team (4yr vesting), 10% advisors (2yr vesting), 15% treasury, 70% community/users",
            "presale": "Limit to 5-10% of total supply, use vesting to prevent dumps",
            "governance": "Consider quadratic voting or delegation to prevent whale control"
        },
        "incentive_mechanisms": {
            "staking_rewards": "2-5% APY sustainable on platform revenue, not new inflation",
            "fee_sharing": "Distribute trading/transaction fees to stakers and LPs",
            "liquidity_mining": "Bootstrap liquidity with 3-6 month campaigns, then wind down"
        },
        "sustainability": "Revenue must support tokenomics. Calculate: daily inflation < daily protocol revenue"
    },
    "payment_integration": {
        "stripe": "Process fiat payments, instant settlement, built-in compliance",
        "crypto_native": "Accept SOL, ETH, USDC - lower fees than Stripe, faster settlement",
        "hybrid": "Fiat on-ramp via Stripe, crypto payments to smart contracts",
        "fee_structure": "Platform takes 3-5% as sustainable recurring revenue"
    },
    "compliance": {
        "jurisdictions": {
            "us": "Treat tokens as securities (Howey Test), register or qualify for exemptions",
            "eu": "MiCA regulation - need authorization if offering digital assets",
            "asia": "Singapore (MAS) most friendly, Japan (FSA) regulated, China prohibited"
        },
        "legal_musts": [
            "Terms of Service clarifying non-custody",
            "Privacy Policy for data handling",
            "Disclaimer that you're not a money transmitter (if true)",
            "AML/KYC if handling >$10k USD equivalent"
        ]
    },
    "security": {
        "smart_contract": ["Audit by trail-of-bits or reputable firm", "Formal verification for critical functions", "Bug bounty program"],
        "operational": ["Multi-sig wallets for treasury", "Timelock contracts for upgrades", "Circuit breakers for anomalies"],
        "user_education": ["Clear documentation of risks", "Warnings about impermanent loss", "Security best practices"]
    }
}

MONETIZATION_STRATEGIES = {
    "transaction_fees": {
        "description": "Take small percentage of trades/transfers",
        "optimal_rate": "0.1% - 0.5% depending on market",
        "revenue_potential": "High volume = sustainable revenue",
        "implementation": "Router contract takes fee before execution"
    },
    "premium_features": {
        "description": "Advanced analytics, API access, white-label solution",
        "pricing_model": "Tiered: Basic (free), Pro ($99/mo), Enterprise (custom)",
        "revenue_potential": "Recurring, predictable MRR",
        "implementation": "Rate limiting, API keys, feature flags"
    },
    "staking_incentives": {
        "description": "Users stake your token, earn percentage of protocol fees",
        "optimal_apy": "5-10% APY sustainable",
        "revenue_potential": "Reduces token selling pressure, loyal community",
        "implementation": "Reward contract distributing weekly/monthly"
    },
    "data_monetization": {
        "description": "Anonymized trading data, aggregated insights (non-identifying)",
        "pricing_model": "Enterprise data subscriptions",
        "revenue_potential": "$10k-50k/mo per customer",
        "implementation": "Data warehouse, reporting API"
    },
    "governance_services": {
        "description": "Protocol governance as a service for other DAOs",
        "pricing_model": "% of governance treasury or fixed fee",
        "revenue_potential": "Scales with ecosystem partnerships",
        "implementation": "Snapshot integration, governance tooling"
    }
}

# Intent categories that trigger specialized agents
INTENT_CATEGORIES = {
    "contract_development": ["write contract", "deploy contract", "smart contract", "solidity", "anchor"],
    "tokenomics": ["token design", "apy", "staking", "rewards", "vesting", "distribution"],
    "launch_preparation": ["launch", "go live", "audit", "testnet", "mainnet"],
    "fundraising": ["raise funds", "pitch", "investor", "valuation", "token sale"],
    "marketing": ["marketing", "promotion", "community", "growth", "virality"],
    "technical_architecture": ["architecture", "scalability", "performance", "database"],
    "revenue_optimization": ["revenue", "monetization", "fees", "margin", "profit"],
    "general_knowledge": ["explain", "how does", "what is", "tell me", "learn"]
}
