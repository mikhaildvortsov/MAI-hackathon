"""Pydantic models shared across the API."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


Tone = Literal["formal", "neutral", "friendly"]
Purpose = Literal["response", "proposal", "notification", "refusal"]
Length = Literal["short", "medium", "long"]
Audience = Literal["colleague", "manager", "client", "partner", "regulator"]
AddressStyle = Literal["vy", "ty", "full_name"]
Urgency = Literal["low", "normal", "high"]


class EmailParameters(BaseModel):
    """High-level levers that shape the generated letter."""

    tone: Tone = "formal"
    purpose: Purpose = "response"
    length: Length = "medium"
    audience: Audience = "client"
    address_style: AddressStyle = "vy"
    include_formal_greetings: bool = True
    urgency: Urgency = "normal"
    include_corporate_phrases: bool = True
    include_greeting_and_signoff: bool = True
    extra_directives: Optional[list[str]] = Field(
        default=None,
        description="Additional free-form requirements merged into the prompt.",
    )


class EmailGenerationRequest(BaseModel):
    """Request payload for /emails/generate."""

    source_subject: str = Field(
        ..., description="Subject of the inbound letter or summary of request."
    )
    source_body: str = Field(
        ..., description="Original text or structured summary of the incoming letter."
    )
    company_context: str = Field(
        ...,
        description="Corporate facts/boilerplate that should remain stable across replies.",
    )
    sender_first_name: Optional[str] = Field(
        default=None, description="Имя сотрудника, который подписывает письмо."
    )
    sender_last_name: Optional[str] = Field(
        default=None, description="Фамилия сотрудника, который подписывает письмо."
    )
    sender_position: Optional[str] = Field(
        default=None, description="Должность отправителя для блока подписи."
    )
    custom_prompt: Optional[str] = Field(
        default=None,
        description="Optional free-form task description appended to the generated prompt.",
    )
    parameters: EmailParameters = Field(
        default_factory=EmailParameters, description="Controls tone/style of the reply."
    )


class EmailGenerationResponse(BaseModel):
    """Returned to the caller after the LLM produces a draft."""

    subject: str
    body: str

