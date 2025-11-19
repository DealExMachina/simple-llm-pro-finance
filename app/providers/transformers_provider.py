import os
import time
import json
import logging
import torch
import re
from typing import Dict, Any, AsyncIterator, Union, List, Optional
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
    MODEL_INIT_TIMEOUT_SECONDS,
    MODEL_INIT_WAIT_INTERVAL_SECONDS,
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
from app.utils.stats import get_stats_tracker, RequestStats

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
            while _initializing and wait_count < MODEL_INIT_TIMEOUT_SECONDS:
                time.sleep(MODEL_INIT_WAIT_INTERVAL_SECONDS)
                wait_count += 1
                if _initialized and model is not None:
                    return
            if wait_count >= MODEL_INIT_TIMEOUT_SECONDS:
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
                print("2. Accept model terms at: https://huggingface.co/DragonLLM/Qwen-Open-Finance-R-8B")
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
            tools = payload.get("tools", None)  # ✅ Extract tools
            tool_choice = payload.get("tool_choice", "auto")  # ✅ Extract tool_choice
            response_format = payload.get("response_format", None)  # ✅ Extract response_format
            
            # Handle tool_choice="required" - treat as "auto" for text-based tool calls
            if tool_choice == "required":
                tool_choice = "auto"
                log_info("tool_choice='required' converted to 'auto' for text-based tool calls")
            
            # Detect French and add system prompt if needed
            if is_french_request(messages) and not has_french_system_prompt(messages):
                messages = [{"role": "system", "content": FRENCH_SYSTEM_PROMPT}] + messages
            
            # ✅ Handle response_format for structured JSON outputs
            json_output_required = False
            if response_format:
                if isinstance(response_format, dict):
                    json_output_required = response_format.get("type") == "json_object"
                elif hasattr(response_format, "type"):
                    json_output_required = response_format.type == "json_object"
            
            # ✅ Add tools to system prompt if provided
            if tools:
                tools_description = self._format_tools_for_prompt(tools)
                # Add tools to the last system message or create a new one
                system_messages = [msg for msg in messages if msg.get("role") == "system"]
                if system_messages:
                    # Append to existing system message
                    last_system = system_messages[-1]
                    last_system["content"] = f"{last_system['content']}\n\n{tools_description}"
                else:
                    # Add new system message with tools
                    messages = [{"role": "system", "content": tools_description}] + messages
                log_info(f"Tools added to prompt: {len(tools)} tools")
            
            # ✅ Add JSON output requirement to system prompt if response_format requires it
            if json_output_required:
                json_instruction = (
                    "\n\nIMPORTANT: Vous devez répondre UNIQUEMENT avec un JSON valide. "
                    "Ne pas inclure de texte avant ou après le JSON. "
                    "Ne pas inclure de balises de raisonnement (<think>). "
                    "Répondez directement avec le JSON, sans explication ni raisonnement visible. "
                    "Le JSON doit être bien formé et respecter le schéma demandé."
                )
                system_messages = [msg for msg in messages if msg.get("role") == "system"]
                if system_messages:
                    last_system = system_messages[-1]
                    last_system["content"] = f"{last_system['content']}{json_instruction}"
                else:
                    messages = [{"role": "system", "content": json_instruction}] + messages
                log_info("JSON output format enforced via system prompt")
            
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
                return self._chat_stream(inputs, temperature, top_p, max_tokens, payload.get("model", MODEL_NAME), tools, json_output_required)
            
            return self._generate_response(inputs, temperature, top_p, max_tokens, payload.get("model", MODEL_NAME), tools, json_output_required)
            
        except Exception as e:
            log_error(f"Error in chat completion: {str(e)}", exc_info=True)
            raise
    
    def _generate_response(
        self, inputs, temperature: float, top_p: float, max_tokens: int, model_id: str, tools: Optional[List[Dict[str, Any]]] = None, json_output_required: bool = False
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
            
            # Extract token counts using tokenizer for accuracy
            # Count prompt tokens (more accurate than shape[1] as it handles special tokens correctly)
            prompt_tokens = len(inputs.input_ids[0])
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            completion_tokens = len(generated_ids)
            
            # ✅ If JSON output is required, try to extract JSON from the response
            if json_output_required:
                generated_text = self._extract_json_from_text(generated_text)
            
            # ✅ Parse tool calls from generated text
            tool_calls = None
            if tools:
                tool_calls = self._parse_tool_calls(generated_text, tools)
                if tool_calls:
                    log_info(f"Parsed {len(tool_calls)} tool calls from response")
                    # Remove tool call markers from content if present
                    generated_text = self._clean_tool_calls_from_text(generated_text)
            
            finish_reason = "tool_calls" if tool_calls else ("length" if completion_tokens >= max_tokens else "stop")
            
            log_info(f"Generated {completion_tokens} tokens (max: {max_tokens}), finish: {finish_reason}")
            
            # Record statistics
            stats_tracker = get_stats_tracker()
            stats_tracker.record_request(RequestStats(
                timestamp=time.time(),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                model=model_id,
                finish_reason=finish_reason,
            ))
            
            # Build message with optional tool_calls
            message = {"role": "assistant", "content": generated_text if generated_text.strip() else None}
            if tool_calls:
                message["tool_calls"] = tool_calls
            
            return {
                "id": f"chatcmpl-{os.urandom(12).hex()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_id,
                "choices": [
                    {
                        "index": 0,
                        "message": message,
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
        self, inputs, temperature: float, top_p: float, max_tokens: int, model_id: str, tools: Optional[List[Dict[str, Any]]] = None, json_output_required: bool = False
    ) -> AsyncIterator[str]:
        """Stream chat completions."""
        completion_id = f"chatcmpl-{os.urandom(12).hex()}"
        created = int(time.time())
        
        # Count prompt tokens
        prompt_tokens = len(inputs.input_ids[0])
        completion_tokens = 0
        generated_text = ""
        
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
                generated_text += token
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
            
            # Count completion tokens accurately from generated text
            if generated_text:
                # Use tokenizer to count tokens accurately
                completion_tokens = len(tokenizer.encode(generated_text, add_special_tokens=False))
            else:
                completion_tokens = 0
            
            # Record statistics for streaming request
            stats_tracker = get_stats_tracker()
            finish_reason = "length" if completion_tokens >= max_tokens else "stop"
            stats_tracker.record_request(RequestStats(
                timestamp=time.time(),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                model=model_id,
                finish_reason=finish_reason,
            ))
            
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
    
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in system prompt."""
        tools_text = "Vous avez accès aux outils suivants. Utilisez-les quand nécessaire.\n\n"
        for i, tool in enumerate(tools, 1):
            func = tool.get("function", {})
            name = func.get("name", "")
            description = func.get("description", "")
            parameters = func.get("parameters", {})
            
            tools_text += f"Outil {i}: {name}\n"
            if description:
                tools_text += f"Description: {description}\n"
            if parameters:
                tools_text += f"Paramètres: {json.dumps(parameters, ensure_ascii=False, indent=2)}\n"
            tools_text += "\n"
        
        tools_text += "Pour utiliser un outil, répondez au format suivant:\n"
        tools_text += "<tool_call>\n"
        tools_text += '{"name": "nom_de_l_outil", "arguments": {"param1": "valeur1", "param2": "valeur2"}}\n'
        tools_text += "</tool_call>\n"
        
        return tools_text
    
    def _parse_tool_calls(self, generated_text: str, tools: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Parse tool calls from generated text."""
        tool_calls = []
        
        # Pattern to match <tool_call>...</tool_call> blocks
        pattern = r'<tool_call>\s*({.*?})\s*</tool_call>'
        matches = re.findall(pattern, generated_text, re.DOTALL)
        
        # Also try to match JSON objects that look like tool calls
        if not matches:
            # Try to find JSON objects with "name" and "arguments" keys
            json_pattern = r'\{\s*"name"\s*:\s*"[^"]+",\s*"arguments"\s*:\s*\{[^}]+\}\s*\}'
            matches = re.findall(json_pattern, generated_text, re.DOTALL)
        
        for i, match in enumerate(matches):
            try:
                call_data = json.loads(match)
                name = call_data.get("name", "")
                arguments = call_data.get("arguments", {})
                
                # Validate tool name exists in provided tools
                tool_names = [t.get("function", {}).get("name", "") for t in tools]
                if name not in tool_names:
                    log_warning(f"Tool call to unknown tool: {name}")
                    continue
                
                # Ensure arguments is a JSON string
                if isinstance(arguments, dict):
                    arguments_str = json.dumps(arguments, ensure_ascii=False)
                else:
                    arguments_str = str(arguments)
                
                tool_calls.append({
                    "id": f"call_{os.urandom(8).hex()}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": arguments_str
                    }
                })
            except json.JSONDecodeError as e:
                log_warning(f"Failed to parse tool call JSON: {e}, match: {match[:100]}")
                continue
            except Exception as e:
                log_warning(f"Error parsing tool call: {e}")
                continue
        
        return tool_calls if tool_calls else None
    
    def _clean_tool_calls_from_text(self, text: str) -> str:
        """Remove tool call markers from text to return clean content."""
        # Remove <tool_call>...</tool_call> blocks
        text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL)
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text, handling cases where JSON is wrapped in markdown, reasoning tags, or other text."""
        # Step 1: Remove reasoning tags first (Qwen reasoning models)
        # Handle both <think> and <think> tags
        cleaned_text = text
        
        # Remove reasoning tags (handles both <think> and <think>)
        # Pattern matches any tag starting with <think and ending with </think>
        cleaned_text = re.sub(
            r'<think[^>]*>.*?</think[^>]*>',
            '',
            cleaned_text,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Handle unclosed reasoning tags (split on closing tags)
        # Try both </think> and </think>
        for closing_tag in ["</think>", "</think>"]:
            if closing_tag in cleaned_text:
                parts = cleaned_text.split(closing_tag, 1)
                if len(parts) > 1:
                    cleaned_text = parts[1].strip()
                    break  # Only need to split once
        
        # Step 2: Try to find JSON wrapped in markdown code blocks
        json_code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
        if json_code_block:
            json_str = json_code_block.group(1).strip()
            try:
                json.loads(json_str)  # Validate
                return json_str
            except json.JSONDecodeError:
                pass
        
        # Step 3: Find JSON object(s) in the text
        # Use a more robust approach: find all { ... } patterns and validate them
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.finditer(json_pattern, cleaned_text, re.DOTALL)
        
        # Try to find the largest valid JSON object
        best_match = None
        best_length = 0
        
        for match in matches:
            json_candidate = match.group(0)
            try:
                json.loads(json_candidate)  # Validate
                if len(json_candidate) > best_length:
                    best_match = json_candidate
                    best_length = len(json_candidate)
            except json.JSONDecodeError:
                continue
        
        if best_match:
            return best_match.strip()
        
        # Step 4: Fallback - try to find any JSON-like structure
        # Look for { ... } and try to extract it, even if nested
        brace_start = cleaned_text.find('{')
        if brace_start != -1:
            # Find matching closing brace
            brace_count = 0
            for i in range(brace_start, len(cleaned_text)):
                if cleaned_text[i] == '{':
                    brace_count += 1
                elif cleaned_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_candidate = cleaned_text[brace_start:i+1]
                        try:
                            json.loads(json_candidate)
                            return json_candidate.strip()
                        except json.JSONDecodeError:
                            break
        
        # Step 5: If no JSON found, return cleaned text (without reasoning tags)
        # This allows the caller to handle it or show an error
        return cleaned_text.strip()


# Module-level provider instance
_provider = TransformersProvider()


def is_model_ready() -> bool:
    """
    Thread-safe check if the model is loaded and ready for inference.
    
    Returns:
        True if model is initialized and loaded, False otherwise.
    """
    with _init_lock:
        return _initialized and model is not None and tokenizer is not None


# Module-level functions for direct import
async def list_models() -> Dict[str, Any]:
    """List available models."""
    return await _provider.list_models()


async def chat(payload: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[str]]:
    """Chat completion."""
    return await _provider.chat(payload, stream=stream)
