"""
Optik Platform - Main API Server
Enterprise-grade FastAPI application for Web2→Web3 e-commerce conversion
"""

import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any
import uvicorn
import logging
from datetime import datetime
import asyncio

# Import security middleware
from middleware.rate_limiter import RateLimitMiddleware
from middleware.security_headers import (
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    SecurityLoggingMiddleware
)

# Import AWS Secrets Manager
from utils.aws_secrets import get_secrets_manager, get_api_keys, get_database_credentials
from utils.env import allow_demo_data

# Import our agents and pipelines
from agents.scraper_agent import ShopifyScraperAgent, WooCommerceScraperAgent
from agents.analyzer_agent import StoreAnalyzerAgent
from agents.converter_agent import Web3ConverterAgent
from agents.deployer_agent import SolanaDeployerAgent
from agents.growth_agent import GrowthAgent # Assuming GrowthAgent is in agents/growth_agent.py
from pipelines.conversion_pipeline import ConversionPipeline
from utils.database import DatabaseManager, db
from utils.redis_manager import redis
from utils.auth import verify_api_key, get_current_user
from api.payment_routes import router as payments_router
from api.auth_routes import router as auth_router
from api.connect_routes import router as connect_router
from api.marketing_routes import router as marketing_router
from api.product_routes import router as products_router
from api.integration_routes import router as integrations_router
from api.convert_routes import router as convert_router
from api.deploy_routes import router as deploy_router
from api.system_routes import router as system_router
from api.dapps_routes import router as dapps_router
from api.analytics_routes import router as analytics_router
from api.security_routes import router as security_router
from api.liquidity_routes import router as liquidity_router
from api.nft_routes import router as nft_router
from api.verify_routes import router as verify_router
from api.onboarding_routes import router as onboarding_router
from api.assistant_routes import router as assistant_router
from api.pipeline_endpoints import router as pipeline_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
APP_START = datetime.utcnow()

# Initialize secrets manager
secrets_manager = get_secrets_manager()
logger.info("Secrets manager initialized")

# Initialize FastAPI app
app = FastAPI(
    title="Optik Platform API",
    description="Enterprise Web2→Web3 E-commerce Conversion Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ============================================================================
# SECURITY MIDDLEWARE (Order matters!)
# ============================================================================

# 1. Request ID tracking (first, so all logs have request IDs)
app.add_middleware(RequestIDMiddleware)

# 2. Security logging (early to catch all requests)
app.add_middleware(SecurityLoggingMiddleware)

# 3. Security headers (protect against common attacks)
environment = os.getenv("ENVIRONMENT", "production").lower()
ALLOW_DEMO_DATA = allow_demo_data()
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=os.getenv("ENABLE_HSTS", "true").lower() == "true",
    hsts_max_age=int(os.getenv("HSTS_MAX_AGE", "31536000")),
    enable_csp=os.getenv("ENABLE_CSP", "true").lower() == "true",
    environment=environment
)

# 4. Rate limiting (prevent abuse)
rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
if rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
        burst_size=int(os.getenv("RATE_LIMIT_BURST_SIZE", "10")),
        exclude_paths=["/health", "/metrics", "/", "/api/docs", "/api/redoc"]
    )
    logger.info("Rate limiting enabled")

# 5. CORS Configuration (last, so it can process other middleware headers)
cors_origin_env = os.getenv("CORS_ORIGIN")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3003")
cors_origins = (cors_origin_env or f"{frontend_url},http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Security middleware initialized for environment: {environment}")

# Initialize managers
# db is imported as singleton
growth_agent = GrowthAgent() # Initialize GrowthAgent

# Initialize OptikGPT
try:
    from optik_gpt.assistant.conversation_engine import OptikAssistant
    optik_assistant = OptikAssistant()
except ImportError as e:
    logger.warning(f"Failed to load OptikGPT Assistant: {e}")
    optik_assistant = None

# Include routers
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(connect_router)
app.include_router(marketing_router)
app.include_router(products_router)
app.include_router(integrations_router)
app.include_router(convert_router)
app.include_router(deploy_router)
app.include_router(system_router)
app.include_router(dapps_router)
app.include_router(analytics_router)
app.include_router(security_router)
app.include_router(liquidity_router)
app.include_router(nft_router)
app.include_router(verify_router)
app.include_router(onboarding_router)
app.include_router(assistant_router)
app.include_router(pipeline_router)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class StoreSubmission(BaseModel):
    """Store submission for conversion"""
    store_url: HttpUrl
    platform: str  # 'shopify' or 'woocommerce'
    tier: str  # 'starter', 'growth', 'pro', 'enterprise', 'premium', 'platinum'
    email: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
    @validator('platform')
    def validate_platform(cls, v):
        if v not in ['shopify', 'woocommerce', 'custom']:
            raise ValueError('Platform must be shopify, woocommerce, or custom')
        return v
    
    @validator('tier')
    def validate_tier(cls, v):
        valid_tiers = ['basic', 'growth', 'global', 'scale', 'elite']
        if v.lower() not in valid_tiers:
            raise ValueError(f'Tier must be one of: {", ".join(valid_tiers)}')
        return v.lower()


class ConversionStatus(BaseModel):
    """Response model for conversion status"""
    job_id: str
    status: str  # 'pending', 'scraping', 'analyzing', 'converting', 'deploying', 'completed', 'failed'
    progress: int  # 0-100
    message: str
    created_at: datetime
    updated_at: datetime
    dapp_url: Optional[str] = None
    error: Optional[str] = None


class DeploymentConfig(BaseModel):
    """Configuration for Web3 deployment"""
    job_id: str
    enable_nft: bool = True
    enable_token_rewards: bool = True
    custom_branding: bool = False
    analytics_enabled: bool = True
    custom_domain: Optional[str] = None


class WebhookConfig(BaseModel):
    """Webhook configuration for status updates"""
    url: HttpUrl
    events: List[str]  # ['scrape_complete', 'conversion_complete', 'deployment_complete']

# Pydantic Models for Marketing
class AirdropRequest(BaseModel):
    criteria: str = "active_users"
    amount: float = 100.0

class StakingRequest(BaseModel):
    apy: float = 12.5
    lock_period_days: int = 30


class ChatRequest(BaseModel):
    message: str
    merchant_id: str = "default_merchant"
    context: Optional[Dict[str, Any]] = None
    prompt_profile: Optional[str] = None
    prompt_version: Optional[str] = None
    assistant_mode: Optional[str] = None
    page_context: Optional[str] = None
    model_preference: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    actions: List[str] = []
    status: str = "success"


# ============================================================================
# OPTIK GPT ENDPOINTS
# ============================================================================

@app.post("/api/v1/assistant/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest, user = Depends(get_current_user)):
    """
    Chat with OptikGPT Assistant
    """
    if not optik_assistant:
        return {
            "message": "OptikGPT is currently offline. Please try again later.",
            "actions": [],
            "status": "error"
        }
        
    try:
        response = await optik_assistant.handle_message(
            merchant_id=request.merchant_id,
            message=request.message,
            context={
                "prompt_profile": request.prompt_profile,
                "prompt_version": request.prompt_version,
                "assistant_mode": request.assistant_mode,
                "page_context": request.page_context,
                "model_preference": request.model_preference,
                "request_context": request.context,
            },
        )
        return {
            "message": response.get("message", "I didn't understand that."),
            "actions": response.get("actions", []),
            "status": response.get("status", "success")
        }
    except Exception as e:
        logger.error(f"OptikGPT Error: {str(e)}")
        return {
            "message": "I encountered an error processing your request.",
            "actions": [],
            "status": "error"
        }


# ============================================================================
# HEALTH CHECK & METRICS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Optik Platform API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db_status = await db.check_connection()
        
        # Check Redis connection
        redis_status = await redis.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "up" if db_status else "down",
                "redis": "up" if redis_status else "down",
                "api": "up"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/metrics")
async def metrics(api_key = Depends(verify_api_key)):
    """System metrics for monitoring"""
    uptime_seconds = (datetime.utcnow() - APP_START).total_seconds()
    return {
        "active_jobs": await redis.get_active_job_count(),
        "completed_conversions": await db.get_conversion_count(),
        "total_revenue": await db.get_total_revenue(),
        "uptime_seconds": int(uptime_seconds),
        "started_at": APP_START.isoformat(),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# CORE CONVERSION ENDPOINTS
# ============================================================================



# ============================================================================
# SCRAPING ENDPOINTS
# ============================================================================

@app.post("/api/v1/scrape/preview")
async def preview_store(store_url: HttpUrl, platform: str):
    """
    Preview what will be scraped from a store without creating a job
    Used for the frontend preview before user commits
    """
    try:
        if platform == 'shopify':
            scraper = ShopifyScraperAgent()
        elif platform == 'woocommerce':
            scraper = WooCommerceScraperAgent()
        else:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        # Get basic info (first 5 products)
        preview = await scraper.preview_store(str(store_url), limit=5)
        
        return {
            "success": True,
            "store_info": preview["store_info"],
            "sample_products": preview["products"],
            "estimated_products": preview["total_products"],
            "estimated_time": f"{preview['total_products'] * 2} seconds"  # ~2s per product
        }
        
    except Exception as e:
        logger.error(f"Failed to preview store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/scrape/platforms")
async def get_supported_platforms():
    """
    Get list of supported e-commerce platforms
    """
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


# ============================================================================
# DEPLOYMENT ENDPOINTS
# ============================================================================

@app.post("/api/v1/deploy/configure")
async def configure_deployment(config: DeploymentConfig, user = Depends(get_current_user)):
    """
    Configure deployment settings for a converted store
    """
    try:
        # Verify job exists and user owns it
        job = await db.get_job(config.job_id)
        if job.user_id != user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Update deployment config
        await db.update_deployment_config(config.job_id, config.dict())
        
        return {
            "success": True,
            "message": "Deployment configuration updated"
        }
        
    except Exception as e:
        logger.error(f"Failed to configure deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/v1/analytics/{job_id}")
async def get_store_analytics(job_id: str, user = Depends(get_current_user)):
    """
    Get analytics for a deployed store
    """
    try:
        job = await db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        raise HTTPException(
            status_code=501,
            detail="Job analytics are not configured. Enable the analytics pipeline to retrieve real data."
        )
        
    except Exception as e:
        logger.error(f"Failed to get analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.post("/api/v1/webhooks/configure")
async def configure_webhook(webhook: WebhookConfig, user = Depends(get_current_user)):
    """
    Configure webhook for receiving conversion status updates
    """
    try:
        await db.save_webhook_config(user.id, webhook.dict())
        return {
            "success": True,
            "message": "Webhook configured successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def run_conversion_pipeline(job_id: str, submission: StoreSubmission):
    """
    Main conversion pipeline - runs in background
    
    Steps:
    1. Scrape store data
    2. Analyze products and structure
    3. Convert to Web3 format
    4. Generate NFT metadata
    5. Prepare for deployment
    
    Each step has error handling to prevent the pipeline from getting stuck.
    """
    store_data = None
    analysis = None
    web3_store = None
    nft_data = None
    
    try:
        # Initialize pipeline
        pipeline = ConversionPipeline(job_id)
        
        # ========== STEP 1: SCRAPING ==========
        try:
            await redis.set_job_status(job_id, {
                "status": "scraping",
                "progress": 10,
                "message": "Scraping store data..."
            })
            
            logger.info(f"Job {job_id}: Starting scrape step")
            store_data = await asyncio.wait_for(
                pipeline.scrape_store(
                    url=str(submission.store_url),
                    platform=submission.platform,
                    api_key=submission.api_key,
                    api_secret=submission.api_secret
                ),
                timeout=30.0  # 30 second timeout for scraping
            )
            logger.info(f"Job {job_id}: Scrape completed with {len(store_data.get('products', []))} products")
            
        except asyncio.TimeoutError as e:
            logger.warning(f"Job {job_id}: Scraping timed out")
            if not ALLOW_DEMO_DATA:
                raise RuntimeError("Scraping timed out and demo fallback is disabled") from e
            logger.warning(f"Job {job_id}: Using demo fallback data (non-production only)")
            store_data = {
                "url": str(submission.store_url),
                "platform": submission.platform,
                "products": [
                    {
                        "id": "fallback_1",
                        "title": "Demo Product",
                        "description": "Fallback product data",
                        "price": "99.99",
                        "images": []
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Job {job_id}: Scraping failed: {str(e)}")
            if not ALLOW_DEMO_DATA:
                raise RuntimeError("Scraping failed and demo fallback is disabled") from e
            logger.warning(f"Job {job_id}: Using demo fallback data (non-production only)")
            store_data = {
                "url": str(submission.store_url),
                "platform": submission.platform,
                "products": [
                    {
                        "id": "fallback_1",
                        "title": "Demo Product",
                        "description": "Fallback product data",
                        "price": "99.99",
                        "images": []
                    }
                ]
            }
        
        # ========== STEP 2: ANALYZING ==========
        try:
            await redis.set_job_status(job_id, {
                "status": "analyzing",
                "progress": 40,
                "message": "Analyzing store structure and products..."
            })
            
            logger.info(f"Job {job_id}: Starting analysis step")
            analysis = await asyncio.wait_for(
                pipeline.analyze_store(store_data),
                timeout=20.0  # 20 second timeout for analysis
            )
            logger.info(f"Job {job_id}: Analysis completed")
            
        except Exception as e:
            logger.error(f"Job {job_id}: Analysis failed: {str(e)}")
            if not ALLOW_DEMO_DATA:
                raise RuntimeError("Analysis failed and demo fallback is disabled") from e
            logger.warning(f"Job {job_id}: Using basic analysis fallback (non-production only)")
            analysis = {
                "product_count": len(store_data.get("products", [])),
                "categories": [],
                "recommendations": []
            }
        
        # ========== STEP 3: CONVERTING ==========
        try:
            await redis.set_job_status(job_id, {
                "status": "converting",
                "progress": 60,
                "message": "Converting to Web3 format..."
            })
            
            logger.info(f"Job {job_id}: Starting conversion step")
            web3_store = await asyncio.wait_for(
                pipeline.convert_to_web3(
                    store_data=store_data,
                    analysis=analysis,
                    tier=submission.tier
                ),
                timeout=30.0  # 30 second timeout for conversion
            )
            logger.info(f"Job {job_id}: Conversion completed")
            
        except Exception as e:
            logger.error(f"Job {job_id}: Conversion failed: {str(e)}")
            if not ALLOW_DEMO_DATA:
                raise RuntimeError("Conversion failed and demo fallback is disabled") from e
            logger.warning(f"Job {job_id}: Using basic conversion fallback (non-production only)")
            web3_store = {
                "products": store_data.get("products", []),
                "tier": submission.tier,
                "active_agents": ["Core Optik AI"],
                "preview_url": f"https://optik.store/preview/{job_id}"
            }
        
        # ========== STEP 4: GENERATING NFTs ==========
        try:
            await redis.set_job_status(job_id, {
                "status": "generating_nfts",
                "progress": 80,
                "message": "Generating NFT metadata..."
            })
            
            logger.info(f"Job {job_id}: Starting NFT generation step")
            nft_data = await asyncio.wait_for(
                pipeline.generate_nfts(web3_store),
                timeout=20.0  # 20 second timeout for NFT generation
            )
            logger.info(f"Job {job_id}: NFT generation completed")
            
        except Exception as e:
            logger.error(f"Job {job_id}: NFT generation failed: {str(e)}")
            if not ALLOW_DEMO_DATA:
                raise RuntimeError("NFT generation failed and demo fallback is disabled") from e
            logger.warning(f"Job {job_id}: Using empty NFT data fallback (non-production only)")
            nft_data = []
        
        # ========== STEP 5: SAVE RESULTS ==========
        try:
            await db.save_conversion_result(job_id, web3_store, nft_data)
        except Exception as e:
            logger.error(f"Job {job_id}: Failed to save to database: {str(e)}")
            # Continue anyway - we can still show the preview
        
        # ========== FINAL: MARK AS COMPLETE ==========
        await redis.set_job_status(job_id, {
            "status": "completed",
            "progress": 100,
            "message": "Conversion completed successfully!",
            "dapp_url": web3_store.get("preview_url", f"https://optik.store/preview/{job_id}")
        })
        
        logger.info(f"Conversion job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Conversion pipeline catastrophic failure for job {job_id}: {str(e)}")
        await redis.set_job_status(job_id, {
            "status": "failed",
            "progress": 0,
            "message": "Conversion failed",
            "error": str(e)
        })
        try:
            await db.update_job_status(job_id, "failed", error=str(e))
        except Exception as db_error:
            logger.error(f"Job {job_id}: Failed to update database status: {str(db_error)}")


async def deploy_to_solana(job_id: str):
    """
    Deploy converted store to Solana blockchain using the revenue-share tiers.
    """
    try:
        from pipelines.deployment_pipeline import DeploymentPipeline
        deployer = DeploymentPipeline()
        
        # Get conversion data
        conversion_data = await db.get_conversion_data(job_id)
        job_info = await db.get_job(job_id)
        
        # Map tier to fee BPS (1% = 100 bps)
        tier_fees = {
            'basic': 300,    # 3%
            'growth': 500,   # 5%
            'global': 900,   # 9%
            'scale': 1200,   # 12%
            'elite': 1500    # 15%
        }
        fee_bps = tier_fees.get(getattr(job_info, 'tier', 'basic').lower(), 300)
        
        # Configuration for deployment
        wallet_address = os.getenv("OPTIK_DEPLOY_WALLET_ADDRESS")
        if not wallet_address:
            raise RuntimeError("OPTIK_DEPLOY_WALLET_ADDRESS is required for Solana deployment")

        config = {
            "wallet_address": wallet_address,
            "fee_bps": fee_bps,
            "enable_nft": True,
            "backing_amount": 1000.0 if getattr(job_info, 'tier', 'basic') != 'elite' else 5000.0 # Extra backing for Elite
        }
        
        # Start deployment process (includes OptikCoin backing)
        deployment_result = await deployer.run(job_id, conversion_data, config)
        
        # Update database with result (PDA address, TX hash, Backing status)
        await db.update_deployment_result(job_id, deployment_result)
        
        # Update job status: Deployed
        await redis.set_job_status(job_id, {
            "status": "deployed",
            "progress": 100,
            "message": "Dapp successfully deployed to Solana!",
            "dapp_url": deployment_result.get("dapp_url")
        })
        
        logger.info(f"Deployment for job {job_id} ({getattr(job_info, 'tier', 'unknown')}) completed successfully")
        
    except Exception as e:
        logger.error(f"Deployment failed for job {job_id}: {str(e)}")
        await db.update_job_status(job_id, "deployment_failed", error=str(e))
        await redis.set_job_status(job_id, {
            "status": "failed",
            "progress": 0,
            "message": "Deployment failed",
            "error": str(e)
        })


# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Optik Platform API...")
    await db.connect()
    await redis.connect()
    logger.info("All services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Optik Platform API...")
    await db.disconnect()
    await redis.disconnect()
    logger.info("Cleanup completed")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to listen on all interfaces for Docker compatibility
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # The original code had more parameters, but the instruction implies a simpler call.
    # If the intention was to keep all parameters, the instruction was ambiguous.
    # Keeping the host as 0.0.0.0 as per instruction.
    # Original parameters:
    # uvicorn.run(
    #     "main:app",
    #     host="0.0.0.0",
    #     port=8000,
    #     reload=True,  # Set to False in production
    #     workers=4,  # Adjust based on CPU cores
    #     log_level="info"
    # )
