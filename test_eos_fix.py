#!/usr/bin/env python3
"""
Test that the EOS token fix is working properly
Verify: no regressions, better completion, proper finish_reason
"""
import httpx
import json
import time

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

def check_space_status():
    """Check if Space is running"""
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=10.0)
        data = response.json()
        return data.get("status") == "ok" and data.get("backend") == "Transformers"
    except:
        return False

print("="*80)
print("TESTING EOS TOKEN FIX")
print("="*80)

if not check_space_status():
    print("❌ Space not ready. Please wait for rebuild.")
    exit(1)

print("✅ Space is ready\n")

# Test 1: Check finish_reason is accurate
print("[TEST 1] Verify finish_reason accuracy")
print("-" * 80)

response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": "What is 2+2? Answer in 5 words."}],
        "max_tokens": 50,
        "temperature": 0.3
    },
    timeout=60.0
)

data = response.json()
finish = data["choices"][0]["finish_reason"]
content = data["choices"][0]["message"]["content"]
tokens = data.get("usage", {}).get("completion_tokens", 0)

print(f"Max tokens: 50")
print(f"Generated: {tokens} tokens")
print(f"Finish reason: {finish}")
print(f"Response: {content[:150]}...")

if finish == "stop" and tokens < 50:
    print("✅ PASS: Stopped naturally with EOS token (not length limit)")
elif finish == "length" and tokens >= 50:
    print("✅ PASS: Correctly detected length limit")
else:
    print(f"⚠️  Unexpected: finish={finish}, tokens={tokens}")

# Test 2: Check complete French answer
print("\n[TEST 2] Complete French answer")
print("-" * 80)

response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": "Qu'est-ce qu'une obligation? Soyez concis."}],
        "max_tokens": 300,
        "temperature": 0.3
    },
    timeout=60.0
)

data = response.json()
content = data["choices"][0]["message"]["content"]
finish = data["choices"][0]["finish_reason"]
tokens = data.get("usage", {}).get("completion_tokens", 0)

# Extract answer
if "</think>" in content:
    answer = content.split("</think>")[1].strip()
else:
    answer = content

print(f"Generated: {tokens} tokens")
print(f"Finish reason: {finish}")
print(f"\nFull answer:\n{answer}\n")

# Check completeness
ends_properly = answer.rstrip().endswith((".", "!", "?", ")", "]"))
has_french = any(c in answer for c in ["é", "è", "à", "ç"])

print(f"Ends properly: {ends_properly}")
print(f"Is French: {has_french}")
print(f"Finish: {finish}")

if ends_properly and finish == "stop" and has_french:
    print("✅ PASS: Complete French answer with proper EOS")
else:
    print(f"⚠️  Check: ends={ends_properly}, finish={finish}, french={has_french}")

# Test 3: Long answer completeness
print("\n[TEST 3] Long answer completeness")
print("-" * 80)

response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": "Expliquez en détail le nantissement de compte-titres."}],
        "temperature": 0.3
        # Use default max_tokens (1500)
    },
    timeout=90.0
)

data = response.json()
content = data["choices"][0]["message"]["content"]
finish = data["choices"][0]["finish_reason"]
tokens = data.get("usage", {}).get("completion_tokens", 0)

if "</think>" in content:
    answer = content.split("</think>")[1].strip()
else:
    answer = content

print(f"Generated: {tokens} tokens (default max: 1500)")
print(f"Finish reason: {finish}")
print(f"Answer length: {len(answer)} chars")
print(f"Last 150 chars: ...{answer[-150:]}")

if finish == "stop":
    print("✅ PASS: Model stopped naturally at EOS (complete answer)")
elif finish == "length":
    print(f"⚠️  Hit token limit - may need higher max_tokens for complex questions")
else:
    print(f"❌ Unexpected finish_reason: {finish}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("If all tests show 'stop' finish_reason and proper sentence endings,")
print("the EOS token fix is working correctly!")

