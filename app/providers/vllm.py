import httpx
from app.config import settings


async def list_models():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{settings.vllm_base_url}/models")
        r.raise_for_status()
        return r.json()


async def chat(payload, stream: bool = False):
    async with httpx.AsyncClient(timeout=None) as client:
        if stream:
            return await client.stream(
                "POST", f"{settings.vllm_base_url}/chat/completions", json=payload
            )
        r = await client.post(
            f"{settings.vllm_base_url}/chat/completions", json=payload
        )
        r.raise_for_status()
        return r.json()


