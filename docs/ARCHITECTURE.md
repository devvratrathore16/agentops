# Architecture

## Phase 0 intent

AgentOps is an SDK-first AI agent observability, evaluation, and reliability platform. The planned architecture keeps instrumentation independent from the hosted control plane and separates the web client, API, and asynchronous processing concerns. This document records boundaries, not an implemented runtime design.

## Components and responsibilities

| Component | Planned responsibility | Boundary |
| --- | --- | --- |
| `packages/python-sdk` | Framework-agnostic public Python client and telemetry contract | Independently installable; no dependency on API internals |
| `apps/api` | FastAPI HTTP interface, authentication, validation, and orchestration | Owns external API boundary; resolves project scope from authenticated credentials and persists through PostgreSQL when implemented |
| `workers/processing` | Dramatiq tasks for asynchronous work | Separate process; Redis broker planned; no direct web coupling |
| `apps/web` | Next.js and TypeScript user interface | Calls documented API contracts |
| PostgreSQL | Durable project, trace, and span data | Accessed by backend components through controlled persistence interfaces |
| Redis | Message broker and optionally ephemeral coordination/cache | Not the durable source of truth |

The API and worker are components of one backend system, not separately designed microservices. Their deployment or scaling can remain independent where operationally useful.

## Data flow (planned)

The planned Phase 1 backend establishes authentication and sessions, organizations and memberships, projects, project API keys, SQLAlchemy models, Alembic migrations, and tenant-isolation tests. Phase 2 provides the independent SDK; Phase 3 adds ingestion and observability. The authenticated project API key determines project scope; any project identifier supplied in an untrusted telemetry payload is ignored for authorization and routing. The API validates and stores accepted events, and asynchronous processing may be dispatched through Redis to the Dramatiq worker when that capability is in scope. The web client reads through documented API contracts when its implementation phase arrives. Delivery, API, and processing behavior are specified only to the degree described in `TELEMETRY_CONTRACT.md`; no ingestion behavior is implemented in Phases 0 or 0.1.

## Technology choices

- Next.js, TypeScript, and Tailwind CSS for the web client.
- Python, FastAPI, Pydantic, SQLAlchemy, and Alembic for the API and persistence layer.
- A standalone Python package for framework-agnostic instrumentation.
- Dramatiq for asynchronous processing, with Redis as broker.
- PostgreSQL for durable relational data.
- Docker Compose for local PostgreSQL and Redis only during Phase 0.

## Phase 0 boundaries

No application services, dependencies, migrations, API endpoints, instrumentation hooks, evaluations, or dashboard features are implemented in Phases 0 or 0.1. Phase 1 is scoped to the backend foundation and tenant boundary in `DEVELOPMENT_ROADMAP.md`. Decisions about deployment topology, detailed authentication/session mechanisms, telemetry batching/retries, retention, and scaling remain subject to the approved product specification and later-phase gates.
