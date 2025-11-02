import os
import time
import torch
from typing import Dict, Any, AsyncIterator, Union
import asyncio
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

# Model configuration
model_name = "DragonLLM/qwen3-8b-fin-v1.0"
model = None
tokenizer = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def initialize_model():
    """Initialize Transformers model with Qwen3
    
    Handles authentication with Hugging Face Hub for accessing DragonLLM models.
    Prioritizes HF_TOKEN_LC2 (DragonLLM access) over HF_TOKEN_LC.
    """
    global model, tokenizer
    
    if model is None:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Initializing Transformers with model: {model_name}")
        print(f"Initializing Transformers with model: {model_name}")
        
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
            
            # Set all possible environment variables
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
            os.environ["HF_API_TOKEN"] = hf_token
            
            logger.info("✅ Hugging Face token environment variables set")
        else:
            logger.warning("⚠️  WARNING: No HF token found in environment!")
            print("⚠️  WARNING: No HF token found in environment!")
            print(f"   Checked: HF_TOKEN_LC2, HF_TOKEN_LC, HF_TOKEN, HUGGING_FACE_HUB_TOKEN")
            print("   ⚠️  Model download may fail if DragonLLM/qwen3-8b-fin-v1.0 is gated!")
        
        try:
            logger.info(f"Loading model: {model_name}")
            print(f"Loading model: {model_name}")
            print(f"Model type: DragonLLM Qwen3 8B")
            print(f"Device: {device}")
            print(f"Trust remote code: True")
            
            # Load tokenizer
            print("📥 Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=hf_token,
                trust_remote_code=True,
                cache_dir="/tmp/huggingface"
            )
            logger.info("✅ Tokenizer loaded")
            print("✅ Tokenizer loaded")
            
            # Load model with optimizations
            print("📥 Loading model (this may take a few minutes)...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                token=hf_token,
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                cache_dir="/tmp/huggingface"
            )
            
            # Set to eval mode for inference
            model.eval()
            
            print(f"✅ Model loaded successfully!")
            logger.info("✅ Model initialized successfully")
            
        except Exception as e:
            error_msg = f"❌ Error initializing model: {e}"
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


class TransformersProvider:
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
            # Initialize model on first use
            if model is None:
                logger.info("Model not initialized, initializing now...")
                initialize_model()
                logger.info("Model initialized successfully")
            
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", 0.7)
            max_tokens = payload.get("max_tokens", 1000)
            top_p = payload.get("top_p", 1.0)
            
            # Convert messages to prompt using tokenizer's chat template
            if hasattr(tokenizer, "apply_chat_template"):
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                # Fallback to simple prompt format
                prompt = self._messages_to_prompt(messages)
            
            logger.info(f"Generating response for prompt: {prompt[:100]}...")
            
            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            
            # Handle streaming vs non-streaming
            if stream:
                return self._chat_stream(inputs, temperature, top_p, max_tokens, payload.get("model", model_name))
            
            # Generate response (non-streaming)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=temperature > 0,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            logger.info(f"Generated text: {generated_text[:100]}...")
            
            # Calculate tokens (approximate)
            prompt_tokens = inputs.input_ids.shape[1]
            completion_tokens = len(generated_ids)
            
            # Build OpenAI-compatible response
            completion_id = f"chatcmpl-{os.urandom(12).hex()}"
            created = int(time.time())
            
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
    
    async def _chat_stream(self, inputs, temperature: float, top_p: float, max_tokens: int, model_id: str) -> AsyncIterator[str]:
        """Stream chat completions using Transformers TextIteratorStreamer"""
        import logging
        logger = logging.getLogger(__name__)
        
        completion_id = f"chatcmpl-{os.urandom(12).hex()}"
        created = int(time.time())
        
        # Create streamer
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        # Generation parameters
        generation_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "pad_token_id": tokenizer.eos_token_id,
            "streamer": streamer
        }
        
        # Run generation in a separate thread
        def generate():
            with torch.no_grad():
                model.generate(**inputs, **generation_kwargs)
        
        generation_thread = Thread(target=generate)
        generation_thread.start()
        
        # Stream tokens as they're generated
        try:
            for token in streamer:
                # Yield chunks
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_id,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": token
                            },
                            "finish_reason": None
                        }
                    ]
                }
                
                yield f"data: {self._json_dumps(chunk)}\n\n"
                await asyncio.sleep(0)  # Yield control
        finally:
            # Wait for generation to complete
            generation_thread.join()
        
        # Send final chunk
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
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
        """Convert OpenAI messages format to prompt (fallback)"""
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
_provider = TransformersProvider()


# Module-level functions for direct import
async def list_models() -> Dict[str, Any]:
    """List available models"""
    return await _provider.list_models()


async def chat(payload: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[str]]:
    """Chat completion"""
    return await _provider.chat(payload, stream=stream)
