# FATHER Visual Workbench — Backend Specification

Status: `PRIMARY BACKEND DESIGN WORKSTREAM / NO IMPLEMENTATION AUTHORIZED`

This directory decomposes the backend of FATHER Visual Engineering Workbench to implementation-ready contracts **before product code is allowed**.

## Read order

1. `00_BACKEND_MASTER_TZ.md` — backend goals, architecture, module boundaries and invariants.
2. `01_DOMAIN_MODULE_BOUNDARIES.md` — bounded modules, aggregates, commands, queries and ownership.
3. `02_STATE_MACHINE_TRANSACTION_MODEL.md` — object/gate/review/baseline/change state machines and transaction boundaries.
4. `03_PERSISTENCE_INDEXING_QUERY_MODEL.md` — PostgreSQL/object-store design, indexes, graph queries, versioning and retention.
5. `04_SOURCE_EVIDENCE_FILE_PIPELINE.md` — source registration, immutable bytes, locators, evidence, parsing boundary and provenance.
6. `05_SEARCH_TRACE_IMPACT_ENGINE.md` — search, trace, dependency traversal, stale propagation and impact analysis.
7. `06_AUTHORITY_SECURITY_AUDIT_BACKEND.md` — RBAC/ABAC, authority decisions, audit immutability and backend threat controls.
8. `07_JOBS_INTEGRATION_NOTIFICATION_MODEL.md` — synchronous vs async boundary, outbox, jobs, retries, idempotency and integrations.
9. `08_OBSERVABILITY_BACKUP_RECOVERY.md` — logs, metrics, traces, health, backup, restore and failure recovery.
10. `09_BACKEND_TEST_ACCEPTANCE_GATE.md` — deterministic acceptance package required before implementation promotion.
11. `10_BACKEND_REQUIREMENTS_TRACEABILITY.yaml` — machine-readable backend requirements and verification mapping.

## Governing principle

```text
canonical domain model
→ backend contracts
→ state machines
→ transaction semantics
→ storage/query design
→ authority/security model
→ failure/recovery model
→ test oracles
→ BACKEND DESIGN READY
→ only then implementation planning
```

The backend is not a CRUD layer behind the canvas. It is the **engineering truth and governance engine** of FATHER.

## Simplicity rule

Initial architecture remains a modular monolith with PostgreSQL and object storage. Splitting into services, introducing a message broker, graph database, external search engine or distributed workers requires a measured reason and an ADR.
