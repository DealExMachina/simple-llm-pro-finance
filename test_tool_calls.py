#!/usr/bin/env python3
"""
Test script to verify tool calls functionality in the OpenAI-compatible API.

This script tests:
1. Tool calls are accepted in requests
2. Tools are formatted correctly in prompts
3. Tool calls are parsed from responses
4. Tool calls are returned in the correct format
"""

import json
import requests
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"  # Hugging Face Space
API_KEY = "not-needed"  # No authentication required


def test_tool_calls_basic():
    """Test basic tool calls functionality."""
    print("=" * 60)
    print("Test 1: Basic Tool Calls")
    print("=" * 60)
    
    # Define a simple calculator tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculer_valeur_future",
                "description": "Calcule la valeur future d'un investissement avec intérêts composés",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "capital_initial": {
                            "type": "number",
                            "description": "Le montant initial investi"
                        },
                        "taux_annuel": {
                            "type": "number",
                            "description": "Le taux d'intérêt annuel (en décimal, ex: 0.05 pour 5%)"
                        },
                        "annees": {
                            "type": "number",
                            "description": "Le nombre d'années"
                        }
                    },
                    "required": ["capital_initial", "taux_annuel", "annees"]
                }
            }
        }
    ]
    
    # Make request with tools
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {
                "role": "user",
                "content": "Calcule la valeur future de 10000 euros investis à 5% par an pendant 10 ans."
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=120
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return False
        
        data = response.json()
        print(f"\n📥 Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Check if tool_calls are present
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")
        
        if tool_calls:
            print(f"\n✅ Tool calls found: {len(tool_calls)}")
            for i, tool_call in enumerate(tool_calls, 1):
                print(f"\n  Tool Call {i}:")
                print(f"    ID: {tool_call.get('id')}")
                print(f"    Type: {tool_call.get('type')}")
                func = tool_call.get("function", {})
                print(f"    Function: {func.get('name')}")
                print(f"    Arguments: {func.get('arguments')}")
            return True
        else:
            print("\n⚠️  No tool calls found in response")
            print(f"   Content: {message.get('content', '')[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_calls_multiple():
    """Test multiple tool calls."""
    print("\n" + "=" * 60)
    print("Test 2: Multiple Tool Calls")
    print("=" * 60)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculer_valeur_future",
                "description": "Calcule la valeur future d'un investissement",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "capital_initial": {"type": "number"},
                        "taux_annuel": {"type": "number"},
                        "annees": {"type": "number"}
                    },
                    "required": ["capital_initial", "taux_annuel", "annees"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculer_paiement_mensuel",
                "description": "Calcule le paiement mensuel d'un prêt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "montant": {"type": "number"},
                        "taux_annuel": {"type": "number"},
                        "duree_annees": {"type": "number"}
                    },
                    "required": ["montant", "taux_annuel", "duree_annees"]
                }
            }
        }
    ]
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {
                "role": "user",
                "content": "Calcule la valeur future de 5000 euros à 4% sur 5 ans, puis le paiement mensuel d'un prêt de 200000 euros à 3% sur 20 ans."
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    print(f"\n📤 Request with {len(tools)} tools")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return False
        
        data = response.json()
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")
        
        if tool_calls:
            print(f"\n✅ Found {len(tool_calls)} tool calls")
            return True
        else:
            print("\n⚠️  No tool calls found")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_tool_calls_format():
    """Test that tool calls are in the correct format."""
    print("\n" + "=" * 60)
    print("Test 3: Tool Calls Format Validation")
    print("=" * 60)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {
                "role": "user",
                "content": "Quel est le temps à Paris?"
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 300
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return False
        
        data = response.json()
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")
        
        if tool_calls:
            # Validate format
            for tool_call in tool_calls:
                required_fields = ["id", "type", "function"]
                for field in required_fields:
                    if field not in tool_call:
                        print(f"❌ Missing required field: {field}")
                        return False
                
                func = tool_call.get("function", {})
                if "name" not in func or "arguments" not in func:
                    print(f"❌ Missing function fields: {func}")
                    return False
                
                # Try to parse arguments as JSON
                try:
                    args = json.loads(func["arguments"])
                    print(f"✅ Tool call format valid: {tool_call['function']['name']}")
                except json.JSONDecodeError:
                    print(f"⚠️  Arguments not valid JSON: {func['arguments']}")
            
            return True
        else:
            print("⚠️  No tool calls to validate")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Tool Calls Test Suite")
    print("=" * 60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Make sure the server is running!\n")
    
    # Check if server is up
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"⚠️  Server health check returned: {health.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running at", BASE_URL)
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Basic Tool Calls", test_tool_calls_basic()))
    results.append(("Multiple Tool Calls", test_tool_calls_multiple()))
    results.append(("Format Validation", test_tool_calls_format()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

