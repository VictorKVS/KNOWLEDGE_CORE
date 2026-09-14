# FATHER Visual Engineering Workbench — Backend Master ТЗ

Status: `DRAFT_V0.2 / DESIGN BEFORE CODE / OSINT_KB CANONICAL`

## 1. Назначение backend

Backend FATHER — не вспомогательный CRUD для canvas. Он является серверным контуром инженерной истины и обязан обеспечивать:

- канонические инженерные объекты и их версии;
- типизированные связи и трассируемость;
- evidence/provenance;
- требования, угрозы, риски, решения, тесты и gates;
- authority boundaries и human approval;
- baseline/change/version semantics;
- поиск, trace и impact analysis;
- аудит и воспроизводимость;
- экспорт/импорт канонической модели;
- безопасную точку интеграции для будущих LLM/Model Zoo workers.

## 1.1 Каноническая БД

Все подразделения FATHER используют **одну физическую operational PostgreSQL БД**:

```text
osint_kb
```

Не создаются отдельные `father_db`, `alina_db`, полный дублирующий `knowledge_factory` или per-agent vector DB.

FATHER, ALINA, OSINT, Security и будущие подразделения используют общие canonical IDs, общие review/audit/provenance rules и единый shared pgvector layer.

`KNOWLEDGE_CORE` — source corpus/provenance/specification layer, а не вторая operational DB.

До любого DDL обязательна фактическая инвентаризация `osint_kb` и reconciliation существующих схем по `KEEP / EXTEND / RENAME_VIEW / NEW` согласно `11_FATHER_DB_CANONICAL_ARCHITECTURE_V1.md` и `12_DB_RECONCILIATION_MATRIX.yaml`.

## 2. Главные инварианты

### BE-INV-001 Semantic object is canonical
UI node, diagram position, generated Markdown or export file are representations. Canonical operational state lives in `osint_kb` domain objects/adapters.

### BE-INV-002 Stable logical identity
Logical object ID survives revisions. Exact revision is immutable and addressed separately.

### BE-INV-003 No silent overwrite
Material revision is never destructively overwritten. New material edit creates a revision or candidate state according to object policy.

### BE-INV-004 Evidence is resolvable
Material claim/requirement/decision/control/test must be able to resolve back through `Source → Capture/Version → Span/Locator → Object` or explicitly carry `UNKNOWN / OWNER_DECISION / ASSUMPTION / HYPOTHESIS / DERIVED_CALCULATION` status.

### BE-INV-005 UI cannot authorize
Hiding a button in UI does not constitute authorization. Backend validates permissions and authority for every command.

### BE-INV-006 Gate is command + evidence snapshot
Gate result cannot be set by arbitrary PATCH. Evaluation and final decision are explicit commands with evidence snapshot, decision actor, authority and rationale.

### BE-INV-007 Residual risk is human-owned
Models, automated rules and ordinary reviewers may recommend; only authorized risk owner may accept residual risk.

### BE-INV-008 Change propagates staleness, not hidden mutation
Upstream material change does not silently rewrite downstream artifacts. It may mark dependent objects/gates/tests `STALE_CANDIDATE` or `REVIEW_REQUIRED` according to deterministic dependency rules.

### BE-INV-009 Brownfield first maps, then creates
Existing source material and existing `osint_kb` structures are inventoried/mapped before missing artifacts or new schemas are created.

### BE-INV-010 Deterministic before AI
Validation, schema checks, exact dependency traversal, authority checks, state machines, hashes and calculations remain deterministic.

### BE-INV-011 One canonical DB
One semantic object has one canonical operational owner in `osint_kb`. Duplicate canonical tables across schemas/divisions are prohibited.

### BE-INV-012 Graph is projection
`graph.*` is derived/rebuildable and never becomes independent authoring truth.

### BE-INV-013 Weights are versioned
Weight revisions are append-only and retain method, factors, evidence, reason, actor and previous version.

### BE-INV-014 Shared review/audit
Review and audit infrastructure is universal across FATHER divisions; no incompatible per-agent review/audit silos.

### BE-INV-015 No auto-promotion
Parser/LLM/model output cannot promote directly into canonical state without required validation/review/gate.

## 3. Reference architecture

Initial backend is a **modular monolith** over the existing `osint_kb` database.

```text
HTTP/API Boundary
      ↓
Application Commands / Queries
      ↓
Domain Modules / Canonical Adapters
  ├─ Project & Baseline
  ├─ Canonical Object Graph
  ├─ Source & Evidence
  ├─ Product / Requirements
  ├─ System Model
  ├─ Security / Risk
  ├─ Architecture / Decision
  ├─ Verification / Tests
  ├─ Gate / Review / Approval
  ├─ Search / Trace / Impact
  ├─ Version / Audit / Change
  └─ Import / Export
      ↓
Infrastructure Ports
  ├─ PostgreSQL: osint_kb
  ├─ Protected Object/File Storage
  ├─ PostgreSQL FTS/trigram/pgvector where justified
  ├─ Outbox / Job Runner
  └─ External Connector Adapters
```

No service split is part of initial design.

## 4. Architectural layers

### 4.1 Transport layer
Responsibilities:
- HTTP request/response;
- authentication context;
- input schema validation;
- ETag/idempotency/correlation headers;
- problem detail responses;
- streaming/download endpoints.

Must not contain engineering decision logic.

### 4.2 Application layer
Responsibilities:
- commands and queries;
- transaction orchestration;
- calling domain policies;
- scheduling post-commit work;
- authority pre-check orchestration;
- canonical adapters over existing `osint_kb` schemas;
- returning DTOs/projections.

### 4.3 Domain layer
Responsibilities:
- invariants;
- state transitions;
- typed relationships;
- gate policies;
- evidence rules;
- baseline/change semantics;
- stale propagation rules;
- authority rules expressed as domain policies.

Domain must not depend on FastAPI, SQLAlchemy, React Flow, HTTP or vendor SDKs.

### 4.4 Infrastructure layer
Responsibilities:
- `osint_kb` persistence/adapters;
- object bytes;
- search/index adapters;
- shared pgvector indexing;
- outbox/job runner;
- connectors;
- email/webhook notifications;
- backup/restore integration.

## 5. Module rule

Each module must have:
- explicit owned entities/aggregates;
- explicit mapping to canonical `osint_kb` physical structures;
- explicit public commands/queries;
- no uncontrolled direct table access from another module;
- documented transaction boundaries;
- domain events only for post-commit propagation/integration, not as substitute for ordinary function calls inside one transaction;
- tests for its invariants.

Existing tables may be exposed through canonical adapters/views rather than copied into new tables.

## 6. Core modules

### BE-MOD-01 Project & Baseline
Owns canonical project/baseline semantics and maps to reconciled `osint_kb` structures.

### BE-MOD-02 Object Graph
Owns canonical object/relation API semantics; graph projection itself remains derived.

### BE-MOD-03 Source & Evidence
Owns Source/Capture/Version/Span/Locator/Evidence semantics and provenance adapters.

### BE-MOD-04 Product / Analysis / Requirements
Owns product and requirements semantics; may map to existing knowledge/normative structures where appropriate.

### BE-MOD-05 System Model
Owns System/Boundary/Actor/Function/DataFlow/Interface/Dependency/OperationalMode semantics.

### BE-MOD-06 Security & Risk
Owns Asset/Threat/Risk/Control/RiskAcceptance semantics, reconciling `security_core`, `security_advanced` and future canonical security view.

### BE-MOD-07 Architecture & Decision
Owns ArchitectureDriver/Option/View/Tradeoff/ADR/Component/API/Event/Data/Deployment semantics.

### BE-MOD-08 Verification
Owns TestOracle/TestCase/TestSuite/TestRun/TestResult/Defect/Vulnerability/Verification/Validation semantics.

### BE-MOD-09 Review / Gate / Authority
Owns universal ReviewTask/ReviewFinding/ApprovalDecision/GateEvaluation/GateDecision/authority snapshot semantics.

### BE-MOD-10 Search / Trace / Impact
Owns projections/indexes only, never semantic truth.

### BE-MOD-11 Version / Change / Audit
Owns version/change metadata, append-only AuditEvent and snapshot semantics.

### BE-MOD-12 Import / Export
Owns import jobs, mapping reports, git-safe exports and compatibility checks; imported data remains candidate until mapped/validated.

## 7. Command/query separation

Backend is not required to implement formal CQRS infrastructure, but conceptually separates commands and queries.

**Commands** mutate canonical state through explicit domain rules.

**Queries** read canonical state or derived projections without mutation.

No query endpoint may have mutation side effects.

## 8. Transaction strategy

Default rule: one business command = one `osint_kb` database transaction for canonical state.

Post-commit activities such as indexing, notifications and external webhooks happen via outbox/job mechanism.

Never keep DB transaction open while calling external LLM/SaaS, waiting for human approval or running long parse/eval jobs.

## 9. Baseline model

Baseline is an immutable named snapshot of selected canonical object/relation revisions.

No baseline is edited after creation. New state creates a new baseline candidate.

## 10. Version model

Every material object must expose logical ID + immutable revision ID + actor/time/change reason/source-evidence delta/status even if its physical representation is an existing table with compatibility adapter.

## 11. State model

Backend uses explicit state machines for canonical artifacts, sources, evidence verification, review tasks, gates, risks, change requests, baselines, imports and jobs.

## 12. Relationship model

Relations are first-class, typed and versionable. Canonical relation semantics may be stored in existing domain tables or normalized relation structures, but duplicate truths are not allowed.

## 13. Traceability engine

Must answer deterministically:
- What source/evidence supports this field/object?
- Which requirements drive this decision?
- Which threats created this security requirement?
- Which controls mitigate this risk?
- Which tests verify this requirement/control?
- Which downstream artifacts become suspect if this object changes?
- Which gate was decided using this revision?

## 14. Impact model

Tier 1 deterministic structural impact is authoritative for known relations. Tier 2 semantic/model-assisted impact remains candidate until confirmed.

## 15. Search strategy

Start inside `osint_kb` with PostgreSQL B-tree/GIN/FTS/trigram and shared pgvector. External search engine requires benchmark/ADR.

## 16. Object/file storage

Canonical metadata lives in `osint_kb`; protected originals and large generated artifacts live in protected object/local storage addressed by content hash + storage key.

## 17. Async work

Initial backend may run a simple in-process/database-backed job runner. Kafka/message broker is explicitly outside baseline until measured need.

## 18. Authorization model

Use RBAC + project assignment + object/classification conditions. Authority is evaluated server-side at command execution.

## 19. Audit model

Material commands emit append-only audit facts into universal audit infrastructure. Audit stream must not rely only on application logs.

## 20. Failure model

Backend must fail closed for missing authority, revision conflict, invalid relation, unresolved evidence when required, illegal state transition, classification violation, baseline mutation, missing gate evidence and canonical-duplication violations.

## 21. Recovery model

Required: transaction rollback, retry-safe commands, outbox retry, dead-letter/review state, backup/restore, restore verification and object-level history reconstruction.

## 22. API principles

- versioned API;
- OpenAPI contract;
- optimistic concurrency;
- idempotency for retryable material creates;
- typed errors;
- cursor pagination;
- bounded graph queries;
- no whole-project mutable mega-document;
- no generic status PATCH for governed transitions;
- canonical adapters hide physical legacy differences without copying truth.

## 23. Import/export principles

Import never equals truth promotion. Git export is only reviewed/sanitized/classification-allowed projection.

## 24. Integration boundaries

External integrations use adapters and cannot write canonical tables directly. Future FATHER/ALINA/OSINT/Security agents interact through scoped application APIs using shared canonical IDs.

## 25. Observability

Backend exposes structured logs, correlation IDs, DB/query/job metrics, gate/review metrics, audit health, storage health, backup age and restore-test status.

## 26. Security requirements

At minimum: least privilege, secure auth/session, upload quarantine, no trust in client authority, secrets outside repo, classification-aware export, immutable audit, dependency/SAST/SCA/secret scanning, threat model before implementation.

## 27. AI boundary

Future AI workers cannot connect directly for uncontrolled writes, bypass authority, accept risk or auto-promote candidate knowledge.

## 28. Canonical DB reconciliation gate

Before backend implementation or new DDL, `FATHER_DB_CANONICAL_ARCHITECTURE_V1_READY` requires:
- actual `osint_kb` schema/table/view/extension/index inventory;
- schema ownership map;
- mapping of target logical families to physical structures;
- `KEEP / EXTEND / RENAME_VIEW / NEW` classification;
- duplicate truth report;
- compatibility adapter/view plan;
- migration test plan;
- rollback plan;
- architecture review.

## 29. Backend design exit criteria

`BACKEND_DESIGN_READY` requires all of:
- `FATHER_DB_CANONICAL_ARCHITECTURE_V1_READY`;
- module ownership accepted;
- object/relationship schemas stable enough for v1;
- state machines defined;
- transaction boundaries defined;
- persistence/index model reviewed against actual `osint_kb`;
- authority matrix mapped to commands;
- audit model defined;
- async/job semantics defined;
- backup/restore strategy defined;
- test oracles written;
- failure/rework scenarios reviewed;
- unresolved UNKNOWNs explicitly listed;
- no code architecture decision left intentionally to implementation without ADR/owner.

Until this gate is satisfied, backend implementation remains blocked.
