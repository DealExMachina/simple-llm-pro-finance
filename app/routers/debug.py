from typing import Any, Dict, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class DebugPromptRequest(BaseModel):
    messages: List[Dict[str, str]]


@router.post("/debug/prompt")
async def debug_prompt(body: DebugPromptRequest):
    """Debug endpoint to see what prompt is generated from messages"""
    try:
        from app.providers.transformers_provider import tokenizer, model_name
        from huggingface_hub import hf_hub_download
        import os
        
        # Get token
        hf_token = (
            os.getenv("HF_TOKEN_LC2") or 
            os.getenv("HF_TOKEN_LC") or 
            os.getenv("HF_TOKEN")
        )
        
        # Load tokenizer if needed
        if tokenizer is None:
            from transformers import AutoTokenizer
            temp_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=hf_token,
                trust_remote_code=True
            )
            
            # Try to load custom chat template
            try:
                template_path = hf_hub_download(
                    repo_id=model_name,
                    filename="chat_template.jinja",
                    repo_type="model",
                    token=hf_token
                )
                with open(template_path, 'r', encoding='utf-8') as f:
                    temp_tokenizer.chat_template = f.read()
            except:
                pass
        else:
            temp_tokenizer = tokenizer
        
        # Apply chat template
        if hasattr(temp_tokenizer, "apply_chat_template") and temp_tokenizer.chat_template:
            prompt = temp_tokenizer.apply_chat_template(
                body.messages,
                tokenize=False,
                add_generation_prompt=True
            )
            has_template = True
        else:
            prompt = "No chat template available"
            has_template = False
        
        return JSONResponse(content={
            "messages_received": body.messages,
            "message_count": len(body.messages),
            "has_chat_template": has_template,
            "template_length": len(temp_tokenizer.chat_template) if has_template else 0,
            "generated_prompt": prompt,
            "prompt_length": len(prompt)
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

