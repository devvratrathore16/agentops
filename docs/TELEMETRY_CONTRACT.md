# Initial Telemetry Event Contract

This document defines the initial design contract for a span telemetry event. It guides later SDK and API implementation; it is not an implemented SDK, wire protocol, database schema, or validation policy. The authenticated project API key establishes the project scope for ingestion. A payload-supplied project identifier is untrusted and must never select or override that scope.

## Span event

| Field | Type / shape | Meaning |
| --- | --- | --- |
| `schema_version` | string | Version of this event schema, independent of the SDK release. Required. |
| `event_id` | opaque string identifier | Stable identifier for this event and all its delivery retries. Required. |
| `sdk_version` | string | Version of the SDK that created the event. Required when available; otherwise explicitly marked unknown. |
| `sequence_number` | non-negative integer or `null` | Event ordering within a trace where the SDK can guarantee it. It may be absent when ordering cannot be guaranteed. |
| `trace_id` | opaque string identifier | Groups spans from one agent execution. Required. |
| `span_id` | opaque string identifier | Identifies this span within the trace. Required. |
| `parent_span_id` | identifier or `null` | Parent span; `null` denotes a root span. |
| `span_type` | string enum | Kind of work, initially `agent`, `llm`, `tool`, or `workflow`; extension policy TBD. |
| `status` | string enum | Execution outcome: `unset`, `ok`, or `error`. |
| `start_time` | RFC 3339 UTC timestamp | Span start wall-clock time, normalized to UTC with `Z`. Required. |
| `end_time` | RFC 3339 UTC timestamp or `null` | Span completion wall-clock time; null for an incomplete span. |
| `duration_ms` | non-negative number or `null` | SDK elapsed duration measured with a monotonic clock; null if incomplete/unavailable. |
| `model` | object or `null` | Optional provider, model name, and model version where available. |
| `token_usage` | object or `null` | Provider-reported input, output, and total token counts, preserved as reported; see reconciliation below. |
| `error` | object or `null` | Optional error type, message, and stack/detail fields subject to privacy policy below. |
| `metadata` | object | User-defined structured attributes subject to privacy and size policy below. |

No project ID is part of the trusted event identity. If a future wire format carries a project identifier for diagnostics, it must be ignored for authorization and routing.

## Identifier scope and ordering

- `event_id` is unique within a project. Reuse the same value for every retry of the same logical event. A distinct event, including a later update if updates are introduced, receives a distinct event ID unless an explicitly versioned upsert model is adopted.
- `trace_id` is unique within a project. A trace may contain many spans and events.
- `span_id` is unique within its trace. A span can be represented by one or more events only if a future event lifecycle explicitly defines that behavior.
- `parent_span_id`, when present, refers to a span in the same trace.
- Uniqueness is scoped by the project resolved from the authenticated API key, never by a payload project ID.
- `sequence_number` is monotonic within a trace when the SDK can guarantee ordering. It is an ordering hint, not an identity or a substitute for timestamps. Gaps are valid. If process restarts, concurrent producers, or offline queues make monotonicity uncertain, omit it or use a later-defined stream epoch; do not claim ordering the SDK cannot guarantee.
- Identifier character set, generation algorithm, and sequence reset/epoch behavior require finalization before implementation.

## Event delivery semantics

The initial delivery model is **at-least-once delivery attempts**. Networks can fail after the server accepts an event but before the acknowledgement reaches the SDK, so duplicates are expected.

- The SDK assigns and persists (for the lifetime of its retry queue) a stable `event_id` before first transmission. Retries reuse that ID and the same logical event contents.
- Ingestion is idempotent within a project: repeated delivery of an already accepted `event_id` is recognized as a duplicate and must not create a second logical event. The server scopes duplicate detection with the authenticated project identity.
- A batch response must acknowledge outcomes per event (accepted, duplicate/already accepted, retryable failure, or permanent rejection). A single batch-level success flag is insufficient for partial acceptance.
- On a partially accepted batch, the SDK removes accepted and duplicate-acknowledged events from its retry queue. It retains and retries only events explicitly marked retryable or whose outcome is unknown because the request/response failed. It must not resend acknowledged events as new events or silently discard rejected ones.
- Permanent per-event rejections are surfaced to the caller through the SDK's error/reporting mechanism and are not retried automatically. The SDK retains or exposes the rejected payload/error according to the configured privacy-safe queue policy so the caller can remediate or discard it deliberately.
- Retry transient transport and server failures with bounded exponential backoff and jitter, honoring server retry guidance where provided. Enforce a configurable retry limit/age and queue capacity; when exhausted, surface data loss risk rather than silently dropping events.
- Duplicate detection retention must cover the supported retry horizon. The exact idempotency retention window, queue persistence guarantees, response shape, and retry limits are unresolved implementation decisions.

## Time and duration semantics

- `start_time` and `end_time` are UTC wall-clock timestamps encoded as RFC 3339 with `Z`. The SDK records wall-clock instants for cross-system context.
- SDK `duration_ms` is measured using a monotonic clock, not by subtracting wall-clock timestamps. It is elapsed time and is not affected by wall-clock adjustments during the span.
- The backend validates timestamp syntax, timezone normalization, `end_time >= start_time`, and plausible bounds/future skew under a documented tolerance. It must not silently rewrite event timestamps. Invalid or suspicious values should be rejected or flagged according to a versioned validation policy.
- For complete spans, compare wall-clock delta (`end_time - start_time`) with monotonic `duration_ms`. Preserve both values and flag material discrepancies; do not silently replace one with the other. Define tolerance for clock resolution, transport precision, and clock skew before implementation.
- Incomplete spans have `end_time: null` and `duration_ms: null` until a completion event/lifecycle is explicitly defined. Do not infer an end time from ingestion time.
- Parent and child spans may come from different clocks. Their wall-clock intervals can exhibit clock skew; do not reject an otherwise valid trace solely because a child timestamp slightly precedes its parent. Validate and report skew against a policy rather than silently shifting timestamps.

## Token usage reconciliation

- Preserve provider-reported input, output, and total counts as separate reported values with their provenance. Never overwrite an inconsistent reported total with a locally calculated value.
- When input and output counts are available, calculate a separate derived total (`input + output`) for normalized analytics. If the provider also reported a total and it differs, retain both, flag a reconciliation discrepancy, and expose the discrepancy for diagnostics.
- Analytics that specifically represent provider billing/usage use the provider-reported values. Cross-provider normalized analytics may use the derived total only when both components are present, clearly labeling it as derived. Never treat an inferred value as provider-reported.
- Missing values stay missing; do not infer provider counts. Define provider-specific semantics (cached tokens, reasoning tokens, rounding, and included subcounts) before aggregating those fields.

## Privacy and payload policy (recommended initial defaults)

These are conservative starting recommendations to confirm against the approved product and compliance requirements before implementing collection:

- **Input/output capture:** Disabled by default. Require explicit opt-in for full prompts, tool inputs, model outputs, and tool outputs. Prefer sizes, token counts, model identifiers, and caller-supplied summaries when full content is unnecessary.
- **Metadata:** Capture only explicitly supplied structured metadata; document an allowlist approach and prohibit credentials, secrets, and unnecessary personal data. Apply size/depth limits and do not collect environment variables or request headers wholesale.
- **Errors and stack traces:** Record error type and a bounded, sanitized message by default. Full stack traces and exception locals are opt-in; strip secrets, prompt content, and personal data before capture.
- **SDK redaction:** Provide configurable redaction before events enter serialization, logging, or retry queues. Redact common credential patterns by default where feasible, allow caller-defined rules, and never claim pattern redaction guarantees removal of all sensitive data.
- **API credentials:** API keys are transport credentials only. Never include them in event fields, metadata, error messages, SDK logs, or persisted retry payloads. Redact authorization headers from diagnostics.
- **Maximum size:** Recommend a 256 KiB uncompressed serialized event limit and a 1 MiB uncompressed batch limit. Reject oversized events with a clear per-event permanent error; do not silently truncate telemetry. Revisit limits based on product requirements and transport constraints.
- **Maximum batch:** Recommend at most 100 events per request, also subject to the 1 MiB uncompressed batch limit. The first limit reached applies.
- **Retention:** Recommend a 30-day default retention period for raw telemetry, configurable only within product/legal policy. Define deletion propagation, backups, and any derived-data retention before implementation.
- **Sensitive data:** Treat all prompts, outputs, metadata, errors, and stack traces as potentially sensitive. Document customer responsibility and platform safeguards; establish access controls, encryption, deletion, and compliance review before production ingestion.

## Illustrative JSON

```json
{
  "schema_version": "1",
  "event_id": "ev_01JEXAMPLEEVENT",
  "sdk_version": "0.1.0",
  "sequence_number": 2,
  "trace_id": "tr_01JEXAMPLETRACE",
  "span_id": "sp_01JEXAMPLESPAN",
  "parent_span_id": null,
  "span_type": "llm",
  "status": "ok",
  "start_time": "2026-01-15T10:30:00.000Z",
  "end_time": "2026-01-15T10:30:01.250Z",
  "duration_ms": 1250,
  "model": {
    "provider": "provider-name",
    "name": "model-name",
    "version": null
  },
  "token_usage": {
    "input_tokens": 120,
    "output_tokens": 32,
    "reported_total_tokens": 151
  },
  "error": null,
  "metadata": {}
}
```

In this example, analytics may expose a derived total of 152 alongside the provider-reported total of 151 and flag the discrepancy. The authenticated API key—not a payload field—determines the project scope.

## Remaining decisions before implementation

Finalize identifier format and event lifecycle, schema compatibility policy, sequence ordering across restarts/concurrency, ACK wire format, idempotency retention, retry queue persistence and limits, timestamp/skew tolerances, provider-specific token accounting, redaction guarantees, and retention/deletion requirements. Phase 1 must not be treated as approval to implement telemetry ingestion unless it is included in the approved phase scope.
