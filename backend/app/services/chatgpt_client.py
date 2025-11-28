"""Thin OpenAI ChatGPT wrapper."""

from __future__ import annotations

import json
import re
from typing import Protocol

from openai import OpenAI

from ..config import get_settings
from ..models import EmailGenerationRequest, EmailGenerationResponse, EmailParameters
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
        """Генерирует письмо на основе запроса."""
        messages = build_messages(payload)
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.4,
        )
        raw_text = completion.choices[0].message.content or ""
        subject, body = _extract_subject_and_body(raw_text)

        return EmailGenerationResponse(subject=subject, body=body)

    def analyze_email_parameters(
        self, subject: str, body: str, company_context: str
    ) -> EmailParameters:
        """
        Анализирует входящее письмо и определяет оптимальные параметры для ответа.
        """
        analysis_prompt = f"""Проанализируй входящее письмо и определи оптимальные параметры для ответа.

Входящее письмо:
Тема: {subject}
Текст: {body}
Контекст компании: {company_context}

Верни ТОЛЬКО валидный JSON со следующими параметрами:
{{
  "tone": "formal",
  "purpose": "response",
  "length": "medium",
  "audience": "colleague",
  "urgency": "normal",
  "address_style": "vy",
  "include_formal_greetings": true,
  "include_greeting_and_signoff": true,
  "include_corporate_phrases": true
}}

Возможные значения:
- tone: "formal" | "neutral" | "friendly"
- purpose: "response" | "proposal" | "notification" | "refusal"
- length: "short" | "medium" | "long"
- audience: "colleague" | "manager" | "client" | "partner" | "regulator"
- urgency: "low" | "normal" | "high"
- address_style: "vy" | "ty" | "full_name"
"""

        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по деловой переписке. Отвечай только валидным JSON.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            raw_json = completion.choices[0].message.content or "{}"
            params_dict = json.loads(raw_json.strip())
            
            return EmailParameters(**params_dict)

        except Exception as e:
            print(f"Ошибка анализа параметров: {e}")
            return EmailParameters(
                tone="formal",
                purpose="response",
                length="medium",
                audience="colleague",
                urgency="normal",
                address_style="vy",
                include_formal_greetings=True,
                include_greeting_and_signoff=True,
                include_corporate_phrases=True,
            )
