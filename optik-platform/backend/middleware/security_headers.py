"""
Security Headers Middleware for FastAPI
Implements security best practices through HTTP headers
"""

import logging
from typing import Callable
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


def add_security_headers_middleware(app: FastAPI, environment: str = "production") -> None:
    """
    Add security headers middleware to FastAPI application
    
    Implements OWASP security headers best practices
    """
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)

        # Content Security Policy (CSP) — API only serves JSON, no inline scripts needed
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'none'"
        )

        # HTTP Strict-Transport-Security (HSTS) - force HTTPS
        if environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy - limit referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (Feature Policy) - restrict browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Cross-Domain Policy
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Prevent MIME type detection
        response.headers["X-Content-Security-Policy"] = response.headers["Content-Security-Policy"]

        # Remove server header (don't reveal server info)
        response.headers.pop("Server", None)
        
        return response

    logger.info("✅ Security headers middleware installed")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses

    Implements OWASP security headers best practices:
    - Content Security Policy (CSP)
    - X-Frame-Options (Clickjacking protection)
    - X-Content-Type-Options (MIME sniffing protection)
    - Strict-Transport-Security (HSTS)
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """

    def __init__(
        self,
        app: ASGIApp,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        enable_csp: bool = True,
        csp_directives: dict = None,
        environment: str = "production"
    ):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.enable_csp = enable_csp
        self.environment = environment

        # Default CSP directives — API only, no HTML served, so lockdown completely
        self.csp_directives = csp_directives or {
            "default-src": ["'none'"],
            "frame-ancestors": ["'none'"],
            "form-action": ["'none'"],
        }

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header value"""
        directives = []
        for directive, sources in self.csp_directives.items():
            sources_str = " ".join(sources)
            directives.append(f"{directive} {sources_str}")
        return "; ".join(directives)

    async def dispatch(self, request: Request, call_next: Callable):
        """Add security headers to response"""
        response = await call_next(request)

        # Content Security Policy
        if self.enable_csp:
            csp = self._build_csp_header()
            response.headers["Content-Security-Policy"] = csp
            # Also set report-only for monitoring in development
            if self.environment == "development":
                response.headers["Content-Security-Policy-Report-Only"] = csp

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection (legacy, but still useful for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS - Force HTTPS (only in production)
        if self.enable_hsts and self.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )

        # Referrer Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(self)"
        )

        # Cross-Origin policies - LOOSENED for development
        if self.environment == "production":
            response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        else:
            # In development, these often cause CORS heartaches
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
            response.headers["Cross-Origin-Opener-Policy"] = "unsafe-none"

        # Prevent caching of sensitive data
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        # Remove server identification headers
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with security checks

    Additional security over FastAPI's built-in CORS:
    - Validates Origin header against whitelist
    - Logs suspicious CORS attempts
    - Prevents CORS bypass attacks
    """

    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: list = None,
        allow_credentials: bool = True,
        max_age: int = 600
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or [
            "http://localhost:3000",
            "http://localhost:3003",
            "https://optik-platform.com"
        ]
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is in allowed list"""
        if not origin:
            return False

        # Exact match
        if origin in self.allowed_origins:
            return True

        # Pattern match (e.g., *.optik-platform.com)
        for allowed in self.allowed_origins:
            if allowed.startswith("*."):
                domain = allowed[2:]
                if origin.endswith(domain):
                    return True

        return False

    async def dispatch(self, request: Request, call_next: Callable):
        """Handle CORS with security checks"""
        origin = request.headers.get("origin")

        # Log suspicious CORS attempts
        if origin and not self._is_origin_allowed(origin):
            logger.warning(
                f"CORS request from unauthorized origin: {origin} "
                f"to {request.url.path}"
            )

        response = await call_next(request)

        # Only add CORS headers if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

            # Handle preflight requests
            if request.method == "OPTIONS":
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = (
                    "Content-Type, Authorization, X-API-Key, X-Request-ID"
                )
                response.headers["Access-Control-Max-Age"] = str(self.max_age)

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request for tracking and debugging
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        """Add request ID to request and response"""
        import uuid

        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Store in request state for access in route handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log security-relevant events and suspicious activity
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.suspicious_patterns = [
            "../",  # Path traversal
            "UNION SELECT",  # SQL injection
            "<script>",  # XSS
            "eval(",  # Code injection
            "exec(",  # Code injection
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        """Log security events"""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Check for suspicious patterns in URL and query params
        full_url = str(request.url)
        for pattern in self.suspicious_patterns:
            if pattern.lower() in full_url.lower():
                logger.warning(
                    f"Suspicious request from {client_ip}: "
                    f"Pattern '{pattern}' found in {request.method} {request.url.path}"
                )

        # Process request and measure time
        import time
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Log security events
        if response.status_code >= 400:
            logger.warning(
                f"{client_ip} - {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {duration:.3f}s"
            )
        elif duration > 5.0:
            # Log slow requests (potential DoS)
            logger.warning(
                f"Slow request from {client_ip}: "
                f"{request.method} {request.url.path} took {duration:.3f}s"
            )

        return response
