# Backend Persistence, Indexing & Query Model

Status: `DRAFT_V0.1`

## 1. Goal

Define a storage model that preserves engineering history and traceability without prematurely introducing a graph database or distributed persistence.

## 2. Baseline storage

### PostgreSQL stores
- canonical object envelopes and typed payloads;
- object revisions;
- relation revisions;
- project/baseline membership;
- assignments/authority;
- reviews/gates/decisions;
- risks/acceptances;
- audit events;
- job/outbox metadata;
- searchable source metadata.

### Object/file storage stores
- original source bytes;
- large generated reports;
- archive/export packages;
- binary test evidence;
- rendered source previews when needed.

## 3. Logical table families

Reference families, not final SQL names:

```text
projects
project_baselines
baseline_members
object_logical
object_revisions
relation_logical
relation_revisions
sources
source_versions
source_locators
evidence_items
evidence_links
assignments
review_tasks
review_findings
gate_evaluations
gate_decisions
risk_acceptances
change_requests
change_sets
audit_events
outbox_events
jobs
view_definitions
view_layouts
```

Typed domain payload may initially use validated JSONB under a strict schema registry, with later extraction of frequently queried attributes into relational columns when measured.

## 4. JSONB rule

JSONB is allowed for typed payload evolution, not as an excuse to avoid domain design.

Each object revision records:
- `object_type`;
- `schema_version`;
- validated payload;
- common envelope columns.

Schema validator must reject payload inconsistent with object type/schema version.

## 5. Object logical/revision split

`object_logical`:
- stable ID;
- project;
- type;
- current candidate revision;
- lifecycle summary metadata.

`object_revisions`:
- immutable revision ID;
- parent revision;
- full validated payload snapshot or supported delta strategy;
- actor/time/reason;
- status at revision;
- hash/checksum for integrity where appropriate.

Prefer full snapshots initially for simplicity and reliable reconstruction; optimize to deltas only if storage evidence justifies it.

## 6. Relation storage

Relation is first-class and versioned similarly:
- stable relation ID;
- source logical ID;
- target logical ID;
- type;
- payload/rationale/evidence;
- revision/status.

Adjacency indexes required on both source and target.

## 7. Baseline storage

Baseline stores exact immutable membership:

```text
baseline_id
object_id → revision_id
relation_id → relation_revision_id
metadata/evidence/gate snapshot refs
```

Do not define baseline by “all current objects at time X” without explicit membership snapshot.

## 8. Audit storage

Audit is append-only at application level and protected from ordinary update/delete paths.

Audit fields:
- event ID;
- timestamp;
- actor/service identity;
- project;
- correlation ID;
- command type;
- target refs;
- before revision refs;
- after revision refs;
- authority context;
- result;
- rationale where required.

High-value audit may later be streamed to external immutable/WORM storage, but this is not MVP baseline.

## 9. Index strategy

### Mandatory candidate indexes
- `(project_id, object_type, status)`;
- `(project_id, updated_at)`;
- revision lookup by `(object_id, revision_sequence)`;
- relation adjacency by `(source_id, relation_type)`;
- relation adjacency by `(target_id, relation_type)`;
- source version by `(source_id, version_sequence)`;
- evidence by `source_version_id`;
- review queue by `(assignee, status)`;
- gate queue by `(project_id, status)`;
- jobs by `(status, next_attempt_at)`;
- outbox by `(published_at/null, created_at)`.

### Full text
PostgreSQL FTS over selected normalized text fields.

### Fuzzy lookup
Trigram indexes for names/terms/IDs where UX requires typo-tolerant search.

### JSONB
GIN only for demonstrated payload queries; do not indiscriminately GIN all JSONB.

## 10. Query categories

### Q1 Point lookup
Object/source/gate/review by stable ID and revision.

### Q2 Filtered list
Status, type, owner, station, stage, unresolved flags.

### Q3 Adjacency
Inbound/outbound direct neighbors.

### Q4 Bounded graph traversal
Trace and impact up to explicit depth/node count.

### Q5 Search
Free text + structured filters.

### Q6 Baseline compare
Object/relation additions, removals, revision changes.

### Q7 Coverage queries
- requirements without tests;
- claims without evidence;
- controls without verification;
- objects with UNKNOWN/conflict;
- stale objects;
- gates with blockers.

## 11. Graph traversal without graph DB

Initial traversal uses recursive SQL/CTE or application BFS/DFS over indexed adjacency, with:
- visited set;
- depth limit;
- node/edge result cap;
- relation-type filter;
- project/baseline scope.

Graph DB is considered only if measured workloads show unacceptable complexity/latency/operability.

## 12. Read projections

Derived projections may be maintained for expensive UI views, e.g.:
- station readiness summary;
- gate blocker count;
- trace coverage percentage;
- unresolved conflicts by stage;
- visual perspective membership.

Projection is rebuildable and never authoritative.

## 13. Referential integrity

Database constraints should enforce deterministic constraints where possible:
- project IDs exist;
- source/target object IDs exist;
- revision parent exists;
- baseline membership references immutable revision;
- unique stable IDs per namespace/project policy.

Domain validation handles semantic constraints not expressible cleanly in DB.

## 14. Retention

Do not hard-delete material engineering history by default.

Support:
- logical retirement;
- retention rules for uploaded source bytes by classification/legal policy;
- explicit disposition workflow;
- export/archive before permitted deletion where required.

## 15. Backup scope

Backup must include consistent set of:
- PostgreSQL canonical DB;
- object storage manifests/content;
- schema/migration metadata;
- encryption key/secret recovery process references (not secrets in backups docs);
- configuration needed to restore mappings.

## 16. Restore correctness

Restore verification checks:
- object/revision counts and hashes;
- baseline membership integrity;
- relation endpoint integrity;
- source byte hashes;
- audit continuity;
- representative trace queries;
- ability to open known baseline/project.

## 17. Capacity unknowns to measure before implementation sizing

- project count;
- average canonical object count/project;
- relation density;
- source bytes/project;
- revision rate;
- concurrent editors;
- trace query depth/frequency;
- import sizes;
- audit growth;
- retention horizon.

No invented sizing numbers are part of the design baseline.
