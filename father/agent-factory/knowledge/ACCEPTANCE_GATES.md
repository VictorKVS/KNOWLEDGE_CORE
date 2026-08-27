# FATHER Knowledge Factory M1 — Acceptance Gates

## MIN — Foundation works

Required:
- schema creates a fresh SQLite DB;
- `PRAGMA foreign_key_check` returns no rows;
- `PRAGMA quick_check` returns `ok`;
- golden fixture creates document -> fragment -> translation -> node -> evidence -> score -> review -> six role views;
- approved fixture is visible through `v_kb_ready_nodes`;
- original/source/translation layers remain separate;
- trace schema is installed (`trace_events`, `entity_trace_links`);
- one `trace_id` is visible for the golden run and every created golden entity is linked to the creating span.

Failure at MIN blocks all bulk processing.

## MED — Factory integration works

Required:
- short EN architecture/security fixture passes local model translator + reviewer;
- translation record is ingested into canonical DB;
- at least one atomic node is produced with evidence link;
- deterministic QA blocks a deliberately unsupported candidate;
- role views are produced for Architect, Programmer, Security, Lawyer, Manager and Product without cloning node identity;
- interruption/resume does not duplicate canonical records;
- JSONL exports contain stable logical IDs and provenance;
- trace correlation survives process/worker boundaries;
- each executed stage emits START + terminal OK/WARN/ERROR/BLOCKED with `elapsed_ms`;
- an injected failure is discoverable by `trace_id`, `span_id`, stage and entity context.

## MAX — Real source works

Required:
- one real technical PDF/book is classified as native-text/scanned/mixed;
- OCR is applied only where required and confidence is recorded;
- EN->RU translation preserves code/numbers/URLs and glossary consistency;
- multiple knowledge nodes and at least one relation are built;
- contradiction fixture is preserved as `CONTRADICTS`, not silently resolved;
- GPT/Chief Analyst evidence package can resolve exact source fragment and translation;
- export/import round-trip reconstructs node IDs, edges, evidence and review history;
- no copyrighted full source or translation is staged to public GitHub;
- trace traversal works in both directions: source -> KB_READY and KB_READY -> original source;
- model calls retain model/profile/input-output hashes and latency without logging credentials/secrets.

## Mandatory traceability gate

Tracing is a hard acceptance gate, not optional debug output. Canonical standard: `TRACEABILITY_AND_DEBUGGING_STANDARD.md`.

Minimum required trace fields: `trace_id`, `span_id`, `parent_span_id`, `run_id`, `stream_id`, `worker_id`, `stage`, `status`, entity identity where available, hashes where available, elapsed time, exact error type/message on failure.

Canonical local trace sink: `G:\1\FATHER_KNOWLEDGE\traces\<trace_id>.jsonl`.

Database traceability uses `trace_events` plus `entity_trace_links`. Retry creates a new span under the same trace. Full copyrighted payloads and secrets are not emitted into public diagnostics.

## Production telemetry gate

Before reporting acceleration versus one stream, record a comparable one-stream baseline. Required fields: run_id, worker_count, items_total, items_processed, accepted, rework, errors, elapsed_seconds, throughput, model/runtime profile. ETA is emitted only when remaining volume and stable measured throughput exist.

## Promotion rule

`KB_READY = evidence present AND approved review AND deterministic integrity checks AND source resolvable AND trace resolvable`.

For legal/regulatory nodes add: verified source identity + exact anchor + currentness status; applicability remains a separate field.
