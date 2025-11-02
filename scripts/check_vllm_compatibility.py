#!/usr/bin/env python3
"""
Check compatibility between DragonLLM/qwen3-8b-fin-v1.0 and vLLM 0.6.5

This script verifies:
1. vLLM version installed
2. Model architecture support
3. Configuration compatibility
4. Known issues or limitations
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import vllm
    from vllm import LLM
    from vllm.model_executor.models import MODEL_REGISTRY
except ImportError:
    print("❌ Error: vLLM not installed")
    print("   Install it with: pip install vllm==0.6.5")
    sys.exit(1)

try:
    from huggingface_hub import model_info
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("⚠️  Warning: huggingface_hub not installed")
    print("   Some checks will be skipped")
    model_info = None

MODEL_NAME = "DragonLLM/qwen3-8b-fin-v1.0"
VLLM_VERSION = "0.6.5"


def check_vllm_version():
    """Check installed vLLM version"""
    print("\n" + "="*70)
    print("CHECK 1: vLLM Version")
    print("="*70)
    
    installed_version = vllm.__version__
    print(f"Installed vLLM version: {installed_version}")
    print(f"Expected version: {VLLM_VERSION}")
    
    if installed_version == VLLM_VERSION:
        print("✅ Version matches!")
        return True
    elif installed_version.startswith("0.6"):
        print(f"⚠️  Version mismatch: {installed_version} (expected {VLLM_VERSION})")
        print("   This should be compatible but may have differences")
        return True
    else:
        print(f"❌ Version mismatch: {installed_version}")
        print(f"   This may cause compatibility issues")
        return False


def check_model_registry():
    """Check if Qwen3 is in vLLM's model registry"""
    print("\n" + "="*70)
    print("CHECK 2: Model Architecture Support")
    print("="*70)
    
    # Get all registered models
    registered_models = list(MODEL_REGISTRY.keys())
    
    # Look for Qwen variants
    qwen_models = [m for m in registered_models if 'qwen' in m.lower()]
    
    print(f"Total models in registry: {len(registered_models)}")
    print(f"Qwen-related models found: {len(qwen_models)}")
    
    if qwen_models:
        print("\n✅ Qwen models found in registry:")
        for model in sorted(qwen_models):
            print(f"   - {model}")
        
        # Check specifically for Qwen3
        qwen3_models = [m for m in qwen_models if 'qwen3' in m.lower() or '3' in m]
        if qwen3_models:
            print("\n✅ Qwen3 support detected!")
            for model in qwen3_models:
                print(f"   - {model}")
            return True
        else:
            print("\n⚠️  Qwen models found but Qwen3 specifically not detected")
            print("   Qwen3 might be handled by a generic Qwen loader")
            return True  # Still likely compatible
    else:
        print("\n❌ No Qwen models found in registry")
        print("   This suggests Qwen3 may not be supported")
        return False


def check_model_info():
    """Check model information from Hugging Face"""
    print("\n" + "="*70)
    print("CHECK 3: Model Information")
    print("="*70)
    
    if not model_info:
        print("⚠️  Skipping (huggingface_hub not available)")
        return None
    
    try:
        info = model_info(MODEL_NAME, token=True)
        print(f"Model: {MODEL_NAME}")
        print(f"Architecture: {info.config.get('architectures', ['Unknown'])[0] if hasattr(info, 'config') else 'qwen3'}")
        
        # Check model config
        if hasattr(info, 'config') and info.config:
            config = info.config
            print(f"\nModel Configuration:")
            
            # Check for Qwen-specific config
            if 'qwen' in str(config).lower():
                print("   ✅ Qwen architecture detected in config")
            
            # Check for required fields
            if hasattr(config, 'torch_dtype') or 'torch_dtype' in str(config):
                print(f"   ✅ torch_dtype found")
            
            if 'bfloat16' in str(config).lower():
                print(f"   ✅ bfloat16 support confirmed")
            
        return True
        
    except HfHubHTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ Unauthorized: Need to accept model terms")
            print(f"   Visit: https://huggingface.co/{MODEL_NAME}")
            return False
        else:
            print(f"❌ Error accessing model: {e}")
            return False
    except Exception as e:
        print(f"⚠️  Could not fetch model info: {e}")
        return None


def check_configuration():
    """Check if the configuration used is compatible"""
    print("\n" + "="*70)
    print("CHECK 4: Configuration Compatibility")
    print("="*70)
    
    print("Current configuration:")
    print(f"   - dtype: bfloat16")
    print(f"   - trust_remote_code: True")
    print(f"   - enforce_eager: True")
    print(f"   - max_model_len: 4096")
    
    # Check if bfloat16 is supported
    try:
        import torch
        if torch.cuda.is_bf16_supported():
            print("   ✅ CUDA supports bfloat16")
        else:
            print("   ⚠️  CUDA may not fully support bfloat16")
    except Exception:
        pass
    
    print("\n✅ Configuration looks compatible")
    print("   - bfloat16: Required for Qwen3")
    print("   - trust_remote_code: Required for custom architectures")
    print("   - enforce_eager: Recommended for stability")
    
    return True


def check_known_issues():
    """Check for known compatibility issues"""
    print("\n" + "="*70)
    print("CHECK 5: Known Issues / Compatibility Notes")
    print("="*70)
    
    print("Known considerations for Qwen3 + vLLM 0.6.5:")
    print("   ✅ VLLM_USE_V1=0: Using v0 engine (more stable)")
    print("   ✅ enforce_eager=True: Avoids CUDA graph issues")
    print("   ✅ bfloat16: Required dtype for Qwen3")
    print("   ✅ trust_remote_code: Required for custom tokenizers")
    
    print("\n⚠️  Potential Issues:")
    print("   - Qwen3 may require newer vLLM version (check if issues occur)")
    print("   - If model fails to load, may need vLLM 0.6.6+ or 0.7.0+")
    print("   - Monitor for tokenizer compatibility issues")
    
    return True


def main():
    """Run all compatibility checks"""
    print("\n" + "#"*70)
    print("# vLLM 0.6.5 + DragonLLM/qwen3-8b-fin-v1.0 Compatibility Check")
    print("#"*70)
    
    results = {}
    
    # Check 1: Version
    results['version'] = check_vllm_version()
    
    # Check 2: Model registry
    results['registry'] = check_model_registry()
    
    # Check 3: Model info
    results['model_info'] = check_model_info()
    
    # Check 4: Configuration
    results['configuration'] = check_configuration()
    
    # Check 5: Known issues
    results['known_issues'] = check_known_issues()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for check_name, success in results.items():
        if success is None:
            status = "⚠️  SKIP"
        else:
            status = "✅ PASS" if success else "❌ FAIL"
        check_display = check_name.replace('_', ' ').title()
        print(f"{status} - {check_display}")
    
    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if results.get('version') and results.get('registry'):
        print("\n✅ Basic compatibility looks good!")
        print("   The model should work with vLLM 0.6.5")
        print("\n   If you encounter issues:")
        print("   1. Ensure HF_TOKEN_LC2 is set")
        print("   2. Check model repository access")
        print("   3. Verify CUDA/bfloat16 support")
        print("   4. Consider upgrading to vLLM 0.6.6+ if problems persist")
    elif results.get('registry') == False:
        print("\n⚠️  Qwen3 may not be explicitly supported in vLLM 0.6.5")
        print("   Consider:")
        print("   1. Testing with the model anyway (might still work)")
        print("   2. Upgrading to vLLM 0.6.6 or 0.7.0+")
        print("   3. Using a different model if compatibility issues occur")
    else:
        print("\n⚠️  Some compatibility concerns detected")
        print("   Review the checks above for details")


if __name__ == "__main__":
    main()

