# Backend Observability, Backup & Recovery

Status: `DRAFT_V0.1`

## 1. Purpose

The Workbench must be observable and recoverable as an engineering system. Loss or silent corruption of requirements, decisions, evidence or approvals is a material system failure.

## 2. Observability layers

### Application
- request rate/latency/errors;
- command rate/latency/errors;
- query latency;
- graph traversal depth/result size;
- import/export durations;
- review/gate queue age.

### Database
- connection pool;
- transaction latency;
- lock waits/deadlocks;
- slow queries;
- table/index growth;
- replication/backup status when applicable.

### Jobs
- queued/running/retry/dead-letter counts;
- queue age;
- attempts;
- execution duration;
- worker health.

### Storage
- object store availability;
- source byte integrity check failures;
- capacity;
- upload/quarantine failures.

### Governance health
- stale evidence count;
- unresolved conflict count;
- gates blocked by missing authority;
- expiring risk acceptances;
- baseline age;
- audit continuity check status.

## 3. Structured logs

Every request/job log should carry where available:
- timestamp;
- level;
- service/module;
- request/correlation ID;
- project ID;
- actor/service identity;
- command/query/job type;
- target refs;
- outcome/error code;
- duration.

Do not log source contents or sensitive payloads by default.

## 4. Correlation model

One correlation ID follows:
HTTP command → canonical transaction → audit event → outbox → job → external integration result.

This lets operator reconstruct a change without scraping unrelated logs.

## 5. Metrics baseline

Candidate metrics:
- API p50/p95/p99 latency by route category;
- 4xx/5xx rate;
- command conflict rate;
- DB transaction errors;
- graph traversal timeout count;
- search latency;
- job backlog age;
- dead-letter count;
- notification failure;
- source hash integrity failures;
- audit write failure;
- backup age;
- last successful restore test age.

Thresholds remain TO_BE_BASELINED from test/operation evidence.

## 6. Tracing

Distributed tracing is not mandatory for one-process modular monolith, but internal spans/correlation instrumentation should be designed so OpenTelemetry can be added without changing domain semantics.

Trace candidates:
- request;
- application command;
- DB transaction;
- trace/impact query;
- object store call;
- integration adapter call;
- job execution.

## 7. Health endpoints

Separate:
- liveness;
- readiness;
- dependency health;
- degraded feature status.

Readiness may fail if DB unavailable; optional notification connector outage should not necessarily mark entire application unready.

## 8. Backup strategy

Backup has at least:
- PostgreSQL data;
- object/file storage;
- schema migrations;
- application configuration references;
- audit state;
- exportable registry/config definitions.

Backup encryption/access follows classification policy.

## 9. Recovery objectives

RPO/RTO are project/production NFRs and must not be invented at design stage.

Architecture must support defining and testing them later.

## 10. Consistent restore

Database and object store restore must reconcile exact source-version/storage keys.

Restore procedure validates:
1. DB starts at expected schema;
2. object manifests resolve;
3. source hashes match;
4. baseline membership resolves;
5. relation endpoints resolve;
6. audit records are readable;
7. representative trace queries pass;
8. privileged authority records restore correctly.

## 11. Restore test

Backup is not accepted merely because backup job succeeded.
Periodic restore test records:
- backup ID/time;
- restore environment;
- duration;
- verification checks;
- defects;
- operator/reviewer;
- outcome.

## 12. Disaster/failure scenarios

Paper and later executable tests must cover:
- application crash during command;
- DB transaction rollback;
- outbox publisher crash after/around publish;
- worker crash mid-job;
- duplicate external delivery;
- object store temporary outage;
- missing/corrupted source object;
- partial backup;
- bad migration;
- credentials/connector failure;
- search projection corruption;
- accidental logical object retirement;
- malicious/unauthorized mutation attempt.

## 13. Migration safety

Database migration must define:
- backward/forward compatibility window as needed;
- precondition checks;
- backup/rollback requirement for destructive migration;
- migration audit;
- post-migration invariants.

No production migration that silently rewrites evidence or revision history.

## 14. Degraded mode

Where practical, system may retain read-only access to existing baseline when non-critical subsystem fails.

Examples:
- notification outage → core read/write may continue;
- search index stale → direct object/trace may continue with warning;
- object preview renderer down → source metadata remains accessible.

Authority/gate decisions must not proceed when required canonical dependencies or audit write path are unavailable.

## 15. Operational dashboards

Suggested operator views:
- API/DB health;
- job backlog;
- failed integrations;
- storage integrity;
- backup/restore status;
- audit health;
- security/auth failures;
- governance blockers.

These are operations views, not engineering truth.
