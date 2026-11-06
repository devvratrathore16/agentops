# Development Roadmap

The approved product specification remains authoritative. This roadmap records phase boundaries for repository work and does not add product scope.

## Phase 0 — Repository initialization (current)

- Establish monorepo directories, repository guidance, documentation, environment template, and local PostgreSQL/Redis Compose services.
- Define a conceptual initial telemetry event contract.
- Do not implement authentication, database business logic, SDK instrumentation, evaluation, dashboards, or application dependencies.

## Phase 1 — Foundation design and minimal component skeletons

Recommended next steps, subject to the approved specification:

1. Confirm open decisions from the architecture, database, and telemetry documents, especially tenancy, privacy/redaction, identity formats, ingestion semantics, and retention.
2. Agree package managers, supported language/runtime versions, formatting/lint/type-check tools, and CI expectations.
3. Add minimal independently configured web, API, SDK, and worker package skeletons with health/startup checks only where specified.
4. Define and review versioned API/SDK contracts and the first migration plan before implementing persistence behavior.
5. Add focused tests and CI checks alongside each skeleton.

Phase 1 should still avoid unapproved future product capabilities. Later phases should be planned from the product specification rather than inferred from this repository scaffold.
