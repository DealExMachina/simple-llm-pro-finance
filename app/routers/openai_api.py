from typing import Any, Dict
import logging

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse

from app.config import settings
from app.models.openai import ChatCompletionRequest
from app.services import chat_service
from app.providers.transformers_provider import initialize_model

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models")
async def list_models():
    """List available models (OpenAI-compatible endpoint)"""
    return await chat_service.list_models()


@router.post("/models/reload")
async def reload_model(force: bool = Query(False, description="Force reload from Hugging Face Hub")):
    """
    Reload the model from cache or Hugging Face Hub.
    
    Args:
        force: If True, force reload from Hugging Face Hub (bypass cache)
    
    Returns:
        Status of reload operation
    """
    try:
        logger.info(f"Model reload requested (force={force})")
        initialize_model(force_reload=force)
        return JSONResponse(content={
            "status": "success",
            "message": f"Model reloaded successfully (force={force})",
            "from_cache": not force,
        })
    except Exception as e:
        logger.error(f"Error reloading model: {str(e)}", exc_info=True)
        # Sanitize error message for client
        error_msg = str(e)
        # Only expose safe error messages
        if "401" in error_msg or "Unauthorized" in error_msg:
            error_msg = "Authentication failed. Check your Hugging Face token."
        elif "timeout" in error_msg.lower():
            error_msg = "Model initialization timed out. Please try again."
        else:
            error_msg = "Failed to reload model. Check logs for details."
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error_msg,
            }
        )


@router.post("/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    """Chat completions endpoint (OpenAI-compatible)"""
    try:
        # Validate messages list is not empty
        if not body.messages:
            return JSONResponse(
                status_code=400,
                content={"error": {"message": "messages list cannot be empty", "type": "invalid_request_error"}}
            )
        
        # Build payload with all supported parameters
        payload: Dict[str, Any] = {
            "model": body.model or settings.model,
            "messages": [m.model_dump() for m in body.messages],
            "temperature": body.temperature or 0.7,
            "top_p": body.top_p or 1.0,
            "stream": body.stream or False,
        }
        
        # ✅ Add tools and tool_choice if provided
        if body.tools:
            payload["tools"] = [t.model_dump() for t in body.tools]
        if body.tool_choice:
            payload["tool_choice"] = body.tool_choice
        
        # Validate temperature range
        if payload["temperature"] < 0 or payload["temperature"] > 2:
            return JSONResponse(
                status_code=400,
                content={"error": {"message": "temperature must be between 0 and 2", "type": "invalid_request_error"}}
            )
        
        # Add optional max_tokens if provided
        if body.max_tokens is not None:
            if body.max_tokens < 1:
                return JSONResponse(
                    status_code=400,
                    content={"error": {"message": "max_tokens must be at least 1", "type": "invalid_request_error"}}
                )
            payload["max_tokens"] = body.max_tokens
        
        logger.info(f"Chat completion request: model={payload['model']}, messages={len(payload['messages'])}, stream={payload['stream']}")

        if body.stream:
            stream = await chat_service.chat(payload, stream=True)
            # stream is already an AsyncIterator[str] with SSE-formatted chunks
            return StreamingResponse(stream, media_type="text/event-stream")

        # Non-streaming response
        data = await chat_service.chat(payload, stream=False)
        return JSONResponse(content=data)
        
    except ValueError as e:
        # Validation errors - safe to expose
        logger.warning(f"Validation error in chat completions: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": {"message": str(e), "type": "invalid_request_error"}}
        )
    except Exception as e:
        # Internal errors - sanitize message
        logger.error(f"Error in chat completions endpoint: {str(e)}", exc_info=True)
        # Don't expose internal error details to client
        return JSONResponse(
            status_code=500,
            content={"error": {"message": "An internal error occurred. Please try again later.", "type": "internal_error"}}
        )


