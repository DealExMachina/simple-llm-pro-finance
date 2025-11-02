#!/usr/bin/env python3
"""
Comprehensive test to verify all bug fixes:
1. No OOM errors
2. No race conditions (sequential requests work)
3. French language support works
4. Answers are complete (not truncated)
"""

import httpx
import json
import time
import sys

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

def test_basic_functionality():
    """Test 1: Basic request doesn't cause OOM"""
    print("\n" + "="*80)
    print("TEST 1: Basic Functionality (No OOM)")
    print("="*80)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": "What is 2+2? Explain briefly."}],
                "max_tokens": 150,
                "temperature": 0.3
            },
            timeout=60.0
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        if "error" in data:
            print(f"❌ FAIL: {data['error']['message']}")
            return False
        
        content = data["choices"][0]["message"]["content"]
        print(f"✅ PASS: Got response")
        print(f"Response: {content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_sequential_requests():
    """Test 2: Sequential requests don't cause OOM or race conditions"""
    print("\n" + "="*80)
    print("TEST 2: Sequential Requests (5 requests)")
    print("="*80)
    
    success_count = 0
    for i in range(1, 6):
        print(f"\n[Request {i}/5]")
        try:
            start = time.time()
            response = httpx.post(
                f"{BASE_URL}/v1/chat/completions",
                json={
                    "model": "DragonLLM/qwen3-8b-fin-v1.0",
                    "messages": [{"role": "user", "content": f"Calculate {i} + {i}. Show your work."}],
                    "max_tokens": 200,
                    "temperature": 0.3
                },
                timeout=60.0
            )
            elapsed = time.time() - start
            
            if response.status_code != 200:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}")
                continue
            
            data = response.json()
            if "error" in data:
                error_msg = data["error"]["message"]
                print(f"  ❌ Error: {error_msg[:100]}")
                if "out of memory" in error_msg.lower():
                    print("  🚨 OOM ERROR DETECTED!")
                continue
            
            content = data["choices"][0]["message"]["content"]
            finish_reason = data["choices"][0].get("finish_reason", "unknown")
            
            print(f"  ✅ Success ({elapsed:.1f}s, finish: {finish_reason})")
            print(f"  Response: {content[:100]}...")
            success_count += 1
            
            time.sleep(2)  # Small delay between requests
            
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    print(f"\n✅ Passed {success_count}/5 requests")
    return success_count >= 4  # Allow 1 failure


def test_french_language():
    """Test 3: French language support"""
    print("\n" + "="*80)
    print("TEST 3: French Language Support")
    print("="*80)
    
    test_questions = [
        "Expliquez brièvement ce qu'est une obligation.",
        "Qu'est-ce que le CAC 40? Répondez en français.",
        "Si j'investis 5000€ à 4% pendant 2 ans, combien aurai-je?"
    ]
    
    french_count = 0
    for i, question in enumerate(test_questions, 1):
        print(f"\n[Test {i}/3]: {question[:50]}...")
        
        try:
            response = httpx.post(
                f"{BASE_URL}/v1/chat/completions",
                json={
                    "model": "DragonLLM/qwen3-8b-fin-v1.0",
                    "messages": [{"role": "user", "content": question}],
                    "max_tokens": 300,
                    "temperature": 0.3
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                print(f"  ❌ HTTP {response.status_code}")
                continue
            
            data = response.json()
            if "error" in data:
                print(f"  ❌ Error: {data['error']['message'][:100]}")
                continue
            
            content = data["choices"][0]["message"]["content"]
            
            # Extract answer after <think> tags
            answer = content
            if "</think>" in answer:
                answer = answer.split("</think>")[-1].strip()
            
            # Check if answer is in French
            french_indicators = ["est", "sont", "une", "le", "la", "les", "c'est", "qu'", "l'"]
            french_found = sum(1 for word in french_indicators if f" {word} " in answer.lower() or answer.lower().startswith(f"{word} "))
            
            is_french = french_found >= 3
            
            print(f"  Answer (first 200 chars): {answer[:200]}...")
            print(f"  French indicators found: {french_found}")
            print(f"  ✅ Is French: {is_french}")
            
            if is_french:
                french_count += 1
            
            time.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    print(f"\n✅ {french_count}/3 answers in French")
    return french_count >= 2


def test_complete_answers():
    """Test 4: Answers are complete (not truncated)"""
    print("\n" + "="*80)
    print("TEST 4: Complete Answers (No Truncation)")
    print("="*80)
    
    question = "Explain the Black-Scholes option pricing model, including its key assumptions and main formula components. Be thorough."
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": question}],
                "max_tokens": 600,  # Higher limit for complete answer
                "temperature": 0.3
            },
            timeout=60.0
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
        
        data = response.json()
        if "error" in data:
            print(f"❌ FAIL: {data['error']['message']}")
            return False
        
        content = data["choices"][0]["message"]["content"]
        finish_reason = data["choices"][0].get("finish_reason", "unknown")
        
        # Check if answer ends properly
        ends_properly = content.strip().endswith((".", "!", "?"))
        is_complete = finish_reason == "stop"
        
        print(f"Finish reason: {finish_reason}")
        print(f"Length: {len(content)} chars")
        print(f"Ends properly: {ends_properly}")
        print(f"\nLast 200 chars:\n{content[-200:]}")
        
        if is_complete and ends_properly:
            print(f"\n✅ PASS: Answer is complete")
            return True
        else:
            print(f"\n⚠️  WARNING: Answer may be truncated")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("COMPREHENSIVE BUG FIX VERIFICATION")
    print("="*80)
    
    results = {}
    
    # Run all tests
    results["basic"] = test_basic_functionality()
    results["sequential"] = test_sequential_requests()
    results["french"] = test_french_language()
    results["complete"] = test_complete_answers()
    
    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"1. Basic Functionality: {'✅ PASS' if results['basic'] else '❌ FAIL'}")
    print(f"2. Sequential Requests: {'✅ PASS' if results['sequential'] else '❌ FAIL'}")
    print(f"3. French Language: {'✅ PASS' if results['french'] else '❌ FAIL'}")
    print(f"4. Complete Answers: {'✅ PASS' if results['complete'] else '❌ FAIL'}")
    
    all_pass = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")
    
    sys.exit(0 if all_pass else 1)

