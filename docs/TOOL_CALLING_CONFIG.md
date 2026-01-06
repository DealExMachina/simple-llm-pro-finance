# Tool Calling Configuration

## Overview

Tool calling (function calling) is **enabled by default** for both Hugging Face Spaces and Koyeb deployments. Both platforms use the same `start-vllm.sh` script, ensuring consistent configuration.

## Configuration

### Default Settings

Tool calling is configured in `start-vllm.sh` with these defaults:

```bash
ENABLE_AUTO_TOOL_CHOICE="${ENABLE_AUTO_TOOL_CHOICE:-true}"  # Default: enabled
TOOL_CALL_PARSER="${TOOL_CALL_PARSER:-hermes}"              # Default: hermes parser
```

### For Qwen Models

- **Parser**: `hermes` (default for Qwen models)
- **Auto Tool Choice**: Enabled by default
- **vLLM Arguments**: `--enable-auto-tool-choice --tool-call-parser hermes`

## Platform Support

| Platform | Tool Calling | Parser | Configurable |
|----------|--------------|--------|--------------|
| **Hugging Face Spaces** | ✅ Enabled | `hermes` | Yes (via env vars) |
| **Koyeb** | ✅ Enabled | `hermes` | Yes (via env vars) |

Both platforms use the same `start-vllm.sh` script, so configuration is identical.

## Environment Variables

You can override the defaults using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_AUTO_TOOL_CHOICE` | `true` | Enable/disable tool calling |
| `TOOL_CALL_PARSER` | `hermes` | Parser type (hermes for Qwen) |

### Examples

**Disable tool calling:**
```bash
ENABLE_AUTO_TOOL_CHOICE=false
```

**Use different parser (if supported):**
```bash
TOOL_CALL_PARSER=hermes  # or other parser
```

## Verification

### Check Startup Logs

When vLLM starts, you should see:
```
Tool Calling: ENABLED (parser: hermes)
```

### Test Tool Calling

```bash
curl -X POST "https://your-endpoint/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/Qwen-Open-Finance-R-8B",
    "messages": [{"role": "user", "content": "What is the weather?"}],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get weather information",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {"type": "string", "description": "City name"}
            }
          }
        }
      }
    ]
  }'
```

Expected response should include `tool_calls` in the message if tool calling is working.

## Implementation Details

The tool calling configuration is in `start-vllm.sh`:

```bash
# Tool Calling Support
# ENABLED BY DEFAULT for Qwen models (using hermes parser)
ENABLE_AUTO_TOOL_CHOICE="${ENABLE_AUTO_TOOL_CHOICE:-true}"
TOOL_CALL_PARSER="${TOOL_CALL_PARSER:-hermes}"

if [ "${ENABLE_AUTO_TOOL_CHOICE}" = "true" ]; then
    VLLM_ARGS+=(--enable-auto-tool-choice --tool-call-parser "$TOOL_CALL_PARSER")
    echo "Tool Calling: ENABLED (parser: $TOOL_CALL_PARSER)"
else
    echo "Tool Calling: DISABLED"
fi
```

## Notes

- ✅ **Unified Configuration**: Both HF Spaces and Koyeb use the same script
- ✅ **Default Enabled**: Tool calling is on by default for Qwen models
- ✅ **Hermes Parser**: Optimized for Qwen model tool calling format
- ✅ **Configurable**: Can be disabled or customized via environment variables

## Troubleshooting

### Tool Calls Not Working

1. **Check logs**: Look for "Tool Calling: ENABLED" in startup logs
2. **Verify parser**: Should show "parser: hermes"
3. **Check model**: Ensure you're using a Qwen model that supports tool calling
4. **Verify request**: Ensure `tools` array is provided in the request

### Disable Tool Calling

If you need to disable tool calling (not recommended for Qwen models):

```bash
# In Hugging Face Spaces: Set in Space settings
ENABLE_AUTO_TOOL_CHOICE=false

# In Koyeb: Set in service environment variables
ENABLE_AUTO_TOOL_CHOICE=false
```

