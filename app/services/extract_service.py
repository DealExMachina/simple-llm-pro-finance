import json
from pathlib import Path
from typing import List

from app.config import settings
from app.models.priips import ExtractRequest, ExtractResult, PriipsFields
from app.providers import vllm
from app.utils.pdf import download_to_tmp, extract_text_from_pdf
from app.utils.json_guard import try_parse_json


def build_prompt(text: str) -> str:
    schema = {
        "product_name": "string",
        "manufacturer": "string",
        "isin": "string",
        "sri": "integer (1-7)",
        "recommended_holding_period": "string",
        "costs": {
            "entry_cost_pct": "number?",
            "ongoing_cost_pct": "number?",
            "exit_cost_pct": "number?",
        },
        "performance_scenarios": [
            {"name": "string", "description": "string?", "return_pct": "number?"}
        ],
        "date": "string?",
        "language": "string?",
        "source_url": "string?",
    }
    instruction = (
        "You are an expert financial document parser. "
        "Extract the requested PRIIPs fields as STRICT JSON only, no extra text. "
        f"JSON schema keys: {list(schema.keys())}."
    )
    return f"{instruction}\n\nDocument:\n{text[:15000]}"


async def process_source(src: str) -> ExtractResult:
    try:
        path: Path
        if src.lower().startswith("http"):
            path = await download_to_tmp(src, Path(".tmp"))
        else:
            path = Path(src)
        text = extract_text_from_pdf(path)
        prompt = build_prompt(text)

        payload = {
            "model": settings.model,
            "messages": [
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 800,
            "stream": False,
        }
        data = await vllm.chat(payload, stream=False)

        # vLLM OpenAI response
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            if isinstance(data, dict)
            else ""
        )
        ok, parsed = try_parse_json(content)
        if not ok:
            return ExtractResult(source=src, success=False, error=str(parsed))

        model_data = PriipsFields(**parsed)
        model_data.source_url = src
        return ExtractResult(source=src, success=True, data=model_data)
    except Exception as e:
        return ExtractResult(source=src, success=False, error=str(e))


async def extract(req: ExtractRequest) -> List[ExtractResult]:
    results: List[ExtractResult] = []
    for src in req.sources:
        results.append(await process_source(src))
    return results


