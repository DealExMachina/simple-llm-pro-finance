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

| Platform | Backend | Docker Image | Port |
|----------|---------|--------------|------|
| **HF Spaces** | Transformers | Default (builds from `Dockerfile`) | 7860 |
| **Koyeb** | vLLM (optimized) | `jeanbapt/dragon-llm-inference:vllm` | 8000 |

### Docker Hub Public Images

```
jeanbapt/dragon-llm-inference:vllm      # Koyeb - vLLM with CUDA optimizations
jeanbapt/dragon-llm-inference:latest    # HF Spaces - Transformers backend
```

## Features

- **OpenAI-compatible API** - Drop-in replacement for OpenAI SDK
- **French and English support** - Automatic language detection  
- **Rate limiting** - Built-in protection (30 req/min, 500 req/hour)
- **Statistics tracking** - Token usage and request metrics via `/v1/stats`
- **Health monitoring** - Model readiness status in `/health` endpoint
- **Streaming support** - Real-time response streaming
- **Tool calls support** - OpenAI-compatible tool/function calling
- **Structured outputs** - JSON format support via `response_format`

## API Endpoints

### Chat Completions
```bash
curl -X POST "https://your-endpoint/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is compound interest?"}],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### List Models
```bash
curl -X GET "https://your-endpoint/v1/models"
```

### Streaming
```bash
curl -X POST "https://your-endpoint/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "Explain Value at Risk"}],
    "stream": true
  }'
```

### Health Check
```bash
curl -X GET "https://your-endpoint/health"
```

## Configuration

### Environment Variables

**Required:**
- `HF_TOKEN_LC2` - Hugging Face token with access to DragonLLM models

**Optional:**
- `MODEL` - Model name (default: `DragonLLM/Qwen-Open-Finance-R-8B`)
- `PORT` - Server port (default: 7860 for HF, 8000 for Koyeb)
- `SERVICE_API_KEY` - API key for authentication
- `LOG_LEVEL` - Logging level (default: `info`)

Token priority: `HF_TOKEN_LC2` > `HF_TOKEN_LC` > `HF_TOKEN` > `HUGGING_FACE_HUB_TOKEN`

**Note:** Accept model terms at https://huggingface.co/DragonLLM/Qwen-Open-Finance-R-8B before use.

## Integration

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-endpoint/v1",
    api_key="not-needed"  # or your SERVICE_API_KEY
)

response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "What is compound interest?"}],
    max_tokens=500
)
```

## Koyeb Deployment (vLLM)

The Koyeb deployment uses vLLM's native OpenAI-compatible server with full CUDA optimizations:

- **Flash Attention 2** - Faster attention computation
- **PagedAttention** - Efficient GPU memory management
- **Continuous batching** - High throughput inference
- **Prefix caching** - Reuse KV cache for common prefixes

See [KOYEB_VLLM_DEPLOYMENT.md](KOYEB_VLLM_DEPLOYMENT.md) for detailed setup.

### Quick Deploy to Koyeb

1. Create app in Koyeb dashboard
2. Set Docker image: `jeanbapt/dragon-llm-inference:vllm`
3. Add environment variables:
   - `MODEL`: `DragonLLM/Qwen-Open-Finance-R-8B`
   - `HF_TOKEN_LC2`: (your HF token as secret)
   - `PORT`: `8000`
4. Select GPU instance (L40s recommended)
5. Set health check: `GET /health` on port 8000

## Technical Specifications

**Model:**
- DragonLLM/Qwen-Open-Finance-R-8B (8B parameters)
- Fine-tuned on financial data
- English and French support

**HF Spaces Backend:**
- Transformers 4.45.0+
- PyTorch 2.5.0+ (CUDA 12.4)

**Koyeb Backend:**
- vLLM 0.6.0+
- Flash Attention 2
- CUDA 12.4

**Hardware:**
- Minimum: L4 GPU (24GB VRAM)
- Recommended: L40s GPU (48GB VRAM)

## Project Structure

```
.
├── app/                      # Main API application
│   ├── main.py              # FastAPI app (HF Spaces)
│   ├── routers/             # API routes
│   ├── providers/           # Model providers (Transformers)
│   ├── middleware/          # Rate limiting, auth
│   └── utils/               # Utilities, stats tracking
├── Dockerfile               # HF Spaces (Transformers)
├── Dockerfile.koyeb         # Koyeb (vLLM)
├── start.sh                 # HF Spaces startup
├── start-vllm.sh            # Koyeb vLLM startup
├── docs/                    # Technical documentation
└── tests/                   # Test suite
```

## Development

### Local Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Testing

```bash
# Unit tests
pytest tests/ -v

# Integration tests
python tests/integration/test_space_basic.py
python tests/integration/test_tool_calls.py
```

## License

MIT License - see [LICENSE](LICENSE) file.
