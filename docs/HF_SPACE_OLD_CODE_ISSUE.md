# HF Space Still Running Old Code - Troubleshooting

## Problem

HF Space logs show it's still running the **old FastAPI/Transformers** code instead of **vLLM**:

**Current logs show:**
- `INFO:app.main:` - FastAPI running
- `Uvicorn running on http://0.0.0.0:7860` - Uvicorn server
- `Initializing Transformers` - Transformers provider
- `Loading checkpoint shards` - Model loading with Transformers

**Expected logs with vLLM:**
- `vLLM OpenAI Server - Starting`
- `Tool Calling: ENABLED (parser: hermes)`
- `🌐 Detected Hugging Face Spaces environment`
- No FastAPI/Uvicorn logs
- No Transformers loading

## Possible Causes

1. **Push didn't reach HF Space** - Changes not pushed to `huggingface` remote
2. **Cached build** - HF Space using old Docker image
3. **Build in progress** - Space still building old code
4. **Wrong branch** - Space might be tracking different branch

## Solutions

### Solution 1: Verify and Force Push

```bash
cd /Users/jeanbapt/simple-llm-pro-finance

# Check current state
git log --oneline -1
git status

# Force push to HF (safe - only if remote hasn't changed)
git push huggingface main:main --force-with-lease
```

### Solution 2: Manual Space Restart

1. Go to HF Space: https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b
2. Click **"Settings"** tab
3. Scroll to **"Rebuild Space"** section
4. Click **"Rebuild Space"** button
5. Wait for rebuild (5-10 minutes)

### Solution 3: Check Space Configuration

1. Go to Space **Settings**
2. Check **"Dockerfile"** path - should be `Dockerfile` (not `Dockerfile.koyeb`)
3. Check **"SDK"** - should be `docker`
4. Verify **"Hardware"** - should be `GPU` (L4 or better)

### Solution 4: Verify Files in HF Space

1. Go to Space **"Files"** tab
2. Check if `Dockerfile` exists and has:
   ```dockerfile
   FROM vllm/vllm-openai:latest
   ```
3. Check if `start-vllm.sh` exists
4. Verify `app/main.py` is **removed** (should not exist)

## Verification After Fix

After pushing/rebuilding, logs should show:

```
==========================================
vLLM OpenAI Server - Starting
==========================================
Model: DragonLLM/Qwen-Open-Finance-R-8B
Port: 7860
Max Model Len: 8192
GPU Memory Utilization: 0.90
Tensor Parallel Size: 1
HF Token: set (37 chars)
==========================================
🌐 Detected Hugging Face Spaces environment
Tool Calling: ENABLED (parser: hermes)
==========================================
```

## Next Steps

1. ✅ Force push to `huggingface` remote
2. ✅ Manually restart/rebuild Space
3. ✅ Verify logs show vLLM startup
4. ✅ Test `/v1/models` endpoint
5. ✅ Verify tool calling works

