#!/bin/bash
# vLLM OpenAI-compatible API server startup script for Koyeb
# Uses vLLM's native server with all CUDA optimizations

# Redirect all output to stderr for Koyeb logs
exec 2>&1

echo "=========================================="
echo "vLLM OpenAI Server - Starting"
echo "=========================================="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "PWD: $(pwd)"

# Configuration from environment
MODEL=${MODEL:-"DragonLLM/Qwen-Open-Finance-R-8B"}
PORT=${PORT:-8000}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-8192}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}

# HF Token (try multiple env var names)
HF_TOKEN="${HF_TOKEN_LC2:-${HF_TOKEN:-${HUGGING_FACE_HUB_TOKEN:-}}}"

echo "=========================================="
echo "Configuration:"
echo "  Model: $MODEL"
echo "  Port: $PORT"
echo "  Max Model Length: $MAX_MODEL_LEN"
echo "  GPU Memory Utilization: $GPU_MEMORY_UTILIZATION"
echo "  HF Token: ${HF_TOKEN:+set (${#HF_TOKEN} chars)}"
echo "=========================================="

# Check Python
echo "Checking Python..."
which python || { echo "ERROR: python not found!"; exit 1; }
python --version

# Check vLLM
echo "Checking vLLM installation..."
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')" || { 
    echo "ERROR: vLLM not installed correctly!"
    exit 1
}

# Check for GPU
echo "=========================================="
echo "GPU Information:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || echo "nvidia-smi failed"
    nvidia-smi || echo "nvidia-smi full output failed"
else
    echo "WARNING: nvidia-smi not found - GPU may not be available!"
fi
echo "=========================================="

# Set HF token for model download
if [ -n "$HF_TOKEN" ]; then
    export HF_TOKEN
    export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
    echo "HF Token exported for model download"
else
    echo "WARNING: No HF token set - model download may fail for gated models!"
fi

echo "=========================================="
echo "Starting vLLM OpenAI server..."
echo "Endpoints:"
echo "  - POST /v1/chat/completions"
echo "  - POST /v1/completions"  
echo "  - GET  /v1/models"
echo "  - GET  /health"
echo "=========================================="

# Build vLLM serve command
exec python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$PORT" \
    --host "0.0.0.0" \
    --dtype "bfloat16" \
    --max-model-len "$MAX_MODEL_LEN" \
    --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
    --trust-remote-code \
    --enable-prefix-caching \
    --disable-log-requests
