#!/usr/bin/env python3
"""
Convert DragonLLM models from Hugging Face to GGUF format.

This script:
1. Downloads the model from Hugging Face
2. Converts it to GGUF format using llama.cpp
3. Quantizes to multiple levels (Q4_K_M, Q5_K_M, Q6_K, Q8_0)

Requirements:
- llama.cpp installed (git clone https://github.com/ggerganov/llama.cpp.git)
- Python packages: huggingface_hub, python-dotenv
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

HF_TOKEN = os.getenv("HF_TOKEN_LC2") or os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")

# Available 32B models found
AVAILABLE_32B_MODELS = [
    "DragonLLM/Qwen-Pro-Finance-R-32B",
    "DragonLLM/qwen3-32b-fin-v1.0",
    "DragonLLM/qwen3-32b-fin-v0.3",
    "DragonLLM/qwen3-32b-fin-v1.0-fp8",
    "DragonLLM/Qwen-Pro-Finance-R-32B-FP8",
]

# Quantization levels (best trade-off first)
QUANTIZATIONS = [
    ("Q5_K_M", "~20GB", "Best balance of quality and size"),
    ("Q6_K", "~24GB", "Higher quality"),
    ("Q4_K_M", "~16GB", "Smaller size, good quality"),
    ("Q8_0", "~32GB", "Highest quality, larger size"),
]


def check_llama_cpp() -> Optional[Path]:
    """Check if llama.cpp is available."""
    # Check common locations
    possible_paths = [
        Path.home() / "llama.cpp",
        Path(__file__).parent.parent / "llama.cpp",
        Path("/usr/local/llama.cpp"),
    ]
    
    for path in possible_paths:
        # Try both naming conventions
        convert_script = path / "convert_hf_to_gguf.py"
        if not convert_script.exists():
            convert_script = path / "convert-hf-to-gguf.py"
        quantize_bin = path / "llama-quantize"
        if convert_script.exists() and (quantize_bin.exists() or (path / "llama-quantize.exe").exists()):
            return path
    
    return None


def install_llama_cpp(target_dir: Path) -> Path:
    """Clone and set up llama.cpp."""
    print(f"📦 Cloning llama.cpp to {target_dir}...")
    
    if target_dir.exists():
        print(f"   {target_dir} already exists, using existing installation")
        return target_dir
    
    try:
        subprocess.run(
            ["git", "clone", "https://github.com/ggerganov/llama.cpp.git", str(target_dir)],
            check=True,
            capture_output=True,
        )
        print("✅ llama.cpp cloned successfully")
        
        # Install Python requirements for conversion
        requirements = target_dir / "requirements" / "requirements-convert_hf_to_gguf.txt"
        if not requirements.exists():
            requirements = target_dir / "requirements.txt"
        if requirements.exists():
            print("📦 Installing Python requirements for llama.cpp conversion...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements), "--quiet"],
                check=False,  # Don't fail if some packages are already installed
            )
        
        # Try to build (optional, but faster)
        print("🔨 Attempting to build llama-quantize (optional)...")
        try:
            subprocess.run(["make", "-C", str(target_dir)], check=True, capture_output=True)
            print("✅ Build successful")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Build failed or make not available, will use Python quantize")
        
        return target_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Error cloning llama.cpp: {e}")
        sys.exit(1)


def convert_to_gguf(
    model_name: str,
    output_dir: Path,
    llama_cpp_dir: Path,
    hf_token: str,
) -> Path:
    """Convert Hugging Face model to GGUF format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = model_name.split("/")[-1].replace(".", "-")
    output_file = output_dir / f"{base_name}-f16.gguf"
    
    if output_file.exists():
        print(f"✅ Base GGUF file already exists: {output_file}")
        return output_file
    
    print(f"🔄 Converting {model_name} to GGUF (FP16)...")
    print(f"   This may take 30-60 minutes and requires ~64GB RAM...")
    
    # Try both naming conventions
    convert_script = llama_cpp_dir / "convert_hf_to_gguf.py"
    if not convert_script.exists():
        convert_script = llama_cpp_dir / "convert-hf-to-gguf.py"
    
    try:
        subprocess.run(
            [
                sys.executable,
                str(convert_script),
                "--outdir", str(output_dir),
                "--outfile", output_file.name,
                model_name,
                "--token", hf_token,
            ],
            check=True,
        )
        print(f"✅ Conversion complete: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)


def quantize_gguf(
    input_file: Path,
    output_dir: Path,
    llama_cpp_dir: Path,
    quantizations: list,
) -> list[Path]:
    """Quantize GGUF file to different levels."""
    quantized_files = []
    
    # Try binary quantize first, fallback to Python
    quantize_bin = llama_cpp_dir / "llama-quantize"
    if not quantize_bin.exists():
        quantize_bin = llama_cpp_dir / "llama-quantize.exe"
    
    use_binary = quantize_bin.exists()
    
    if not use_binary:
        print("⚠️  Binary quantize not found, will use Python quantize (slower)")
        quantize_script = llama_cpp_dir / "quantize.py"
        if not quantize_script.exists():
            print("❌ No quantize tool found!")
            return []
    
    for qtype, size, description in quantizations:
        output_file = output_dir / input_file.name.replace("-f16.gguf", f"-{qtype.lower()}.gguf")
        
        if output_file.exists():
            print(f"✅ {qtype} already exists: {output_file}")
            quantized_files.append(output_file)
            continue
        
        print(f"🔄 Quantizing to {qtype} ({size}, {description})...")
        
        try:
            if use_binary:
                subprocess.run(
                    [str(quantize_bin), str(input_file), str(output_file), qtype],
                    check=True,
                )
            else:
                subprocess.run(
                    [
                        sys.executable,
                        str(quantize_script),
                        str(input_file),
                        str(output_file),
                        qtype,
                    ],
                    check=True,
                )
            print(f"✅ {qtype} complete: {output_file}")
            quantized_files.append(output_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Quantization to {qtype} failed: {e}")
            continue
    
    return quantized_files


def main():
    """Main conversion script."""
    if not HF_TOKEN:
        print("❌ Error: HF_TOKEN_LC2 not found in environment")
        print("   Please set it in .env file or environment variables")
        sys.exit(1)
    
    # Select model
    print("Available 32B models:")
    for i, model in enumerate(AVAILABLE_32B_MODELS, 1):
        print(f"  {i}. {model}")
    
    if len(sys.argv) > 1:
        try:
            model_idx = int(sys.argv[1]) - 1
            if 0 <= model_idx < len(AVAILABLE_32B_MODELS):
                model_name = AVAILABLE_32B_MODELS[model_idx]
            else:
                model_name = sys.argv[1]  # Use as model name directly
        except ValueError:
            model_name = sys.argv[1]  # Use as model name directly
    else:
        # Default to best model
        model_name = AVAILABLE_32B_MODELS[0]
        print(f"\nUsing default model: {model_name}")
        print("   (Pass model number or name as argument to use different model)")
    
    print(f"\n🎯 Target model: {model_name}")
    
    # Setup directories
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / "gguf_models"
    llama_cpp_dir = script_dir / "llama.cpp"
    
    # Check/install llama.cpp
    llama_cpp_path = check_llama_cpp()
    if not llama_cpp_path:
        print("📦 llama.cpp not found, installing...")
        llama_cpp_path = install_llama_cpp(llama_cpp_dir)
    else:
        print(f"✅ Found llama.cpp at: {llama_cpp_path}")
    
    # Convert to GGUF
    base_gguf = convert_to_gguf(model_name, output_dir, llama_cpp_path, HF_TOKEN)
    
    # Quantize
    print(f"\n📊 Quantizing to multiple levels...")
    quantized = quantize_gguf(base_gguf, output_dir, llama_cpp_path, QUANTIZATIONS)
    
    # Summary
    print(f"\n✅ Conversion complete!")
    print(f"\n📁 Output directory: {output_dir}")
    print(f"\n📦 Generated files:")
    print(f"   - {base_gguf.name} ({base_gguf.stat().st_size / (1024**3):.1f} GB)")
    for qfile in quantized:
        size_gb = qfile.stat().st_size / (1024**3)
        print(f"   - {qfile.name} ({size_gb:.1f} GB)")
    
    print(f"\n💡 Recommended for Mac:")
    print(f"   - 32GB RAM: Use Q5_K_M or Q4_K_M")
    print(f"   - 64GB+ RAM: Use Q6_K or Q8_0")
    print(f"\n🚀 To use with oLLama:")
    print(f"   ollama create {model_name.split('/')[-1].lower()} -f <(echo 'FROM {quantized[0] if quantized else base_gguf}')")


if __name__ == "__main__":
    main()

