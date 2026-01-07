# GGUF Conversion Setup Complete ✅

## What Was Created

1. **`scripts/convert_to_gguf.py`** - Main conversion script
2. **`scripts/README_GGUF.md`** - Detailed usage instructions
3. **Dependencies installed** - transformers, torch, sentencepiece, etc.

## Quick Start

```bash
cd /path/to/simple-llm-pro-finance  # Or: cd "$(git rev-parse --show-toplevel)"
source venv313/bin/activate

# Convert default model (Qwen-Pro-Finance-R-32B)
python3 scripts/convert_to_gguf.py

# Or specify a different 32B model
python3 scripts/convert_to_gguf.py 2  # qwen3-32b-fin-v1.0
```

## Available 32B Models

The script found these 32B models in DragonLLM:

1. **DragonLLM/Qwen-Pro-Finance-R-32B** ⭐ (Recommended - latest)
2. DragonLLM/qwen3-32b-fin-v1.0
3. DragonLLM/qwen3-32b-fin-v0.3
4. DragonLLM/qwen3-32b-fin-v1.0-fp8 (Pre-quantized)
5. DragonLLM/Qwen-Pro-Finance-R-32B-FP8 (Pre-quantized)

## What the Script Does

1. ✅ Checks for llama.cpp (clones if needed)
2. ✅ Installs required Python dependencies
3. ✅ Converts model to base GGUF (FP16, ~64GB)
4. ✅ Quantizes to multiple levels:
   - **Q5_K_M** (~20GB) - **Best balance** ⭐
   - Q6_K (~24GB) - Higher quality
   - Q4_K_M (~16GB) - Smaller size
   - Q8_0 (~32GB) - Highest quality

## Memory Requirements

- **Base conversion**: ~64GB RAM (takes 30-60 min)
- **Quantization**: ~32GB RAM (10-20 min per level)
- **Disk space**: ~200GB recommended

## Output Location

All GGUF files will be saved to:
```
./gguf_models/
```

## Recommended Quantization for Mac

Based on your Mac's RAM:

| Mac RAM | Recommended | Alternative |
|---------|-------------|------------|
| 32GB    | Q5_K_M      | Q4_K_M     |
| 64GB+   | Q6_K        | Q8_0       |

## Tool Calling Support

✅ GGUF models maintain full tool calling capabilities
✅ oLLama supports OpenAI-compatible function calling
✅ Works with your existing PydanticAI agents

## Next Steps

1. **Run the conversion** (when ready - it takes time):
   ```bash
   python3 scripts/convert_to_gguf.py
   ```

2. **Create oLLama model** (after conversion):
   ```bash
   ollama create qwen-finance-32b -f Modelfile
   ```

3. **Use with your agents** - Update your endpoint config to point to local oLLama

## Notes

- The script uses `HF_TOKEN_LC2` from your `.env` file automatically
- llama.cpp is cloned to `simple-llm-pro-finance/llama.cpp/`
- You can stop and resume - the script checks for existing files
- Base FP16 file is created first, then quantizations run

## Troubleshooting

If you encounter issues:

1. **Out of memory**: Use Q4_K_M instead
2. **Conversion fails**: Check HF token has access to model
3. **Dependencies missing**: Script auto-installs, but you can manually run:
   ```bash
   pip install transformers torch sentencepiece protobuf gguf
   ```

---

**Ready to convert!** Run `python3 scripts/convert_to_gguf.py` when you're ready (it will take 30-60 minutes).





