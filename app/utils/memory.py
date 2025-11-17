"""GPU memory management utilities."""

import gc
from typing import Optional, Any

import torch


def clear_gpu_memory(model: Optional[Any] = None, tokenizer: Optional[Any] = None) -> None:
    """Clear GPU memory by emptying CUDA cache and running garbage collection.
    
    This function performs aggressive GPU memory cleanup by:
    1. Clearing CUDA cache
    2. Running multiple garbage collection passes
    
    Important: This function does NOT delete model or tokenizer objects.
    The caller must set their references to None (e.g., `model = None`) 
    for the objects to be garbage collected and GPU memory to be freed.
    
    The model and tokenizer parameters are accepted for API compatibility
    but are not used internally. They serve as documentation that the caller
    should clear their references after calling this function.
    
    Args:
        model: Optional model object (caller must set reference to None)
        tokenizer: Optional tokenizer object (caller must set reference to None)
    """
    if not torch.cuda.is_available():
        return
    
    # Clear CUDA cache
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    gc.collect()
    
    # Force multiple garbage collection passes
    for _ in range(3):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

