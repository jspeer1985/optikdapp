import os
from typing import Dict, Any

DEFAULT_PLANS: Dict[str, Dict[str, Any]] = {
    "basic": {
        "id": "basic",
        "name": "Basic DApp Conversion",
        "price": 29900,
        "currency": "usd",
        "billing_mode": "payment",
        "features": ["Basic NFT collection", "Up to 50 products", "Standard support"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_BASIC"),
    },
    "growth": {
        "id": "growth",
        "name": "Growth DApp Conversion",
        "price": 59900,
        "currency": "usd",
        "billing_mode": "payment",
        "features": ["Advanced NFT collection", "Up to 500 products", "Priority support", "Analytics dashboard"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_GROWTH"),
    },
    "global": {
        "id": "global",
        "name": "Global DApp Conversion",
        "price": 99900,
        "currency": "usd",
        "billing_mode": "payment",
        "features": ["Custom NFT collection", "Unlimited products", "Dedicated support", "Multi-region deployment"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_GLOBAL"),
    },
    "scale": {
        "id": "scale",
        "name": "Scale DApp Conversion",
        "price": 149900,
        "currency": "usd",
        "billing_mode": "payment",
        "features": ["Security suite", "Advanced analytics", "Custom branding", "Enterprise support"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_SCALE"),
    },
    "elite": {
        "id": "elite",
        "name": "Elite DApp Conversion",
        "price": 249900,
        "currency": "usd",
        "billing_mode": "payment",
        "features": ["Full autonomy", "Dedicated success team", "Custom SLA", "White-glove onboarding"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_ELITE"),
    },
}


def get_plans() -> Dict[str, Dict[str, Any]]:
    return DEFAULT_PLANS
