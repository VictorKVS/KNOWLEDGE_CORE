# FATHER Knowledge Factory — Traceability and Debugging Standard

Status: ACTIVE

## Goal

Every material operation in the FATHER Agent/Knowledge Factory must be traceable end-to-end so a failed translation, OCR fragment, knowledge node, edge, score or review can be replayed and debugged without guessing.

Canonical trace chain:

`RUN -> STREAM -> WORKER -> STAGE -> SPAN -> ENTITY -> EVIDENCE -> REVIEW -> KB_READY`

## Mandatory identifiers

Every traceable event must carry when available:

- `trace_id` — one end-to-end execution/correlation ID;
- `span_id` — one operation/stage ID;
- `parent_span_id` — caller operation;
- `run_id` — processing run identity;
- `stream_id` — S1/S2/S3/S4 or translation worker queue;
- `worker_id` — concrete local worker/process/thread;
- `stage` — pipeline stage;
- `entity_type` and `entity_id` — DOC/FRG/TRN/KN/EDGE/EVD/REV/SCORE/VIEW;
- `source_sha256` / `fragment_sha256` where applicable;
- `model` and `prompt_profile` for LLM operations;
- `status` — START/OK/WARN/ERROR/BLOCKED/RETRY;
- `elapsed_ms` for completed operations;
- `error_type`, `error_message`, `error_context` on failure.

## Required stage names

- `INGEST`
- `PDF_CLASSIFY`
- `NATIVE_EXTRACT`
- `OCR`
- `LAYOUT_RECONSTRUCT`
- `LANGUAGE_DETECT`
- `CHUNK`
- `TRANSLATE`
- `TRANSLATION_REVIEW`
- `DETERMINISTIC_QA`
- `KNOWLEDGE_EXTRACT`
- `NODE_UPSERT`
- `EDGE_UPSERT`
- `EVIDENCE_LINK`
- `SCORE`
- `ROLE_VIEW`
- `ANALYST_REVIEW`
- `KB_READY_GATE`
- `EXPORT`
- `ROUND_TRIP_VERIFY`

## Event rules

1. Every stage emits `START` and one terminal event: `OK`, `WARN`, `ERROR` or `BLOCKED`.
2. A terminal event records `elapsed_ms`.
3. Errors preserve exception class and message; do not replace them with generic `failed`.
4. LLM calls record endpoint profile, model, prompt-profile revision, input/output hashes and latency. Full copyrighted text remains local and is not copied into public Git history.
5. Every database entity created from a traced operation must be linkable to the `trace_id` and `span_id` through `entity_trace_links`.
6. Retry creates a new span with the same trace_id and `retry_of_span_id` in attributes.
7. Worker/thread boundaries preserve trace_id.
8. No secret/token/password may be written to trace attributes.
9. Source absolute paths may exist only in local trace output; public diagnostics must redact them.
10. Trace JSONL is append-only per run.

## Local runtime

Default trace root:

`G:\1\FATHER_KNOWLEDGE\traces\`

File naming:

`<trace_id>.jsonl`

Optional human-readable console output is allowed, but JSONL is canonical for debugging and regression analysis.

## Debugging contract

From any `knowledge_node` we must be able to traverse:

`node_id -> entity_trace_links -> trace/span -> evidence_link -> fragment -> document SHA -> original source`

From any translation:

`translation_id -> trace -> translator/reviewer model -> source fragment -> QA -> downstream node(s)`

From any failure:

`trace_id + span_id -> stage -> worker -> error -> input entity -> retry/recovery history`

## Acceptance

A golden-path run is not accepted unless:

- one trace_id spans all executed stages;
- child spans have valid parent_span_id values;
- every created DOC/FRG/TRN/KN/EVD/REV/SCORE/VIEW entity has a trace link;
- one injected failure is visible as ERROR/BLOCKED with exact stage and entity context;
- JSONL can be parsed deterministically;
- source files remain untouched.
