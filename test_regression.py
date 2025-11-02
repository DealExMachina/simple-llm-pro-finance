#!/usr/bin/env python3
"""
Regression test: verify EOS token fix improves completeness without breaking anything
"""
import httpx
import json
import time

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("="*80)
print("REGRESSION & IMPROVEMENT TEST")
print("="*80)

# Test 1: Basic functionality still works
print("\n[1] Basic functionality check")
try:
    response = httpx.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
            "max_tokens": 100,
            "temperature": 0.3
        },
        timeout=30.0
    )
    
    data = response.json()
    if "error" not in data:
        print(f"✅ Basic request works")
    else:
        print(f"❌ Error: {data['error']['message']}")
except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(3)

# Test 2: French answer with reasonable token limit
print("\n[2] French answer (500 tokens)")
try:
    response = httpx.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": "Qu'est-ce qu'une obligation? Réponse courte."}],
            "max_tokens": 500,
            "temperature": 0.3
        },
        timeout=45.0
    )
    
    data = response.json()
    if "error" in data:
        print(f"❌ Error: {data['error']['message'][:100]}")
    else:
        content = data["choices"][0]["message"]["content"]
        finish = data["choices"][0]["finish_reason"]
        tokens = data.get("usage", {}).get("completion_tokens", 0)
        
        answer = content.split("</think>")[1].strip() if "</think>" in content else content
        
        print(f"Tokens: {tokens}/500")
        print(f"Finish: {finish}")
        print(f"Answer: {answer}")
        print(f"Ends properly: {answer.rstrip().endswith(('.', '!', '?'))}")
        
        if finish == "stop":
            print(f"✅ IMPROVEMENT: Stopped naturally at EOS (was hitting length before)")
        elif finish == "length":
            print(f"⚠️  Still hitting length limit")
            
except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(3)

# Test 3: Sequential requests (no OOM regression)
print("\n[3] Sequential requests (memory check)")
success = 0
for i in range(1, 4):
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": f"Calculate {i}+{i}"}],
                "max_tokens": 200,
                "temperature": 0.3
            },
            timeout=30.0
        )
        
        data = response.json()
        if "error" not in data:
            success += 1
            print(f"  [{i}] ✅")
        else:
            if "out of memory" in data["error"]["message"].lower():
                print(f"  [{i}] ❌ OOM!")
            else:
                print(f"  [{i}] ❌ Error")
        time.sleep(2)
    except:
        print(f"  [{i}] ❌ Timeout/Exception")

if success == 3:
    print(f"✅ NO REGRESSION: Memory management still working")
else:
    print(f"❌ REGRESSION: Only {success}/3 succeeded")

print("\n" + "="*80)
print("VERDICT")
print("="*80)
print("If Test 2 shows finish='stop' → EOS fix is working ✅")
print("If Test 2 shows finish='length' → Need more investigation ⚠️")
print("If Test 3 passes → No memory regression ✅")

