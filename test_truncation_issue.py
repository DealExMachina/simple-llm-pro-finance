#!/usr/bin/env python3
"""
Debug truncation issue - check full responses
"""
import httpx
import json

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

print("="*80)
print("DEBUGGING TRUNCATION")
print("="*80)

response = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    json={
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "system", "content": "Réponds en français."},
            {"role": "user", "content": "Expliquez le CAC 40. Répondez EN FRANÇAIS."}
        ],
        "max_tokens": 600,
        "temperature": 0.3
    },
    timeout=60.0
)

data = response.json()

if "error" in data:
    print(f"❌ Error: {data['error']}")
else:
    choice = data["choices"][0]
    content = choice["message"]["content"]
    finish_reason = choice.get("finish_reason", "unknown")
    usage = data.get("usage", {})
    
    print(f"\n📊 Response Metadata:")
    print(f"  Finish reason: {finish_reason}")
    print(f"  Content length: {len(content)} chars")
    print(f"  Usage: {usage}")
    
    # Check for </think> tag
    has_closing_think = "</think>" in content
    has_opening_think = "<think>" in content
    
    print(f"\n🏷️  Thinking Tags:")
    print(f"  Has <think>: {has_opening_think}")
    print(f"  Has </think>: {has_closing_think}")
    
    if has_opening_think and not has_closing_think:
        print("  ⚠️  WARNING: Reasoning not closed - response was truncated!")
    
    # Extract parts
    if has_closing_think:
        parts = content.split("</think>")
        reasoning = parts[0].replace("<think>", "").strip()
        answer = parts[1].strip() if len(parts) > 1 else ""
        
        print(f"\n📝 Reasoning ({len(reasoning)} chars):")
        print(f"  {reasoning[:200]}...")
        
        print(f"\n💬 Answer ({len(answer)} chars):")
        print(f"  {answer}")
        
        # Check if answer is in French
        if answer:
            is_french = any(c in answer for c in ["é", "è", "à", "ç"]) or " est " in answer.lower() or "le " in answer.lower()
            print(f"\n✅ Answer is in French: {is_french}")
        else:
            print(f"\n❌ Answer is EMPTY!")
    else:
        print(f"\n📄 Full Content (no </think> found):")
        print(content)

