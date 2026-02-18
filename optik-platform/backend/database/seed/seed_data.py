import asyncio
import os
import json
from datetime import datetime

# In a real scenario, we would use the Prisma client or a direct SQL link.
# This script serves as a template for seeding the development database.
environment = os.getenv("ENVIRONMENT", "production").lower()
allow_demo = os.getenv("OPTIK_ALLOW_DEMO_DATA", "false").lower() == "true"
if environment == "production" or not allow_demo:
    raise SystemExit("Demo seed data is disabled outside non-production environments.")

demo_user = {
    "id": "user_demo_123",
    "email": "demo@optikplatform.com",
    "wallet": "7x...demo...wallet",
    "createdAt": datetime.utcnow()
}

demo_store = {
    "id": "store_demo_456",
    "name": "The Web3 Experiment",
    "originalUrl": "https://demo.shopify.com",
    "platform": "shopify",
    "userId": "user_demo_123",
    "convertedStatus": "completed"
}

demo_products = [
    {
        "title": "Genesis Hoodie",
        "description": "The first ever garment on the Optik Platform. Verified on-chain.",
        "priceUsd": 89.99,
        "priceSol": 0.6,
        "storeId": "store_demo_456",
        "metadata": json.dumps({"rarity": "Legendary", "material": "Organic Cotton"})
    },
    {
        "title": "Digital Access Key",
        "description": "NFT that grants access to the platform's beta features.",
        "priceUsd": 150.00,
        "priceSol": 1.0,
        "storeId": "store_demo_456",
        "metadata": json.dumps({"utility": "Early Access", "transferable": True})
    }
]

async def seed():
    print("🚀 Starting Database Seed...")
    
    # Simulate database insertion
    print(f"Adding User: {demo_user['email']}")
    await asyncio.sleep(0.5)
    
    print(f"Adding Store: {demo_store['name']}")
    await asyncio.sleep(0.5)
    
    for product in demo_products:
        print(f"Adding Product: {product['title']} ({product['priceUsd']} USD)")
        await asyncio.sleep(0.2)
        
    print("✅ Seed Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
