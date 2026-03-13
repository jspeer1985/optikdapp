"""
Payment Routes - Mock Implementation
Handles payment processing endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.get("/")
async def get_payments(user=Depends(get_current_user)):
    """Get all payments for current user"""
    return {"payments": [], "message": "Payment routes not implemented yet"}


@router.post("/create")
async def create_payment(payment_data: Dict[str, Any], user=Depends(get_current_user)):
    """Create a new payment"""
    return {"message": "Payment creation not implemented yet", "status": "pending"}
