# BizMail AI Assistant

Минимальный сервис FastAPI, который получает параметры письма и вызывает ChatGPT для генерации ответа в корпоративном стиле.

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # заполните OPENAI_API_KEY
uvicorn backend.app.main:app --reload
```

Документация доступна на `http://localhost:8000/api/docs`.

## Проверка интеграции

```bash
PYTHONPATH=. pytest -q
```

## Пример запроса

- По умолчанию `custom_prompt` оставляйте пустым (`""` или просто не передавайте). Добавляйте текст только тогда, когда нужно явно описать задачу или цель письма.

```bash
curl -X POST http://localhost:8000/api/emails/generate \
  -H "Content-Type: application/json" \
  -d '{
        "source_subject":"Ответ ФНС",
        "source_body":"Напоминаем о необходимости отчета до 30 ноября.",
        "company_context":"ПАО Банк. Соблюдаем строгий деловой стиль.",
        "sender_first_name":"Анна",
        "sender_last_name":"Иванова",
        "sender_position":"Начальник управления комплаенса",
        "custom_prompt":"",
        "parameters":{
          "tone":"formal",
          "purpose":"response",
          "length":"short",
          "audience":"regulator",
          "address_style":"vy",
          "include_formal_greetings":true,
          "include_greeting_and_signoff":true,
          "urgency":"high",
          "include_corporate_phrases":true,
          "extra_directives":["Добавь блок со следующими шагами"]
        }
      }'
```

### Тестовые сценарии

1. **Ответ регулятору (высокая срочность)**  
   ```json
   {
     "source_subject": "Запрос ЦБ по отчётности",
     "source_body": "Прошу предоставить обновлённый отчёт по ликвидности до конца дня.",
     "company_context": "ПАО Банк. Соблюдаем строгий деловой стиль.",
     "sender_first_name": "Ирина",
     "sender_last_name": "Петрова",
     "sender_position": "Директор департамента отчётности",
     "custom_prompt": "",
     "parameters": {
       "tone": "formal",
       "purpose": "response",
       "length": "medium",
       "audience": "regulator",
       "address_style": "vy",
       "include_formal_greetings": true,
       "include_greeting_and_signoff": true,
       "urgency": "high",
       "include_corporate_phrases": true
     }
   }
   ```

2. **Коммерческое предложение партнёру**  
   ```json
   {
     "source_subject": "Совместная акция",
     "source_body": "Партнёр просит описать условия совместной программы лояльности.",
     "company_context": "ПАО Банк. Фокус на выгоде для клиента.",
     "sender_first_name": "Дмитрий",
     "sender_last_name": "Николаев",
     "sender_position": "Руководитель партнёрских программ",
     "custom_prompt": "Сделай акцент на совместной выгоде и мягко попроси фидбек до пятницы.",
     "parameters": {
       "tone": "friendly",
       "purpose": "proposal",
       "length": "medium",
       "audience": "partner",
       "address_style": "full_name",
       "include_formal_greetings": true,
       "include_greeting_and_signoff": true,
       "urgency": "normal",
       "include_corporate_phrases": false,
       "extra_directives": ["Добавь список следующих шагов"]
     }
   }
   ```

3. **Внутреннее уведомление команде**  
   ```json
   {
     "source_subject": "Перенос дедлайна",
     "source_body": "Нужно уведомить команду об изменении срока сдачи проекта на 5 декабря.",
     "company_context": "ПАО Банк. Команда разработки BizMail.",
     "sender_first_name": "Мария",
     "sender_last_name": "Семенова",
     "sender_position": "Тимлид BizMail",
     "custom_prompt": "",
     "parameters": {
       "tone": "neutral",
       "purpose": "notification",
       "length": "short",
       "audience": "colleague",
       "address_style": "vy",
       "include_formal_greetings": false,
       "include_greeting_and_signoff": true,
       "urgency": "normal",
       "include_corporate_phrases": false
     }
   }
   ```

## Структура

- `backend/app/models.py` – Pydantic-модели и параметры тонкой настройки (включая `custom_prompt` и поля `sender_first_name`/`sender_last_name`/`sender_position` для подписи).
- `backend/app/services/prompt_builder.py` – генерация промпта из параметров.
- `backend/app/services/chatgpt_client.py` – вызов OpenAI и парсинг ответа.
- `backend/app/api/routes.py` – REST-эндпоинт `/api/emails/generate`.
- `tests/test_prompt_builder.py` – проверяет, что параметры попадают в промпт.

