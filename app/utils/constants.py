"""Constants used across the application."""

# Environment variable names for HF tokens (in priority order)
HF_TOKEN_VARS = [
    "HF_TOKEN_LC2",
    "HF_TOKEN",
    "HUGGING_FACE_HUB_TOKEN",
]

# French language detection patterns
FRENCH_PHRASES = [
    "en français",
    "réponds en français",
    "parle français",
    "in french",
]

FRENCH_CHARS = "éèêëàâäùûüôöîïç"

FRENCH_PATTERNS = [
    "qu'est-ce",
    "est-ce que",
    "comment",
    "pourquoi",
    "combien",
]

