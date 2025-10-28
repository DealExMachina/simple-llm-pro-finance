import os
from typing import Dict, Any, AsyncIterator
from vllm import LLM, SamplingParams
from vllm.entrypoints.openai.api_server import build_async_engine_client
import asyncio
from huggingface_hub import login

# Model configuration - optimized for 8B Qwen3 on L4
model_name = "DragonLLM/qwen3-8b-fin-v1.0"
llm_engine = None

def initialize_vllm():
    """Initialize vLLM engine with the model"""
    global llm_engine
    
    if llm_engine is None:
        print(f"Initializing vLLM with model: {model_name}")
        
        # Get HF token from environment (Hugging Face Space secret)
        # Try HF_TOKEN_LC2 first (for DragonLLM access), then fall back to HF_TOKEN_LC
        hf_token = os.getenv("HF_TOKEN_LC2") or os.getenv("HF_TOKEN_LC")
        if hf_token:
            token_source = "HF_TOKEN_LC2" if os.getenv("HF_TOKEN_LC2") else "HF_TOKEN_LC"
            print(f"✅ {token_source} found (length: {len(hf_token)})")
            # Properly authenticate with Hugging Face Hub
            try:
                login(token=hf_token, add_to_git_credential=False)
                print("✅ Successfully authenticated with Hugging Face Hub")
            except Exception as e:
                print(f"⚠️  Warning: Failed to authenticate with HF Hub: {e}")
            # Also set environment variables as fallback
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
        else:
            print("⚠️  WARNING: Neither HF_TOKEN_LC2 nor HF_TOKEN_LC found in environment!")
            print("Available env vars:", list(os.environ.keys()))
        
        try:
            # Initialize vLLM engine with explicit token
            print(f"Attempting to load model: {model_name}")
            print(f"Model type: Qwen3 8B (bfloat16) - Optimized for L4")
            print(f"Download directory: /tmp/huggingface")
            print(f"Trust remote code: True")
            print(f"L4 GPU: 24GB VRAM available")
            print(f"Mode: Eager mode (CUDA graphs disabled for L4)")
            print(f"GPU memory utilization: 0.70 (conservative to avoid multi-process OOM)")
            print(f"Engine: Legacy (v0) - single-process, more stable (VLLM_USE_V1=0)")
            
            llm_engine = LLM(
                model=model_name,
                trust_remote_code=True,
                dtype="bfloat16",  # Use bfloat16 for Qwen3 (required)
                max_model_len=4096,  # Reduced for L4 KV cache constraints
                gpu_memory_utilization=0.85,  # Can use more with stable v0 engine
                tensor_parallel_size=1,  # Single L4 GPU
                download_dir="/tmp/huggingface",
                tokenizer_mode="auto",
                # Disable torch.compile on L4 due to memory constraints
                enforce_eager=True,  # Use eager mode (no CUDA graphs/compilation)
                # Let vLLM handle compilation and fallback gracefully
                disable_log_stats=False,  # Enable logging for debugging
            )
            print(f"✅ vLLM engine initialized successfully with {model_name}!")
        except Exception as e:
            print(f"❌ Error initializing vLLM: {e}")
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
