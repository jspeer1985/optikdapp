from fastapi import APIRouter, Depends
from collections import defaultdict
from datetime import datetime

from utils.auth import get_current_user
from utils.database import db

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary(user=Depends(get_current_user)):
    merchant = await db.get_merchant_by_user(user.id)
    entries = []
    if merchant:
        entries = await db.get_ledger_entries(merchant["id"])

    total_revenue = sum(e.get("gross_amount", 0) for e in entries) / 100
    order_count = len(entries)
    currency = entries[0].get("currency", "usd") if entries else "usd"

    daily = defaultdict(float)
    top_products = defaultdict(lambda: {"revenue": 0.0, "orders": 0})

    for entry in entries:
        created_at = entry.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except Exception:
                created_at = None
        if isinstance(created_at, datetime):
            key = created_at.date().isoformat()
            daily[key] += (entry.get("gross_amount", 0) / 100)

        metadata = entry.get("metadata") or {}
        product_name = metadata.get("product_name") or metadata.get("name") or "Unknown"
        top_products[product_name]["revenue"] += (entry.get("gross_amount", 0) / 100)
        top_products[product_name]["orders"] += 1

    volume_points = [
        {"date": date, "amount": amount}
        for date, amount in sorted(daily.items())
    ]

    top_products_list = [
        {"name": name, "revenue": data["revenue"], "orders": data["orders"]}
        for name, data in sorted(top_products.items(), key=lambda item: item[1]["revenue"], reverse=True)[:5]
    ]

    return {
        "total_revenue": total_revenue,
        "order_count": order_count,
        "currency": currency,
        "volume_points": volume_points,
        "top_products": top_products_list,
    }
