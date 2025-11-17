"""Main FastAPI application entry point."""

import logging
import threading
from typing import Dict

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware import api_key_guard
from app.routers import openai_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Pro Finance API (Transformers)",
    description="OpenAI-compatible API for financial LLM inference",
    version="1.0.0"
)

# Mount routers
app.include_router(openai_api.router, prefix="/v1")

# Optional API key middleware
app.middleware("http")(api_key_guard)


@app.on_event("startup")
async def startup_event() -> None:
    """Startup event - initialize model in background thread.
    
    Loads the model asynchronously to avoid blocking the API startup.
    Model loading happens in a daemon thread so it doesn't prevent shutdown.
    """
    logger.info("Starting LLM Pro Finance API...")
    
    force_reload = settings.force_model_reload
    if force_reload:
        logger.info("Force model reload enabled (FORCE_MODEL_RELOAD=true)")
    
    logger.info("Initializing model in background thread...")
    
    def load_model() -> None:
        """Load the model in a background thread."""
        from app.providers.transformers_provider import initialize_model
        initialize_model(force_reload=force_reload)
    
    # Start model loading in background thread
    thread = threading.Thread(target=load_model, daemon=True)
    thread.start()
    logger.info("Model initialization started in background")


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning API status and information.
    
    Returns:
        Dictionary containing API status, service name, version, model, and backend.
    """
    return {
        "status": "ok", 
        "service": "Qwen Open Finance R 8B Inference", 
        "version": "1.0.0",
        "model": settings.model,
        "backend": "Transformers"
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    """Liveness check endpoint for monitoring and load balancers.
    
    Returns:
        Dictionary indicating the service is alive.
    """
    return {"status": "service alive", "service": "LLM Pro Finance API"}


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness check endpoint for orchestrators and load balancers.
    
    Checks if the model is loaded and ready to handle requests.
    Returns 503 Service Unavailable if the model is not ready.
    
    Returns:
        JSONResponse with ready/model_loaded fields and appropriate status code.
    """
    from app.providers.transformers_provider import is_model_ready
    
    model_loaded = is_model_ready()
    ready_status = model_loaded
    
    response_data = {
        "ready": ready_status,
        "model_loaded": model_loaded,
        "service": "LLM Pro Finance API"
    }
    
    if ready_status:
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(
            content=response_data,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


