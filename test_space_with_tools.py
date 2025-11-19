#!/usr/bin/env python3
"""Test Space API with tool calls and JSON format."""

import requests
import json
import time
from typing import Dict, Any

SPACE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"
API_BASE = f"{SPACE_URL}/v1"

def test_tool_calls():
    """Test tool calls functionality."""
    print("=" * 60)
    print("Test: Tool Calls")
    print("=" * 60)
    try:
        payload = {
            "model": "dragon-llm-open-finance",
            "messages": [
                {
                    "role": "user",
                    "content": "Calcule la valeur future de 10000€ à 5% sur 10 ans en utilisant l'outil calculer_valeur_future"
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "calculer_valeur_future",
                        "description": "Calcule la valeur future d'un capital avec intérêts composés",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "capital_initial": {
                                    "type": "number",
                                    "description": "Capital initial en euros"
                                },
                                "taux": {
                                    "type": "number",
                                    "description": "Taux d'intérêt annuel (ex: 0.05 pour 5%)"
                                },
                                "duree": {
                                    "type": "number",
                                    "description": "Durée en années"
                                }
                            },
                            "required": ["capital_initial", "taux", "duree"]
                        }
                    }
                }
            ],
            "tool_choice": "auto",
            "temperature": 0.7,
            "max_tokens": 200
        }
        print(f"Request: tool_choice='auto', tools provided")
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            timeout=120
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tool calls request accepted")
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0]["message"]
                if "tool_calls" in message and message["tool_calls"]:
                    print(f"✅ Tool calls found: {len(message['tool_calls'])}")
                    for i, tool_call in enumerate(message["tool_calls"]):
                        print(f"  Tool call {i+1}:")
                        print(f"    ID: {tool_call.get('id', 'N/A')}")
                        print(f"    Function: {tool_call.get('function', {}).get('name', 'N/A')}")
                        print(f"    Arguments: {tool_call.get('function', {}).get('arguments', 'N/A')[:100]}...")
                    return True
                else:
                    print(f"⚠️  No tool_calls in response")
                    print(f"   Content: {message.get('content', '')[:200]}...")
                    return False
            return True
        else:
            print(f"❌ Tool calls test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Tool calls test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_choice_required():
    """Test tool_choice='required' with tools."""
    print("\n" + "=" * 60)
    print("Test: tool_choice='required' with Tools")
    print("=" * 60)
    try:
        payload = {
            "model": "dragon-llm-open-finance",
            "messages": [
                {
                    "role": "user",
                    "content": "Utilise l'outil pour calculer 10000€ à 5% sur 10 ans"
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "calculer_valeur_future",
                        "description": "Calcule la valeur future",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "capital_initial": {"type": "number"},
                                "taux": {"type": "number"},
                                "duree": {"type": "number"}
                            },
                            "required": ["capital_initial", "taux", "duree"]
                        }
                    }
                }
            ],
            "tool_choice": "required",  # This should not cause 422 error
            "temperature": 0.7,
            "max_tokens": 200
        }
        print(f"Request: tool_choice='required'")
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            timeout=120
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ tool_choice='required' accepted (no 422 error)")
            return True
        elif response.status_code == 422:
            print(f"❌ Still getting 422 error with tool_choice='required'")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_response_format_json():
    """Test response_format with JSON output."""
    print("\n" + "=" * 60)
    print("Test: response_format JSON")
    print("=" * 60)
    try:
        payload = {
            "model": "dragon-llm-open-finance",
            "messages": [
                {
                    "role": "user",
                    "content": "Donne-moi un nombre aléatoire entre 1 et 10 au format JSON avec la clé 'nombre'"
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
            "max_tokens": 100
        }
        print(f"Request: response_format={{'type': 'json_object'}}")
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            timeout=120
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ response_format accepted")
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"].get("content", "")
                print(f"Generated content (first 200 chars): {content[:200]}")
                
                # Try to parse as JSON
                try:
                    # Remove reasoning tags if present
                    cleaned = content
                    if "<think>" in cleaned.lower():
                        # Try to extract JSON after reasoning
                        if "}" in cleaned:
                            brace_pos = cleaned.find('{')
                            if brace_pos != -1:
                                cleaned = cleaned[brace_pos:]
                    
                    json_data = json.loads(cleaned)
                    print(f"✅ Response is valid JSON: {json_data}")
                    return True
                except json.JSONDecodeError as e:
                    print(f"⚠️  Response is not valid JSON: {e}")
                    print(f"   Full content: {content[:500]}")
                    return False
            return True
        else:
            print(f"❌ response_format test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SPACE API TESTS - TOOLS AND JSON FORMAT")
    print("=" * 60)
    print(f"Testing Space: {SPACE_URL}")
    print()
    
    results = []
    
    results.append(("Tool Calls (auto)", test_tool_calls()))
    results.append(("tool_choice='required'", test_tool_choice_required()))
    results.append(("response_format JSON", test_response_format_json()))
    
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
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

