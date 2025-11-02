"""GPU memory management utilities."""

import gc
import torch
from typing import Optional


def clear_gpu_memory(model=None, tokenizer=None):
    """Clear GPU memory completely."""
    if not torch.cuda.is_available():
        return
    
    # Delete model and tokenizer if provided
    if model is not None:
        try:
            del model
        except Exception:
            pass
    
    if tokenizer is not None:
        try:
            del tokenizer
        except Exception:
            pass
    
    # Clear CUDA cache
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    gc.collect()
    
    # Force multiple garbage collection passes
    for _ in range(3):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

