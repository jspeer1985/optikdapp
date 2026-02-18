from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class LedgerEntry(BaseModel):
    id: str
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

class OrderAudit(BaseModel):
    order_id: str
    events: list[dict] # [{time, event, status}]
    
# In-memory storage for current dev preview, 
# but structured to be swapped for a database instantly.
GLOBAL_LEDGER: Dict[str, LedgerEntry] = {}

def record_transaction(entry: LedgerEntry):
    GLOBAL_LEDGER[entry.id] = entry
    print(f"📖 LEDGER RECORDED: {entry.transaction_type} | {entry.merchant_payout} {entry.currency} to {entry.merchant_id}")

def get_merchant_balance(merchant_id: str) -> Dict:
    merchant_entries = [e for e in GLOBAL_LEDGER.values() if e.merchant_id == merchant_id]
    total_revenue = sum(e.merchant_payout for e in merchant_entries if e.status == 'settled')
    return {
        "merchant_id": merchant_id,
        "settled_balance": total_revenue,
        "entry_count": len(merchant_entries)
    }
