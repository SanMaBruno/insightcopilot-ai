import os
from typing import Literal

from pydantic_settings import BaseSettings

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    upload_dir: str = os.path.join(_PROJECT_ROOT, "data", "uploads")
    curated_dir: str = os.path.join(_PROJECT_ROOT, "data", "curated")
    database_url: str = os.path.join(_PROJECT_ROOT, "data", "insightcopilot.db")
    llm_mode: Literal["mock", "gemini", "ollama", "openai"] = "mock"
    embedding_mode: Literal["mock", "gemini", "local", "openai"] = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    etl_mode: Literal["manual", "auto_safe"] = "manual"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
