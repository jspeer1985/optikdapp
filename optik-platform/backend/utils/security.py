import os
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "optik-platform")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "optik-platform")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", os.getenv("JWT_EXPIRATION_MINUTES", "30")))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "30"))


class TokenError(ValueError):
    pass


def _require_secret():
    if not JWT_SECRET:
        raise TokenError("JWT_SECRET is not configured")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def _build_token(payload: Dict[str, Any], expires_at: datetime, token_type: str) -> str:
    _require_secret()
    now = datetime.now(timezone.utc)
    payload = {
        **payload,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: str, session_id: str, role: str) -> Tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    token = _build_token({"sub": user_id, "sid": session_id, "role": role}, expires_at, "access")
    return token, expires_at


def create_refresh_token(user_id: str, session_id: str) -> Tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
    token = _build_token({"sub": user_id, "sid": session_id}, expires_at, "refresh")
    return token, expires_at


def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    _require_secret()
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid token") from exc

    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        raise TokenError("Invalid token type")

    return payload
