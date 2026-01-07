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
[![Docker Image](https://img.shields.io/docker/pulls/jeanbapt/dragon-llm-inference?label=docker&logo=docker)](https://hub.docker.com/r/jeanbapt/dragon-llm-inference)
[![Koyeb](https://img.shields.io/badge/Koyeb-Deployed-success?logo=koyeb)](https://www.koyeb.com)

## ✨ Features

- **OpenAI-compatible API** - Drop-in replacement for OpenAI endpoints
- **Tool/Function Calling** - Native support with hermes parser
- **Streaming Responses** - Real-time token generation
- **High Performance** - vLLM with Flash Attention backend
- **Observability** - Langfuse & Logfire integration

## 🎯 Available Models

This deployment uses **DragonLLM/Qwen-Open-Finance-R-8B** (8B parameters), a free open-source model optimized for finance.

**Looking for more capable models?** DragonLLM offers commercial-licensed models with enhanced performance:

- **[LLM Open Finance Collection](https://huggingface.co/collections/DragonLLM/llm-open-finance)** - Open-source financial models (8B variants)
- **[LLM Pro Finance Collection](https://huggingface.co/collections/DragonLLM/llm-pro-finance)** - Commercial models (12B-70B) with advanced capabilities

These collections include models ranging from 8B to 70B parameters, optimized for finance, economics, and business use-cases.

## 📚 Research

This deployment is based on the **LLM Pro Finance Suite**, a collection of multilingual large language models specifically designed for financial applications. The models are fine-tuned on a curated, high-quality financial corpus comprising over 50% finance-related data in English, French, and German.

### Abstract

The financial industry's growing demand for advanced natural language processing (NLP) capabilities has highlighted the limitations of generalist large language models (LLMs) in handling domain-specific financial tasks. To address this gap, we introduce the LLM Pro Finance Suite, a collection of five instruction-tuned LLMs (ranging from 8B to 70B parameters) specifically designed for financial applications. Our approach focuses on enhancing generalist instruction-tuned models, leveraging their existing strengths in instruction following, reasoning, and toxicity control, while fine-tuning them on a curated, high-quality financial corpus comprising over 50% finance-related data in English, French, and German.

We evaluate the LLM Pro Finance Suite on a comprehensive financial benchmark suite, demonstrating consistent improvement over state-of-the-art baselines in finance-oriented tasks and financial translation. Notably, our models maintain the strong general-domain capabilities of their base models, ensuring reliable performance across non-specialized tasks. This dual proficiency, enhanced financial expertise without compromise on general abilities, makes the LLM Pro Finance Suite an ideal drop-in replacement for existing LLMs in financial workflows, offering improved domain-specific performance while preserving overall versatility.

### Citation

If you use this model in your research, please cite:

```bibtex
@article{caillaut2025llm,
  title={The LLM Pro Finance Suite: Multilingual Large Language Models for Financial Applications},
  author={Caillaut, Ga{\"e}tan and Qader, Raheel and Liu, Jingshu and Nakhl{\'e}, Mariam and Sadoune, Arezki and Ahmim, Massinissa and Barthelemy, Jean-Gabriel},
  journal={arXiv preprint arXiv:2511.08621},
  year={2025}
}
```

**Paper**: [arXiv:2511.08621](https://arxiv.org/abs/2511.08621)

## 📦 Key Dependencies

This project builds upon several open-source technologies. If you use this project in your research or production, please consider citing the following:

### vLLM

High-performance LLM inference and serving engine:

```bibtex
@software{vllm2024,
  title={vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention},
  author={Kwon, Woosuk and others},
  year={2024},
  url={https://github.com/vllm-project/vllm}
}
```

**Repository**: [vllm-project/vllm](https://github.com/vllm-project/vllm)

### Langfuse

Open-source LLM observability and analytics:

```bibtex
@software{langfuse2024,
  title={Langfuse: Open-source LLM Engineering Platform},
  author={Langfuse},
  year={2024},
  url={https://github.com/langfuse/langfuse}
}
```

**Repository**: [langfuse/langfuse](https://github.com/langfuse/langfuse)

### Logfire

Observability platform by Pydantic:

```bibtex
@software{logfire2024,
  title={Logfire: Observability for Python Applications},
  author={Pydantic},
  year={2024},
  url={https://github.com/pydantic/logfire}
}
```

**Repository**: [pydantic/logfire](https://github.com/pydantic/logfire)

### Flash Attention

Efficient attention mechanism (included in vLLM):

```bibtex
@article{dao2022flashattention,
  title={FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness},
  author={Dao, Tri and Fu, Daniel Y. and Ermon, Stefano and Rudra, Atri and R{\'e}, Christopher},
  journal={Advances in Neural Information Processing Systems},
  volume={35},
  pages={16344--16359},
  year={2022}
}
```

**Paper**: [arXiv:2205.14135](https://arxiv.org/abs/2205.14135)

## 🚀 Quick Start

### Chat Completion

```bash
curl -X POST "https://your-username-open-finance-llm-8b.hf.space/v1/chat/completions" \
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
    base_url="https://your-username-open-finance-llm-8b.hf.space/v1",
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
| [HF Spaces](https://huggingface.co/spaces/your-username/open-finance-llm-8b) | L4 (24GB) | `Dockerfile` | ✅ Live |
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

## 🤝 Contributing

We welcome contributions! This project is part of the Dragon-LLM ecosystem and benefits from community input.

### How to Contribute

1. **Report Issues**: Found a bug or have a feature request?
   - Open an issue on [GitHub Issues](https://github.com/DealExMachina/simple-llm-pro-finance/issues)
   - Include details about the problem, steps to reproduce, and your environment
   - For deployment issues, specify the platform (HF Spaces, Koyeb, or local)

2. **Submit Pull Requests**:
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/amazing-feature`)
   - Make your changes and test thoroughly
   - Commit with clear messages (`git commit -m 'Add amazing feature'`)
   - Push to your fork (`git push origin feature/amazing-feature`)
   - Open a Pull Request with a clear description

3. **Improve Documentation**:
   - Fix typos or clarify instructions
   - Add examples or use cases
   - Improve code comments

4. **Enhance Features**:
   - Add support for new models
   - Improve observability integration
   - Optimize deployment configurations
   - Add new API endpoints or features

### Development Guidelines

- Follow existing code style and patterns
- Add tests for new features when possible
- Update documentation for significant changes
- Ensure Docker builds succeed for both `Dockerfile` and `Dockerfile.koyeb`
- Test on both Hugging Face Spaces and Koyeb when applicable

### Areas for Contribution

- 🐛 **Bug Fixes**: Help us improve stability and reliability
- 🚀 **Performance**: Optimize inference speed or memory usage
- 📚 **Documentation**: Improve guides, examples, and API docs
- 🔧 **Tooling**: Enhance deployment scripts, CI/CD, or development tools
- 🌐 **Multi-language**: Add support for additional languages or locales
- 📊 **Observability**: Improve Langfuse/Logfire integration or add new metrics

### Questions?

- Check existing [Issues](https://github.com/DealExMachina/simple-llm-pro-finance/issues) and [Discussions](https://github.com/DealExMachina/simple-llm-pro-finance/discussions)
- Review the [Documentation](./docs/) directory
- Reach out to the [Dragon-LLM organization](https://github.com/Dragon-LLM)

Thank you for contributing to open-source financial AI! 🎉

## 📄 License

**Code & Deployment**: MIT License - see [LICENSE](LICENSE)

**Models**: Please refer to [Dragon-LLM license terms](https://github.com/Dragon-LLM) and the underlying base model's license. The `DragonLLM/Qwen-Open-Finance-R-8B` model is fine-tuned from Qwen models. For specific licensing information, please check:
- [DragonLLM/Qwen-Open-Finance-R-8B on Hugging Face](https://huggingface.co/DragonLLM/Qwen-Open-Finance-R-8B)
- [Dragon-LLM GitHub Organization](https://github.com/Dragon-LLM)

---

Built with ❤️ by [DealExMachina](https://github.com/DealExMachina) & [Dragon-LLM](https://github.com/Dragon-LLM)
