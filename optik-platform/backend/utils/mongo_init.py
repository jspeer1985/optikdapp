"""
MongoDB Initialization and Startup/Shutdown Hooks
Integrates MongoDB with FastAPI application lifecycle
"""

import logging
from fastapi import FastAPI
from utils.mongo_db import mongodb, JobRepository, ProductRepository
from utils.env import allow_demo_data
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


async def init_mongodb(app: FastAPI):
    """
    Initialize MongoDB connection on app startup.

    Usage in main.py:
        @app.on_event("startup")
        async def startup():
            await init_mongodb(app)
    """
    logger.info("🔄 Initializing MongoDB...")

    # Connect to MongoDB
    connected = await mongodb.connect()

    if not connected:
        logger.error("❌ Failed to connect to MongoDB on startup")
        raise RuntimeError("MongoDB connection failed")

    logger.info("✅ MongoDB initialized successfully")

    # Seed initial data if collections are empty
    await seed_initial_data()

    # Store mongodb in app state for access
    app.state.mongodb = mongodb


async def close_mongodb(app: FastAPI):
    """
    Close MongoDB connection on app shutdown.

    Usage in main.py:
        @app.on_event("shutdown")
        async def shutdown():
            await close_mongodb(app)
    """
    logger.info("🔄 Closing MongoDB connection...")
    await mongodb.disconnect()
    logger.info("✅ MongoDB closed")


async def seed_initial_data():
    """
    Seed initial data if collections are empty.
    Useful for development and testing.
    """
    if not allow_demo_data():
        logger.info("Demo data seeding disabled outside non-production environments.")
        return
    try:
        # Check if collections are empty
        job_repo = JobRepository()
        product_repo = ProductRepository()

        job_count = await job_repo.count()
        product_count = await product_repo.count()

        if job_count == 0:
            logger.info("📊 Seeding initial jobs data...")
            await seed_jobs()

        if product_count == 0:
            logger.info("📊 Seeding initial products data...")
            await seed_products()

        logger.info("✅ Initial data seeding complete")

    except Exception as e:
        logger.warning(f"⚠️ Could not seed initial data: {str(e)}")


async def seed_jobs():
    """Seed initial jobs for testing."""
    job_repo = JobRepository()

    initial_jobs = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_demo_001",
            "store_url": "https://demo-store.shopify.com",
            "platform": "shopify",
            "tier": "growth",
            "status": "completed",
            "message": "Store conversion completed successfully",
            "deployment_config": {
                "network": "devnet",
                "treasury": "7dzzihnceMRrhDvDFVH5E4pVKhFeEgLTTfxWczvbHrPa"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_demo_002",
            "store_url": "https://example-woo.com",
            "platform": "woocommerce",
            "tier": "scale",
            "status": "processing",
            "message": "Analyzing store products...",
            "deployment_config": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    for job in initial_jobs:
        await job_repo.create(job)

    logger.info(f"✅ Seeded {len(initial_jobs)} jobs")


async def seed_products():
    """Seed initial products for testing."""
    product_repo = ProductRepository()

    initial_products = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_demo_001",
            "name": "Genesis Hoodie",
            "description": "Limited edition founding member hoodie",
            "supply": "100",
            "sold": 45,
            "price": "0.5 SOL",
            "status": "Live",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_demo_001",
            "name": "Founder Cap",
            "description": "Exclusive founder cap with blockchain badge",
            "supply": "50",
            "sold": 50,
            "price": "1.2 SOL",
            "status": "Sold Out",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_demo_001",
            "name": "Digital Badge",
            "description": "Unlimited digital membership badge",
            "supply": "Unlimited",
            "sold": 1240,
            "price": "0.1 SOL",
            "status": "Live",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    for product in initial_products:
        await product_repo.create(product)

    logger.info(f"✅ Seeded {len(initial_products)} products")


async def health_check():
    """Get health status of MongoDB."""
    return await mongodb.health_check()
