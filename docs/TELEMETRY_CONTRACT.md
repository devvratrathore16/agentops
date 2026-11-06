# Initial Telemetry Event Contract

This document defines the initial conceptual span event shape for SDK and API design. It is not an implemented SDK, wire protocol, database schema, or validation policy. Field representation and compatibility guarantees must be finalized before ingestion is implemented.

## Span event

| Field | Type / shape | Meaning |
| --- | --- | --- |
| `trace_id` | string identifier | Groups spans from one agent execution. Required. |
| `span_id` | string identifier | Identifies this span within the trace. Required. |
| `parent_span_id` | string identifier or `null` | Parent span; `null` denotes a root span. |
| `span_type` | string enum | Kind of work, initially `agent`, `llm`, `tool`, or `workflow`; extensibility rules TBD. |
| `status` | string enum | Execution outcome: `unset`, `ok`, or `error`. |
| `start_time` | RFC 3339 timestamp | Span start time, timezone required. |
| `end_time` | RFC 3339 timestamp or `null` | Span completion time; nullable for an in-progress event. |
| `duration_ms` | non-negative number or `null` | Duration in milliseconds; derived from timestamps when complete. |
| `model` | object or `null` | Optional model provider, model name, and model version where available. |
| `token_usage` | object or `null` | Optional input, output, and total token counts; counts are non-negative integers when present. |
| `error` | object or `null` | Optional error type, message, and stack/detail fields. Sensitive detail policy TBD. |
| `metadata` | object | User-defined structured attributes; defaults to empty object. Size and value limits TBD. |

## Illustrative JSON

```json
{
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
    "total_tokens": 152
  },
  "error": null,
  "metadata": {}
}
```

## Contract considerations

- Identifiers are opaque strings in this conceptual contract; uniqueness scope and wire encoding remain to be finalized.
- `duration_ms` should agree with start/end timestamps within a defined tolerance. Open spans may have a null end time and duration.
- Token counts may be unavailable; do not infer a count when the provider does not supply one. Define reconciliation rules for inconsistent totals before implementation.
- An error status should carry error information; exact validation and partial-failure semantics remain TBD.
- Metadata and errors may contain secrets, prompts, or personal data. SDK defaults, redaction, size limits, retention, and access policy require explicit design before collection.
- Versioning, batching, delivery semantics, and compatibility policy are not defined in Phase 0.
