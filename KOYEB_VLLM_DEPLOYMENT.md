# Koyeb vLLM Deployment

## Overview

The Koyeb deployment uses **vLLM's official Docker image** (`vllm/vllm-openai`) for maximum compatibility and performance.

## Koyeb Configuration

### Using Official vLLM Image (Recommended)

**Docker Image:** `vllm/vllm-openai:latest`

**Command args:** 
```
--model DragonLLM/Qwen-Open-Finance-R-8B --trust-remote-code --dtype bfloat16 --max-model-len 8192
```

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `HF_TOKEN` | (secret) | Hugging Face token for gated model |
| `VLLM_API_KEY` | (optional) | API key to protect the endpoint |

### Instance Type

- **Recommended**: `gpu-nvidia-l40s` (48GB VRAM)
- **Region**: `na` (North America) - where L40s is most available

### Health Check

- **Type**: TCP
- **Port**: 8000
- **Grace Period**: 900 seconds (15 minutes for model loading)

## Koyeb Dashboard Setup

1. **Create new service** in `dragon-llm` app
2. **Docker image**: `vllm/vllm-openai:latest`
3. **Command args**: `--model DragonLLM/Qwen-Open-Finance-R-8B --trust-remote-code --dtype bfloat16 --max-model-len 8192`
4. **Environment**: Add `HF_TOKEN` secret (your HuggingFace token)
5. **Instance**: `gpu-nvidia-l40s` in `na` region
6. **Port**: 8000 (HTTP)
7. **Health check**: TCP on port 8000, grace period 900s

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
    base_url="https://dragon-llm-dealexmachina.koyeb.app/v1",
    api_key="not-needed"  # or your VLLM_API_KEY
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

## Troubleshooting

### "Application exited with code 8" with no logs

This usually means GPU allocation failed at the hypervisor level. Try:
1. Different region (try `na` for L40s availability)
2. Different GPU type (`gpu-nvidia-a100`)
3. Wait and retry later (GPU availability varies)

### Model download issues

Ensure `HF_TOKEN` is set and the token has access to the gated model.

## Custom Image (Alternative)

If you prefer a custom image, use:
```
jeanbapt/dragon-llm-inference:vllm
```

Built from `Dockerfile.koyeb` in this repository.
