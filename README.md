---
title: Qwen Open Finance R 8B Inference
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: apache-2.0
app_port: 7860
hardware: l4
---

# Qwen Open Finance R 8B Inference

OpenAI-compatible API and financial document processor powered by `DragonLLM/qwen3-8b-fin-v1.0` via vLLM.

## 🚀 Quick Start

This service provides:
- **OpenAI-compatible API** at `/v1/models` and `/v1/chat/completions`
- **PRIIPs extraction** at `/extract-priips` for structured financial document parsing
- **Provider abstraction** for easy integration with PydanticAI/DSPy

## 📋 API Endpoints

### OpenAI-Compatible API

#### List Models
```bash
curl -X GET "https://your-space-url.hf.space/v1/models"
```

#### Chat Completions
```bash
curl -X POST "https://your-space-url.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/gemma3-12b-fin-v0.3",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

### PRIIPs Extraction

#### Extract Structured Data from PDFs
```bash
curl -X POST "https://your-space-url.hf.space/extract-priips" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["https://example.com/priips-document.pdf"],
    "options": {"language": "en", "ocr": false}
  }'
```

**Response:**
```json
{
  "product_name": "Example Investment Fund",
  "manufacturer": "Example Asset Management",
  "isin": "DE0001234567",
  "sri": 3,
  "recommended_holding_period": "5 years",
  "costs": {
    "entry_cost_pct": 2.5,
    "ongoing_cost_pct": 1.2,
    "exit_cost_pct": 0.5
  },
  "performance_scenarios": [
    {
      "name": "Bull Market",
      "description": "Optimistic scenario",
      "return_pct": 15.5
    }
  ],
  "date": "2024-01-01",
  "language": "en",
  "source_url": "https://example.com/priips-document.pdf"
}
```

## 🔧 Configuration

The service uses these environment variables:

- `VLLM_BASE_URL`: vLLM server endpoint (default: `http://localhost:8000/v1`)
- `MODEL`: Model name (default: `DragonLLM/LLM-Pro-Finance-Small`)
- `SERVICE_API_KEY`: Optional API key for authentication
- `LOG_LEVEL`: Logging level (default: `info`)

## 🔗 Integration Examples

### PydanticAI
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    "DragonLLM/gemma3-12b-fin-v0.3",
    base_url="https://your-space-url.hf.space/v1"
)

agent = Agent(model=model)
```

### DSPy
```python
import dspy

lm = dspy.OpenAI(
    model="DragonLLM/gemma3-12b-fin-v0.3",
    api_base="https://your-space-url.hf.space/v1"
)
```

## 📊 Features

- ✅ **OpenAI-compatible API** - Drop-in replacement for OpenAI API
- ✅ **PRIIPs document extraction** - Structured JSON from financial PDFs
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

**Note**: This service requires a vLLM server running `DragonLLM/LLM-Pro-Finance-Small` model. For production use, ensure your vLLM server is properly configured and accessible.
