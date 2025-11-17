"""Middleware package."""

# Import api_key_guard from the parent-level middleware module
# We need to import it directly to avoid circular imports
import os
import importlib.util

# Get the path to the parent middleware.py file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_middleware_file = os.path.join(_parent_dir, "middleware.py")

# Load the middleware.py module directly
spec = importlib.util.spec_from_file_location("app.middleware_module", _middleware_file)
middleware_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(middleware_module)

# Re-export
api_key_guard = middleware_module.api_key_guard
from app.middleware.rate_limit import rate_limit_middleware

__all__ = ["api_key_guard", "rate_limit_middleware"]

