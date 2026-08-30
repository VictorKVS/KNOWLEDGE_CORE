# FATHER Knowledge Factory — API / Trace / Microservice Policy

Document ID: `FATHER-KF-ARCH-POLICY-0001`
Status: `MANDATORY_ARCHITECTURE_RULE`
Owner: `FATHER Architect`
Applies to: all runtime modules, services, workers and role-facing interfaces.

## 1. Core rule

FATHER Knowledge Factory is `API-first` and `trace-first`.

Every material operation must be callable through a documented contract and must emit trace data sufficient to reconstruct what happened, to which entity, by which worker/model, with which input revision, and with what result or error.

No hidden cross-module side effects are allowed for material state changes.

## 2. API everywhere — what this means

Each material capability has an explicit interface. The interface can be:

- HTTP/REST OpenAPI for inter-service and UI/backend integration;
- internal typed Python protocol/interface for in-process modules;
- event contract for asynchronous processing;
- CLI contract for local batch/bootstrap jobs;
- SQL/view contract only for read-only reporting where direct DB access is explicitly approved.

A module is not forced to become a network microservice merely because it has an API contract.

Mandatory API domains:

- source ingestion;
- document classification;
- native extraction/OCR;
- structure/chunk generation;
- translation;
- evidence construction;
- knowledge candidate creation;
- graph node/edge operations;
- contradiction registration;
- score calculation;
- review lifecycle;
- KB_READY promotion;
- role projections;
- recommendation/research query;
- report/export;
- trace retrieval;
- health/readiness/metrics.

## 3. Mandatory request context

Every state-changing or material analytical API call must propagate:

- `request_id`;
- `trace_id`;
- `span_id`;
- `parent_span_id` when applicable;
- `run_id` for pipeline runs;
- `actor_id` or worker identity where applicable;
- `schema_version` / `contract_version`;
- entity IDs (`DOC`, `FRG`, `TRN`, `KN`, `EDGE`, `EVD`, `REV`, `SCORE`, `VIEW`) when already known.

For HTTP, `trace_id`/request context may be transported in headers and repeated in the response envelope for audit convenience.

## 4. Mandatory response envelope

Material APIs return enough metadata for debugging:

- operation status;
- entity IDs created/updated/read;
- `trace_id`;
- warnings;
- deterministic validation result;
- error code/type for failures;
- safe model/profile/version metadata if AI was used.

Full copyrighted source payloads, secrets and credentials must not be copied into generic trace logs.

## 5. Trace everywhere

Every material stage emits at least:

- START;
- terminal `SUCCESS`, `FAILURE`, `BLOCKED`, `SKIPPED` or equivalent;
- elapsed time;
- stage name;
- service/module/worker identity;
- entity links;
- exact machine-readable error code/type/message when failed;
- safe input/output fingerprints (SHA/IDs/versions), not unnecessary full payloads.

The end-to-end trace must cross process/service boundaries without changing `trace_id`.

## 6. Trace traversal acceptance

The system must support both directions:

`product/output -> knowledge -> evidence -> fragment -> document -> source SHA -> original`

and

`entity -> creating/updating span -> parent spans -> run -> worker/service/model -> result/error`.

If traversal is broken, the affected result cannot be considered production-ready.

## 7. Microservice decision rule

Default for M1: modular local architecture / modular monolith plus isolated workers where useful.

A separate microservice is introduced only when at least one strong driver exists:

1. independent scaling requirement;
2. independent failure isolation requirement;
3. separate trust/security boundary;
4. materially different runtime dependency stack;
5. GPU/CPU workload isolation;
6. independent deployment/release cadence;
7. external integration boundary;
8. data residency or legal boundary;
9. measured contention proving in-process separation is insufficient.

`Because microservices are fashionable` is not an architectural reason.

## 8. Candidate microservices

Likely candidates when the project grows:

- `Document Ingest Service` — untrusted file boundary, parsers, validation;
- `OCR Service` — heavy native dependencies / CPU-GPU OCR scaling;
- `Translation Service` — GPU inference, model routing, glossary/reviewer chain;
- `AI / Evidence Service` — RAG, evidence retrieval, recommendations;
- `Review / Promotion Service` — privileged KB_READY trust boundary;
- `Graph Service` — if graph load/API lifecycle outgrows canonical DB access layer;
- `Trace / Audit Service` — if centralized multi-process collection becomes necessary;
- `Report / Export Service` — if expensive rendering/export becomes asynchronous.

M1 may implement these as modules behind stable APIs first, then split without changing external contracts.

## 9. API versioning

- External/network contracts use explicit versioning (`/v1/...` or contract version field).
- Breaking changes require new major contract version or approved migration plan.
- JSON schemas and OpenAPI are version-controlled artifacts.
- Producers and consumers have contract tests.
- Entity logical IDs survive service split and export/import.

## 10. Observability endpoints

Every deployable service must expose or produce equivalents of:

- `/health` — process alive;
- `/ready` — dependencies/gates ready;
- `/metrics` — measured runtime counters where applicable;
- trace lookup by `trace_id` through an approved debug/admin interface.

Health is not proof of functional correctness; golden-path tests remain separate.

## 11. Security rules

- API authorization follows least privilege.
- Promotion to `KB_READY` is a privileged operation.
- Original Store write API is append/immutable-by-policy; derived layers cannot overwrite originals.
- Model outputs are untrusted inputs until deterministic/evidence validation.
- Trace data is sanitized for secrets, credentials, personal data and copyrighted full payloads.
- Internal service authentication is introduced when processes cross a trust boundary.

## 12. Development rule

For every new feature, the implementation checklist is:

`REQ -> API/event/interface contract -> trace stages -> data/entity IDs -> implementation -> contract tests -> negative tests -> trace traversal test -> integration gate`.

Code without a defined contract and trace path is incomplete.

## 13. Visual workspace requirement

The development/OSINT-style site must consume the same APIs, not hidden ad-hoc database queries for canonical write operations.

The UI must be able to visualize:

- source list;
- nodes and edges;
- evidence chain;
- contradictions;
- role projections;
- pipeline stages;
- trace timeline;
- products/artifacts derived from knowledge.

Thus visualization itself becomes a consumer of the governed API/trace layer.
