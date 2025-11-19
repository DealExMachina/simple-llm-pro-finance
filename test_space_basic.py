#!/usr/bin/env python3
"""Basic tests for the Hugging Face Space API."""

import requests
import json
import time
from typing import Dict, Any

SPACE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"
API_BASE = f"{SPACE_URL}/v1"

def test_health():
    """Test if the Space is accessible."""
    print("=" * 60)
    print("Test 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{SPACE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_list_models():
    """Test listing available models."""
    print("\n" + "=" * 60)
    print("Test 2: List Models")
    print("=" * 60)
    try:
        response = requests.get(f"{API_BASE}/models", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ List models passed")
            return True
        else:
            print(f"❌ List models failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ List models error: {e}")
        return False

def test_simple_chat():
    """Test basic chat completion."""
    print("\n" + "=" * 60)
    print("Test 3: Simple Chat Completion")
    print("=" * 60)
    try:
        payload = {
            "model": "dragon-llm-open-finance",
            "messages": [
                {"role": "user", "content": "Bonjour, dis-moi simplement 'test réussi'"}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        print(f"Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            timeout=120  # Increased timeout for model loading/generation
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"].get("content", "")
                print(f"\n✅ Chat completion passed")
                print(f"Generated text: {content[:100]}...")
                return True
            else:
                print("❌ No choices in response")
                return False
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_choice_required():
    """Test tool_choice='required' (our fix)."""
    print("\n" + "=" * 60)
    print("Test 4: tool_choice='required' (Fix Verification)")
    print("=" * 60)
    try:
        payload = {
            "model": "dragon-llm-open-finance",
            "messages": [
                {"role": "user", "content": "Dis bonjour"}
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "say_hello",
                        "description": "Say hello",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name to greet"
                                }
                            }
                        }
                    }
                }
            ],
            "tool_choice": "required",  # This should not cause 422 error anymore
            "temperature": 0.7,
            "max_tokens": 100
        }
        print(f"Request: tool_choice='required'")
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            timeout=120  # Increased timeout for model loading/generation
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ tool_choice='required' accepted (no 422 error)")
            print(f"Response keys: {list(data.keys())}")
            return True
        elif response.status_code == 422:
            print(f"❌ Still getting 422 error with tool_choice='required'")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ tool_choice test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_format():
    """Test response_format for structured outputs (our fix)."""
    print("\n" + "=" * 60)
    print("Test 5: response_format (Fix Verification)")
    print("=" * 60)
    try:
        payload = {
            "model": "dragon-llm-open-finance",
            "messages": [
                {"role": "user", "content": "Donne-moi un nombre aléatoire entre 1 et 10 au format JSON: {\"nombre\": X}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
            "max_tokens": 50
        }
        print(f"Request: response_format={{'type': 'json_object'}}")
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            timeout=120  # Increased timeout for model loading/generation
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ response_format accepted")
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"].get("content", "")
                print(f"Generated content: {content}")
                # Try to parse as JSON
                try:
                    json.loads(content)
                    print("✅ Response is valid JSON")
                    return True
                except json.JSONDecodeError:
                    print("⚠️  Response format requested but content is not JSON")
                    return False
            return True
        else:
            print(f"❌ response_format test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ response_format test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BASIC SPACE API TESTS")
    print("=" * 60)
    print(f"Testing Space: {SPACE_URL}")
    print(f"API Base: {API_BASE}")
    print()
    
    results = []
    
    # Wait a bit for Space to be ready
    print("Waiting 5 seconds for Space to be ready...")
    time.sleep(5)
    
    results.append(("Health Check", test_health()))
    results.append(("List Models", test_list_models()))
    results.append(("Simple Chat", test_simple_chat()))
    results.append(("tool_choice='required'", test_tool_choice_required()))
    results.append(("response_format", test_response_format()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

