import os
import time
from typing import Dict, Any, AsyncIterator, Union
from vllm import LLM, SamplingParams
import asyncio
from huggingface_hub import login

# Model configuration - back to working DragonLLM model
model_name = "DragonLLM/qwen3-8b-fin-v1.0"
llm_engine = None

def initialize_vllm():
    """Initialize vLLM engine with the model
    
    Handles authentication with Hugging Face Hub for accessing DragonLLM models.
    Prioritizes HF_TOKEN_LC2 (DragonLLM access) over HF_TOKEN_LC.
    """
    global llm_engine
    
    if llm_engine is None:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Initializing vLLM with model: {model_name}")
        print(f"Initializing vLLM with model: {model_name}")
        
        # Get HF token from environment (Hugging Face Space secret)
        # Priority: HF_TOKEN_LC2 (for DragonLLM access) > HF_TOKEN_LC > HF_TOKEN
        hf_token = (
            os.getenv("HF_TOKEN_LC2") or 
            os.getenv("HF_TOKEN_LC") or 
            os.getenv("HF_TOKEN") or
            os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        
        if hf_token:
            # Determine token source for logging
            if os.getenv("HF_TOKEN_LC2"):
                token_source = "HF_TOKEN_LC2"
            elif os.getenv("HF_TOKEN_LC"):
                token_source = "HF_TOKEN_LC"
            elif os.getenv("HF_TOKEN"):
                token_source = "HF_TOKEN"
            else:
                token_source = "HUGGING_FACE_HUB_TOKEN"
            
            logger.info(f"✅ {token_source} found (length: {len(hf_token)})")
            print(f"✅ {token_source} found (length: {len(hf_token)})")
            
            # Authenticate with Hugging Face Hub
            try:
                login(token=hf_token, add_to_git_credential=False)
                logger.info("✅ Successfully authenticated with Hugging Face Hub")
                print("✅ Successfully authenticated with Hugging Face Hub")
            except Exception as e:
                logger.warning(f"⚠️  Warning: Failed to authenticate with HF Hub: {e}")
                print(f"⚠️  Warning: Failed to authenticate with HF Hub: {e}")
            
            # Set all possible environment variables that vLLM/huggingface_hub might check
            # This ensures compatibility across different versions
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
            # Some tools check for these variants too
            os.environ["HF_API_TOKEN"] = hf_token
            
            logger.info("✅ Hugging Face token environment variables set")
        else:
            logger.warning("⚠️  WARNING: No HF token found in environment!")
            logger.warning(f"   Checked: HF_TOKEN_LC2, HF_TOKEN_LC, HF_TOKEN, HUGGING_FACE_HUB_TOKEN")
            logger.warning(f"   Available env vars: {[k for k in os.environ.keys() if 'TOKEN' in k or 'HF' in k]}")
            print("⚠️  WARNING: No HF token found in environment!")
            print(f"   Checked: HF_TOKEN_LC2, HF_TOKEN_LC, HF_TOKEN, HUGGING_FACE_HUB_TOKEN")
            print(f"   Available env vars with 'TOKEN' or 'HF': {[k for k in os.environ.keys() if 'TOKEN' in k or 'HF' in k]}")
            print("   ⚠️  Model download may fail if DragonLLM/qwen3-8b-fin-v1.0 is gated!")
        
        try:
            # Initialize vLLM engine
            # Note: vLLM 0.6.5 will use HF_TOKEN from environment for model downloads
            logger.info(f"Attempting to load model: {model_name}")
            print(f"Attempting to load model: {model_name}")
            print(f"Model type: DragonLLM Qwen3 8B (bfloat16)")
            print(f"Download directory: /tmp/huggingface")
            print(f"Trust remote code: True")
            print(f"L4 GPU: 24GB VRAM available")
            
            # Try optimized mode first (CUDA graphs enabled)
            # Falls back to eager mode if CUDA graphs fail
            use_optimized = os.getenv("VLLM_USE_EAGER", "auto").lower()
            if use_optimized == "true":
                enforce_eager = True
                mode_desc = "Eager mode (forced)"
            elif use_optimized == "false":
                enforce_eager = False
                mode_desc = "Optimized mode (CUDA graphs enabled)"
            else:  # "auto" - try optimized, fallback to eager
                enforce_eager = False
                mode_desc = "Optimized mode (auto, fallback to eager if needed)"
            
            print(f"Mode: {mode_desc}")
            print(f"GPU memory utilization: 0.85")
            print(f"vLLM: v0.9.2 (Latest stable, improved Qwen3 support)")
            print(f"PyTorch: 2.5.0+ (CUDA 12.4 binary)")
            
            # Common initialization parameters
            init_params = {
                "model": model_name,
                "trust_remote_code": True,
                "dtype": "bfloat16",  # Use bfloat16 for Qwen3 (required)
                "max_model_len": 4096,  # Reduced for L4 KV cache constraints
                "gpu_memory_utilization": 0.85,  # Can use more with stable v0 engine
                "tensor_parallel_size": 1,  # Single L4 GPU
                "download_dir": "/tmp/huggingface",
                "tokenizer_mode": "auto",
                "disable_log_stats": False,  # Enable logging for debugging
            }
            
            # Try optimized mode first (unless explicitly disabled)
            if use_optimized == "auto" or use_optimized == "false":
                try:
                    print(f"🚀 Attempting optimized mode with CUDA graphs...")
                    logger.info("Attempting optimized mode (enforce_eager=False)")
                    init_params["enforce_eager"] = False
                    llm_engine = LLM(**init_params)
                    print(f"✅ vLLM engine initialized successfully in OPTIMIZED mode!")
                    logger.info("✅ vLLM engine initialized in optimized mode (CUDA graphs enabled)")
                except Exception as opt_error:
                    error_msg = str(opt_error).lower()
                    # Check if error is CUDA graph related
                    if "cuda graph" in error_msg or "graph" in error_msg or use_optimized == "auto":
                        logger.warning(f"⚠️  Optimized mode failed, falling back to eager mode: {opt_error}")
                        print(f"⚠️  Optimized mode failed: {opt_error}")
                        print(f"🔄 Falling back to eager mode for stability...")
                        init_params["enforce_eager"] = True
                        llm_engine = LLM(**init_params)
                        print(f"✅ vLLM engine initialized successfully in EAGER mode (fallback)")
                        logger.info("✅ vLLM engine initialized in eager mode (fallback after optimized mode failure)")
                    else:
                        # Re-raise if it's not a CUDA graph issue or if optimized is forced
                        raise
            else:
                # Eager mode explicitly requested
                print(f"⚙️  Using eager mode (explicitly requested)")
                logger.info("Using eager mode (VLLM_USE_EAGER=true)")
                init_params["enforce_eager"] = True
                llm_engine = LLM(**init_params)
                print(f"✅ vLLM engine initialized successfully in EAGER mode!")
                logger.info("✅ vLLM engine initialized in eager mode")
            
        except Exception as e:
            error_msg = f"❌ Error initializing vLLM: {e}"
            logger.error(error_msg, exc_info=True)
            print(error_msg)
            
            # Provide helpful error message for authentication issues
            if "401" in str(e) or "Unauthorized" in str(e) or "authentication" in str(e).lower():
                print("\n🔐 Authentication Error Detected!")
                print("   This usually means:")
                print("   1. HF_TOKEN_LC2 is missing or invalid")
                print("   2. You haven't accepted the model's terms on Hugging Face")
                print("   3. The token doesn't have access to DragonLLM models")
                print("\n   To fix:")
                print("   1. Visit: https://huggingface.co/DragonLLM/qwen3-8b-fin-v1.0")
                print("   2. Accept the model's terms of use")
                print("   3. Ensure HF_TOKEN_LC2 is set as a secret in your HF Space")
            
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
    
    async def chat(self, payload: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[str]]:
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
            
            # Handle streaming vs non-streaming
            if stream:
                return self._chat_stream(prompt, sampling_params, payload.get("model", model_name))
            
            # Generate response using vLLM (non-streaming)
            outputs = llm_engine.generate([prompt], sampling_params)
            
            # Extract the generated text
            generated_text = outputs[0].outputs[0].text
            logger.info(f"Generated text: {generated_text[:100]}...")
            
            # Build OpenAI-compatible response
            completion_id = f"chatcmpl-{os.urandom(12).hex()}"
            created = int(time.time())
            prompt_tokens = len(outputs[0].prompt_token_ids)
            completion_tokens = len(outputs[0].outputs[0].token_ids)
            
            return {
                "id": completion_id,
                "object": "chat.completion",
                "created": created,
                "model": payload.get("model", model_name),
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
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
            raise
    
    async def _chat_stream(self, prompt: str, sampling_params: SamplingParams, model: str) -> AsyncIterator[str]:
        """Stream chat completions using vLLM
        
        Note: vLLM 0.6.5 with synchronous LLM doesn't support true streaming.
        This implementation generates the full response and yields it in chunks
        for OpenAI API compatibility. For true streaming, use AsyncLLMEngine.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        completion_id = f"chatcmpl-{os.urandom(12).hex()}"
        created = int(time.time())
        
        # Generate response (non-streaming backend, but we'll chunk it)
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        outputs = await loop.run_in_executor(
            None,
            lambda: llm_engine.generate([prompt], sampling_params)
        )
        
        generated_text = outputs[0].outputs[0].text
        finish_reason = outputs[0].outputs[0].finish_reason or "stop"
        
        # Yield text in chunks (simulate streaming)
        # Split into reasonable chunks (words or characters)
        chunk_size = 10  # words per chunk
        words = generated_text.split()
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            delta_text = " ".join(chunk_words)
            if i + chunk_size < len(words):
                delta_text += " "
            
            # Format as OpenAI SSE stream chunk
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": delta_text
                        },
                        "finish_reason": None
                    }
                ]
            }
            
            yield f"data: {self._json_dumps(chunk)}\n\n"
            await asyncio.sleep(0)  # Yield control
        
        # Send final chunk with finish_reason
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": finish_reason
                }
            ]
        }
        yield f"data: {self._json_dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    def _json_dumps(self, obj: Dict[str, Any]) -> str:
        """JSON dump helper"""
        import json
        return json.dumps(obj, ensure_ascii=False)
    
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


# Module-level provider instance for backward compatibility
_provider = VLLMProvider()


# Module-level functions for direct import
async def list_models() -> Dict[str, Any]:
    """List available models"""
    return await _provider.list_models()


async def chat(payload: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[str]]:
    """Chat completion"""
    return await _provider.chat(payload, stream=stream)
