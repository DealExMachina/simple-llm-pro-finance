# Use NVIDIA CUDA 12.4 base image (12.1 is deprecated)
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# Build argument to force cache invalidation - update this timestamp to force rebuild
ARG CACHE_BUST=20250130_1425
RUN echo "Build cache bust: ${CACHE_BUST}" && \
    echo "Transformers backend - forced rebuild $(date)"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV BUILD_ID=transformers_backend_20250130

# Install Python 3.11 and build dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Install PyTorch with CUDA 12.4 support
RUN pip install --no-cache-dir \
    torch>=2.5.0 \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu124

# Install Transformers and accelerate for optimized inference
RUN pip install --no-cache-dir \
    transformers>=4.40.0 \
    accelerate>=0.30.0 \
    bitsandbytes  # Optional: for quantization support

# Install application dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.30.0 \
    pydantic>=2.8.0 \
    pydantic-settings>=2.4.0 \
    httpx>=0.27.0 \
    python-dotenv>=1.0.1 \
    tenacity>=8.3.0 \
    PyMuPDF>=1.24.0 \
    python-multipart>=0.0.6

# Force cache invalidation before copying code - this ensures fresh code is always copied
RUN echo "Code cache bust: transformers_backend_20250130_$(date +%s)" && \
    rm -rf /app/app 2>/dev/null || true

# Copy application code (this will NOT use cache if previous step changed)
COPY app/ ./app/

# Verify we have the Transformers code, not vLLM
RUN grep -q "from transformers import" /app/app/providers/vllm.py && \
    grep -q "def initialize_model" /app/app/providers/vllm.py && \
    echo "✅ Verified: Transformers code is present" || \
    (echo "❌ ERROR: Old vLLM code detected!" && exit 1)

# Create a non-root user and set up cache directories
RUN useradd -m -u 1000 user && \
    mkdir -p /tmp/huggingface /tmp/torch/inductor /tmp/triton && \
    chown -R user:user /app /tmp/huggingface /tmp/torch /tmp/triton

USER user

# Set environment variables for optimal Transformers performance
ENV HF_HOME=/tmp/huggingface
ENV TORCHINDUCTOR_CACHE_DIR=/tmp/torch/inductor
ENV CUDA_VISIBLE_DEVICES=0
# Optimize CUDA memory allocation
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# Enable Transformers optimizations
ENV TRANSFORMERS_CACHE=/tmp/huggingface

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
# Transformers backend - DO NOT USE CACHED IMAGE
