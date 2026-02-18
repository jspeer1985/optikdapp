import os
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from payments.stripe_client import StripeClient
from utils.validators import validate_redirect_url

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])
stripe_client = StripeClient()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3003")


class OnboardingCheckoutRequest(BaseModel):
    success_url: str
    cancel_url: str
    agreement_version: str


class AgreementRequest(BaseModel):
    agreement_version: str


@router.post("/agreement")
async def sign_agreement(request_body: AgreementRequest, request: Request, user=Depends(get_current_user)):
    if not request_body.agreement_version:
        raise HTTPException(status_code=400, detail="Agreement version required")

    agreement_id = await db.record_agreement(
        user_id=user.id,
        agreement_version=request_body.agreement_version,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"success": True, "agreement_id": agreement_id}


@router.get("/status")
async def onboarding_status(user=Depends(get_current_user)):
    agreement = await db.get_latest_agreement(user.id)
    payment = await db.get_onboarding_payment(user.id)

    return {
        "agreement_signed": bool(agreement),
        "agreement_version": agreement.get("agreement_version") if agreement else None,
        "payment_status": payment.get("status") if payment else None,
        "payment_amount_cents": payment.get("amount_cents") if payment else None,
    }


@router.post("/checkout")
async def onboarding_checkout(request_body: OnboardingCheckoutRequest, user=Depends(get_current_user)):
    if not user.email:
        raise HTTPException(status_code=400, detail="Email required for checkout")

    amount_cents = int(os.getenv("ONBOARDING_FEE_CENTS", "4900"))
    currency = os.getenv("ONBOARDING_FEE_CURRENCY", "usd")
    success_url = _resolve_url(validate_redirect_url(request_body.success_url))
    cancel_url = _resolve_url(validate_redirect_url(request_body.cancel_url))

    price_data = {
        "currency": currency,
        "product_data": {"name": "Optik Enterprise Onboarding"},
        "unit_amount": amount_cents,
    }

    session = await stripe_client.create_checkout_session(
        customer_email=user.email,
        price_data=price_data,
        success_url=success_url,
        cancel_url=cancel_url,
        mode="payment",
        metadata={
            "type": "onboarding",
            "user_id": user.id,
            "agreement_version": request_body.agreement_version,
            "non_refundable": "true",
        },
    )

    await db.create_onboarding_payment(user.id, session.id, amount_cents, currency)

    return {"checkout_url": session.url}


def _resolve_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc:
        return url
    return f"{FRONTEND_URL}{url}"
