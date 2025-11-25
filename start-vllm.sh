#!/bin/bash
# vLLM OpenAI-compatible API server startup script for Koyeb
# Uses vLLM's native server with all CUDA optimizations

set -e

# Configuration from environment
MODEL=${MODEL:-"DragonLLM/Qwen-Open-Finance-R-8B"}
PORT=${PORT:-8000}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-8192}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}

# HF Token (try multiple env var names)
HF_TOKEN="${HF_TOKEN_LC2:-${HF_TOKEN:-${HUGGING_FACE_HUB_TOKEN:-}}}"

echo "=========================================="
echo "vLLM OpenAI Server - Koyeb Deployment"
echo "=========================================="
echo "Model: $MODEL"
echo "Port: $PORT"
echo "Max Model Length: $MAX_MODEL_LEN"
echo "GPU Memory Utilization: $GPU_MEMORY_UTILIZATION"
echo "HF Token: ${HF_TOKEN:+set (${#HF_TOKEN} chars)}"
echo "CUDA Devices: ${CUDA_VISIBLE_DEVICES:-auto}"
echo "=========================================="

# Check for GPU
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Info:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo "=========================================="
fi

# Build vLLM serve command with optimizations
VLLM_ARGS=(
    "--model" "$MODEL"
    "--port" "$PORT"
    "--host" "0.0.0.0"
    "--dtype" "bfloat16"
    "--max-model-len" "$MAX_MODEL_LEN"
    "--gpu-memory-utilization" "$GPU_MEMORY_UTILIZATION"
    "--trust-remote-code"
    # Optimization flags
    "--enable-prefix-caching"           # Cache common prefixes for faster inference
    "--enable-chunked-prefill"          # Better memory management
    "--max-num-batched-tokens" "8192"   # Batch optimization
    "--max-num-seqs" "256"              # Concurrent request handling
    # Disable logging overhead in production
    "--disable-log-requests"
)

# Add HF token if available
if [ -n "$HF_TOKEN" ]; then
    export HF_TOKEN
    export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi

echo "Starting vLLM OpenAI server..."
echo "Endpoints available:"
echo "  - POST /v1/chat/completions"
echo "  - POST /v1/completions"  
echo "  - GET  /v1/models"
echo "  - GET  /health"
echo "=========================================="

# Start vLLM server
exec python -m vllm.entrypoints.openai.api_server "${VLLM_ARGS[@]}"

