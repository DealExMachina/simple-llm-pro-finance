# Use official vLLM OpenAI API server image
FROM vllm/vllm-openai:latest

# Set environment variables
ENV MODEL=DragonLLM/Qwen-Open-Finance-R-8B \
    PORT=8000 \
    HOST=0.0.0.0

# Expose vLLM API port
EXPOSE 8000

# Run vLLM OpenAI API server
# Supports environment variables:
# - MODEL: Model name (default: DragonLLM/Qwen-Open-Finance-R-8B)
# - VLLM_API_KEY: Optional API key for authentication
# - HF_TOKEN: Hugging Face token (if model is gated)
# - TENSOR_PARALLEL_SIZE: Number of GPUs for tensor parallelism
CMD python -m vllm.entrypoints.openai.api_server \
    --model ${MODEL} \
    --port ${PORT} \
    --host ${HOST}
