# FATHER Knowledge Factory — Senior Implementation Plan

Document ID: `FATHER-KF-IMPL-0001`
Package: `PACKAGE_01_FOUNDATION`
Status: `ACTIVE_DEVELOPMENT`
Owner: `FATHER Senior Engineering`
Upstream: `01_PRODUCT_DOCUMENT.md`, `02_ANALYTICS_STAGE_01.md`, `02_ANALYTICS_STAGE_02_DISCOVERY_DELIVERY.md`, `03_ARCHITECTURE.md`

## 1. Development rule

Implementation may now proceed only against approved/drafted contracts with preserved traceability:

`FR/NFR -> C2 Container -> C3 Component -> API/Data Contract -> Code Module -> Test -> Trace Span -> Acceptance Gate`.

No stream may silently redefine a requirement, entity, status, edge type, review verdict or trace contract.

## 2. Parallel development streams

### S1 — Canonical DB, IDs, migrations and tracing

Branch: `agent/father-kf-s1-db-tracing`
Issue: `#41`

Code ownership:
- `father/agent-factory/knowledge/schema/`
- `scripts/init_father_knowledge_db.py`
- `scripts/father_trace.py`
- DB bootstrap/migrations/integrity helpers
- tests for FK/idempotency/trace traversal

Immediate backlog:
1. make schema versioning explicit;
2. make repeated bootstrap idempotent;
3. finish `trace_events` + `entity_trace_links` persistence;
4. add deterministic logical-ID strategy contract;
5. add reverse traversal query from KN to DOC/source SHA;
6. add negative fixture for orphan evidence;
7. add MIN gate runner.

Exit gate: `DB_MIN_GREEN`.

### S2 — Ingest, PDF classification, OCR, translation and evidence

Branch: `agent/father-kf-s2-ingest-ocr-translation`
Issue: `#42`

Code ownership:
- document ingest adapters;
- PDF native/scanned/mixed classifier;
- page/block locator extraction;
- OCR adapter/fallback;
- Translation Factory bridge;
- evidence package builder;
- source/fragment/translation SHA provenance.

Immediate backlog:
1. introduce page-level PDF classifier;
2. native text first, OCR only when needed;
3. preserve page/section/block/bbox/ordinal locators;
4. persist ORIGINAL / EXTRACTED / TRANSLATION separately;
5. connect model-zoo translator/reviewer outputs to canonical DB;
6. emit spans `INGEST/PDF_CLASSIFY/EXTRACT/OCR/CHUNK/TRANSLATE/REVIEW/QA/EVIDENCE_BUILD/DB_WRITE`;
7. add short EN fixture golden path.

Exit gate: `INGEST_MED_GREEN`.

### S3 — Knowledge extraction, graph, contradictions, scores and role views

Branch: `agent/father-kf-s3-graph-roleviews`
Issue: `#43`

Code ownership:
- atomic knowledge candidate schema;
- canonical node/edge services;
- normalization/dedup candidates;
- contradiction preservation;
- score-vector computation;
- role projections.

Immediate backlog:
1. define strict machine-readable candidate contract;
2. create node/edge repository service;
3. implement `SAME_AS` as candidate, never auto-merge by embedding alone;
4. implement explicit `CONTRADICTS` relation;
5. store component scores separately;
6. generate six role views from one node identity;
7. emit spans `KNOWLEDGE_EXTRACT/NORMALIZE/DEDUP_CHECK/NODE/EDGE/CONTRADICTION/SCORE/ROLE_PROJECT/GRAPH_INTEGRITY`.

Exit gate: `GRAPH_MED_GREEN`.

### S4 — Deterministic QA, model/Chief Analyst review, KB_READY and round-trip

Branch: `agent/father-kf-s4-review-export`
Issue: `#44`

Code ownership:
- evidence package validation;
- review lifecycle;
- promotion rules;
- JSONL export/import;
- machine-readable failure reports;
- regression fixtures.

Immediate backlog:
1. implement deterministic pre-review validators;
2. enforce verdicts `APPROVE/REVISE/REJECT/ESCALATE`;
3. enforce `KB_READY = evidence + source resolvable + QA + approved review`;
4. add unsupported-claim negative fixture;
5. add model/reviewer/prompt/input-revision provenance;
6. implement deterministic JSONL export/import round-trip;
7. emit spans `EVIDENCE_PACKAGE/DETERMINISTIC_QA/MODEL_REVIEW/CHIEF_ANALYST_REVIEW/PROMOTION/EXPORT/ROUND_TRIP_VERIFY`.

Exit gate: `REVIEW_MED_GREEN`.

## 3. Shared contracts

All streams must preserve:
- `trace_id`, `span_id`, `parent_span_id`, `run_id`, `stream_id`, `worker_id`;
- stable entity prefixes `DOC/FRG/TRN/KN/EDGE/EVD/REV/SCORE/VIEW/RUN`;
- immutable source SHA-256;
- separation of source, OCR/extracted, translation, interpretation and knowledge;
- append-only review history;
- explicit failures; retries never erase the original failure event.

## 4. Integration order

Streams develop in parallel, but integration follows:

`S1 contracts -> S2 evidence path -> S3 graph path -> S4 review/promotion -> end-to-end golden path`.

S2/S3/S4 may develop against fixtures/mocks before S1 merge, but cannot change shared schema independently.

## 5. Required tests

MIN:
- fresh DB bootstrap;
- FK/quick_check;
- trace START + terminal pairs;
- reverse entity traversal;
- no orphan evidence.

MED:
- short EN fixture -> translation -> evidence -> node -> role views -> review -> KB_READY;
- unsupported claim blocked;
- repeated run does not duplicate canonical records;
- trace traversal across all four streams.

MAX:
- one real technical PDF classified native/scanned/mixed;
- OCR only where required;
- multiple nodes + one edge + one contradiction fixture;
- JSONL export/import round-trip retains logical IDs and provenance.

## 6. Production telemetry

Each stream records actual only:
- items_total / processed / accepted / rejected;
- rework;
- errors by stage;
- elapsed_seconds;
- throughput;
- model/runtime profile;
- worker_count.

Speed-up versus one stream, remaining volume and ETA remain `N/A` until comparable telemetry exists.

## 7. Definition of Done for Development Sprint 01

Sprint 01 is complete when all four stream exit gates are green and one short English fixture can be followed end-to-end through one `trace_id` from source ingest to `KB_READY`, with every entity linked to its creating span and exact source evidence recoverable.