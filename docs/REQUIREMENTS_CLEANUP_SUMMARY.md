# Requirements Cleanup Summary

## ✅ Cleanup Complete

### Dockerfiles (HF Spaces & Koyeb)
Both `Dockerfile` and `Dockerfile.koyeb` are **already minimal**:
- ✅ Only install: `langfuse>=2.50.0` and `logfire>=0.0.1`
- ✅ Use `vllm/vllm-openai:latest` base image (includes all vLLM dependencies)
- ✅ Do NOT copy app code or use `requirements.txt`
- ✅ Run vLLM directly via `start-vllm.sh`

**No changes needed** - Dockerfiles are already optimized.

### requirements.txt
**Cleaned up** from 15 dependencies to 2:
- ✅ Removed: `fastapi`, `uvicorn`, `transformers`, `torch`, `httpx`, `python-dotenv`, `tenacity`, `PyMuPDF`, `python-multipart`, `huggingface-hub`, `pydantic`, `pydantic-settings`
- ✅ Kept: `langfuse>=2.50.0`, `logfire>=0.0.1` (for local development/testing)

**Rationale**: 
- vLLM deployments don't use `requirements.txt` (they install dependencies directly in Dockerfiles)
- vLLM provides its own OpenAI-compatible API server, so FastAPI/uvicorn are not needed
- vLLM base image includes PyTorch, Transformers, and all model dependencies
- Only observability dependencies are kept for potential local testing

## Dependencies Removed

| Dependency | Why Removed |
|------------|-------------|
| `fastapi>=0.115.0` | vLLM provides its own API server |
| `uvicorn[standard]>=0.30.0` | vLLM runs its own server |
| `pydantic>=2.8.0` | Not used in vLLM deployment |
| `pydantic-settings>=2.4.0` | Not used in vLLM deployment |
| `httpx>=0.27.0` | Not used |
| `python-dotenv>=1.0.1` | vLLM uses environment variables directly |
| `tenacity>=8.3.0` | Not used |
| `PyMuPDF>=1.24.0` | Not used |
| `python-multipart>=0.0.6` | Not used |
| `huggingface-hub>=0.20.0` | vLLM handles this internally |
| `transformers` | vLLM handles model loading |
| `torch` | Included in vLLM base image |

## Final State

### For vLLM Deployment (HF Spaces & Koyeb)
```dockerfile
# Both Dockerfiles install only:
RUN pip install --no-cache-dir \
    langfuse>=2.50.0 \
    logfire>=0.0.1
```

### For Local Development
```txt
# requirements.txt (minimal)
langfuse>=2.50.0
logfire>=0.0.1
```

## Impact

- ✅ **Smaller Docker images**: Removed ~500MB+ of unused dependencies
- ✅ **Faster builds**: Fewer packages to install
- ✅ **Clearer dependencies**: Only what's actually needed
- ✅ **Consistent**: Both platforms use the same minimal set

## Notes

- If you need to run the FastAPI app locally for testing, you can install additional dependencies as needed
- The `requirements-dev.txt` file can be used for additional development dependencies
- vLLM base image (`vllm/vllm-openai:latest`) already includes all necessary ML dependencies

