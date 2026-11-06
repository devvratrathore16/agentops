"""Test configuration uses an isolated in-memory database, never local PostgreSQL."""

import os
from collections.abc import Generator

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["APP_ENV"] = "test"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost:3000"]'

import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def dispose_test_engine() -> Generator[None, None, None]:
    yield
    engine.dispose()
