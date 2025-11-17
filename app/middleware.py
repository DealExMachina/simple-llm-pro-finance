import hmac
from fastapi import Request
from fastapi.responses import JSONResponse, Response
from typing import Callable, Awaitable, Union

from app.config import settings

# Public endpoints that don't require authentication
PUBLIC_PATHS = frozenset(["/", "/health", "/docs", "/redoc", "/openapi.json"])


async def api_key_guard(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Union[Response, JSONResponse]:
    """
    Middleware to protect API endpoints with optional API key authentication.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in the chain
    
    Returns:
        Response from next handler or 401 if unauthorized
    """
    # Skip auth for public endpoints
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    
    # Skip auth if no API key is configured
    if not settings.service_api_key:
        return await call_next(request)
    
    # Check API key from headers
    api_key = request.headers.get("x-api-key")
    if not api_key:
        # Also check Authorization header with Bearer token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "").strip()
    
    if api_key:
        # Use constant-time comparison to prevent timing attacks
        expected_key = str(settings.service_api_key) if settings.service_api_key else ""
        if hmac.compare_digest(str(api_key), expected_key):
            return await call_next(request)
    
    return JSONResponse(
        content={"error": {"message": "unauthorized", "type": "authentication_error"}},
        status_code=401
    )


