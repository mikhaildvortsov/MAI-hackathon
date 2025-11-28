"""API routes for email generation."""

from fastapi import APIRouter

from ..models import (
    EmailGenerationRequest,
    EmailGenerationResponse,
    EmailAnalysisRequest,
    EmailParametersResponse,
)
from ..services.chatgpt_client import ChatGPTService

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.post("/generate", response_model=EmailGenerationResponse)
def generate_email(request: EmailGenerationRequest) -> EmailGenerationResponse:
    """Generate a professional email based on the request parameters."""
    service = ChatGPTService()
    return service.generate_letter(request)


@router.post("/analyze", response_model=EmailParametersResponse)
def analyze_email(request: EmailAnalysisRequest) -> EmailParametersResponse:
    """Analyze incoming email and automatically determine optimal parameters."""
    service = ChatGPTService()
    
    params = service.analyze_email_parameters(
        subject=request.source_subject,
        body=request.source_body,
        company_context=request.company_context,
    )
    
    return EmailParametersResponse(parameters=params)
