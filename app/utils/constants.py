"""Application-wide constants."""

import os

# Model configuration
MODEL_NAME = "DragonLLM/qwen3-8b-fin-v1.0"

# Cache directory - respect HF_HOME if set, otherwise use default
CACHE_DIR = os.getenv("HF_HOME", "/tmp/huggingface")

# Hugging Face token environment variable priority order
HF_TOKEN_VARS = ["HF_TOKEN_LC2", "HF_TOKEN_LC", "HF_TOKEN", "HUGGING_FACE_HUB_TOKEN"]

# French language detection patterns
FRENCH_PHRASES = [
    "en français",
    "répondez en français",
    "réponse française",
    "répondez uniquement en français",
    "expliquez en français",
]

FRENCH_CHARS = ["é", "è", "ê", "à", "ç", "ù", "ô", "î", "â", "û", "ë", "ï"]

FRENCH_PATTERNS = [
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

FRENCH_SYSTEM_PROMPT = (
    "Vous êtes un assistant financier expert. "
    "Répondez TOUJOURS en français. "
    "Soyez concis et précis dans vos explications. "
    "Fournissez des réponses claires et complètes sans développements excessifs."
)

# Qwen3 EOS tokens
EOS_TOKENS = [151645, 151643]  # [<|im_end|>, <|endoftext|>]
PAD_TOKEN_ID = 151643  # <|endoftext|>

# Generation defaults
DEFAULT_MAX_TOKENS = 1000  # Increased for complete answers with concise reasoning
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 1.0
DEFAULT_TOP_K = 20
REPETITION_PENALTY = 1.05

