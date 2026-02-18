#!/usr/bin/env python3
"""
Stripe Connect Setup for Optik Platform
Collecting percentages from each transaction (Marketplace Model)
"""

import stripe
import os
import json
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def setup_stripe_connect():
    """Setup Stripe Connect for collecting platform fees"""
    
    # 1. Create your platform Connect account
    try:
        platform_account = stripe.Account.create(
            type="express",
            country="US",
            email="platform@optik.com",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="company",
            company={
                "name": "Optik Platform",
                "address": {
                    "line1": "123 Tech Street",
                    "city": "San Francisco", 
                    "state": "CA",
                    "postal_code": "94105",
                    "country": "US"
                }
            }
        )
        
        print(f"✅ Platform Connect Account Created: {platform_account.id}")
        print(f"   Dashboard: https://dashboard.stripe.com/connect/accounts/{platform_account.id}")
        print()
        
        return platform_account
        
    except Exception as e:
        print(f"❌ Error creating platform account: {str(e)}")
        return None

def create_merchant_onboarding(merchant_email, merchant_name):
    """Create onboarding link for new merchants"""
    
    try:
        # Create Express account for merchant
        merchant_account = stripe.Account.create(
            type="express",
            country="US",
            email=merchant_email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="individual",
            individual={
                "email": merchant_email,
                "first_name": merchant_name.split()[0],
                "last_name": " ".join(merchant_name.split()[1:]) if len(merchant_name.split()) > 1 else "Merchant"
            }
        )
        
        # Create onboarding link
        account_link = stripe.AccountLink.create(
            account=merchant_account.id,
            refresh_url="https://optik.com/merchant/refresh",
            return_url="https://optik.com/merchant/complete",
            type="account_onboarding"
        )
        
        return {
            "merchant_account_id": merchant_account.id,
            "onboarding_url": account_link.url,
            "expires_at": account_link.expires_at
        }
        
    except Exception as e:
        print(f"❌ Error creating merchant account: {str(e)}")
        return None

def create_direct_charge_with_fee(merchant_account_id, amount_cents, platform_fee_percent=3.0):
    """
    Create a direct charge where you collect a percentage fee
    
    Example: $100 transaction with 3% fee
    - Customer pays: $100.00
    - Merchant receives: $97.00  
    - Platform receives: $3.00
    """
    
    try:
        # Calculate platform fee in cents
        platform_fee_cents = int(amount_cents * (platform_fee_percent / 100))
        
        # Create payment intent with platform fee
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method_types=["card"],
            application_fee_amount=platform_fee_cents,
            transfer_data={
                "destination": merchant_account_id,
            },
            metadata={
                "platform_fee_percent": str(platform_fee_percent),
                "platform_fee_cents": str(platform_fee_cents),
                "merchant_account_id": merchant_account_id,
                "type": "marketplace_transaction"
            }
        )
        
        print(f"✅ Payment Intent Created:")
        print(f"   Total Amount: ${amount_cents/100:.2f}")
        print(f"   Platform Fee ({platform_fee_percent}%): ${platform_fee_cents/100:.2f}")
        print(f"   Merchant Receives: ${(amount_cents - platform_fee_cents)/100:.2f}")
        print(f"   Payment Intent ID: {payment_intent.id}")
        print()
        
        return payment_intent
        
    except Exception as e:
        print(f"❌ Error creating payment: {str(e)}")
        return None

def create_checkout_with_platform_fee(merchant_account_id, amount_cents, platform_fee_percent=3.0):
    """Create checkout session with platform fee collection"""
    
    try:
        platform_fee_cents = int(amount_cents * (platform_fee_percent / 100))
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Optik DApp Conversion Service',
                        'description': f'Professional Web3 conversion with {platform_fee_percent}% platform fee',
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://optik.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://optik.com/cancel',
            payment_intent_data={
                'application_fee_amount': platform_fee_cents,
                'transfer_data': {
                    'destination': merchant_account_id,
                },
            },
            metadata={
                'platform_fee_percent': str(platform_fee_percent),
                'platform_fee_cents': str(platform_fee_cents),
                'merchant_account_id': merchant_account_id,
                'type': 'marketplace_transaction'
            }
        )
        
        return session
        
    except Exception as e:
        print(f"❌ Error creating checkout: {str(e)}")
        return None

def create_platform_fee_tiers():
    """Create different fee tiers for different merchant levels"""
    
    FEE_TIERS = {
        "starter": {
            "name": "Starter Merchant",
            "platform_fee_percent": 5.0,  # 5% fee
            "description": "Basic merchants pay 5% platform fee"
        },
        "growth": {
            "name": "Growth Merchant", 
            "platform_fee_percent": 3.0,  # 3% fee
            "description": "Growth merchants pay 3% platform fee"
        },
        "pro": {
            "name": "Pro Merchant",
            "platform_fee_percent": 2.0,  # 2% fee
            "description": "Pro merchants pay 2% platform fee"
        },
        "enterprise": {
            "name": "Enterprise Merchant",
            "platform_fee_percent": 1.0,  # 1% fee
            "description": "Enterprise merchants pay 1% platform fee"
        }
    }
    
    print("🏦 Optik Platform Fee Tiers:")
    print("=" * 50)
    
    for tier, config in FEE_TIERS.items():
        print(f"{tier.upper()}: {config['platform_fee_percent']}% - {config['description']}")
    
    print()
    return FEE_TIERS

def simulate_transaction_examples():
    """Show examples of different transaction amounts and fees"""
    
    print("💰 Transaction Examples (3% Platform Fee):")
    print("=" * 50)
    
    transaction_amounts = [10000, 50000, 100000, 500000]  # $100, $500, $1000, $5000
    platform_fee_percent = 3.0
    
    for amount_cents in transaction_amounts:
        platform_fee_cents = int(amount_cents * (platform_fee_percent / 100))
        merchant_receives = amount_cents - platform_fee_cents
        
        print(f"Transaction: ${amount_cents/100:.2f}")
        print(f"  Platform Fee (3%): ${platform_fee_cents/100:.2f}")
        print(f"  Merchant Receives: ${merchant_receives/100:.2f}")
        print(f"  Platform Profit: ${platform_fee_cents/100:.2f}")
        print()

def setup_webhook_for_connect():
    """Setup webhooks to track platform fees and transfers"""
    
    webhook_events = [
        "payment_intent.succeeded",
        "payment_intent.payment_failed", 
        "charge.succeeded",
        "transfer.created",
        "transfer.paid",
        "transfer.failed",
        "account.updated"
    ]
    
    print("🔗 Required Webhook Events for Connect:")
    print("=" * 40)
    
    for event in webhook_events:
        print(f"✅ {event}")
    
    print()
    print("Webhook URL: https://optik.com/api/webhooks/stripe-connect")
    print("These events track:")
    print("- When merchants receive money")
    print("- When platform gets fees")
    print("- When transfers happen")
    print("- Account status changes")

def main():
    print("🚀 Setting up Stripe Connect for Optik Platform")
    print("=" * 60)
    print()
    
    # Show fee structure
    create_platform_fee_tiers()
    
    # Show transaction examples
    simulate_transaction_examples()
    
    # Setup webhooks
    setup_webhook_for_connect()
    
    # Create platform account
    print("1. Creating Platform Connect Account...")
    platform_account = setup_stripe_connect()
    
    if platform_account:
        print("\n2. Example: Creating Merchant Onboarding...")
        merchant = create_merchant_onboarding(
            "merchant@example.com", 
            "John's Store"
        )
        
        if merchant:
            print(f"✅ Merchant Onboarding Ready:")
            print(f"   Merchant Account ID: {merchant['merchant_account_id']}")
            print(f"   Onboarding URL: {merchant['onboarding_url']}")
            print()
            
            print("3. Example: Creating $500 Transaction with 3% Fee...")
            payment = create_direct_charge_with_fee(
                merchant['merchant_account_id'],
                50000,  # $500.00
                3.0     # 3% platform fee
            )
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Complete platform account setup in Stripe Dashboard")
    print("2. Add Connect account ID to your .env file")
    print("3. Update payment endpoints to use destination transfers")
    print("4. Test merchant onboarding flow")
    print("5. Test fee collection with real transactions")
    print()
    print("📚 Documentation: https://stripe.com/docs/connect")

if __name__ == "__main__":
    main()
