# Performance Test Suite

Comprehensive performance and compatibility tests for the PRIIPs LLM Service.

## Quick Start

```bash
# Install additional test dependencies
pip install pytest pytest-asyncio openai

# Run all performance tests
pytest tests/performance/ -v -s

# Run specific test suites
pytest tests/performance/test_inference_speed.py -v -s
pytest tests/performance/test_openai_compatibility.py -v -s

# Run comprehensive benchmark
python tests/performance/benchmark.py
```

## Test Suites

### 1. Inference Speed Tests (`test_inference_speed.py`)

Tests various performance metrics:

- **Single Request Latency**: Measures end-to-end latency for individual requests
- **Token Throughput**: Measures tokens generated per second at different lengths
- **Concurrent Requests**: Tests performance under concurrent load
- **Time to First Token (TTFT)**: Measures latency to first generated token
- **Prompt Processing Speed**: Tests how quickly different prompt lengths are processed
- **Temperature Variance**: Tests response generation with different temperatures

#### Key Metrics:
- Latency (seconds)
- Tokens per second
- Concurrent request handling
- TTFT (Time to First Token)

### 2. OpenAI Compatibility Tests (`test_openai_compatibility.py`)

Validates OpenAI API compatibility:

**Endpoint Compatibility:**
- `GET /v1/models` - Model listing
- `POST /v1/chat/completions` - Chat completions

**Message Format Tests:**
- System messages
- Conversation history
- Multi-turn conversations

**Parameter Tests:**
- `temperature`
- `max_tokens`
- `top_p`
- `stream`

**Client Library Tests:**
- Official OpenAI Python client compatibility
- Streaming support

**Error Handling:**
- Invalid models
- Missing required fields
- Empty messages

**Response Schema:**
- Full OpenAI response format validation
- Proper usage statistics
- Correct finish reasons

### 3. Comprehensive Benchmark (`benchmark.py`)

All-in-one benchmark script that:
- Runs all performance tests
- Validates OpenAI compatibility
- Generates detailed report
- Saves results to JSON

## Configuration

### Change Target URL

Edit the `BASE_URL` in each test file:

```python
# For production
BASE_URL = "https://jeanbaptdzd-priips-llm-service.hf.space"

# For local testing
BASE_URL = "http://localhost:7860"
```

### Adjust Test Parameters

Modify test parameters in each test:

```python
# Number of concurrent requests
num_concurrent = 10

# Number of test runs
num_runs = 10

# Max tokens for generation
max_tokens = 100
```

## Expected Results

### Good Performance Metrics (on L40 GPU):

- **Latency**: < 2 seconds for 100 tokens
- **Token Throughput**: > 50 tokens/second
- **TTFT**: < 500ms
- **Concurrent Handling**: > 5 requests/second

### OpenAI Compatibility:

Should pass all compatibility tests (100% score)

## Test Output Examples

### Inference Speed Test Output:
```
=== Single Request Performance ===
Latency: 1.45s
Prompt tokens: 12
Completion tokens: 89
Total tokens: 101
Tokens per second: 61.38
Response: Artificial intelligence (AI) refers to...
```

### Concurrent Load Test Output:
```
=== Concurrent Requests Test (10 requests) ===
Total time: 3.21s
Successful requests: 10/10
Average latency: 2.15s
Requests per second: 3.12
```

### OpenAI Compatibility Output:
```
=== OpenAI API Compatibility ===
✓ List models endpoint
✓ Chat completions endpoint
✓ System message support
✓ Conversation history
✓ Temperature parameter
✓ Max tokens parameter

Compatibility Score: 6/7 (86%)
```

## Troubleshooting

### Tests Timeout
- Increase timeout in `httpx.AsyncClient(timeout=120.0)`
- Check if service is running with health check

### Connection Errors
- Verify BASE_URL is correct
- Check network connectivity
- Ensure service is deployed and running

### Performance Lower Than Expected
- Check GPU utilization on server
- Verify vLLM configuration
- Look for model loading issues in logs

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio openai
      - name: Run performance tests
        run: pytest tests/performance/ -v
```

## Benchmark Results

Results are saved to `benchmark_results.json` with structure:

```json
{
  "single_request": {
    "avg_latency": 1.45,
    "avg_tokens_per_sec": 61.38
  },
  "concurrent_load": {
    "requests_per_sec": 3.12,
    "successful": 10
  },
  "openai_compatibility": {
    "score": "6/7"
  }
}
```

## Advanced Usage

### Custom Test Scenarios

Create custom test scenarios:

```python
@pytest.mark.asyncio
async def test_custom_scenario(client):
    # Your custom test here
    payload = {
        "model": "DragonLLM/LLM-Pro-Finance-Small",
        "messages": [{"role": "user", "content": "Custom prompt"}],
        "max_tokens": 200
    }
    response = await client.post(f"{BASE_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 200
```

### Stress Testing

For stress testing, increase concurrent requests:

```python
await benchmark_concurrent_load(num_concurrent=50)
```

## Monitoring

Metrics to monitor during tests:

- **Server-side**:
  - GPU utilization
  - Memory usage
  - Request queue length
  - Model loading time

- **Client-side**:
  - Response times
  - Error rates
  - Token throughput
  - Network latency

## Support

For issues or questions:
- Check service logs at Hugging Face Spaces dashboard
- Review DEPLOYMENT.md for configuration details
- Verify vLLM is properly initialized with model







