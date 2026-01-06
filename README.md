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

## Deployment

| Platform | Backend | Dockerfile | Use Case |
|----------|---------|------------|----------|
| Hugging Face Spaces | vLLM | `Dockerfile` | Development, L4 GPU |
| Koyeb | vLLM | `Dockerfile.koyeb` | Production, L40s GPU |

**Note**: Both platforms now use vLLM for unified deployment and better performance.

## Features

- OpenAI-compatible API (vLLM backend)
- Tool/function calling support (hermes parser)
- Streaming responses
- High-performance inference
- Observability (Langfuse & Logfire)

## Quick Start

```bash
curl -X POST "https://your-endpoint/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is compound interest?"}],
    "max_tokens": 500
  }'
```

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

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN_LC2` | Yes | - | Hugging Face token |
| `MODEL` | No | `DragonLLM/Qwen-Open-Finance-R-8B` | Model name |
| `PORT` | No | `8000` (default) / `7860` (HF Spaces) | Server port |

**vLLM-specific (both platforms):**
- `ENABLE_AUTO_TOOL_CHOICE=true` - Enable tool calling
- `TOOL_CALL_PARSER=hermes` - Parser for Qwen models
- `MAX_MODEL_LEN=8192` - Max context length
- `GPU_MEMORY_UTILIZATION=0.90` - GPU memory fraction
- `PORT=8000` - Server port (default) or `7860` for HF Spaces

## API Endpoints

vLLM provides standard OpenAI-compatible endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | List available models (use as health check) |
| `/v1/chat/completions` | POST | Chat completion (supports streaming) |

**Note**: vLLM does not provide custom endpoints like `/health`, `/ready`, or `/v1/stats`.

## Technical Specs

- **Model**: DragonLLM/Qwen-Open-Finance-R-8B (8B parameters)
- **Backend**: vLLM (vllm-openai:latest) with hermes tool parser
- **Unified Deployment**: Both HF Spaces and Koyeb use vLLM
- **Minimum VRAM**: 20GB (L4), recommended 48GB (L40s)

## Development

```bash
# Create virtual environment with Python 3.13
python3.13 -m venv venv313
source venv313/bin/activate  # On Windows: venv313\Scripts\activate

# Install dependencies (minimal - only observability)
pip install -r requirements.txt

# For local vLLM testing, use Docker:
docker build -f Dockerfile -t open-finance-llm .
docker run -p 8000:8000 -e HF_TOKEN_LC2=your_token open-finance-llm

# Run integration tests
pytest tests/integration/ -v
```

**Note**: This project uses vLLM for deployment. For local development, use Docker or deploy to Hugging Face Spaces/Koyeb.

## License

MIT License
