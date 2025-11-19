from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_models(monkeypatch):
    async def fake_list_models():
        return {"data": [{"id": "DragonLLM/LLM-Pro-Finance-Small"}]}

    from app.providers import transformers_provider

    monkeypatch.setattr(transformers_provider, "list_models", fake_list_models)

    r = client.get("/v1/models")
    assert r.status_code == 200
    j = r.json()
    assert "data" in j


def test_chat_completions(monkeypatch):
    async def fake_chat(payload, stream=False):
        assert payload["model"]
        return {
            "id": "cmpl-1",
            "object": "chat.completion",
            "created": 0,
            "model": payload["model"],
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello"},
                    "finish_reason": "stop",
                }
            ],
        }

    from app.providers import transformers_provider

    monkeypatch.setattr(transformers_provider, "chat", fake_chat)

    r = client.post(
        "/v1/chat/completions",
        json={
            "model": "DragonLLM/LLM-Pro-Finance-Small",
            "messages": [{"role": "user", "content": "Hi"}],
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j["choices"][0]["message"]["content"] == "Hello"


