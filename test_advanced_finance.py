#!/usr/bin/env python3
"""
Advanced finance tests including streaming and complex scenarios.
"""

import httpx
import json
import time

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

def test_streaming_response():
    """Test streaming chat completion."""
    print("\n" + "="*80)
    print("TESTING STREAMING RESPONSE")
    print("="*80)
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {
                "role": "user",
                "content": "Explain the Black-Scholes option pricing model in simple terms."
            }
        ],
        "stream": True,
        "max_tokens": 150,
        "temperature": 0.4
    }
    
    print(f"\nQuestion: {payload['messages'][0]['content']}")
    print(f"\nStreaming response:")
    print("─" * 80)
    
    start_time = time.time()
    chunks_received = 0
    full_response = ""
    
    try:
        with httpx.stream(
            "POST",
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60.0
        ) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            print(content, end="", flush=True)
                            full_response += content
                            chunks_received += 1
                    except json.JSONDecodeError:
                        pass
        
        elapsed = time.time() - start_time
        
        print("\n" + "─" * 80)
        print(f"\n✅ Streaming test successful!")
        print(f"   ⏱️  Time: {elapsed:.2f}s")
        print(f"   📦 Chunks received: {chunks_received}")
        print(f"   📝 Total characters: {len(full_response)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_complex_finance_scenario():
    """Test complex multi-step finance reasoning."""
    print("\n" + "="*80)
    print("TESTING COMPLEX FINANCE SCENARIO")
    print("="*80)
    
    question = """A company has the following financials:
- Revenue: $10 million
- Cost of Goods Sold: $4 million
- Operating Expenses: $3 million
- Interest Expense: $500,000
- Tax Rate: 25%

Calculate the company's:
1. Gross Profit Margin
2. Operating Income
3. Net Income
4. EBITDA (assuming $200k depreciation)"""

    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.1,
        "max_tokens": 300
    }
    
    print(f"\nQuestion:\n{question}")
    print("\n" + "─" * 80)
    
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
            
            print(f"\n💬 Answer:\n{answer}")
            print("\n" + "─" * 80)
            print(f"\n✅ Complex scenario test successful!")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   📝 Tokens: {usage.get('total_tokens', 'N/A')}")
            
            # Check for key calculations in response
            calculations = ["gross profit", "operating income", "net income", "ebitda"]
            found = [calc for calc in calculations if calc in answer.lower()]
            print(f"   🎯 Calculations mentioned: {len(found)}/{len(calculations)}")
            
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_financial_advice():
    """Test investment advice generation."""
    print("\n" + "="*80)
    print("TESTING FINANCIAL ADVICE")
    print("="*80)
    
    question = """I'm 30 years old with $50,000 to invest. My risk tolerance is moderate, 
and I'm investing for retirement in 35 years. What asset allocation would you recommend?"""

    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.5,
        "max_tokens": 250
    }
    
    print(f"\nQuestion: {question}")
    print("\n" + "─" * 80)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            
            print(f"\n💬 Answer:\n{answer}")
            print("\n" + "─" * 80)
            print(f"\n✅ Financial advice test successful!")
            
            # Check for relevant concepts
            concepts = ["stocks", "bonds", "diversification", "allocation", "risk"]
            found = [c for c in concepts if c in answer.lower()]
            print(f"   🎯 Relevant concepts: {', '.join(found)}")
            
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_market_interpretation():
    """Test market data interpretation."""
    print("\n" + "="*80)
    print("TESTING MARKET DATA INTERPRETATION")
    print("="*80)
    
    question = """A stock has the following characteristics:
- Current Price: $100
- 52-week High: $120
- 52-week Low: $75
- P/E Ratio: 25
- Beta: 1.5
- Dividend Yield: 2%

What does this data tell you about the stock's risk and valuation?"""

    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.3,
        "max_tokens": 250
    }
    
    print(f"\nQuestion:\n{question}")
    print("\n" + "─" * 80)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            
            print(f"\n💬 Answer:\n{answer}")
            print("\n" + "─" * 80)
            print(f"\n✅ Market interpretation test successful!")
            
            # Check for key concepts
            concepts = ["beta", "p/e", "volatility", "risk", "valuation"]
            found = [c for c in concepts if c in answer.lower()]
            print(f"   🎯 Key concepts addressed: {', '.join(found)}")
            
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all advanced tests."""
    print("="*80)
    print("ADVANCED FINANCE LLM TESTING")
    print("="*80)
    print(f"Target: {BASE_URL}")
    
    results = []
    
    # Test 1: Streaming
    results.append(("Streaming Response", test_streaming_response()))
    time.sleep(2)
    
    # Test 2: Complex scenario
    results.append(("Complex Finance Calculations", test_complex_finance_scenario()))
    time.sleep(2)
    
    # Test 3: Financial advice
    results.append(("Investment Advice", test_financial_advice()))
    time.sleep(2)
    
    # Test 4: Market interpretation
    results.append(("Market Data Interpretation", test_market_interpretation()))
    
    # Summary
    print("\n" + "="*80)
    print("ADVANCED TESTS SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

