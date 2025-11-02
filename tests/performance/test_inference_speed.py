"""
Performance tests for inference speed and token throughput
Run with: pytest tests/performance/test_inference_speed.py -v -s
"""
import pytest
import httpx
import time
import asyncio
from typing import List, Dict

# Test configuration
BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"
# BASE_URL = "http://localhost:7860"  # For local testing

@pytest.fixture
def client():
    return httpx.AsyncClient(timeout=120.0)

@pytest.mark.asyncio
async def test_single_request_latency(client):
    """Test latency for a single chat completion request"""
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    start_time = time.time()
    response = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload)
    end_time = time.time()
    
    assert response.status_code == 200
    data = response.json()
    
    latency = end_time - start_time
    prompt_tokens = data["usage"]["prompt_tokens"]
    completion_tokens = data["usage"]["completion_tokens"]
    total_tokens = data["usage"]["total_tokens"]
    
    print(f"\n=== Single Request Performance ===")
    print(f"Latency: {latency:.2f}s")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Completion tokens: {completion_tokens}")
    print(f"Total tokens: {total_tokens}")
    print(f"Tokens per second: {completion_tokens / latency:.2f}")
    print(f"Response: {data['choices'][0]['message']['content'][:100]}...")
    
    assert latency < 10.0, f"Latency too high: {latency:.2f}s"
    assert completion_tokens > 0, "No tokens generated"


@pytest.mark.asyncio
async def test_token_throughput_various_lengths(client):
    """Test token generation speed with various output lengths"""
    test_cases = [
        {"max_tokens": 50, "prompt": "Explain photosynthesis in one sentence."},
        {"max_tokens": 100, "prompt": "Explain photosynthesis in a short paragraph."},
        {"max_tokens": 200, "prompt": "Explain photosynthesis in detail."},
        {"max_tokens": 500, "prompt": "Write a detailed essay about photosynthesis."},
    ]
    
    print(f"\n=== Token Throughput Test ===")
    
    for test_case in test_cases:
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": test_case["prompt"]}],
            "max_tokens": test_case["max_tokens"],
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload)
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        
        latency = end_time - start_time
        completion_tokens = data["usage"]["completion_tokens"]
        tokens_per_sec = completion_tokens / latency if latency > 0 else 0
        
        print(f"\nMax tokens: {test_case['max_tokens']}")
        print(f"  Generated: {completion_tokens} tokens")
        print(f"  Time: {latency:.2f}s")
        print(f"  Throughput: {tokens_per_sec:.2f} tokens/sec")
        
        assert completion_tokens > 0


@pytest.mark.asyncio
async def test_concurrent_requests(client):
    """Test performance with concurrent requests"""
    num_requests = 5
    
    async def make_request(request_id: int):
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [
                {"role": "user", "content": f"Request {request_id}: What is 2+2?"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload)
        end_time = time.time()
        
        return {
            "request_id": request_id,
            "status": response.status_code,
            "latency": end_time - start_time,
            "response": response.json() if response.status_code == 200 else None
        }
    
    print(f"\n=== Concurrent Requests Test ({num_requests} requests) ===")
    
    start_time = time.time()
    results = await asyncio.gather(*[make_request(i) for i in range(num_requests)])
    end_time = time.time()
    
    total_time = end_time - start_time
    successful = sum(1 for r in results if r["status"] == 200)
    avg_latency = sum(r["latency"] for r in results) / len(results)
    
    print(f"Total time: {total_time:.2f}s")
    print(f"Successful requests: {successful}/{num_requests}")
    print(f"Average latency: {avg_latency:.2f}s")
    print(f"Requests per second: {num_requests / total_time:.2f}")
    
    for result in results:
        print(f"  Request {result['request_id']}: {result['latency']:.2f}s - {result['status']}")
    
    assert successful == num_requests


@pytest.mark.asyncio
async def test_time_to_first_token(client):
    """Test time to first token (TTFT) using streaming"""
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": "Count from 1 to 10."}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": True
    }
    
    start_time = time.time()
    first_token_time = None
    token_count = 0
    
    async with client.stream("POST", f"{BASE_URL}/v1/chat/completions", json=payload) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: ") and line.strip() != "data: [DONE]":
                if first_token_time is None:
                    first_token_time = time.time()
                token_count += 1
    
    end_time = time.time()
    
    if first_token_time:
        ttft = first_token_time - start_time
        total_time = end_time - start_time
        
        print(f"\n=== Time to First Token ===")
        print(f"TTFT: {ttft:.3f}s")
        print(f"Total time: {total_time:.2f}s")
        print(f"Chunks received: {token_count}")
        
        assert ttft < 5.0, f"TTFT too high: {ttft:.3f}s"


@pytest.mark.asyncio
async def test_prompt_processing_speed(client):
    """Test speed with different prompt lengths"""
    prompts = [
        "Hi",  # Very short
        "What is artificial intelligence?" * 5,  # Short
        "Explain quantum computing. " * 20,  # Medium
        "Write a detailed explanation of machine learning. " * 50,  # Long
    ]
    
    print(f"\n=== Prompt Processing Speed ===")
    
    for i, prompt in enumerate(prompts):
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            latency = end_time - start_time
            prompt_tokens = data["usage"]["prompt_tokens"]
            
            print(f"\nPrompt {i+1} (length ~{len(prompt)} chars):")
            print(f"  Prompt tokens: {prompt_tokens}")
            print(f"  Latency: {latency:.2f}s")
            print(f"  Tokens/sec: {prompt_tokens / latency:.2f}")


@pytest.mark.asyncio
async def test_temperature_variance(client):
    """Test response variance with different temperatures"""
    temperatures = [0.0, 0.5, 1.0, 1.5]
    prompt = "The future of artificial intelligence is"
    
    print(f"\n=== Temperature Variance Test ===")
    
    for temp in temperatures:
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
            "temperature": temp
        }
        
        response = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        print(f"\nTemperature: {temp}")
        print(f"Response: {content[:100]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])







