# Database Schema (Initial Proposal)

This document records conceptual entities and constraints to guide later design. No SQLAlchemy models, Alembic revisions, or business logic are part of Phases 0 or 0.1. Phase 1 will implement and test the approved backend foundation described in `DEVELOPMENT_ROADMAP.md`; confirm detailed relationships against the approved product specification before finalizing migrations.

## Phase 1 foundation entities

| Entity | Purpose | Candidate identifiers/relationships |
| --- | --- | --- |
| Organization | Tenant boundary and shared ownership scope | Organization ID; owns or scopes memberships and projects |
| Membership | Associates a user/principal with an organization and its role | Membership ID; references organization and authenticated principal; role policy TBD |
| Session | Represents an authenticated session | Session ID and principal/reference; storage and lifecycle depend on the chosen authentication design |
| Project | Logical scope for settings and telemetry | Project ID; belongs to an organization |
| Project API key | Authenticates SDK/API access for a project | Key ID and project reference; persist only a non-recoverable verifier/hash, never the plaintext key |

These names describe domain concepts, not a final relational design. Session representation, membership roles, organization/project deletion behavior, and key rotation/revocation policy require approval before migrations.

## Future telemetry entities

| Entity | Purpose | Candidate identifiers/relationships |
| --- | --- | --- |
| Trace | One agent execution/request | Trace ID; unique within the authenticated project scope; belongs to a project |
| Span | A unit of work within a trace | Span ID; unique within its trace; references trace and optional parent span |
| Telemetry event | A delivered versioned event for a span | Event ID; unique within the authenticated project scope; includes schema version and optional sequence number |
| Evaluation | Future evaluation result or annotation | Trace/span reference and evaluator/version metadata, subject to the approved phase scope |

Telemetry ingestion and persistence are planned for Phase 3; evaluation records are planned for Phase 4. Listing these concepts does not move them into Phase 1.

## Tenant isolation and integrity considerations

- Tenant context must come from the authenticated user/session or validated project API key, not an untrusted payload field.
- Organization and membership access must constrain project operations. Project API keys must be bound to one project and cannot select another project by payload value.
- Enforce tenant-aware lookups and authorization consistently in service/query boundaries; add database tests proving cross-organization and cross-project access is denied.
- Telemetry uniqueness should be scoped as documented in `TELEMETRY_CONTRACT.md`: event ID within project, trace ID within project, span ID within trace. Determine database constraints/indexes that preserve those scopes.

## Timestamp, payload, and storage considerations

- Store timestamps with timezone-aware semantics. Telemetry wall-clock values are UTC RFC 3339; elapsed duration is measured separately with a monotonic clock by the SDK.
- Duration may be derived from start/end timestamps for one view, but preserve the SDK's monotonic elapsed duration as a separate reported value and flag material discrepancy.
- Preserve provider-reported token values separately from normalized/derived analytics values. Do not overwrite inconsistent reported totals.
- Model/token fields and arbitrary metadata are contract concerns described in `TELEMETRY_CONTRACT.md`; choose normalized columns versus JSON based on approved query requirements.
- Error detail and metadata may contain sensitive content; apply redaction, access, retention, and deletion policies before persistence.

## Open design items

Resolve authentication/session model, organization membership semantics, API key verifier and rotation lifecycle, tenant-aware constraints, deletion/retention, event idempotency window, indexes/partitioning, telemetry storage phase, and migration strategy against the approved specification. Do not treat this proposal as authorization to implement telemetry schema or business behavior ahead of its phase.
