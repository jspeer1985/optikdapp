"""
Pipeline API Endpoints
REST API endpoints for the Optik DApp conversion pipeline
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl
import asyncio

from pipelines.master_pipeline import MasterPipeline, master_pipeline
from pipelines.ingestion_manager import UniversalIngestionManager
from utils.platform_detector import platform_detector
from utils.data_processor import data_processor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

# Pydantic models for request/response
class PipelineRequest(BaseModel):
    source_url: HttpUrl
    config: Optional[Dict[str, Any]] = None
    webhook_url: Optional[HttpUrl] = None

class PlatformDetectionRequest(BaseModel):
    url: HttpUrl

class IngestionRequest(BaseModel):
    source_url: HttpUrl
    platform: Optional[str] = None
    limit: Optional[int] = 250

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    stage: Optional[str] = None
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

# Dependency to get pipeline instance
def get_pipeline():
    return master_pipeline

@router.post("/detect-platform", response_model=Dict[str, Any])
async def detect_platform(request: PlatformDetectionRequest):
    """
    Detect the e-commerce platform for a given URL
    """
    try:
        result = await platform_detector.detect_platform(str(request.url))
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Platform detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest", response_model=Dict[str, Any])
async def ingest_products(request: IngestionRequest):
    """
    Ingest products from an e-commerce store
    """
    try:
        ingestion_manager = UniversalIngestionManager()
        result = await ingestion_manager.ingest(
            str(request.source_url),
            request.platform,
            request.limit
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Product ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start", response_model=Dict[str, Any])
async def start_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    pipeline: MasterPipeline = Depends(get_pipeline)
):
    """
    Start the complete DApp conversion pipeline
    """
    try:
        # Start pipeline in background
        job_id = await pipeline.job_service.create_job(
            "master_pipeline",
            {"source_url": str(request.source_url)}
        )
        
        # Run pipeline asynchronously
        background_tasks.add_task(
            pipeline.execute_full_pipeline,
            str(request.source_url),
            request.config
        )
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "source_url": str(request.source_url),
                "status": "started",
                "message": "Pipeline started successfully"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-sync", response_model=Dict[str, Any])
async def start_pipeline_sync(
    request: PipelineRequest,
    pipeline: MasterPipeline = Depends(get_pipeline)
):
    """
    Start the complete DApp conversion pipeline synchronously
    """
    try:
        result = await pipeline.execute_full_pipeline(
            str(request.source_url),
            request.config
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=Dict[str, Any])
async def get_job_status(
    job_id: str,
    pipeline: MasterPipeline = Depends(get_pipeline)
):
    """
    Get the status of a pipeline job
    """
    try:
        status = await pipeline.get_pipeline_status(job_id)
        
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{job_id}", response_model=Dict[str, Any])
async def cancel_job(
    job_id: str,
    pipeline: MasterPipeline = Depends(get_pipeline)
):
    """
    Cancel a running pipeline job
    """
    try:
        cancelled = await pipeline.cancel_pipeline(job_id)
        
        return {
            "success": cancelled,
            "data": {
                "job_id": job_id,
                "cancelled": cancelled
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=Dict[str, Any])
async def list_jobs(
    limit: int = 10,
    pipeline: MasterPipeline = Depends(get_pipeline)
):
    """
    List recent pipeline jobs
    """
    try:
        jobs = await pipeline.list_recent_jobs(limit)
        
        return {
            "success": True,
            "data": {
                "jobs": jobs,
                "count": len(jobs)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=Dict[str, Any])
async def validate_products(products: List[Dict[str, Any]]):
    """
    Validate and normalize a batch of products
    """
    try:
        # Normalize products
        normalized_products = data_processor.batch_normalize(products)
        
        # Validate batch
        validation_result = data_processor.validate_batch(normalized_products)
        
        return {
            "success": True,
            "data": {
                "products": normalized_products,
                "validation": validation_result
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Product validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms", response_model=Dict[str, Any])
async def get_supported_platforms():
    """
    Get list of supported e-commerce platforms
    """
    try:
        platforms = platform_detector.get_supported_platforms()
        
        return {
            "success": True,
            "data": {
                "platforms": platforms,
                "count": len(platforms)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint
    """
    try:
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "service": "optik-pipeline-api",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook endpoints for real-time updates
@router.post("/webhook/shopify", response_model=Dict[str, Any])
async def shopify_webhook(payload: Dict[str, Any]):
    """
    Handle Shopify webhooks for real-time product updates
    """
    try:
        # Process webhook payload
        webhook_type = payload.get("type")
        product_data = payload.get("payload", {})
        
        # Normalize the product data
        if product_data:
            normalized = data_processor.normalize_product(product_data, "shopify")
            
            # Here you would typically:
            # 1. Update database
            # 2. Trigger re-sync
            # 3. Send notifications
            
            logger.info(f"Processed Shopify webhook: {webhook_type} for product {normalized.get('external_id')}")
        
        return {
            "success": True,
            "message": "Webhook processed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Shopify webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/woocommerce", response_model=Dict[str, Any])
async def woocommerce_webhook(payload: Dict[str, Any]):
    """
    Handle WooCommerce webhooks for real-time product updates
    """
    try:
        # Process webhook payload
        webhook_type = payload.get("topic")
        product_data = payload.get("payload", {})
        
        # Normalize the product data
        if product_data:
            normalized = data_processor.normalize_product(product_data, "woocommerce")
            
            # Here you would typically:
            # 1. Update database
            # 2. Trigger re-sync
            # 3. Send notifications
            
            logger.info(f"Processed WooCommerce webhook: {webhook_type} for product {normalized.get('external_id')}")
        
        return {
            "success": True,
            "message": "Webhook processed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"WooCommerce webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

        
