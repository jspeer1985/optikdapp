"""
Rate Limiting Middleware for FastAPI
Prevents API abuse and DDoS attacks
"""

import time
import logging
from typing import Dict, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import asyncio
from utils.security import decode_token, TokenError
import os

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )


class RateLimiter:
    """
    Token bucket rate limiter with sliding window
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size

        # Storage for request timestamps
        self._minute_buckets: Dict[str, list] = defaultdict(list)
        self._hour_buckets: Dict[str, list] = defaultdict(list)

        # Cleanup task
        self._cleanup_task = None

    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks"""
        now = time.time()
        cutoff_minute = now - 60
        cutoff_hour = now - 3600

        # Clean minute buckets
        for key in list(self._minute_buckets.keys()):
            self._minute_buckets[key] = [
                ts for ts in self._minute_buckets[key] if ts > cutoff_minute
            ]
            if not self._minute_buckets[key]:
                del self._minute_buckets[key]

        # Clean hour buckets
        for key in list(self._hour_buckets.keys()):
            self._hour_buckets[key] = [
                ts for ts in self._hour_buckets[key] if ts > cutoff_hour
            ]
            if not self._hour_buckets[key]:
                del self._hour_buckets[key]

    async def _periodic_cleanup(self):
        """Run cleanup every 5 minutes"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            self._cleanup_old_entries()

    def check_rate_limit(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request should be allowed

        Args:
            identifier: Unique identifier (IP address, user ID, API key)

        Returns:
            Tuple of (allowed: bool, retry_after: Optional[int])
        """
        now = time.time()
        cutoff_minute = now - 60
        cutoff_hour = now - 3600

        # Get recent requests
        minute_requests = [
            ts for ts in self._minute_buckets[identifier] if ts > cutoff_minute
        ]
        hour_requests = [
            ts for ts in self._hour_buckets[identifier] if ts > cutoff_hour
        ]

        # Check limits
        if len(minute_requests) >= self.requests_per_minute:
            retry_after = int(60 - (now - minute_requests[0]))
            logger.warning(
                f"Rate limit exceeded (per minute) for {identifier}: "
                f"{len(minute_requests)} requests"
            )
            return False, retry_after

        if len(hour_requests) >= self.requests_per_hour:
            retry_after = int(3600 - (now - hour_requests[0]))
            logger.warning(
                f"Rate limit exceeded (per hour) for {identifier}: "
                f"{len(hour_requests)} requests"
            )
            return False, retry_after

        # Allow request and record it
        self._minute_buckets[identifier].append(now)
        self._hour_buckets[identifier].append(now)

        return True, None

    def get_rate_limit_info(self, identifier: str) -> Dict[str, int]:
        """
        Get current rate limit status

        Args:
            identifier: Unique identifier

        Returns:
            Dictionary with rate limit info
        """
        now = time.time()
        cutoff_minute = now - 60
        cutoff_hour = now - 3600

        minute_requests = len([
            ts for ts in self._minute_buckets[identifier] if ts > cutoff_minute
        ])
        hour_requests = len([
            ts for ts in self._hour_buckets[identifier] if ts > cutoff_hour
        ])

        return {
            "limit_per_minute": self.requests_per_minute,
            "remaining_per_minute": max(0, self.requests_per_minute - minute_requests),
            "limit_per_hour": self.requests_per_hour,
            "remaining_per_hour": max(0, self.requests_per_hour - hour_requests),
            "reset_minute": int(60 - (now - self._minute_buckets[identifier][0])) if minute_requests > 0 else 60,
            "reset_hour": int(3600 - (now - self._hour_buckets[identifier][0])) if hour_requests > 0 else 3600,
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
        exclude_paths: list = None
    ):
        super().__init__(app)
        self.limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            burst_size=burst_size
        )
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/"]

    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting

        Priority:
        1. API key from header
        2. User ID from auth
        3. Client IP address
        """
        # Try Bearer token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_token(token, expected_type="access")
                user_id = payload.get("sub")
                if user_id:
                    return f"user:{user_id}"
            except TokenError:
                pass

        cookie_name = os.getenv("ACCESS_COOKIE_NAME", "optik_access")
        cookie_token = request.cookies.get(cookie_name)
        if cookie_token:
            try:
                payload = decode_token(cookie_token, expected_type="access")
                user_id = payload.get("sub")
                if user_id:
                    return f"user:{user_id}"
            except TokenError:
                pass

        # Try to get API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Try to get authenticated user
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # Fallback to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP from X-Forwarded-For
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process each request through rate limiter
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Get identifier
        identifier = self._get_identifier(request)

        # Check rate limit
        allowed, retry_after = self.limiter.check_rate_limit(identifier)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Get rate limit info for response headers
        rate_info = self.limiter.get_rate_limit_info(identifier)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit-Minute"] = str(rate_info["limit_per_minute"])
        response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["remaining_per_minute"])
        response.headers["X-RateLimit-Limit-Hour"] = str(rate_info["limit_per_hour"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(rate_info["remaining_per_hour"])

        return response


# Alternative: Decorator-based rate limiting for specific endpoints
def rate_limit(requests_per_minute: int = 10):
    """
    Decorator for rate limiting specific endpoints

    Usage:
        @app.get("/api/expensive-operation")
        @rate_limit(requests_per_minute=5)
        async def expensive_operation():
            pass
    """
    limiter = RateLimiter(requests_per_minute=requests_per_minute)

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get identifier
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                identifier = f"ip:{forwarded_for.split(',')[0].strip()}"
            else:
                identifier = f"ip:{request.client.host if request.client else 'unknown'}"

            # Check rate limit
            allowed, retry_after = limiter.check_rate_limit(identifier)
            if not allowed:
                raise RateLimitExceeded(retry_after=retry_after)

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# Redis-backed rate limiter for distributed systems
class RedisRateLimiter:
    """
    Redis-backed rate limiter for distributed systems
    Use this in production with multiple servers
    """

    def __init__(self, redis_client, requests_per_minute: int = 60):
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute

    async def check_rate_limit(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check rate limit using Redis

        Args:
            identifier: Unique identifier

        Returns:
            Tuple of (allowed: bool, retry_after: Optional[int])
        """
        key = f"rate_limit:{identifier}"
        now = int(time.time())
        minute_ago = now - 60

        try:
            # Use Redis sorted set to store timestamps
            pipe = self.redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, minute_ago)

            # Count requests in last minute
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Set expiry
            pipe.expire(key, 60)

            results = await pipe.execute()
            count = results[1]

            if count >= self.requests_per_minute:
                # Get oldest request timestamp
                oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(60 - (now - oldest[0][1]))
                    return False, retry_after

            return True, None

        except Exception as e:
            logger.error(f"Redis rate limiter error: {e}")
            # Fail open - allow request if Redis is down
            return True, None
