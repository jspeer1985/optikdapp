"""
Stripe Connect Routes for Optik Platform
Collecting platform fees from merchant transactions
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import stripe
import os
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from payments.stripe_client import StripeClient
from utils.auth import get_current_user
from utils.database import db
from utils.validators import validate_redirect_url

router = APIRouter(prefix="/api/v1/connect", tags=["stripe-connect"])
logger = logging.getLogger(__name__)

stripe_client = StripeClient()

# Platform fee tiers
PLATFORM_FEES = {
    "basic": 3.0,
    "growth": 5.0,
    "global": 9.0,
    "scale": 12.0,
    "elite": 15.0,
}

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3003")


class MerchantOnboardRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = "Merchant Store"
    tier: str = "basic"
    refresh_url: Optional[str] = None
    return_url: Optional[str] = None


def _resolve_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc:
        return url
    return f"{FRONTEND_URL}{url}"


@router.post("/merchant/onboard")
async def create_merchant_account(request: MerchantOnboardRequest, user=Depends(get_current_user)):
    try:
        merchant_email = request.email or user.email
        merchant_name = request.name or "Merchant Store"
        merchant_tier = request.tier or "basic"

        if not merchant_email:
            raise HTTPException(status_code=400, detail="Email is required")

        merchant_account = await stripe_client.create_express_account(
            email=merchant_email,
            name=merchant_name,
            metadata={"tier": merchant_tier, "platform": "optik", "user_id": user.id},
        )

        refresh_url = _resolve_url(validate_redirect_url(request.refresh_url or "/dashboard/merchant"))
        return_url = _resolve_url(validate_redirect_url(request.return_url or "/dashboard/merchant"))

        account_link = await stripe_client.create_account_link(
            account_id=merchant_account.id,
            refresh_url=refresh_url,
            return_url=return_url,
        )

        await db.upsert_merchant(user.id, merchant_account.id, merchant_tier, "pending")

        return {
            "success": True,
            "merchant_account_id": merchant_account.id,
            "onboarding_url": account_link.url,
            "expires_at": account_link.expires_at,
            "platform_fee_percent": PLATFORM_FEES.get(merchant_tier, 3.0),
        }

    except stripe.error.StripeError as e:
        logger.error(f"Merchant onboarding error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/merchant/me")
async def get_my_merchant(user=Depends(get_current_user)):
    merchant = await db.get_merchant_by_user(user.id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    account = None
    if merchant.get("stripe_account_id"):
        try:
            account = await stripe_client.retrieve_account(merchant["stripe_account_id"])
        except Exception:
            account = None

    return {
        "merchant": merchant,
        "stripe": {
            "charges_enabled": getattr(account, "charges_enabled", None),
            "payouts_enabled": getattr(account, "payouts_enabled", None),
        } if account else None,
    }


@router.post("/merchant/link")
async def refresh_onboarding_link(user=Depends(get_current_user)):
    merchant = await db.get_merchant_by_user(user.id)
    if not merchant or not merchant.get("stripe_account_id"):
        raise HTTPException(status_code=404, detail="Merchant not found")

    refresh_url = _resolve_url(validate_redirect_url("/dashboard/merchant"))
    return_url = _resolve_url(validate_redirect_url("/dashboard/merchant"))

    account_link = await stripe_client.create_account_link(
        account_id=merchant["stripe_account_id"],
        refresh_url=refresh_url,
        return_url=return_url,
    )

    return {"onboarding_url": account_link.url, "expires_at": account_link.expires_at}


@router.get("/fees")
async def get_platform_fees():
    return {
        "success": True,
        "fee_tiers": PLATFORM_FEES,
        "description": "Platform collects percentage of each transaction",
        "example": {
            "transaction_amount": "$100.00",
            "basic_tier_fee": "$3.00 (3%)",
            "growth_tier_fee": "$5.00 (5%)",
            "global_tier_fee": "$9.00 (9%)",
            "scale_tier_fee": "$12.00 (12%)",
            "elite_tier_fee": "$15.00 (15%)",
        },
    }


@router.post("/webhook")
async def connect_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.warning("Webhook secret not configured")
            return JSONResponse(status_code=400)

        body = await request.body()
        sig_header = request.headers.get("stripe-signature")

        try:
            event = stripe.Webhook.construct_event(body, sig_header, webhook_secret)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return JSONResponse(status_code=400)

        if event["type"] == "account.updated":
            account = event["data"]["object"]
            merchant = await db.get_merchant_by_stripe_account_id(account["id"])
            if merchant:
                status = "active" if account.get("charges_enabled") and account.get("payouts_enabled") else "pending"
                await db.upsert_merchant(merchant["user_id"], account["id"], merchant.get("tier", "basic"), status)

        return JSONResponse(status_code=200)

    except Exception as e:
        logger.error(f"Connect webhook processing error: {str(e)}")
        return JSONResponse(status_code=500)
