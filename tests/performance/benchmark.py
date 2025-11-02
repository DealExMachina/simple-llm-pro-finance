#!/usr/bin/env python3
"""
Comprehensive benchmark suite for PRIIPs LLM Service
Run with: python tests/performance/benchmark.py
"""
import asyncio
import httpx
import time
import statistics
from typing import List, Dict
import json

# Configuration
BASE_URL = "https://jeanbaptdzd-priips-llm-service.hf.space"
# BASE_URL = "http://localhost:7860"  # For local testing


class Benchmark:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
        self.results = {}
    
    async def health_check(self) -> bool:
        """Check if service is available"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    async def benchmark_single_request(self, num_runs: int = 10) -> Dict:
        """Benchmark single request latency"""
        print(f"\n{'='*60}")
        print("BENCHMARK: Single Request Latency")
        print(f"{'='*60}")
        
        latencies = []
        tokens_per_sec = []
        
        payload = {
            "model": "DragonLLM/LLM-Pro-Finance-Small",
            "messages": [
                {"role": "user", "content": "What is artificial intelligence?"}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        for i in range(num_runs):
            start = time.time()
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                latency = end - start
                completion_tokens = data["usage"]["completion_tokens"]
                tps = completion_tokens / latency if latency > 0 else 0
                
                latencies.append(latency)
                tokens_per_sec.append(tps)
                
                print(f"Run {i+1}/{num_runs}: {latency:.2f}s, {tps:.2f} tokens/sec")
        
        results = {
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "std_latency": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "avg_tokens_per_sec": statistics.mean(tokens_per_sec),
            "max_tokens_per_sec": max(tokens_per_sec),
        }
        
        print(f"\nResults:")
        print(f"  Average latency: {results['avg_latency']:.2f}s (±{results['std_latency']:.2f}s)")
        print(f"  Min/Max latency: {results['min_latency']:.2f}s / {results['max_latency']:.2f}s")
        print(f"  Average throughput: {results['avg_tokens_per_sec']:.2f} tokens/sec")
        print(f"  Max throughput: {results['max_tokens_per_sec']:.2f} tokens/sec")
        
        return results
    
    async def benchmark_concurrent_load(self, num_concurrent: int = 10) -> Dict:
        """Benchmark concurrent request handling"""
        print(f"\n{'='*60}")
        print(f"BENCHMARK: Concurrent Load ({num_concurrent} requests)")
        print(f"{'='*60}")
        
        async def make_request(request_id: int):
            payload = {
                "model": "DragonLLM/LLM-Pro-Finance-Small",
                "messages": [
                    {"role": "user", "content": f"Request {request_id}: Explain machine learning."}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            start = time.time()
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            end = time.time()
            
            return {
                "request_id": request_id,
                "latency": end - start,
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        
        start_time = time.time()
        results = await asyncio.gather(*[make_request(i) for i in range(num_concurrent)])
        end_time = time.time()
        
        total_time = end_time - start_time
        successful = [r for r in results if r["status"] == 200]
        latencies = [r["latency"] for r in successful]
        
        benchmark_results = {
            "total_time": total_time,
            "num_requests": num_concurrent,
            "successful": len(successful),
            "failed": num_concurrent - len(successful),
            "avg_latency": statistics.mean(latencies) if latencies else 0,
            "requests_per_sec": num_concurrent / total_time,
        }
        
        print(f"\nResults:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful: {len(successful)}/{num_concurrent}")
        print(f"  Average latency: {benchmark_results['avg_latency']:.2f}s")
        print(f"  Requests/sec: {benchmark_results['requests_per_sec']:.2f}")
        
        return benchmark_results
    
    async def benchmark_different_lengths(self) -> Dict:
        """Benchmark with different output lengths"""
        print(f"\n{'='*60}")
        print("BENCHMARK: Different Output Lengths")
        print(f"{'='*60}")
        
        test_cases = [
            {"name": "Short (50 tokens)", "max_tokens": 50},
            {"name": "Medium (100 tokens)", "max_tokens": 100},
            {"name": "Long (200 tokens)", "max_tokens": 200},
            {"name": "Very Long (500 tokens)", "max_tokens": 500},
        ]
        
        results_by_length = {}
        
        for test_case in test_cases:
            payload = {
                "model": "DragonLLM/LLM-Pro-Finance-Small",
                "messages": [
                    {"role": "user", "content": "Write about the history of computing."}
                ],
                "max_tokens": test_case["max_tokens"],
                "temperature": 0.7
            }
            
            start = time.time()
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                latency = end - start
                completion_tokens = data["usage"]["completion_tokens"]
                tps = completion_tokens / latency if latency > 0 else 0
                
                results_by_length[test_case["name"]] = {
                    "latency": latency,
                    "tokens": completion_tokens,
                    "tokens_per_sec": tps
                }
                
                print(f"\n{test_case['name']}:")
                print(f"  Generated: {completion_tokens} tokens")
                print(f"  Time: {latency:.2f}s")
                print(f"  Throughput: {tps:.2f} tokens/sec")
        
        return results_by_length
    
    async def benchmark_openai_compatibility(self) -> Dict:
        """Test OpenAI API compatibility"""
        print(f"\n{'='*60}")
        print("BENCHMARK: OpenAI API Compatibility")
        print(f"{'='*60}")
        
        tests = {
            "list_models": False,
            "chat_completions": False,
            "system_message": False,
            "conversation_history": False,
            "streaming": False,
            "temperature_param": False,
            "max_tokens_param": False,
        }
        
        # Test 1: List models
        try:
            response = await self.client.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    tests["list_models"] = True
                    print("✓ List models endpoint")
        except:
            pass
        
        # Test 2: Chat completions
        try:
            payload = {"model": "DragonLLM/LLM-Pro-Finance-Small", "messages": [{"role": "user", "content": "Hi"}]}
            response = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and "usage" in data:
                    tests["chat_completions"] = True
                    print("✓ Chat completions endpoint")
        except:
            pass
        
        # Test 3: System message
        try:
            payload = {
                "model": "DragonLLM/LLM-Pro-Finance-Small",
                "messages": [
                    {"role": "system", "content": "Be helpful."},
                    {"role": "user", "content": "Hi"}
                ]
            }
            response = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            if response.status_code == 200:
                tests["system_message"] = True
                print("✓ System message support")
        except:
            pass
        
        # Test 4: Conversation history
        try:
            payload = {
                "model": "DragonLLM/LLM-Pro-Finance-Small",
                "messages": [
                    {"role": "user", "content": "My name is Alice"},
                    {"role": "assistant", "content": "Hello Alice"},
                    {"role": "user", "content": "What's my name?"}
                ]
            }
            response = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            if response.status_code == 200:
                tests["conversation_history"] = True
                print("✓ Conversation history")
        except:
            pass
        
        # Test 5: Temperature parameter
        try:
            payload = {
                "model": "DragonLLM/LLM-Pro-Finance-Small",
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.5
            }
            response = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            if response.status_code == 200:
                tests["temperature_param"] = True
                print("✓ Temperature parameter")
        except:
            pass
        
        # Test 6: Max tokens parameter
        try:
            payload = {
                "model": "DragonLLM/LLM-Pro-Finance-Small",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10
            }
            response = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            if response.status_code == 200:
                tests["max_tokens_param"] = True
                print("✓ Max tokens parameter")
        except:
            pass
        
        passed = sum(1 for v in tests.values() if v)
        total = len(tests)
        
        print(f"\nCompatibility Score: {passed}/{total} ({100*passed/total:.0f}%)")
        
        return {"tests": tests, "score": f"{passed}/{total}"}
    
    async def run_all_benchmarks(self):
        """Run all benchmarks"""
        print(f"\n{'#'*60}")
        print("PRIIPs LLM Service - Comprehensive Benchmark Suite")
        print(f"Service: {self.base_url}")
        print(f"{'#'*60}")
        
        # Health check
        print("\nChecking service health...")
        if not await self.health_check():
            print("❌ Service is not available!")
            return
        print("✓ Service is healthy")
        
        # Run benchmarks
        self.results["single_request"] = await self.benchmark_single_request(num_runs=5)
        self.results["concurrent_load"] = await self.benchmark_concurrent_load(num_concurrent=5)
        self.results["different_lengths"] = await self.benchmark_different_lengths()
        self.results["openai_compatibility"] = await self.benchmark_openai_compatibility()
        
        # Summary
        print(f"\n{'#'*60}")
        print("SUMMARY")
        print(f"{'#'*60}")
        print(f"\n⚡ Performance:")
        print(f"  Average latency: {self.results['single_request']['avg_latency']:.2f}s")
        print(f"  Token throughput: {self.results['single_request']['avg_tokens_per_sec']:.2f} tokens/sec")
        print(f"  Concurrent capacity: {self.results['concurrent_load']['requests_per_sec']:.2f} req/sec")
        print(f"\n🔌 OpenAI Compatibility: {self.results['openai_compatibility']['score']}")
        
        # Save results
        with open("benchmark_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📊 Full results saved to benchmark_results.json")
        
        await self.client.aclose()


async def main():
    benchmark = Benchmark()
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())







