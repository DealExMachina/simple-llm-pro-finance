# Open Finance LLM 8B - Koyeb vLLM Deployment

OpenAI-compatible API powered by DragonLLM/Qwen-Open-Finance-R-8B using vLLM on Koyeb GPU infrastructure.

## Overview

This service provides an OpenAI-compatible API for the DragonLLM Qwen3-8B finance-specialized language model deployed on Koyeb using vLLM. The model supports both English and French financial terminology and includes chain-of-thought reasoning.

## Features

- ✅ **OpenAI-Compatible API** - Drop-in replacement for OpenAI API via vLLM
- ✅ **High-Performance Inference** - vLLM optimized for GPU acceleration
- ✅ **Scale-to-Zero** - Automatic scaling down during inactivity
- ✅ **Autoscaling** - Dynamic scaling based on traffic
- ✅ **Health Monitoring** - Built-in `/health` endpoint for Koyeb
- ✅ **Streaming Support** - Real-time response streaming
- ✅ **API Key Authentication** - Optional API key protection via `VLLM_API_KEY`

## API Endpoints

vLLM provides OpenAI-compatible endpoints:

### List Models
```bash
curl -X GET "https://your-koyeb-app.koyeb.app/v1/models"
```

### Chat Completions
```bash
curl -X POST "https://your-koyeb-app.koyeb.app/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is compound interest?"}],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Streaming
```bash
curl -X POST "https://your-koyeb-app.koyeb.app/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "Explain Value at Risk"}],
    "stream": true
  }'
```

### Health Check
```bash
curl -X GET "https://your-koyeb-app.koyeb.app/health"
```

## Configuration

### Environment Variables

**Required:**
- `MODEL` - Model name (default: `DragonLLM/Qwen-Open-Finance-R-8B`)

**Optional:**
- `VLLM_API_KEY` - API key for authentication (if set, all requests require Bearer token)
- `HF_TOKEN` - Hugging Face token (required if model is gated)
- `TENSOR_PARALLEL_SIZE` - Number of GPUs for tensor parallelism (default: 1)
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

**Note:** Accept model terms at https://huggingface.co/DragonLLM/Qwen-Open-Finance-R-8B before use.

## Deployment on Koyeb

### Prerequisites

- Koyeb account with GPU access
- Hugging Face token (if model is gated)
- Koyeb API token (for GitHub Actions deployment)

### Automatic Deployment via GitHub Actions

This repository includes a GitHub Actions workflow that automatically deploys to Koyeb on every push to the `master` branch.

**Setup:**

1. **Get your Koyeb API token:**
   - Go to [Koyeb API Tokens](https://app.koyeb.com/account/api)
   - Generate a new API token

2. **Add GitHub Secrets:**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `KOYEB_API_TOKEN`: Your Koyeb API token
     - `VLLM_API_KEY`: (Optional) API key for vLLM authentication
     - `HF_TOKEN`: (Optional) Hugging Face token if model is gated

3. **Push to master:**
   - The workflow will automatically deploy on push to `master` branch
   - You can also manually trigger it from the Actions tab

The workflow will:
- Create the Koyeb app if it doesn't exist
- Create or update the service with GPU configuration
- Deploy from the Dockerfile automatically

### Manual Deployment Steps

1. **Build and push Docker image** (or use Koyeb's Git integration):
   ```bash
   docker build -t your-registry/dragon-inference:latest .
   docker push your-registry/dragon-inference:latest
   ```

2. **Deploy on Koyeb**:
   - Use Koyeb UI, CLI, or API
   - Instance type: `gpu-nvidia-l40s` (for 8B model)
   - Port: 8000
   - Health check: TCP on port 8000, grace period 900s
   - Scaling: min 0, max 5 (adjust as needed)
   - Region: `fra` (or your preferred region)

3. **Set environment variables** in Koyeb:
   - `MODEL=DragonLLM/Qwen-Open-Finance-R-8B`
   - `VLLM_API_KEY` (optional, set as secret)
   - `HF_TOKEN` (if needed, set as secret)

### Using Koyeb CLI

```bash
koyeb service create \
  --name dragon-inference \
  --type web \
  --instance-type gpu-nvidia-l40s \
  --region fra \
  --port 8000 \
  --health-check-tcp-port 8000 \
  --health-check-grace-period 900 \
  --scaling-min 0 \
  --scaling-max 5 \
  --env MODEL=DragonLLM/Qwen-Open-Finance-R-8B \
  --env-secret VLLM_API_KEY=your-api-key \
  --env-secret HF_TOKEN=your-hf-token \
  your-registry/dragon-inference:latest
```

## Integration

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-koyeb-app.koyeb.app/v1",
    api_key="YOUR_API_KEY"  # If VLLM_API_KEY is set
)

response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "What is compound interest?"}],
    max_tokens=500
)
```

### LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    base_url="https://your-koyeb-app.koyeb.app/v1",
    api_key="YOUR_API_KEY"
)
```

## Technical Specifications

**Model:**
- DragonLLM/Qwen-Open-Finance-R-8B (8B parameters)
- Fine-tuned on financial data
- English and French support

**Backend:**
- vLLM (high-performance inference engine)
- Optimized for GPU acceleration
- Continuous batching for throughput

**Hardware (Koyeb):**
- Instance type: `gpu-nvidia-l40s` (48GB VRAM)
- Supports scale-to-zero and autoscaling

**Performance:**
- High throughput with vLLM's continuous batching
- Low latency inference
- Efficient GPU memory usage

## Local Development

### Run with Docker

```bash
docker build -t dragon-inference .
docker run -p 8000:8000 \
  -e MODEL=DragonLLM/Qwen-Open-Finance-R-8B \
  -e VLLM_API_KEY=your-key \
  -e HF_TOKEN=your-token \
  --gpus all \
  dragon-inference
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/v1/models

# Chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-key" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Project Structure

```
.
├── Dockerfile              # vLLM Docker configuration
├── koyeb.yaml             # Koyeb deployment configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## License

MIT License - see [LICENSE](LICENSE) file.
