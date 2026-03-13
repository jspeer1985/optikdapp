# 🔑 Environment Variables You Need to Input

## 🤖 **AI API Keys**
```env
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXX
```

## 💳 **Payment Processing (Stripe)**
```env
STRIPE_SECRET_KEY=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
STRIPE_PUBLISHABLE_KEY=pk_live_51ReGls2LJT0UztDgwOAxuKEIJvbJoPuhr3S3boEfh5ujj4ZbCP6TlStqjHH7OXcN6fAJ0MIFO9tsQSfcRN8mAYvB006TZ7B5ob
STRIPE_WEBHOOK_SECRET=whsec_3667c3020153b1fc595b4938e2fc5cea6f7a675848f81bdaec1e21f72e7bb587
```

## 🛒 **Shopify Integration**
```env
SHOPIFY_API_KEY=shp_live_XXXXXXXXXXXXXXXXXXXX
SHOPIFY_API_SECRET=shp_live_XXXXXXXXXXXXXXXXXXXX
SHOPIFY_WEBHOOK_SECRET=shopify_webhook_secret_2024
```

## 🔗 **Blockchain (Solana)**
```env
SOLANA_WALLET_PRIVATE_KEY=your_base58_private_key_here
TREASURY_WALLET=your_public_wallet_address_here
OPTIK_PROGRAM_ID=5kat1PUqnGRwMLZhsZ7ryDXcRtwaGPiFe8hEknLQ32dC
SOLANA_COLLECTION_MINT=your_collection_mint_address
OPTIK_MINT_ADDRESS=your_optik_token_mint
```

## 🗄️ **Database**
```env
DATABASE_URL=postgresql+asyncpg://username:password@host:5432/database
REDIS_URL=redis://host:port/db
REDIS_PASSWORD=your_redis_password
```

## ☁️ **AWS (Optional)**
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

## 📧 **Email**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.production_api_key_2024
```

## 📊 **Monitoring**
```env
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
```

## 🎯 **Already Configured**
```env
CORS_ORIGIN=https://optikcoin.com
FRONTEND_URL=https://optikcoin.com
ALLOWED_REDIRECT_HOSTS=optikcoin.com,www.optikcoin.com
COOKIE_DOMAIN=.optikcoin.com
```

## ✅ **Quick Setup**
1. Copy `.env.production` to `.env`
2. Replace all `XXXXX` and placeholder values above
3. Run: `./update_config_to_production.sh`
4. Test: `python demo_shopify_scraping.py`
