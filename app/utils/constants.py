"""Application-wide constants and configuration."""

import os
from typing import Final, List


# Model configuration
MODEL_NAME: Final[str] = "DragonLLM/qwen3-8b-fin-v1.0"

# Cache directory - respect HF_HOME if set, otherwise use default
CACHE_DIR: Final[str] = os.getenv("HF_HOME", "/tmp/huggingface")

# Hugging Face token environment variable priority order
HF_TOKEN_VARS: Final[List[str]] = [
    "HF_TOKEN_LC2",
    "HF_TOKEN_LC",
    "HF_TOKEN",
    "HUGGING_FACE_HUB_TOKEN"
]

# French language detection patterns
FRENCH_PHRASES: Final[List[str]] = [
    "en français",
    "répondez en français",
    "réponse française",
    "répondez uniquement en français",
    "expliquez en français",
]

FRENCH_CHARS: Final[List[str]] = [
    "é", "è", "ê", "à", "ç", "ù", "ô", "î", "â", "û", "ë", "ï"
]

FRENCH_PATTERNS: Final[List[str]] = [
    "qu'est-ce",
    "qu'est",
    "expliquez",
    "comment",
    "pourquoi",
    "combien",
    "quel",
    "quelle",
    "quels",
    "quelles",
    "où",
    "quand",
    "définissez",
]

FRENCH_SYSTEM_PROMPT: Final[str] = (
    "Vous êtes un assistant financier expert. "
    "Répondez TOUJOURS en français. "
    "Soyez concis et précis dans vos explications. "
    "Fournissez des réponses claires et complètes sans développements excessifs."
)

# Qwen3 EOS tokens
EOS_TOKENS: Final[List[int]] = [151645, 151643]  # [<|im_end|>, <|endoftext|>]
PAD_TOKEN_ID: Final[int] = 151643  # <|endoftext|>

# Generation defaults
DEFAULT_MAX_TOKENS: Final[int] = 1000  # Increased for complete answers with concise reasoning
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_TOP_P: Final[float] = 1.0
DEFAULT_TOP_K: Final[int] = 20
REPETITION_PENALTY: Final[float] = 1.05

# Model initialization constants
MODEL_INIT_TIMEOUT_SECONDS = 300  # 5 minutes timeout for model initialization
MODEL_INIT_WAIT_INTERVAL_SECONDS = 1  # Check interval while waiting for initialization

# Rate limiting constants (for demo/single user)
RATE_LIMIT_REQUESTS_PER_MINUTE = 30  # 30 requests per minute (generous for single user)
RATE_LIMIT_REQUESTS_PER_HOUR = 500  # 500 requests per hour

# Confidence calculation constants
MIN_ANSWER_LENGTH_FOR_HIGH_CONFIDENCE = 50  # Minimum answer length for high confidence score

