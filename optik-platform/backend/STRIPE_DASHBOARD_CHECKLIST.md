# 🏦 Stripe Dashboard Exact Steps

## 🎯 What You Need to Do Inside Stripe Dashboard

### 1. GET YOUR KEYS (First Thing)

**Go to**: https://dashboard.stripe.com/test/apikeys

**Find these 2 keys**:
- **Secret Key**: Starts with `sk_test_...`
- **Publishable Key**: Starts with `pk_test_...`

**Copy the Secret Key** and add to your `.env`:
```bash
STRIPE_SECRET_KEY=sk_test_51ReGli2M6dPE2ciPZEIts44A9Lei7BaZBV3beoVz8xaZAserDHvipKgYSzP1D0yn5Hji45CZFf6KOc6rl9fg9fQO00WFC196NK
```

### 2. CREATE YOUR PRODUCTS (Required for Payments)

**Go to**: https://dashboard.stripe.com/test/products

**Click "Add product" and create these 3 products**:

#### Product 1: Starter DApp Conversion
- **Name**: `Starter DApp Conversion`
- **Description**: `Convert your e-commerce store to Web3 with basic features`
- **Price**: `$299.00 USD`
- **One-time payment** (not subscription)

#### Product 2: Growth DApp Conversion  
- **Name**: `Growth DApp Conversion`
- **Description**: `Advanced Web3 conversion with premium features`
- **Price**: `$599.00 USD`
- **One-time payment**

#### Product 3: Pro DApp Conversion
- **Name**: `Pro DApp Conversion`
- **Description**: `Enterprise Web3 conversion with full features`
- **Price**: `$999.00 USD`
- **One-time payment**

**After creating each product, copy the Price ID** (looks like `price_1OxYZz2eZvKYlo2C7X8Z7X8Z`)

### 3. SET UP WEBHOOKS (Critical)

**Go to**: https://dashboard.stripe.com/test/webhooks

**Click "Add endpoint"**:
- **Endpoint URL**: `http://localhost:8000/api/v1/payments/webhook`
- **Events to send**: Select these:
  - `checkout.session.completed`
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`

**After creating, copy the "Signing secret"** (starts with `whsec_...`)

**Add to your `.env`**:
```bash
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 4. TEST YOUR SETUP

**Go to**: https://dashboard.stripe.com/test/payments

**You should see**:
- Your 3 products listed
- Test payments when you run your app
- Webhook events coming through

### 5. ENABLE BUSINESS FEATURES (Optional but Recommended)

**Go to**: https://dashboard.stripe.com/test/settings

**Enable these**:
- **Payment methods**: Card, Apple Pay, Google Pay
- **Email receipts**: Turn ON
- **Customer emails**: Turn ON
- **Radar fraud detection**: Turn ON

### 6. FOR LIVE MODE (When Ready)

**Toggle to "Live mode"** (top-left switch)

**Repeat steps 1-3** with live keys:
- Get live keys: `sk_live_...` and `pk_live_...`
- Create live products
- Set up live webhook: `https://your-domain.com/api/v1/payments/webhook`

## 🚨 CRITICAL THINGS TO REMEMBER

### NEVER DO:
- ❌ Commit real API keys to git
- ❌ Use test keys in production
- ❌ Share webhook secrets publicly

### ALWAYS DO:
- ✅ Use test mode for development
- ✅ Verify webhook signatures
- ✅ Test with test cards only

### TEST CARDS:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`

## 📋 Quick Copy-Paste Checklist

### Your .env should look like this:
```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...  # Copy from API keys page
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Copy from API keys page  
STRIPE_WEBHOOK_SECRET=whsec_...  # Copy from webhooks page
```

### Your frontend should call:
```javascript
// Get plans
fetch('http://localhost:8000/api/v1/payments/plans')

// Create checkout
fetch('http://localhost:8000/api/v1/payments/checkout', {
  method: 'POST',
  body: JSON.stringify({
    plan_id: 'starter',
    customer_email: 'customer@example.com'
  })
})
```

## 🎯 EXACT URLS TO VISIT

1. **API Keys**: https://dashboard.stripe.com/test/apikeys
2. **Products**: https://dashboard.stripe.com/test/products  
3. **Webhooks**: https://dashboard.stripe.com/test/webhooks
4. **Payments**: https://dashboard.stripe.com/test/payments
5. **Settings**: https://dashboard.stripe.com/test/settings

## ⚡ One-Click Setup Script

If you want to automate this, run:
```bash
cd /home/kali/Dapp_Optik/optik-platform/backend
source venv/bin/activate
python stripe_setup.py
```

This will create all products and webhooks automatically!

---

## 🎉 When You're Done

You'll have:
- ✅ 3 products ready for payment
- ✅ API keys configured
- ✅ Webhook endpoint receiving events
- ✅ Test payment flow working
- ✅ Ready to take real money!

**That's it! Your Stripe setup will be complete.**
