#!/usr/bin/env python3
import httpx
import json

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("Testing French with system prompt...")

response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert financier. Réponds EN FRANÇAIS. Start with FRENCH TEST:"
            },
            {
                "role": "user",
                "content": "Qu'est-ce qu'une obligation?"
            }
        ],
        "max_tokens": 300,
        "temperature": 0.3
    },
    timeout=60.0
)

data = response.json()
if "error" in data:
    print(f"Error: {data['error']['message']}")
else:
    content = data["choices"][0]["message"]["content"]
    print(f"\nFull response:\n{content}\n")
    print(f"Starts with 'FRENCH TEST:': {'FRENCH TEST:' in content}")
    
    # Extract answer after thinking
    if "</think>" in content:
        answer = content.split("</think>")[1].strip()
        print(f"\nAnswer only (after thinking):\n{answer}\n")
