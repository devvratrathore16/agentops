# AgentOps API (Phase 1A)

This package contains the FastAPI, PostgreSQL, SQLAlchemy, and Alembic foundation. It currently provides liveness and database-readiness endpoints only. Authentication, sessions, organizations, projects, API keys, and tenant authorization are planned for Phase 1B/1C. Telemetry ingestion, workers, SDK features, and product APIs are not part of this milestone.

## Requirements

- Python 3.12 or newer.
- [uv](https://docs.astral.sh/uv/) for dependency synchronization and lockfile consistency.
- The repository's PostgreSQL 16 Docker Compose service for local PostgreSQL readiness checks.

## Configuration

Copy or merge the API entries in the root `.env.example` into the root `.env`. Preserve any existing local Compose credentials and set `DATABASE_URL` to match them. The local template uses:

```text
postgresql+psycopg://agentops:change-me-local-only@localhost:5432/agentops
```

Supported settings:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy URL; PostgreSQL with psycopg for application use, SQLite accepted by isolated tests. |
| `APP_ENV` | `development`, `test`, `staging`, or `production`. |
| `ALLOWED_ORIGINS` | JSON array of exact HTTP(S) origins; wildcard and URL paths are rejected. |
| `LOG_LEVEL` | Structured application log threshold. |
| `APP_SECRET_KEY` | Placeholder for later authentication/session milestones; unused in Phase 1A. |
| `SESSION_COOKIE_NAME`, `SESSION_TTL_HOURS`, `SESSION_COOKIE_SECURE` | Session configuration reserved for Phase 1B. |
| `API_KEY_HEADER_NAME` | API-key header configuration reserved for Phase 1C. |

Never commit `.env` or real credentials. In production, use deployment-managed secrets and secure cookie settings.

## Run locally

Start PostgreSQL from the repository root, then run:

```powershell
uv sync --project apps/api
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --project apps/api uvicorn app.main:app --app-dir apps/api --reload
```

Endpoints:

- `GET /api/v1/health` — process liveness; does not require PostgreSQL.
- `GET /api/v1/ready` — executes `SELECT 1` against PostgreSQL and returns 503 if the database is unavailable.
- `/docs` — generated OpenAPI documentation.

Application startup never runs `Base.metadata.create_all()` and never applies migrations automatically. Run Alembic explicitly before starting the service. The current baseline revision records migration history but creates no domain tables; Phase 1B/1C migrations will add approved backend entities.

## Tests and migrations

```powershell
uv run --project apps/api pytest apps/api/tests
uv run --project apps/api alembic -c apps/api/alembic.ini heads
```

The tests use in-memory or temporary SQLite databases and do not use or reset the normal development PostgreSQL database. Alembic upgrade/downgrade tests use a temporary SQLite file. PostgreSQL-specific integration verification requires the Docker Compose database to be running.
