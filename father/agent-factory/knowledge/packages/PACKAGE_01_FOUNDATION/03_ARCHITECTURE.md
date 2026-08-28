# FATHER Knowledge Factory — Architecture Package 01

Document ID: `FATHER-KF-ARCH-0001`
Package: `PACKAGE_01_FOUNDATION`
Status: `DRAFT_FOR_REVIEW`
Owner: `FATHER Architect`
Upstream: `01_PRODUCT_DOCUMENT.md`, `02_ANALYTICS_STAGE_01.md`, `02_ANALYTICS_STAGE_02_DISCOVERY_DELIVERY.md`

## 1. Архитектурный принцип

Используем C4-абстракции последовательно: Software System -> Containers -> Components -> Code. Контейнер в C4 означает приложение или хранилище данных, а не Docker-контейнер.

Архитектура должна обеспечивать доказательную цепочку:

`SOURCE_DOCUMENT -> SOURCE_FRAGMENT -> TRANSLATION_FRAGMENT -> KNOWLEDGE_NODE -> KNOWLEDGE_EDGE -> EVIDENCE_LINK -> REVIEW -> ROLE_VIEW -> KB_READY`

Ни один AI-компонент не имеет права присвоить `KB_READY` без evidence/review gate.

## 2. C1 — System Context

Акторы:
- Analyst — задаёт исследовательский запрос, проверяет claims и evidence;
- Chief Analyst / Reviewer — рассматривает спорные случаи;
- Architect / Software Engineer / Security / Lawyer / Manager / Product — потребляют role-specific views одного канонического графа.

Система:
- `FATHER Knowledge Factory / Research Graph` — принимает разрешённые документы, сохраняет оригиналы, извлекает/переводит фрагменты, строит evidence-backed knowledge graph и выдаёт проверяемые рекомендации.

Внешние зависимости:
- Local/approved LLM Endpoint;
- optional external identity/source registries;
- local filesystem/object storage for originals.

## 3. C2 — Container architecture

Обязательные контейнеры домашнего задания:

| Container | Technology | Responsibility | Primary requirements |
|---|---|---|---|
| Frontend | Next.js/React | Workspace аналитика, evidence panel, graph/review UI | FR-004, FR-005, FR-006 |
| Backend API | FastAPI | Sessions/projects, auth facade, orchestration facade | FR-004, FR-006, NFR-006 |
| AI / Evidence Service | Python | RAG, evidence retrieval, prompt/model routing, claim/citation validation | FR-002, FR-003, FR-009, FR-010 |
| Vector DB | pgvector/Qdrant | Semantic retrieval over fragments/embeddings | FR-002, FR-005 |
| SQL DB | SQLite M1 -> PostgreSQL later | Canonical documents/fragments/nodes/edges/reviews/traces | FR-003..FR-012 |

Additional containers required by the product contract:

| Container | Responsibility |
|---|---|
| Original Store | Immutable originals + revisions + SHA-256 |
| Document Pipeline | Native extraction/OCR/structure/chunking |
| Translation Service | EN->RU translation + glossary + reviewer provenance |
| Review/Promotion Service | APPROVE/REVISE/REJECT/ESCALATE and KB_READY gate |
| Trace/Audit Store | trace_id/span_id/entity links, errors, latency |
| LLM Endpoint | Local or approved external inference |

## 4. Trust boundaries

TB-01 User boundary: Frontend never writes canonical evidence directly.
TB-02 Backend-to-AI boundary: authenticated/internal request with `request_id` and `trace_id`.
TB-03 AI/model boundary: model output is untrusted candidate data until citation/evidence validation.
TB-04 Original boundary: source originals are immutable; OCR/translation are derivative layers.
TB-05 Promotion boundary: only Review/Promotion Service may move candidate knowledge to `KB_READY`.
TB-06 Public/local boundary: copyrighted originals/translations remain local and never enter public Git history.

## 5. C3 — AI / Evidence Service

Components:

1. `Recommendation Controller` — receives `/get_recommendation`, creates/propagates request/trace context and coordinates scenario.
2. `Policy Guard` — validates project scope, role, source policy and request constraints.
3. `RAG Manager` — performs retrieval and context assembly.
4. `Evidence Retriever` — resolves exact fragment text, locator, SHA and version from canonical stores.
5. `Prompt Template Factory` — builds versioned evidence-first prompts.
6. `LLM Client` — one adapter for local/approved external models.
7. `Citation Validator` — checks claims against evidence and source locators.
8. `Knowledge Projector` — maps approved/candidate knowledge into role views without cloning canonical nodes.
9. `Audit Emitter` — emits START/terminal spans, latency, model/profile version and outcome.

Rules:
- C3 component names are reused unchanged in Sequence/API documentation;
- `LLM Client` cannot bypass `Citation Validator`;
- `Citation Validator` cannot promote `KB_READY`; it only produces validation outcome;
- `Audit Emitter` never logs secrets/full copyrighted payloads.

## 6. Sequence — User requests recommendation

Main path:

1. Analyst -> Frontend: question + project_id.
2. Frontend -> Backend API: `POST /projects/{id}/recommendations`.
3. Backend API -> Recommendation Controller: `POST /get_recommendation`.
4. Controller -> Policy Guard: validate role/scope/request.
5. Controller -> RAG Manager: retrieval request.
6. RAG Manager -> Vector DB: semantic search.
7. RAG Manager -> Evidence Retriever: resolve exact fragments/locators/hashes.
8. RAG Manager -> Prompt Template Factory: build versioned prompt.
9. RAG Manager -> LLM Client: generate recommendation + claim candidates.
10. Controller -> Citation Validator: verify claims against evidence.
11. Controller -> Knowledge Projector: apply role view/relevance.
12. Controller -> Audit Emitter: record trace/outcome.
13. Controller -> Backend -> Frontend: recommendation + citations + warnings + review status.

Failure paths:
- policy fail -> HTTP 403/422;
- no admissible evidence -> 200 with `status=INSUFFICIENT_EVIDENCE`, no fabricated recommendation;
- model unavailable -> 503 with trace_id;
- citation mismatch -> recommendation returned as `REVIEW_REQUIRED`, not verified.

## 7. API boundary

Backend-to-AI integration contract is `POST /get_recommendation`.

Request carries:
- request_id;
- trace_id;
- project_id;
- question;
- role;
- retrieval filters/top_k;
- requested language.

Response carries:
- recommendation_id;
- status;
- answer;
- claim candidates;
- citations with `document_id`, `fragment_id`, locator and SHA;
- warnings;
- model/profile metadata safe for audit;
- trace_id.

Canonical OpenAPI file: `api/openapi.yaml`.

## 8. Data/storage decisions

ADR-001: SQLite is canonical M1 store because local-first M1 needs transactions/FK/replay without distributed infrastructure.
ADR-002: Vector DB is retrieval index only, not source of truth.
ADR-003: Original Store is immutable evidence store; derived OCR/translation never overwrite it.
ADR-004: one canonical knowledge node + role projections; no per-role copies.
ADR-005: model consensus is not evidence; source-backed review is required.

## 9. Traceability matrix

| Requirement | Container | C3/Mechanism | Verification |
|---|---|---|---|
| FR-001 | Original Store / Document Pipeline | source identity + SHA | source hash test |
| FR-002 | Document Pipeline / AI Service | extraction/chunk pipeline | golden fixture |
| FR-003 | SQL DB / Evidence Retriever | evidence_links + exact locator | reverse traversal test |
| FR-004 | Frontend / Review Service | review lifecycle | approval audit test |
| FR-005 | SQL DB / Graph API | nodes + typed edges | graph integrity test |
| FR-006 | Backend / Report Builder | evidence-backed report | reproducibility test |
| FR-007 | Original Store / Version Comparator | revision chain/diff | version fixture |
| FR-008 | stores/data model | layer separation | schema constraints |
| FR-009 | Trace Store / Audit Emitter | trace_id/span hierarchy | trace traversal test |
| FR-010 | Review/Promotion Service | promotion gate | unsupported claim negative test |
| FR-011 | SQL DB / Knowledge Projector | role_views | same-node multi-role test |
| FR-012 | SQL DB / Graph Builder | CONTRADICTS edge | contradiction fixture |

## 10. HLD -> LLD handoff

HLD artifacts:
- C2 container diagram;
- trust boundaries;
- data flow;
- container responsibilities;
- ADR-001..005.

LLD artifacts:
- C3 AI/Evidence Service;
- sequence `/get_recommendation`;
- OpenAPI 3.1;
- entity/data contracts;
- trace propagation contract;
- negative/error scenarios;
- test mapping.

## 11. Architecture gate

`P01-G3 ARCHITECTURE_DRAFTED` is green when:
- C2 contains Frontend, Backend, AI Service, Vector DB, SQL DB;
- C3 expands AI Service with named components;
- Sequence uses only containers/components defined in C2/C3;
- `/get_recommendation` exists in OpenAPI;
- FR-001..FR-012 map to architecture responsibility;
- trust boundaries and failure paths are explicit;
- tracing propagates through Backend -> AI -> model/evidence calls;
- no architecture decision silently violates product/analytics constraints.
