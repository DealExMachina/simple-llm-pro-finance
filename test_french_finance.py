#!/usr/bin/env python3
"""
Test French finance queries against the OpenAI-compatible API.
"""

import os
import sys
import asyncio
import httpx
from typing import Dict, Any

# Default API URL (can be overridden with API_URL env var)
API_URL = os.getenv("API_URL", "http://localhost:7860/v1")
API_KEY = os.getenv("SERVICE_API_KEY")

# French finance test questions
FRENCH_QUESTS = [
    {
        "name": "Obligations",
        "question": "Qu'est-ce qu'une obligation?",
        "max_tokens": 400,
    },
    {
        "name": "SICAV",
        "question": "Qu'est-ce qu'une SICAV?",
        "max_tokens": 400,
    },
    {
        "name": "CAC 40",
        "question": "Expliquez le CAC 40",
        "max_tokens": 500,
    },
    {
        "name": "VaR",
        "question": "Qu'est-ce que la Value at Risk (VaR) et comment la calcule-t-on?",
        "max_tokens": 600,
    },
]


async def test_french_query(client: httpx.AsyncClient, test: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single French finance query."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [{"role": "user", "content": test["question"]}],
        "temperature": 0.7,
        "max_tokens": test["max_tokens"],
    }

    try:
        response = await client.post(
            f"{API_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "name": test["name"],
            "success": True,
            "question": test["question"],
            "answer": data["choices"][0]["message"]["content"],
            "finish_reason": data["choices"][0]["finish_reason"],
            "tokens": data["usage"]["completion_tokens"],
            "total_tokens": data["usage"]["total_tokens"],
        }
    except Exception as e:
        return {
            "name": test["name"],
            "success": False,
            "question": test["question"],
            "error": str(e),
        }


async def main():
    """Run all French finance tests."""
    print("=" * 70)
    print("French Finance Test Suite")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print()

    async with httpx.AsyncClient() as client:
        results = []
        for i, test in enumerate(FRENCH_QUESTS, 1):
            print(f"[{i}/{len(FRENCH_QUESTS)}] Testing: {test['name']}")
            print(f"  Question: {test['question']}")
            result = await test_french_query(client, test)
            results.append(result)

            if result["success"]:
                answer_preview = result["answer"][:150] + "..." if len(result["answer"]) > 150 else result["answer"]
                print(f"  ✓ Success")
                print(f"  Finish reason: {result['finish_reason']}")
                print(f"  Tokens: {result['tokens']}")
                print(f"  Answer preview: {answer_preview}")
            else:
                print(f"  ✗ Failed: {result['error']}")
            print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    passed = sum(1 for r in results if r["success"])
    print(f"Passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        for r in results:
            if not r["success"]:
                print(f"  - {r['name']}: {r['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

