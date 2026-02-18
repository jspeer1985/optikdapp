# 🏦 Optik Platform Stripe Setup Guide

## 🚨 SECURITY FIRST - Before You Start

1. **NEVER commit real API keys to git**
2. **Use test keys for development**
3. **Switch to live keys only for production**

## 📋 Step 1: Get Your Stripe Keys

### Test Mode (Development)
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
2. Find "Test mode" toggle - make sure it's ON
3. Copy these keys:
   - **Secret Key**: `sk_test_...` (starts with `sk_test_`)
   - **Publishable Key**: `pk_test_...` (starts with `pk_test_`)

### Production Mode (Live)
1. Toggle to "Live mode" in Stripe Dashboard
2. Copy live keys:
   - **Secret Key**: `sk_live_...` (starts with `sk_live_`)
   - **Publishable Key**: `pk_live_...` (starts with `pk_live_`)

## 🔧 Step 2: Configure Your Environment

Add to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51ReGli2M6dPE2ciPZEIts44A9Lei7BaZBV3beoVz8xaZAserDHvipKgYSzP1D0yn5Hji45CZFf6KOc6rl9fg9fQO00WFC196NK
STRIPE_PUBLISHABLE_KEY=pk_test_51ReGli2M6dPE2ciPZEIts44A9Lei7BaZBV3beoVz8xaZAserDHvipKgYSzP1D0yn5Hji45CZFf6KOc6rl9fg9fQO00WFC196NK
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

## 💰 Step 3: Define Your Payment Tiers

### Optik Platform Pricing Structure:

| Service | Price | Features |
|---------|-------|----------|
| **Starter Conversion** | $299 | Basic NFT collection, 50 products, standard support |
| **Growth Conversion** | $599 | Advanced NFTs, 500 products, priority support, analytics |
| **Pro Conversion** | $999 | Custom NFTs, unlimited products, dedicated support |
| **NFT Minting** | $199 | Professional NFT creation and deployment |
| **Token Rewards** | $149 | Customer loyalty token system |

## 🛠️ Step 4: Run the Setup Script

```bash
cd /home/kali/Dapp_Optik/optik-platform/backend
source venv/bin/activate
python stripe_setup.py
```

This will:
- ✅ Create all products in Stripe
- ✅ Set up pricing for each tier
- ✅ Create webhook endpoints
- ✅ Set up Stripe Connect (for marketplace)
- ✅ Generate configuration file

## 🎯 Step 5: Frontend Integration

Update your frontend to use the new price IDs:

```javascript
// Example price IDs (replace with actual IDs from setup)
const PRICING = {
  starter: 'price_1OxYZz2eZvKYlo2C7X8Z7X8Z',
  growth: 'price_1OxYZz2eZvKYlo2C7X8Z7X8Z', 
  pro: 'price_1OxYZz2eZvKYlo2C7X8Z7X8Z',
  nft_minting: 'price_1OxYZz2eZvKYlo2C7X8Z7X8Z',
  token_rewards: 'price_1OxYZz2eZvKYlo2C7X8Z7X8Z'
};
```

## 🔗 Step 6: Webhook Setup

### Local Development (ngrok)
```bash
# Install ngrok
npm install -g ngrok

# Start your backend
python simple_server.py

# In another terminal, expose port 8000
ngrok http 8000

# Copy the ngrok URL and add to Stripe:
# https://your-ngrok-url.ngrok.io/api/webhooks/stripe
```

### Production
```bash
# Your production webhook URL
https://your-domain.com/api/webhooks/stripe
```

## 🧪 Step 7: Test Payment Flow

### Test Cards for Development:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Insufficient Funds**: `4000 0000 0000 9995`

### Testing Process:
1. Go to your frontend: http://localhost:3003
2. Select a pricing tier
3. Click "Pay Now"
4. Use test card details
5. Complete checkout
6. Verify webhook receives events

## 📊 Step 8: Monitor Transactions

### Stripe Dashboard Events to Watch:
- `checkout.session.completed` - Payment successful
- `payment_intent.succeeded` - Money received
- `payment_intent.payment_failed` - Payment failed
- `invoice.payment_succeeded` - Subscription paid

### Your Backend Endpoints:
- `POST /api/payments/create-checkout-session`
- `POST /api/webhooks/stripe` (webhook handler)

## 🔒 Step 9: Security Checklist

- [ ] API keys stored in environment variables
- [ ] Webhook signature verification enabled
- [ ] HTTPS enabled in production
- [ ] Rate limiting on payment endpoints
- [ ] Error handling doesn't expose sensitive data
- [ ] PCI compliance (Stripe handles this)

## 🚀 Step 10: Go Live

1. **Switch to Live Mode** in Stripe Dashboard
2. **Update .env** with live API keys
3. **Update frontend** with live publishable key
4. **Test with real cards** (small amounts)
5. **Monitor first transactions**
6. **Set up bank transfers** in Stripe

## 💡 Pro Tips

### Maximize Conversions:
- Offer multiple payment methods (card, Apple Pay, Google Pay)
- Show security badges (SSL, Stripe Verified)
- Display pricing clearly with features comparison
- Offer money-back guarantee

### Reduce Fraud:
- Enable Stripe Radar
- Set up 3D Secure for high-value transactions
- Monitor suspicious activity patterns
- Use Stripe's built-in fraud detection

### Customer Support:
- Set up email notifications for payment events
- Create refund policies
- Handle disputes promptly
- Provide payment receipts

## 📞 Support

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: support@stripe.com
- **Optik Platform**: Check your backend logs for issues

---

## 🎉 You're Ready to Make Money!

Once you complete these steps, your Optik Platform will be able to:
- ✅ Accept payments for DApp conversions
- ✅ Handle subscription billing
- ✅ Process marketplace transactions
- ✅ Manage customer accounts
- ✅ Track revenue and analytics

**Start with test mode, verify everything works, then go live!**
