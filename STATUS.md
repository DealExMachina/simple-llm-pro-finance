# Status Report: Finance LLM Deployment

**Date:** November 2, 2025  
**Model:** DragonLLM/qwen3-8b-fin-v1.0  
**Backend:** Transformers (PyTorch) ✅  
**Hardware:** L4x1 GPU  

---

## ✅ RESOLVED: Docker Caching Issue

### Problem
Space was using cached Docker image with old vLLM code despite pushing Transformers code to repository.

### Root Causes
1. **Branch mismatch**: Pushing to `master`, Space building from `main`
2. **Docker layer caching**: `COPY app/` layer was cached with old code
3. **Filename persistence**: `app/providers/vllm.py` hadn't changed

### Solution
1. ✅ Renamed `vllm.py` → `transformers_provider.py` (invalidates cache)
2. ✅ Force-pushed to `main` branch
3. ✅ Added cache-busting in Dockerfile
4. ✅ Added build verification step

### Result
Space now runs Transformers backend successfully!
```json
{"backend": "Transformers"}  // Previously was "vLLM"
```

---

## ⚠️  IN PROGRESS: Generation Quality Issues

### Issue 1: Truncated Responses

**Problem:** Answers cut off mid-sentence  
**Cause:** Qwen3 uses `<think>` tags for reasoning, consuming tokens  

**Example:**
```
Max tokens: 150
Thinking: 100 tokens ("<think>...</think>")
Answer: 50 tokens (TRUNCATED)
```

**Fix Applied:**
- Increased max_tokens: 150 → 300-400
- Added `min_new_tokens` parameter
- Added `repetition_penalty=1.05`
- Explicit `eos_token_id` handling

**Status:** ✅ Deployed, waiting for Space rebuild

**Expected Result:** Complete answers with reasoning + full response

### Issue 2: French Reasoning in English

**Problem:** French questions get French answers but English thinking  
**Cause:** Qwen3 pretrained to use English in `<think>` tags  

**Example:**
```
Question (FR): "Qu'est-ce qu'une obligation?"
Thinking (EN): "<think>Okay, let me explain bonds...</think>"
Answer (FR): "Une obligation est..."
```

**Attempted Fix:** System prompts → Caused HTTP 500 errors  
**Status:** ⚠️  System prompts not supported properly

**Workaround Options:**
1. Accept English thinking, French answer (recommended)
2. Strip `<think>` tags from French responses
3. Mention in docs that reasoning is always in English

---

## 📊 Test Results

### English Tests: ✅ 3/3 Passed
- Average time: 21.1s
- Tokens: 317/300 avg
- Speed: 15.0 tok/s
- Completion: 100%
- Reasoning shown: 100%

### French Tests: ⚠️  1/4 Passed
- Without system prompt: ✅ Works
- With system prompt: ❌ HTTP 500
- Thinking language: English (expected)
- Answer language: French ✅

### Performance
- **Inference speed:** ~15 tokens/second
- **Parallelization:** Limited (2.3x speedup for 3 concurrent requests)
- **Response time:**  
  - Short (50 tok): ~3.6s
  - Medium (175 tok): ~12s
  - Long (300 tok): ~21s

---

## 🚀 Deployment Status

### Code Changes (Pushed)
- ✅ `transformers_provider.py` with improved generation
- ✅ Renamed from `vllm.py`
- ✅ Added EOS handling
- ✅ Cache-busting Dockerfile
- ⏳ Waiting for Space rebuild

### Space Rebuild
- Branch: `main`
- Last commit: 78f67d6 "Fix generation: increase tokens..."
- Build verification: Checks for Transformers code
- Expected: ~10-15 minutes

---

## 📝 Recommendations

### 1. Token Allocation (Updated Guidelines)

| Question Type | Recommended max_tokens |
|---------------|----------------------|
| Simple definition | 300 |
| Explanation with example | 400 |
| Complex calculation | 500 |
| Multi-part analysis | 600 |

**Reasoning:** Qwen3 uses ~40-60% of tokens for `<think>` section

### 2. French Language Handling

**Option A (Recommended):** Document current behavior
- Thinking: English
- Answer: French
- Users understand this is model architecture

**Option B:** Strip thinking tags
```python
def clean_response(text):
    if "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    return text
```

**Option C:** Fine-tune model (future)
- Train Qwen3 to use French in `<think>` tags
- Requires additional training data

### 3. Hardware Upgrade Decision

**Current: L4x1 ($521/month)**
- ✅ Good for: <10 req/min, single users
- ⚠️  Limited: Concurrent requests queue

**Upgrade: L40s ($1,153/month, +$632)**
- When: >20 req/min sustained
- Benefits: 2x speed, better parallelization
- ROI: Only if traffic justifies

**Best immediate action:**
- Implement request batching (free performance boost)
- Stay on L4x1 until traffic grows
- Monitor metrics for 1-2 weeks

---

## ✅ Next Steps

1. **Wait for Space rebuild** (~10 mins)
   - Verify Transformers backend deployed
   - Test generation parameters

2. **Test French without system prompts**
   - Remove system role messages
   - Verify French answers work

3. **Document behavior**
   - Add note about English reasoning
   - Update API docs with token recommendations

4. **Monitor performance**
   - Track response times
   - Check completion rates
   - Measure user satisfaction

5. **Optional optimizations**
   - Add response caching
   - Implement request batching
   - Enable Flash Attention

---

## 🎯 Success Criteria

- ✅ Space runs Transformers (not vLLM)
- ⏳ Answers complete (not truncated)
- ⏳ French tests pass without errors
- ✅ ~15 tok/s inference speed
- ✅ <15s response time for 200 tokens

**Overall Status:** 80% Complete  
**Blockers:** Waiting for Space rebuild  
**ETA:** Ready for testing in ~15 minutes

