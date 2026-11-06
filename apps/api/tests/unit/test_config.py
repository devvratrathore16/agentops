"""Configuration validation tests."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accept_explicit_local_origins() -> None:
    settings = Settings(
        DATABASE_URL="postgresql+psycopg://agentops:local@localhost:5432/agentops",
        ALLOWED_ORIGINS=["http://localhost:3000", "https://console.example.test"],
    )

    assert settings.allowed_origins == [
        "http://localhost:3000",
        "https://console.example.test",
    ]


@pytest.mark.parametrize(
    "origins",
    [["*"], ["https://example.test/path"], ["file:///tmp"]],
)
def test_settings_reject_unrestricted_or_invalid_cors_origins(origins: list[str]) -> None:
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql+psycopg://agentops:local@localhost:5432/agentops",
            ALLOWED_ORIGINS=origins,
        )


def test_settings_reject_unsupported_database_driver() -> None:
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL="postgresql://localhost/agentops")


def test_settings_reject_sqlite_outside_test_environment() -> None:
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL="sqlite+pysqlite:///:memory:", APP_ENV="development")
