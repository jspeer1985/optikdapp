from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import or_

from utils.database import db, ledger_entries

router = APIRouter(prefix="/api/v1", tags=["verification"])


class VerifyRequest(BaseModel):
    order_id: Optional[str] = None
    stripe_intent_id: Optional[str] = None
    solana_signature: Optional[str] = None


@router.post("/verify")
async def verify_payment(request: VerifyRequest):
    if not request.order_id and not request.stripe_intent_id and not request.solana_signature:
        raise HTTPException(status_code=400, detail="Provide order_id, stripe_intent_id, or solana_signature")

    filters = []
    if request.order_id:
        filters.append(ledger_entries.c.order_id == request.order_id)
    if request.stripe_intent_id:
        filters.append(ledger_entries.c.stripe_intent_id == request.stripe_intent_id)
    if request.solana_signature:
        filters.append(ledger_entries.c.solana_signature == request.solana_signature)

    query = ledger_entries.select().where(or_(*filters))
    row = await db.database.fetch_one(query)
    if not row:
        return {"status": "not_found"}

    return {
        "status": "verified",
        "entry": dict(row),
    }
