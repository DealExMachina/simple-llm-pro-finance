# Koyeb vLLM Deployment

## Overview

The Koyeb deployment uses **vLLM's native OpenAI-compatible API server** with full CUDA optimizations for maximum inference performance.

## Docker Image

**Public image on Docker Hub:**
```
jeanbapt/dragon-llm-inference:vllm
```

Built from `Dockerfile.koyeb` with:
- NVIDIA CUDA 12.4 base
- vLLM 0.6.0+ with all optimizations
- Native OpenAI-compatible server

## vLLM Optimizations

| Feature | Benefit |
|---------|---------|
| **Flash Attention 2** | Faster attention computation |
| **PagedAttention** | Efficient KV cache management |
| **Continuous Batching** | Handle multiple requests simultaneously |
| **Prefix Caching** | Reuse KV cache for common prefixes |
| **Chunked Prefill** | Better memory utilization |
| **CUDA Graphs** | Reduced kernel launch overhead |

## Koyeb Configuration

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `MODEL` | `DragonLLM/Qwen-Open-Finance-R-8B` | Model to serve |
| `HF_TOKEN_LC2` | (secret) | Hugging Face token |
| `PORT` | `8000` | Server port |
| `MAX_MODEL_LEN` | `8192` | Maximum context length |
| `GPU_MEMORY_UTILIZATION` | `0.90` | GPU memory usage (90%) |

### Instance Type

- **Recommended**: `gpu-nvidia-l40s` (48GB VRAM)
- **Alternative**: `gpu-nvidia-rtx-4000-sff-ada` (20GB VRAM)

### Health Check

- **Path**: `/health`
- **Port**: 8000
- **Grace Period**: 300s (model loading time)
- **Interval**: 60s

## API Endpoints

vLLM's native OpenAI-compatible server provides:

```
POST /v1/chat/completions  - Chat completions
POST /v1/completions       - Text completions
GET  /v1/models            - List models
GET  /health               - Health check
```

## Usage Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://dragon-llm-dealexmachina.koyeb.app/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[
        {"role": "user", "content": "Analyze the impact of rising interest rates on bond portfolios"}
    ],
    temperature=0.7,
    max_tokens=1024
)

print(response.choices[0].message.content)
```

## Build & Push (Development)

```bash
# Build vLLM image
docker build -f Dockerfile.koyeb -t jeanbapt/dragon-llm-inference:vllm .

# Push to Docker Hub
docker push jeanbapt/dragon-llm-inference:vllm
```

## Performance Notes

- **First request**: Slower due to model loading + CUDA warmup
- **Subsequent requests**: Benefit from batching, KV cache reuse, CUDA graphs
- **L40s GPU**: 48GB VRAM provides ample room for 8B model with long context
