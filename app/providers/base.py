"""Base protocol for LLM providers."""

from typing import Any, Dict, Protocol


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers.
    
    Any class implementing this protocol must provide async methods
    for listing models and generating chat completions.
    """
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models.
        
        Returns:
            Dictionary containing model information.
        """
        ...
    
    async def chat(self, payload: Dict[str, Any], stream: bool = False) -> Any:
        """Generate chat completion.
        
        Args:
            payload: Request payload containing messages and parameters
            stream: Whether to stream the response
            
        Returns:
            Chat completion response (varies by implementation)
        """
        ...


