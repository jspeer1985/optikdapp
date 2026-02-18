"""
Conversion Routes for Store → DApp conversion endpoints
Implements: /api/v1/convert/* endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging

from utils.auth import get_current_user
from utils.database import db
from utils.redis_manager import redis
from pipelines.job_service import run_conversion_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/convert", tags=["Conversion"])


class ConversionSubmitRequest(BaseModel):
    store_url: HttpUrl
    platform: str
    tier: str
    email: str
    store_name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


class ConversionResponse(BaseModel):
    success: bool
    job_id: str
    message: str
    status_endpoint: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    dapp_url: Optional[str] = None
    error: Optional[str] = None


@router.post("/submit", response_model=ConversionResponse)
async def submit_conversion(request: ConversionSubmitRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    try:
        job_id = await db.create_conversion_job(
            user_id=user.id,
            store_url=str(request.store_url),
            platform=request.platform,
            tier=request.tier,
            email=request.email,
        )

        if request.store_name:
            await db.update_job_store_name(job_id, request.store_name)

        await redis.set_job_status(job_id, {
            "status": "pending",
            "progress": 0,
            "message": "Job queued",
        })

        background_tasks.add_task(run_conversion_pipeline, job_id, request)

        logger.info(f"Conversion submitted: {job_id} for {request.store_url}")

        return ConversionResponse(
            success=True,
            job_id=job_id,
            message="Conversion started successfully",
            status_endpoint=f"/api/v1/convert/status/{job_id}",
        )

    except Exception as e:
        logger.error(f"Conversion submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_conversion_status(job_id: str, user=Depends(get_current_user)):
    try:
        job = await db.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        if job.get("user_id") != user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        redis_status = await redis.get_job_status(job_id)
        status_data = redis_status or job

        return StatusResponse(
            job_id=job_id,
            status=status_data.get("status", "pending"),
            progress=int(status_data.get("progress", 0)),
            message=status_data.get("message", ""),
            dapp_url=status_data.get("dapp_url"),
            error=status_data.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{job_id}")
async def get_conversion_preview(job_id: str, user=Depends(get_current_user)):
    job = await db.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("user_id") != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    record = await db.get_conversion_record(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Conversion data not available yet")

    web3_store = record.get("web3_store_data") or {}
    return {
        "job_id": job_id,
        "store": web3_store.get("store", {}),
        "products": web3_store.get("products", []),
        "nfts": record.get("nft_data", []),
    }


@router.get("/")
async def list_conversions(user=Depends(get_current_user)):
    jobs = await db.list_jobs(user.id)
    return {"total": len(jobs), "jobs": jobs}
