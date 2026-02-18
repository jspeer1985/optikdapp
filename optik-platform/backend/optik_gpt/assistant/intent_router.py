from typing import Dict, Any

def route_intent(message: str) -> str:
    """
    Lightweight intent router for Optik Assistant.
    """
    msg = message.lower()

    if "create product" in msg or "list item" in msg or "add product" in msg:
        return "CREATE_PRODUCT"

    if "deploy store" in msg or "launch store" in msg:
        return "DEPLOY_STORE"

    if "sales" in msg or "check sales" in msg or "revenue" in msg:
        return "CHECK_SALES"

    if "withdraw" in msg or "payout" in msg:
        return "WITHDRAW_FUNDS"

    if "staking" in msg or "stake" in msg:
        return "SETUP_STAKING"
        
    if "help" in msg:
        return "GENERAL_HELP"

    return "UNKNOWN_INTENT"
