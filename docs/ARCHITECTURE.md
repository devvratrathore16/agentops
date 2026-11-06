# Architecture

## Phase 0 intent

AgentOps is an SDK-first AI agent observability, evaluation, and reliability platform. The planned architecture keeps instrumentation independent from the hosted control plane and separates the web client, API, and asynchronous processing concerns. This document records boundaries, not an implemented runtime design.

## Components and responsibilities

| Component | Planned responsibility | Boundary |
| --- | --- | --- |
| `packages/python-sdk` | Framework-agnostic public Python client and telemetry contract | Independently installable; no dependency on API internals |
| `apps/api` | FastAPI HTTP interface, validation, and orchestration | Owns external API boundary; persists through PostgreSQL when implemented |
| `workers/processing` | Dramatiq tasks for asynchronous work | Separate process; Redis broker planned; no direct web coupling |
| `apps/web` | Next.js and TypeScript user interface | Calls documented API contracts |
| PostgreSQL | Durable project, trace, and span data | Accessed by backend components through controlled persistence interfaces |
| Redis | Message broker and optionally ephemeral coordination/cache | Not the durable source of truth |

The API and worker are components of one backend system, not separately designed microservices. Their deployment or scaling can remain independent where operationally useful.

## Data flow (planned)

An application uses the SDK to construct trace/span events and send them to the API. The API validates the external contract and stores accepted data; asynchronous processing may be dispatched through Redis to the Dramatiq worker. The web client reads data through API endpoints. Authentication, ingestion delivery guarantees, query APIs, and processing semantics are intentionally unspecified in Phase 0.

## Technology choices

- Next.js, TypeScript, and Tailwind CSS for the web client.
- Python, FastAPI, Pydantic, SQLAlchemy, and Alembic for the API and persistence layer.
- A standalone Python package for framework-agnostic instrumentation.
- Dramatiq for asynchronous processing, with Redis as broker.
- PostgreSQL for durable relational data.
- Docker Compose for local PostgreSQL and Redis only during Phase 0.

## Phase 0 boundaries

No application services, dependencies, migrations, API endpoints, instrumentation hooks, evaluations, or dashboard features are implemented. Decisions about deployment topology, tenancy, auth, batching, retries, retention, and scaling belong to later phases and the approved product specification.
