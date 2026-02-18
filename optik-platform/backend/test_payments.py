#!/usr/bin/env python3
"""
Test Stripe Payment Integration
Run this to verify your Stripe setup is working
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def test_payment_plans():
    """Test getting payment plans"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/payments/plans")
        
        if response.status_code == 200:
            print("✅ Payment plans endpoint working")
            plans = response.json()
            print(f"   Available plans: {list(plans.get('plans', {}).keys())}")
            return True
        else:
            print(f"❌ Payment plans failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment plans: {str(e)}")
        return False

def test_checkout_session():
    """Test creating a checkout session"""
    try:
        payload = {
            "plan_id": "starter",
            "customer_email": "test@example.com",
            "success_url": "http://localhost:3003/success",
            "cancel_url": "http://localhost:3003/cancel"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/payments/checkout",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Checkout session creation working")
            session_data = response.json()
            print(f"   Session ID: {session_data.get('session_id')}")
            print(f"   Checkout URL: {session_data.get('checkout_url')}")
            return True
        else:
            print(f"❌ Checkout session failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing checkout: {str(e)}")
        return False

def test_stripe_keys():
    """Test if Stripe keys are properly configured"""
    try:
        import stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        
        # Test by creating a product (this will fail with bad keys)
        try:
            product = stripe.Product.create(
                name="Test Product",
                description="Test product for key validation"
            )
            # Clean up test product
            stripe.Product.delete(product.id)
            print("✅ Stripe keys are valid")
            return True
        except stripe.error.AuthenticationError:
            print("❌ Stripe secret key is invalid")
            return False
        except stripe.error.RateLimitError:
            print("✅ Stripe keys are valid (rate limited)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Stripe keys: {str(e)}")
        return False

def test_simple_server():
    """Test if the simple server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            print("✅ Backend server is running")
            health = response.json()
            print(f"   Status: {health.get('status')}")
            return True
        else:
            print(f"❌ Backend server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend server not accessible: {str(e)}")
        return False

def main():
    print("🧪 Testing Optik Platform Payment System")
    print("=" * 50)
    
    # Test basic connectivity
    print("\n1. Testing backend connectivity...")
    server_ok = test_simple_server()
    
    # Test Stripe configuration
    print("\n2. Testing Stripe configuration...")
    stripe_ok = test_stripe_keys()
    
    if server_ok:
        # Test payment endpoints
        print("\n3. Testing payment plans...")
        plans_ok = test_payment_plans()
        
        print("\n4. Testing checkout session...")
        checkout_ok = test_checkout_session()
    else:
        plans_ok = False
        checkout_ok = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Backend Server: {'✅' if server_ok else '❌'}")
    print(f"   Stripe Keys: {'✅' if stripe_ok else '❌'}")
    print(f"   Payment Plans: {'✅' if plans_ok else '❌'}")
    print(f"   Checkout Session: {'✅' if checkout_ok else '❌'}")
    
    if all([server_ok, stripe_ok, plans_ok, checkout_ok]):
        print("\n🎉 All tests passed! Your payment system is ready!")
        print("\nNext steps:")
        print("1. Add your real Stripe keys to .env")
        print("2. Run stripe_setup.py to create products")
        print("3. Test with the frontend")
        print("4. Go live!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("1. Make sure backend is running on port 8000")
        print("2. Add valid Stripe keys to .env")
        print("3. Check if payment routes are properly included")

if __name__ == "__main__":
    main()
