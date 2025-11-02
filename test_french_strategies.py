#!/usr/bin/env python3
"""
Test different strategies for getting French responses
"""
import httpx
import json

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("="*80)
print("TESTING DIFFERENT FRENCH PROMPTING STRATEGIES")
print("="*80)

question = "Expliquez le CAC 40"

# Strategy 1: No system prompt, just French question
print("\n[Strategy 1] French question only (no system prompt)")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 400,
        "temperature": 0.3
    },
    timeout=60.0
)
data = response.json()
if "choices" in data:
    content = data["choices"][0]["message"]["content"]
    print(f"Response: {content[:300]}...")

# Strategy 2: French instruction in USER message
print("\n" + "="*80)
print("[Strategy 2] French instruction in USER message")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": f"{question}. Répondez en français."}],
        "max_tokens": 400,
        "temperature": 0.3
    },
    timeout=60.0
)
data = response.json()
if "choices" in data:
    content = data["choices"][0]["message"]["content"]
    print(f"Response: {content[:300]}...")

# Strategy 3: System prompt (what we're currently doing)
print("\n" + "="*80)
print("[Strategy 3] System prompt for French")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "system", "content": "Réponds TOUJOURS en français."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 400,
        "temperature": 0.3
    },
    timeout=60.0
)
data = response.json()
if "choices" in data:
    content = data["choices"][0]["message"]["content"]
    print(f"Response: {content[:300]}...")

# Strategy 4: Both user instruction AND system prompt
print("\n" + "="*80)
print("[Strategy 4] Both system prompt AND user instruction")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "system", "content": "Tu es un assistant financier. Réponds en français."},
            {"role": "user", "content": f"{question}. Réponds EN FRANÇAIS."}
        ],
        "max_tokens": 400,
        "temperature": 0.3
    },
    timeout=60.0
)
data = response.json()
if "choices" in data:
    content = data["choices"][0]["message"]["content"]
    # Extract answer
    if "</think>" in content:
        answer = content.split("</think>")[1].strip()
    else:
        answer = content
    
    print(f"Response: {content[:300]}...")
    print(f"\nAnswer only: {answer[:200]}...")
    
    # Check language
    is_french = any(c in answer for c in ["é", "è", "à"]) or " est " in answer.lower()
    print(f"✅ Answer is French: {is_french}")

