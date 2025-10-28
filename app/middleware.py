from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings


async def api_key_guard(request: Request, call_next):
    if not settings.service_api_key:
        return await call_next(request)
    key = request.headers.get("x-api-key") or request.headers.get("authorization")
    if key and key.replace("Bearer ", "").strip() == settings.service_api_key:
        return await call_next(request)
    return JSONResponse({"error": "unauthorized"}, status_code=401)


