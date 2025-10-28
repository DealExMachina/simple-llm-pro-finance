import time
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from app.config import settings
from app.models.openai import ChatCompletionRequest
from app.services import chat_service


router = APIRouter()


@router.get("/models")
async def list_models():
    return await chat_service.list_models()


@router.post("/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    payload: Dict[str, Any] = {
        "model": body.model or settings.model,
        "messages": [m.model_dump() for m in body.messages],
        "temperature": body.temperature,
        **({"max_tokens": body.max_tokens} if body.max_tokens is not None else {}),
        "stream": body.stream or False,
    }

    if body.stream:
        upstream = await chat_service.chat(payload, stream=True)

        async def event_stream():
            async for line in upstream.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    yield f"{line}\n\n"
                else:
                    yield f"data: {line}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    data = await chat_service.chat(payload, stream=False)
    # Assume vLLM already returns OpenAI-compatible schema; pass through.
    # If needed, normalize here.
    return JSONResponse(content=data)


