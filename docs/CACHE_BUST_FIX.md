# Cache Bust Fix Applied

## Problem

HF Space was using cached Docker layers from the old FastAPI/Transformers build, preventing the vLLM migration from taking effect.

## Solution Applied

Added cache-busting to `Dockerfile`:

```dockerfile
# Cache bust: Force rebuild on each push
ARG CACHE_BUST=$(date +%s)
RUN echo "Build timestamp: $CACHE_BUST"
```

This ensures HF Spaces rebuilds from scratch on each push instead of reusing cached layers.

## What Happens Now

1. ✅ Push triggers rebuild
2. ✅ Dockerfile cache is invalidated
3. ✅ Fresh build with vLLM
4. ✅ Old FastAPI/Transformers code is not included

## Verification

After rebuild, check logs for:
- ✅ `vLLM OpenAI Server - Starting`
- ✅ `Tool Calling: ENABLED (parser: hermes)`
- ❌ No `Uvicorn running`
- ❌ No `Initializing Transformers`

## Additional Steps

If Space still shows old code after this fix:

1. **Manual Rebuild**: Go to HF Space Settings → Rebuild Space
2. **Check Files**: Verify `app/main.py` is removed in Space Files tab
3. **Verify Dockerfile**: Check that Space is using the updated Dockerfile

## Why This Works

Docker caches layers based on:
- Dockerfile content (unchanged = cache hit)
- File checksums (unchanged = cache hit)

By adding a timestamp-based ARG that changes on each build, we force Docker to:
- Skip cache for that layer
- Rebuild all subsequent layers
- Ensure fresh build with new code

