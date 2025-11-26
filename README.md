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

OpenAI-compatible API powered by DragonLLM/Qwen-Open-Finance-R-8B.

## Deployment Options

| Platform | Backend | Dockerfile | Use Case |
|----------|---------|------------|----------|
| Hugging Face Spaces | Transformers | `Dockerfile` | Development, L4 GPU |
| Koyeb | vLLM | `Dockerfile.koyeb` | Production, L40s GPU |

## Features

- OpenAI-compatible API
- Tool/function calling support
- Streaming responses
- French and English financial terminology
- Rate limiting (30 req/min, 500 req/hour)
- Statistics tracking via `/v1/stats`

## Quick Start

### Chat Completion
```bash
curl -X POST "https://your-endpoint/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is compound interest?"}],
    "max_tokens": 500
  }'
```

### OpenAI SDK
```python
from openai import OpenAI

client = OpenAI(base_url="https://your-endpoint/v1", api_key="not-needed")
response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "What is compound interest?"}],
    max_tokens=500
)
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN_LC2` | Yes | - | Hugging Face token |
| `MODEL` | No | `DragonLLM/Qwen-Open-Finance-R-8B` | Model name |
| `PORT` | No | `8000` (vLLM) / `7860` (Transformers) | Server port |

### vLLM-specific (Koyeb)

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_AUTO_TOOL_CHOICE` | `true` | Enable tool calling |
| `TOOL_CALL_PARSER` | `hermes` | Parser for Qwen models |
| `MAX_MODEL_LEN` | `8192` | Max context length |
| `GPU_MEMORY_UTILIZATION` | `0.90` | GPU memory fraction |

## Koyeb Deployment

Build and push the vLLM image:
```bash
docker build --platform linux/amd64 -f Dockerfile.koyeb -t your-registry/dragon-llm-inference:vllm-amd64 .
docker push your-registry/dragon-llm-inference:vllm-amd64
```

Recommended instance: `gpu-nvidia-l40s` (48GB VRAM)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completion |
| `/v1/stats` | GET | Usage statistics |
| `/health` | GET | Health check |

## Technical Specifications

- **Model**: DragonLLM/Qwen-Open-Finance-R-8B (8B parameters)
- **vLLM Backend**: vllm-openai:latest with hermes tool parser
- **Transformers Backend**: 4.45.0+ with PyTorch 2.5.0+ (CUDA 12.4)
- **Minimum VRAM**: 20GB (L4), recommended 48GB (L40s)

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Testing
```bash
pytest tests/ -v
python tests/integration/test_tool_calls.py
```

## License

MIT License
