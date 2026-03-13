"""
Onboarding Routes - Mock Implementation
Handles user onboarding endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


@router.get("/steps")
async def get_onboarding_steps(user=Depends(get_current_user)):
    """Get onboarding steps for current user"""
    return {
        "steps": [
            {"id": 1, "name": "Connect Wallet", "completed": False},
            {"id": 2, "name": "Create Store", "completed": False},
            {"id": 3, "name": "Deploy DApp", "completed": False}
        ]
    }


@router.post("/complete")
async def complete_step(step_data: Dict[str, Any], user=Depends(get_current_user)):
    """Complete an onboarding step"""
    return {"message": "Step completed successfully", "next_step": step_data.get("step_id", 1) + 1}
