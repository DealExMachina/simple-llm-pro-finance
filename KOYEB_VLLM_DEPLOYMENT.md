# Koyeb vLLM Deployment

## Overview

The Koyeb deployment uses **vLLM's native OpenAI-compatible API server** with full CUDA optimizations.

## Docker Image

**Public image on Docker Hub:**
```
jeanbapt/dragon-llm-inference:vllm-amd64
```

**Important:** Must be built with `--platform linux/amd64` for Koyeb GPU instances.

Built from `Dockerfile.koyeb` with:
- Base: `vllm/vllm-openai:latest`
- Custom startup script for env var configuration
- Flash Attention 2, PagedAttention, continuous batching

## Koyeb Configuration

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `HF_TOKEN_LC2` | (secret) | Hugging Face token for model access |
| `MODEL` | `DragonLLM/Qwen-Open-Finance-R-8B` | Model to load |
| `PORT` | `8000` | Server port |
| `MAX_MODEL_LEN` | `8192` | Max context length |
| `GPU_MEMORY_UTILIZATION` | `0.90` | GPU memory usage |

### Instance Type

- **Recommended**: `gpu-nvidia-l40s` (48GB VRAM) in Iowa (`dsm`)
- **Alternative**: `gpu-nvidia-rtx-4000-sff-ada` (20GB VRAM) in Frankfurt (`fra`)

### Health Check

- **Type**: TCP
- **Port**: 8000
- **Grace Period**: 900 seconds (15 minutes for model loading)

## API Endpoints (vLLM Native)

```
POST /v1/chat/completions  - Chat completions (OpenAI compatible)
POST /v1/completions       - Text completions
GET  /v1/models            - List models
GET  /health               - Health check
```

## Usage Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://dragon-llm-open-finance-inference.koyeb.app/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[
        {"role": "user", "content": "Analyze the impact of rising interest rates"}
    ],
    temperature=0.7,
    max_tokens=1024
)
```

## Build & Push

```bash
# Build for linux/amd64 (required for Koyeb GPU)
docker buildx build --platform linux/amd64 \
  -f Dockerfile.koyeb \
  -t jeanbapt/dragon-llm-inference:vllm-amd64 \
  --push .
```

## Troubleshooting

### "Application exited with code 8" with no logs

1. **Wrong architecture**: Ensure image is built for `linux/amd64`, not ARM
2. **GPU allocation failed**: Try different region or GPU type
3. **Container crash**: Check if `python3` is used (not `python`)

### Model download issues

Ensure `HF_TOKEN_LC2` is set with access to the model.
