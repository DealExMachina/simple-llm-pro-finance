"""Simple rate limiting middleware for demo/single user scenarios."""

import time
from collections import defaultdict, deque
from typing import Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.utils.constants import (
    RATE_LIMIT_REQUESTS_PER_MINUTE,
    RATE_LIMIT_REQUESTS_PER_HOUR,
)


class SimpleRateLimiter:
    """Simple in-memory rate limiter for demo use (not for production with multiple servers)."""
    
    def __init__(self):
        # Track requests by IP address
        self._requests_by_ip: dict[str, deque] = defaultdict(lambda: deque())
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # Clean up old entries every 5 minutes
    
    def _cleanup_old_entries(self):
        """Remove old request timestamps to prevent memory growth."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff_minute = current_time - 60
        cutoff_hour = current_time - 3600
        
        for ip in list(self._requests_by_ip.keys()):
            requests = self._requests_by_ip[ip]
            # Keep only requests from last hour
            while requests and requests[0] < cutoff_hour:
                requests.popleft()
            
            # Remove IP if no recent requests
            if not requests:
                del self._requests_by_ip[ip]
        
        self._last_cleanup = current_time
    
    def check_rate_limit(self, ip: str) -> tuple[bool, str | None]:
        """
        Check if request should be allowed.
        
        Returns:
            (allowed, error_message)
        """
        self._cleanup_old_entries()
        
        current_time = time.time()
        requests = self._requests_by_ip[ip]
        
        # Remove requests older than 1 hour
        cutoff_hour = current_time - 3600
        while requests and requests[0] < cutoff_hour:
            requests.popleft()
        
        # Check hourly limit
        if len(requests) >= RATE_LIMIT_REQUESTS_PER_HOUR:
            return False, f"Rate limit exceeded: {RATE_LIMIT_REQUESTS_PER_HOUR} requests per hour"
        
        # Check per-minute limit (last 60 seconds)
        cutoff_minute = current_time - 60
        recent_requests = [r for r in requests if r >= cutoff_minute]
        if len(recent_requests) >= RATE_LIMIT_REQUESTS_PER_MINUTE:
            return False, f"Rate limit exceeded: {RATE_LIMIT_REQUESTS_PER_MINUTE} requests per minute"
        
        # Record this request
        requests.append(current_time)
        return True, None


# Global rate limiter instance
_rate_limiter = SimpleRateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable):
    """Rate limiting middleware."""
    # Skip rate limiting for public endpoints
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json", "/v1/stats"]
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    allowed, error_msg = _rate_limiter.check_rate_limit(client_ip)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "message": error_msg,
                    "type": "rate_limit_error"
                }
            },
            headers={
                "Retry-After": "60",  # Suggest retrying after 60 seconds
                "X-RateLimit-Limit-Minute": str(RATE_LIMIT_REQUESTS_PER_MINUTE),
                "X-RateLimit-Limit-Hour": str(RATE_LIMIT_REQUESTS_PER_HOUR),
            }
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    requests = _rate_limiter._requests_by_ip[client_ip]
    current_time = time.time()
    recent_minute = [r for r in requests if r >= current_time - 60]
    recent_hour = [r for r in requests if r >= current_time - 3600]
    
    response.headers["X-RateLimit-Limit-Minute"] = str(RATE_LIMIT_REQUESTS_PER_MINUTE)
    response.headers["X-RateLimit-Limit-Hour"] = str(RATE_LIMIT_REQUESTS_PER_HOUR)
    response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, RATE_LIMIT_REQUESTS_PER_MINUTE - len(recent_minute)))
    response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, RATE_LIMIT_REQUESTS_PER_HOUR - len(recent_hour)))
    
    return response

