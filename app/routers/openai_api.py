from typing import Any, Dict
import logging

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse

from app.config import settings
from app.models.openai import ChatCompletionRequest
from app.providers.transformers_provider import initialize_model, chat, list_models
from app.langfuse_config import get_langfuse_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models")
async def list_models_endpoint():
    """List available models (OpenAI-compatible endpoint)"""
    return await list_models()


@router.get("/stats")
async def get_stats():
    """Get API usage statistics.
    
    Returns:
        Dictionary containing request counts, token usage, and performance metrics.
    """
    try:
        from app.utils.stats import get_stats_tracker
        return get_stats_tracker().get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to retrieve statistics. Check logs for details.",
            }
        )


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
            # Handle tool_choice: if it's a dict, pass as-is; if it's a string, pass as-is
            if isinstance(body.tool_choice, dict):
                payload["tool_choice"] = body.tool_choice
            else:
                payload["tool_choice"] = body.tool_choice
        # ✅ Add response_format if provided (for structured outputs)
        if body.response_format:
            if isinstance(body.response_format, dict):
                payload["response_format"] = body.response_format
            else:
                payload["response_format"] = body.response_format.model_dump()
        
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

        # Langfuse tracing
        langfuse = get_langfuse_client()
        trace = None
        span = None
        
        if langfuse:
            try:
                trace = langfuse.trace(
                    name="chat_completion",
                    metadata={
                        "model": payload['model'],
                        "stream": payload['stream'],
                        "has_tools": bool(body.tools),
                        "temperature": payload.get('temperature'),
                        "max_tokens": payload.get('max_tokens'),
                    },
                )
                span = trace.span(
                    name="llm_generation",
                    metadata={
                        "messages_count": len(payload['messages']),
                        "tools_count": len(body.tools) if body.tools else 0,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to create Langfuse trace: {e}")

        if body.stream:
            stream = await chat(payload, stream=True)
            # stream is already an AsyncIterator[str] with SSE-formatted chunks
            # Note: Streaming responses are harder to trace, so we skip detailed tracing for now
            if span:
                try:
                    span.end(output={"streaming": True})
                except Exception:
                    pass
            return StreamingResponse(stream, media_type="text/event-stream")

        # Non-streaming response
        data = await chat(payload, stream=False)
        
        # Update Langfuse trace with results
        if trace and span:
            try:
                # Extract token usage and other metrics from response
                usage = data.get("usage", {})
                choices = data.get("choices", [])
                first_choice = choices[0] if choices else {}
                message = first_choice.get("message", {})
                
                span.end(
                    output={
                        "content": message.get("content", "")[:1000] if message.get("content") else None,
                        "role": message.get("role"),
                        "tool_calls": message.get("tool_calls"),
                        "finish_reason": first_choice.get("finish_reason"),
                    },
                    metadata={
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                )
                
                trace.update(
                    output={
                        "success": True,
                        "choices_count": len(choices),
                    },
                    metadata={
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to update Langfuse trace: {e}")
        
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


