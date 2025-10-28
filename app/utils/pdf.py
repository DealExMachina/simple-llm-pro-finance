from pathlib import Path
from typing import Optional

import httpx
import fitz  # PyMuPDF


async def download_to_tmp(url: str, tmp_dir: Path) -> Path:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    filename = url.split("/")[-1] or "document.pdf"
    target = tmp_dir / filename
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        target.write_bytes(r.content)
    return target


def extract_text_from_pdf(path: Path) -> str:
    doc = fitz.open(path)
    try:
        texts: list[str] = []
        for page in doc:
            texts.append(page.get_text("text"))
        return "\n".join(texts).strip()
    finally:
        doc.close()


