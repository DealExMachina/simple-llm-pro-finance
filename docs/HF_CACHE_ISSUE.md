# HF Space Cache Issue - Force Clean Rebuild

## Problem

HF Space is still running the old FastAPI/Transformers code despite pushing vLLM changes. This is likely a **Docker build cache** issue.

## Root Cause

Hugging Face Spaces caches Docker layers. If the Dockerfile structure hasn't changed significantly, HF might reuse cached layers from the old build, including the old application code.

## Solutions

### Solution 1: Force Clean Rebuild via HF Space UI (Recommended)

1. Go to: https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b
2. Click **"Settings"** tab
3. Scroll to **"Rebuild Space"** section
4. Click **"Rebuild Space"** button
5. **Important**: If there's a "Clear cache" or "Force rebuild" option, enable it
6. Wait for rebuild (5-10 minutes)

### Solution 2: Add Cache-Busting to Dockerfile

Add a cache-busting layer to force rebuild:

```dockerfile
# Add this after the FROM line to bust cache
ARG CACHE_BUST=1
RUN echo "Cache bust: $CACHE_BUST"

# Or use a timestamp
ARG BUILD_DATE=$(date +%s)
RUN echo "Build date: $BUILD_DATE"
```

### Solution 3: Modify Dockerfile to Force Rebuild

Add a comment or whitespace change to trigger rebuild:

```dockerfile
# Unified Dockerfile for Hugging Face Spaces using vLLM
# Migrated from Transformers backend to vLLM for better performance and deployment parity
# Now matches Koyeb deployment (Dockerfile.koyeb) for consistency
# Cache bust: $(date +%s)  # Add this line

FROM vllm/vllm-openai:latest
```

### Solution 4: Delete and Recreate Space (Last Resort)

If nothing else works:
1. Create a new Space
2. Push code to new Space
3. Delete old Space

## Current Dockerfile Cache Strategy

The current Dockerfile uses:
- `--no-cache-dir` for pip install (good - prevents pip cache)
- But HF Spaces might cache the entire Docker layer

## Recommended Fix

**Immediate action:**
1. Go to HF Space Settings
2. Click "Rebuild Space" with cache cleared (if option exists)
3. Or manually trigger rebuild via API

**Long-term fix:**
Add cache-busting to Dockerfile to ensure clean builds:

```dockerfile
# Force cache invalidation on each push
ARG BUILD_ID
RUN echo "Build ID: ${BUILD_ID:-$(date +%s)}"
```

## Verification

After rebuild, check logs for:
- ✅ `vLLM OpenAI Server - Starting`
- ✅ `Tool Calling: ENABLED (parser: hermes)`
- ❌ No `Uvicorn running`
- ❌ No `Initializing Transformers`

## HF Spaces Build Cache Behavior

HF Spaces caches:
- Docker layers (if Dockerfile structure is similar)
- Base image layers
- pip install layers (unless `--no-cache-dir` is used)

To bypass cache:
- Change Dockerfile (even whitespace)
- Use `--no-cache` in build (if available in UI)
- Force rebuild via Settings

