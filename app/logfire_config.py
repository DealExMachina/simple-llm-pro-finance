"""Logfire configuration for LLM Pro Finance API."""

import logfire
from app import __version__
from app.config import settings

# Flag to avoid multiple configurations
_logfire_configured = False


def configure_logfire(send_to_logfire: bool | str | None = 'if-token-present'):
    """
    Configure Logfire for the LLM Pro Finance API project.
    
    Args:
        send_to_logfire: If 'if-token-present', only sends if a token is present.
                        If False, completely disables sending.
                        If True, forces sending (requires authentication).
    """
    global _logfire_configured
    
    if _logfire_configured:
        return
    
    logfire.configure(
        service_name="llm-pro-finance",
        service_version=__version__,
        environment=settings.environment,
        send_to_logfire=send_to_logfire,
        # Token is automatically retrieved from:
        # - LOGFIRE_TOKEN environment variable
        # - Or via logfire auth (stored in .logfire/)
        # Project and organization are determined by the token
    )
    
    _logfire_configured = True

