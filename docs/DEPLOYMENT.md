# Deployment Guide

## Overview

This project uses **vLLM** for unified deployment across both Hugging Face Spaces and Koyeb platforms. vLLM provides a high-performance, OpenAI-compatible API server optimized for production use.

## Architecture

```
vLLM Server → Model
  (Port 8000 / 7860)
```

Both platforms use the same vLLM backend, ensuring consistency and better performance.

## Platforms

| Platform | Dockerfile | Port | Use Case |
|----------|------------|------|----------|
| Hugging Face Spaces | `Dockerfile` | 7860 | Development, L4 GPU |
| Koyeb | `Dockerfile.koyeb` | 8000 | Production, L40s GPU |

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN_LC2` | Yes | - | Hugging Face token for model access |
| `MODEL` | No | `DragonLLM/Qwen-Open-Finance-R-8B` | Model identifier |
| `PORT` | No | `8000` (Koyeb) / `7860` (HF Spaces) | Server port (auto-detected) |
| `MAX_MODEL_LEN` | No | `8192` | Max context length |
| `GPU_MEMORY_UTILIZATION` | No | `0.90` | GPU memory fraction |
| `DTYPE` | No | `bfloat16` | Data type |
| `ENABLE_AUTO_TOOL_CHOICE` | No | `true` | Enable tool calling |
| `TOOL_CALL_PARSER` | No | `hermes` | Tool call parser for Qwen models |
| `TENSOR_PARALLEL_SIZE` | No | `1` | Number of GPUs (Koyeb: uses `KOYEB_GPU_COUNT`) |

### Port Detection

The `start-vllm.sh` script automatically detects the environment:
- **Hugging Face Spaces**: Detects `SPACE_ID` or `SPACES_APP_PORT`, uses port `7860`
- **Koyeb**: Uses port `8000` (default)
- **Manual Override**: Set `PORT` environment variable to override

## API Endpoints

vLLM provides standard OpenAI-compatible endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completion (supports streaming) |

**Note**: vLLM does not provide custom endpoints like `/health`, `/ready`, or `/v1/stats`. Use `/v1/models` as a health check.

## Deployment Steps

### Hugging Face Spaces

1. Push code to the repository
2. HF Spaces automatically builds using `Dockerfile`
3. vLLM server starts on port 7860
4. Space is accessible at: `https://your-space.hf.space`

### Koyeb

1. GitHub Actions builds and pushes Docker image to Docker Hub
2. Koyeb deploys using `Dockerfile.koyeb`
3. vLLM server starts on port 8000
4. Service is accessible at: `https://your-app.koyeb.app`

## Verification

### Health Check

```bash
# Test if vLLM is running
curl "https://your-endpoint/v1/models"

# Expected: JSON with model list
```

### Chat Completion

```bash
curl -X POST "https://your-endpoint/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

## Observability

### Langfuse

Configure Langfuse for tracing and evaluation:

```bash
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com  # or self-hosted URL
ENABLE_LANGFUSE=true
```

### Logfire

Configure Logfire for logging:

```bash
LOGFIRE_TOKEN=your_token
ENVIRONMENT=production
```

## Troubleshooting

### Space Stuck on "Starting"
- **Cause**: Model loading takes time (especially first time)
- **Solution**: Wait 5-10 minutes, check logs

### 404 on `/health`
- **Expected**: vLLM doesn't provide this endpoint
- **Solution**: Use `/v1/models` as health check

### Port Issues
- **Check**: Logs should show "Port: 7860" (HF Spaces) or "Port: 8000" (Koyeb)
- **Verify**: Environment variables are set correctly

## Technical Specs

- **Model**: DragonLLM/Qwen-Open-Finance-R-8B (8B parameters)
- **Backend**: vLLM (vllm-openai:latest) with hermes tool parser
- **Minimum VRAM**: 20GB (L4), recommended 48GB (L40s)
- **Base Image**: `vllm/vllm-openai:latest`

## Tool Calling

Tool calling (function calling) is **enabled by default** for both platforms using the `hermes` parser (optimized for Qwen models). Both HF Spaces and Koyeb use the same `start-vllm.sh` script, ensuring consistent configuration.

See [TOOL_CALLING_CONFIG.md](./TOOL_CALLING_CONFIG.md) for detailed configuration and troubleshooting.

## Benefits of vLLM

1. **Performance**: Faster and more efficient than Transformers
2. **Consistency**: Same backend on both platforms
3. **Simplicity**: No FastAPI wrapper needed
4. **Maintenance**: One deployment pattern to maintain
5. **Future-Proof**: Aligned with Hugging Face's direction
6. **Tool Calling**: Unified configuration across platforms

