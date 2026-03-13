"""
Connect Routes - Mock Implementation
Handles wallet connection endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/connect", tags=["connect"])


@router.get("/wallets")
async def get_wallets():
    """Get available wallet connections"""
    return {
        "wallets": [
            {"name": "phantom", "display_name": "Phantom", "icon": "👻"},
            {"name": "solflare", "display_name": "Solflare", "icon": "🔥"},
            {"name": "backpack", "display_name": "Backpack", "icon": "🎒"}
        ]
    }


@router.post("/disconnect")
async def disconnect_wallet(wallet_data: Dict[str, Any], user=Depends(get_current_user)):
    """Disconnect a wallet"""
    return {"message": "Wallet disconnected successfully"}
