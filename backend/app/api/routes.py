"""API routes for email generation."""

from fastapi import APIRouter

from ..config import get_settings
from ..models import (
    EmailGenerationRequest,
    EmailGenerationResponse,
    EmailAnalysisRequest,
    EmailParametersResponse,
)
from ..services.yandex_gpt_client import YandexGPTService

router = APIRouter(prefix="/api/emails", tags=["emails"])


def _get_service():
    """Get AI service based on configuration."""
    return YandexGPTService()


@router.post("/generate", response_model=EmailGenerationResponse)
def generate_email(request: EmailGenerationRequest) -> EmailGenerationResponse:
    """Generate a professional email based on the request parameters."""
    service = _get_service()
    return service.generate_letter(request)


@router.post("/analyze", response_model=EmailParametersResponse)
def analyze_email(request: EmailAnalysisRequest) -> EmailParametersResponse:
    """Analyze incoming email and automatically determine optimal parameters."""
    service = _get_service()
    
    params = service.analyze_email_parameters(
        subject=request.source_subject,
        body=request.source_body,
        company_context=request.company_context,
    )
    
    return EmailParametersResponse(parameters=params)
