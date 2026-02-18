"""
Simple Optik Platform API - Minimal Working Version
For quick testing and demo purposes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
import stripe
from utils.env import allow_demo_data

if not allow_demo_data():
    raise RuntimeError(
        "simple_server is demo-only. Set OPTIK_ALLOW_DEMO_DATA=true and ENVIRONMENT!=production to run."
    )

app = FastAPI(
    title="Optik Platform API - Simple",
    description="Web2→Web3 E-commerce Conversion Platform",
    version="1.0.0"
)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise RuntimeError("STRIPE_SECRET_KEY is required to run the demo server.")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pricing plans
PRICING_PLANS = {
    "starter": {
        "name": "Starter DApp Conversion",
        "price": 29900,  # $299.00 in cents
        "currency": "usd",
        "features": ["Basic NFT collection", "Up to 50 products", "Standard support"]
    },
    "growth": {
        "name": "Growth DApp Conversion", 
        "price": 59900,  # $599.00 in cents
        "currency": "usd",
        "features": ["Advanced NFT collection", "Up to 500 products", "Priority support", "Analytics dashboard"]
    },
    "pro": {
        "name": "Pro DApp Conversion",
        "price": 99900,  # $999.00 in cents
        "currency": "usd", 
        "features": ["Custom NFT collection", "Unlimited products", "Dedicated support", "Advanced analytics", "Custom branding"]
    }
}

@app.get("/")
async def root():
    return {
        "service": "Optik Platform API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "up",
            "database": "simulated",
            "redis": "simulated"
        }
    }

@app.get("/api/v1/scrape/platforms")
async def get_platforms():
    return {
        "platforms": [
            {
                "id": "shopify",
                "name": "Shopify",
                "requires_api": False,
                "supports_preview": True
            },
            {
                "id": "woocommerce", 
                "name": "WooCommerce",
                "requires_api": True,
                "supports_preview": True
            },
            {
                "id": "custom",
                "name": "Custom Website",
                "requires_api": False,
                "supports_preview": False
            }
        ]
    }

@app.post("/api/v1/scrape/preview")
async def preview_store(data: dict):
    return {
        "success": True,
        "store_info": {
            "name": "Demo Store",
            "url": data.get("store_url", ""),
            "platform": data.get("platform", "shopify")
        },
        "sample_products": [
            {
                "id": "demo_1",
                "title": "Sample Product 1",
                "price": "$99.99",
                "image": "https://via.placeholder.com/300x300"
            },
            {
                "id": "demo_2", 
                "title": "Sample Product 2",
                "price": "$149.99",
                "image": "https://via.placeholder.com/300x300"
            }
        ],
        "estimated_products": 25,
        "estimated_time": "50 seconds"
    }

# Payment endpoints
@app.get("/api/v1/payments/plans")
async def get_payment_plans():
    return {
        "plans": PRICING_PLANS,
        "currency": "USD"
    }

@app.post("/api/v1/payments/checkout")
async def create_checkout_session(request: dict):
    try:
        plan_id = request.get("plan_id")
        customer_email = request.get("customer_email", "test@example.com")
        success_url = request.get("success_url", "http://localhost:3003/success")
        cancel_url = request.get("cancel_url", "http://localhost:3003/cancel")
        
        if plan_id not in PRICING_PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        plan = PRICING_PLANS[plan_id]
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=customer_email,
            line_items=[{
                'price_data': {
                    'currency': plan['currency'],
                    'product_data': {
                        'name': plan['name'],
                        'description': f"Optik Platform - {plan['name']}",
                    },
                    'unit_amount': plan['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url + f"?session_id={{CHECKOUT_SESSION_ID}}&plan={plan_id}",
            cancel_url=cancel_url + f"?plan={plan_id}",
            metadata={
                'plan_id': plan_id,
                'customer_email': customer_email,
                'platform': 'optik'
            }
        )
        
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url
        }
        
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/v1/connect/fees")
async def get_platform_fees():
    return {
        "success": True,
        "fee_tiers": {
            "starter": 5.0,
            "growth": 3.0, 
            "pro": 2.0,
            "enterprise": 1.0
        },
        "description": "Platform collects percentage of each transaction"
    }

@app.post("/api/v1/connect/payment")
async def create_payment_with_fee(request: dict):
    """Create payment with platform fee collection"""
    try:
        merchant_account_id = request.get("merchant_account_id")
        amount_cents = request.get("amount_cents", 10000)  # $100 default
        platform_fee_percent = 3.0  # 3% platform fee
        platform_fee_cents = int(amount_cents * (platform_fee_percent / 100))
        
        # Create payment with platform fee
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method_types=["card"],
            application_fee_amount=platform_fee_cents,
            transfer_data={
                "destination": merchant_account_id,
            },
            metadata={
                "platform_fee_percent": str(platform_fee_percent),
                "platform_fee_cents": str(platform_fee_cents),
                "merchant_account_id": merchant_account_id,
                "type": "marketplace_transaction"
            }
        )
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "amount_cents": amount_cents,
            "platform_fee_cents": platform_fee_cents,
            "merchant_receives_cents": amount_cents - platform_fee_cents,
            "message": f"Customer pays ${amount_cents/100:.2f}, Merchant gets ${(amount_cents-platform_fee_cents)/100:.2f}, Platform gets ${platform_fee_cents/100:.2f}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/payments/webhook")
async def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        # For now, just acknowledge webhook
        return {"status": "received"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("simple_server:app", host="0.0.0.0", port=port, reload=True)
