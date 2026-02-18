#!/usr/bin/env python3
"""
Test script to verify the conversion pipeline doesn't get stuck at 10%
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import run_conversion_pipeline
from pydantic import BaseModel, HttpUrl

class MockSubmission:
    """Mock submission for testing"""
    def __init__(self):
        self.store_url = "https://example-store.myshopify.com"
        self.platform = "shopify"
        self.tier = "basic"
        self.email = "test@example.com"
        self.api_key = None
        self.api_secret = None

async def test_pipeline():
    """Test the conversion pipeline"""
    print("🧪 Testing conversion pipeline...")
    print("=" * 60)
    
    job_id = "test_job_123"
    submission = MockSubmission()
    
    print(f"📝 Job ID: {job_id}")
    print(f"🏪 Store URL: {submission.store_url}")
    print(f"📦 Platform: {submission.platform}")
    print(f"🎯 Tier: {submission.tier}")
    print("=" * 60)
    
    try:
        # Run the pipeline
        await run_conversion_pipeline(job_id, submission)
        print("\n✅ Pipeline completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting pipeline test...\n")
    success = asyncio.run(test_pipeline())
    
    if success:
        print("\n" + "=" * 60)
        print("✨ Test PASSED - Pipeline completed without getting stuck!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("💥 Test FAILED - Pipeline encountered errors")
        print("=" * 60)
        sys.exit(1)
