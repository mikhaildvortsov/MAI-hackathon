"""YandexGPT API client using Responses API."""

from __future__ import annotations

import json
import re

import httpx

from ..config import get_settings
from ..models import EmailGenerationRequest, EmailGenerationResponse, EmailParameters
from .prompt_builder import build_messages
from .department_detector import detect_department_by_keywords, get_department_instruction


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
    else:
        body = raw_text.strip()

    # Убираем строку "Направить в [отдел]" если она есть
    body = re.sub(r'\n?\s*Направить в .+?\n?$', '', body, flags=re.IGNORECASE | re.MULTILINE)
    body = re.sub(r'\n?\s*направить в .+?\n?$', '', body, flags=re.MULTILINE)

    # Сохраняем переносы строк в теле письма (особенно для подписи)
    # Только убираем множественные пробелы, но сохраняем переносы строк
    lines = body.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = re.sub(r'\s+', ' ', line.strip())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
        else:
            cleaned_lines.append('')
    
    body = '\n'.join(cleaned_lines).strip()
    return subject, body


class YandexGPTService:
    """YandexGPT API client using Responses API."""

    def __init__(self, api_key: str | None = None, folder_id: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.yandex_api_key
        self._folder_id = folder_id or settings.yandex_folder_id
        self._model = settings.yandex_model
        self._api_url = "https://rest-assistant.api.cloud.yandex.net/v1/responses"

    def _make_request(self, messages: list[dict[str, str]], temperature: float = 0.4, response_format: dict | None = None) -> str:
        """Make request to YandexGPT Responses API."""
        system_message = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg["content"])

        instructions = system_message or "Ты полезный ассистент."
        input_text = "\n\n".join(user_messages)

        model_uri = f"gpt://{self._folder_id}/{self._model}"
        
        headers = {
            "Authorization": f"Api-Key {self._api_key}",
            "x-folder-id": self._folder_id,
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_uri,
            "instructions": instructions,
            "input": input_text,
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self._api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "failed" or result.get("error"):
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    error_code = result.get("error", {}).get("code", "")
                    if "Failed to get model" in error_msg or error_code == "model_call_error":
                        raise RuntimeError(
                            f"Модель '{self._model}' недоступна в вашем каталоге. "
                            f"Проверьте:\n"
                            f"1. Что модель активирована в консоли Яндекс.Облака\n"
                            f"2. Что у вас есть доступ к модели в каталоге {self._folder_id}\n"
                            f"3. Попробуйте другую модель, например: qwen3-235b-a22b-fp8/latest или yandexgpt/latest"
                        )
                    raise RuntimeError(f"YandexGPT API error: {error_msg}")
                
                output_text = result.get("output_text")
                if output_text:
                    return output_text.strip()
                
                output = result.get("output")
                if output and isinstance(output, list):
                    texts = []
                    for msg in output:
                        if isinstance(msg, dict) and "content" in msg:
                            for content_item in msg["content"]:
                                if isinstance(content_item, dict) and "text" in content_item:
                                    texts.append(content_item["text"])
                    if texts:
                        return "\n".join(texts).strip()
                
                text = result.get("text")
                if text:
                    return str(text).strip()
                
                raise RuntimeError(f"Empty response from YandexGPT API. Full response: {result}")
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            raise RuntimeError(f"YandexGPT API HTTP error {e.response.status_code}: {error_detail}") from e
        except Exception as e:
            raise RuntimeError(f"YandexGPT API error: {e}") from e

    def generate_letter(self, payload: EmailGenerationRequest) -> EmailGenerationResponse:
        """Генерирует письмо на основе запроса."""
        # Определяем отдел банка на основе содержания письма
        department = detect_department_by_keywords(
            payload.source_subject,
            payload.source_body
        )
        
        # Формируем промпт с информацией об отделе
        messages = build_messages(payload, department=department)
        raw_text = self._make_request(messages, temperature=0.4)
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
  * "client" - Клиент банка (получает услуги: кредиты, вклады, счета)
  * "partner" - Бизнес-партнер (сотрудничество на равных: интеграции, совместные проекты, B2B)
- urgency: "low" | "normal" | "high"
- address_style: "vy" | "ty" | "full_name"
"""

        try:
            raw_json = self._make_request(
                [
                    {
                        "role": "system",
                        "content": "Ты эксперт по деловой переписке. Отвечай только валидным JSON.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            if isinstance(raw_json, str):
                raw_json = raw_json.strip()
            else:
                raw_json = str(raw_json).strip()
            
            params_dict = json.loads(raw_json)
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

