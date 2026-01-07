# Documentation Index

Welcome to the Open Finance LLM 8B documentation. This directory contains guides and technical specifications for deploying and using the financial LLM API.

## 📚 Core Documentation

### Deployment

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Comprehensive deployment guide for Hugging Face Spaces and Koyeb platforms. Covers architecture, configuration, API endpoints, troubleshooting, and observability setup.

### Configuration

- **[TOOL_CALLING_CONFIG.md](./TOOL_CALLING_CONFIG.md)** - Detailed guide on tool calling (function calling) configuration for Qwen models. Includes default settings, platform support, examples, and troubleshooting.

### Setup & Operations

- **[DOCKERHUB_SETUP.md](./DOCKERHUB_SETUP.md)** - Docker Hub authentication setup for GitHub Actions. Step-by-step instructions for configuring secrets and variables.

## 🔧 Technical Specifications

### Model Specifications

- **[qwen3_specifications.md](./qwen3_specifications.md)** - Qwen-3 8B model specifications including context window (32K base, 128K with YaRN), token limits, and configuration recommendations.

- **[generation_limits.md](./generation_limits.md)** - Generation limits and constraints for the Qwen-3 8B model. Practical examples and recommendations for different use cases.

**Note**: These specification documents reference the model capabilities. The deployment uses vLLM as the inference backend (not Transformers).

## 🚀 Quick Links

- **Main README**: [../README.md](../README.md) - Project overview, quick start, and API examples
- **GitHub Repository**: [DealExMachina/simple-llm-pro-finance](https://github.com/DealExMachina/simple-llm-pro-finance)
- **Dragon-LLM Organization**: [Dragon-LLM](https://github.com/Dragon-LLM)
- **Model on Hugging Face**: [DragonLLM/Qwen-Open-Finance-R-8B](https://huggingface.co/DragonLLM/Qwen-Open-Finance-R-8B)

## 📖 Additional Resources

- **Research Paper**: [arXiv:2511.08621](https://arxiv.org/abs/2511.08621) - The LLM Pro Finance Suite paper
- **vLLM Documentation**: [vllm-project/vllm](https://github.com/vllm-project/vllm)
- **Langfuse Documentation**: [langfuse/langfuse](https://github.com/langfuse/langfuse)
- **Logfire Documentation**: [pydantic/logfire](https://github.com/pydantic/logfire)
