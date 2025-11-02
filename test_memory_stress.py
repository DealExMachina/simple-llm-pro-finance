#!/usr/bin/env python3
"""
Stress test memory management with multiple sequential requests.
Also checks if responses are complete and in French when requested.
"""

import httpx
import json
import time
import sys
from typing import List, Dict, Any

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

def test_memory_stability(num_requests: int = 10):
    """Send multiple requests sequentially to test memory cleanup."""
    print("="*80)
    print(f"MEMORY STRESS TEST - {num_requests} sequential requests")
    print("="*80)
    
    errors = []
    times = []
    token_counts = []
    
    for i in range(1, num_requests + 1):
        print(f"\n[Request {i}/{num_requests}]")
        start_time = time.time()
        
        try:
            response = httpx.post(
                f"{BASE_URL}/v1/chat/completions",
                json={
                    "model": "DragonLLM/qwen3-8b-fin-v1.0",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Question {i}: Calculate compound interest on $5,000 at 4% for 2 years. Show your work."
                        }
                    ],
                    "max_tokens": 250,
                    "temperature": 0.3
                },
                timeout=60.0
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Error: {error_msg}")
                errors.append((i, error_msg))
                continue
            
            data = response.json()
            
            if "error" in data:
                error_msg = data["error"]["message"]
                print(f"❌ API Error: {error_msg}")
                errors.append((i, error_msg))
                
                # Check if it's an OOM error
                if "out of memory" in error_msg.lower() or "cuda" in error_msg.lower():
                    print(f"🚨 MEMORY ERROR DETECTED at request {i}!")
                continue
            
            # Extract response data
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            finish_reason = choice.get("finish_reason", "unknown")
            usage = data.get("usage", {})
            
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            times.append(elapsed)
            token_counts.append(completion_tokens)
            
            # Check if response is complete
            is_complete = finish_reason == "stop"
            is_truncated = finish_reason == "length"
            
            # Check if answer seems complete (doesn't end mid-sentence)
            ends_properly = (
                content.strip().endswith(".") or 
                content.strip().endswith("!") or 
                content.strip().endswith("?") or
                content.strip().endswith("€") or
                content.strip().endswith("$")
            )
            
            print(f"  ✅ Status: {finish_reason}")
            print(f"  ⏱️  Time: {elapsed:.2f}s")
            print(f"  📝 Tokens: {completion_tokens}/{total_tokens}")
            print(f"  📄 Length: {len(content)} chars")
            print(f"  ✅ Complete: {'Yes' if is_complete and ends_properly else 'No'}")
            
            if is_truncated or (not is_complete) or (not ends_properly):
                print(f"  ⚠️  WARNING: Response may be truncated!")
                print(f"     Last 100 chars: ...{content[-100:]}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Error: {error_msg}")
            errors.append((i, error_msg))
        
        # Small delay between requests
        if i < num_requests:
            time.sleep(1)
    
    # Summary
    print("\n" + "="*80)
    print("MEMORY STRESS TEST SUMMARY")
    print("="*80)
    print(f"Total requests: {num_requests}")
    print(f"Successful: {num_requests - len(errors)}")
    print(f"Failed: {len(errors)}")
    
    if errors:
        print("\n❌ Errors:")
        for req_num, error in errors:
            print(f"  Request {req_num}: {error}")
    
    if times:
        print(f"\n📊 Performance:")
        print(f"  Average time: {sum(times)/len(times):.2f}s")
        print(f"  Min time: {min(times):.2f}s")
        print(f"  Max time: {max(times):.2f}s")
        print(f"  Average tokens: {sum(token_counts)/len(token_counts):.0f}")
        
        # Check for memory leaks (increasing response times)
        if len(times) > 3:
            first_half = sum(times[:len(times)//2]) / (len(times)//2)
            second_half = sum(times[len(times)//2:]) / (len(times) - len(times)//2)
            if second_half > first_half * 1.5:
                print(f"  ⚠️  WARNING: Response times increasing ({first_half:.2f}s → {second_half:.2f}s)")
                print(f"     This may indicate memory leak!")
    
    return len(errors) == 0


def test_french_language():
    """Test if French prompts produce French answers."""
    print("\n" + "="*80)
    print("FRENCH LANGUAGE TEST")
    print("="*80)
    
    test_questions = [
        {
            "name": "Simple French question",
            "prompt": "Expliquez brièvement ce qu'est une obligation (bond).",
            "max_tokens": 200
        },
        {
            "name": "French with explicit instruction",
            "prompt": "Expliquez ce qu'est le CAC 40. Répondez UNIQUEMENT en français, sans utiliser d'anglais.",
            "max_tokens": 250
        },
        {
            "name": "French calculation",
            "prompt": "Si j'investis 10 000€ à 5% pendant 3 ans, combien aurai-je? Montrez le calcul. Répondez en français.",
            "max_tokens": 300
        },
        {
            "name": "French finance terms",
            "prompt": "Qu'est-ce qu'une SICAV et comment fonctionne-t-elle? Expliquez en français.",
            "max_tokens": 350
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n[Test {i}/{len(test_questions)}] {test['name']}")
        print(f"Prompt: {test['prompt']}")
        
        try:
            response = httpx.post(
                f"{BASE_URL}/v1/chat/completions",
                json={
                    "model": "DragonLLM/qwen3-8b-fin-v1.0",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Vous êtes un assistant financier expert. Répondez toujours en français."
                        },
                        {
                            "role": "user",
                            "content": test["prompt"]
                        }
                    ],
                    "max_tokens": test["max_tokens"],
                    "temperature": 0.3
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                results.append({"test": test["name"], "status": "error", "error": response.text})
                continue
            
            data = response.json()
            
            if "error" in data:
                print(f"❌ API Error: {data['error']['message']}")
                results.append({"test": test["name"], "status": "error", "error": data["error"]["message"]})
                continue
            
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            finish_reason = choice.get("finish_reason", "unknown")
            
            # Check if answer is in French (simple heuristic)
            # Remove reasoning tags for analysis
            answer_only = content
            if "<think>" in answer_only:
                parts = answer_only.split("</think>")
                if len(parts) > 1:
                    answer_only = parts[-1].strip()
            
            # Check for French words
            french_indicators = ["est", "sont", "pour", "dans", "avec", "comme", "une", "le", "la", "les", "l'", "c'est", "qu'est", "fonctionne"]
            english_indicators = ["is", "are", "for", "in", "with", "the", "a", "an", "it's", "what's", "works"]
            
            french_count = sum(1 for word in french_indicators if word.lower() in answer_only.lower())
            english_count = sum(1 for word in english_indicators if word.lower() in answer_only.lower())
            
            is_french = french_count > english_count * 2 or french_count > 3
            
            # Check completeness
            is_complete = finish_reason == "stop"
            ends_properly = answer_only.strip().endswith((".", "!", "?", "€", "$", ":"))
            
            print(f"\n📄 Full Response (first 500 chars):")
            print(content[:500] + ("..." if len(content) > 500 else ""))
            
            print(f"\n📄 Answer Only (after reasoning):")
            print(answer_only[:400] + ("..." if len(answer_only) > 400 else ""))
            
            print(f"\n📊 Analysis:")
            print(f"  Finish reason: {finish_reason}")
            print(f"  French words found: {french_count}")
            print(f"  English words found: {english_count}")
            print(f"  Is French: {'✅ Yes' if is_french else '❌ No'}")
            print(f"  Is complete: {'✅ Yes' if is_complete and ends_properly else '❌ No'}")
            
            if not is_french:
                print(f"  ⚠️  WARNING: Answer appears to be in English!")
            
            results.append({
                "test": test["name"],
                "status": "success" if is_french and is_complete else "partial",
                "is_french": is_french,
                "is_complete": is_complete,
                "content": content,
                "answer_only": answer_only
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({"test": test["name"], "status": "error", "error": str(e)})
    
    # Summary
    print("\n" + "="*80)
    print("FRENCH LANGUAGE TEST SUMMARY")
    print("="*80)
    
    french_count = sum(1 for r in results if r.get("is_french", False))
    complete_count = sum(1 for r in results if r.get("is_complete", False))
    
    print(f"Total tests: {len(results)}")
    print(f"French answers: {french_count}/{len(results)}")
    print(f"Complete answers: {complete_count}/{len(results)}")
    
    if french_count < len(results):
        print("\n❌ Some answers are not in French!")
    
    return french_count == len(results) and complete_count == len(results)


if __name__ == "__main__":
    print("Starting comprehensive tests...\n")
    
    # Test memory stability
    memory_ok = test_memory_stability(num_requests=15)
    
    # Test French language
    french_ok = test_french_language()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Memory management: {'✅ PASS' if memory_ok else '❌ FAIL'}")
    print(f"French language: {'✅ PASS' if french_ok else '❌ FAIL'}")
    
    sys.exit(0 if (memory_ok and french_ok) else 1)

