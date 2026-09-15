# FATHER Visual Engineering Workbench — API, Event & Persistence Contract

Status: `DRAFT_V0.1 / REFERENCE ARCHITECTURE`

## 1. Purpose

This document defines system boundaries between UI, application logic, persistence, import/export and future automation. It deliberately favors a **modular monolith** for the first implementation while keeping interfaces separable.

Core rule:

```text
simple transactional backend first
→ explicit modules
→ measurable bottleneck
→ only then split services / introduce broker / graph DB / search engine
```

---

# 2. Reference deployment topology

MVP reference:

```text
Browser
  ↓ HTTPS
FATHER Web/API application
  ├─ Project module
  ├─ Artifact/Graph module
  ├─ Source/Evidence module
  ├─ Requirements module
  ├─ Security/Risk module
  ├─ Architecture module
  ├─ Test/Gate module
  ├─ Version/Audit module
  ├─ Search module
  └─ Import/Export module
        ↓
PostgreSQL + object/file storage
```

Optional later:

```text
outbox
→ worker queue
→ async processors
```

Broker is not mandatory for MVP.

---

# 3. API principles

## API-001 Stable object IDs

External API uses stable logical IDs and explicit revision IDs.

## API-002 Optimistic concurrency

Write requests include expected revision/ETag. Conflict returns 409 with current revision metadata.

## API-003 Server authorization

UI visibility is convenience only. Backend enforces every permission and authority rule.

## API-004 Idempotency

Material create/approval/import operations support idempotency keys where retry could duplicate state.

## API-005 Structured errors

Error envelope:

```json
{
  "code": "RELATION_TYPE_MISMATCH",
  "message": "...",
  "object_ref": "REQ-014",
  "details": {},
  "correlation_id": "..."
}
```

## API-006 Pagination/filtering

Large object lists and relation traversals support cursor pagination and filters.

## API-007 No opaque mega-endpoint

Avoid endpoint that returns whole project as one unversioned JSON blob for editing.

---

# 4. API resource groups

Reference REST-style resource groups:

```text
/api/v1/projects
/api/v1/projects/{projectId}/baselines
/api/v1/projects/{projectId}/stations
/api/v1/objects
/api/v1/objects/{objectId}
/api/v1/objects/{objectId}/revisions
/api/v1/relations
/api/v1/sources
/api/v1/evidence
/api/v1/requirements
/api/v1/risks
/api/v1/threats
/api/v1/architecture
/api/v1/tests
/api/v1/gates
/api/v1/reviews
/api/v1/change-requests
/api/v1/views
/api/v1/search
/api/v1/trace
/api/v1/impact
/api/v1/audit
/api/v1/import
/api/v1/export
```

Exact route design may evolve via OpenAPI ADR; semantic resource boundaries are mandatory.

---

# 5. Project APIs

Minimum operations:

- create project shell;
- read project;
- update non-material project metadata;
- list baselines;
- create baseline candidate;
- promote baseline with authority;
- read stage/station states;
- switch project mode metadata GREENFIELD/BROWNFIELD/HYBRID with review when material.

Project creation must not create dozens of fake completed artifacts.

---

# 6. Object APIs

Generic canonical object API may expose polymorphic core envelope with typed payload.

Minimum:

- GET object current revision;
- GET specific revision;
- GET history;
- POST draft/new object;
- PATCH draft/current candidate under optimistic concurrency;
- POST retire/reject/supersede action;
- GET upstream/downstream relations;
- GET field evidence coverage.

Material state transitions should use explicit action endpoints or commands rather than arbitrary status PATCH.

---

# 7. Relation APIs

Operations:

- create typed relation;
- validate candidate relation;
- list inbound/outbound;
- retire/supersede relation;
- resolve relation evidence;
- trace path query.

Server validates endpoint classes and port types.

---

# 8. Trace API

Examples:

```text
GET /trace/{objectId}?direction=upstream&depth=5
GET /trace/{objectId}?direction=downstream&depth=5
GET /trace/{objectId}?target_type=TEST_CASE
GET /trace/path?from=SRC-1&to=TEST-42
```

Return graph fragment with relation semantics and revision info.

Depth/cycle controls mandatory.

---

# 9. Impact API

Impact is preview-first.

```text
POST /impact/preview
```

Input:

- proposed object revision/change set;
- selected baseline/context.

Output:

- directly affected objects;
- transitive affected objects;
- likely stale candidates;
- impacted gates;
- impacted tests;
- impacted approvals;
- suggested rework stations based on deterministic dependency rules;
- uncertainty flags.

Impact preview must not mutate project.

---

# 10. Source/Evidence APIs

Source operations:

- register source;
- register source version;
- attach/upload/link bytes;
- fetch metadata;
- fetch locator fragment/page representation;
- mark superseded/effective state;
- list dependent evidence links.

Evidence operations:

- create evidence link;
- classify support/conflict relation;
- verify locator resolvability;
- retire invalid evidence;
- list fields relying on evidence.

Large source content served via bounded endpoints/pre-signed references, not embedded in all object payloads.

---

# 11. Search API

Search query dimensions:

- free text;
- object type;
- project;
- stage/station;
- status;
- owner/reviewer;
- source;
- classification;
- tags;
- changed since;
- unresolved conflict/unknown;
- no evidence/no test.

Search result includes enough metadata to render command palette without secondary request where possible.

Initial implementation may use PostgreSQL FTS/trigram/indexes.

---

# 12. Gate/Approval APIs

Gate decision is a command, not generic object edit.

Reference:

```text
POST /gates/{gateId}/evaluate
POST /gates/{gateId}/decisions
```

Decision request contains:

- expected gate evaluation version;
- authority assignment;
- decision type;
- rationale;
- condition refs;
- evidence snapshot refs.

Server checks authority at decision time.

Risk acceptance uses dedicated command with expiry/review trigger.

---

# 13. Review APIs

- create review task;
- assign/reassign under policy;
- submit findings;
- mark finding resolved/unresolved;
- submit reviewer outcome;
- list review queue.

Review comments do not directly alter canonical object.

---

# 14. Change Request APIs

Flow:

```text
create proposal
→ impact preview
→ review
→ authority decision
→ execute linked changes
→ verify impacted objects/gates
→ close change request
```

Change Request stores exact before/after revision refs.

---

# 15. View/Layout APIs

View is non-authoritative projection metadata.

Operations:

- save view definition;
- save layout positions;
- save filters/perspective;
- share saved view;
- duplicate view definition;
- auto-layout preview/apply.

Layout writes should not create engineering audit noise unless view itself is controlled artifact.

---

# 16. Realtime transport

MVP requirement:

- server notifications for changed object/review assignment/import progress may use SSE or WebSocket;
- full collaborative CRDT editing is not required initially.

Preference: SSE for simple server→client events unless bi-directional realtime need is proven.

---

# 17. Engineering event model

Application events differ from immutable audit events.

Examples:

- OBJECT_REVISION_CREATED;
- RELATION_CREATED;
- SOURCE_SUPERSEDED;
- OBJECT_BECAME_STALE;
- REVIEW_ASSIGNED;
- REVIEW_COMPLETED;
- GATE_EVALUATED;
- GATE_DECIDED;
- TEST_RESULT_RECORDED;
- CHANGE_REQUEST_APPROVED;
- BASELINE_PROMOTED;
- RELEASE_DEPLOYED.

Event envelope:

```json
{
  "event_id": "uuid",
  "event_type": "OBJECT_REVISION_CREATED",
  "project_id": "...",
  "aggregate_ref": "REQ-014",
  "aggregate_version": "...",
  "occurred_at": "...",
  "actor_ref": "...",
  "correlation_id": "...",
  "causation_id": "...",
  "payload": {}
}
```

---

# 18. Transactional outbox

If async workers/events are introduced, use transactional outbox first:

```text
DB transaction:
  write domain change
  write outbox event
commit
worker publishes/processes outbox
```

This is preferred over dual-write to broker.

Kafka/NATS/RabbitMQ decision requires measured requirement and ADR.

---

# 19. Persistence model

Reference PostgreSQL schemas/modules:

```text
projects
objects
object_revisions
relations
relation_revisions
sources
source_versions
source_locators
evidence_links
baselines
baseline_members
assignments
reviews
review_findings
gates
gate_decisions
change_requests
tests
test_runs
test_results
views
view_layout
station_states
audit_events
outbox_events
```

Domain-specific typed tables may be added where query/integrity benefits justify them.

---

# 20. Revision storage strategy

Recommended hybrid:

- core logical object table stores stable identity/current pointer;
- immutable revision table stores versioned payload;
- important searchable fields normalized/indexed;
- relations versioned similarly;
- baseline table references exact revision IDs.

Avoid mutable in-place overwrite of verified/baselined material data.

---

# 21. Object storage

Use for:

- original source files;
- large PDFs/images/media;
- exported packages;
- test artifacts/log bundles;
- SBOM/scanner files where large;
- future model/eval artifacts.

Store content hash and metadata in DB.

Local filesystem may be DEV adapter, not assumed Production design.

---

# 22. Git synchronization/export

Git is an important interoperability target, not necessarily primary transactional DB.

Export package should produce deterministic paths/IDs where possible:

```text
project/
  manifest.yaml
  sources/
  product/
  requirements/
  security/
  architecture/
  tests/
  releases/
  views/
```

Structured files should be diff-friendly.

Import from Git must detect divergence and never silently overwrite newer server revisions.

---

# 23. OpenAPI / AsyncAPI generation

API contracts defined in Workbench may export to OpenAPI/AsyncAPI.

Conversely existing OpenAPI may be imported as candidate interface evidence.

Round-trip requires stable mapping metadata.

---

# 24. Structurizr integration

Architecture module should support adapter:

```text
canonical FATHER model
→ Structurizr workspace/DSL projection
→ Context/Container/Component/Dynamic/Deployment view
```

Imported Structurizr changes are candidate changes until validated/mapped.

---

# 25. BPMN integration

BPMN is optional process view.

bpmn-js may render/edit process representations, but FATHER remains canonical authority for project objects/roles/gates.

A BPMN user task may map to FATHER Review/Approval Task by stable reference.

---

# 26. Import pipeline

Generic import contract:

```text
RECEIVED
→ TYPE_DETECTED
→ PARSED
→ VALIDATED
→ MAPPED_CANDIDATES
→ USER/OWNER_REVIEW
→ COMMITTED
```

Failures preserve original input and error report.

Importer cannot directly promote mapped objects to VERIFIED unless explicit rule permits.

---

# 27. Export pipeline

Exports are snapshot-based.

Export manifest contains:

- project ID;
- baseline/timepoint;
- included object revisions;
- generated_at;
- exporter version;
- hashes where useful.

---

# 28. Future AI Gateway API

AI Gateway interface only after activation:

```text
POST /ai/runs
GET /ai/runs/{id}
```

Request references frozen canonical inputs instead of arbitrary raw prompt where possible.

Server performs:

- role/capability validation;
- data classification/provider policy;
- tool permission policy;
- prompt/version selection;
- output schema validation;
- audit record.

AI output becomes candidate object/review finding, never direct verified truth.

---

# 29. Caching

Allowed caches:

- object current revision;
- graph neighborhoods;
- search results;
- view projections;
- source previews.

Cache key includes project/revision context where stale mix could occur.

Cache invalidation triggered by domain events.

---

# 30. Backup / restore

Production-ready requirements:

- DB backups;
- object storage backup/versioning policy;
- encryption/key handling;
- documented restore procedure;
- periodic restore test;
- baseline reconstruction test.

RPO/RTO values remain project deployment NFR to baseline later.

---

# 31. Migration

Every schema migration includes:

- forward script;
- compatibility impact;
- data transformation validation;
- backup requirement;
- rollback or restore plan;
- test fixture.

No destructive migration without explicit release review.

---

# 32. API security

- OAuth2/OIDC or approved enterprise identity;
- short-lived sessions/tokens as deployment policy;
- CSRF protection where cookie sessions;
- input validation;
- output encoding;
- rate limiting on sensitive/expensive endpoints;
- object-level authorization;
- audit of material operations;
- secure file upload pipeline;
- secrets never returned in API payloads.

---

# 33. Performance strategy

Before introducing specialized stores:

1. benchmark representative PostgreSQL graph traversal;
2. benchmark search;
3. benchmark canvas projection queries;
4. profile largest expected neighborhood;
5. identify dominant bottleneck;
6. only then ADR for GraphDB/OpenSearch/broker.

---

# 34. Observability

Backend request context:

- request ID;
- user/actor;
- project;
- operation;
- duration;
- result/error class.

Trace material async work using correlation/causation IDs.

Metrics later include:

- request latency;
- graph query latency;
- import throughput;
- search latency;
- stale propagation duration;
- failed authorization;
- audit write failure;
- queue depth if async introduced.

---

# 35. Failure semantics

System must fail closed for:

- authority check uncertainty;
- invalid source version reference;
- unresolved required evidence pointer;
- sensitive external AI routing;
- baseline promotion race;
- conflicting concurrent material edit.

Read-only access may degrade gracefully if noncritical projection/cache services fail.

---

# 36. Compatibility

API versioning required for breaking public contract changes.

Internal object schema version independent from HTTP API version.

Frontend/backend version skew policy defined in release deployment design.

---

# 37. Reference repository structure

Future implementation candidate:

```text
father_workbench/
  backend/
    app/
      api/
      domain/
      services/
      persistence/
      security/
      importers/
      exporters/
  frontend/
    src/
      canvas/
      inspector/
      views/
      api/
      state/
      components/
  contracts/
    openapi/
    schemas/
  tests/
    unit/
    integration/
    e2e/
    security/
    performance/
```

This is a logical recommendation, not implementation authorization.

---

# 38. Acceptance checks for this contract

Before implementation:

- data model objects can be represented without UI-specific hacks;
- all material state transitions map to explicit API commands;
- baselines reconstruct exact revisions;
- impact preview is non-mutating;
- source locator is version-specific;
- authority cannot be bypassed via generic object PATCH;
- audit event records material operation;
- import does not auto-verify;
- layout persistence separate from semantic model;
- future AI API is feature-gated and policy-bound.