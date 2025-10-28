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
    """Startup event - initialize model in background"""
    import threading
    logger.info("Starting PRIIPs LLM Service...")
    logger.info("Initializing model in background thread...")
    
    def load_model():
        from app.providers.vllm import initialize_vllm
        initialize_vllm()
    
    # Start model loading in background thread
    thread = threading.Thread(target=load_model, daemon=True)
    thread.start()
    logger.info("Model initialization started in background")

@app.get("/")
async def root():
    return {
        "status": "ok", 
        "service": "Qwen Open Finance R 8B Inference", 
        "version": "1.0.0",
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "backend": "vLLM"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "PRIIPs LLM Service"}


