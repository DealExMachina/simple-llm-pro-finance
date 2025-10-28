from fastapi import APIRouter

from app.models.priips import ExtractRequest
from app.services import extract_service


router = APIRouter()


@router.post("/extract-priips")
async def extract_priips(body: ExtractRequest):
    return await extract_service.extract(body)


