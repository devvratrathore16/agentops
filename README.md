# AgentOps

AgentOps is an SDK-first AI agent observability, evaluation, and reliability platform. It is designed to collect structured execution telemetry through an independent Python SDK, process it through an API and background worker, and make it useful to teams through a web application.

The repository has completed Phases 0 and 0.1. Phase 1A establishes the FastAPI and PostgreSQL backend foundation. Authentication, organizations, projects, API keys, and tenant authorization remain in Phase 1B/1C; telemetry ingestion and later product capabilities are out of scope for Phase 1.

## Architecture

The planned repository separates the Next.js/TypeScript web client (`apps/web`), FastAPI service (`apps/api`), framework-agnostic Python SDK (`packages/python-sdk`), and Dramatiq processing worker (`workers/processing`). PostgreSQL is the durable data store and Redis is intended for broker/cache use. Docker Compose starts only PostgreSQL and Redis at this phase. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/TELEMETRY_CONTRACT.md](docs/TELEMETRY_CONTRACT.md).

## Repository layout

```text
apps/web/                 Next.js frontend
apps/api/                 FastAPI backend
packages/python-sdk/      Independent Python SDK
workers/processing/       Background processing worker
infrastructure/docker/    Container-related configuration
infrastructure/database/  Database-related configuration
examples/                 Basic, research, and failure simulation examples
docs/                     Architecture and engineering documentation
```

## Prerequisites

- Docker Engine or Docker Desktop with the Docker Compose plugin.
- Git.
- Python 3.12+ and [uv](https://docs.astral.sh/uv/) for the API backend.
- Node.js and a package manager compatible with the chosen Next.js setup (needed when the web app is introduced).

The web app, SDK, and worker do not yet have runtime commands or dependencies.

## Start local infrastructure

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

The PostgreSQL and Redis services expose ports 5433 and 6379 by default and store data in named local volumes. Change the port variables in `.env` if those ports are already in use. The example PostgreSQL password is for local development only; use managed secrets and secure credentials outside local development. To stop services while preserving data, run `docker compose down`. To remove the local data volumes too, run `docker compose down -v`.

## Run the API foundation

The existing `.env.example` includes API settings. If you already have a `.env`, merge the API variables from `.env.example` without replacing your local PostgreSQL password. From the repository root:

```powershell
uv sync --project apps/api
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --project apps/api uvicorn app.main:app --app-dir apps/api --reload
```

The API listens on `http://127.0.0.1:8000`. Liveness is at `/api/v1/health`, database readiness at `/api/v1/ready`, and OpenAPI docs at `/docs`. The app does not create or modify domain tables on startup; schema changes are made only by Alembic. The current baseline migration creates no application tables.

Run the API tests with `uv run --project apps/api pytest apps/api/tests`. Tests use isolated SQLite databases and do not modify the normal development database. See [apps/api/README.md](apps/api/README.md) for configuration and migration details.

## Development guidance

Read [AGENTS.md](AGENTS.md) before contributing. Phase boundaries and the recommended Phase 1 work are in [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md). Database documentation describes the proposed initial entities only; no migrations or business logic exist yet.

## Security

Keep `.env` local and never commit real credentials. Telemetry can contain prompts, model output, and other sensitive data; production collection requires explicit redaction, retention, and access-control policies before implementation.
