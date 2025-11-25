# Structured Outputs: vLLM vs PydanticAI Comparison

## Overview

This document compares how vLLM and PydanticAI handle structured outputs, and why they may not be fully compatible.

## vLLM Structured Outputs

### Method
vLLM uses **`extra_body`** parameter with `structured_outputs` key (NOT standard OpenAI `response_format`):

```python
completion = client.chat.completions.create(
    model="DragonLLM/Qwen-Open-Finance-R-8B",
    messages=[{"role": "user", "content": "Generate JSON..."}],
    extra_body={
        "structured_outputs": {
            "json": json_schema  # Pydantic model.model_json_schema()
        }
    }
)
```

### Supported Formats
1. **JSON Schema**: `{"json": json_schema}`
2. **Regex**: `{"regex": r"pattern"}`
3. **Choice**: `{"choice": ["option1", "option2"]}`
4. **Grammar**: `{"grammar": "CFG definition"}`

### Response Format
- Returns JSON string in `message.content`
- No tool calls involved
- Direct JSON in content field

## PydanticAI Structured Outputs

### Method
PydanticAI uses **tool calling** with `tool_choice="required"`:

```python
agent = Agent(model, system_prompt="...")
result = await agent.run(prompt, output_type=Portfolio)
```

### How It Works
1. PydanticAI converts `output_type` (Pydantic model) to a tool definition
2. Sends request with:
   - `tools`: [function definition matching the schema]
   - `tool_choice`: `"required"` (forces tool call)
3. Expects response with `tool_calls` array
4. Extracts JSON from `tool_calls[0].function.arguments`

### Expected Response Format
```json
{
  "choices": [{
    "message": {
      "tool_calls": [{
        "function": {
          "name": "...",
          "arguments": "{\"field\": \"value\"}"  // JSON string
        }
      }]
    }
  }]
}
```

## Compatibility Issue

### Problem
- **vLLM**: Uses `extra_body.structured_outputs` → Returns JSON in `message.content`
- **PydanticAI**: Uses `tools` + `tool_choice="required"` → Expects JSON in `tool_calls[].function.arguments`

### Current Status
- ✅ **HF Space**: Works because it implements tool calling support
- ❌ **vLLM**: Fails because vLLM's structured outputs return JSON in `content`, not `tool_calls`

## Solutions

### Option 1: Use vLLM's `extra_body` (Recommended)
Modify PydanticAI's OpenAI provider to detect vLLM and use `extra_body` instead of tools:

```python
# In PydanticAI OpenAI provider
if output_type:
    json_schema = output_type.model_json_schema()
    # Use vLLM structured_outputs instead of tools
    extra_body = {
        "structured_outputs": {"json": json_schema}
    }
```

### Option 2: Add Tool Call Support to vLLM Response
When vLLM receives `tools` + `tool_choice="required"`, wrap the structured output in a tool call format.

### Option 3: Use `response_format` (Limited)
Standard OpenAI `response_format={"type": "json_object"}` works but:
- Only enforces JSON, not schema validation
- PydanticAI would need to parse and validate manually
- Less reliable than schema-based approaches

## Current Implementation Status

### HF Space (Transformers)
- ✅ Supports tool calling (text-based parsing)
- ✅ Supports `response_format`
- ✅ Works with PydanticAI's tool-based approach

### vLLM
- ✅ Supports `extra_body.structured_outputs` (JSON schema)
- ❌ Does NOT support tool calling for structured outputs
- ✅ Supports `response_format` (basic JSON mode only)

## Recommendation

For full compatibility with PydanticAI, we need to:

1. **Detect vLLM endpoint** in PydanticAI provider
2. **Use `extra_body.structured_outputs`** instead of tools when using vLLM
3. **Parse `message.content`** instead of `tool_calls` for vLLM responses

Alternatively, implement a middleware in the HF Space API that:
- Detects `tools` + `tool_choice="required"` requests
- Converts to `extra_body.structured_outputs` for vLLM
- Wraps response in tool call format for PydanticAI compatibility

## References

- [vLLM Structured Outputs Docs](https://docs.vllm.ai/en/stable/features/structured_outputs/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)

