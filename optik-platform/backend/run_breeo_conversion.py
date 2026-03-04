import asyncio
import os
import uuid
import logging
from datetime import datetime
from pydantic import HttpUrl

# Load original env first
from dotenv import load_dotenv
load_dotenv()

# Set environment for the run
os.environ["ENVIRONMENT"] = "development"
os.environ["OPTIK_ALLOW_DEMO_DATA"] = "true"
os.environ["MOCK_BLOCKCHAIN"] = "true"
os.environ["SOL_USD_PRICE"] = "150.0" # Mock SOL price
os.environ["OPTIK_DEPLOY_WALLET_ADDRESS"] = "optik_deployer_wallet_mock_address"

# Now import the API code
from api.main import run_conversion_pipeline, deploy_to_solana, StoreSubmission
from utils.database import db
from utils.redis_manager import redis

# FORCE UNSET REDIS_URL AFTER ALL IMPORTS
if "REDIS_URL" in os.environ:
    del os.environ["REDIS_URL"]
    
# Re-configure redis instance if it was already initialized with the URL
redis.redis_enabled = False
redis.client = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BreeoConversionRunner")

async def run_full_pipeline_for_breeo():
    try:
        # 1. Initialize services
        os.environ["REDIS_URL"] = "" 
        
        logger.info("Connecting to Database and Redis (Forced Fallback)...")
        await db.connect()
        await redis.connect()
        
        # 2. Create a test user if not exists
        user_email = "breeo_test@optik.store"
        user = await db.get_user_by_email(user_email)
        if not user:
            user = await db.create_user(email=user_email, wallet_address=None)
        
        user_id = user["id"]
        
        # 3. Define the conversion request
        store_url = "https://breeo.myshopify.com"
        submission = StoreSubmission(
            store_url=store_url,
            platform="shopify",
            tier="growth",
            email=user_email
        )
        
        # 4. Create the job in DB
        job_id = await db.create_conversion_job(
            user_id=user_id,
            store_url=store_url,
            platform="shopify",
            tier="growth",
            email=user_email
        )
        logger.info(f"🚀 Job Created: {job_id}")
        
        # 5. Run Conversion Pipeline
        logger.info("Starting Conversion Pipeline stage...")
        await run_conversion_pipeline(job_id, submission)
        
        # 6. Check status after conversion using REDIS (in-memory)
        status = await redis.get_job_status(job_id)
        logger.info(f"Conversion complete. Status: {status.get('status')}")
        
        if status.get("status") == "completed":
            # 7. Run Deployment Pipeline
            logger.info("Starting Deployment Pipeline stage...")
            # We need to manually update the DB status for deploy_to_solana to find it
            await db.update_job_status(job_id, "completed")
            
            await deploy_to_solana(job_id)
            
            # 8. Final check
            final_status = await redis.get_job_status(job_id)
            logger.info(f"🏁 PIPELINE FINISHED: {final_status.get('status')}")
            logger.info(f"🔗 DApp URL: {final_status.get('dapp_url')}")
            
            # 9. Verify deployment data in DB
            deployment = await db.database.fetch_one("SELECT * FROM deployments WHERE job_id = :job_id", {"job_id": job_id})
            if deployment:
                logger.info(f"📦 Deployment recorded in DB: {dict(deployment).get('dapp_url')}")
        else:
            logger.error(f"Pipeline failed at conversion stage: {status.get('status')} - Error: {status.get('error')}")

    except Exception as e:
        logger.error(f"Catastrophic failure in runner: {e}", exc_info=True)
    finally:
        await db.disconnect()
        await redis.disconnect()

if __name__ == "__main__":
    asyncio.run(run_full_pipeline_for_breeo())
