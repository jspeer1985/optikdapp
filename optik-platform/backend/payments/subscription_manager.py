import stripe
from .stripe_client import StripeClient

class SubscriptionManager:
    def __init__(self):
        self.client = StripeClient()

    async def subscribe_user(self, customer_id, price_id):
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                expand=["latest_invoice.payment_intent"]
            )
            return subscription
        except Exception as e:
            print(f"Error subscribing user: {e}")
            return None

    async def cancel_subscription(self, subscription_id):
        try:
            cancelled_subscription = stripe.Subscription.delete(subscription_id)
            return cancelled_subscription
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
            return None

    async def get_user_subscriptions(self, customer_id):
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id, status='all')
            return subscriptions.data
        except Exception as e:
            print(f"Error fetching user subscriptions: {e}")
            return []
