import os
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import base58

from utils.database import db
from utils.security import (
    generate_token,
    hash_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenError,
)
from utils.email import EmailClient
from middleware.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

ACCESS_COOKIE_NAME = os.getenv("ACCESS_COOKIE_NAME", "optik_access")
REFRESH_COOKIE_NAME = os.getenv("REFRESH_COOKIE_NAME", "optik_refresh")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")
NONCE_TTL_MINUTES = int(os.getenv("WALLET_NONCE_TTL_MINUTES", "5"))
MAGIC_LINK_TTL_MINUTES = int(os.getenv("MAGIC_LINK_TTL_MINUTES", "15"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3003")

email_client = EmailClient()

# Strict per-IP rate limiters for auth endpoints
_nonce_limiter = RateLimiter(requests_per_minute=5, requests_per_hour=30)
_magic_link_limiter = RateLimiter(requests_per_minute=3, requests_per_hour=10)
_verify_limiter = RateLimiter(requests_per_minute=5, requests_per_hour=20)


def _client_ip(req: Request) -> str:
    forwarded = req.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return req.client.host if req.client else "unknown"


class WalletNonceRequest(BaseModel):
    wallet_address: str


class WalletVerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    nonce: str
    email: Optional[EmailStr] = None


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerifyRequest(BaseModel):
    token: str


def _build_wallet_message(wallet_address: str, nonce: str, origin: Optional[str]) -> str:
    origin_line = f"Origin: {origin}" if origin else "Origin: unknown"
    return (
        "Optik Platform sign-in\n"
        f"Wallet: {wallet_address}\n"
        f"Nonce: {nonce}\n"
        f"{origin_line}\n"
    )


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, access_expires_at: datetime, refresh_expires_at: datetime):
    # Ensure we're working with timezone-aware datetimes
    now = datetime.now(timezone.utc)
    if access_expires_at.tzinfo is None:
        access_expires_at = access_expires_at.replace(tzinfo=timezone.utc)
    if refresh_expires_at.tzinfo is None:
        refresh_expires_at = refresh_expires_at.replace(tzinfo=timezone.utc)
    
    max_age_access = max(1, int((access_expires_at - now).total_seconds()))
    max_age_refresh = max(1, int((refresh_expires_at - now).total_seconds()))

    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age_access,
        path="/",
        domain=COOKIE_DOMAIN,
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age_refresh,
        path="/api/v1/auth/refresh",
        domain=COOKIE_DOMAIN,
    )


def _clear_auth_cookies(response: Response):
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/", domain=COOKIE_DOMAIN)
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/v1/auth/refresh", domain=COOKIE_DOMAIN)


@router.post("/wallet/nonce")
async def wallet_nonce(request: WalletNonceRequest, req: Request):
    ip = _client_ip(req)
    allowed, retry_after = _nonce_limiter.check_rate_limit(f"nonce:{ip}")
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests", headers={"Retry-After": str(retry_after)})
    logger.info("Wallet nonce requested")
    try:
        wallet_bytes = base58.b58decode(request.wallet_address)
        if len(wallet_bytes) != 32:
            raise ValueError("Invalid wallet address")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid wallet address") from exc

    nonce = generate_token(16)
    expires_at = datetime.utcnow() + timedelta(minutes=NONCE_TTL_MINUTES)
    origin = req.headers.get("origin") or req.headers.get("host")

    await db.create_wallet_nonce(request.wallet_address, nonce, expires_at, origin)

    message = _build_wallet_message(request.wallet_address, nonce, origin)
    return {
        "nonce": nonce,
        "message": message,
        "expires_at": expires_at.isoformat(),
    }


@router.post("/wallet/verify")
async def wallet_verify(request: WalletVerifyRequest, response: Response, req: Request):
    ip = _client_ip(req)
    allowed, retry_after = _verify_limiter.check_rate_limit(f"verify:{ip}")
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests", headers={"Retry-After": str(retry_after)})
    nonce_record = await db.get_wallet_nonce(request.wallet_address, request.nonce)
    if not nonce_record:
        raise HTTPException(status_code=400, detail="Invalid or expired nonce")

    if nonce_record.get("expires_at") < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Nonce expired")

    message = _build_wallet_message(
        request.wallet_address,
        nonce_record["nonce"],
        nonce_record.get("origin"),
    )

    try:
        public_key = Ed25519PublicKey.from_public_bytes(base58.b58decode(request.wallet_address))
        public_key.verify(base58.b58decode(request.signature), message.encode("utf-8"))
    except (InvalidSignature, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Signature verification failed") from exc

    await db.mark_wallet_nonce_used(nonce_record["id"])

    user = await db.get_user_by_wallet(request.wallet_address)
    if not user:
        user = await db.create_user(email=request.email, wallet_address=request.wallet_address)
    elif request.email and not user.get("email"):
        await db.update_user(user["id"], {"email": request.email})
        user = await db.get_user(user["id"])

    session_id = f"sess_{uuid.uuid4().hex}"
    refresh_token, refresh_expires_at = create_refresh_token(user["id"], session_id)
    await db.create_session(
        user_id=user["id"],
        refresh_token_hash=hash_token(refresh_token),
        expires_at=refresh_expires_at,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        session_id=session_id,
    )
    access_token, access_expires_at = create_access_token(user["id"], session_id, user["role"])

    _set_auth_cookies(response, access_token, refresh_token, access_expires_at, refresh_expires_at)

    return {
        "user": {
            "id": user["id"],
            "email": user.get("email"),
            "wallet_address": user.get("wallet_address"),
            "role": user.get("role"),
        }
    }


@router.post("/magic-link")
async def magic_link(request: MagicLinkRequest, req: Request):
    ip = _client_ip(req)
    allowed, retry_after = _magic_link_limiter.check_rate_limit(f"magic:{ip}")
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests", headers={"Retry-After": str(retry_after)})
    user = await db.get_user_by_email(request.email)
    if not user:
        user = await db.create_user(email=request.email, wallet_address=None)

    token = generate_token(24)
    expires_at = datetime.utcnow() + timedelta(minutes=MAGIC_LINK_TTL_MINUTES)
    await db.create_magic_link(user["id"], hash_token(token), expires_at)

    verification_url = f"{FRONTEND_URL}/auth?token={token}"
    email_client.send_magic_link(request.email, verification_url)

    response = {"success": True}
    if os.getenv("ENVIRONMENT", "development").lower() != "production":
        response["verification_url"] = verification_url

    return response


@router.post("/magic-link/verify")
async def magic_link_verify(request: MagicLinkVerifyRequest, response: Response, req: Request):
    token_hash = hash_token(request.token)
    link = await db.get_magic_link(token_hash)
    if not link:
        raise HTTPException(status_code=400, detail="Invalid or expired link")

    if link.get("expires_at") < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Link expired")

    await db.mark_magic_link_used(link["id"])

    user = await db.get_user(link["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session_id = f"sess_{uuid.uuid4().hex}"
    refresh_token, refresh_expires_at = create_refresh_token(user["id"], session_id)
    await db.create_session(
        user_id=user["id"],
        refresh_token_hash=hash_token(refresh_token),
        expires_at=refresh_expires_at,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        session_id=session_id,
    )
    access_token, access_expires_at = create_access_token(user["id"], session_id, user["role"])
    _set_auth_cookies(response, access_token, refresh_token, access_expires_at, refresh_expires_at)

    return {
        "user": {
            "id": user["id"],
            "email": user.get("email"),
            "wallet_address": user.get("wallet_address"),
            "role": user.get("role"),
        }
    }


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_token(refresh_cookie, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    session_id = payload.get("sid")
    user_id = payload.get("sub")
    if not session_id or not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    session = await db.get_session(session_id)
    if not session or session.get("revoked_at"):
        raise HTTPException(status_code=401, detail="Session revoked")

    if session.get("expires_at") < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Session expired")

    if session.get("refresh_token_hash") != hash_token(refresh_cookie):
        await db.revoke_session(session_id)
        raise HTTPException(status_code=401, detail="Token reuse detected")

    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_refresh_token, refresh_expires_at = create_refresh_token(user_id, session_id)
    await db.update_session_refresh(session_id, hash_token(new_refresh_token), refresh_expires_at)

    access_token, access_expires_at = create_access_token(user_id, session_id, user.get("role", "merchant"))
    _set_auth_cookies(response, access_token, new_refresh_token, access_expires_at, refresh_expires_at)

    return {"success": True}


@router.post("/logout")
async def logout(request: Request, response: Response):
    refresh_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_cookie:
        try:
            payload = decode_token(refresh_cookie, expected_type="refresh")
            session_id = payload.get("sid")
            if session_id:
                await db.revoke_session(session_id)
        except TokenError:
            pass

    _clear_auth_cookies(response)
    return {"success": True}


@router.get("/me")
async def me(request: Request):
    access_cookie = request.cookies.get(ACCESS_COOKIE_NAME)
    if not access_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(access_cookie, expected_type="access")
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    user = await db.get_user(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user["id"],
        "email": user.get("email"),
        "wallet_address": user.get("wallet_address"),
        "role": user.get("role"),
    }
