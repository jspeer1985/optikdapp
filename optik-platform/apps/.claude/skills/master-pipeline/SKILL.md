# Master AI Agent Pipeline

Orchestrate and develop the Optik Platform's complete dApp and NFT e-commerce conversion pipeline. Use this skill when working on any agent, pipeline, integration, or deployment component.

---

## Architecture Overview

```
                    ┌─────────────────────────┐
                    │      FastAPI Server      │
                    │   backend/api/main.py    │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                   │
    ┌─────────▼──────┐  ┌───────▼────────┐  ┌──────▼───────┐
    │  Conversion    │  │   OptikGPT     │  │   Growth     │
    │  Pipeline      │  │   Assistant    │  │   Agent      │
    │  (Background)  │  │   (Real-time)  │  │  (Campaigns) │
    └────────┬───────┘  └───────┬────────┘  └──────┬───────┘
             │                  │                   │
    ┌────────▼──────────────────▼───────────────────▼────────┐
    │                   AGENT LAYER                           │
    │  ScraperAgent → AnalyzerAgent → ConverterAgent →       │
    │  NFTGenerator → DeployerAgent                          │
    └────────┬──────────────────┬───────────────────┬────────┘
             │                  │                   │
    ┌────────▼────────┐ ┌──────▼──────┐  ┌────────▼────────┐
    │  Integrations   │ │  Utilities  │  │   Payments      │
    │  solana.py      │ │  database   │  │   stripe_client │
    │  shopify.py     │ │  redis      │  │   webhook       │
    │  woocommerce.py │ │  nft_gen    │  │   ledger        │
    └─────────────────┘ └─────────────┘  └─────────────────┘
```

## File Map

### Agents (`backend/agents/`)

| File | Class | Status | Purpose |
|------|-------|--------|---------|
| `scraper_agent.py` | `ShopifyScraperAgent` | Working | Scrapes Shopify `/products.json` |
| `scraper_agent.py` | `WooCommerceScraperAgent` | Stub | Placeholder, returns empty |
| `analyzer_agent.py` | `StoreAnalyzerAgent` | Heuristic | Rule-based tier recommendation (LLM initialized but unused) |
| `converter_agent.py` | `Web3ConverterAgent` | Simulated | Appends "(Genesis Edition)", hardcodes 0.5 SOL price |
| `deployer_agent.py` | `SolanaDeployerAgent` | Simulated | Returns random hex as tx_hash, 2s sleep |
| `growth_agent.py` | `GrowthAgent` | Simulated | Hardcoded recipient counts, fake tx_hash |

### Pipelines (`backend/pipelines/`)

| File | Class | Purpose |
|------|-------|---------|
| `conversion_pipeline.py` | `ConversionPipeline` | Orchestrates: scrape -> analyze -> convert -> NFT gen |
| `deployment_pipeline.py` | `DeploymentPipeline` | Orchestrates: balance check -> init store -> deploy collection -> OPTIK backing |
| `scraping_pipeline.py` | `ScrapingPipeline` | Universal ingestion via `UniversalIngestionManager` |
| `ingestion_manager.py` | `UniversalIngestionManager` | Platform detection + routing (Shopify/Woo/MetaScraper) |
| `ingestion_manager.py` | `MetaScraperAgent` | JSON-LD / Schema.org product extraction for generic sites |

### Integrations (`backend/integrations/`)

| File | Class | Status |
|------|-------|--------|
| `solana.py` | `SolanaIntegration` | Partially real: balance checks work, transfers implemented, deployment simulated |
| `shopify.py` | - | Not audited |
| `woocommerce.py` | - | Not audited |

### Utilities (`backend/utils/`)

| File | Class | Status |
|------|-------|--------|
| `smart_contract_deployer.py` | `SmartContractDeployer` | Simulated: uses System Program ID, returns random hex |
| `nft_generator.py` | `NFTGenerator` | Working: generates Metaplex-compatible JSON metadata |
| `database.py` | `DatabaseManager` | SQLite active, MongoDB/Postgres supported |
| `redis_manager.py` | `RedisManager` | Job status caching |
| `image_processor.py` | `ImageProcessor` | Not audited |
| `auth.py` | - | API key verification |
| `aws_secrets.py` | - | AWS Secrets Manager integration |

### OptikGPT (`backend/optik_gpt/`)

| File | Class | Status |
|------|-------|--------|
| `assistant/conversation_engine.py` | `OptikAssistant` | Working: keyword intent routing -> mock action agents |
| `assistant/intent_router.py` | `route_intent()` | Keyword matching (not LLM-based) |
| `assistant/claude_engine.py` | - | Not audited |
| `services/knowledge_manager.py` | - | Not audited |

### Payments (`backend/payments/`)

| File | Class | Status |
|------|-------|--------|
| `stripe_client.py` | `StripeClient` | Working: Checkout Sessions, Connect payments with fee splitting |
| `subscription_manager.py` | - | Not audited |
| `webhook_handler.py` | - | Not audited |
| `invoice_generator.py` | - | Not audited |
| `ledger.py` | - | Not audited |

## Conversion Pipeline - Detailed Flow

### Stage 1: SCRAPE (progress 10%)
```
Input:  store_url, platform, api_key?, api_secret?
Agent:  ShopifyScraperAgent or WooCommerceScraperAgent
Action: GET {url}/products.json (Shopify) or WooCommerce API
Output: { url, platform, products: [{ id, title, description, price, images }] }
Timeout: 30s -> falls back to mock data
```

### Stage 2: ANALYZE (progress 40%)
```
Input:  store_data from Stage 1
Agent:  StoreAnalyzerAgent
Action: Heuristic: >50 products = "Bulk NFT Collection" / "premium" keyword = "Luxury"
Output: { strategy, recommended_tier, product_count, platform_origin }
Timeout: 20s -> falls back to basic analysis
```

### Stage 3: CONVERT (progress 60%)
```
Input:  store_data, analysis, tier
Agent:  Web3ConverterAgent
Action: For each product (max 5): append "(Genesis Edition)", set 0.5 SOL price
Tier -> agent mapping:
  basic:  [Core Optik AI]
  growth: [Marketing, Product]
  global: [Marketing, Product, UI Design]
  scale:  [Marketing, Product, UI Design, Security]
  elite:  [Marketing, Product, UI Design, Security, NFT, Optik AI+]
Output: { products, tier, active_agents, preview_url }
Timeout: 30s
```

### Stage 4: GENERATE NFTs (progress 80%)
```
Input:  web3_store from Stage 3
Agent:  NFTGenerator (static methods)
Action: For each product: create Metaplex-compatible JSON metadata
Output: [{ name, symbol, description, seller_fee_basis_points, image, attributes, properties }]
Timeout: 20s
```

### Stage 5: DEPLOY (progress 100%)
```
Input:  conversion_data, config { wallet_address, fee_bps, enable_nft, backing_amount }
Agent:  DeploymentPipeline -> SolanaIntegration + SmartContractDeployer
Action:
  1. Check wallet balance (real RPC call)
  2. Initialize store PDA (simulated)
  3. Deploy NFT collection (simulated)
  4. Pair with $OPTIK backing (simulated)
Output: { status, network, tx_hash, merchant_pda, collection, backing_mode, dapp_url }
Fee mapping: basic=300bps, growth=500bps, global=900bps, scale=1200bps, elite=1500bps
```

## Status Tracking

Redis stores real-time job status:
```
pending -> scraping -> analyzing -> converting -> generating_nfts -> deploying -> deployed
                                                                                   |
                                                                                 failed
```

## What's Simulated vs Real

| Component | Real | Simulated |
|-----------|------|-----------|
| Shopify product scraping | Yes (via /products.json) | - |
| WooCommerce scraping | - | Returns empty array |
| Generic site scraping | Yes (JSON-LD extraction) | HTML heuristics stub |
| Platform detection | Yes (HTML keyword matching) | - |
| Store analysis | - | Keyword heuristic, LLM initialized but unused |
| Product conversion | - | String concatenation, hardcoded price |
| NFT metadata generation | Yes (Metaplex JSON format) | - |
| Solana balance check | Yes (real RPC) | - |
| SOL transfers | Yes (real transaction) | - |
| Store account deployment | - | Random hex as PDA |
| NFT collection deployment | - | Random hex as mint |
| OPTIK token backing | - | Random hex as pairing ID |
| Stripe payments | Yes (real API) | - |
| Stripe Connect fee split | Yes (application_fee_amount) | - |
| OptikGPT intent routing | - | Keyword matching (not LLM) |
| Airdrop campaigns | - | Hardcoded recipient counts |
| Staking configuration | - | Static response |

## Development Priorities

### Priority 1: Core Pipeline (Make It Real)
1. **WooCommerce scraper** - Implement WooCommerce REST API integration
2. **Store analyzer** - Wire up the initialized Claude LLM for actual analysis
3. **Product converter** - Use LLM for intelligent Web3 metadata generation
4. **Smart contract deployer** - Deploy actual Anchor program, use real PDAs

### Priority 2: Solana On-Chain
1. **Anchor program** - Write/deploy OptikStore program (initialize_merchant, process_sale, etc.)
2. **Real PDA derivation** - Replace random hex with seeds-based PDAs
3. **NFT minting** - Integrate Metaplex SDK for actual compressed NFT minting
4. **Token pairing** - Implement liquidity pool or locking contract for $OPTIK backing

### Priority 3: Intelligence Layer
1. **OptikGPT** - Replace keyword router with LLM-based intent classification
2. **Growth Agent** - Implement real on-chain airdrop distribution
3. **Staking** - Deploy actual staking program with configurable APY

### Priority 4: Production Readiness
1. **Database migration** - Move from SQLite to PostgreSQL/MongoDB
2. **Authentication** - Implement JWT + wallet signature verification
3. **Testing** - Unit tests for all agents, integration tests for pipeline
4. **Error recovery** - Implement job retry logic and dead letter queue

## Environment Variables Required

### Backend (`backend/.env`)
```
ANTHROPIC_API_KEY=         # Claude API for analyzer/converter agents
OPENAI_API_KEY=            # Alternative LLM provider
SOLANA_RPC_URL=            # Solana RPC (devnet or mainnet)
SOLANA_WALLET_PRIVATE_KEY= # Platform wallet (base58 or JSON array)
STRIPE_SECRET_KEY=         # Stripe payments
STRIPE_WEBHOOK_SECRET=     # Stripe webhook verification
PINATA_API_KEY=            # IPFS storage for NFT metadata
PINATA_SECRET_KEY=         # Pinata auth
DATABASE_URL=              # sqlite:///optik.db (dev) or postgres/mongo (prod)
REDIS_URL=                 # Job status caching
```

### Frontend (`apps/.env.local`)
```
NEXT_PUBLIC_SOLANA_NETWORK=devnet
NEXT_PUBLIC_RPC_ENDPOINT=https://api.devnet.solana.com
NEXT_PUBLIC_PLATFORM_WALLET=      # Platform treasury address
NEXT_PUBLIC_OPTIK_TOKEN_MINT=     # $OPTIK SPL token mint
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=    # Stripe publishable key
```

## Key Commands

```bash
# Start backend
cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
cd apps && npm run dev    # runs on port 3003

# Test conversion pipeline
curl -X POST http://localhost:8000/api/v1/scrape/preview \
  -H "Content-Type: application/json" \
  -d '{"store_url": "https://example.myshopify.com", "platform": "shopify"}'

# Check health
curl http://localhost:8000/health

# Chat with OptikGPT
curl -X POST http://localhost:8000/api/v1/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help", "merchant_id": "test"}'
```
