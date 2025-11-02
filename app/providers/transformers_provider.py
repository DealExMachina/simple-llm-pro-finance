import os
import time
import json
import logging
import torch
from typing import Dict, Any, AsyncIterator, Union
import asyncio
from threading import Thread, Lock
from huggingface_hub import login, hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from app.utils.constants import (
    MODEL_NAME,
    CACHE_DIR,
    FRENCH_SYSTEM_PROMPT,
    EOS_TOKENS,
    PAD_TOKEN_ID,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_TOP_K,
    REPETITION_PENALTY,
)
from app.utils.helpers import (
    get_hf_token,
    is_french_request,
    has_french_system_prompt,
    log_info,
    log_warning,
    log_error,
)
from app.utils.memory import clear_gpu_memory

logger = logging.getLogger(__name__)

# Global model state
model = None
tokenizer = None
device = "cuda" if torch.cuda.is_available() else "cpu"
_init_lock = Lock()
_initializing = False
_initialized = False


def initialize_model(force_reload: bool = False):
    """
    Initialize Transformers model with Qwen3.
    
    Args:
        force_reload: If True, reload model even if already initialized.
    
    Thread-safe initialization with proper memory cleanup on failure.
    Handles authentication with Hugging Face Hub for accessing DragonLLM models.
    """
    global model, tokenizer, _initializing, _initialized
    
    # Check if already initialized (unless force reload)
    if not force_reload and _initialized and model is not None:
        return
    
    with _init_lock:
        # Double-check after acquiring lock
        if not force_reload and _initialized and model is not None:
            return
        
        # Handle concurrent initialization
        if _initializing:
            log_warning("Model initialization already in progress, waiting...")
            wait_count = 0
            while _initializing and wait_count < 300:  # 5 minute timeout
                time.sleep(1)
                wait_count += 1
                if _initialized and model is not None:
                    return
            if wait_count >= 300:
                log_error("Model initialization timeout!", print_output=True)
                raise RuntimeError("Model initialization timed out")
            return
        
        # Clear previous model if force reloading
        if force_reload and model is not None:
            log_info("Force reload requested, clearing existing model...", print_output=True)
            clear_gpu_memory(model, tokenizer)
            model = None
            tokenizer = None
            _initialized = False
        
        # Clear any previous failed attempts
        if model is None and torch.cuda.is_available():
            clear_gpu_memory()
        
        _initializing = True
        
        try:
            log_info(f"Initializing Transformers with model: {MODEL_NAME}", print_output=True)
            
            # Get HF token
            hf_token, token_source = get_hf_token()
            
            if hf_token:
                log_info(f"{token_source} found (length: {len(hf_token)})", print_output=True)
                
                # Authenticate with Hugging Face Hub
                try:
                    login(token=hf_token, add_to_git_credential=False)
                    log_info("Successfully authenticated with Hugging Face Hub", print_output=True)
                except Exception as e:
                    log_warning(f"Failed to authenticate with HF Hub: {e}", print_output=True)
                
                # Set token environment variables
                os.environ.update({
                    "HF_TOKEN": hf_token,
                    "HUGGING_FACE_HUB_TOKEN": hf_token,
                    "HF_API_TOKEN": hf_token,
                })
            else:
                log_warning(
                    "No HF token found! Model download may fail if model is gated.",
                    print_output=True
                )
            
            # Load tokenizer
            log_info("Loading tokenizer...", print_output=True)
            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                token=hf_token,
                trust_remote_code=True,
                cache_dir=CACHE_DIR,
            )
            
            # Load custom chat template if missing
            if not hasattr(tokenizer, 'chat_template') or tokenizer.chat_template is None:
                try:
                    template_path = hf_hub_download(
                        repo_id=MODEL_NAME,
                        filename="chat_template.jinja",
                        repo_type="model",
                        token=hf_token,
                        cache_dir=CACHE_DIR,
                    )
                    with open(template_path, 'r', encoding='utf-8') as f:
                        tokenizer.chat_template = f.read()
                    log_info("Custom chat template applied", print_output=True)
                except Exception as e:
                    log_warning(f"Could not load custom template, using default: {e}")
            
            log_info("Tokenizer loaded", print_output=True)
            
            # Clear GPU memory before loading model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                import gc
                gc.collect()
            
            # Load model
            log_info("Loading model (this may take a few minutes)...", print_output=True)
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                token=hf_token,
                trust_remote_code=True,
                dtype=torch.bfloat16,
                device_map="auto",
                max_memory={0: "20GiB"} if torch.cuda.is_available() else None,
                cache_dir=CACHE_DIR,
                low_cpu_mem_usage=True,
            )
            
            model.eval()
            _initialized = True
            
            log_info("Model loaded successfully!", print_output=True)
            
        except Exception as e:
            error_msg = f"Error initializing model: {e}"
            log_error(error_msg, exc_info=True, print_output=True)
            
            clear_gpu_memory(model, tokenizer)
            model = None
            tokenizer = None
            
            # Provide helpful error message for authentication issues
            if "401" in str(e) or "Unauthorized" in str(e) or "authentication" in str(e).lower():
                print("\nAuthentication Error Detected!")
                print("1. Ensure HF_TOKEN_LC2 is set in your environment")
                print("2. Accept model terms at: https://huggingface.co/DragonLLM/qwen3-8b-fin-v1.0")
                print("3. Verify token has access to DragonLLM models")
            
            raise
        finally:
            _initializing = False


class TransformersProvider:
    """Provider for Transformers-based model inference."""
    
    def __init__(self):
        pass
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models."""
        return {
            "object": "list",
            "data": [
                {
                    "id": MODEL_NAME,
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "DragonLLM",
                    "permission": [],
                    "root": MODEL_NAME,
                    "parent": None,
                }
            ]
        }
    
    async def chat(
        self, payload: Dict[str, Any], stream: bool = False
    ) -> Union[Dict[str, Any], AsyncIterator[str]]:
        """Handle chat completion requests."""
        try:
            # Initialize model on first use
            if model is None:
                log_info("Model not initialized, initializing now...")
                initialize_model()
                log_info("Model initialized successfully")
            
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", DEFAULT_TEMPERATURE)
            max_tokens = payload.get("max_tokens", DEFAULT_MAX_TOKENS)
            top_p = payload.get("top_p", DEFAULT_TOP_P)
            
            # Detect French and add system prompt if needed
            if is_french_request(messages) and not has_french_system_prompt(messages):
                messages = [{"role": "system", "content": FRENCH_SYSTEM_PROMPT}] + messages
            
            # Generate prompt using chat template
            if hasattr(tokenizer, "apply_chat_template"):
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
                log_info(f"Chat template applied. Messages: {len(messages)}")
                if any(msg.get("role") == "system" for msg in messages):
                    system_msg = next(msg for msg in messages if msg.get("role") == "system")
                    log_info(f"System message present: {system_msg['content'][:100]}...")
            else:
                prompt = self._messages_to_prompt(messages)
                log_warning("No chat_template found, using fallback")
            
            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            
            # Handle streaming vs non-streaming
            if stream:
                return self._chat_stream(inputs, temperature, top_p, max_tokens, payload.get("model", MODEL_NAME))
            
            return self._generate_response(inputs, temperature, top_p, max_tokens, payload.get("model", MODEL_NAME))
            
        except Exception as e:
            log_error(f"Error in chat completion: {str(e)}", exc_info=True)
            raise
    
    def _generate_response(
        self, inputs, temperature: float, top_p: float, max_tokens: int, model_id: str
    ) -> Dict[str, Any]:
        """Generate non-streaming response."""
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=DEFAULT_TOP_K,
                    do_sample=temperature > 0,
                    pad_token_id=PAD_TOKEN_ID,
                    eos_token_id=EOS_TOKENS,
                    repetition_penalty=REPETITION_PENALTY,
                    early_stopping=False,
                    use_cache=True,
                )
            
            # Extract token counts before cleanup
            prompt_tokens = inputs.input_ids.shape[1]
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            completion_tokens = len(generated_ids)
            finish_reason = "length" if completion_tokens >= max_tokens else "stop"
            
            log_info(f"Generated {completion_tokens} tokens (max: {max_tokens}), finish: {finish_reason}")
            
            return {
                "id": f"chatcmpl-{os.urandom(12).hex()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_id,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": generated_text},
                        "finish_reason": finish_reason,
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }
        finally:
            # Clean up GPU memory
            if 'inputs' in locals():
                del inputs
            if 'outputs' in locals():
                del outputs
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            import gc
            gc.collect()
    
    async def _chat_stream(
        self, inputs, temperature: float, top_p: float, max_tokens: int, model_id: str
    ) -> AsyncIterator[str]:
        """Stream chat completions."""
        completion_id = f"chatcmpl-{os.urandom(12).hex()}"
        created = int(time.time())
        
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "pad_token_id": tokenizer.eos_token_id,
            "eos_token_id": tokenizer.eos_token_id,
            "min_new_tokens": min(10, max_tokens // 10),
            "repetition_penalty": REPETITION_PENALTY,
            "streamer": streamer,
        }
        
        def generate():
            try:
                with torch.no_grad():
                    model.generate(**inputs, **generation_kwargs)
            finally:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        
        generation_thread = Thread(target=generate)
        generation_thread.start()
        
        try:
            for token in streamer:
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_id,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": token},
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)
        finally:
            generation_thread.join()
            if 'inputs' in locals():
                del inputs
            import gc
            gc.collect()
        
        # Send final chunk
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_id,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    
    def _messages_to_prompt(self, messages: list) -> str:
        """Convert OpenAI messages format to prompt (fallback)."""
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


# Module-level provider instance
_provider = TransformersProvider()


# Module-level functions for direct import
async def list_models() -> Dict[str, Any]:
    """List available models."""
    return await _provider.list_models()


async def chat(payload: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[str]]:
    """Chat completion."""
    return await _provider.chat(payload, stream=stream)
