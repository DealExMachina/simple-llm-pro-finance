from typing import Any, Dict
from app.providers.vllm import VLLMProvider

# Initialize the provider
provider = VLLMProvider()

async def list_models() -> Dict[str, Any]:
    return await provider.list_models()

async def chat(payload: Dict[str, Any], stream: bool = False):
    return await provider.chat(payload, stream=stream)


