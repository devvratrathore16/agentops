"""Alembic upgrade/downgrade tests against a temporary isolated SQLite database."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.core.config import get_settings


def test_baseline_migration_upgrades_and_downgrades(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "migration-test.sqlite3"
    database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).parents[2] / "alembic.ini"
    config = Config(str(alembic_ini))
    command.upgrade(config, "head")

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        assert "alembic_version" in inspector.get_table_names()
        assert "users" not in inspector.get_table_names()
    finally:
        engine.dispose()

    command.downgrade(config, "base")
    command.upgrade(config, "head")
    get_settings.cache_clear()
