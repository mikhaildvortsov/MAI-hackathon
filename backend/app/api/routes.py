"""FastAPI routes for the BizMail backend."""

from fastapi import APIRouter, Depends, HTTPException
import logging

from ..models import EmailGenerationRequest, EmailGenerationResponse
from ..services.chatgpt_client import ChatGPTService

router = APIRouter(prefix="/api", tags=["emails"])
logger = logging.getLogger(__name__)


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
    try:
        return service.generate_letter(payload)
    except Exception as e:
        logger.error(f"Error generating email: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации письма: {str(e)}"
        )

