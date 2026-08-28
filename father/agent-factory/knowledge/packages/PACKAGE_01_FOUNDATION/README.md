# PACKAGE 01 — FATHER Knowledge Factory Foundation

Status: IN_PROGRESS

Execution order is strict:

1. `01_PRODUCT_DOCUMENT.md` — Product/Owner view: problem, users, value, scope, outcomes, constraints, acceptance.
2. `02_ANALYTICS_STAGE_01.md` — Analyst view: users/owners, scope, FR/NFR, constraints, success criteria and initial traceability.
3. `02_ANALYTICS_STAGE_02_DISCOVERY_DELIVERY.md` — Discovery, corpus profiling, golden set, baseline, PERT/range estimation, risk register, value roadmap, delivery gates and architecture handoff.
4. `03_ARCHITECTURE.md` — Architect view: C1/C2/C3, HLD/LLD, data architecture, interfaces, storage, trust boundaries, tracing, failure isolation, security, deployment and ADRs.
5. `HOMEWORK_C4_API.md` + `diagrams/*` + `api/openapi.yaml` + `structurizr/workspace.dsl` — согласованный учебный/интеграционный пакет C4 -> Sequence -> OpenAPI.
6. Only after Product + Analytics + Architecture are reviewed: senior implementation plan, code, tests and production telemetry.

Rules:
- each next document must reference and not silently contradict previous approved documents;
- unresolved contradictions are recorded explicitly;
- implementation is not allowed to invent requirements absent from Product/Analytics/Architecture contracts;
- all runtime stages must remain traceable end-to-end;
- product truth, source evidence, translation, interpretation and role projections remain separate;
- exact schedules/budgets/acceleration are not stated before profiling and measured telemetry.

Current gate: `P01-G3 ARCHITECTURE_DRAFTED`.
Architecture handoff: `READY_FOR_REVIEW`.
Next gate: `P01-G4 SENIOR_IMPLEMENTATION_PLAN` after architecture review.

Architecture artifacts:
- `03_ARCHITECTURE.md`;
- `diagrams/c2-containers.mmd`;
- `diagrams/c3-ai-evidence-service.mmd`;
- `diagrams/sequence-get-recommendation.mmd`;
- `api/openapi.yaml`;
- `structurizr/workspace.dsl`;
- `HOMEWORK_C4_API.md`.

Open assumptions from analytics must remain explicit assumptions/ADRs and must not become hidden implementation choices.
