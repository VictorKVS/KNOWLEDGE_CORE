# FATHER Visual Engineering Workbench — Backend Master ТЗ

Status: `DRAFT_V0.1 / DESIGN BEFORE CODE`

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

## 2. Главные инварианты

### BE-INV-001 Semantic object is canonical
UI node, diagram position, generated Markdown or export file are representations. Canonical state lives in backend domain objects.

### BE-INV-002 Stable logical identity
Logical object ID survives revisions. Exact revision is immutable and addressed separately.

### BE-INV-003 No silent overwrite
Material revision is never destructively overwritten. New material edit creates a revision or candidate state according to object policy.

### BE-INV-004 Evidence is resolvable
Material claim/requirement/decision/control/test must be able to resolve back to source/evidence or explicitly carry `UNKNOWN / OWNER_DECISION / ASSUMPTION` status.

### BE-INV-005 UI cannot authorize
Hiding a button in UI does not constitute authorization. Backend validates permissions and authority for every command.

### BE-INV-006 Gate is command + evidence snapshot
Gate result cannot be set by arbitrary PATCH. Evaluation and final decision are explicit commands with evidence snapshot, decision actor, authority and rationale.

### BE-INV-007 Residual risk is human-owned
Models, automated rules and ordinary reviewers may recommend; only authorized risk owner may accept residual risk.

### BE-INV-008 Change propagates staleness, not hidden mutation
Upstream material change does not silently rewrite downstream artifacts. It may mark dependent objects/gates/tests `STALE_CANDIDATE` or `REVIEW_REQUIRED` according to deterministic dependency rules.

### BE-INV-009 Brownfield first maps, then creates
Existing source material is parsed/mapped before missing artifacts are drafted.

### BE-INV-010 Deterministic before AI
Validation, schema checks, exact dependency traversal, authority checks, state machines, hashes and calculations remain deterministic.

## 3. Reference architecture

Initial backend is a **modular monolith**.

```text
HTTP/API Boundary
      ↓
Application Commands / Queries
      ↓
Domain Modules
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
  ├─ PostgreSQL
  ├─ Object/File Storage
  ├─ Optional FTS/trigram/vector indexes
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
- persistence;
- object bytes;
- search/index adapters;
- outbox/job runner;
- connectors;
- email/webhook notifications;
- backup/restore integration.

## 5. Module rule

Each module must have:
- explicit owned entities/aggregates;
- explicit public commands/queries;
- no direct table access from another module;
- documented transaction boundaries;
- domain events only for post-commit propagation/integration, not as substitute for ordinary function calls inside one transaction;
- tests for its invariants.

## 6. Core modules

### BE-MOD-01 Project & Baseline
Owns:
- Project;
- ProjectBaseline;
- ProjectStageState;
- StationState;
- baseline promotion/supersession.

### BE-MOD-02 Object Graph
Owns:
- generic object envelope;
- relation envelope;
- relation type registry;
- visual projection metadata boundaries.

### BE-MOD-03 Source & Evidence
Owns:
- Source;
- SourceVersion;
- immutable source bytes reference;
- SourceLocator;
- EvidenceItem;
- EvidenceLink;
- supersession/effectivity metadata.

### BE-MOD-04 Product / Analysis / Requirements
Owns:
- BusinessNeed;
- ProductVision;
- Stakeholder;
- ScopeItem;
- Requirement;
- NFRScenario;
- AcceptanceCriterion;
- Assumption/Unknown linkage.

### BE-MOD-05 System Model
Owns:
- System;
- Boundary;
- Actor;
- Function;
- DataFlow;
- Interface;
- Dependency;
- OperationalMode.

### BE-MOD-06 Security & Risk
Owns:
- Asset/ProtectedInterest;
- NegativeConsequence;
- ThreatSource;
- TrustBoundary;
- EntryPoint;
- ThreatScenario;
- SecurityRequirement;
- SecurityControl;
- Risk;
- RiskAcceptance.

### BE-MOD-07 Architecture & Decision
Owns:
- ArchitectureDriver;
- ArchitectureOption;
- ArchitectureView metadata;
- TradeoffRecord;
- ADR;
- Component;
- API/Event/Data/Deployment contracts.

### BE-MOD-08 Verification
Owns:
- TestOracle;
- TestCase;
- TestSuite;
- TestRun;
- TestResult;
- Defect;
- Vulnerability;
- VerificationReport;
- ValidationReport.

### BE-MOD-09 Review / Gate / Authority
Owns:
- ReviewTask;
- ReviewFinding;
- ApprovalDecision;
- Gate;
- GateEvaluation;
- GateDecision;
- Assignment/authority snapshot.

### BE-MOD-10 Search / Trace / Impact
Owns projections/indexes, not engineering source-of-truth objects.

### BE-MOD-11 Version / Change / Audit
Owns:
- ChangeRequest;
- ChangeSet;
- revision metadata;
- immutable AuditEvent;
- correlation chain.

### BE-MOD-12 Import / Export
Owns import jobs, mapping reports, export packages and compatibility checks; imported data remains candidate until mapped/validated.

## 7. Command/query separation

Backend is not required to implement formal CQRS infrastructure, but conceptually separates:

**Commands** — mutate state through explicit domain rules.

Examples:
- RegisterSource;
- CreateRequirementDraft;
- ConfirmArtifact;
- CreateTypedRelation;
- SupersedeObject;
- SubmitReviewFinding;
- AcceptResidualRisk;
- PromoteBaseline;
- DecideGate.

**Queries** — read projections without mutation.

Examples:
- GetObject;
- ListUpstreamTrace;
- FindUnverifiedRequirements;
- GetGateReadiness;
- PreviewImpact;
- CompareBaselines.

No query endpoint may have mutation side effects.

## 8. Transaction strategy

Default rule: one business command = one database transaction for canonical state.

Post-commit activities such as indexing, notifications and external webhooks happen via outbox/job mechanism.

Never keep DB transaction open while:
- calling external LLM;
- uploading large bytes to remote provider;
- waiting for user approval;
- calling external SaaS;
- running long parse/eval job.

## 9. Baseline model

Baseline is an immutable named snapshot of selected object revisions and relation revisions.

A project may contain:
- working candidate state;
- zero or more frozen baselines;
- current approved baseline;
- previous/superseded baselines.

Baseline promotion requires:
- candidate snapshot;
- readiness evaluation;
- authority check;
- unresolved blocker policy;
- audit record.

No baseline is edited after creation. New state creates a new baseline candidate.

## 10. Version model

Every material object stores:
- logical `object_id`;
- immutable `revision_id`;
- monotonic or sortable revision sequence;
- schema version;
- parent revision;
- actor;
- timestamp;
- change reason;
- source/evidence delta;
- status.

For non-material visual layout, a separate lighter versioning policy may be used.

## 11. State model

Backend uses explicit state machines for:
- canonical artifacts;
- sources;
- evidence verification;
- review tasks;
- gates;
- risks;
- change requests;
- baselines;
- imports;
- jobs.

State transition must be command-based and validated centrally.

## 12. Relationship model

Relations are first-class, typed and versionable.

Each relation type defines:
- allowed source types;
- allowed target types;
- direction semantics;
- evidence/rationale requirement;
- whether relation is baseline-significant;
- whether change participates in impact propagation.

Examples:
- DERIVED_FROM;
- SATISFIES;
- DRIVES;
- MITIGATES;
- VERIFIES;
- CONTRADICTS;
- SUPERSEDES;
- DEPENDS_ON;
- IMPLEMENTS;
- MONITORS;
- ACCEPTS_RISK_FOR.

## 13. Traceability engine

Must answer deterministically:
- What source/evidence supports this field/object?
- Which requirements drive this decision?
- Which threats created this security requirement?
- Which controls mitigate this risk?
- Which tests verify this requirement/control?
- Which downstream artifacts become suspect if this object changes?
- Which gate was decided using this revision?

Cycle-safe traversal and depth limits are mandatory.

## 14. Impact model

Impact analysis has two tiers.

### Tier 1 — deterministic structural impact
Uses relation graph and dependency rules.

### Tier 2 — semantic impact candidate
Future model-assisted analysis may suggest additional affected objects, but cannot mark them verified without deterministic relation or human confirmation.

Preview never mutates state.

## 15. Search strategy

Start with PostgreSQL:
- B-tree indexes;
- GIN JSONB where justified;
- FTS;
- trigram;
- materialized/projection tables only where measured.

External search engine is deferred until measured query/scale need.

## 16. Object/file storage

Canonical metadata lives in PostgreSQL.
Original source bytes and large generated artifacts live in object/file storage addressed by content hash + storage key.

Metadata stores:
- SHA-256;
- byte length;
- MIME/type;
- source locator;
- upload actor/time;
- classification;
- malware/quarantine status;
- retention/disposition metadata.

## 17. Async work

Initial backend may run simple in-process worker or database-backed job runner.

Async candidate tasks:
- document parsing;
- checksum/metadata extraction;
- large import/export;
- index rebuild;
- report generation;
- notifications;
- later AI evaluation.

Kafka/message broker is explicitly out of baseline until required.

## 18. Authorization model

Use RBAC + project assignment + object/classification conditions.

Distinguish:
- permission to view;
- permission to propose edit;
- permission to confirm artifact;
- permission to review;
- permission to approve gate;
- permission to accept risk;
- permission to promote baseline;
- administrative permission.

Authority is evaluated at command execution using current assignment and policy snapshot.

## 19. Audit model

Every material command emits immutable audit facts including:
- actor;
- authority context;
- command;
- target;
- previous revision;
- new revision;
- correlation ID;
- rationale/decision when required;
- evidence snapshot refs when required.

Audit stream must not rely only on application logs.

## 20. Failure model

Backend must fail closed for:
- missing required authority;
- revision conflict;
- invalid relation type;
- evidence locator unresolved when policy requires it;
- illegal state transition;
- classification policy violation;
- baseline mutation attempt;
- missing mandatory gate evidence.

Transient infrastructure failure must not produce partial canonical mutation.

## 21. Recovery model

Required:
- transactional rollback;
- retry-safe idempotent commands where applicable;
- outbox retry;
- dead-letter/review state for repeated async failures;
- backup/restore;
- restore verification;
- object-level history reconstruction.

## 22. API principles

- versioned API;
- OpenAPI contract;
- optimistic concurrency;
- idempotency keys for retryable material creates;
- typed structured errors;
- cursor pagination;
- bounded graph queries;
- no whole-project mutable mega-document;
- no generic status PATCH for governed transitions.

## 23. Import/export principles

Import is never equivalent to truth promotion.

Flow:

```text
bytes/source
→ parse
→ mapping candidate
→ validation
→ conflict/gap report
→ owner/domain review where material
→ canonical candidate objects
```

Export must be reproducible from baseline IDs.

## 24. Integration boundaries

External integrations must use adapters and cannot write canonical tables directly.

Categories:
- GitHub/Git repository;
- file/library source;
- issue tracker;
- CI/test systems;
- notification channels;
- future LLM/model gateway.

Each adapter defines:
- credentials boundary;
- data classification policy;
- retry/idempotency;
- provenance;
- rate limit handling;
- failure visibility.

## 25. Observability

Backend itself must expose:
- structured logs;
- request correlation IDs;
- command duration/error metrics;
- DB/query metrics;
- job backlog/failure metrics;
- gate/review queue metrics;
- audit health;
- storage health;
- backup age/restore test status.

## 26. Security requirements

At minimum:
- strong authentication integration;
- least privilege;
- secure session/token handling;
- CSRF/XSS/SSRF controls as applicable;
- upload quarantine/content validation;
- no server-side trust in client-supplied role/authority;
- secrets outside repository;
- classification-aware export/download;
- append-only/immutable audit policy;
- dependency/SAST/SCA/secret scanning during implementation;
- threat model before implementation.

## 27. AI boundary

Future AI workers interact only through application APIs/commands using scoped service identities.

They must not:
- connect directly to DB for uncontrolled writes;
- bypass authority;
- mark themselves human approvers;
- accept risk;
- auto-promote evidence to verified without policy;
- silently expand source scope.

## 28. Backend design exit criteria

`BACKEND_DESIGN_READY` requires all of:
- module ownership accepted;
- object/relationship schemas stable enough for v1;
- state machines defined;
- transaction boundaries defined;
- persistence/index model reviewed;
- authority matrix mapped to commands;
- audit model defined;
- async/job semantics defined;
- backup/restore strategy defined;
- test oracles written;
- failure/rework scenarios reviewed;
- unresolved UNKNOWNs explicitly listed;
- no code architecture decision left intentionally to implementation without ADR/owner.

Until this gate is satisfied, backend implementation remains blocked.
