#!/usr/bin/env python3
"""Quick test of Space API"""
import httpx
import sys

SPACE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

try:
    # Test root endpoint
    r = httpx.get(f"{SPACE_URL}/", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Root endpoint: {data.get('backend', 'unknown')}")
        print(f"  Model: {data.get('model', 'unknown')}")
    else:
        print(f"✗ Root endpoint failed: {r.status_code}")
        sys.exit(1)
    
    # Test models endpoint
    r = httpx.get(f"{SPACE_URL}/v1/models", timeout=10)
    if r.status_code == 200:
        data = r.json()
        models = data.get('data', [])
        print(f"✓ Models endpoint: {len(models)} model(s)")
    else:
        print(f"✗ Models endpoint failed: {r.status_code}")
        sys.exit(1)
    
    # Test chat completion (short)
    r = httpx.post(
        f"{SPACE_URL}/v1/chat/completions",
        json={
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 50
        },
        timeout=60
    )
    if r.status_code == 200:
        data = r.json()
        content = data['choices'][0]['message']['content']
        print(f"✓ Chat completion: {len(content)} chars")
        print(f"  Preview: {content[:50]}...")
    else:
        print(f"✗ Chat completion failed: {r.status_code}")
        print(f"  Response: {r.text[:200]}")
        sys.exit(1)
    
    print("\n✓ All tests passed! Space is working.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

