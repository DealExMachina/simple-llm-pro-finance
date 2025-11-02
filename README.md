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

OpenAI-compatible API powered by `DragonLLM/qwen3-8b-fin-v1.0` via vLLM.

## 🚀 Quick Start

This service provides:
- **OpenAI-compatible API** at `/v1/models` and `/v1/chat/completions`
- **Streaming support** for real-time completions
- **Provider abstraction** for easy integration with PydanticAI/DSPy

## 📋 API Endpoints

### OpenAI-Compatible API

#### List Models
```bash
curl -X GET "https://your-username-open-finance-llm-8b.hf.space/v1/models"
```

#### Chat Completions
```bash
curl -X POST "https://your-username-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

#### Streaming Chat Completions
```bash
curl -X POST "https://your-username-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [{"role": "user", "content": "Tell me about finance"}],
    "stream": true
  }'
```

## 🔧 Configuration

The service uses these environment variables:

### Required for Model Access
- **`HF_TOKEN_LC2`** (Recommended): Hugging Face token with access to DragonLLM models. Set this as a secret in your Hugging Face Space.
  - Priority order: `HF_TOKEN_LC2` > `HF_TOKEN_LC` > `HF_TOKEN` > `HUGGING_FACE_HUB_TOKEN`
  - The service automatically authenticates with Hugging Face Hub using this token
  - **Important**: You must accept the model's terms at https://huggingface.co/DragonLLM/qwen3-8b-fin-v1.0 before the token will work

### Optional Configuration
- `VLLM_BASE_URL`: vLLM server endpoint (default: `http://localhost:8000/v1`)
- `MODEL`: Model name (default: `DragonLLM/qwen3-8b-fin-v1.0`)
- `SERVICE_API_KEY`: Optional API key for authentication (set via `x-api-key` header)
- `LOG_LEVEL`: Logging level (default: `info`)
- `VLLM_USE_EAGER`: Control optimization mode (default: `auto`)
  - `auto`: Try optimized mode (CUDA graphs), fallback to eager if needed (recommended)
  - `false`: Force optimized mode (CUDA graphs enabled, may fail if unsupported)
  - `true`: Force eager mode (slower but more stable)

### Setting Up HF_TOKEN_LC2 in Hugging Face Spaces

1. Go to your Space settings → Secrets and variables
2. Add a new secret named `HF_TOKEN_LC2`
3. Set the value to your Hugging Face token with access to DragonLLM models
4. Make sure you've accepted the terms for `DragonLLM/qwen3-8b-fin-v1.0` on Hugging Face

## 🔗 Integration Examples

### PydanticAI
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    "DragonLLM/qwen3-8b-fin-v1.0",
    base_url="https://your-username-open-finance-llm-8b.hf.space/v1"
)

agent = Agent(model=model)
```

### DSPy
```python
import dspy

lm = dspy.OpenAI(
    model="DragonLLM/qwen3-8b-fin-v1.0",
    api_base="https://your-username-open-finance-llm-8b.hf.space/v1"
)
```

## 📊 Features

- ✅ **OpenAI-compatible API** - Drop-in replacement for OpenAI API
- ✅ **Provider abstraction** - Easy to swap backends
- ✅ **Streaming support** - Real-time chat completions
- ✅ **Error handling** - Robust error handling and validation
- ✅ **Authentication** - Optional API key protection

## 🛠️ Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8080
```

### Testing
```bash
# Run tests
pytest -v

# Test coverage: 91% (52/57 tests passing)
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Note**: This service runs vLLM 0.9.2 (latest stable) with `DragonLLM/qwen3-8b-fin-v1.0` model. The service initializes the model automatically on startup. For production use, ensure proper GPU resources (L4 or better) are available.

### Version Information
- **vLLM:** 0.9.2 (upgraded from 0.6.5 - July 2025 release)
- **PyTorch:** 2.5.0+ (CUDA 12.4)
- **CUDA:** 12.4
