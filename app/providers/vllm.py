import os
from typing import Dict, Any, AsyncIterator
from vllm import LLM, SamplingParams
from vllm.entrypoints.openai.api_server import build_async_engine_client
import asyncio

# Model configuration
model_name = "DragonLLM/LLM-Pro-Finance-Small"
llm_engine = None

def initialize_vllm():
    """Initialize vLLM engine with the model"""
    global llm_engine
    
    if llm_engine is None:
        print(f"Initializing vLLM with model: {model_name}")
        
        # Get HF token from environment
        hf_token = os.getenv("HF_TOKEN_LC")
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
        
        try:
            # Initialize vLLM engine
            llm_engine = LLM(
                model=model_name,
                trust_remote_code=True,
                dtype="float16",
                max_model_len=4096,
                gpu_memory_utilization=0.9,
                tensor_parallel_size=1,  # L40 has 1 GPU
                download_dir="/tmp/huggingface",
            )
            print(f"vLLM engine initialized successfully!")
        except Exception as e:
            print(f"Error initializing vLLM: {e}")
            raise


class VLLMProvider:
    def __init__(self):
        # Don't initialize at import time
        pass
    
    async def list_models(self) -> Dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {
                    "id": model_name,
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "DragonLLM",
                    "permission": [],
                    "root": model_name,
                    "parent": None,
                }
            ]
        }
    
    async def chat(self, payload: Dict[str, Any], stream: bool = False) -> Dict[str, Any]:
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Initialize vLLM on first use
            if llm_engine is None:
                logger.info("vLLM engine not initialized, initializing now...")
                initialize_vllm()
                logger.info("vLLM engine initialized successfully")
            
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", 0.7)
            max_tokens = payload.get("max_tokens", 1000)
            top_p = payload.get("top_p", 1.0)
            
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)
            logger.info(f"Generating response for prompt: {prompt[:100]}...")
            
            # Set up sampling parameters
            sampling_params = SamplingParams(
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            
            # Generate response using vLLM
            outputs = llm_engine.generate([prompt], sampling_params)
            
            # Extract the generated text
            generated_text = outputs[0].outputs[0].text
            logger.info(f"Generated text: {generated_text[:100]}...")
            
            # Build OpenAI-compatible response
            return {
                "id": f"chatcmpl-{os.urandom(12).hex()}",
                "object": "chat.completion",
                "created": int(asyncio.get_event_loop().time()),
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": generated_text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(outputs[0].prompt_token_ids),
                    "completion_tokens": len(outputs[0].outputs[0].token_ids),
                    "total_tokens": len(outputs[0].prompt_token_ids) + len(outputs[0].outputs[0].token_ids)
                }
            }
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
            raise
    
    def _messages_to_prompt(self, messages: list) -> str:
        """Convert OpenAI messages format to prompt"""
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        prompt += "Assistant: "
        return prompt
