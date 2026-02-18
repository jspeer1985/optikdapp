import stripe
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def audit_stripe():
    api_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not api_key or "PASTE_LIVE" in api_key:
        print("❌ ERROR: No valid STRIPE_SECRET_KEY found in .env file.")
        return

    stripe.api_key = api_key
    print(f"--- Stripe Audit Starting (Key: {api_key[:8]}...) ---")
    
    try:
        # 1. Fetch Products
        print("\n📦 Active Products:")
        products = stripe.Product.list(active=True)
        if not products.data:
            print("   No active products found.")
        for product in products.data:
            print(f"   - Name: {product.name}")
            print(f"     ID: {product.id}")
            
            # 2. Fetch Prices for this Product
            prices = stripe.Price.list(product=product.id, active=True)
            for price in prices.data:
                currency = price.currency.upper()
                amount = price.unit_amount / 100
                print(f"     💰 Price ID: {price.id} ({amount} {currency})")
                
                # Check if it matches expected IDs
                if price.id.startswith("price_optik_"):
                    print(f"        ✅ MATCHES expected format.")

        # 3. Check Webhooks
        print("\n🔗 Webhook Endpoints:")
        webhooks = stripe.WebhookEndpoint.list()
        if not webhooks.data:
            print("   No webhook endpoints configured.")
        for wh in webhooks.data:
            print(f"   - URL: {wh.url}")
            print(f"     Status: {wh.status}")

    except Exception as e:
        print(f"❌ Stripe API Error: {str(e)}")

if __name__ == "__main__":
    audit_stripe()
