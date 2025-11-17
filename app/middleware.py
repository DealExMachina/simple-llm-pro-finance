from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings


async def api_key_guard(request: Request, call_next):
    # Public endpoints that don't require authentication
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json", "/v1/stats"]
    
    # Skip auth for public endpoints
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Skip auth if no API key is configured
    if not settings.service_api_key:
        return await call_next(request)
    
    # Check API key
    key = request.headers.get("x-api-key") or request.headers.get("authorization")
    if key and key.replace("Bearer ", "").strip() == settings.service_api_key:
        return await call_next(request)
    
    return JSONResponse({"error": "unauthorized"}, status_code=401)


