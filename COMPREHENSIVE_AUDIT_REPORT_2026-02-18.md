# Comprehensive Audit Report (2026-02-18)

Project: Dapp_Optik
Scope: `optik-platform/apps` (Next.js), `optik-platform/backend` (FastAPI + services), `contracts` (Solidity), `optik-platform/backend/blockchain/programs/optik-store` (Anchor/Solana), root tooling/scripts.
Method: Static code review and route/page inventory. No runtime tests executed.

## Executive Summary
The codebase is large and feature-rich, but several critical and high-impact gaps prevent reliable production use:
- Secrets are committed in the repo (including Stripe test keys). These must be rotated and removed immediately.
- The public pipeline API is wired to a non-existent job service and calls methods that do not exist. This breaks the pipeline endpoints entirely.
- Core blockchain integrations are inconsistent: the EVM router expects a mint function that the NFT contract does not implement, and the Solana deployment flow uses the platform wallet instead of the merchant wallet.
- The verification flow is broken end-to-end (frontend payload doesn’t match backend, and the endpoint is unauthenticated).

Once the above are addressed, the rest of the platform is broadly coherent, with clear separation of UI, API, and pipelines. Several features are “request logging only” or “UI placeholder only,” which is fine if intentional but should be labeled in product UX.

## Inventory: Features and Jobs

### Frontend Pages (Next.js App Router)
Status legend: OK = wired to a working API path; PARTIAL = API exists but data mismatch or missing fields; STUB = UI placeholder/no backend; STATIC = static content only.

| Page | Backend Dependency | Status | Notes |
|---|---|---|---|
| `/` | none | STATIC | Landing page. |
| `/auth` | `/api/v1/auth/*` | OK | Wallet + magic link auth. |
| `/checkout` | `/api/v1/payments/checkout` | OK | Subscription purchase flow. |
| `/payments` | `/api/v1/payments/plans`, `/api/v1/payments/checkout` | OK | Plan listing and checkout. |
| `/create-dapp` | `/api/v1/convert/*`, `/api/v1/deploy/*` | OK | Depends on Pinata + `SOL_USD_PRICE` env. |
| `/store-preview` | `/api/v1/convert/preview`, `/api/v1/convert`, `/api/v1/payments/dapp-payment` | PARTIAL | Preview data lacks merchant wallet/id, causing checkout failures. |
| `/dapps/[id]` | `/api/v1/dapps/{id}`, `/api/v1/payments/dapp-payment` | OK | Uses merchant data from dapp API. |
| `/orchestrator` | `/api/v1/system/status`, `/api/v1/system/proofs`, `/api/v1/convert` | OK | System view + proof log. |
| `/optik-coin` | none | STATIC | Informational. |
| `/whitepaper` | none | STATIC | Informational. |
| `/terms`, `/privacy`, `/shipping`, `/drops`, `/models` | none | STATIC | Informational. |
| `/verify` | `/api/v1/verify` | BROKEN | Frontend payload does not match backend request schema. |

**Dashboard**
| Page | Backend Dependency | Status | Notes |
|---|---|---|---|
| `/dashboard/merchant` | `/api/v1/connect/merchant/me`, `/api/v1/payments/merchant/*`, `/api/v1/dapps` | OK | Relies on Stripe Connect + ledger. |
| `/dashboard/analytics` | `/api/v1/analytics/summary` | OK | Derived from ledger entries. |
| `/dashboard/billing` | `/api/v1/payments/merchant/*`, `/api/v1/connect/merchant/me` | OK | Uses merchant ledger + Connect status. |
| `/dashboard/billing/history` | `/api/v1/payments/invoices` | OK | Pulls Stripe invoices. |
| `/dashboard/billing/subscription` | `/api/v1/payments/subscriptions`, `/api/v1/payments/cancel/{id}` | OK | Stripe subscriptions. |
| `/dashboard/products` | `/api/v1/products/*` | OK | CRUD. |
| `/dashboard/products/[id]/edit` | `/api/v1/products/*` | OK | CRUD; loads full list client-side. |
| `/dashboard/products/[id]/royalties` | none | STUB | UI-only; no backend or on-chain update. |
| `/dashboard/integrations` | `/api/v1/integrations/*` | PARTIAL | Connect/disconnect only updates DB status (no OAuth). |
| `/dashboard/integrations/[id]/configure` | none | STUB | UI-only. |
| `/dashboard/marketing` | `/api/v1/marketing/*` | PARTIAL | Requests stored, no on-chain action. |
| `/dashboard/mobile-app` | `/api/v1/marketing/mobile-app` | PARTIAL | Request logging only. |
| `/dashboard/nft-creator` | `/api/v1/nft/prepare` | OK | Requires Pinata credentials. |
| `/dashboard/security` | `/api/v1/security/*` | PARTIAL | Logs/requests only; no enforcement layer. |
| `/dashboard/liquidity` | `/api/v1/liquidity/*` | PARTIAL | Request logging only. |
| `/dashboard/categories`, `/dashboard/logistics`, `/dashboard/proofs` | none or `/api/v1/system/proofs` | MIXED | Mostly UI; proofs uses API. |

### Backend APIs (FastAPI)
- `/api/v1/auth/*`: Wallet auth, magic link auth, refresh/logout, `me`.
- `/api/v1/payments/*`: Stripe checkout, Connect payments, invoices, webhook, merchant stats.
- `/api/v1/connect/*`: Stripe Connect onboarding and account status.
- `/api/v1/convert/*`: Conversion job submit/status/preview/list.
- `/api/v1/deploy/*`: Deployment start/status.
- `/api/v1/system/*`: Job status counts, proof logs, agent registry.
- `/api/v1/analytics/summary`: Ledger aggregation.
- `/api/v1/marketing/*`: Airdrop/staking/mobile-app request logging.
- `/api/v1/security/*`: Whitelist and freeze requests (logging only).
- `/api/v1/liquidity/*`: Liquidity request logging.
- `/api/v1/nft/prepare`: NFT metadata generation and IPFS upload.
- `/api/v1/dapps/*`: Public storefront data.
- `/api/v1/verify`: Transaction verification (unauthenticated).
- `/api/v1/pipeline/*`: Master pipeline API (currently broken).
- `/api/optik-gpt/*`: LLM endpoints (currently unauthenticated).

### Jobs / Pipelines
- Conversion job: `pipelines/job_service.run_conversion_pipeline` (scrape → analyze → convert → NFT metadata).
- Deployment job: `pipelines/job_service.deploy_to_solana` (Solana store init + collection pairing).
- Universal ingestion: `pipelines/ingestion_manager.UniversalIngestionManager`.
- Scraping pipeline: `pipelines/scraping_pipeline.ScrapingPipeline` (thin wrapper).
- Master pipeline: `pipelines/master_pipeline.MasterPipeline` (broken; calls non-existent methods).
- Stripe webhook handler: `payments/webhook_handler.WebhookHandler` (writes ledger entries).

## Findings (By Severity)

### Critical
1. Secrets committed in repo (`.env` + docs). Rotate and remove immediately.
   - Evidence: `optik-platform/backend/.env:11` (debug + JWT secret placeholder) and `optik-platform/backend/.env:27` (test Stripe keys). Also `optik-platform/backend/STRIPE_SETUP_GUIDE.md:30` and `optik-platform/backend/STRIPE_DASHBOARD_CHECKLIST.md:15` include concrete keys.
   - Impact: key leakage, account compromise, invalidation of security posture.

### High
1. Pipeline API is broken: references a non-existent job service and calls methods that do not exist.
   - Evidence: `optik-platform/backend/api/pipeline_endpoints.py:101` (references `pipeline.job_service`), `optik-platform/backend/pipelines/master_pipeline.py:45` (calls `ingest_store`), `optik-platform/backend/pipelines/master_pipeline.py:53` (calls `process_products`), `optik-platform/backend/pipelines/master_pipeline.py:61` (calls `deploy`).
   - Impact: `/api/v1/pipeline/*` endpoints fail at runtime.

2. EVM pairing flow mismatch: router expects `mintPaired`, NFT contract only exposes `mint`.
   - Evidence: `contracts/src/PairingRouter.sol:19` (interface), `contracts/src/PairingRouter.sol:72` (call), `contracts/src/PairedNFT.sol:31` (only `mint`).
   - Impact: primary minting reverts when used with current `PairedNFT` implementation.

3. Solana deployment uses platform wallet as merchant owner.
   - Evidence: `optik-platform/backend/utils/smart_contract_deployer.py:51` (merchant_wallet param), `optik-platform/backend/utils/smart_contract_deployer.py:66` (owner set to payer, not merchant).
   - Impact: merchant ownership and fee control are effectively centralized to the platform keypair.

4. Verification flow is broken and unauthenticated.
   - Evidence: frontend sends `{ value }` in `optik-platform/apps/app/verify/page.tsx:31`, backend expects `order_id/stripe_intent_id/solana_signature` in `optik-platform/backend/api/verify_routes.py:11`.
   - Impact: verification always fails; endpoint also exposes ledger data without auth.

5. Solana program lacks fee bounds and safe arithmetic.
   - Evidence: `optik-platform/backend/blockchain/programs/optik-store/src/lib.rs:17` (no `fee_bps` bounds), `optik-platform/backend/blockchain/programs/optik-store/src/lib.rs:37` (fee calc), `optik-platform/backend/blockchain/programs/optik-store/src/lib.rs:62` (unchecked add).
   - Impact: overflow/underflow possible; fees can exceed 100%.

6. Contract test suite is out of sync with contract code.
   - Evidence: `contracts/test/pairing.test.ts:16` (constructor args that don’t exist), `contracts/test/pairing.test.ts:24` (`setRouter` missing), `contracts/test/pairing.test.ts:36` (`MintPaired` event missing).
   - Impact: tests will not pass; false sense of safety.

### Medium
1. Store preview checkout lacks merchant wallet/ID.
   - Evidence: conversion output does not include merchant fields `optik-platform/backend/pipelines/conversion_pipeline.py:95`, while the preview expects them `optik-platform/apps/app/store-preview/page.tsx:123` and `optik-platform/apps/app/store-preview/page.tsx:155`.
   - Impact: Stripe and Solana checkout fail in preview flow.

2. Conversion depends on `SOL_USD_PRICE` env, but it is absent in `.env`.
   - Evidence: `optik-platform/backend/agents/converter_agent.py:40` requires `SOL_USD_PRICE`.
   - Impact: conversion fails without explicit configuration.

3. Public LLM endpoints allow anonymous use (potential cost and abuse).
   - Evidence: `optik-platform/backend/optik_gpt/api.py:88` defines `/api/optik-gpt/chat` without auth.
   - Impact: uncontrolled token spend and data exposure.

4. Stripe calls are synchronous inside async endpoints.
   - Evidence: `optik-platform/backend/payments/stripe_client.py:26` uses `stripe.checkout.Session.create` in async contexts.
   - Impact: blocks event loop under load; can degrade API performance.

5. Redis and rate limiting are in-memory fallbacks.
   - Evidence: `optik-platform/backend/utils/redis_manager.py:31` (in-memory fallback), `optik-platform/backend/middleware/rate_limiter.py:169` (in-memory limiter).
   - Impact: job status and rate limits break across multiple workers or restarts.

### Low
1. Several dashboard features are request-only or UI-only placeholders.
   - Evidence: `/dashboard/marketing` uses `api/v1/marketing/*` which only records requests; `/dashboard/security` and `/dashboard/liquidity` are request logging only; `/dashboard/products/[id]/royalties` is UI-only.
   - Impact: user expectations may exceed actual functionality.

2. Next.js API route `/api/dapps/register` is a stub.
   - Evidence: `optik-platform/apps/app/api/dapps/register/route.ts:1` (returns synthetic ID, no persistence).
   - Impact: misleading “registration” behavior in app route.

## Suggested Remediation Roadmap
1. Immediate security cleanup: remove committed keys, rotate all Stripe and any other test secrets, add `.env` to gitignore, update docs to use placeholders only.
2. Fix core pipeline wiring: delete or implement MasterPipeline and its API endpoints, or route them to `job_service` consistently.
3. Align EVM contracts and tests: either implement `mintPaired` + router authorization in `PairedNFT`, or change `PairingRouter` to call the actual mint function and update tests accordingly.
4. Fix Solana merchant ownership: ensure `merchant_wallet` is actually used on-chain and consider PDA derivation for `AdminState`/`MerchantAccount`.
5. Repair verify flow: update frontend payload and protect `/api/v1/verify` (auth or signed requests), return limited fields.
6. Harden production readiness: move Stripe calls to a thread pool or background workers, and require Redis in production for job tracking and rate limiting.

