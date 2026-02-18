import os
from typing import Iterable
from urllib.parse import urlparse

from fastapi import HTTPException


def _allowed_hosts() -> set[str]:
    hosts = os.getenv("ALLOWED_REDIRECT_HOSTS", "").split(",")
    cleaned = [h.strip() for h in hosts if h.strip()]
    if cleaned:
        return set(cleaned)
    return {"localhost:3003", "localhost:3000"}


def validate_redirect_url(url: str, allowed_hosts: Iterable[str] | None = None) -> str:
    if not url:
        raise HTTPException(status_code=400, detail="Redirect URL is required")

    parsed = urlparse(url)
    if not parsed.netloc:
        if not url.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid redirect URL")
        return url

    env = os.getenv("ENVIRONMENT", "production").lower()
    allowed = set(allowed_hosts or _allowed_hosts())
    if not allowed:
        raise HTTPException(status_code=400, detail="Redirect URL is not allowed")

    if parsed.netloc not in allowed:
        raise HTTPException(status_code=400, detail="Redirect host is not allowed")

    if parsed.scheme not in ("https", "http"):
        raise HTTPException(status_code=400, detail="Invalid redirect scheme")

    if env == "production" and parsed.scheme != "https":
        raise HTTPException(status_code=400, detail="Redirect must use https")

    return url
