"""SQLAlchemy engine, session factory, and request-scoped session dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


def _create_engine() -> Engine:
    url = make_url(get_settings().database_url)
    options: dict[str, object] = {"pool_pre_ping": True}
    if url.drivername.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
        if url.database in {None, "", ":memory:"}:
            options["poolclass"] = StaticPool
    return create_engine(url, **options)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped SQLAlchemy session and always close it."""

    with SessionLocal() as session:
        yield session
