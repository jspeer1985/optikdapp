from fastapi import APIRouter, Depends
from pydantic import BaseModel

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/marketing", tags=["marketing"])


class AirdropRequest(BaseModel):
    criteria: str = "active_traders"
    amount: float = 50.0


class StakingRequest(BaseModel):
    apy: float = 15.0
    lock_period_days: int = 30


class MobileAppRequest(BaseModel):
    app_name: str
    platform: str


@router.post("/airdrop")
async def run_airdrop(request: AirdropRequest, user=Depends(get_current_user)):
    await db.create_marketing_request(user.id, "airdrop", request.dict())
    return {
        "success": True,
        "message": "Airdrop configured",
        "criteria": request.criteria,
        "amount": request.amount,
    }


@router.post("/staking")
async def start_staking(request: StakingRequest, user=Depends(get_current_user)):
    await db.create_marketing_request(user.id, "staking", request.dict())
    return {
        "success": True,
        "message": "Staking pool initialized",
        "apy": request.apy,
        "lock_period_days": request.lock_period_days,
    }


@router.get("/logs")
async def list_logs(user=Depends(get_current_user)):
    logs = await db.list_marketing_logs(user.id, limit=25)
    return {"logs": logs}


@router.post("/mobile-app")
async def request_mobile_app(request: MobileAppRequest, user=Depends(get_current_user)):
    payload = {"app_name": request.app_name, "platform": request.platform}
    request_id = await db.create_marketing_request(user.id, "mobile-app", payload)
    return {"success": True, "request_id": request_id}
