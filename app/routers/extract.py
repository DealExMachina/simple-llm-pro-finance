from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import tempfile
import os

from app.models.priips import ExtractRequest
from app.services import extract_service


router = APIRouter()


@router.post("/extract-priips")
async def extract_priips(file: UploadFile = File(...)):
    """Extract PRIIPS fields from uploaded PDF"""
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Process the file using the extract service
        req = ExtractRequest(sources=[tmp_path])
        results = await extract_service.extract(req)
        return results[0] if results else {"success": False, "error": "No results"}
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


