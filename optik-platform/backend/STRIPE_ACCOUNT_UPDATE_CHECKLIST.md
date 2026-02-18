# 🏦 Stripe Account Update Checklist

## 🎯 Current Status Check

### Your Current Setup:
- ✅ **Test Secret Key**: `sk_test_51ReGli...` (configured)
- ❌ **Webhook Secret**: Missing (`your_stripe_webhook_secret_here`)
- ❌ **Connect Account**: Not set up
- ❌ **Products**: Not created
- ❌ **Live Mode**: Not configured

## 📋 What You Need to Update in Stripe Dashboard

### 1. ACCOUNT VERIFICATION (Required for Live Mode)

**Go to**: https://dashboard.stripe.com/settings

**Complete these sections**:
- [ ] **Business Profile**: Add your business name, address, phone
- [ ] **Business Type**: Select "Company" or "Individual"  
- [ ] **Bank Account**: Add your bank for payouts
- [ ] **Identity Verification**: Upload business documents
- [ ] **Website**: Add `https://optik.com` or your domain

### 2. PAYMENT METHODS SETUP

**Go to**: https://dashboard.stripe.com/settings/payment_methods

**Enable these**:
- [ ] **Credit/Debit Cards** (already enabled)
- [ ] **Apple Pay** (recommended)
- [ ] **Google Pay** (recommended)
- [ ] **ACH Bank Transfer** (for large amounts)
- [ ] **ACH Credit Transfer** (for refunds)

### 3. CONNECT PLATFORM SETUP

**Go to**: https://dashboard.stripe.com/connect

**Create Connect Platform**:
- [ ] **Platform Name**: "Optik Platform"
- [ ] **Platform Type**: "Express"
- [ ] **Country**: "US"
- [ ] **Business Type**: "Company"
- [ ] **Capabilities**: 
  - [x] "Card Payments"
  - [x] "Transfers"
  - [ ] "Legacy Payments" (optional)

### 4. CREATE PRODUCTS

**Go to**: https://dashboard.stripe.com/products

**Create these 3 products**:
- [ ] **Starter DApp Conversion** - $299.00
- [ ] **Growth DApp Conversion** - $599.00  
- [ ] **Pro DApp Conversion** - $999.00

### 5. WEBHOOK CONFIGURATION

**Go to**: https://dashboard.stripe.com/webhooks

**Add webhook endpoint**:
- [ ] **Endpoint URL**: `http://localhost:8000/api/v1/payments/webhook`
- [ ] **Events**: 
  - [x] `checkout.session.completed`
  - [x] `payment_intent.succeeded`
  - [x] `payment_intent.payment_failed`
- [ ] **Copy signing secret** and add to `.env`

### 6. SECURITY & COMPLIANCE

**Go to**: https://dashboard.stripe.com/radar

**Configure these**:
- [ ] **Radar Fraud Detection**: Turn ON
- [ ] **3D Secure**: Enable for amounts > $25
- [ ] **Dispute Management**: Set up email alerts
- [ ] **SSL Certificate**: Ensure HTTPS (for production)

### 7. PAYOUT SETTINGS

**Go to**: https://dashboard.stripe.com/settings/payouts

**Configure**:
- [ ] **Payout Schedule**: Daily/Weekly/Monthly
- [ ] **Minimum Payout**: Set your threshold
- [ ] **Payout Method**: Bank transfer
- [ ] **Delay Period**: Standard (7 days) or Custom

## 🚀 QUICK UPDATE ACTIONS

### Option 1: Manual Update (20 minutes)
1. **Login to Stripe Dashboard**
2. **Go through each section above**
3. **Complete all checkboxes**
4. **Copy new IDs/keys to .env**

### Option 2: Automated Setup (5 minutes)
```bash
cd /home/kali/Dapp_Optik/optik-platform/backend
source venv/bin/activate
python stripe_setup.py
```

### Option 3: Live Mode Setup (When Ready)
1. **Toggle to "Live" mode** in Stripe Dashboard
2. **Add live bank account**
3. **Complete live verification**
4. **Get live keys**: `sk_live_...` and `pk_live_...`
5. **Update .env with live keys**

## 📋 AFTER UPDATES - Add These to .env

```bash
# Add these after completing Stripe setup:
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_CONNECT_ACCOUNT_ID=acct_your_connect_account_id_here

# For live mode (when ready):
# STRIPE_SECRET_KEY=sk_live_your_live_secret_key_here
# STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key_here
```

## 🎯 PRIORITY ORDER

### Do This First (Critical):
1. ✅ **Business Profile** - Required for payouts
2. ✅ **Bank Account** - Needed to receive money
3. ✅ **Identity Verification** - Required for live mode

### Do This Second (Important):
4. ✅ **Products** - Needed for payments
5. ✅ **Webhooks** - Needed for automation
6. ✅ **Connect Setup** - Needed for marketplace fees

### Do This Last (Optional but Recommended):
7. ✅ **Security Features** - Reduces fraud
8. ✅ **Payout Settings** - Controls cash flow

## 🔍 VERIFICATION CHECKLIST

### Test Your Updates:
- [ ] **Can create test payments?**
- [ ] **Webhooks receiving events?**
- [ ] **Products showing in checkout?**
- [ ] **Connect account working?**
- [ ] **Bank account verified?**
- [ ] **Can switch to live mode?**

### Production Readiness:
- [ ] **All test payments working**
- [ ] **Live bank account added**
- [ ] **Business verification complete**
- [ ] **Live API keys tested**
- [ ] **HTTPS domain ready**
- [ ] **Error handling tested**

## 🎉 COMPLETION REWARDS

Once you complete all updates:
- ✅ **Accept real payments** from customers
- ✅ **Collect platform fees** automatically
- ✅ **Receive daily payouts** to your bank
- ✅ **Scale to thousands of merchants**
- ✅ **Generate recurring revenue** from fees

## 🆘 TROUBLESHOOTING

### Common Issues:
- **"Account not verified"** → Complete business profile
- **"No payouts"** → Add bank account
- **"Webhook failing"** → Check URL and secret
- **"Connect not working"** → Enable transfers capability
- **"Live mode blocked"** → Complete all verification steps

---

## 📞 NEED HELP?

- **Stripe Support**: https://support.stripe.com
- **Connect Docs**: https://stripe.com/docs/connect
- **API Reference**: https://stripe.com/docs/api

**Your Optik Platform will be ready to scale once these updates are complete!**
