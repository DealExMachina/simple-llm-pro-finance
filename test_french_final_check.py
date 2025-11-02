#!/usr/bin/env python3
"""
Check if French ANSWERS are working (ignore English reasoning)
"""
import httpx
import json

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

tests = [
    "Qu'est-ce qu'une obligation?",
    "Expliquez le CAC 40.",
    "Combien vaut 5000€ investi à 4% pendant 2 ans?",
    "Qu'est-ce qu'une SICAV?"
]

print("="*80)
print("FRENCH ANSWER TEST (ignoring English reasoning)")
print("="*80)

french_answers = 0

for i, question in enumerate(tests, 1):
    print(f"\n[Test {i}] {question}")
    
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
    
    if response.status_code != 200:
        print(f"  ❌ Error: {response.status_code}")
        continue
    
    data = response.json()
    if "error" in data:
        print(f"  ❌ Error: {data['error']['message'][:100]}")
        continue
    
    content = data["choices"][0]["message"]["content"]
    finish_reason = data["choices"][0].get("finish_reason", "unknown")
    
    # Extract answer after </think>
    if "</think>" in content:
        answer = content.split("</think>")[1].strip()
    else:
        answer = content
    
    # Check if answer is in French
    french_words = ["est", "une", "le", "la", "les", "des", "sont", "avec", "pour"]
    french_found = sum(1 for word in french_words if f" {word} " in answer.lower())
    
    # Also check for French-specific patterns
    has_french_chars = any(c in answer for c in ["é", "è", "ê", "à", "ç"])
    is_french = french_found >= 3 or has_french_chars
    
    print(f"  Finish: {finish_reason}")
    print(f"  Answer length: {len(answer)} chars")
    print(f"  French words: {french_found}")
    print(f"  French chars: {has_french_chars}")
    print(f"  ✅ Is French: {is_french}")
    print(f"  Answer: {answer[:200]}...")
    
    if is_french:
        french_answers += 1

print(f"\n" + "="*80)
print(f"RESULT: {french_answers}/{len(tests)} answers in French")
print("="*80)

if french_answers == len(tests):
    print("✅ ALL answers in French - model is working correctly!")
    print("Note: <think> reasoning may be in English (this is normal for Qwen3)")
elif french_answers > 0:
    print("⚠️  PARTIAL: Some answers in French, some in English")
else:
    print("❌ FAIL: No French answers - system prompts not working")
