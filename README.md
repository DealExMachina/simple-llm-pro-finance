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

OpenAI-compatible API powered by DragonLLM/qwen3-8b-fin-v1.0 using Transformers.

## Overview

This service provides an OpenAI-compatible API for the DragonLLM Qwen3-8B finance-specialized language model. The model supports both English and French financial terminology and includes chain-of-thought reasoning.

## Features

- ✅ **OpenAI-Compatible API** - Drop-in replacement for OpenAI API
- ✅ **French & English Support** - Automatic language detection
- ✅ **Rate Limiting** - Built-in protection (30 req/min, 500 req/hour)
- ✅ **Statistics Tracking** - Token usage and request metrics via `/v1/stats`
- ✅ **Health Monitoring** - Model readiness status in `/health` endpoint
- ✅ **Streaming Support** - Real-time response streaming
- ✅ **PydanticAI Integration** - High-level agent framework included

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
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
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
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
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
- `MODEL` - Model name (default: DragonLLM/qwen3-8b-fin-v1.0)
- `SERVICE_API_KEY` - API key for authentication
- `LOG_LEVEL` - Logging level (default: info)
- `HF_HOME` - Hugging Face cache directory (default: /tmp/huggingface)
- `FORCE_MODEL_RELOAD` - Force reload model from Hub on startup (default: false)

Token priority: `HF_TOKEN_LC2` > `HF_TOKEN_LC` > `HF_TOKEN` > `HUGGING_FACE_HUB_TOKEN`

**Note:** Accept model terms at https://huggingface.co/DragonLLM/qwen3-8b-fin-v1.0 before use.

## Integration

### PydanticAI

The repository includes a PydanticAI integration in `pydanticai_app/`:

```python
from pydanticai_app.agents import finance_agent

result = await finance_agent.run("Qu'est-ce qu'une obligation?")
```

Or use the FastAPI server:
```bash
uvicorn pydanticai_app.main:app --port 8001
```

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="DragonLLM/qwen3-8b-fin-v1.0",
    messages=[{"role": "user", "content": "What is compound interest?"}],
    max_tokens=500
)
```

### DSPy

```python
import dspy

lm = dspy.OpenAI(
    model="DragonLLM/qwen3-8b-fin-v1.0",
    api_base="https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1"
)
```

## Technical Specifications

**Model:**
- DragonLLM/qwen3-8b-fin-v1.0 (8B parameters)
- Fine-tuned on financial data
- English and French support

**Backend:**
- Transformers 4.40.0+
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

```bash
# Run tests
pytest -v

# Test deployment
./test_deployment.sh

# Test PydanticAI integration
python test_pydanticai.py
```

## Project Structure

```
.
├── app/                    # Main API application
│   ├── main.py            # FastAPI app
│   ├── routers/           # API routes
│   ├── providers/         # Model providers
│   ├── middleware/       # Rate limiting, auth
│   └── utils/             # Utilities, stats tracking
├── pydanticai_app/        # PydanticAI integration
├── examples/              # Example scripts
├── docs/                  # Documentation
├── tests/                 # Test suite
└── scripts/               # Utility scripts
```

## License

MIT License - see [LICENSE](LICENSE) file.
