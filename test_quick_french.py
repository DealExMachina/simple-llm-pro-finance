#!/usr/bin/env python3
"""Quick test of 3 French finance terms"""
import httpx

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

questions = [
    "Qu'est-ce qu'une main levée d'hypothèque?",
    "Définissez la date de valeur.",
    "Qu'est-ce que l'escompte bancaire?"
]

print("🎯 Test rapide - Termes financiers français\n")

for i, q in enumerate(questions, 1):
    print(f"[{i}] {q}")
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": q}],
                "max_tokens": 400,
                "temperature": 0.3
            },
            timeout=60.0
        )
        
        data = response.json()
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            # Extract answer
            answer = content.split("</think>")[1].strip() if "</think>" in content else content
            print(f"✅ {answer[:200]}...\n")
        else:
            print(f"❌ Error: {data.get('error', 'Unknown')}\n")
    except Exception as e:
        print(f"❌ Exception: {e}\n")
        
print("✅ Test terminé")
