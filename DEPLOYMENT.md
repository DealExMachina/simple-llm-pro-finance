# PRIIPs LLM Service - Deployment Configuration

## Overview
This service uses vLLM on NVIDIA L40 GPU to serve the DragonLLM/LLM-Pro-Finance-Small model.

## Configuration

### Docker Setup
- **Base Image**: `nvidia/cuda:12.1.0-runtime-ubuntu22.04`
- **Python Version**: 3.11
- **vLLM Version**: >=0.6.0

### Model Configuration
- **Model**: `DragonLLM/LLM-Pro-Finance-Small`
- **Backend**: vLLM (optimized for L40 GPU)
- **Authentication**: HF_TOKEN_LC environment variable
- **GPU Utilization**: 90% of available memory
- **Tensor Parallel Size**: 1 (single L40 GPU)
- **Max Model Length**: 4096 tokens
- **Dtype**: float16

### vLLM Advantages
1. **High Throughput**: PagedAttention for efficient memory management
2. **GPU Optimization**: Specifically optimized for NVIDIA GPUs like L40
3. **Fast Inference**: Up to 24x faster than standard Transformers
4. **Batching**: Automatic continuous batching for multiple requests
5. **OpenAI Compatible**: Drop-in replacement for OpenAI API

### Hardware
- **GPU**: NVIDIA L40S
- **VRAM**: 48GB
- **Platform**: Hugging Face Spaces

### Environment Variables Required
```bash
HF_TOKEN_LC=<your_hugging_face_token>  # For accessing Dragon LLM models
SERVICE_API_KEY=<optional>             # For API authentication
```

### API Endpoints
- `GET /` - Service info
- `GET /health` - Health check
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions (OpenAI compatible)
- `POST /extract-priips` - PRIIPs document extraction

### Model Loading
- Model loads on first API request (lazy loading)
- Downloads from Hugging Face using HF_TOKEN_LC
- Cached in `/tmp/huggingface` directory
- Automatic GPU detection and optimization

### Performance
- **Latency**: ~100-200ms per request (depends on prompt length)
- **Throughput**: High with vLLM's continuous batching
- **Memory**: Efficient PagedAttention reduces memory fragmentation

## Integration

### PydanticAI
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    "DragonLLM/LLM-Pro-Finance-Small",
    base_url="https://jeanbaptdzd-priips-llm-service.hf.space/v1"
)
agent = Agent(model=model)
```

### DSPy
```python
import dspy

lm = dspy.OpenAI(
    model="DragonLLM/LLM-Pro-Finance-Small",
    api_base="https://jeanbaptdzd-priips-llm-service.hf.space/v1"
)
dspy.settings.configure(lm=lm)
```

## Troubleshooting

### Build Errors
- Check that CUDA base image is compatible
- Verify vLLM installation with GPU support
- Ensure HF_TOKEN_LC is set in Space secrets

### Runtime Errors
- Check GPU availability: `torch.cuda.is_available()`
- Verify model access with HF token
- Check logs for OOM (out of memory) errors

### Performance Issues
- Increase `gpu_memory_utilization` if underutilizing
- Adjust `max_model_len` based on use case
- Enable tensor parallelism for multi-GPU setups

## Monitoring
- Check Space status via Hugging Face dashboard
- Monitor GPU utilization and memory usage
- Review application logs for errors

