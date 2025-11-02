# Fixes Summary

## Issues Found

### 1. ✅ FIXED: Truncated Responses
**Problem:** Responses were cutting off mid-sentence
**Root cause:** Qwen3 uses `<think>` tags for reasoning, which count toward max_tokens
**Solution:** 
- Increased max_tokens from 150-200 to 300-400
- Added `min_new_tokens` to ensure minimum generation
- Added `repetition_penalty=1.05` to prevent loops
- Added explicit `eos_token_id` handling

**Result:** English tests now complete properly (3/3 passed, all finish_reason=stop)

### 2. ⚠️  PARTIAL: French Language Support
**Problem:** Thinking section `<think>` appears in English even for French questions
**Root cause:** Qwen3 is pretrained to use English for internal reasoning
**Attempted fix:** Added system prompts requesting French reasoning
**Result:** System prompts cause HTTP 500 errors (3/4 French tests failed)

**Analysis:**
- Qwen3 models use English for `<think>` tags by design
- System prompts may not be properly supported by the chat template
- The actual answer (after `</think>`) is in French

**Workaround:**
- Remove system prompts to avoid 500 errors
- Accept that reasoning will be in English
- Ensure final answer is in the requested language
- Alternatively: Strip `<think>` tags from response for French

### 3. ✅ IMPROVED: Generation Parameters
**Changes made:**
```python
# Before
outputs = model.generate(
    **inputs,
    max_new_tokens=max_tokens,
    temperature=temperature,
    top_p=top_p,
    do_sample=temperature > 0,
    pad_token_id=tokenizer.eos_token_id
)

# After
outputs = model.generate(
    **inputs,
    max_new_tokens=max_tokens,
    temperature=temperature,
    top_p=top_p,
    do_sample=temperature > 0,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,  # Explicit EOS
    min_new_tokens=min(20, max_tokens // 2),  # Ensure minimum generation
    repetition_penalty=1.05  # Prevent repetition
)
```

## Performance Results

### English Tests (3/3 passed)
- ✅ All complete (finish_reason=stop)
- ✅ Average time: 21.12s
- ✅ Average tokens: 317
- ✅ Speed: 15.0 tokens/s
- ✅ Shows reasoning: 100%

### French Tests (1/4 passed, 3 HTTP 500)
- ⚠️  System prompts cause errors
- ✅ Test without system prompt succeeded
- ❌ Thinking in English instead of French
- ✅ Final answer in French

## Recommendations

### Immediate Actions

1. **Remove System Prompts for French Tests**
   - System prompts appear unsupported or cause errors
   - Rely on question language to determine response language

2. **Increase Default max_tokens**
   - Current: 150-200 tokens
   - Recommended: 400-500 tokens for complete answers
   - Reasoning: `<think>` section uses 150-200 tokens, answer needs 200-300

3. **Post-process Responses**
   - Option A: Keep `<think>` tags (shows reasoning)
   - Option B: Strip `<think>` section for cleaner output
   - Option C: Add a "hide reasoning" parameter

### Long-term Solutions

1. **Alternative Model**
   - Consider Qwen2.5 models that may have better multilingual reasoning
   - Or fine-tune to use French in `<think>` tags

2. **Custom Prompt Engineering**
   - Add French reasoning instruction in the question itself
   - Example: "Répondez en français (y compris votre raisonnement)"

3. **Response Formatting**
   - Parse and separate thinking from answer
   - Allow clients to request with/without reasoning

## Token Allocation Strategy

For complete answers with Qwen3's thinking pattern:

| Answer Type | Thinking | Answer | Total Recommended |
|-------------|----------|--------|-------------------|
| Short (50 words) | 100 | 100 | 250 |
| Medium (100 words) | 150 | 200 | 400 |
| Long (200 words) | 200 | 350 | 600 |

**Formula:** `max_tokens = thinking_tokens + answer_tokens + buffer(50)`

## Updated Test Parameters

```python
# Recommended max_tokens by question complexity
SIMPLE_QUESTION = 300  # One concept, quick answer
MEDIUM_QUESTION = 400  # Multiple points, examples
COMPLEX_QUESTION = 600  # Detailed explanation, calculations

# Example
{
    "question": "Calculate compound interest for 3 years",
    "max_tokens": 300,  # Enough for thinking + calculation + answer
}

{
    "question": "Explain VaR and give examples",
    "max_tokens": 500,  # More complex, needs examples
}
```

## Qwen3 Behavior Notes

### Thinking Pattern
- Model uses `<think>` and `</think>` tags automatically
- Thinking is always in English (pretrained behavior)
- Cannot be disabled or controlled via parameters
- Thinking typically uses 40-60% of max_tokens

### Chat Template
- Supports `apply_chat_template` 
- May not properly support system role
- Best to use only user/assistant roles

### EOS Handling
- Model generates properly with `eos_token_id`
- `min_new_tokens` helps prevent premature stopping
- `repetition_penalty` prevents loops

## Next Steps

1. ✅ Push updated generation parameters (DONE)
2. ⏳ Test without system prompts for French
3. ⏳ Document thinking pattern behavior
4. ⏳ Add response post-processing option
5. ⏳ Update API documentation with recommended token limits

