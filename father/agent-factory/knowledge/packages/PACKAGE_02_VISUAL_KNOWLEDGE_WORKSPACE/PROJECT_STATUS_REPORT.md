# FATHER Visual Knowledge Workspace — Project Status Report

Report ID: `FATHER-VKW-REPORT-0001`
Date: 2026-08-30
Status: `ACTIVE_SPECIFICATION_AND_DESIGN`

## Executive summary

The project has moved from concept discussion to governed product development. Product, analytical and initial architecture rules are established. A master long-term technical specification has been created. API-first and trace-first are mandatory. A dedicated Figma master file has been created for long-lived product design.

The immediate objective is not bulk document processing. It is to establish the visual workspace, domain contracts, API catalog and trace model so future implementation remains coherent and maintainable.

## What exists now

### Product / analysis
- Product mission and role model defined.
- FR/NFR baseline defined in Package 01.
- Discovery, corpus profiling, golden set, baseline and risk approach defined.
- Product-to-architecture traceability established.

### Architecture
- C4/HLD/LLD baseline exists.
- C2 mandatory containers defined.
- AI/Evidence C3 components defined.
- `/get_recommendation` integration contract exists.
- API-first + trace-first policy is explicit.
- Microservice split is evidence-based, not default.

### Knowledge/data foundation
- canonical source/fragment/translation/knowledge/evidence/review/role-view model exists;
- SQLite M1 schema exists;
- trace event model exists;
- stable logical IDs are a hard requirement.

### Visual product direction
- OSINT-style graph editor is a first-class product capability;
- lineage, perspectives, cases, sources, products, trace and Architecture Studio are defined as product modes;
- competitor UX patterns have been benchmarked and converted into product backlog items.

### Figma
Master file created:
https://www.figma.com/design/jxY8XAblIEbEFMnjBv23oK

Planned pages:
`Product Map, Foundations, Components, Investigate, Lineage, Perspectives, Cases, Sources, Products, Architecture Studio, Trace, Responsive, Prototypes, Archive`.

## Current gate status

| Gate | State | Evidence |
|---|---|---|
| G0 Product scope | GREEN | Product document + Master TZ |
| G1 Analytical contracts | GREEN | Stage 01/02 analytics |
| G2 Architecture/API | AMBER | C4 + OpenAPI baseline; service catalog expansion pending |
| G3 Figma baseline | AMBER | master Figma created; pages/tokens/components pending |
| G4 Implementation skeleton | NOT STARTED for Visual Workspace | existing Knowledge Factory code is upstream foundation |
| G5 Golden path | NOT YET PROVEN end-to-end | local execution evidence required |

## Main risks

1. **Architecture drift** — mitigated by requirement/API/trace ID chain.
2. **Microservice overengineering** — mitigated by explicit split criteria.
3. **Graph UX complexity** — requires senior frontend + UX ownership and performance profiling.
4. **Evidence/interpretation mixing** — strict layer separation and promotion gates.
5. **Design/code divergence** — Figma design system + future Code Connect.
6. **Bulk processing too early** — blocked until golden path acceptance.

## Production telemetry

No new reliable performance baseline exists for the Visual Workspace yet.

- speed-up vs 1 stream: `N/A`
- current throughput: `N/A`
- rework rate: `N/A`
- remaining volume: `N/A`
- ETA: `N/A`

These remain intentionally blank until measured telemetry exists.

## Next deliverables

Priority order:

1. `DOMAIN_MODEL_AND_ID_MAP.md`
2. `UX_INFORMATION_ARCHITECTURE.md`
3. `C4_AND_SERVICE_BOUNDARIES.md`
4. `API_CATALOG_V1.yaml`
5. `TRACE_CONTRACT_V1.md`
6. Figma Product Map + Foundations
7. Figma Investigate Workspace
8. Acceptance matrix
9. senior frontend/backend implementation skeleton

## Project management rule

Every future status report must distinguish:
- designed;
- coded;
- locally executed;
- CI verified;
- user accepted;
- production ready.

No stage is called “working” solely because code or documentation exists.
