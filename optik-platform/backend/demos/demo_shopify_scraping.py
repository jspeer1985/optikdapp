#!/usr/bin/env python3
"""
Demo Script - Shopify Scraping & dApp Integration
Shows how to use the complete system
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000"

def demo_shopify_scraping():
    """Demonstrate Shopify scraping functionality"""
    print("🚀 Optik Platform - Shopify Scraping Demo")
    print("=" * 50)
    
    # 1. Check API Health
    print("\n1️⃣ Checking API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend API is healthy!")
            print(f"   Services: {response.json().get('services', {})}")
        else:
            print("❌ Backend API not responding")
            return
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return
    
    # 2. Check Scraping Status
    print("\n2️⃣ Checking Scraping System Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/shopify-scraping/scraping-status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Scraping system active!")
            print(f"   Cached stores: {status.get('total_cached_stores', 0)}")
            print(f"   MCP Server: {status.get('mcp_server_status', 'unknown')}")
        else:
            print("⚠️ Scraping endpoints may need authentication")
    except Exception as e:
        print(f"⚠️ Scraping status check: {e}")
    
    # 3. Get Available dApp Features
    print("\n3️⃣ Getting Available dApp Features...")
    try:
        response = requests.get(f"{BASE_URL}/api/dapp-integration/feature-types")
        if response.status_code == 200:
            features = response.json()
            print("✅ Available dApp Features:")
            for feature_type, info in features.get('feature_types', {}).items():
                print(f"   • {info['name']}: {info['description']}")
                print(f"     Best for: {info['best_for']}")
                print(f"     Typical ROI: {info['typical_roi']}")
                print()
        else:
            print("⚠️ Feature types endpoint may need authentication")
    except Exception as e:
        print(f"⚠️ Feature types check: {e}")
    
    # 4. Get Smart Contract Templates
    print("\n4️⃣ Getting Smart Contract Templates...")
    try:
        response = requests.get(f"{BASE_URL}/api/dapp-integration/smart-contract-templates")
        if response.status_code == 200:
            templates = response.json()
            print("✅ Available Smart Contract Templates:")
            for template_name, template_info in templates.get('templates', {}).items():
                print(f"   • {template_info['name']}")
                print(f"     {template_info['description']}")
                print(f"     Features: {', '.join(template_info['features'])}")
                print()
        else:
            print("⚠️ Templates endpoint may need authentication")
    except Exception as e:
        print(f"⚠️ Templates check: {e}")
    
    # 5. Example Shopify Store Scrape (Demo)
    print("\n5️⃣ Example Shopify Store Scrape...")
    print("📝 To scrape a real store, you'll need:")
    print("   • Shopify store domain (e.g., mystore.myshopify.com)")
    print("   • Shopify app credentials (Client ID & Secret)")
    print("   • Proper API permissions")
    
    example_config = {
        "store_domain": "demo-store.myshopify.com",
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here",
        "store_name": "Demo Fashion Store",
        "niche": "fashion"
    }
    
    print(f"\n📋 Example request payload:")
    print(json.dumps(example_config, indent=2))
    
    print("\n🔗 API Endpoints you can use:")
    print(f"   POST {BASE_URL}/api/shopify-scraping/scrape-single")
    print(f"   POST {BASE_URL}/api/shopify-scraping/scrape-batch")
    print(f"   GET  {BASE_URL}/api/shopify-scraping/export-dapp-data")
    
    print("\n🎯 dApp Integration Endpoints:")
    print(f"   GET  {BASE_URL}/api/dapp-integration/store-profile/{{domain}}")
    print(f"   GET  {BASE_URL}/api/dapp-integration/market-analysis")
    print(f"   GET  {BASE_URL}/api/dapp-integration/roi-calculator")
    
    print("\n📚 Documentation:")
    print(f"   Swagger UI: {BASE_URL}/api/docs")
    print(f"   ReDoc: {BASE_URL}/api/redoc")
    print(f"   Frontend: http://localhost:3003")
    
    print("\n✨ Demo Complete! Your Optik Platform is ready to use!")
    print("📖 See SHOPIFY_SCRAPING_GUIDE.md for detailed instructions")

def demo_roi_calculator():
    """Demonstrate ROI calculator"""
    print("\n💰 ROI Calculator Demo")
    print("-" * 30)
    
    # Example metrics
    params = {
        "current_revenue": 50000,  # $50k/month
        "current_conversion_rate": 2.5,  # 2.5%
        "current_aov": 85,  # $85 average order value
        "feature_types": ["loyalty_program", "cart_recovery"]
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/dapp-integration/roi-calculator",
            params=params
        )
        if response.status_code == 200:
            roi_data = response.json()
            print("✅ ROI Analysis Results:")
            summary = roi_data.get('summary', {})
            print(f"   Implementation Cost: ${summary.get('total_implementation_cost', 0):,.2f}")
            print(f"   Annual Revenue Increase: ${summary.get('total_annual_revenue_increase', 0):,.2f}")
            print(f"   Overall ROI: {summary.get('overall_roi_percentage', 0):.1f}%")
            print(f"   Payback Period: {summary.get('payback_period_months', 'N/A')} months")
        else:
            print("⚠️ ROI calculator may need authentication")
    except Exception as e:
        print(f"⚠️ ROI calculation: {e}")

if __name__ == "__main__":
    demo_shopify_scraping()
    demo_roi_calculator()
