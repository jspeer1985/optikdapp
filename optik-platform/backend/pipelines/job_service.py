import asyncio
import logging
import os
from typing import Any, Dict

from pipelines.conversion_pipeline import ConversionPipeline
from pipelines.deployment_pipeline import DeploymentPipeline
from utils.database import db
from utils.redis_manager import redis

logger = logging.getLogger(__name__)

WORKFLOW_ID = "merchant_dapp_creation_v1"


def _get(submission: Any, key: str, default=None):
    if hasattr(submission, key):
        return getattr(submission, key)
    if isinstance(submission, dict):
        return submission.get(key, default)
    return default


async def _record_proof(
    job_id: str,
    user_id: str,
    step_id: str,
    status: str,
    details: Dict[str, Any] | None = None,
    artifacts: Dict[str, Any] | None = None,
    owner_agent: str | None = None,
    proof_type: str = "workflow",
):
    await db.create_proof({
        "user_id": user_id,
        "job_id": job_id,
        "workflow_id": WORKFLOW_ID,
        "step_id": step_id,
        "status": status,
        "details": details or {},
        "artifacts": artifacts or {},
        "owner_agent": owner_agent,
        "proof_type": proof_type,
    })


async def _fail_job(job_id: str, message: str, error: str):
    await redis.set_job_status(job_id, {
        "status": "failed",
        "progress": 0,
        "message": message,
        "error": error,
    })
    await db.update_job_status(job_id, "failed", progress=0, message=message, error=error)


async def run_conversion_pipeline(job_id: str, submission: Any):
    store_data = None
    analysis = None
    web3_store = None
    nft_data = None

    job = await db.get_job_status(job_id)
    if not job:
        logger.error(f"Job {job_id} not found for conversion")
        return
    user_id = job.get("user_id")

    try:
        pipeline = ConversionPipeline(job_id)

        await redis.set_job_status(job_id, {
            "status": "scraping",
            "progress": 10,
            "message": "Scraping store data...",
        })
        await db.update_job_status(job_id, "scraping", progress=10, message="Scraping store data...")

        try:
            store_data = await asyncio.wait_for(
                pipeline.scrape_store(
                    url=str(_get(submission, "store_url")),
                    platform=_get(submission, "platform"),
                    api_key=_get(submission, "api_key"),
                    api_secret=_get(submission, "api_secret"),
                ),
                timeout=45.0,
            )
        except Exception as e:
            await _record_proof(
                job_id,
                user_id,
                "catalog_scrape",
                "failed",
                details={"error": str(e)},
                owner_agent="scraper_agent",
            )
            await _fail_job(job_id, "Scrape failed", str(e))
            return

        store_info = store_data.get("store_info", {}) if store_data else {}
        if store_info.get("name"):
            await db.update_job_store_name(job_id, store_info.get("name"))

        await _record_proof(
            job_id,
            user_id,
            "catalog_scrape",
            "completed",
            details={
                "store_url": store_data.get("url"),
                "platform": store_data.get("platform"),
                "product_count": len(store_data.get("products", [])),
            },
            owner_agent="scraper_agent",
        )

        await redis.set_job_status(job_id, {
            "status": "analyzing",
            "progress": 40,
            "message": "Analyzing store structure and products...",
        })
        await db.update_job_status(job_id, "analyzing", progress=40, message="Analyzing store structure and products...")

        try:
            analysis = await asyncio.wait_for(pipeline.analyze_store(store_data), timeout=30.0)
        except Exception as e:
            await _record_proof(
                job_id,
                user_id,
                "catalog_analysis",
                "failed",
                details={"error": str(e)},
                owner_agent="catalog_analyzer_agent",
            )
            await _fail_job(job_id, "Analysis failed", str(e))
            return

        await _record_proof(
            job_id,
            user_id,
            "catalog_analysis",
            "completed",
            details=analysis,
            owner_agent="catalog_analyzer_agent",
        )

        await redis.set_job_status(job_id, {
            "status": "converting",
            "progress": 60,
            "message": "Converting to Web3 format...",
        })
        await db.update_job_status(job_id, "converting", progress=60, message="Converting to Web3 format...")

        try:
            web3_store = await asyncio.wait_for(
                pipeline.convert_to_web3(store_data=store_data, analysis=analysis, tier=_get(submission, "tier")),
                timeout=45.0,
            )
        except Exception as e:
            await _record_proof(
                job_id,
                user_id,
                "storefront_build",
                "failed",
                details={"error": str(e)},
                owner_agent="frontend_agent",
            )
            await _fail_job(job_id, "Conversion failed", str(e))
            return

        await _record_proof(
            job_id,
            user_id,
            "storefront_build",
            "completed",
            details={
                "product_count": len(web3_store.get("products", [])),
                "active_agents": web3_store.get("active_agents", []),
            },
            owner_agent="frontend_agent",
        )

        await redis.set_job_status(job_id, {
            "status": "generating_nfts",
            "progress": 80,
            "message": "Generating NFT metadata...",
        })
        await db.update_job_status(job_id, "generating_nfts", progress=80, message="Generating NFT metadata...")

        try:
            nft_data = await asyncio.wait_for(pipeline.generate_nfts(web3_store), timeout=30.0)
        except Exception as e:
            await _record_proof(
                job_id,
                user_id,
                "nft_metadata_and_mint",
                "failed",
                details={"error": str(e)},
                owner_agent="nft_minter_agent",
            )
            await _fail_job(job_id, "NFT generation failed", str(e))
            return

        await _record_proof(
            job_id,
            user_id,
            "nft_metadata_and_mint",
            "completed",
            details={"nft_count": len(nft_data)},
            artifacts={"nfts": nft_data},
            owner_agent="nft_minter_agent",
        )

        try:
            await db.save_conversion_result(job_id, web3_store, nft_data)
        except Exception as e:
            logger.error(f"Job {job_id}: Failed to save conversion result: {e}")
            await _record_proof(
                job_id,
                user_id,
                "storefront_build",
                "failed",
                details={"error": str(e)},
                owner_agent="backend_agent",
            )
            await _fail_job(job_id, "Failed to persist conversion", str(e))
            return

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3003")
        preview_url = f"{frontend_url}/store-preview?job_id={job_id}"

        await redis.set_job_status(job_id, {
            "status": "completed",
            "progress": 100,
            "message": "Conversion completed successfully!",
            "dapp_url": preview_url,
        })
        await db.update_job_status(job_id, "completed", progress=100, message="Conversion completed successfully!", dapp_url=preview_url)

        await _record_proof(
            job_id,
            user_id,
            "handover",
            "completed",
            details={"preview_url": preview_url},
            owner_agent="onboarding_superagent",
        )

        logger.info(f"Conversion job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Conversion pipeline failure for job {job_id}: {e}")
        await _record_proof(
            job_id,
            user_id,
            "handover",
            "failed",
            details={"error": str(e)},
            owner_agent="supervisor",
        )
        await _fail_job(job_id, "Conversion failed", str(e))


async def deploy_to_solana(job_id: str):
    job = await db.get_job_status(job_id)
    if not job:
        logger.error(f"Job {job_id} not found for deployment")
        return
    user_id = job.get("user_id")

    try:
        deployer = DeploymentPipeline()

        conversion_data = await db.get_conversion_data(job_id)
        job_info = await db.get_job(job_id)

        tier_fees = {
            "basic": 300,
            "growth": 500,
            "global": 900,
            "scale": 1200,
            "elite": 1500,
        }
        fee_bps = tier_fees.get(getattr(job_info, "tier", "basic").lower(), 300)

        config = {
            "wallet_address": os.getenv("TREASURY_WALLET", ""),
            "fee_bps": fee_bps,
            "enable_nft": True,
            "backing_amount": float(os.getenv("OPTIK_BACKING_AMOUNT", "1000")),
            "store_url": job.get("store_url"),
            "collection_symbol": os.getenv("OPTIK_COLLECTION_SYMBOL", "OPTIK"),
            "min_balance_sol": float(os.getenv("SOLANA_MIN_BALANCE", "0.05")),
        }

        await redis.set_job_status(job_id, {
            "status": "deploying",
            "progress": 0,
            "message": "Starting deployment...",
        })
        await db.update_job_status(job_id, "deploying", progress=0, message="Starting deployment...")

        deployment_result = await deployer.run(job_id, conversion_data, config)

        if deployment_result.get("status") != "success":
            error = deployment_result.get("error", "Deployment failed")
            await _record_proof(
                job_id,
                user_id,
                "deployment",
                "failed",
                details={"error": error},
                owner_agent="backend_agent",
            )
            await _fail_job(job_id, "Deployment failed", error)
            return

        await db.update_deployment_result(job_id, deployment_result)

        await redis.set_job_status(job_id, {
            "status": "deployed",
            "progress": 100,
            "message": "Dapp successfully deployed to Solana!",
            "dapp_url": deployment_result.get("dapp_url"),
            "tx_hash": deployment_result.get("tx_hash"),
        })
        await db.update_job_status(job_id, "deployed", progress=100, message="Dapp successfully deployed to Solana!", dapp_url=deployment_result.get("dapp_url"))

        await _record_proof(
            job_id,
            user_id,
            "deployment",
            "completed",
            details={
                "network": deployment_result.get("network"),
                "dapp_url": deployment_result.get("dapp_url"),
                "tx_hash": deployment_result.get("tx_hash"),
            },
            artifacts={"deployment": deployment_result},
            owner_agent="backend_agent",
        )

        logger.info(f"Deployment for job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Deployment failed for job {job_id}: {e}")
        await _record_proof(
            job_id,
            user_id,
            "deployment",
            "failed",
            details={"error": str(e)},
            owner_agent="backend_agent",
        )
        await _fail_job(job_id, "Deployment failed", str(e))
