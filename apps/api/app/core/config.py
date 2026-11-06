"""Validated application settings sourced from environment variables."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the API process.

    Authentication-related settings are declared now for one consistent
    environment contract; they are not consumed until their implementation
    milestone.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str = Field(validation_alias="DATABASE_URL")
    app_env: Literal["development", "test", "staging", "production"] = Field(
        default="development", validation_alias="APP_ENV"
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        validation_alias="ALLOWED_ORIGINS",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", validation_alias="LOG_LEVEL"
    )

    app_secret_key: SecretStr | None = Field(default=None, validation_alias="APP_SECRET_KEY")
    session_cookie_name: str = Field(default="agentops_session", validation_alias="SESSION_COOKIE_NAME")
    session_ttl_hours: int = Field(default=168, ge=1, le=8760, validation_alias="SESSION_TTL_HOURS")
    session_cookie_secure: bool = Field(default=True, validation_alias="SESSION_COOKIE_SECURE")
    api_key_header_name: str = Field(default="Authorization", validation_alias="API_KEY_HEADER_NAME")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"postgresql+psycopg", "sqlite+pysqlite", "sqlite"}:
            raise ValueError("DATABASE_URL must use PostgreSQL with psycopg or SQLite for isolated tests")
        if parsed.scheme.startswith("postgresql") and not parsed.hostname:
            raise ValueError("DATABASE_URL must include a database host")
        return value

    @field_validator("allowed_origins")
    @classmethod
    def validate_allowed_origins(cls, origins: list[str]) -> list[str]:
        normalized: list[str] = []
        for origin in origins:
            candidate = origin.strip().rstrip("/")
            parsed = urlsplit(candidate)
            if (
                candidate == "*"
                or parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.path
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("ALLOWED_ORIGINS must contain explicit HTTP(S) origins without paths or wildcards")
            normalized.append(candidate)
        return normalized

    @model_validator(mode="after")
    def restrict_sqlite_to_tests(self) -> "Settings":
        if self.app_env != "test" and urlsplit(self.database_url).scheme.startswith("sqlite"):
            raise ValueError("SQLite DATABASE_URL is allowed only when APP_ENV=test")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return process settings, cached after first validation."""

    return Settings()
