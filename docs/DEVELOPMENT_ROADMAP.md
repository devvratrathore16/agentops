# AgentOps Development Roadmap

This roadmap follows the approved phase sequence. The approved AgentOps product specification remains authoritative: objectives and completion criteria below describe phase boundaries and do not authorize functionality beyond that specification. Preserve the monorepo boundaries and security rules in `AGENTS.md` and `ARCHITECTURE.md` throughout implementation. Do not introduce microservices, distributed databases, Kubernetes, or other infrastructure without an approved architecture decision.

## Phase 0 — Repository Initialization (complete)

### Objectives

- Establish the repository layout and engineering standards for AgentOps.
- Provide a minimal local infrastructure foundation for PostgreSQL and Redis.

### Deliverables

- Monorepo directories for web, API, Python SDK, processing worker, infrastructure, examples, and docs.
- `AGENTS.md`, README, architecture/database/telemetry docs, environment template, secret-safe `.gitignore`, and Docker Compose configuration with health checks and persistent volumes.

### Completion criteria

- Required repository paths and foundation documents exist and agree on component boundaries.
- Compose configuration is reviewable and local secrets are excluded from version control.
- No application behavior or future-phase feature is implemented.

## Phase 0.1 — Architecture Refinement (complete)

### Objectives

- Refine the initial telemetry contract and clarify project and tenant boundaries before implementation.
- Record delivery, time, token reconciliation, and privacy decisions at the design level.

### Deliverables

- Telemetry event identity/version fields and identifier scope rules.
- At-least-once delivery, stable IDs, idempotency, batch acknowledgement, duplicate, retry, and partial acceptance semantics.
- UTC timestamp and monotonic duration semantics, token reconciliation policy, and recommended privacy/payload limits.
- Aligned architecture and conceptual database documentation.

### Completion criteria

- Telemetry fields and rules are documented consistently with planned authenticated project scope.
- Remaining wire-format and operational decisions are identified for resolution before implementation.
- No SDK instrumentation, ingestion endpoint, migration, or other application functionality is implemented.

## Phase 1 — Backend Foundation (not started)

### Objectives

- Establish the API/backend project and foundational identity, organization, project, and tenant model.
- Provide secure authentication and project-scoped API key access.

### Deliverables

- Backend project setup using the agreed Python/FastAPI toolchain and component-local configuration/dependencies.
- Authentication and session management.
- Organizations and memberships.
- Project management within the organization/tenant model.
- Project API key generation and validation, with scope resolved from the authenticated key.
- SQLAlchemy models and Alembic migrations for approved Phase 1 entities.
- Database tests for persistence, migrations, authentication/key behavior, and tenant isolation.

### Completion criteria

- The approved backend foundation can be initialized and its migrations applied reproducibly to a clean database.
- Database tests demonstrate organization/project access boundaries and deny cross-tenant access.
- API keys are validated for their assigned project and secrets are not stored or logged in recoverable plaintext.
- No SDK instrumentation, telemetry ingestion, evaluation, experiment tracking, failure analysis, or dashboard capability is pulled into Phase 1 unless the approved product specification explicitly assigns it here.

Introduce package skeletons only when required by their implementation phase. Phase 1 does not require placeholder web, SDK, or worker packages solely to fill directories.

## Phase 2 — Python SDK (not started)

### Objectives

- Deliver an independently installable, framework-agnostic Python SDK for AgentOps integration.
- Implement the SDK-side instrumentation and delivery behavior assigned to the SDK by the approved telemetry contract.

### Deliverables

- SDK package metadata, public interfaces, supported Python versions, and installation guidance.
- Framework-agnostic trace/span event creation and context propagation appropriate to the approved SDK scope.
- Event serialization and transport configuration consistent with the versioned telemetry contract.
- SDK handling for stable event IDs, batching, partial acknowledgements, and bounded retries as specified by the contract.
- Unit tests, transport tests, and basic examples for supported SDK usage.

### Completion criteria

- The SDK installs independently and does not depend on API, web, or worker internals.
- Public SDK behavior conforms to the telemetry contract, including opt-in content capture and redaction settings.
- Tests cover event construction, serialization, retry identity, and accepted/rejected batch outcomes.

## Phase 3 — Ingestion and Observability (not started)

### Objectives

- Receive telemetry through the authenticated API and persist it under the project scope established in Phase 1.
- Make accepted trace and span data available through the observability surfaces approved for this phase.

### Deliverables

- Validated ingestion and batch acknowledgement behavior conforming to `TELEMETRY_CONTRACT.md`.
- Project-scoped idempotency and duplicate handling, partial acceptance, and controlled retry-compatible responses.
- Durable telemetry persistence and the required trace/span retrieval or observability views defined by the product specification.
- Component-boundary and database tests for authorization scope, validation, duplicates, and partial batches.

### Completion criteria

- Ingestion derives project scope from the validated project API key and ignores payload-supplied project identifiers for authorization.
- Repeated accepted event IDs do not create duplicate logical events; batch outcomes are explicit per event.
- Persisted and returned telemetry preserves reported timestamps, duration, token values, and privacy settings according to the contract.
- Tests show one project's credentials cannot ingest or read another project's telemetry.

## Phase 4 — Evaluation Engine (not started)

### Objectives

- Add the evaluation capabilities defined in the approved product specification using eligible AgentOps data and inputs.

### Deliverables

- Evaluation interfaces, execution flow, and result representation defined by the product requirements.
- Required persistence and API integration, isolated behind the existing application boundaries.
- Focused evaluator, persistence, and API tests, including representative success and failure cases.

### Completion criteria

- Approved evaluation workflows produce traceable results linked to the appropriate project and source data.
- Invalid inputs and evaluator failures are handled and reported according to the agreed contract.
- Evaluation behavior is tested without introducing unapproved provider integrations or coupling the SDK to API internals.

## Phase 5 — Experiment Tracking (not started)

### Objectives

- Support the experiment tracking workflows and comparison needs included in the approved specification.

### Deliverables

- Approved experiment/run identity and relationships to relevant projects, traces, configurations, and evaluation results.
- The persistence, API, and user-facing surfaces required by the product specification.
- Tests for experiment creation, association, retrieval, and comparison semantics that are in scope.

### Completion criteria

- Experiment data is scoped to the correct tenant/project and can be reliably associated with its source executions and results.
- Any comparison behavior is deterministic, documented, and covered by tests.
- No experiment workflow outside the approved product scope is introduced.

## Phase 6 — AI Failure Analysis (not started)

### Objectives

- Deliver the AI failure analysis capabilities explicitly defined by the approved product specification.

### Deliverables

- Failure-analysis inputs, outputs, and processing flow based on approved telemetry/evaluation data.
- Required API, worker, persistence, and user-facing integration within the existing architecture.
- Tests for representative failure cases, analysis errors, tenant boundaries, and sensitive-data handling.

### Completion criteria

- Analysis results are traceable to their source data and scoped to the authorized tenant/project.
- Analysis errors and uncertainty are represented according to approved product behavior rather than hidden or presented as fact.
- Sensitive telemetry follows the established capture, redaction, access, and retention policies.

## Phase 7 — Testing, Optimization and Deployment (not started)

### Objectives

- Validate end-to-end quality, reliability, security, and performance for the approved product scope.
- Prepare the system for its approved deployment target without expanding the infrastructure architecture unnecessarily.

### Deliverables

- End-to-end and regression coverage across SDK, API, worker, persistence, and web flows that have been implemented.
- Performance and reliability measurements against approved workload targets, with documented improvements where needed.
- Security review and remediation for authentication, tenant isolation, API keys, telemetry privacy, and secrets handling.
- Deployment and operations documentation, environment configuration, health/monitoring expectations, backup and recovery guidance as required by the target environment.
- Release checklist and known limitations.

### Completion criteria

- Required test, security, reliability, and performance gates for the approved release target pass and their results are recorded.
- Deployment can be repeated from documented configuration without committing secrets.
- Operational and recovery procedures are reviewed for the selected deployment target.
- No Kubernetes, microservices, or additional infrastructure is introduced unless separately approved.

## Phase gates and change control

- Complete phases in order unless the approved product specification explicitly documents a dependency exception.
- Resolve open design decisions in `ARCHITECTURE.md`, `DATABASE_SCHEMA.md`, and `TELEMETRY_CONTRACT.md` before implementing the behavior they govern.
- Add tests alongside behavior and run the relevant checks before declaring a phase complete.
- Keep `AGENTS.md` and the approved product specification authoritative for coding, security, architecture, and phase restrictions.
- This roadmap does not authorize starting Phase 1 or any later phase; each phase begins only when explicitly approved.
