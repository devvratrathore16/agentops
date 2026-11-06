# Database Schema (Initial Proposal)

This document is a conceptual starting point, not an implemented schema. No SQLAlchemy models, Alembic revisions, or business logic are part of Phase 0. Confirm the approved product specification before finalizing fields, constraints, or tenancy rules.

## Candidate entities

| Entity | Purpose | Candidate identifiers/relationships |
| --- | --- | --- |
| Project | Logical scope for agent telemetry | Project ID; parent scope for traces |
| Trace | One agent execution/request | Trace ID; belongs to a project; has many spans |
| Span | A unit of work within a trace | Span ID; trace ID; optional parent span ID |
| Evaluation | Future evaluation result or annotation | Trace/span reference and evaluator/version metadata, subject to product design |

Evaluation is listed only as a future concept; it is not in the Phase 0 telemetry storage contract or schema implementation.

## Initial trace and span considerations

- Trace IDs and span IDs should be opaque, globally unique identifiers at the contract boundary; confirm representation and database types in Phase 1.
- A span may reference a parent span. Parent ordering and root-span rules need explicit validation policy.
- Store start/end timestamps with timezone-aware semantics; define behavior for incomplete spans, clock skew, and late arrival before implementation.
- Duration can be derived from start/end times. If stored for query performance, define precision and consistency rules.
- Model/token fields and arbitrary metadata are contract concerns described in `TELEMETRY_CONTRACT.md`; choose normalized columns versus JSON storage based on query requirements.
- Error detail and metadata may contain sensitive content; establish redaction, access, and retention policies before persistence.

## Open design items

Resolve project ownership/tenancy, uniqueness scope, deletion and retention, indexes, partitioning, event idempotency, evaluation relationships, and migration strategy against the approved product specification in a later phase. Do not treat this proposal as authorization to add schema behavior during Phase 0.
