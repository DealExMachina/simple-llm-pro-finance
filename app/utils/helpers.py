"""Helper functions for common operations."""

import os
import logging
from typing import Optional, Tuple, List, Dict, Any

from app.utils.constants import HF_TOKEN_VARS, FRENCH_PHRASES, FRENCH_CHARS, FRENCH_PATTERNS


logger = logging.getLogger(__name__)


def get_hf_token() -> Tuple[Optional[str], str]:
    """
    Get Hugging Face token from environment variables.
    
    Returns:
        Tuple of (token, token_source_name)
    """
    for var_name in HF_TOKEN_VARS:
        token = os.getenv(var_name)
        if token:
            return token, var_name
    return None, "none"


def is_french_request(messages: List[Dict[str, Any]]) -> bool:
    """
    Detect if the request is in French based on user messages.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        
    Returns:
        True if French is detected, False otherwise
    """
    user_messages = [msg for msg in messages if msg.get("role") == "user"]
    
    for msg in user_messages:
        content = msg.get("content", "")
        content_lower = content.lower()
        
        # Check for explicit French language request
        if any(phrase in content_lower for phrase in FRENCH_PHRASES):
            return True
        
        # Check for French characters
        if any(char in content for char in FRENCH_CHARS):
            return True
        
        # Check for French question patterns
        if any(pattern in content_lower for pattern in FRENCH_PATTERNS):
            return True
    
    return False


def has_french_system_prompt(messages: List[Dict[str, Any]]) -> bool:
    """Check if messages already contain a French system prompt."""
    return any(
        "français" in msg.get("content", "").lower()
        for msg in messages
        if msg.get("role") == "system"
    )


def log_info(message: str, print_output: bool = False):
    """Log info message, optionally also print."""
    logger.info(message)
    if print_output:
        print(message)


def log_warning(message: str, print_output: bool = False):
    """Log warning message, optionally also print."""
    logger.warning(message)
    if print_output:
        print(message)


def log_error(message: str, exc_info: bool = False, print_output: bool = False):
    """Log error message, optionally also print."""
    logger.error(message, exc_info=exc_info)
    if print_output:
        print(message)

