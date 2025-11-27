"""FastAPI routes for the BizMail backend."""

from fastapi import APIRouter, Depends

from ..models import EmailGenerationRequest, EmailGenerationResponse
from ..services.chatgpt_client import ChatGPTService

router = APIRouter(prefix="/api", tags=["emails"])


def get_chatgpt_service() -> ChatGPTService:
    return ChatGPTService()


@router.post(
    "/emails/generate",
    response_model=EmailGenerationResponse,
    summary="Generate a corporate email draft via ChatGPT",
)
async def generate_email_endpoint(
    payload: EmailGenerationRequest,
    service: ChatGPTService = Depends(get_chatgpt_service),
) -> EmailGenerationResponse:
    return service.generate_letter(payload)

