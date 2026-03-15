import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="chatbot-backend")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="production")
    log_level: str = Field(default="INFO")

    # OpenAI API configuration
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default="gpt-3.5-turbo")

    # Base URL used by the Streamlit app. HOSTA_API is kept for backward compatibility.
    host_api: str = Field(
        default_factory=lambda: os.getenv("HOST_API")
        or os.getenv("HOSTA_API")
        or "http://localhost:8000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
