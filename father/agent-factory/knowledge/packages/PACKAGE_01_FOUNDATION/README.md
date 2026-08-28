# PACKAGE 01 — FATHER Knowledge Factory Foundation

Status: ACTIVE_DEVELOPMENT

Execution order is strict:

1. `01_PRODUCT_DOCUMENT.md` — Product/Owner view: problem, users, value, scope, outcomes, constraints, acceptance.
2. `02_ANALYTICS_STAGE_01.md` — Analyst view: users/owners, scope, FR/NFR, constraints, success criteria and initial traceability.
3. `02_ANALYTICS_STAGE_02_DISCOVERY_DELIVERY.md` — Discovery, corpus profiling, golden set, baseline, PERT/range estimation, risk register, value roadmap, delivery gates and architecture handoff.
4. `03_ARCHITECTURE.md` — Architect view: C1/C2/C3, HLD/LLD, data architecture, interfaces, storage, trust boundaries, tracing, failure isolation, security, deployment and ADRs.
5. `04_SENIOR_IMPLEMENTATION_PLAN.md` — four-stream senior implementation plan and integration gates.
6. `DEVELOPMENT_SPRINT_01.yaml` — machine-readable active development registry.

Rules:
- each next document must reference and not silently contradict previous approved documents;
- unresolved contradictions are recorded explicitly;
- implementation is not allowed to invent requirements absent from Product/Analytics/Architecture contracts;
- all runtime stages must remain traceable end-to-end;
- product truth, source evidence, translation, interpretation and role projections remain separate;
- exact schedules/budgets/acceleration are not stated before profiling and measured telemetry;
- bulk library processing remains blocked until MIN/MED golden-path gates are green.

Current gate: `P01-G4 SENIOR_IMPLEMENTATION_ACTIVE`.
Architecture handoff: `ACCEPTED_FOR_DEVELOPMENT_WITH_OPEN_ASSUMPTIONS`.
Development sprint: `FATHER-KF-SPRINT-01`.

Active branches:
- S1: `agent/father-kf-s1-db-tracing`;
- S2: `agent/father-kf-s2-ingest-ocr-translation`;
- S3: `agent/father-kf-s3-graph-roleviews`;
- S4: `agent/father-kf-s4-review-export`.

Integration order: `S1 contracts -> S2 evidence -> S3 graph -> S4 review/promotion -> short EN golden path -> real PDF MAX gate`.
