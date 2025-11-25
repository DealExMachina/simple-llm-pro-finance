#!/bin/bash
# vLLM OpenAI-compatible API server startup script
# This script ensures args are always passed, even if Koyeb clears CMD

set -e

# Configuration from environment (with defaults)
MODEL="${MODEL:-DragonLLM/Qwen-Open-Finance-R-8B}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
DTYPE="${DTYPE:-bfloat16}"

# HF Token - HF_TOKEN_LC2 is the model access token (priority)
export HF_TOKEN="${HF_TOKEN_LC2:-${HF_TOKEN:-${HUGGING_FACE_HUB_TOKEN:-}}}"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"

echo "=========================================="
echo "vLLM OpenAI Server - Starting"
echo "=========================================="
echo "Model: $MODEL"
echo "Port: $PORT"
echo "Max Model Len: $MAX_MODEL_LEN"
echo "GPU Memory Utilization: $GPU_MEMORY_UTILIZATION"
echo "HF Token: ${HF_TOKEN:+set (${#HF_TOKEN} chars)}"
echo "=========================================="

# Execute vLLM server
exec python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --trust-remote-code \
    --dtype "$DTYPE" \
    --max-model-len "$MAX_MODEL_LEN" \
    --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
    --port "$PORT" \
    --host 0.0.0.0
