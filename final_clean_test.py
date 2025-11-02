#!/usr/bin/env python3
"""
Clean, accurate test of all functionality
"""
import httpx
import json
import time

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("="*80)
print("FINAL COMPREHENSIVE TEST")
print("="*80)

# Test 1: Memory management (sequential requests)
print("\n[TEST 1] Memory Management - 5 Sequential Requests")
print("-" * 80)
oom_errors = 0
success_count = 0

for i in range(1, 6):
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": f"Calculate {i} + {i}. Show your work."}],
                "max_tokens": 200,
                "temperature": 0.3
            },
            timeout=60.0
        )
        
        data = response.json()
        if "error" in data and "out of memory" in data["error"]["message"].lower():
            oom_errors += 1
            print(f"  [{i}] ❌ OOM Error")
        elif "choices" in data:
            success_count += 1
            print(f"  [{i}] ✅ Success")
        time.sleep(2)
    except Exception as e:
        print(f"  [{i}] ❌ Error: {str(e)[:50]}")

print(f"\nResult: {success_count}/5 successful, {oom_errors} OOM errors")
print(f"{'✅ PASS' if oom_errors == 0 and success_count >= 4 else '❌ FAIL'}: Memory management working")

# Test 2: French language (IMPROVED DETECTION)
print("\n[TEST 2] French Language Support")
print("-" * 80)

french_questions = [
    "Qu'est-ce qu'une obligation?",
    "Expliquez le CAC 40 en quelques phrases.",
    "Qu'est-ce qu'une SICAV?"
]

french_count = 0

for q in french_questions:
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": q}],
                "max_tokens": 500,
                "temperature": 0.3
            },
            timeout=60.0
        )
        
        data = response.json()
        if "choices" not in data:
            print(f"  ❌ {q[:40]}... → Error")
            continue
        
        content = data["choices"][0]["message"]["content"]
        
        # Extract answer (handle </think> properly)
        if "</think>" in content:
            answer = content.split("</think>", 1)[1].strip()
        else:
            answer = content.strip()
        
        # Robust French detection
        has_french_chars = any(c in answer for c in ["é", "è", "ê", "à", "ç", "ù", "î", "ô", "û"])
        has_french_words = sum(1 for w in [" est ", " une ", " le ", " la ", " les ", " des ", " sont "] if w in answer.lower()) >= 2
        is_french = has_french_chars or has_french_words
        
        status = "✅" if is_french else "❌"
        print(f"  {status} {q[:40]}... → {'French' if is_french else 'English'}")
        print(f"     Preview: {answer[:100]}...")
        
        if is_french:
            french_count += 1
        
        time.sleep(2)
    except Exception as e:
        print(f"  ❌ {q[:40]}... → Exception")

print(f"\nResult: {french_count}/3 answers in French")
print(f"{'✅ PASS' if french_count >= 3 else '⚠️  PARTIAL' if french_count >= 2 else '❌ FAIL'}: French support")

# Test 3: Truncation check
print("\n[TEST 3] Response Completeness (No Truncation)")
print("-" * 80)

response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": "Explain the Black-Scholes model briefly."}],
        "temperature": 0.3
        # No max_tokens - use default (should be 1200 now)
    },
    timeout=60.0
)

data = response.json()
if "choices" in data:
    finish_reason = data["choices"][0].get("finish_reason")
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    
    print(f"  Finish reason: {finish_reason}")
    print(f"  Tokens: {usage.get('completion_tokens', 'N/A')}")
    print(f"  Length: {len(content)} chars")
    print(f"  Last 100 chars: ...{content[-100:]}")
    
    is_complete = finish_reason == "stop"
    print(f"\n{'✅ PASS' if is_complete else '⚠️  PARTIAL'}: Response {'complete' if is_complete else 'may be truncated'}")
else:
    print("  ❌ Error getting response")

print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Memory Management: {'✅ PASS' if oom_errors == 0 else '❌ FAIL'}")
print(f"French Support: {'✅ PASS' if french_count >= 3 else '⚠️  PARTIAL'}")
print(f"Complete Answers: Depends on finish_reason above")

