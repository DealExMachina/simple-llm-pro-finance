from typing import Any, Dict

from app.providers import transformers_provider as provider


async def list_models() -> Dict[str, Any]:
    return await provider.list_models()


async def chat(payload: Dict[str, Any], stream: bool = False):
    return await provider.chat(payload, stream=stream)


