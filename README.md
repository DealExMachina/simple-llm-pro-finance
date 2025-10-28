# PRIIPs LLM Service (vLLM + FastAPI)

OpenAI-compatible API and PRIIPs extractor powered by `DragonLLM/LLM-Pro-Finance-Small` via vLLM.

## Setup

1. Create and activate a virtualenv (optional)
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

- Copy `.env.example` to `.env` and adjust values
- Ensure your vLLM server is running and has `HUGGING_FACE_HUB_TOKEN` set so it can pull the model

Start vLLM (example):

```bash
HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
python -m vllm.entrypoints.openai.api_server \
  --model DragonLLM/LLM-Pro-Finance-Small \
  --host 0.0.0.0 --port 8000
```

Run the FastAPI app:

```bash
uvicorn app.main:app --reload --port 8080
```

## OpenAI-compatible API

- GET `/v1/models`
- POST `/v1/chat/completions` (supports `stream=true` if vLLM streaming enabled)

Point PydanticAI/DSPy to `http://localhost:8080/v1` as the base.

## PRIIPs extraction

- POST `/extract-priips` with body:

```json
{
  "sources": ["https://example.com/doc.pdf"],
  "options": {"language": "en", "ocr": false}
}
```

Returns structured JSON validated by Pydantic.
