import os
import json
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status")
async def get_system_status(user=Depends(get_current_user)):
    active = await db.database.fetch_val(
        "SELECT COUNT(*) FROM jobs WHERE status IN ('scraping', 'analyzing', 'converting', 'generating_nfts', 'deploying')"
    )
    queued = await db.database.fetch_val(
        "SELECT COUNT(*) FROM jobs WHERE status IN ('pending')"
    )
    failed = await db.database.fetch_val(
        "SELECT COUNT(*) FROM jobs WHERE status IN ('failed', 'deployment_failed')"
    )

    return {
        "active_jobs": int(active or 0),
        "queued_jobs": int(queued or 0),
        "failed_jobs": int(failed or 0),
    }


@router.get("/proofs")
async def list_proofs(job_id: Optional[str] = None, workflow_id: Optional[str] = None, user=Depends(get_current_user)):
    proofs = await db.list_proofs(user_id=user.id, job_id=job_id, workflow_id=workflow_id)
    return {"proofs": proofs}


@router.post("/proofs")
async def ingest_proofs(payload: Dict[str, Any], user=Depends(get_current_user)):
    proofs = payload.get("proofs")
    if not isinstance(proofs, list) or not proofs:
        raise HTTPException(status_code=400, detail="Proofs list required")

    proof_ids = []
    for proof in proofs:
        proof["user_id"] = proof.get("user_id") or user.id
        proof_ids.append(await db.create_proof(proof))
    return {"success": True, "proof_ids": proof_ids}


@router.get("/registry")
async def get_registry(user=Depends(get_current_user)):
    registry_path = os.getenv("OPTIK_AGENT_REGISTRY_PATH")
    if not registry_path:
        registry_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "agents", "registry.json"))

    if not os.path.exists(registry_path):
        raise HTTPException(status_code=404, detail="Agent registry not found")

    with open(registry_path, "r", encoding="utf-8") as handle:
        registry = json.load(handle)

    return {"registry": registry}
