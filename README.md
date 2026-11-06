# AgentOps

AgentOps is an SDK-first AI agent observability, evaluation, and reliability platform. It is designed to collect structured execution telemetry through an independent Python SDK, process it through an API and background worker, and make it useful to teams through a web application.

This repository is in **Phase 0: repository initialization**. It establishes the monorepo layout, engineering standards, initial telemetry contract, and local infrastructure. Application behavior is not implemented yet.

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
- Node.js and a package manager compatible with the chosen Next.js setup (needed when the web app is introduced).
- Python 3.11+ (needed when Python components are introduced).

Phase 0 does not install application dependencies or define runtime commands for the web, API, SDK, or worker.

## Start local infrastructure

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

The PostgreSQL and Redis services expose ports 5432 and 6379 by default and store data in named local volumes. Change the port variables in `.env` if those ports are already in use. The example PostgreSQL password is for local development only; use managed secrets and secure credentials outside local development. To stop services while preserving data, run `docker compose down`. To remove the local data volumes too, run `docker compose down -v`.

## Development guidance

Read [AGENTS.md](AGENTS.md) before contributing. Phase boundaries and the recommended Phase 1 work are in [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md). Database documentation describes the proposed initial entities only; no migrations or business logic exist yet.

## Security

Keep `.env` local and never commit real credentials. Telemetry can contain prompts, model output, and other sensitive data; production collection requires explicit redaction, retention, and access-control policies before implementation.
