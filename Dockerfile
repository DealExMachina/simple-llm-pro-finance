# Use NVIDIA CUDA 12.4 base image
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# Build argument to force cache invalidation
ARG CACHE_BUST=20250130_1425

# Set environment variables early for better caching
# Note: HF_HOME can be overridden via .env or environment variable
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    BUILD_ID=transformers_backend_20250130 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    HF_HOME=/tmp/huggingface \
    TORCHINDUCTOR_CACHE_DIR=/tmp/torch/inductor \
    CUDA_VISIBLE_DEVICES=0 \
    TRANSFORMERS_CACHE=/tmp/huggingface

# Single RUN command for system dependencies (better layer caching)
RUN echo "Build cache bust: ${CACHE_BUST}" && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        git \
        curl && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    python3 -m pip install --upgrade pip

WORKDIR /app

# Install PyTorch with CUDA 12.4 (single layer, cached)
RUN pip install --no-cache-dir \
    torch>=2.5.0 \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu124

# Install ML dependencies (single layer, cached)
# Transformers 4.45.0+ recommended for Qwen models (supports latest features)
# PyTorch 2.5.0+ for CUDA 12.4 compatibility
RUN pip install --no-cache-dir \
    transformers>=4.45.0 \
    accelerate>=0.30.0 \
    bitsandbytes

# Install application dependencies (single layer, cached)
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.30.0 \
    pydantic>=2.8.0 \
    pydantic-settings>=2.4.0 \
    httpx>=0.27.0 \
    python-dotenv>=1.0.1 \
    tenacity>=8.3.0 \
    PyMuPDF>=1.24.0 \
    python-multipart>=0.0.6 \
    huggingface-hub>=0.20.0 \
    logfire>=0.0.1

# Copy application code (this layer invalidates when code changes)
COPY app/ ./app/

# Verify application code
RUN test -f /app/app/providers/transformers_provider.py && \
    grep -q "from transformers import" /app/app/providers/transformers_provider.py && \
    grep -q "def initialize_model" /app/app/providers/transformers_provider.py || \
    (echo "ERROR: transformers_provider.py not found or invalid!" && exit 1)

# Create non-root user and cache directories in single layer
# Use ${HF_HOME} variable (defaults to /tmp/huggingface if not set)
RUN useradd -m -u 1000 user && \
    mkdir -p ${HF_HOME:-/tmp/huggingface} /tmp/torch/inductor /tmp/triton && \
    chown -R user:user /app ${HF_HOME:-/tmp/huggingface} /tmp/torch /tmp/triton

USER user

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
