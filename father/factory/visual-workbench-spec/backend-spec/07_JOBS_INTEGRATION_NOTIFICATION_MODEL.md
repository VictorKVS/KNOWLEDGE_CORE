# Backend Jobs, Integration & Notification Model

Status: `DRAFT_V0.1`

## 1. Purpose

Define when work is synchronous vs asynchronous, how retries/idempotency work, and how external systems interact without corrupting canonical engineering state.

## 2. Default rule

Use synchronous in-process/domain calls for short, deterministic operations. Use background jobs only when work is long-running, retryable, externally dependent, or should not hold request/DB transaction open.

## 3. Synchronous examples

- validate object schema;
- create draft revision;
- create relation;
- authority check;
- evaluate deterministic gate rules;
- bounded trace query;
- compare small baselines;
- confirm artifact.

## 4. Async examples

- parse uploaded documents;
- build source previews;
- large import/export;
- rebuild search projection;
- send notifications/webhooks;
- CI/test result ingestion;
- future semantic mapping/evaluation;
- future model zoo panel execution.

## 5. Job record

Required fields:
- job ID;
- job type/version;
- project;
- input snapshot refs;
- idempotency key;
- created by;
- priority;
- status;
- attempt count;
- max attempts;
- next attempt at;
- lease/claim metadata;
- correlation ID;
- result refs;
- error class/message;
- created/started/finished timestamps.

## 6. Job execution semantics

Baseline may use DB-backed jobs.

Worker algorithm:
1. claim eligible job atomically;
2. mark lease expiration;
3. execute outside canonical transaction;
4. persist result as candidate/derived data through application command;
5. mark succeeded;
6. retry transient failure with bounded backoff;
7. move repeated/permanent failure to DEAD_LETTER/review.

## 7. Idempotency

Every externally retryable job defines an idempotency strategy.

Examples:
- parse source version: key = source_version + parser_version;
- export baseline: key = baseline + export_profile + generator_version;
- webhook: event ID + destination;
- CI result import: external run ID + provider.

## 8. Outbox

Canonical transaction writes outbox record in same DB transaction.

Outbox publisher/worker later performs:
- projection refresh;
- notification;
- external webhook;
- async job creation.

This prevents “canonical commit succeeded but event was lost”.

## 9. No exactly-once fantasy

External integrations are designed for at-least-once delivery plus idempotent handling unless a specific provider offers stronger semantics and it is verified.

## 10. Integration adapter contract

Each adapter defines:
- provider/system ID;
- authentication method/reference;
- allowed projects/data classes;
- supported commands/reads;
- rate limits;
- pagination/checkpoint model;
- idempotency/dedup strategy;
- retry policy;
- provenance mapping;
- error taxonomy;
- health status.

## 11. Git repository adapter

Candidate capabilities:
- read repository metadata;
- read file at exact commit;
- map commit/file/line locators;
- ingest pull request/CI evidence where authorized;
- export generated canonical artifacts only via explicit workflow.

No connector may silently push/merge code.

## 12. CI/test adapter

Ingest:
- pipeline/run identity;
- commit/build baseline;
- test suite/case/result;
- artifacts/reports;
- security scan results;
- timestamps/tool versions.

Mapping to canonical TEST_RESULT remains explicit.

## 13. Issue tracker adapter

Possible mapping:
- ChangeRequest ↔ ticket;
- Defect ↔ ticket;
- ReviewFinding ↔ ticket.

External ticket status does not automatically overwrite canonical engineering state without mapping policy.

## 14. Notification channels

Notifications are derived side effects, not canonical decisions.

Events may include:
- review assigned;
- blocker introduced;
- gate waiting;
- evidence stale;
- baseline promoted;
- risk acceptance expiring;
- job dead-letter;
- import conflict.

User preferences may reduce noise but cannot suppress mandatory governance/security alerts for required roles.

## 15. Notification dedup

Use notification event key + recipient/channel window to prevent storms.

## 16. Webhooks

Outbound webhook payload includes:
- event ID;
- event type/version;
- project;
- canonical refs;
- timestamp;
- correlation ID;
- optional signature.

Do not include restricted source content by default.

## 17. Integration failure handling

Integration failure states remain visible:
- TRANSIENT;
- AUTH_REQUIRED;
- RATE_LIMITED;
- DATA_POLICY_BLOCKED;
- PERMANENT_MAPPING_ERROR;
- PROVIDER_UNAVAILABLE;
- DEAD_LETTER.

Canonical state must not pretend external side effect succeeded when it did not.

## 18. Backpressure

Before broker introduction, use:
- bounded job queue;
- per-job-type concurrency;
- provider-specific rate limits;
- priority classes;
- admission control for very large imports.

## 19. Broker adoption trigger

Consider broker only when measured needs include one or more:
- DB job polling bottleneck;
- durable fanout across independent services;
- high sustained event throughput;
- replay requirements exceeding DB/outbox ergonomics;
- independent worker scaling;
- cross-service decoupling after justified service split.

Requires benchmark and ADR.

## 20. Future AI jobs

Model/agent jobs must additionally store:
- model/provider/version;
- prompt/instruction version;
- frozen input refs;
- tool permissions;
- output refs;
- token/compute/cost telemetry;
- policy decision;
- human review result.

No AI job completion equals approval.
