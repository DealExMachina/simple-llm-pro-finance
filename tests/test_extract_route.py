from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_extract_priips(monkeypatch, tmp_path):
    # Fake PDF extraction
    from app.services import extract_service

    def fake_extract_text_from_pdf(path):
        return "Product: Test Fund ISIN: TEST1234567 SRI: 3"

    monkeypatch.setattr(extract_service, "extract_text_from_pdf", fake_extract_text_from_pdf)

    # Fake vLLM chat returning JSON
    from app.providers import vllm

    async def fake_chat(payload, stream=False):
        return {
            "id": "cmpl-2",
            "object": "chat.completion",
            "created": 0,
            "model": payload["model"],
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "{\"product_name\":\"Test Fund\",\"isin\":\"TEST1234567\",\"sri\":3}",
                    },
                    "finish_reason": "stop",
                }
            ],
        }

    monkeypatch.setattr(vllm, "chat", fake_chat)

    r = client.post(
        "/extract-priips",
        json={"sources": ["/path/to/local.pdf"]},
    )
    assert r.status_code == 200
    j = r.json()
    assert j[0]["success"] is True
    assert j[0]["data"]["isin"] == "TEST1234567"


