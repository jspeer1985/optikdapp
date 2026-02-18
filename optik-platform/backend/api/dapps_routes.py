from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/dapps", tags=["dapps"])


@router.get("")
async def list_my_dapps(user=Depends(get_current_user)):
    dapps = await db.list_deployed_dapps(user.id)
    return {"dapps": dapps}


@router.get("/public")
async def list_public_dapps():
    dapps = await db.list_public_dapps(limit=20)
    listings = [
        {
            "job_id": d.get("id"),
            "store_name": d.get("store_name") or d.get("store_url"),
            "dapp_url": d.get("dapp_url"),
            "platform": d.get("platform"),
        }
        for d in dapps
    ]
    return {"dapps": listings}


@router.get("/latest")
async def get_latest_dapp(user=Depends(get_current_user)):
    dapp = await db.get_latest_dapp_for_user(user.id)
    if not dapp:
        return {"job_id": None}
    return {"job_id": dapp.get("id")}


@router.get("/{job_id}")
async def get_dapp(job_id: str):
    job = await db.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Dapp not found")
    if job.get("status") not in ["completed", "deployed"]:
        raise HTTPException(status_code=404, detail="Dapp not ready")

    record = await db.get_conversion_record(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Dapp data unavailable")

    web3_store = record.get("web3_store_data") or {}
    store = web3_store.get("store", {})
    products = web3_store.get("products", [])

    merchant_wallet = None
    merchant_id = None
    user_id = job.get("user_id")
    if user_id:
        user = await db.get_user(user_id)
        if user:
            merchant_wallet = user.get("wallet_address")
        merchant = await db.get_merchant_by_user(user_id)
        if merchant:
            merchant_id = merchant.get("id")

    store_payload = {
        **store,
        "merchant_wallet": merchant_wallet,
        "merchant_id": merchant_id,
    }

    return {
        "job_id": job_id,
        "store": store_payload,
        "products": products,
    }
