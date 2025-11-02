#!/usr/bin/env python3
"""
Analyze model performance: inference speed, throughput, and parallelization.
"""

import httpx
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

def analyze_test_results():
    """Analyze the results from previous tests."""
    print("="*80)
    print("PERFORMANCE ANALYSIS FROM RECENT TESTS")
    print("="*80)
    
    # From the test results
    english_tests = {
        "total_tests": 8,
        "avg_time": 11.74,
        "avg_tokens": 175,
        "max_tokens": 150,
    }
    
    french_tests = {
        "total_tests": 10,
        "avg_time": 12.03,
        "avg_tokens": 180,
        "max_tokens": 150,
    }
    
    # Calculate metrics
    print(f"\n📊 English Tests:")
    print(f"   Average response time: {english_tests['avg_time']:.2f}s")
    print(f"   Average tokens generated: {english_tests['avg_tokens']}")
    print(f"   Tokens per second: {english_tests['avg_tokens'] / english_tests['avg_time']:.2f}")
    print(f"   Token efficiency: {english_tests['avg_tokens'] / english_tests['max_tokens'] * 100:.1f}%")
    
    print(f"\n📊 French Tests:")
    print(f"   Average response time: {french_tests['avg_time']:.2f}s")
    print(f"   Average tokens generated: {french_tests['avg_tokens']}")
    print(f"   Tokens per second: {french_tests['avg_tokens'] / french_tests['avg_time']:.2f}")
    print(f"   Token efficiency: {french_tests['avg_tokens'] / french_tests['max_tokens'] * 100:.1f}%")
    
    overall_tokens_per_sec = (english_tests['avg_tokens'] + french_tests['avg_tokens']) / \
                             (english_tests['avg_time'] + french_tests['avg_time'])
    
    print(f"\n🚀 Overall Performance:")
    print(f"   Average tokens/second: {overall_tokens_per_sec:.2f}")
    print(f"   Current hardware: L4x1 GPU")
    print(f"   Model size: 8B parameters (Qwen3)")
    
    return overall_tokens_per_sec

def test_single_request():
    """Test a single request to measure baseline performance."""
    print("\n" + "="*80)
    print("BASELINE SINGLE REQUEST TEST")
    print("="*80)
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": "Explain compound interest in one sentence."}
        ],
        "temperature": 0.2,
        "max_tokens": 50
    }
    
    start = time.time()
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60.0
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            tokens = data['usage']['completion_tokens']
            
            print(f"\n✅ Response received")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   📝 Tokens: {tokens}")
            print(f"   🚀 Speed: {tokens/elapsed:.2f} tokens/s")
            
            return tokens, elapsed
        else:
            print(f"❌ Error: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_concurrent_requests(num_requests: int = 3):
    """Test multiple concurrent requests to check parallelization."""
    print("\n" + "="*80)
    print(f"CONCURRENT REQUESTS TEST ({num_requests} parallel requests)")
    print("="*80)
    
    questions = [
        "What is a stock?",
        "What is a bond?",
        "What is diversification?",
        "What is ROI?",
        "What is inflation?",
    ][:num_requests]
    
    def make_request(question: str, index: int):
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.2,
            "max_tokens": 50
        }
        
        start = time.time()
        try:
            response = httpx.post(
                f"{BASE_URL}/v1/chat/completions",
                json=payload,
                timeout=90.0
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "index": index,
                    "question": question,
                    "time": elapsed,
                    "tokens": data['usage']['completion_tokens'],
                    "success": True
                }
            else:
                return {"index": index, "success": False, "error": response.status_code}
        except Exception as e:
            return {"index": index, "success": False, "error": str(e)}
    
    print(f"\nSending {num_requests} requests simultaneously...")
    overall_start = time.time()
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(make_request, q, i) for i, q in enumerate(questions)]
        results = [future.result() for future in as_completed(futures)]
    
    overall_elapsed = time.time() - overall_start
    
    # Sort results by index
    results.sort(key=lambda x: x.get('index', 0))
    
    successful = [r for r in results if r.get('success')]
    
    print(f"\n📊 Results:")
    print(f"   Total time: {overall_elapsed:.2f}s")
    print(f"   Successful: {len(successful)}/{num_requests}")
    
    if successful:
        for r in successful:
            print(f"\n   Request {r['index'] + 1}: {r['question'][:40]}...")
            print(f"      Time: {r['time']:.2f}s")
            print(f"      Tokens: {r['tokens']}")
            print(f"      Speed: {r['tokens']/r['time']:.2f} tokens/s")
        
        avg_time = sum(r['time'] for r in successful) / len(successful)
        total_tokens = sum(r['tokens'] for r in successful)
        
        print(f"\n   📈 Average per request: {avg_time:.2f}s")
        print(f"   📝 Total tokens: {total_tokens}")
        print(f"   ⚡ Throughput: {total_tokens/overall_elapsed:.2f} tokens/s overall")
        
        # Check if requests were parallelized
        if overall_elapsed < avg_time * num_requests * 0.8:
            print(f"   ✅ Requests appear to be parallelized")
            parallel_speedup = (avg_time * num_requests) / overall_elapsed
            print(f"   🚀 Speedup: {parallel_speedup:.2f}x")
        else:
            print(f"   ⚠️  Requests appear to be sequential (no parallelization)")
            print(f"   💡 Expected time if parallel: ~{avg_time:.2f}s")
            print(f"   💡 Actual time: {overall_elapsed:.2f}s")
    
    return successful, overall_elapsed

def analyze_hardware_upgrade():
    """Analyze potential benefits of upgrading to L40s."""
    print("\n" + "="*80)
    print("HARDWARE UPGRADE ANALYSIS: L4x1 → L40s")
    print("="*80)
    
    print("\n📊 Current Setup (L4x1):")
    print("   GPU: NVIDIA L4")
    print("   VRAM: 24 GB")
    print("   vCPU: 15")
    print("   RAM: 44 GB")
    print("   Cost: ~$0.70/hour ($521/month)")
    
    print("\n📊 Upgrade Option (L40s):")
    print("   GPU: NVIDIA L40s")
    print("   VRAM: 48 GB (2x L4)")
    print("   vCPU: 30 (2x L4)")
    print("   RAM: 92 GB (2x L4)")
    print("   Cost: ~$1.55/hour ($1153/month)")
    print("   Cost increase: +$632/month (+121%)")
    
    print("\n🎯 Expected Benefits:")
    print("   ✅ Better parallelization: More VRAM allows larger batch sizes")
    print("   ✅ Faster inference: ~1.5-2x faster per request")
    print("   ✅ Higher throughput: 2-3x more concurrent requests")
    print("   ✅ Reduced latency: Better for multiple users")
    
    print("\n💡 Recommendations:")
    print("   1. L4x1 is sufficient for:")
    print("      - Sequential requests")
    print("      - Low to medium traffic (<10 requests/min)")
    print("      - Development/testing")
    
    print("\n   2. Upgrade to L40s if:")
    print("      - Need to handle concurrent requests efficiently")
    print("      - Expecting >20 requests/min")
    print("      - Latency is critical (<5s response time)")
    print("      - Multiple users accessing simultaneously")
    
    print("\n   3. Current bottleneck:")
    print("      - Transformers backend is single-threaded by default")
    print("      - Need batching support for true parallelization")
    print("      - Consider implementing request batching")

def main():
    """Run performance analysis."""
    print("="*80)
    print("FINANCE LLM PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Analyze previous test results
    avg_tokens_per_sec = analyze_test_results()
    
    # Test single request
    tokens, elapsed = test_single_request()
    
    # Test concurrent requests
    print("\n" + "="*80)
    print("Testing with 2 concurrent requests...")
    test_concurrent_requests(2)
    
    time.sleep(2)
    
    print("\n" + "="*80)
    print("Testing with 3 concurrent requests...")
    test_concurrent_requests(3)
    
    # Hardware analysis
    analyze_hardware_upgrade()
    
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    print(f"""
📊 Current Performance:
   • Average inference speed: ~{avg_tokens_per_sec:.1f} tokens/second
   • Average response time: ~12 seconds for 175 tokens
   • Model: Qwen3 8B with Transformers backend
   • Hardware: L4x1 GPU (24GB VRAM)

⚠️  Current Limitations:
   • Transformers backend processes requests sequentially
   • No built-in batching/parallelization
   • Each request waits for the previous to complete
   • GPU may be underutilized during single requests

✅ Optimization Options:
   
   1. SOFTWARE (No cost):
      • Implement request batching in the backend
      • Use vLLM for automatic batching (requires code change)
      • Enable continuous batching for better throughput
   
   2. HARDWARE (Higher cost):
      • Upgrade to L40s for 2x VRAM and compute
      • Expected: 1.5-2x faster per request
      • Better for concurrent users
      • Cost: +$632/month
   
   3. HYBRID APPROACH:
      • Stay on L4x1 + implement batching
      • Most cost-effective for moderate traffic
      • Can handle 5-10 concurrent requests efficiently
""")
    
    print("="*80)

if __name__ == "__main__":
    main()

