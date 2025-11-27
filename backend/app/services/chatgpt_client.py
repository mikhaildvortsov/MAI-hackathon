"""Thin OpenAI ChatGPT wrapper."""

from __future__ import annotations

import re
from typing import Protocol

from openai import OpenAI

from ..config import get_settings
from ..models import EmailGenerationRequest, EmailGenerationResponse
from .prompt_builder import build_messages


class ChatCompletionClient(Protocol):
    """Subset of the OpenAI client we rely on, useful for tests."""

    def chat(self) -> object:  # pragma: no cover - structural typing hack
        ...


def _collapse_whitespace(value: str) -> str:
    """Replace escaped sequences and whitespace with single spaces."""
    normalized = value.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", normalized).strip()


def _extract_subject_and_body(raw_text: str) -> tuple[str, str]:
    subject = "Заготовка ответа"
    body = raw_text.strip()

    subject_match = re.search(r"Тема:\s*(.+)", raw_text)
    if subject_match:
        subject = _collapse_whitespace(subject_match.group(1))

    if "Тело:" in raw_text:
        body = raw_text.split("Тело:", maxsplit=1)[1].strip()

    body = _collapse_whitespace(body)
    return subject, body


class ChatGPTService:
    """Encapsulates prompt building and OpenAI invocation."""

    def __init__(self, client: OpenAI | None = None) -> None:
        settings = get_settings()
        self._client = client or OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def generate_letter(self, payload: EmailGenerationRequest) -> EmailGenerationResponse:
        messages = build_messages(payload)
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.4,
        )
        raw_text = completion.choices[0].message.content or ""
        subject, body = _extract_subject_and_body(raw_text)

        return EmailGenerationResponse(subject=subject, body=body)

