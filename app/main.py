from fastapi import FastAPI
from app.middleware import api_key_guard

from app.routers import openai_api, extract


app = FastAPI(title="PRIIPs LLM Service (vLLM)")

# Mount routers
app.include_router(openai_api.router, prefix="/v1")
app.include_router(extract.router)

# Optional API key middleware
app.middleware("http")(api_key_guard)


@app.get("/")
async def root():
    return {"status": "ok"}


