#!/usr/bin/env python3
"""
Test the deployed finance LLM with various finance-specific questions.
"""

import httpx
import json
import time
from typing import Dict, Any, List

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

# Finance test questions covering different domains
FINANCE_TESTS = [
    {
        "category": "Financial Calculations",
        "question": "If I invest $10,000 at an annual interest rate of 5% compounded annually, how much will I have after 3 years?",
        "expected_topics": ["compound interest", "10000", "5%", "3 years"]
    },
    {
        "category": "Risk Management",
        "question": "What is Value at Risk (VaR) and how is it used in portfolio management?",
        "expected_topics": ["VaR", "risk", "portfolio", "loss"]
    },
    {
        "category": "Financial Instruments",
        "question": "Explain the difference between a call option and a put option.",
        "expected_topics": ["call", "put", "option", "buy", "sell"]
    },
    {
        "category": "Market Analysis",
        "question": "What factors typically influence stock market volatility?",
        "expected_topics": ["volatility", "market", "uncertainty", "factors"]
    },
    {
        "category": "Corporate Finance",
        "question": "What is the difference between EBITDA and net income?",
        "expected_topics": ["EBITDA", "net income", "earnings", "depreciation"]
    },
    {
        "category": "Investment Strategy",
        "question": "What is diversification and why is it important in investing?",
        "expected_topics": ["diversification", "risk", "portfolio", "assets"]
    },
    {
        "category": "Financial Ratios",
        "question": "How do you calculate and interpret the Price-to-Earnings (P/E) ratio?",
        "expected_topics": ["P/E", "price", "earnings", "ratio", "valuation"]
    },
    {
        "category": "Fixed Income",
        "question": "What happens to bond prices when interest rates rise?",
        "expected_topics": ["bond", "interest rate", "price", "inverse"]
    },
]

def test_endpoint_availability():
    """Test if the endpoint is available."""
    print("\n" + "="*80)
    print("TESTING ENDPOINT AVAILABILITY")
    print("="*80)
    
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=30.0)
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Backend: {data.get('backend')}")
        print(f"✅ Model: {data.get('model')}")
        print(f"✅ Service: {data.get('service')}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_models_endpoint():
    """Test the /v1/models endpoint."""
    print("\n" + "="*80)
    print("TESTING MODELS ENDPOINT")
    print("="*80)
    
    try:
        response = httpx.get(f"{BASE_URL}/v1/models", timeout=30.0)
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Available models: {len(data.get('data', []))}")
        for model in data.get('data', []):
            print(f"   - {model.get('id')}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_finance_test(test: Dict[str, Any], max_tokens: int = 200) -> Dict[str, Any]:
    """Run a single finance test question."""
    print(f"\n{'─'*80}")
    print(f"Category: {test['category']}")
    print(f"Question: {test['question']}")
    print(f"{'─'*80}")
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": test["question"]}
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens
    }
    
    start_time = time.time()
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60.0
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            print(f"\n📊 Response Stats:")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   📝 Tokens: {usage.get('total_tokens', 'N/A')} "
                  f"(prompt: {usage.get('prompt_tokens', 'N/A')}, "
                  f"completion: {usage.get('completion_tokens', 'N/A')})")
            
            print(f"\n💬 Answer:\n{answer}")
            
            # Check if expected topics are mentioned
            answer_lower = answer.lower()
            topics_found = [topic for topic in test.get('expected_topics', []) 
                          if topic.lower() in answer_lower]
            
            if topics_found:
                print(f"\n✅ Relevant topics found: {', '.join(topics_found)}")
            
            return {
                "success": True,
                "category": test['category'],
                "time": elapsed,
                "tokens": usage.get('total_tokens', 0),
                "topics_found": len(topics_found),
                "topics_expected": len(test.get('expected_topics', []))
            }
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   {response.text}")
            return {
                "success": False,
                "category": test['category'],
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return {
            "success": False,
            "category": test['category'],
            "error": str(e)
        }

def print_summary(results: List[Dict[str, Any]]):
    """Print test summary."""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        avg_tokens = sum(r['tokens'] for r in successful) / len(successful)
        total_topics = sum(r['topics_found'] for r in successful)
        expected_topics = sum(r['topics_expected'] for r in successful)
        
        print(f"\n📊 Performance Metrics:")
        print(f"   ⏱️  Average response time: {avg_time:.2f}s")
        print(f"   📝 Average tokens: {avg_tokens:.0f}")
        print(f"   🎯 Topic coverage: {total_topics}/{expected_topics} "
              f"({100*total_topics/expected_topics if expected_topics > 0 else 0:.1f}%)")
    
    if failed:
        print(f"\n❌ Failed Tests:")
        for r in failed:
            print(f"   - {r['category']}: {r.get('error', 'Unknown error')}")

def main():
    """Run all finance tests."""
    print("="*80)
    print("FINANCE LLM TESTING SUITE")
    print("="*80)
    print(f"Target: {BASE_URL}")
    print(f"Total tests: {len(FINANCE_TESTS)}")
    
    # Test endpoint availability
    if not test_endpoint_availability():
        print("\n❌ Endpoint not available. Exiting.")
        return
    
    # Test models endpoint
    if not test_models_endpoint():
        print("\n⚠️  Models endpoint not available, but continuing...")
    
    # Run finance tests
    print("\n" + "="*80)
    print("RUNNING FINANCE TESTS")
    print("="*80)
    
    results = []
    for i, test in enumerate(FINANCE_TESTS, 1):
        print(f"\n[Test {i}/{len(FINANCE_TESTS)}]")
        result = run_finance_test(test)
        results.append(result)
        
        # Small delay between requests
        if i < len(FINANCE_TESTS):
            time.sleep(1)
    
    # Print summary
    print_summary(results)
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

