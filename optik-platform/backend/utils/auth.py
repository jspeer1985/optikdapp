import os
from datetime import datetime
from fastapi import Security, HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from utils.database import db
from utils.security import decode_token, TokenError, hash_token

API_KEY_NAME = "X-Optik-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

bearer_scheme = HTTPBearer(auto_error=False)
ACCESS_COOKIE_NAME = os.getenv("ACCESS_COOKIE_NAME", "optik_access")


class User(BaseModel):
    id: str
    email: str | None = None
    wallet_address: str | None = None
    role: str = "merchant"
    status: str = "active"


def _unauthorized(message: str = "Could not validate credentials"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing API key")

    key_hash = hash_token(api_key)
    key = await db.get_api_key(key_hash)
    if not key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    return key


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    token = None
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials

    if not token:
        token = request.cookies.get(ACCESS_COOKIE_NAME)

    if not token:
        _unauthorized()

    try:
        payload = decode_token(token, expected_type="access")
    except TokenError:
        _unauthorized()

    session_id = payload.get("sid")
    user_id = payload.get("sub")

    if not session_id or not user_id:
        _unauthorized()

    session = await db.get_session(session_id)
    if not session:
        _unauthorized()

    if session.get("revoked_at") or session.get("expires_at") < datetime.utcnow():
        _unauthorized("Session expired")

    user_data = await db.get_user(user_id)
    if not user_data or user_data.get("status") != "active":
        _unauthorized()

    request.state.user = user_data
    return User(**user_data)


async def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User | None:
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None


def require_roles(*roles: str):
    async def _role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _role_checker
