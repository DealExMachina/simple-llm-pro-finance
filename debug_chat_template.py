#!/usr/bin/env python3
"""
Test chat template locally to see what prompt is generated
"""
import os
from huggingface_hub import login, hf_hub_download
from transformers import AutoTokenizer

token = os.getenv("HF_TOKEN_LC2") or os.getenv("HF_TOKEN_LC")
if token:
    login(token=token)

model_name = "DragonLLM/qwen3-8b-fin-v1.0"

print("="*80)
print("Loading tokenizer and testing chat template...")
print("="*80)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    token=token,
    trust_remote_code=True
)

print(f"\nTokenizer loaded")
print(f"Has chat_template attribute: {hasattr(tokenizer, 'chat_template')}")
print(f"chat_template is None: {tokenizer.chat_template is None if hasattr(tokenizer, 'chat_template') else 'N/A'}")

# Try to load custom template
try:
    template_path = hf_hub_download(
        repo_id=model_name,
        filename="chat_template.jinja",
        token=token
    )
    with open(template_path, 'r', encoding='utf-8') as f:
        custom_template = f.read()
    
    print(f"\n✅ Custom template found in chat_template.jinja")
    print(f"Template length: {len(custom_template)} chars")
    print(f"\nFirst 500 chars:")
    print(custom_template[:500])
    
    # Apply it
    tokenizer.chat_template = custom_template
    print("\n✅ Custom template applied to tokenizer")
except Exception as e:
    print(f"\n❌ Could not load custom template: {e}")

# Test different message combinations
print("\n" + "="*80)
print("TEST 1: User message only (English)")
print("="*80)
messages = [{"role": "user", "content": "What is 2+2?"}]
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
print(f"Generated prompt:\n{prompt}\n")

print("="*80)
print("TEST 2: System + User (French)")
print("="*80)
messages = [
    {"role": "system", "content": "Réponds EN FRANÇAIS."},
    {"role": "user", "content": "Qu'est-ce qu'une obligation?"}
]
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
print(f"Generated prompt:\n{prompt}\n")

print("="*80)
print("TEST 3: Does template preserve system message?")
print("="*80)
if "<|im_start|>system" in prompt and "FRANÇAIS" in prompt:
    print("✅ System message IS in the prompt!")
else:
    print("❌ System message NOT in the prompt or not preserved!")

