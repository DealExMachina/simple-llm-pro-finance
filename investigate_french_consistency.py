#!/usr/bin/env python3
"""
Deep investigation: Why does the model sometimes respond in English?
"""
import httpx
import json
import time

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

# Same question, different approaches
question = "Qu'est-ce que le CAC 40?"

tests = [
    {
        "name": "1. No system prompt",
        "messages": [
            {"role": "user", "content": question}
        ]
    },
    {
        "name": "2. French system prompt (generic)",
        "messages": [
            {"role": "system", "content": "Réponds en français."},
            {"role": "user", "content": question}
        ]
    },
    {
        "name": "3. French system prompt (financial context)",
        "messages": [
            {"role": "system", "content": "Tu es un expert financier français. Réponds toujours en français."},
            {"role": "user", "content": question}
        ]
    },
    {
        "name": "4. User message includes language instruction",
        "messages": [
            {"role": "user", "content": f"{question} Réponds en français."}
        ]
    },
    {
        "name": "5. Strong French enforcement in system",
        "messages": [
            {"role": "system", "content": "You are a French financial expert. You MUST respond ONLY in French. Never use English. Toujours répondre en français uniquement."},
            {"role": "user", "content": question}
        ]
    },
    {
        "name": "6. Check if English question gets English",
        "messages": [
            {"role": "user", "content": "What is the CAC 40?"}
        ]
    },
    {
        "name": "7. English question with French system prompt",
        "messages": [
            {"role": "system", "content": "Réponds toujours en français."},
            {"role": "user", "content": "What is the CAC 40?"}
        ]
    }
]

print("="*80)
print("FRENCH CONSISTENCY INVESTIGATION")
print("="*80)

results = []

for test in tests:
    print(f"\n{test['name']}")
    print("-" * 80)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": test["messages"],
                "max_tokens": 400,
                "temperature": 0.3
            },
            timeout=60.0
        )
        
        data = response.json()
        if "error" in data:
            print(f"❌ Error: {data['error']['message'][:100]}")
            results.append({"test": test['name'], "french": False, "error": True})
            continue
        
        content = data["choices"][0]["message"]["content"]
        
        # Extract answer after </think>
        if "</think>" in content:
            answer = content.split("</think>")[1].strip()
        else:
            answer = content
        
        # Check if French
        french_indicators = {
            "chars": any(c in answer for c in ["é", "è", "ê", "à", "ç", "ù"]),
            "words": any(w in answer.lower() for w in [" est ", " le ", " la ", " les ", " une ", " des "]),
            "patterns": "cac 40" in answer.lower() and ("indice" in answer.lower() or "index" not in answer.lower())
        }
        
        is_french = french_indicators["chars"] or (french_indicators["words"] and french_indicators["patterns"])
        
        print(f"First 200 chars of answer: {answer[:200]}...")
        print(f"French indicators: {french_indicators}")
        print(f"{'✅ FRENCH' if is_french else '❌ ENGLISH'}")
        
        results.append({
            "test": test['name'],
            "french": is_french,
            "has_french_chars": french_indicators["chars"],
            "answer_preview": answer[:100]
        })
        
        time.sleep(2)  # Rate limiting
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        results.append({"test": test['name'], "french": False, "error": True})

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
french_count = sum(1 for r in results if r.get("french"))
total = len(results)
print(f"French responses: {french_count}/{total}")

for r in results:
    status = "✅" if r.get("french") else "❌"
    print(f"{status} {r['test']}")

if french_count == 0:
    print("\n🚨 CRITICAL: Model NEVER responds in French!")
    print("   → Model may not be French-capable or wrong model loaded")
elif french_count < total * 0.8:
    print(f"\n⚠️  INCONSISTENT: Only {french_count}/{total} in French")
    print("   → System prompts not being followed properly")
else:
    print(f"\n✅ GOOD: {french_count}/{total} in French")

