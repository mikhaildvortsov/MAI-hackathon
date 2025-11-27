"""Configuration helpers for the BizMail backend."""

from functools import lru_cache
from typing import Literal
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Holds application-wide configuration."""

    openai_api_key: str
    openai_model: str

    def __init__(self) -> None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.openai_api_key = key
        self.openai_model = model


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

