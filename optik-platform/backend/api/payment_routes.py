from fastapi import APIRouter, Depends, HTTPException, Request
import os
from urllib.parse import urlparse
from typing import Optional
from pydantic import BaseModel

from payments.stripe_client import StripeClient
from payments.subscription_manager import SubscriptionManager
from payments.webhook_handler import WebhookHandler
from payments.plans import get_plans
from utils.auth import get_current_user
from utils.database import db
from utils.validators import validate_redirect_url

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3003")

stripe_client = StripeClient()
subscription_manager = SubscriptionManager()
webhook_handler = WebhookHandler()


class CheckoutRequest(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str
    customer_email: Optional[str] = None


class DappPaymentRequest(BaseModel):
    amount_cents: int
    currency: str = "usd"
    merchant_id: Optional[str] = None
    merchant_stripe_account_id: Optional[str] = None
    fee_percentage: Optional[float] = None
    product_name: str
    order_id: str
    success_url: str
    cancel_url: str


class PaymentLinkRequest(BaseModel):
    amount_cents: int
    currency: str = "usd"
    product_name: str
    success_url: str
    cancel_url: str



def _resolve_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc:
        return url
    return f"{FRONTEND_URL}{url}"


@router.get("/plans")
async def list_plans():
    return {"plans": get_plans(), "currency": "USD"}


@router.post("/checkout")
async def create_checkout_session(request: CheckoutRequest, user=Depends(get_current_user)):
    plans = get_plans()
    plan = plans.get(request.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    success_url = _resolve_url(validate_redirect_url(request.success_url))
    cancel_url = _resolve_url(validate_redirect_url(request.cancel_url))

    customer_email = request.customer_email or user.email
    if not customer_email:
        raise HTTPException(status_code=400, detail="Customer email required")

    price_id = plan.get("stripe_price_id")
    if price_id:
        session = await stripe_client.create_checkout_session(
            customer_email=customer_email,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            mode=plan.get("billing_mode", "payment"),
        )
    else:
        price_data = {
            "currency": plan.get("currency", "usd"),
            "product_data": {"name": plan.get("name", request.plan_id)},
            "unit_amount": plan.get("price"),
        }
        session = await stripe_client.create_checkout_session(
            customer_email=customer_email,
            price_data=price_data,
            success_url=success_url,
            cancel_url=cancel_url,
            mode=plan.get("billing_mode", "payment"),
        )

    return {"success": True, "checkout_url": session.url}


@router.post("/payment-link")
async def create_payment_link(request: PaymentLinkRequest, user=Depends(get_current_user)):
    success_url = _resolve_url(validate_redirect_url(request.success_url))
    cancel_url = _resolve_url(validate_redirect_url(request.cancel_url))

    session = await stripe_client.create_payment_link(
        amount=request.amount_cents,
        currency=request.currency,
        name=request.product_name,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"checkout_url": session.url}


@router.post("/dapp-payment")
async def create_dapp_payment(request: DappPaymentRequest):
    success_url = _resolve_url(validate_redirect_url(request.success_url))
    cancel_url = _resolve_url(validate_redirect_url(request.cancel_url))

    merchant_account_id = request.merchant_stripe_account_id
    merchant_tier = "basic"

    if request.merchant_id:
        merchant = await db.get_merchant(request.merchant_id)
        if merchant:
            merchant_account_id = merchant.get("stripe_account_id")
            merchant_tier = merchant.get("tier", "basic")

    if not merchant_account_id:
        raise HTTPException(status_code=400, detail="Merchant account not configured")

    tier_fees = {
        "basic": 3.0,
        "growth": 5.0,
        "global": 9.0,
        "scale": 12.0,
        "elite": 15.0,
    }
    fee_percentage = tier_fees.get(merchant_tier, request.fee_percentage or 3.0)

    session = await stripe_client.create_dapp_payment_session(
        amount=request.amount_cents,
        currency=request.currency,
        merchant_account_id=merchant_account_id,
        fee_percentage=fee_percentage,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "order_id": request.order_id,
            "merchant_id": request.merchant_id or merchant_account_id,
            "product_name": request.product_name,
        },
    )
    return {"checkout_url": session.url}


@router.get("/subscriptions")
async def get_my_subscriptions(user=Depends(get_current_user)):
    if not user.email:
        return []

    customer = await stripe_client.get_customer_by_email(user.email)
    if not customer:
        return []

    subscriptions = await subscription_manager.get_user_subscriptions(customer.id)
    return subscriptions


@router.post("/cancel/{subscription_id}")
async def cancel_subscription(subscription_id: str, user=Depends(get_current_user)):
    res = await subscription_manager.cancel_subscription(subscription_id)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    return {"message": "Subscription cancelled"}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    return await webhook_handler.handle_webhook(request)


@router.get("/merchant/stats")
async def get_merchant_reporting(user=Depends(get_current_user)):
    merchant = await db.get_merchant_by_user(user.id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    entries = await db.get_ledger_entries(merchant["id"])

    gross = sum(e.get("gross_amount", 0) for e in entries)
    platform_fees = sum(e.get("platform_fee", 0) for e in entries)
    net = sum(e.get("merchant_payout", 0) for e in entries)

    return {
        "gross_revenue": gross / 100,
        "net_payouts": net / 100,
        "platform_fees": platform_fees / 100,
        "order_count": len(entries),
        "currency": "usd",
        "sys_status": "OPERATIONAL" if entries else "AWAITING_VOLUME",
    }


@router.get("/merchant/transactions")
async def get_merchant_transactions(user=Depends(get_current_user)):
    merchant = await db.get_merchant_by_user(user.id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    entries = await db.get_ledger_entries(merchant["id"])
    return entries


@router.get("/invoices")
async def get_invoices(user=Depends(get_current_user)):
    if not user.email:
        return {"invoices": []}

    customer = await stripe_client.get_customer_by_email(user.email)
    if not customer:
        return {"invoices": []}

    invoices = await stripe_client.list_invoices(customer.id, limit=12)
    payload = []
    for inv in invoices:
        payload.append({
            "id": inv.id,
            "status": inv.status,
            "amount_due": inv.amount_due,
            "amount_paid": inv.amount_paid,
            "currency": inv.currency,
            "hosted_invoice_url": inv.hosted_invoice_url,
            "created": inv.created,
        })

    return {"invoices": payload}
