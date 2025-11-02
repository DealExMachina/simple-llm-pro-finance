#!/usr/bin/env python3
"""
Test if system prompts are being applied at all
"""
import httpx
import json

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("="*80)
print("TESTING IF SYSTEM PROMPTS ARE RESPECTED")
print("="*80)

# Test with a very strong instruction
print("\n[Test] Strong system instruction")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {
                "role": "system", 
                "content": "You MUST start every response with 'SYSTEM PROMPT WORKING:'. Always respond in French. Toujours répondre en français."
            },
            {
                "role": "user", 
                "content": "Qu'est-ce qu'une obligation?"
            }
        ],
        "max_tokens": 200,
        "temperature": 0.3
    },
    timeout=60.0
)

if response.status_code == 200:
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"\nFull response:\n{content}\n")
    
    if "SYSTEM PROMPT WORKING" in content:
        print("✅ System prompt IS being applied!")
    else:
        print("❌ System prompt NOT being applied!")
    
    # Check language
    if any(french in content for french in ["l'", "est", "une", "le", "la"]):
        print("✅ Contains some French")
    else:
        print("❌ No French detected")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

