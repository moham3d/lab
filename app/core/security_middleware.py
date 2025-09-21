"""
Security middleware for production readiness
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from typing import Dict, Any
import re

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    def __init__(self, app: ASGIApp, csp_policy: str = None):
        super().__init__(app)
        self.csp_policy = csp_policy or self._get_default_csp()

    def _get_default_csp(self) -> str:
        """Get default Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy

        # HSTS (HTTP Strict Transport Security) - only for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]

        # Add request timing
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with structured format"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log incoming request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
            }
        )

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": self._get_client_ip(request),
            }
        )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to client host
        client = request.client
        return client.host if client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)

        # Clean old requests
        current_time = time.time()
        if client_ip in self.requests:
            self.requests[client_ip] = [
                timestamp for timestamp in self.requests[client_ip]
                if current_time - timestamp < 60
            ]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        client = request.client
        return client.host if client else "unknown"


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize input data to prevent injection attacks"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Patterns for potential injection attacks
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>.*?</iframe>',  # Iframes
            r'<object[^>]*>.*?</object>',  # Object tags
            r'<embed[^>]*>.*?</embed>',  # Embed tags
            r'union\s+select',  # SQL injection
            r';\s*drop\s+table',  # SQL injection
            r'--',  # SQL comments
            r'/\*.*?\*/',  # SQL comments
        ]

    async def dispatch(self, request: Request, call_next):
        # Check request body for suspicious content
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

            # Convert to string for pattern matching
            body_str = body.decode('utf-8', errors='ignore')

            for pattern in self.suspicious_patterns:
                if re.search(pattern, body_str, re.IGNORECASE):
                    logger.warning(
                        "Suspicious input detected",
                        extra={
                            "client_ip": self._get_client_ip(request),
                            "method": request.method,
                            "url": str(request.url),
                            "pattern": pattern
                        }
                    )
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid input detected"}
                    )

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        client = request.client
        return client.host if client else "unknown"