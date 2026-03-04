import asyncio
import logging
import os
from datetime import datetime

# Setup environment
os.environ["ENVIRONMENT"] = "development"

from utils.database import db
from payments.ledger import record_transaction, LedgerEntry, get_merchant_balance, get_platform_stats
from agents.outreach_agent import outreach_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SalesRevenueTest")

async def test_sales_and_revenue_flow():
    try:
        await db.connect()
        logger.info("--- STARTING SALESMAN & CASHIER TEST ---")

        # 1. FIND THE BREEO JOB
        query = "SELECT id, user_id FROM jobs WHERE store_url LIKE '%breeo%' AND status = 'deployed' LIMIT 1"
        job = await db.database.fetch_one(query=query)
        
        if not job:
            logger.error("Breeo job not found in 'deployed' state. Run run_breeo_conversion.py first.")
            return

        job_id = job["id"]
        merchant_id = job["user_id"]
        
        # 2. THE CASHIER: RECORD A MOCK SALE
        logger.info(f"💰 Simulating a $100 sale for Breeo (Job: {job_id})")
        
        # Calculate fees (e.g., 5% for Growth tier)
        gross_amount = 10000 # $100.00 in cents
        platform_fee = int(gross_amount * 0.05) # $5.00
        merchant_payout = gross_amount - platform_fee # $95.00
        
        entry = LedgerEntry(
            job_id=job_id,
            order_id=f"order_breeo_{datetime.now().strftime('%H%M%S')}",
            merchant_id=merchant_id,
            transaction_type="fiat",
            status="settled",
            gross_amount=gross_amount,
            platform_fee=platform_fee,
            merchant_payout=merchant_payout,
            currency="usd",
            stripe_intent_id="pi_mock_12345"
        )
        
        tx_id = await record_transaction(entry)
        logger.info(f"✅ Transaction recorded: {tx_id}")

        # 3. CHECK BALANCES
        balance = await get_merchant_balance(merchant_id)
        logger.info(f"📊 Merchant Balance: {balance}")
        
        stats = await get_platform_stats()
        logger.info(f"📈 Platform Revenue (Fees Collected): {stats['total_revenue_fees'] / 100} USD")

        # 4. THE SALESMAN: GENERATE PITCH
        logger.info("--- TESTING THE SALESMAN ---")
        pitch_data = await outreach_agent.generate_pitch(job_id)
        if pitch_data:
            logger.info(f"📧 Generated Pitch for {pitch_data['store_name']}:")
            logger.info("-" * 40)
            logger.info(pitch_data['pitch'])
            logger.info("-" * 40)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(test_sales_and_revenue_flow())
