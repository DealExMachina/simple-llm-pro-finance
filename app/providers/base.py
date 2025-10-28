from typing import Protocol, Dict, Any


class LLMProvider(Protocol):
    async def list_models(self) -> Dict[str, Any]:
        ...

    async def chat(self, payload: Dict[str, Any], stream: bool = False) -> Any:
        ...


