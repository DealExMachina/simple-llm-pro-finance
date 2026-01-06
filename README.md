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

# 🐉 Open Finance LLM 8B

High-performance OpenAI-compatible API for financial AI, powered by **DragonLLM/Qwen-Open-Finance-R-8B** and **vLLM**.

[![HF Space](https://img.shields.io/badge/🤗-Live%20Demo-blue)](https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b)

## ✨ Features

- **OpenAI-compatible API** - Drop-in replacement for OpenAI endpoints
- **Tool/Function Calling** - Native support with hermes parser
- **Streaming Responses** - Real-time token generation
- **High Performance** - vLLM with Flash Attention backend
- **Observability** - Langfuse & Logfire integration

## 🚀 Quick Start

### Chat Completion

```bash
curl -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is a PRIIP in finance?"}],
    "max_tokens": 200
  }'
```

### Python Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "What is compound interest?"}],
    max_tokens=500
)
print(response.choices[0].message.content)
```

### Tool Calling

```python
response = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "Get the stock price for AAPL"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get current stock price",
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string"}},
                "required": ["ticker"]
            }
        }
    }],
    tool_choice="auto"
)
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completion (supports streaming & tools) |
| `/v1/completions` | POST | Text completion |

## 🏗️ Deployment

| Platform | Hardware | Dockerfile | Status |
|----------|----------|------------|--------|
| [HF Spaces](https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b) | L4 (24GB) | `Dockerfile` | ✅ Live |
| Koyeb | L40s (48GB) | `Dockerfile.koyeb` | ✅ Production |

Both platforms use **vLLM** for unified, high-performance inference.

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN_LC2` | - | Hugging Face token (required) |
| `MODEL` | `DragonLLM/Qwen-Open-Finance-R-8B` | Model to serve |
| `PORT` | `8000` / `7860` (HF) | Server port |
| `MAX_MODEL_LEN` | `8192` | Max context length |
| `GPU_MEMORY_UTILIZATION` | `0.90` | GPU memory fraction |
| `ENABLE_AUTO_TOOL_CHOICE` | `true` | Enable tool calling |
| `TOOL_CALL_PARSER` | `hermes` | Tool parser for Qwen |

### Observability (Optional)

| Variable | Description |
|----------|-------------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_HOST` | Langfuse host URL |
| `LOGFIRE_TOKEN` | Logfire token |

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/DealExMachina/simple-llm-pro-finance.git
cd simple-llm-pro-finance

# Create virtual environment
python3.13 -m venv venv313
source venv313/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with Docker
docker build -t open-finance-llm .
docker run --gpus all -p 8000:8000 \
  -e HF_TOKEN_LC2=your_token \
  open-finance-llm

# Run tests
pytest tests/integration/ -v
```

## 📊 Technical Specs

| Spec | Value |
|------|-------|
| **Model** | DragonLLM/Qwen-Open-Finance-R-8B |
| **Parameters** | 8B |
| **Backend** | vLLM 0.13.0 |
| **Attention** | Flash Attention |
| **Tool Parser** | Hermes |
| **Min VRAM** | 20GB (L4) |
| **Recommended** | 48GB (L40s) |

## 📁 Project Structure

```
simple-llm-pro-finance/
├── Dockerfile          # HF Spaces deployment
├── Dockerfile.koyeb    # Koyeb deployment
├── start-vllm.sh       # vLLM startup script
├── app/                # Config & utilities
├── docs/               # Documentation
├── scripts/            # GGUF conversion tools
└── tests/              # Integration & benchmarks
```

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

Built with ❤️ by [DealExMachina](https://github.com/DealExMachina) & [Dragon-LLM](https://github.com/Dragon-LLM)
