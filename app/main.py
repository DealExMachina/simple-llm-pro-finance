from fastapi import FastAPI
from app.middleware import api_key_guard
from app.routers import openai_api, extract
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PRIIPs LLM Service (vLLM)")

# Mount routers
app.include_router(openai_api.router, prefix="/v1")
app.include_router(extract.router)

# Optional API key middleware
app.middleware("http")(api_key_guard)

@app.on_event("startup")
async def startup_event():
    """Preload the model on startup"""
    logger.info("Starting PRIIPs LLM Service...")
    logger.info("Model will be loaded on first request to optimize startup time")

@app.get("/")
async def root():
    return {
        "status": "ok", 
        "service": "PRIIPs LLM Service", 
        "version": "1.0.0",
        "model": "DragonLLM/LLM-Pro-Finance-Small",
        "backend": "vLLM"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "PRIIPs LLM Service"}


