import stripe
import os
from fastapi import Request, HTTPException
import logging

from utils.database import db

logger = logging.getLogger(__name__)


class WebhookHandler:
    def __init__(self):
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    async def handle_webhook(self, request: Request):
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not self.webhook_secret:
            raise HTTPException(status_code=400, detail="Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

        existing = await db.get_webhook_event("stripe", event["id"])
        if existing:
            return {"status": "duplicate"}

        await db.record_webhook_event("stripe", event["id"], event)

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await self._handle_successful_payment(session)
        elif event["type"] == "charge.refunded":
            charge = event["data"]["object"]
            await self._handle_refund(charge)
        elif event["type"] == "invoice.paid":
            invoice = event["data"]["object"]
            await self._handle_paid_invoice(invoice)
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            await self._handle_subscription_cancelled(subscription)

        await db.mark_webhook_processed("stripe", event["id"], status="processed")
        return {"status": "success"}

    async def _handle_successful_payment(self, session):
        metadata = session.get("metadata", {})
        session_type = metadata.get("type")

        if session_type == "dapp_purchase":
            entry = {
                "id": session["id"],
                "order_id": metadata.get("order_id", "unknown"),
                "merchant_id": metadata.get("merchant_id", "unknown"),
                "transaction_type": "fiat",
                "status": "settled",
                "gross_amount": session.get("amount_total", 0),
                "platform_fee": int(metadata.get("platform_fee_cents", 0)),
                "merchant_payout": session.get("amount_total", 0) - int(metadata.get("platform_fee_cents", 0)),
                "currency": session.get("currency", "usd"),
                "stripe_intent_id": session.get("payment_intent"),
                "metadata": metadata,
            }
            await db.record_ledger_entry(entry)
            logger.info(f"Ledger updated for order {entry['order_id']}")
        elif session_type == "onboarding":
            await db.update_onboarding_payment_status(session.get("id"), "paid")
            logger.info(f"Onboarding payment recorded for session {session.get('id')}")
        else:
            logger.info(f"Subscription active for {session.get('customer_email')}")

    async def _handle_refund(self, charge):
        intent_id = charge.get("payment_intent")
        if not intent_id:
            return
        logger.info(f"Refund received for payment intent {intent_id}")

    async def _handle_paid_invoice(self, invoice):
        logger.info(f"Invoice paid: {invoice['id']}")

    async def _handle_subscription_cancelled(self, subscription):
        logger.info(f"Subscription cancelled: {subscription['id']}")
