# GGUF Conversion Script

This script converts DragonLLM models from Hugging Face to GGUF format for use with oLLama on Mac.

## Quick Start

```bash
# Activate virtual environment
cd /Users/jeanbapt/simple-llm-pro-finance
source venv/bin/activate

# Run conversion (uses default: Qwen-Pro-Finance-R-32B)
python3 scripts/convert_to_gguf.py

# Or specify a model by number (1-5) or name
python3 scripts/convert_to_gguf.py 1  # Qwen-Pro-Finance-R-32B
python3 scripts/convert_to_gguf.py 2  # qwen3-32b-fin-v1.0
python3 scripts/convert_to_gguf.py "DragonLLM/qwen3-32b-fin-v1.0"
```

## Available 32B Models

1. **DragonLLM/Qwen-Pro-Finance-R-32B** (Recommended - latest)
2. DragonLLM/qwen3-32b-fin-v1.0
3. DragonLLM/qwen3-32b-fin-v0.3
4. DragonLLM/qwen3-32b-fin-v1.0-fp8 (Already quantized to FP8)
5. DragonLLM/Qwen-Pro-Finance-R-32B-FP8 (Already quantized to FP8)

## What It Does

1. **Downloads llama.cpp** (if not already present)
2. **Converts model to base GGUF** (FP16, ~64GB)
3. **Quantizes to multiple levels**:
   - Q5_K_M (~20GB) - **Best balance** ⭐
   - Q6_K (~24GB) - Higher quality
   - Q4_K_M (~16GB) - Smaller size
   - Q8_0 (~32GB) - Highest quality

## Memory Requirements

- **Base conversion (FP16)**: ~64GB RAM
- **Quantization**: ~32GB RAM (can be done separately)

## Output

Files are saved to: `simple-llm-pro-finance/gguf_models/`

```
gguf_models/
├── Qwen-Pro-Finance-R-32B-f16.gguf      (~64GB)
├── Qwen-Pro-Finance-R-32B-q5_k_m.gguf  (~20GB) ⭐ Recommended
├── Qwen-Pro-Finance-R-32B-q6_k.gguf    (~24GB)
├── Qwen-Pro-Finance-R-32B-q4_k_m.gguf  (~16GB)
└── Qwen-Pro-Finance-R-32B-q8_0.gguf    (~32GB)
```

## Using with oLLama

After conversion, create an oLLama model:

```bash
# Create Modelfile
cat > Modelfile << EOF
FROM ./gguf_models/Qwen-Pro-Finance-R-32B-q5_k_m.gguf
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ .Response }}<|im_end|>
"""
PARAMETER num_ctx 8192
PARAMETER temperature 0.7
EOF

# Create model
ollama create qwen-finance-32b -f Modelfile

# Use it
ollama run qwen-finance-32b "What is compound interest?"
```

## Tool Calling Support

GGUF models maintain tool calling capabilities. oLLama supports OpenAI-compatible function calling:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.chat.completions.create(
    model="qwen-finance-32b",
    messages=[{"role": "user", "content": "Calculate future value of 10000 at 5% for 10 years"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "calculate_fv",
            "description": "Calculate future value",
            "parameters": {
                "type": "object",
                "properties": {
                    "pv": {"type": "number"},
                    "rate": {"type": "number"},
                    "nper": {"type": "number"}
                }
            }
        }
    }],
    tool_choice="auto"
)
```

## Troubleshooting

### Out of Memory
- Use Q4_K_M instead of Q5_K_M
- Close other applications
- Reduce context window in oLLama (`num_ctx 4096`)

### Conversion Fails
- Ensure HF_TOKEN_LC2 is set in .env
- Check you have access to the model on Hugging Face
- Verify you have enough disk space (~200GB recommended)

### Quantization Fails
- The base FP16 file is still usable
- Try quantizing manually: `./llama.cpp/llama-quantize input.gguf output.gguf Q5_K_M`

## Notes

- **FP8 models** (models 4 and 5) are already quantized, but converting to GGUF still provides benefits for oLLama
- **Q5_K_M is recommended** for best quality/size trade-off on Mac
- Conversion takes 30-60 minutes depending on your system
- Quantization takes 10-20 minutes per level





