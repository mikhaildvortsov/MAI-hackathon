"""Configuration helpers for the BizMail backend."""

from functools import lru_cache
from typing import Optional
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Holds application-wide configuration."""

    yandex_api_key: str
    yandex_folder_id: str
    yandex_model: str
    
    # Redis cache settings
    redis_enabled: bool
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: Optional[str]
    redis_ttl_analysis: int  # TTL for analysis cache in hours
    redis_ttl_generation: int  # TTL for generation cache in hours

    def __init__(self) -> None:
        api_key = os.getenv("YANDEX_API_KEY") or os.getenv("api_key")
        folder_id = os.getenv("YANDEX_FOLDER_ID") or os.getenv("folder_id")
        
        if not api_key:
            raise RuntimeError("YANDEX_API_KEY (or api_key) is not set")
        if not folder_id:
            raise RuntimeError("YANDEX_FOLDER_ID (or folder_id) is not set")

        self.yandex_api_key = api_key
        self.yandex_folder_id = folder_id
        self.yandex_model = os.getenv("YANDEX_MODEL", "qwen3-235b-a22b-fp8/latest")
        
        # Redis configuration
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.redis_ttl_analysis = int(os.getenv("REDIS_TTL_ANALYSIS_HOURS", "24"))  # 24 hours default
        self.redis_ttl_generation = int(os.getenv("REDIS_TTL_GENERATION_HOURS", "12"))  # 12 hours default


def get_settings() -> Settings:
    """Return settings instance."""
    return Settings()

