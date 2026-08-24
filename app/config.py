from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Auth — if unset, server runs in open dev mode
    rubra_api_key: str | None = None

    # Storage — defaults to SQLite .rubra/rubra.db
    rubra_database_url: str | None = None

    # Server
    rubra_host: str = "0.0.0.0"
    rubra_port: int = 8000
    rubra_debug: bool = False

    # CORS — restrict in production
    rubra_cors_origins: list[str] = ["*"]


settings = Settings()
