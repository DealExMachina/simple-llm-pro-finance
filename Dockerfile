# Unified Dockerfile for Hugging Face Spaces using vLLM
# Migrated from Transformers backend to vLLM for better performance and deployment parity
# Now matches Koyeb deployment (Dockerfile.koyeb) for consistency

FROM vllm/vllm-openai:latest

# Cache bust: Force rebuild on each push (prevents HF Spaces from using cached old image)
ARG CACHE_BUST
RUN echo "Build timestamp: ${CACHE_BUST:-$(date +%s)}"

# Environment variables
ENV HF_HOME=/tmp/huggingface \
    VLLM_ATTENTION_BACKEND=FLASH_ATTN

# Create cache directories
RUN mkdir -p /tmp/huggingface && chmod 777 /tmp/huggingface

# Install Langfuse and other observability dependencies
# Note: vLLM base image already includes most dependencies
RUN pip install --no-cache-dir \
    langfuse>=2.50.0 \
    logfire>=0.0.1

# Copy startup script (handles both HF Spaces and Koyeb)
COPY start-vllm.sh /start-vllm.sh
RUN chmod +x /start-vllm.sh

# Expose ports: 8000 (default) and 7860 (HF Spaces)
# The start-vllm.sh script auto-detects the environment
EXPOSE 8000 7860

# Use ENTRYPOINT so it can't be overridden
ENTRYPOINT ["/start-vllm.sh"]
