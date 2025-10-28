# Use NVIDIA CUDA 12.4 base image (12.1 is deprecated)
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

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

# Install vLLM and dependencies in one layer for efficiency
RUN pip install --no-cache-dir \
    vllm \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.30.0 \
    pydantic>=2.8.0 \
    pydantic-settings>=2.4.0 \
    httpx>=0.27.0 \
    python-dotenv>=1.0.1 \
    tenacity>=8.3.0 \
    PyMuPDF>=1.24.0

# Copy application code
COPY app/ ./app/

# Create a non-root user and set up cache directories
RUN useradd -m -u 1000 user && \
    mkdir -p /tmp/huggingface /tmp/torch/inductor /tmp/triton && \
    chown -R user:user /app /tmp/huggingface /tmp/torch /tmp/triton

USER user

# Set environment variables for optimal vLLM + torch.compile performance
ENV HF_HOME=/tmp/huggingface
ENV TORCHINDUCTOR_CACHE_DIR=/tmp/torch/inductor
ENV TRITON_CACHE_DIR=/tmp/triton
ENV TORCH_COMPILE_DEBUG=0
ENV CUDA_VISIBLE_DEVICES=0
# Prevent OOM during multi-process initialization
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ENV CUDA_LAUNCH_BLOCKING=1
# Force vLLM to use legacy (v0) engine - more stable, single-process
ENV VLLM_USE_V1=0

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
