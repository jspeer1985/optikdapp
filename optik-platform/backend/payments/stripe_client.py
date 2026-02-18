import stripe
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class StripeClient:
    def __init__(self):
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    def _ensure_key(self):
        if not stripe.api_key:
            raise RuntimeError("STRIPE_SECRET_KEY is not configured")

    async def create_payment_link(self, amount, currency, name, success_url, cancel_url):
        self._ensure_key()
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": name},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session
        except Exception as e:
            logger.error(f"Stripe Payment Link Error: {str(e)}")
            raise e

    async def create_checkout_session(
        self,
        customer_email: str,
        success_url: str,
        cancel_url: str,
        price_id: Optional[str] = None,
        price_data: Optional[Dict[str, Any]] = None,
        mode: str = "payment",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self._ensure_key()
        try:
            if not price_id and not price_data:
                raise ValueError("Either price_id or price_data is required")

            if price_id:
                line_items = [{"price": price_id, "quantity": 1}]
            else:
                line_items = [{"price_data": price_data, "quantity": 1}]

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=customer_email,
                line_items=line_items,
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            return session
        except Exception as e:
            logger.error(f"Stripe Checkout Error: {str(e)}")
            raise e

    async def create_dapp_payment_session(self, amount: int, currency: str, merchant_account_id: str, fee_percentage: float, success_url: str, cancel_url: str, metadata: dict = None):
        """
        Calculates and sets application_fee_amount for Stripe Connect.
        Uses Direct Charges (on behalf of the merchant).
        """
        self._ensure_key()
        try:
            application_fee = int(amount * (fee_percentage / 100))

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": (metadata or {}).get("product_name", "Optik Dapp Product"),
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                payment_intent_data={
                    "application_fee_amount": application_fee,
                    "transfer_data": {
                        "destination": merchant_account_id,
                    },
                },
                metadata={
                    **(metadata or {}),
                    "type": "dapp_purchase",
                    "platform_fee_cents": str(application_fee),
                },
            )
            return session
        except Exception as e:
            logger.error(f"Dapp Payment Session Error: {str(e)}")
            raise e

    async def create_customer(self, email, name=None):
        self._ensure_key()
        try:
            customer = stripe.Customer.create(email=email, name=name)
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None

    async def get_customer_by_email(self, email):
        self._ensure_key()
        try:
            customers = stripe.Customer.list(email=email, limit=1)
            if customers.data:
                return customers.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching customer: {e}")
            return None

    async def list_invoices(self, customer_id: str, limit: int = 10):
        self._ensure_key()
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
            return invoices.data
        except Exception as e:
            logger.error(f"Error fetching invoices: {e}")
            return []

    async def create_express_account(self, email: str, name: str, metadata: Dict[str, str]):
        self._ensure_key()
        return stripe.Account.create(
            type="express",
            country="US",
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="individual",
            individual={
                "email": email,
                "first_name": name.split()[0] if name else "Merchant",
                "last_name": " ".join(name.split()[1:]) if name and len(name.split()) > 1 else "Store",
            },
            metadata=metadata,
        )

    async def create_account_link(self, account_id: str, refresh_url: str, return_url: str):
        self._ensure_key()
        return stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

    async def retrieve_account(self, account_id: str):
        self._ensure_key()
        return stripe.Account.retrieve(account_id)
