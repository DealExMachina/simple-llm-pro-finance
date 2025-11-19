---
title: Open Finance LLM 8B
emoji: 🐉
colorFrom: red
colorTo: red
sdk: docker
pinned: false
app_port: 7860
suggested_hardware: l4x1
---

# Open Finance LLM 8B

OpenAI-compatible API powered by DragonLLM/Qwen-Open-Finance-R-8B using Transformers.

## Overview

This service provides an OpenAI-compatible API for the DragonLLM Qwen3-8B finance-specialized language model. The model supports both English and French financial terminology and includes chain-of-thought reasoning.

## Features

- OpenAI-compatible API - Drop-in replacement for OpenAI API
- French and English support - Automatic language detection
- Rate limiting - Built-in protection (30 req/min, 500 req/hour)
- Statistics tracking - Token usage and request metrics via `/v1/stats`
- Health monitoring - Model readiness status in `/health` endpoint
- Streaming support - Real-time response streaming
- Tool calls support - OpenAI-compatible tool/function calling
- Structured outputs - JSON format support via response_format

## API Endpoints

### List Models
```bash
curl -X GET "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/models"
```

### Chat Completions
```bash
curl -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is compound interest?"}],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Streaming
```bash
curl -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "Explain Value at Risk"}],
    "stream": true
  }'
```

### Statistics
```bash
curl -X GET "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/stats"
```

### Health Check
```bash
curl -X GET "https://jeanbaptdzd-open-finance-llm-8b.hf.space/health"
```

## Response Format

Responses include chain-of-thought reasoning in `<think>` tags followed by the answer. Reasoning typically consumes 40-60% of tokens.

**Recommended `max_tokens`:**
- Simple queries: 300-400
- Complex queries: 500-800
- Detailed analysis: 800-1200

## Configuration

### Environment Variables

**Required:**
- `HF_TOKEN_LC2` - Hugging Face token with access to DragonLLM models

**Optional:**
- `MODEL` - Model name (default: DragonLLM/Qwen-Open-Finance-R-8B)
- `SERVICE_API_KEY` - API key for authentication
- `LOG_LEVEL` - Logging level (default: info)
- `HF_HOME` - Hugging Face cache directory (default: /tmp/huggingface)
- `FORCE_MODEL_RELOAD` - Force reload model from Hub on startup (default: false)

Token priority: `HF_TOKEN_LC2` > `HF_TOKEN_LC` > `HF_TOKEN` > `HUGGING_FACE_HUB_TOKEN`

**Note:** Accept model terms at https://huggingface.co/DragonLLM/Qwen-Open-Finance-R-8B before use.

## Integration

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "What is compound interest?"}],
    max_tokens=500
)
```


## Technical Specifications

**Model:**
- DragonLLM/Qwen-Open-Finance-R-8B (8B parameters)
- Fine-tuned on financial data
- English and French support

**Backend:**
- Transformers 4.45.0+
- PyTorch 2.5.0+ (CUDA 12.4)
- Accelerate 0.30.0+

**Performance:**
- Inference: ~15 tokens/second (L4 GPU)
- Response time: 3-27 seconds
- Minimum VRAM: 20GB

**Hardware:**
- Development: L4x1 GPU (24GB VRAM)
- Production: L40s GPU (48GB VRAM)

## Development

### Local Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Testing

**Unit Tests:**
```bash
pytest tests/ -v
```

**Integration Tests:**
The integration tests evaluate the model's ability to produce valid JSON outputs and execute tool calls, which are critical requirements for financial applications.

```bash
# Basic API functionality
python tests/integration/test_space_basic.py

# Tool calls and JSON format
python tests/integration/test_space_with_tools.py

# Detailed tool call validation
python tests/integration/test_tool_calls.py
```

**Test Coverage:**
- API endpoints (health, models, chat completions)
- Tool calls with `tool_choice` parameter
- Structured JSON outputs via `response_format`
- Model response parsing and validation

These tests verify that the small 8B model can reliably produce valid JSON and execute tool calls, which is mandatory for financial workflows requiring structured data and function execution.

## Project Structure

```
.
├── app/                    # Main API application
│   ├── main.py            # FastAPI app
│   ├── routers/           # API routes
│   ├── providers/         # Model providers
│   ├── middleware/       # Rate limiting, auth
│   └── utils/             # Utilities, stats tracking
├── docs/                  # Documentation
├── tests/                 # Test suite
│   ├── integration/      # Integration tests (API, tool calls, JSON)
│   └── performance/      # Performance benchmarks
└── scripts/               # Utility scripts
```

## License

MIT License - see [LICENSE](LICENSE) file.
