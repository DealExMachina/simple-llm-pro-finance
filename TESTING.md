# Testing Guide

## Quick Start

Once your Hugging Face Space is deployed and running, you can run comprehensive performance tests:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run the comprehensive benchmark (recommended)
python tests/performance/benchmark.py

# Or run individual test suites
pytest tests/performance/test_inference_speed.py -v -s
pytest tests/performance/test_openai_compatibility.py -v -s
```

## What Gets Tested

### ⚡ Performance Metrics
- **Latency**: End-to-end response time
- **Token Throughput**: Tokens generated per second
- **Concurrent Handling**: Multiple simultaneous requests
- **Time to First Token (TTFT)**: Latency to start streaming

### 🔌 OpenAI API Compatibility
- Endpoint compatibility (`/v1/models`, `/v1/chat/completions`)
- Message formats (system, user, assistant, multi-turn)
- Parameters (temperature, max_tokens, top_p, stream)
- Official OpenAI client library compatibility
- Response schema validation

### 📊 Load Testing
- Single request performance
- Concurrent request handling (5-10 requests)
- Different prompt lengths
- Different output lengths (50-500 tokens)

## Expected Results (L40 GPU with vLLM)

### Good Performance:
```
✓ Average latency: 1-2 seconds (100 tokens)
✓ Token throughput: 50-100 tokens/second
✓ TTFT: < 500ms
✓ Concurrent capacity: 5-10 req/sec
✓ OpenAI compatibility: 100%
```

### Performance Indicators:

| Metric | Excellent | Good | Needs Improvement |
|--------|-----------|------|-------------------|
| Latency (100 tokens) | < 1s | 1-3s | > 3s |
| Token throughput | > 80 tok/s | 40-80 tok/s | < 40 tok/s |
| TTFT | < 300ms | 300-700ms | > 700ms |
| Concurrent (5 req) | < 4s | 4-8s | > 8s |

## Test Output Example

```bash
$ python tests/performance/benchmark.py

############################################################
PRIIPs LLM Service - Comprehensive Benchmark Suite
Service: https://jeanbaptdzd-priips-llm-service.hf.space
############################################################

Checking service health...
✓ Service is healthy

============================================================
BENCHMARK: Single Request Latency
============================================================
Run 1/5: 1.45s, 61.38 tokens/sec
Run 2/5: 1.52s, 58.92 tokens/sec
Run 3/5: 1.48s, 60.14 tokens/sec
Run 4/5: 1.51s, 59.21 tokens/sec
Run 5/5: 1.46s, 61.01 tokens/sec

Results:
  Average latency: 1.48s (±0.03s)
  Min/Max latency: 1.45s / 1.52s
  Average throughput: 60.13 tokens/sec
  Max throughput: 61.38 tokens/sec

============================================================
BENCHMARK: Concurrent Load (5 requests)
============================================================

Results:
  Total time: 3.21s
  Successful: 5/5
  Average latency: 2.15s
  Requests/sec: 1.56

============================================================
BENCHMARK: OpenAI API Compatibility
============================================================
✓ List models endpoint
✓ Chat completions endpoint
✓ System message support
✓ Conversation history
✓ Temperature parameter
✓ Max tokens parameter

Compatibility Score: 6/6 (100%)

############################################################
SUMMARY
############################################################

⚡ Performance:
  Average latency: 1.48s
  Token throughput: 60.13 tokens/sec
  Concurrent capacity: 1.56 req/sec

🔌 OpenAI Compatibility: 6/6

📊 Full results saved to benchmark_results.json
```

## Running Specific Tests

### Test Inference Speed Only:
```bash
pytest tests/performance/test_inference_speed.py::test_single_request_latency -v -s
```

### Test OpenAI Compatibility Only:
```bash
pytest tests/performance/test_openai_compatibility.py::TestOpenAIClientLibrary -v -s
```

### Test Streaming:
```bash
pytest tests/performance/test_openai_compatibility.py::TestOpenAIClientLibrary::test_streaming_with_openai_client -v -s
```

## Troubleshooting

### Service Not Available
```bash
# Check health endpoint
curl https://jeanbaptdzd-priips-llm-service.hf.space/health

# Check if Space is running on HF dashboard
```

### Slow Performance
- Check GPU utilization in HF Spaces logs
- Verify model is loaded (first request is slower)
- Check if using correct hardware (L40 GPU)

### OpenAI Client Errors
```bash
# Install latest OpenAI client
pip install --upgrade openai
```

## Integration Examples

### Use with PydanticAI:
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    "DragonLLM/LLM-Pro-Finance-Small",
    base_url="https://jeanbaptdzd-priips-llm-service.hf.space/v1"
)
agent = Agent(model=model)
result = agent.run_sync("What is machine learning?")
```

### Use with DSPy:
```python
import dspy

lm = dspy.OpenAI(
    model="DragonLLM/LLM-Pro-Finance-Small",
    api_base="https://jeanbaptdzd-priips-llm-service.hf.space/v1"
)
dspy.settings.configure(lm=lm)
```

### Direct OpenAI Client:
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://jeanbaptdzd-priips-llm-service.hf.space/v1",
    api_key="dummy"  # Not required if no auth
)

response = client.chat.completions.create(
    model="DragonLLM/LLM-Pro-Finance-Small",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Continuous Monitoring

Set up automated performance monitoring:

```bash
# Run benchmarks hourly
0 * * * * cd /path/to/repo && python tests/performance/benchmark.py

# Compare results over time
python scripts/compare_benchmarks.py benchmark_results_*.json
```

## Next Steps

1. ✅ Run initial benchmark to establish baseline
2. Monitor performance over time
3. Optimize based on bottlenecks found
4. Test with production workloads
5. Set up alerts for performance degradation

