"""GPU memory management utilities."""

import gc
from typing import Optional, Any

import torch


def clear_gpu_memory(model: Optional[Any] = None, tokenizer: Optional[Any] = None) -> None:
    """Clear GPU memory completely.
    
    This function performs aggressive GPU memory cleanup by:
    1. Deleting model and tokenizer objects if provided
    2. Clearing CUDA cache
    3. Running multiple garbage collection passes
    
    Args:
        model: Optional model object to delete
        tokenizer: Optional tokenizer object to delete
    """
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

