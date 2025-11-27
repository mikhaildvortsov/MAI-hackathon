"""Converts API input into a ChatGPT-ready prompt."""

from __future__ import annotations

from textwrap import dedent
from typing import List, Dict

from ..models import EmailGenerationRequest, EmailParameters


def _map_length(length: str) -> str:
    return {
        "short": "3-4 предложения",
        "medium": "5-8 предложений",
        "long": "8-12 предложений",
    }[length]


def _render_parameters(params: EmailParameters) -> str:
    directives = [
        f"Тон: {params.tone}",
        f"Цель: {params.purpose}",
        f"Длина: {_map_length(params.length)}",
        f"Аудитория: {params.audience}",
        f"Стиль обращения: {params.address_style}",
        f"Формальные приветствия: {'да' if params.include_formal_greetings else 'нет'}",
        f"Приветствие и заключение: {'включить' if params.include_greeting_and_signoff else 'опустить'}",
        f"Срочность: {params.urgency}",
        f"Корпоративные фразы: {'использовать' if params.include_corporate_phrases else 'избегать'}",
    ]
    if params.extra_directives:
        directives.append("Доп. указания: " + "; ".join(params.extra_directives))
    return "\n".join(f"- {item}" for item in directives)


def _compose_context(req: EmailGenerationRequest) -> str:
    sections = [f"Постоянный корпоративный контекст:\n{req.company_context.strip()}"]

    if req.custom_prompt:
        sections.append(
            "Дополнительное описание задачи:\n" + req.custom_prompt.strip()
        )

    sender_lines = []
    if req.sender_first_name:
        sender_lines.append(f"- Имя: {req.sender_first_name}")
    if req.sender_last_name:
        sender_lines.append(f"- Фамилия: {req.sender_last_name}")
    if req.sender_position:
        sender_lines.append(f"- Должность: {req.sender_position}")
    if sender_lines:
        sections.append("Данные подписанта:\n" + "\n".join(sender_lines))

    return "\n\n".join(sections)


def build_messages(req: EmailGenerationRequest) -> List[Dict[str, str]]:
    """Return chat messages array for OpenAI Chat Completions API."""
    params_section = _render_parameters(req.parameters)
    context_block = _compose_context(req)
    prompt = dedent(
        f"""
        Ты корпоративный ассистент крупного банка. Сгенерируй черновик письма,
        строго соблюдая требования ниже.

        Входящее письмо:
        Тема: {req.source_subject}
        Текст:
        {req.source_body}

        {context_block}

        Параметры стилизации:
        {params_section}

        Требования:
        - При необходимости переформулируй факты, но не добавляй неподтверждённые данные.
        - Если исходное письмо содержит вопросы, дай чёткие ответы пунктами.
        - Укажи степень срочности в тексте, если параметр urgency = high.
        - Не оставляй пустых шаблонных заглушек.
        - Ответ возвращай строго в формате:
          Тема: <краткая формулировка>
          Тело:
          <готовый текст письма>
        - Заверши письмо подписью из блока "Данные подписанта" (Имя, Фамилия, Должность), перечисляя каждое поле с новой строки. Если данных нет, ограничься общим корпоративным завершением.
        """
    ).strip()
    return [
        {
            "role": "system",
            "content": (
                "Ты профессиональный автор деловой корреспонденции. "
                "Всегда отвечай на русском языке."
            ),
        },
        {"role": "user", "content": prompt},
    ]

