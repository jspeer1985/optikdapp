import asyncio
import logging
import sys
import os

# Add the current directory to sys.path to import agents and pipelines
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.conversion_pipeline import ConversionPipeline
from pipelines.deployment_pipeline import DeploymentPipeline

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestPipeline")

async def run_test_conversion(store_url: str):
    job_id = "test_job_" + os.urandom(4).hex()
    logger.info(f"🚀 Starting TEST FULL PIPELINE for: {store_url} (Job: {job_id})")
    
    # 1. Conversion Phase
    conv_pipeline = ConversionPipeline(job_id)
    
    print("\n--- 🛒 PHASE 1: SCRAPING & AI ANALYSIS ---")
    store_data = await conv_pipeline.scrape_store(store_url, 'shopify')
    if not store_data["products"]:
        logger.error("❌ No products found. Public scraping might be blocked or URL is incorrect.")
        return

    print(f"✅ Found {len(store_data['products'])} products.")
    
    analysis = await conv_pipeline.analyze_store(store_data)
    print(f"🧠 AI Analysis Ready: {analysis.get('brand_tone', 'N/A')} style identified.")
    
    web3_store = await conv_pipeline.convert_to_web3(store_data, analysis, tier="Professional")
    print(f"💎 Web3 Products Generated: {len(web3_store['products'])} preview items ready.")

    # 2. Deployment Phase (Live Mode: OPTIK BACKED)
    print("\n--- ⛓️ PHASE 2: SOLANA DEPLOYMENT & OPTIK BACKING ---")
    deploy_pipeline = DeploymentPipeline()
    config = {
        "wallet_address": "7dzzihnceMRrhDvDFVH5E4pVKhFeEgLTTfxWczvbHrPa",
        "fee_bps": 500, # 5% Professional Tier
        "enable_nft": True,
        "backing_amount": 5000.0 # Back with 5000 $OPTIK
    }
    
    result = await deploy_pipeline.run(job_id, web3_store, config)
    
    print("\n--- ✅ TEST COMPLETE ---")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Using a known public shopify store for testing
    test_url = "https://shop.porsche.com" # Public shopify store
    asyncio.run(run_test_conversion(test_url))
