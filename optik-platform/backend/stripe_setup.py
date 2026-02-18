#!/usr/bin/env python3
"""
Stripe Setup Script for Optik Platform
Creates products, prices, and webhook endpoints
"""

import stripe
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize Stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Optik Platform Payment Tiers
PAYMENT_PRODUCTS = {
    "starter_conversion": {
        "name": "Starter DApp Conversion",
        "description": "Convert your e-commerce store to Web3 with basic features",
        "price": 29900,  # $299.00 in cents
        "currency": "usd",
        "features": ["Basic NFT collection", "Up to 50 products", "Standard support"]
    },
    "growth_conversion": {
        "name": "Growth DApp Conversion", 
        "description": "Advanced Web3 conversion with premium features",
        "price": 59900,  # $599.00 in cents
        "currency": "usd",
        "features": ["Advanced NFT collection", "Up to 500 products", "Priority support", "Analytics dashboard"]
    },
    "pro_conversion": {
        "name": "Pro DApp Conversion",
        "description": "Enterprise Web3 conversion with full features",
        "price": 99900,  # $999.00 in cents
        "currency": "usd", 
        "features": ["Custom NFT collection", "Unlimited products", "Dedicated support", "Advanced analytics", "Custom branding"]
    },
    "nft_minting": {
        "name": "NFT Minting Service",
        "description": "Professional NFT collection creation and deployment",
        "price": 19900,  # $199.00 in cents
        "currency": "usd",
        "features": ["Custom NFT design", "Smart contract deployment", "IPFS storage", "Marketing materials"]
    },
    "token_rewards": {
        "name": "Token Rewards System",
        "description": "Implement customer loyalty tokens",
        "price": 14900,  # $149.00 in cents
        "currency": "usd",
        "features": ["Token creation", "Reward mechanisms", "Customer dashboard", "Analytics"]
    }
}

def create_products_and_prices():
    """Create all Stripe products and prices"""
    created_items = {}
    
    for product_key, product_data in PAYMENT_PRODUCTS.items():
        try:
            # Create product
            product = stripe.Product.create(
                name=product_data["name"],
                description=product_data["description"],
                metadata={
                    "type": "optik_service",
                    "features": json.dumps(product_data["features"])
                }
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=product_data["price"],
                currency=product_data["currency"],
                metadata={
                    "product_key": product_key
                }
            )
            
            created_items[product_key] = {
                "product_id": product.id,
                "price_id": price.id,
                "price_amount": product_data["price"],
                "currency": product_data["currency"]
            }
            
            print(f"✅ Created: {product_data['name']} - ${product_data['price']/100:.2f}")
            print(f"   Product ID: {product.id}")
            print(f"   Price ID: {price.id}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating {product_key}: {str(e)}")
    
    return created_items

def create_webhook_endpoint():
    """Create webhook endpoint for payment events"""
    try:
        webhook = stripe.WebhookEndpoint.create(
            url="https://your-domain.com/api/webhooks/stripe",
            enabled_events=[
                "checkout.session.completed",
                "payment_intent.succeeded",
                "payment_intent.payment_failed",
                "invoice.payment_succeeded",
                "customer.subscription.created"
            ],
            description="Optik Platform payment webhooks"
        )
        
        print(f"✅ Webhook created: {webhook.url}")
        print(f"   Webhook Secret: {webhook.secret}")
        print("   ⚠️  Add this secret to your .env file as STRIPE_WEBHOOK_SECRET")
        print()
        
        return webhook
        
    except Exception as e:
        print(f"❌ Error creating webhook: {str(e)}")
        return None

def setup_connect_account():
    """Setup Stripe Connect for marketplace functionality"""
    try:
        account = stripe.Account.create(
            type="express",
            country="US",
            email="platform@optik.com",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="company",
            company={
                "name": "Optik Platform",
                "address": {
                    "line1": "123 Tech Street",
                    "city": "San Francisco", 
                    "state": "CA",
                    "postal_code": "94105",
                    "country": "US"
                }
            }
        )
        
        print(f"✅ Connect Account created: {account.id}")
        print(f"   Account Link: https://dashboard.stripe.com/connect/accounts/{account.id}")
        print()
        
        return account
        
    except Exception as e:
        print(f"❌ Error creating Connect account: {str(e)}")
        return None

def generate_env_config(created_items):
    """Generate .env configuration for created items"""
    env_config = """
# ============================================
# STRIPE CONFIGURATION (ADD TO YOUR .env)
# ============================================

# Your existing Stripe keys
STRIPE_SECRET_KEY=sk_test_...  # Your test secret key
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Your test publishable key
STRIPE_WEBHOOK_SECRET=whsec_...  # From webhook creation

# Product Price IDs (copy from output above)
STRIPE_STARTER_PRICE_ID=price_...
STRIPE_GROWTH_PRICE_ID=price_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_NFT_MINTING_PRICE_ID=price_...
STRIPE_TOKEN_REWARDS_PRICE_ID=price_...

# Connect Account (for marketplace)
STRIPE_CONNECT_ACCOUNT_ID=acct_...

# Webhook endpoint
STRIPE_WEBHOOK_URL=https://your-domain.com/api/webhooks/stripe
"""
    
    with open("stripe_config.txt", "w") as f:
        f.write(env_config)
    
    print("📝 Configuration saved to stripe_config.txt")
    print("   Copy the relevant sections to your .env file")

def main():
    print("🚀 Setting up Stripe for Optik Platform...")
    print("=" * 50)
    print()
    
    # Check if Stripe key is configured
    if not stripe.api_key or stripe.api_key == "your_stripe_secret_key_here":
        print("❌ Please set your STRIPE_SECRET_KEY in .env first")
        print("   Get it from: https://dashboard.stripe.com/apikeys")
        return
    
    print("1. Creating products and prices...")
    created_items = create_products_and_prices()
    
    print("2. Creating webhook endpoint...")
    webhook = create_webhook_endpoint()
    
    print("3. Setting up Connect account...")
    connect_account = setup_connect_account()
    
    print("4. Generating configuration...")
    generate_env_config(created_items)
    
    print("=" * 50)
    print("✅ Stripe setup complete!")
    print()
    print("Next steps:")
    print("1. Add the generated configuration to your .env file")
    print("2. Update your frontend with the price IDs")
    print("3. Test the payment flow")
    print("4. Deploy to production with live keys")

if __name__ == "__main__":
    main()
