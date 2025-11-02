import os
import time
import gc
import torch
from typing import Dict, Any, AsyncIterator, Union
import asyncio
from threading import Thread, Lock
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

# Model configuration
model_name = "DragonLLM/qwen3-8b-fin-v1.0"
model = None
tokenizer = None
device = "cuda" if torch.cuda.is_available() else "cpu"
_init_lock = Lock()  # Lock to prevent concurrent initialization
_initializing = False  # Track if initialization is in progress
_initialized = False  # Track if initialization completed successfully

def _clear_gpu_memory():
    """Clear GPU memory completely."""
    global model, tokenizer
    if torch.cuda.is_available():
        if model is not None:
            try:
                del model
            except:
                pass
        if tokenizer is not None:
            try:
                del tokenizer
            except:
                pass
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        gc.collect()
        # Force garbage collection multiple times
        for _ in range(3):
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

def initialize_model():
    """Initialize Transformers model with Qwen3
    
    Thread-safe initialization with proper memory cleanup on failure.
    Handles authentication with Hugging Face Hub for accessing DragonLLM models.
    Prioritizes HF_TOKEN_LC2 (DragonLLM access) over HF_TOKEN_LC.
    """
    global model, tokenizer, _initializing, _initialized
    
    # If already initialized, return immediately
    if _initialized and model is not None:
        return
    
    # Acquire lock to prevent concurrent initialization
    with _init_lock:
        # Double-check after acquiring lock
        if _initialized and model is not None:
            return
        
        # If already initializing, wait
        if _initializing:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Model initialization already in progress, waiting...")
            # Wait for initialization to complete (with timeout)
            wait_count = 0
            while _initializing and wait_count < 300:  # 5 minute timeout
                time.sleep(1)
                wait_count += 1
                if _initialized and model is not None:
                    return
            if wait_count >= 300:
                logger.error("Model initialization timeout!")
                raise RuntimeError("Model initialization timed out")
            return
        
        # Clear any previous failed attempts
        if model is None and torch.cuda.is_available():
            _clear_gpu_memory()
        
        _initializing = True
        
        try:
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
                
                # Load custom chat template if missing
                if not hasattr(tokenizer, 'chat_template') or tokenizer.chat_template is None:
                    logger.info("Loading custom chat template from chat_template.jinja...")
                    try:
                        from huggingface_hub import hf_hub_download
                        template_path = hf_hub_download(
                            repo_id=model_name,
                            filename="chat_template.jinja",
                            repo_type="model",
                            token=hf_token,
                            cache_dir="/tmp/huggingface"
                        )
                        with open(template_path, 'r', encoding='utf-8') as f:
                            tokenizer.chat_template = f.read()
                        logger.info("✅ Custom chat template applied")
                        print("✅ Custom chat template applied")
                    except Exception as e:
                        logger.warning(f"Could not load custom template, using default: {e}")
                
                logger.info("✅ Tokenizer loaded")
                print("✅ Tokenizer loaded")
                
                # Clear GPU memory before loading model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    gc.collect()
                
                # Load model with optimizations and memory limits
                print("📥 Loading model (this may take a few minutes)...")
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    token=hf_token,
                    trust_remote_code=True,
                    dtype=torch.bfloat16,  # Use dtype instead of torch_dtype (newer API)
                    device_map="auto",
                    max_memory={0: "20GiB"} if torch.cuda.is_available() else None,  # Leave 2GB buffer
                    cache_dir="/tmp/huggingface",
                    low_cpu_mem_usage=True
                )
                
                # Set to eval mode for inference
                model.eval()
                
                # Mark as initialized only after successful load
                _initialized = True
                
                print(f"✅ Model loaded successfully!")
                logger.info("✅ Model initialized successfully")
                
            except Exception as e:
                error_msg = f"❌ Error initializing model: {e}"
                logger.error(error_msg, exc_info=True)
                print(error_msg)
                
                # Clear memory on failure
                _clear_gpu_memory()
                model = None
                tokenizer = None
                
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
        finally:
            _initializing = False


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
            # Very high default to ensure complete answers with reasoning
            # Qwen3 <think> tags use 300-600 tokens, answer needs 400-1000 tokens
            max_tokens = payload.get("max_tokens", 1500)
            top_p = payload.get("top_p", 1.0)
            
            # Detect if French language is requested and add system prompt
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            system_messages = [msg for msg in messages if msg.get("role") == "system"]
            
            # Check if any user message is in French or explicitly requests French
            is_french_request = False
            for msg in user_messages:
                content = msg.get("content", "")
                content_lower = content.lower()
                
                # Check for explicit French language request
                if any(phrase in content_lower for phrase in ["en français", "répondez en français", "réponse française", "répondez uniquement en français", "expliquez en français"]):
                    is_french_request = True
                    break
                
                # Check for French characters (strong indicator)
                if any(char in content for char in ["é", "è", "ê", "à", "ç", "ù", "ô", "î", "â", "û", "ë", "ï"]):
                    is_french_request = True
                    break
                
                # Check for common French question words/patterns
                french_patterns = [
                    "qu'est-ce",
                    "qu'est",
                    "expliquez",
                    "comment",
                    "pourquoi",
                    "combien",
                    "quel",
                    "quelle",
                    "quels",
                    "quelles",
                    "où",
                    "quand",
                    "définissez"
                ]
                if any(pattern in content_lower for pattern in french_patterns):
                    is_french_request = True
                    break
            
            # Add French system prompt if needed and not already present
            if is_french_request and not any("français" in msg.get("content", "").lower() for msg in system_messages):
                messages = [{"role": "system", "content": "Vous êtes un assistant financier expert. Répondez TOUJOURS en français, y compris dans votre raisonnement. Toutes vos réponses doivent être entièrement en français."}] + messages
            
            # Convert messages to prompt using tokenizer's chat template
            if hasattr(tokenizer, "apply_chat_template"):
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                logger.info(f"✅ Chat template applied. Messages: {len(messages)}")
                # Log if there's a system message
                if any(msg.get("role") == "system" for msg in messages):
                    system_msg = next(msg for msg in messages if msg.get("role") == "system")
                    logger.info(f"📋 System message present: {system_msg['content'][:100]}...")
                logger.info(f"Generated prompt (first 500 chars): {prompt[:500]}")
            else:
                # Fallback to simple prompt format
                prompt = self._messages_to_prompt(messages)
                logger.warning("⚠️  No chat_template found, using fallback")
            
            logger.info(f"Generating response for prompt length: {len(prompt)} chars")
            
            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            
            # Handle streaming vs non-streaming
            if stream:
                return self._chat_stream(inputs, temperature, top_p, max_tokens, payload.get("model", model_name))
            
            # Generate response (non-streaming)
            try:
                with torch.no_grad():
                    # Use Qwen3-specific generation settings for complete answers
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=temperature > 0,
                        pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        # Let model finish naturally - don't stop early
                        repetition_penalty=1.05,
                        length_penalty=1.0,
                        # CRITICAL: Don't stop until EOS or max_tokens
                        early_stopping=False,
                        # Use beam search for more complete answers if temperature is low
                        num_beams=1,  # Greedy/sampling only
                        # Ensure continuation tokens work properly
                        use_cache=True
                    )
                
                # Save token counts before cleanup
                prompt_tokens = inputs.input_ids.shape[1]
                
                # Decode response
                generated_ids = outputs[0][inputs.input_ids.shape[1]:]
                generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
                completion_tokens = len(generated_ids)
                
                # Determine finish reason
                # If we generated max_tokens, it's likely truncated
                finish_reason = "length" if completion_tokens >= max_tokens else "stop"
                
                logger.info(f"Generated {completion_tokens} tokens (max: {max_tokens})")
                logger.info(f"Finish reason: {finish_reason}")
                logger.info(f"Generated text: {generated_text[:100]}...")
                
            finally:
                # Clean up GPU memory after inference
                if 'inputs' in locals():
                    del inputs
                if 'outputs' in locals():
                    del outputs
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
            
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
                        "finish_reason": finish_reason
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
            "eos_token_id": tokenizer.eos_token_id,
            "min_new_tokens": min(10, max_tokens // 10),
            "repetition_penalty": 1.05,
            "streamer": streamer
        }
        
        # Run generation in a separate thread
        def generate():
            try:
                with torch.no_grad():
                    model.generate(**inputs, **generation_kwargs)
            finally:
                # Clean up GPU memory after generation
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        
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
            # Final cleanup
            if 'inputs' in locals():
                del inputs
            gc.collect()
        
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
