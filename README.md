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

OpenAI-compatible API powered by DragonLLM/qwen3-8b-fin-v1.0 using Transformers.

## Overview

This service provides an OpenAI-compatible API for the DragonLLM Qwen3-8B finance-specialized language model. The model supports both English and French financial terminology and includes chain-of-thought reasoning.

## API Endpoints

### List Models
```bash
curl -X GET "https://your-username-open-finance-llm-8b.hf.space/v1/models"
```

### Chat Completions
```bash
curl -X POST "https://your-username-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [{"role": "user", "content": "What is compound interest?"}],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Streaming
```bash
curl -X POST "https://your-username-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [{"role": "user", "content": "Explain Value at Risk"}],
    "stream": true
  }'
```

## Response Format

Responses include chain-of-thought reasoning in `<think>` tags followed by the answer. Reasoning typically consumes 40-60% of tokens.

Recommended `max_tokens`:
- Simple queries: 300-400
- Complex queries: 500-800
- Detailed analysis: 800-1200

## Configuration

### Environment Variables

**Required:**
- `HF_TOKEN_LC2` - Hugging Face token with access to DragonLLM models

**Optional:**
- `MODEL` - Model name (default: DragonLLM/qwen3-8b-fin-v1.0)
- `SERVICE_API_KEY` - API key for authentication
- `LOG_LEVEL` - Logging level (default: info)
- `HF_HOME` - Hugging Face cache directory (default: /tmp/huggingface)
- `FORCE_MODEL_RELOAD` - Force reload model from Hub on startup (default: false)

Token priority: `HF_TOKEN_LC2` > `HF_TOKEN_LC` > `HF_TOKEN` > `HUGGING_FACE_HUB_TOKEN`

Note: Accept model terms at https://huggingface.co/DragonLLM/qwen3-8b-fin-v1.0 before use.

## Integration

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

## Technical Specifications

**Model:**
- DragonLLM/qwen3-8b-fin-v1.0 (8B parameters)
- Fine-tuned on financial data
- English and French support

**Backend:**
- Transformers 4.40.0+
- PyTorch 2.5.0+ (CUDA 12.4)
- Accelerate 0.30.0+

**Performance:**
- Inference: ~15 tokens/second (L4 GPU)
- Response time: 3-27 seconds
- Minimum VRAM: 20GB

**Hardware:**
- Development: L4x1 GPU (24GB VRAM)
- Production: L40s GPU (48GB VRAM)

## Development

### Local Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Testing
```bash
pytest -v
pytest --cov=app tests/
```

## Documentation

- [FINAL_STATUS.md](FINAL_STATUS.md) - Deployment status
- [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) - Test results and metrics

## License

MIT License - see [LICENSE](LICENSE) file.
