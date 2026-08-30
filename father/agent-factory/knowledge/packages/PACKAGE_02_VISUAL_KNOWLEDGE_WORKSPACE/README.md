# FATHER Visual Knowledge Workspace

> Professional evidence-driven investigation, architecture and productization workspace for FATHER.

**Status:** `ACTIVE_SPECIFICATION_AND_DESIGN`

**Product lifetime:** multi-year

**Primary goal:** turn raw source information into traceable knowledge, decisions and reusable products while preserving the complete path back to evidence.

**Figma master file:** https://www.figma.com/design/jxY8XAblIEbEFMnjBv23oK

## North Star

```text
SOURCE
  -> EXTRACT / OCR
  -> TRANSLATION
  -> CLAIM / ENTITY
  -> EVIDENCE
  -> KNOWLEDGE NODE / EDGE
  -> REVIEW
  -> ROLE VIEW
  -> DECISION
  -> PRODUCT
  -> OUTCOME
  -> LESSON
```

Every material transition is:

- API-addressable;
- traceable by `trace_id/span_id`;
- linked to stable logical IDs;
- visible in the workspace;
- reviewable and reproducible.

## Product modes

| Mode | Purpose |
|---|---|
| **Investigate** | OSINT-style graph research, pivot, expand, filter and compare |
| **Lineage** | Source-to-product and product-to-source provenance |
| **Perspectives** | Architect / Programmer / Security / Lawyer / Manager / Product views over one canonical graph |
| **Cases** | Investigation queue, owner, state, review and history |
| **Sources** | Original file registry, hashes, versions, OCR/translation state and downstream usage |
| **Products** | Reports, ADRs, dossiers, checklists, recommendations and agent knowledge packs |
| **Trace** | Runtime call tree, spans, API operations, models, errors and latency |
| **Architecture Studio** | Editable C4/C1/C2/C3, sequence, data-flow, trust-boundary and API/ADR overlays |

## Project documentation

### Baseline specification
- [MASTER_TZ_V1.md](MASTER_TZ_V1.md) — senior PM + lead analyst master technical specification.
- [COMPETITOR_BENCHMARK_AND_UX_PATTERNS.md](../PACKAGE_01_FOUNDATION/COMPETITOR_BENCHMARK_AND_UX_PATTERNS.md) — patterns inspired by Maltego, OpenCTI, Palantir, Neo4j Bloom, Linkurious, Graphistry and NotebookLM.
- [API_TRACE_MICROSERVICE_POLICY.md](../PACKAGE_01_FOUNDATION/API_TRACE_MICROSERVICE_POLICY.md) — API-first, trace-first and microservice split rules.

### Project governance
- [PROJECT_STATUS_REPORT.md](PROJECT_STATUS_REPORT.md) — current executive/project report.
- [DECISION_LOG.md](DECISION_LOG.md) — important product/architecture decisions and rationale.
- [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md) — append-oriented project history.

## Delivery gates

| Gate | Meaning | Status |
|---|---|---|
| G0 | Product scope | ✅ BASELINED |
| G1 | Analytical contracts | ✅ BASELINED |
| G2 | Architecture / C4 / API contracts | 🟡 IN PROGRESS |
| G3 | Figma UX + design-system baseline | 🟡 STARTED |
| G4 | Implementation skeleton | ⬜ |
| G5 | Golden path | ⬜ |
| G6 | Real-document PoC | ⬜ |
| G7 | MVP workflow | ⬜ |
| G8 | Pilot | ⬜ |
| G9 | Production readiness | ⬜ |

## Development standard

This is not treated as a junior CRUD application. Core architecture and complex editor/runtime work require senior-level ownership.

Minimum senior owners:
- Senior/Lead Product Manager;
- Lead System Analyst;
- Senior/Staff Architect;
- Senior Frontend Engineer;
- Senior Backend Engineer;
- Senior Data/ML Engineer;
- Senior UX/Product Designer;
- QA Automation Engineer;
- Security Engineer review;
- DevOps/SRE for production stages.

Junior/middle contributors may implement bounded tasks only against approved contracts and with senior review.

## API-first rule

Every material capability has a documented API/event contract even when M1 is deployed as a modular monolith.

Logical API domains:

`Source | Ingestion | OCR | Translation | Evidence | Knowledge Graph | Search | Review | Perspectives | Cases | Products | Trace | Architecture Studio | Model Gateway`

Every material response propagates `trace_id` and every material write supports stable IDs and idempotency where applicable.

## Trace-first rule

Every material stage emits a `START` event and exactly one terminal state:

`SUCCESS | FAILED | BLOCKED | SKIPPED | CANCELLED`

The UI must allow traversal:

`PRODUCT -> DECISION -> KNOWLEDGE -> EVIDENCE -> FRAGMENT -> SOURCE -> PROCESSING SPAN -> API / WORKER / MODEL`

and the reverse path.

## Figma structure

The master design file is planned as a long-lived product system with pages:

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

## Immediate next work

1. Domain model + ID map.
2. UX information architecture.
3. C4 and service-boundary map.
4. API catalog v1.
5. Trace contract v1.
6. Figma foundations and product map.
7. Work breakdown and acceptance matrix.
8. First editable Investigate Workspace prototype.

## Principle of change

A future implementation may replace React Flow with Cytoscape, SQLite with PostgreSQL, local inference with another model gateway, or introduce services — but it must not break canonical IDs, source/evidence lineage, API semantics or traceability.
