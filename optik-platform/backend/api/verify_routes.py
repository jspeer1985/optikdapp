"""
Verify Routes - Mock Implementation
Handles verification endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/verify", tags=["verify"])


@router.post("/wallet")
async def verify_wallet(wallet_data: Dict[str, Any]):
    """Verify wallet ownership"""
    return {"verified": True, "message": "Wallet verified successfully"}


@router.post("/domain")
async def verify_domain(domain_data: Dict[str, Any], user=Depends(get_current_user)):
    """Verify domain ownership"""
    return {"verified": True, "message": "Domain verified successfully"}
