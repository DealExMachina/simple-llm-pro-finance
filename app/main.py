from typing import Dict, Any
from fastapi import FastAPI
from app.middleware import api_key_guard
from app.middleware.rate_limit import rate_limit_middleware
from app.routers import openai_api
from app.config import settings
from app.providers.transformers_provider import model, _initialized
from app.utils.stats import get_stats_tracker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Pro Finance API (Transformers)")

# Mount routers
app.include_router(openai_api.router, prefix="/v1")

# Middleware order: rate limiting first, then API key guard
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(api_key_guard)

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize model in background"""
    import threading
    logger.info("Starting LLM Pro Finance API...")
    
    force_reload = settings.force_model_reload
    if force_reload:
        logger.info("Force model reload enabled (FORCE_MODEL_RELOAD=true)")
    
    logger.info("Initializing model in background thread...")
    
    def load_model():
        from app.providers.transformers_provider import initialize_model
        initialize_model(force_reload=force_reload)
    
    # Start model loading in background thread
    thread = threading.Thread(target=load_model, daemon=True)
    thread.start()
    logger.info("Model initialization started in background")

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning API status and information."""
    return {
        "status": "ok", 
        "service": "Qwen Open Finance R 8B Inference", 
        "version": "1.0.0",
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "backend": "Transformers"
    }

@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint with model readiness status."""
    model_ready = _initialized and model is not None
    return {
        "status": "healthy" if model_ready else "initializing",
        "service": "LLM Pro Finance API",
        "model_ready": model_ready,
    }


@app.get("/v1/stats")
async def get_stats() -> Dict[str, Any]:
    """Get API usage statistics and token counts."""
    stats_tracker = get_stats_tracker()
    return stats_tracker.get_stats()


