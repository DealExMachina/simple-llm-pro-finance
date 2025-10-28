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

# Install PyTorch with CUDA 12.4 support FIRST (critical for vLLM compatibility)
RUN pip install --no-cache-dir \
    torch==2.4.0 \
    --index-url https://download.pytorch.org/whl/cu124

# Install vLLM (will use the PyTorch we just installed)
RUN pip install --no-cache-dir vllm==0.6.4.post1

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

# Copy application code
COPY app/ ./app/

# Create a non-root user and set up cache directories
RUN useradd -m -u 1000 user && \
    mkdir -p /tmp/huggingface /tmp/torch/inductor /tmp/triton && \
    chown -R user:user /app /tmp/huggingface /tmp/torch /tmp/triton

USER user

# Set environment variables for optimal vLLM performance
ENV HF_HOME=/tmp/huggingface
ENV TORCHINDUCTOR_CACHE_DIR=/tmp/torch/inductor
ENV TRITON_CACHE_DIR=/tmp/triton
ENV TORCH_COMPILE_DEBUG=0
ENV CUDA_VISIBLE_DEVICES=0
# Optimize CUDA memory allocation
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# Force vLLM to use legacy (v0) engine - more stable, single-process
ENV VLLM_USE_V1=0

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
