from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/liquidity", tags=["liquidity"])


class LiquidityRequest(BaseModel):
    amount_sol: float


@router.get("/summary")
async def liquidity_summary(user=Depends(get_current_user)):
    summary = await db.get_liquidity_summary(user.id)
    return summary


@router.post("/request")
async def request_liquidity(request: LiquidityRequest, user=Depends(get_current_user)):
    if request.amount_sol <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    request_id = await db.create_liquidity_request(user.id, request.amount_sol)
    return {"success": True, "request_id": request_id}
