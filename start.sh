#!/bin/bash
# Get port from environment variable, default to 7860
PORT=${PORT:-7860}

# Redirect all output to stderr so it shows in logs
exec >&2

# Start uvicorn with the specified port
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

