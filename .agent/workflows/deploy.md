---
description: How to deploy the Optik Platform to production (Vercel & Render)
---

# 🚀 Deployment Workflow

Follow these steps to take the Optik Platform live.

// turbo

1. Run the automation script to verify readiness

```bash
./automate_deployment.sh
```

2. Confirm all environment variables are set in the backend `.env`

   - `STRIPE_SECRET_KEY`
   - `ANTHROPIC_API_KEY`
   - `SOLANA_WALLET_PRIVATE_KEY`

3. Deploy the Backend

   - Host the `/optik-platform/backend` directory on Render or Railway.
   - Use the command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:$PORT`
   - Note the deployment URL (e.g., `https://api.optik.io`).

4. Deploy the Frontend (Vercel)

   - Connect your repository to Vercel.
   - Set the **Root Directory** to `optik-platform/apps`.
   - Add environment variables:
     - `NEXT_PUBLIC_API_URL`: (Your backend URL from step 3)
     - `NEXT_PUBLIC_OPTIK_TOKEN_MINT`: (Your token mint address)

5. Verify Health
   - Visit `https://your-dapp.vercel.app`
   - Open the "Create DApp" page to ensure the connection to the backend is live.
   - Test a Stripe checkout in test mode.

// turbo 6. Final Audit

```bash
python3 optik-platform/apps/scripts/api_contract_audit.py
```
