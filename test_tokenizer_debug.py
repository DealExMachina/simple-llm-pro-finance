#!/usr/bin/env python3
"""
Debug the tokenizer and chat template to understand French handling
"""
import httpx
import json

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("="*80)
print("DEBUGGING TOKENIZER & CHAT TEMPLATE")
print("="*80)

# Test 1: Simple French question
print("\n[Test 1] Simple French question")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": "Qu'est-ce qu'une obligation?"}
        ],
        "max_tokens": 300,
        "temperature": 0.3
    },
    timeout=60.0
)
if response.status_code == 200:
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"Response: {content[:500]}...")
    
    # Check if reasoning is in French
    if "<think>" in content:
        reasoning = content.split("<think>")[1].split("</think>")[0] if "</think>" in content else ""
        print(f"\nReasoning language check:")
        print(f"  Has French words: {'oui' in reasoning.lower() or 'est' in reasoning.lower()}")
        print(f"  First 200 chars of reasoning: {reasoning[:200]}")

# Test 2: With explicit French system prompt
print("\n" + "="*80)
print("[Test 2] With explicit French system prompt")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "system", "content": "Tu es un expert en finance. Réponds TOUJOURS et UNIQUEMENT en français. Même ton raisonnement interne doit être en français."},
            {"role": "user", "content": "Explique ce qu'est le CAC 40"}
        ],
        "max_tokens": 300,
        "temperature": 0.3
    },
    timeout=60.0
)
if response.status_code == 200:
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"Response: {content[:500]}...")
    
    if "<think>" in content and "</think>" in content:
        reasoning = content.split("<think>")[1].split("</think>")[0]
        answer = content.split("</think>")[1].strip()
        print(f"\nReasoning: {reasoning[:200]}...")
        print(f"\nAnswer: {answer[:200]}...")

# Test 3: No system prompt, very explicit French request
print("\n" + "="*80)
print("[Test 3] Very explicit French request in user message")
response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": "Réponds EN FRANÇAIS SEULEMENT: Qu'est-ce qu'une SICAV?"}
        ],
        "max_tokens": 300,
        "temperature": 0.3
    },
    timeout=60.0
)
if response.status_code == 200:
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"Response: {content[:500]}...")

