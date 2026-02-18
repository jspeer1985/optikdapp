from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/security", tags=["security"])


class WhitelistRequest(BaseModel):
    ip: str


@router.get("/events")
async def list_events(user=Depends(get_current_user)):
    events = await db.list_security_events(user.id)
    return {"events": events}


@router.get("/whitelist")
async def get_whitelist(user=Depends(get_current_user)):
    ips = await db.list_ip_whitelist(user.id)
    return {"ips": ips}


@router.post("/whitelist")
async def add_whitelist(request: WhitelistRequest, user=Depends(get_current_user)):
    if not request.ip:
        raise HTTPException(status_code=400, detail="IP address required")
    await db.add_ip_whitelist(user.id, request.ip)
    await db.record_security_event(user.id, f"IP whitelisted: {request.ip}")
    return {"success": True}


@router.post("/freeze")
async def freeze_account(user=Depends(get_current_user)):
    await db.create_security_action(user.id, "freeze")
    await db.record_security_event(user.id, "Account freeze requested")
    return {"success": True, "status": "requested"}
