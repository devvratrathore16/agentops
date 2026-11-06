# AgentOps Engineering Guide

## Project overview

AgentOps is an SDK-first platform for AI agent observability, evaluation, and reliability. This repository is a monorepo with a web application, API, independent Python SDK, background processing worker, infrastructure, examples, and documentation.

## Technology stack

- Web: Next.js, TypeScript, Tailwind CSS.
- API: Python, FastAPI, SQLAlchemy, Alembic, Pydantic.
- SDK: independent, framework-agnostic Python package.
- Processing: Python worker using Dramatiq.
- Local infrastructure: PostgreSQL, Redis, Docker Compose.

Add dependencies only when a phase requires them and document the reason. Keep each component's dependency manifest in its own directory when implementation begins.

## Coding conventions

- Prefer readable, typed code and small, cohesive modules.
- Use TypeScript strict mode and Python type annotations for new code.
- Follow the formatting and linting tools configured by the owning component; do not create competing project-wide rules.
- Keep public interfaces documented and backward-compatibility decisions explicit.
- Avoid unnecessary abstractions, duplicate configuration, and hidden cross-component coupling.

## Testing requirements

- Add focused unit tests for behavior and integration tests at component boundaries as features are introduced.
- Keep tests deterministic; do not rely on external services unless the test explicitly provisions them.
- Run the relevant lint, type-check, and test commands before claiming verification. Report commands and outcomes accurately.
- Phase 0 establishes standards only; it does not add application tests or claim a test suite exists.

## Architecture rules

- Preserve the boundaries between `apps/web`, `apps/api`, `packages/python-sdk`, and `workers/processing`.
- The Python SDK must remain independently installable and must not depend on the API or web application.
- The API owns request validation and service orchestration; workers own asynchronous processing. Use PostgreSQL for durable application data and Redis for broker/cache roles when those features are implemented.
- Keep a modular monolith for the backend. Do not introduce microservices without an approved product and architecture decision.
- Shared contracts belong in versioned/documented interfaces, not implicit imports across deployable components.
- Phase 0 documents intended boundaries; it does not establish runtime behavior or schema migrations.

## Security requirements

- Never commit credentials, tokens, private keys, or populated local environment files. Commit templates with placeholders only.
- Validate and constrain untrusted input at component boundaries. Avoid logging secrets, prompts, or personal data by default.
- Treat telemetry metadata and error content as potentially sensitive; define retention, redaction, and access controls before production collection.
- Use least-privilege credentials and TLS for non-local deployments. Local Compose credentials are development-only.
- Pin and review dependencies through the package manager's lockfile when dependencies are introduced.

## Phase-based development restrictions

- Follow `docs/DEVELOPMENT_ROADMAP.md` and the approved product specification.
- Phase 0 is repository foundation and engineering standards only.
- Do not implement authentication, database business logic, SDK instrumentation, evaluation functionality, or dashboard features during Phase 0.
- Do not pull future-phase behavior forward without explicit approval. Record decisions and stop when Phase 0 deliverables are complete.
