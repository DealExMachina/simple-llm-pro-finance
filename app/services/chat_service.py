"""Chat service layer providing abstraction over the provider."""
from typing import Any, Dict, Union, AsyncIterator

from app.providers import transformers_provider as provider


async def list_models() -> Dict[str, Any]:
    """
    List available models.
    
    Returns:
        Dictionary containing model list in OpenAI-compatible format
    """
    return await provider.list_models()


async def chat(
    payload: Dict[str, Any], 
    stream: bool = False
) -> Union[Dict[str, Any], AsyncIterator[str]]:
    """
    Process chat completion request.
    
    Args:
        payload: Request payload containing messages and generation parameters
        stream: Whether to stream the response
    
    Returns:
        Response dictionary or async iterator for streaming
    """
    return await provider.chat(payload, stream=stream)


