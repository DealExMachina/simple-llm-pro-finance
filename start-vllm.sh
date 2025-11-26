#!/bin/bash
# vLLM OpenAI-compatible API server startup script
# Compatible with Koyeb GPU deployment patterns
# Based on Koyeb's one-click vLLM + Qwen deployment templates

set -e

# Configuration from environment (with defaults)
MODEL="${MODEL:-DragonLLM/Qwen-Open-Finance-R-8B}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
DTYPE="${DTYPE:-bfloat16}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-${KOYEB_GPU_COUNT:-1}}"

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
echo "Tensor Parallel Size: $TENSOR_PARALLEL_SIZE"
echo "HF Token: ${HF_TOKEN:+set (${#HF_TOKEN} chars)}"
echo "=========================================="

# Build vLLM arguments
VLLM_ARGS=(
    --model "$MODEL"
    --trust-remote-code
    --dtype "$DTYPE"
    --max-model-len "$MAX_MODEL_LEN"
    --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION"
    --tensor-parallel-size "$TENSOR_PARALLEL_SIZE"
    --port "$PORT"
    --host 0.0.0.0
)

# Tool Calling Support
# ENABLED BY DEFAULT for Qwen models (using hermes parser)
# Set ENABLE_AUTO_TOOL_CHOICE=false to disable
# For Qwen models, the default parser is 'hermes'
ENABLE_AUTO_TOOL_CHOICE="${ENABLE_AUTO_TOOL_CHOICE:-true}"
TOOL_CALL_PARSER="${TOOL_CALL_PARSER:-hermes}"

if [ "${ENABLE_AUTO_TOOL_CHOICE}" = "true" ]; then
    VLLM_ARGS+=(--enable-auto-tool-choice --tool-call-parser "$TOOL_CALL_PARSER")
    echo "Tool Calling: ENABLED (parser: $TOOL_CALL_PARSER)"
else
    echo "Tool Calling: DISABLED"
fi

echo "=========================================="

# Execute vLLM server
exec python3 -m vllm.entrypoints.openai.api_server "${VLLM_ARGS[@]}"
