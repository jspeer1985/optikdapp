"""
Deployment Routes for DApp deployment
Implements: /api/v1/deploy/* endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import uuid

from utils.auth import get_current_user
from utils.database import db
from utils.redis_manager import redis
from pipelines.job_service import deploy_to_solana

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/deploy", tags=["Deployment"])


class DeploymentResponse(BaseModel):
    success: bool
    message: str
    job_id: str
    deployment_id: str


class DeploymentStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    dapp_url: Optional[str] = None
    contract_address: Optional[str] = None
    tx_hash: Optional[str] = None
    error: Optional[str] = None


@router.post("/start/{job_id}", response_model=DeploymentResponse)
async def start_deployment(job_id: str, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    try:
        job = await db.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        if job.get("user_id") != user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        if job.get("status") not in ["completed"]:
            raise HTTPException(status_code=400, detail=f"Cannot deploy: conversion status is {job.get('status')}")

        deployment_id = str(uuid.uuid4())
        await db.update_job_status(job_id, "deploying", progress=0, message="Starting deployment...")
        await redis.set_job_status(job_id, {"status": "deploying", "progress": 0, "message": "Starting deployment..."})

        background_tasks.add_task(deploy_to_solana, job_id)

        logger.info(f"Deployment started: {deployment_id} for job {job_id}")

        return DeploymentResponse(
            success=True,
            message="Deployment started successfully",
            job_id=job_id,
            deployment_id=deployment_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deployment start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=DeploymentStatusResponse)
async def get_deployment_status(job_id: str, user=Depends(get_current_user)):
    try:
        job = await db.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        if job.get("user_id") != user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        redis_status = await redis.get_job_status(job_id)
        status_data = redis_status or job

        return DeploymentStatusResponse(
            job_id=job_id,
            status=status_data.get("status", "pending"),
            progress=int(status_data.get("progress", 0)),
            message=status_data.get("message", ""),
            dapp_url=status_data.get("dapp_url"),
            contract_address=status_data.get("contract_address"),
            tx_hash=status_data.get("tx_hash"),
            error=status_data.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deployment status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
