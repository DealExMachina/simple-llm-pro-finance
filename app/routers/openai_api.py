from typing import Any, Dict
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from app.config import settings
from app.models.openai import ChatCompletionRequest
from app.services import chat_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models")
async def list_models():
    """List available models (OpenAI-compatible endpoint)"""
    return await chat_service.list_models()


@router.post("/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    """Chat completions endpoint (OpenAI-compatible)"""
    try:
        # Build payload with all supported parameters
        payload: Dict[str, Any] = {
            "model": body.model or settings.model,
            "messages": [m.model_dump() for m in body.messages],
            "temperature": body.temperature or 0.7,
            "top_p": body.top_p or 1.0,
            "stream": body.stream or False,
        }
        
        # Add optional max_tokens if provided
        if body.max_tokens is not None:
            payload["max_tokens"] = body.max_tokens
        
        logger.info(f"Chat completion request: model={payload['model']}, messages={len(payload['messages'])}, stream={payload['stream']}")

        if body.stream:
            stream = await chat_service.chat(payload, stream=True)
            # stream is already an AsyncIterator[str] with SSE-formatted chunks
            return StreamingResponse(stream, media_type="text/event-stream")

        # Non-streaming response
        data = await chat_service.chat(payload, stream=False)
        return JSONResponse(content=data)
        
    except Exception as e:
        logger.error(f"Error in chat completions endpoint: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "type": "internal_error"}}
        )


