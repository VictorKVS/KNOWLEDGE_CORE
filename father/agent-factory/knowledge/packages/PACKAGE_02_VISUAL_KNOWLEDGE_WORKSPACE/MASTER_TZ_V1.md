# FATHER Visual Knowledge Workspace — Master Technical Specification v1.0

Document ID: `FATHER-VKW-TZ-0001`
Status: `BASELINE_DRAFT`
Owners: Senior Project Manager + Lead System Analyst + Chief Architect
Lifetime intent: multi-year professional product
Upstream: FATHER Knowledge Factory Package 01

## 1. Product mission

Build a long-lived professional workspace that turns source information into traceable, reviewable, reusable knowledge and then into concrete products: reports, ADRs, checklists, recommendations, dossiers, control mappings, role-specific knowledge packs and future agent memory.

Core transformation:

`SOURCE -> EXTRACT/OCR -> TRANSLATION -> CLAIM/ENTITY -> EVIDENCE -> KNOWLEDGE_NODE -> KNOWLEDGE_EDGE -> REVIEW -> ROLE_VIEW -> DECISION -> PRODUCT -> OUTCOME -> LESSON`

Every transition is observable, API-addressable and traceable.

## 2. Product principles

1. Evidence-first: no verified fact without resolvable evidence.
2. Source immutability: originals are never overwritten by OCR, translation or interpretation.
3. One canonical truth graph: role views are projections, never semantic copies.
4. API-first: every material capability has a documented service contract.
5. Trace-first: every material execution stage emits trace/span events.
6. Human governance: models propose; review/promotion gates decide.
7. Visual-first: relationships, lineage, status, contradictions and product derivation are visible graphically.
8. Long-term evolution: architecture must permit replacement of UI renderer, model, vector store and runtime without breaking logical IDs.
9. Design-as-system: Figma is the canonical UX/design source; code follows governed components/tokens.
10. Microservices by evidence, not fashion: split only for independent scaling, trust boundary, failure isolation, GPU/runtime differences or release lifecycle.

## 3. Users and professional roles

Primary:
- Analyst
- Chief Analyst / Reviewer
- Architect
- Software Engineer
- Information Security specialist
- Lawyer
- Manager
- Product Manager

Secondary:
- QA
- DevOps/SRE
- Data/ML engineer
- Security engineer
- Knowledge curator
- Auditor

## 4. User outcomes

The user must be able to answer:
1. What source entered the system?
2. What was extracted from it?
3. What changed during OCR/translation/normalization?
4. Which claims/entities/relations were created?
5. Which exact evidence supports each claim?
6. What contradicts or refines it?
7. Who/what reviewed it?
8. Which role sees it and why?
9. Which decision used it?
10. Which product/artifact was generated from it?
11. What runtime/API/model created each step?
12. What changed later and why?

## 5. Workspace modes

### 5.1 Investigate
OSINT-style graph investigation. Expand/pivot from any node. Save scenes/workspaces.

### 5.2 Lineage
Upstream/downstream chain from source to product and back.

### 5.3 Perspectives
Role-specific projections over one canonical graph: Architect, Programmer, Security, Lawyer, Manager, Product.

### 5.4 Cases
Queue of investigations/tasks with owner, status, SLA/review state, comments, attachments and trace.

### 5.5 Sources
Source registry: original, SHA-256, version, legal/use status, language, OCR state, extraction quality, translation state, downstream usage.

### 5.6 Products
Products generated from knowledge: report, ADR, checklist, dossier, recommendation, control mapping, agent knowledge pack.

### 5.7 Trace
Execution lineage: trace_id, span_id, parent_span_id, stage, service, API operation, worker, model, latency, retries, result/error.

### 5.8 Architecture Studio
Graphical architecture editor with C4 C1/C2/C3, sequence, data-flow, trust boundaries, API links, ADR links and requirement traceability.

## 6. Graph editor requirements

The central workspace behaves as a professional graphical editor, not a passive chart.

Required operations:
- pan/zoom/minimap
- multi-select
- drag/drop
- group/subgraph/scene
- pin/unpin
- expand neighbours
- collapse branch
- pivot by node type/relation
- filter by role/status/source/time/confidence
- search by ID/text/source
- context menu actions
- compare two nodes or source revisions
- open source/evidence side panel
- open trace side panel
- open product lineage panel
- save workspace layout
- export selected subgraph
- generate report/product from selected subgraph

Node visual semantics:
- type
- lifecycle state
- evidence state
- review state
- source authority/currentness where applicable
- contradiction state
- role relevance
- product usage count

Edge visual semantics:
- direct vs inferred
- evidence-backed vs candidate
- active vs superseded
- relation type
- confidence/profile

## 7. Canonical graph entities

Core:
`SOURCE_DOCUMENT, SOURCE_FRAGMENT, TRANSLATION_FRAGMENT, ENTITY, CLAIM, KNOWLEDGE_NODE, KNOWLEDGE_EDGE, EVIDENCE_LINK, SCORE_VECTOR, REVIEW, ROLE_VIEW, PROCESSING_RUN, TRACE_EVENT, ENTITY_TRACE_LINK, CASE, DECISION, PRODUCT, PRODUCT_ARTIFACT, LESSON`

Mandatory logical IDs:
`DOC-, FRG-, TRN-, ENT-, CLM-, KN-, EDGE-, EVD-, SCORE-, REV-, VIEW-, RUN-, TRACE-, CASE-, DEC-, PROD-, ART-, LES-`.

IDs survive export/import and renderer/database migration.

## 8. Data separation

Strict layers:
1. ORIGINAL
2. EXTRACTED_NATIVE
3. OCR
4. TRANSLATION
5. CLAIM/ENTITY EXTRACTION
6. INTERPRETATION
7. VERIFIED KNOWLEDGE
8. DECISION
9. PRODUCT
10. OUTCOME/LESSON

No layer silently overwrites another.

## 9. API-first contract

Every material subsystem exposes explicit operations. M1 may implement several contracts inside one deployable monolith, but boundaries remain logical and OpenAPI/event-schema documented.

Minimum logical APIs:
- Source API
- Ingestion API
- Extraction/OCR API
- Translation API
- Evidence API
- Knowledge Graph API
- Search/Retrieval API
- Review/Promotion API
- Role Perspective API
- Case API
- Product API
- Trace/Observability API
- Architecture Studio API
- Model Gateway API

Cross-cutting headers/context:
- request_id
- trace_id
- actor_id/service_id
- project_id/workspace_id
- schema_version
- idempotency_key for writes

Every response returns trace_id and machine-readable error code.

## 10. Trace-first policy

Every executed material stage emits:
- START
- terminal event: SUCCESS / FAILED / BLOCKED / SKIPPED / CANCELLED

Required dimensions:
`trace_id, span_id, parent_span_id, run_id, service, operation, API route/event, entity_type, entity_id, worker_id, model_id, prompt/profile version, start/end, elapsed_ms, retry_count, input/output hashes where safe, status, error_type, error_code, error_message`.

No secrets/full copyrighted payloads in public/log sinks.

UI requirements:
- trace timeline per entity
- distributed call tree
- filter by service/stage/error/model
- link span -> entity -> source/product
- one-click copy trace_id

## 11. Microservice decision rule

Do not split simply because a component exists on C4.

Create a separate service only when at least one material reason exists:
1. independent scaling profile
2. GPU/runtime isolation
3. trust/security boundary
4. independent release lifecycle
5. fault isolation
6. separate data ownership
7. high concurrency/background queue
8. external integration boundary

Likely service candidates after PoC telemetry:
- Document/OCR workers
- Translation/Model Gateway
- Trace/Telemetry collector
- Review/Promotion service
- Graph/query API

M1 recommended deployable shape: modular monolith + isolated GPU/model workers + queue-ready contracts.

## 12. Architecture Studio / C4 requirements

The site must itself become a graphical architecture workspace.

Supported views:
- C1 System Context
- C2 Containers
- C3 Components
- Sequence
- Data Flow
- Trust Boundaries
- Deployment view later
- Requirements traceability overlay
- Risk overlay
- API overlay
- Runtime trace overlay

Each architecture element has:
- stable ID
- owner
- responsibility
- linked FR/NFR
- linked ADR
- linked API operations
- linked data entities
- linked tests
- linked runtime services/traces

Clicking a C4 node opens a detail inspector.

## 13. Requirement-to-code traceability

Mandatory chain:
`PRODUCT_GOAL -> FR/NFR -> USE_CASE -> C4_CONTAINER -> C3_COMPONENT -> API_OPERATION/EVENT -> DATA_SCHEMA -> CODE_MODULE -> TEST -> TRACE_STAGE -> RELEASE -> PRODUCT_OUTCOME`

No production feature is accepted if the chain is broken for Must requirements.

## 14. Analytical diagrams required at each stage

### Product/Discovery
- stakeholder map
- context diagram
- value stream
- current vs target process
- scope map

### Analysis
- use-case map
- BPMN-like process/flow
- state machine
- domain/entity model
- data lineage
- requirement traceability matrix
- risk heatmap/register

### Architecture
- C1/C2/C3
- sequence diagrams
- trust boundaries
- data-flow diagrams
- deployment assumptions
- API map
- ADR map

### Development
- module/dependency map
- DB schema/ERD
- event/API contracts
- test pyramid/matrix
- trace topology

### Operations
- service dependency map
- SLI/SLO dashboard
- failure tree
- incident timeline
- change/deployment lineage

All diagrams are linked to canonical IDs, not decorative screenshots.

## 15. UX layout baseline

Desktop-first professional workstation, optimized for 1440p+ but responsive.

Top navigation:
`Investigate | Lineage | Perspectives | Cases | Sources | Products | Architecture | Trace`

Default Investigate layout:
- left: filters, node palette, saved searches/actions
- center: graph canvas
- right: entity/evidence/review inspector
- bottom: timeline/trace/events drawer
- top contextual toolbar: workspace, role, status, layout, save/export/productize

Architecture Studio layout:
- left: C4/component/data palette
- center: editable canvas
- right: properties/requirements/API/ADR inspector
- bottom: traceability and validation problems

## 16. Visual design direction

Professional investigation/engineering environment.
- light/dark themes
- high information density without visual noise
- restrained semantic color system
- status always encoded by icon/text in addition to color
- readable edge labels
- keyboard shortcuts
- accessibility WCAG AA target
- no decorative gradients that reduce data readability

## 17. Figma as design source of truth

Create one long-lived Figma design file with pages:
1. `00 Product Map`
2. `01 Foundations & Tokens`
3. `02 Components`
4. `03 Investigate Workspace`
5. `04 Lineage`
6. `05 Perspectives`
7. `06 Cases`
8. `07 Sources`
9. `08 Products`
10. `09 Architecture Studio`
11. `10 Trace & Observability`
12. `11 Responsive States`
13. `12 Prototypes`
14. `13 Deprecated / Archive`

Design system requirements:
- variables/tokens for color, spacing, typography, radius, elevation, semantic statuses
- components with variants
- component descriptions
- stable naming
- Code Connect where implementation stabilizes
- no hardcoded one-off copies when reusable component exists

## 18. Core reusable UI components

- App Shell
- Top Nav
- Left Toolrail
- Graph Canvas shell
- Node Card
- Edge Label
- Inspector Panel
- Evidence Card
- Source Card
- Trace Span Row
- Trace Tree
- Status Badge
- Role/Perspective selector
- Filter Builder
- Search Box
- Timeline
- Case Card
- Product Card
- C4 Element
- Requirement Chip
- API Operation Chip
- ADR Card
- Validation Problem Row
- Data Table
- Command Palette
- Context Menu

## 19. Technology baseline

Frontend:
- React / Next.js
- TypeScript strict
- graph renderer abstraction; evaluate React Flow vs Cytoscape.js, keep adapter boundary
- TanStack Table for dense tables
- Mermaid/Structurizr import/export for architecture diagrams, but canonical editable model remains internal graph

Backend:
- FastAPI / Python 3.12
- OpenAPI 3.1
- SQLite M1; PostgreSQL later
- background worker interface
- JSONL portable exports

Graph/search:
- relational canonical graph first
- optional pgvector/Qdrant index for retrieval
- renderer/search indexes are projections, not truth store

Observability:
- internal trace schema compatible in spirit with OpenTelemetry concepts
- JSONL + SQLite M1 sink
- future OTLP/export adapter

## 20. Developer class / staffing requirements

This is not a junior CRUD project.

Mandatory core roles:
- Lead/Senior Product Manager: requirements, value gates, roadmap, change control
- Lead System Analyst: domain model, FR/NFR, states, contracts, traceability
- Senior/Staff Architect: C4, ADRs, API/service boundaries, NFR trade-offs
- Senior Frontend Engineer: complex graph editor, performance, state architecture, accessibility
- Senior Backend Engineer: APIs, transactions, idempotency, migrations, tracing
- Senior Data/ML Engineer: OCR/model/retrieval pipelines, reproducibility
- Senior UX/Product Designer: investigation UX, graph interaction, dense professional UI
- QA Automation Engineer: contract/integration/regression/golden-path tests
- DevOps/SRE later: deployments, observability, reliability
- Security Engineer review at trust-boundary and production gates

Junior/middle developers may implement bounded tasks only under approved contracts and senior review.

## 21. Engineering standards

- Type hints / strict typing
- schema-first contracts
- migrations only, no ad-hoc DB edits
- parameterized SQL
- idempotent writes
- explicit error taxonomy
- append-only review/audit history
- deterministic validators before LLM judges
- no silent retry that hides failure
- feature flags for experimental UX/AI
- backward-compatible API versioning policy
- security review for untrusted document/model content

## 22. Testing strategy

MIN:
- component/unit tests
- schema validation
- API contract tests
- DB integrity

MED:
- end-to-end golden fixture
- trace traversal
- graph/source/product lineage
- role perspective invariants
- unsupported claim blocked

MAX:
- representative PDF/scan/mixed corpus
- performance profiling
- large graph UI responsiveness
- interruption/resume
- version migration/roundtrip
- security negative cases

## 23. Performance targets — initially hypotheses, must be measured

Do not invent final SLOs before profiling.

Must instrument:
- graph node/edge counts
- initial render latency
- interaction latency
- query latency p50/p95
- source/evidence retrieval latency
- OCR/translation throughput
- model latency
- rework rate
- memory/VRAM usage

Architecture choices are revisited after measured bottlenecks.

## 24. Security and data governance

- untrusted file ingestion sandbox boundary
- file type/size validation
- content classification/use-policy gate
- secret/PDn scanning before public export
- RBAC later by project/case/role
- immutable source identity
- signed/hashable export manifests later
- no LLM output treated as authoritative evidence

## 25. Productization model

A selected evidence-backed subgraph can be converted into:
- report
- dossier
- ADR
- checklist
- recommendation
- requirement/control matrix
- knowledge pack for an agent

Every generated product stores `DERIVED_FROM` links to all contributing knowledge/evidence and its generation/review trace.

## 26. Long-term extensibility

Planned compatible expansions:
- OSINT connectors
- regulatory digital twin
- Narrative Drift / media manipulation analysis
- multi-agent research workflows
- external graph DB
- collaborative multi-user editing
- plugin/transform SDK
- case automation
- enterprise SSO/RBAC
- versioned knowledge publishing
- evaluation/experimentation platform

Extensions must use public/internal versioned contracts rather than direct DB coupling.

## 27. Delivery phases

### Phase 0 — specification/design baseline
Product map, domain model, UX map, C4, API map, Figma design system.

### Phase 1 — Visual Workspace skeleton
App shell, graph canvas, inspector, source/evidence cards, mock API, trace panel.

### Phase 2 — Canonical backend connection
Real source/knowledge/trace APIs, SQLite DB, lineage.

### Phase 3 — Investigation workflows
Pivot/expand, cases, review, perspectives, productization.

### Phase 4 — Architecture Studio
Editable C4, requirement/API/ADR links, validation.

### Phase 5 — production hardening
Auth/RBAC, performance, SLO, backup/DR, audit/export, security.

## 28. Gate model

G0 Product scope
G1 Analytical contracts
G2 Architecture/C4/API contracts
G3 Figma UX/design system baseline
G4 Implementation skeleton
G5 Golden path
G6 Real-document PoC
G7 MVP user workflow
G8 Pilot
G9 Production readiness

No gate is closed by screenshots alone; each has machine-readable acceptance evidence.

## 29. Immediate acceptance criteria for this specification

This TZ is accepted for downstream architecture/design work when:
- mission and scope are understood
- API-first and trace-first are mandatory
- microservice split criteria are explicit
- graph editor and Architecture Studio are first-class product capabilities
- Figma file/page structure is defined
- developer seniority/roles are defined
- end-to-end traceability chain is defined
- delivery phases/gates are defined

## 30. Next artifacts

1. `DOMAIN_MODEL_AND_ID_MAP.md`
2. `UX_INFORMATION_ARCHITECTURE.md`
3. `C4_AND_SERVICE_BOUNDARIES.md`
4. `API_CATALOG_V1.yaml`
5. `TRACE_CONTRACT_V1.md`
6. `FIGMA_STRUCTURE_AND_DESIGN_SYSTEM.md`
7. `DEVELOPMENT_WORK_BREAKDOWN.md`
8. `ACCEPTANCE_MATRIX.md`
