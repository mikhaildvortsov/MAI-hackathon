from backend.app.services.chatgpt_client import _extract_subject_and_body


def test_extract_subject_and_body_flattens_newlines():
    raw = """Тема: Ответ по заявке
Тело:
Уважаемый коллега,

Сообщаем, что\\nвыполнили задачу.
С уважением,
Банк."""

    subject, body = _extract_subject_and_body(raw)

    assert subject == "Ответ по заявке"
    assert body == "Уважаемый коллега, Сообщаем, что выполнили задачу. С уважением, Банк."

