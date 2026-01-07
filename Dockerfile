# Unified Dockerfile for Hugging Face Spaces and Koyeb
# Uses vLLM for high-performance inference on both platforms
# The start-vllm.sh script auto-detects the deployment environment

FROM vllm/vllm-openai:latest

# Cache bust: Force rebuild on each push (prevents HF Spaces from using cached old image)
# Harmless for Koyeb (unused ARG)
ARG CACHE_BUST
RUN echo "Build timestamp: ${CACHE_BUST:-$(date +%s)}"

# Environment variables
ENV HF_HOME=/tmp/huggingface \
    VLLM_ATTENTION_BACKEND=FLASH_ATTN

# Create cache directories
RUN mkdir -p /tmp/huggingface && chmod 777 /tmp/huggingface

# Install observability dependencies
# Note: vLLM base image already includes most dependencies
RUN pip install --no-cache-dir \
    langfuse>=2.50.0 \
    logfire>=0.0.1

# Copy startup script (handles both HF Spaces and Koyeb)
COPY start-vllm.sh /start-vllm.sh
RUN chmod +x /start-vllm.sh

# Expose ports: 8000 (default/Koyeb) and 7860 (HF Spaces)
# The start-vllm.sh script auto-detects the environment and uses the correct port
EXPOSE 8000 7860

# Use ENTRYPOINT so it can't be overridden
ENTRYPOINT ["/start-vllm.sh"]
