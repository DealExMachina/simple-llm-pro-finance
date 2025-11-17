"""GPU memory management utilities."""

import gc
import warnings
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
    
    .. deprecated:: 
        The `model` and `tokenizer` parameters are deprecated and will be removed
        in a future release. The function will become parameterless in the next major
        version. These parameters are no longer used internally.
    
    Args:
        model: Optional model object (deprecated, will be removed in future release)
        tokenizer: Optional tokenizer object (deprecated, will be removed in future release)
    """
    # Emit deprecation warning if parameters are provided
    if model is not None or tokenizer is not None:
        warnings.warn(
            "The 'model' and 'tokenizer' parameters to clear_gpu_memory() are deprecated "
            "and will be removed in a future release. The function will become parameterless "
            "in the next major version. These parameters are no longer used internally. "
            "Simply call clear_gpu_memory() without arguments.",
            DeprecationWarning,
            stacklevel=2
        )
    
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

