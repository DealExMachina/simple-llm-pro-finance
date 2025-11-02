#!/usr/bin/env python3
"""
Test the Hugging Face Space API to verify the refactored code works.
"""

import os
import sys
import asyncio
import httpx
from typing import Dict, Any

# Space URL - update this if your Space has a different URL
SPACE_URL = os.getenv("SPACE_URL", "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1")
API_KEY = os.getenv("SERVICE_API_KEY")


async def test_endpoint(client: httpx.AsyncClient, name: str, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Test a single API endpoint."""
    try:
        headers = kwargs.pop("headers", {})
        if API_KEY:
            headers["x-api-key"] = API_KEY
        
        if method.upper() == "GET":
            response = await client.get(url, headers=headers, timeout=30.0)
        elif method.upper() == "POST":
            response = await client.post(url, headers=headers, timeout=120.0, **kwargs)
        else:
            return {"name": name, "success": False, "error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return {
            "name": name,
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200],
        }
    except Exception as e:
        return {
            "name": name,
            "success": False,
            "error": str(e),
        }


async def main():
    """Run API tests."""
    print("=" * 70)
    print("Testing Hugging Face Space API")
    print("=" * 70)
    print(f"Space URL: {SPACE_URL}")
    print()
    
    async with httpx.AsyncClient() as client:
        results = []
        
        # Test 1: Root endpoint
        print("[1/4] Testing root endpoint...")
        result = await test_endpoint(client, "Root", "GET", SPACE_URL.replace("/v1", ""))
        results.append(result)
        if result["success"]:
            print(f"  ✓ Success: {result.get('data', {}).get('status', 'ok')}")
        else:
            print(f"  ✗ Failed: {result['error']}")
        print()
        
        # Test 2: List models
        print("[2/4] Testing /v1/models endpoint...")
        result = await test_endpoint(client, "List Models", "GET", f"{SPACE_URL}/models")
        results.append(result)
        if result["success"]:
            models = result.get("data", {}).get("data", [])
            print(f"  ✓ Success: Found {len(models)} model(s)")
            if models:
                print(f"    Model: {models[0].get('id', 'unknown')}")
        else:
            print(f"  ✗ Failed: {result['error']}")
        print()
        
        # Test 3: Chat completion (simple)
        print("[3/4] Testing /v1/chat/completions endpoint...")
        result = await test_endpoint(
            client,
            "Chat Completion",
            "POST",
            f"{SPACE_URL}/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": "What is compound interest? Answer in one sentence."}],
                "temperature": 0.7,
                "max_tokens": 100,
            }
        )
        results.append(result)
        if result["success"]:
            data = result.get("data", {})
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            tokens = data.get("usage", {}).get("total_tokens", 0)
            print(f"  ✓ Success: Generated {tokens} tokens")
            print(f"    Response preview: {content[:100]}...")
        else:
            print(f"  ✗ Failed: {result['error']}")
        print()
        
        # Test 4: Model reload endpoint
        print("[4/4] Testing /v1/models/reload endpoint...")
        result = await test_endpoint(
            client,
            "Model Reload",
            "POST",
            f"{SPACE_URL}/models/reload",
            params={"force": False}
        )
        results.append(result)
        if result["success"]:
            data = result.get("data", {})
            print(f"  ✓ Success: {data.get('message', 'OK')}")
        else:
            print(f"  ✗ Failed: {result['error']}")
        print()
        
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(1 for r in results if r["success"])
    print(f"Passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("✓ All tests passed! The Space is working correctly.")
        return 0
    else:
        print("✗ Some tests failed")
        for r in results:
            if not r["success"]:
                print(f"  - {r['name']}: {r['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

