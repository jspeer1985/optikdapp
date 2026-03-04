from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List
import logging
import uuid
from utils.database import db

logger = logging.getLogger("CashierLedger")

class LedgerEntry(BaseModel):
    id: Optional[str] = None
    job_id: Optional[str] = None
    order_id: str
    merchant_id: str
    transaction_type: str  # 'fiat' or 'crypto'
    status: str  # 'pending', 'settled', 'refunded', 'disputed'
    
    # Financials (in smallest unit, e.g., cents or lamports)
    gross_amount: int
    platform_fee: int
    merchant_payout: int
    currency: str
    
    # External References
    stripe_intent_id: Optional[str] = None
    solana_signature: Optional[str] = None
    
    # Traceability
    metadata: Dict = {}
    timestamp: datetime = datetime.utcnow()

async def record_transaction(entry: LedgerEntry):
    """Persists a transaction to the SQL ledger."""
    if not entry.id:
        entry.id = f"tx_{uuid.uuid4().hex[:8]}"
    
    try:
        query = """
            INSERT INTO transactions (
                id, job_id, order_id, merchant_id, transaction_type, status, 
                gross_amount, platform_fee, merchant_payout, currency, 
                stripe_intent_id, solana_signature, created_at
            ) VALUES (
                :id, :job_id, :order_id, :merchant_id, :transaction_type, :status,
                :gross_amount, :platform_fee, :merchant_payout, :currency,
                :stripe_intent_id, :solana_signature, :created_at
            )
        """
        values = {
            "id": entry.id,
            "job_id": entry.job_id,
            "order_id": entry.order_id,
            "merchant_id": entry.merchant_id,
            "transaction_type": entry.transaction_type,
            "status": entry.status,
            "gross_amount": entry.gross_amount,
            "platform_fee": entry.platform_fee,
            "merchant_payout": entry.merchant_payout,
            "currency": entry.currency,
            "stripe_intent_id": entry.stripe_intent_id,
            "solana_signature": entry.solana_signature,
            "created_at": entry.timestamp
        }
        await db.database.execute(query=query, values=values)
        logger.info(f"📖 LEDGER RECORDED: {entry.id} | {entry.merchant_payout} {entry.currency} for {entry.merchant_id}")
        return entry.id
    except Exception as e:
        logger.error(f"Failed to record transaction: {e}")
        raise

async def get_merchant_balance(merchant_id: str) -> Dict:
    """Calculates balances from the persistent ledger."""
    query = "SELECT * FROM transactions WHERE merchant_id = :merchant_id AND status = 'settled'"
    rows = await db.database.fetch_all(query=query, values={"merchant_id": merchant_id})
    
    total_revenue = sum(row["merchant_payout"] for row in rows)
    total_gross = sum(row["gross_amount"] for row in rows)
    total_fees = sum(row["platform_fee"] for row in rows)
    
    return {
        "merchant_id": merchant_id,
        "settled_balance": total_revenue,
        "gross_volume": total_gross,
        "fees_generated": total_fees,
        "transaction_count": len(rows)
    }

async def get_platform_stats() -> Dict:
    """Total metrics for the Optik Cashier."""
    query = "SELECT SUM(platform_fee) as total_fees, COUNT(*) as count FROM transactions WHERE status = 'settled'"
    row = await db.database.fetch_one(query=query)
    return {
        "total_revenue_fees": row["total_fees"] or 0,
        "total_transactions": row["count"] or 0
    }
