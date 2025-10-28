#!/usr/bin/env python3
"""
Quick test script to verify the PRIIPs LLM Service is working
Run with: python test_service.py
"""
import httpx
import json
import time
import os
from huggingface_hub import get_token

BASE_URL = "https://jeanbaptdzd-priips-llm-service.hf.space"

# Get HF token for private Space access
HF_TOKEN = get_token()
if not HF_TOKEN:
    print("⚠️  Warning: No HF token found. Private Space access may fail.")
    print("   Run: huggingface-cli login")

def test_endpoint(name, method, url, json_data=None, timeout=10):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    
    # Add authentication headers for private Space
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    
    try:
        if method == "GET":
            response = httpx.get(url, headers=headers, timeout=timeout)
        else:
            response = httpx.post(url, json=json_data, headers=headers, timeout=timeout)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
                return True
            except:
                print(f"Response (text): {response.text[:200]}")
                return False
        else:
            print(f"Error: {response.text[:200]}")
            return False
            
    except httpx.TimeoutException:
        print(f"❌ Timeout after {timeout}s")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print(f"\n{'#'*60}")
    print("PRIIPs LLM Service - Quick Test Script")
    print(f"Service: {BASE_URL}")
    print(f"{'#'*60}")
    
    results = {}
    
    # Test 1: Root endpoint
    results['root'] = test_endpoint(
        "Root Endpoint",
        "GET",
        f"{BASE_URL}/"
    )
    
    # Test 2: Health endpoint
    results['health'] = test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/health"
    )
    
    # Test 3: List models
    results['models'] = test_endpoint(
        "List Models",
        "GET",
        f"{BASE_URL}/v1/models"
    )
    
    # Test 4: Chat completion (this will load the model - may take 30s-1min first time)
    print("\n" + "="*60)
    print("Testing: Chat Completion (Model Loading)")
    print("="*60)
    print("⚠️  First request will take 30s-1min to load the model...")
    print("    Please wait...")
    
    chat_payload = {
        "model": "DragonLLM/gemma3-12b-fin-v0.3",
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    results['chat'] = test_endpoint(
        "Chat Completion",
        "POST",
        f"{BASE_URL}/v1/chat/completions",
        json_data=chat_payload,
        timeout=120  # Longer timeout for model loading
    )
    
    # Summary
    print(f"\n{'#'*60}")
    print("SUMMARY")
    print(f"{'#'*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Service is fully operational.")
    elif results.get('root') or results.get('health'):
        print("\n⚠️  Service is responding but some endpoints failed.")
        print("   This might be normal if model is still loading.")
    else:
        print("\n❌ Service is not accessible. Check:")
        print("   1. Space is running on HF dashboard")
        print("   2. No firewall/network issues")
        print("   3. Correct URL")


if __name__ == "__main__":
    main()

