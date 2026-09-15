# FATHER Visual Engineering Workbench — Implementation Roadmap

Status: `DRAFT_V0.1 / IMPLEMENTATION SEQUENCE`

## 1. Governing rule

Implementation must follow evidence maturity, not feature excitement.

```text
paper pipeline
→ technical specification
→ test/oracle design
→ read-only projection
→ structured editing
→ traceability/evidence
→ gates/reviews/tests
→ hardening/integrations
→ AI assistance last
```

No phase may silently redefine upstream canonical contracts.

---

# Phase 0 — Specification & Manual Walkthrough

## Goal

Prove the paper model and UX contract before product code.

## Required work

- review A0–A16;
- review S00–S59;
- verify artifact dependency matrix;
- verify role/authority matrix;
- review node/port/relation types;
- manual greenfield walkthrough;
- manual brownfield walkthrough;
- exception/rework walkthrough;
- define first representative fixture project;
- draft E2E tests;
- architecture ADR for implementation baseline.

## Deliverables

- accepted TZ package;
- accepted station model;
- first data schema;
- implementation ADR;
- test plan;
- backlog mapped to requirement IDs.

## Exit Gate

`WG-0 SPECIFICATION_READY`

No frontend/backend product-path implementation before this gate except disposable prototypes used to test UX/technology assumptions.

---

# Phase 1 — Read-Only Engineering Viewer

## Goal

Show real canonical project data as a live graph without editing authority.

## Scope

- load fixture/canonical JSON/YAML projection;
- Z0 lifecycle;
- Z1 stations;
- node selection;
- inspector read-only;
- breadcrumb drill-down using predefined subgraphs;
- perspectives;
- minimap;
- global search by ID/name;
- deep links;
- upstream/downstream trace;
- source/evidence link display.

## Explicitly not included

- database write;
- approvals;
- AI;
- complex import;
- realtime collaboration.

## Tests

- rendering fixture;
- click/inspect;
- drill-down/return context;
- perspective switch;
- trace path;
- keyboard navigation basics.

## Exit Gate

`WG-1 READ_ONLY_MODEL_PROVEN`

Question to answer: does the visual grammar make the engineering process clearer than documents/tree alone?

---

# Phase 2 — Canonical Persistence & Structured Editing

## Goal

Introduce real server truth and versioned structured objects.

## Scope

- PostgreSQL schema;
- object/revision/relation model;
- FastAPI reference API;
- draft editing;
- optimistic concurrency;
- status state machine;
- typed ports/relations;
- validation;
- layout persistence separated from semantics;
- audit baseline;
- RBAC baseline.

## UX

- read/edit mode distinction;
- dirty state;
- validation inline;
- save revision;
- conflict resolution UI.

## Tests

- invariant suite;
- concurrent edit;
- invalid relation;
- version history;
- audit event;
- permission negatives.

## Exit Gate

`WG-2 STRUCTURED_MODEL_EDITING_PROVEN`

---

# Phase 3 — Source, Evidence & Brownfield Mapping

## Goal

Make evidence traceability first-class.

## Scope

- source registry;
- source versions/hash;
- object storage adapter;
- PDF/text source preview;
- source locator;
- evidence links;
- side-by-side viewer;
- source→artifact field mapping;
- initial import pipeline;
- coverage/gap/conflict state;
- brownfield project mode.

## Important constraint

No automatic truth promotion from extracted text.

## Tests

- source version immutable;
- locator exact version;
- supersession;
- file security;
- evidence trace;
- brownfield mapping E2E.

## Exit Gate

`WG-3 EVIDENCE_TRACEABILITY_PROVEN`

---

# Phase 4 — Impact, Stale & Change Management

## Goal

Make model genuinely “live” under change.

## Scope

- impact preview;
- dependency traversal;
- material/nonmaterial change classification rules;
- stale propagation;
- change request object;
- semantic diff;
- baseline compare;
- time-travel read-only baseline view;
- rework routing suggestions based on deterministic rules.

## UX

- before/after overlay;
- impacted nodes highlight;
- stale badges;
- change flow playback.

## Tests

- non-mutating preview;
- deterministic stale fixtures;
- cycles/depth limits;
- baseline diff;
- cancel proposal leaves canonical state unchanged.

## Exit Gate

`WG-4 CHANGE_IMPACT_PROVEN`

---

# Phase 5 — Reviews, Authority & Gates

## Goal

Implement controlled human governance.

## Scope

- role assignments;
- review tasks;
- anchored comments/findings;
- independence constraints;
- gate evaluation;
- authority forms;
- approval decisions;
- residual risk acceptance;
- expiry/review triggers;
- project/review queues.

## Security priority

This phase requires focused security review and authorization tests.

## Exit Gate

`WG-5 AUTHORITY_MODEL_PROVEN`

---

# Phase 6 — Requirements, Security & Test Engineering Workbenches

## Goal

Provide role-specific useful engineering views over the common graph.

## Scope

### Requirements
- requirements baseline;
- NFR scenarios;
- acceptance criteria;
- RTM;
- no-test/no-evidence views.

### Security
- threat graph;
- trust boundaries;
- controls;
- residual risk;
- security perspective.

### Testing
- test oracle;
- test cases/suites/runs/results;
- coverage;
- defect/vulnerability links.

## Exit Gate

`WG-6 CORE_ENGINEERING_VIEWS_PROVEN`

---

# Phase 7 — Architecture Workbench

## Goal

Support real architecture design instead of merely displaying imported diagrams.

## Scope

- architecture driver objects;
- options/trade-offs;
- ADR;
- component model;
- C4 projection;
- Structurizr adapter/export;
- deployment view;
- dynamic scenario flow;
- option compare;
- architecture health/revisit trigger.

## Explicit rule

C4 diagrams are views of canonical FATHER architecture model, not separate truth.

## Exit Gate

`WG-7 ARCHITECTURE_WORKBENCH_PROVEN`

---

# Phase 8 — Integrations / Import-Export Pack

## Goal

Connect existing engineering ecosystem without making FATHER own every tool.

Candidate adapters:

- GitHub/GitLab;
- OpenAPI/AsyncAPI;
- Structurizr;
- BPMN/bpmn-js;
- CI result import;
- scanner result import (SARIF/SBOM where practical);
- issue tracker;
- documentation export.

Each adapter needs separate security/authority/data-flow review.

## Exit Gate

`WG-8 INTEROPERABILITY_PROVEN`

---

# Phase 9 — Performance, Hardening & Operations

## Goal

Move from capable application to production-grade engineering platform.

## Work

- large graph profiling;
- query/index tuning;
- frontend virtualization;
- cache strategy;
- security hardening;
- backup/restore;
- observability;
- migration procedures;
- accessibility;
- browser matrix;
- deployment IaC;
- operational runbooks;
- DR tests according to deployment NFR.

## Technology escalation gate

Only here, based on measured evidence, decide whether needed:

- dedicated search engine;
- graph DB;
- distributed queue/broker;
- split microservices;
- separate compute workers.

## Exit Gate

`WG-9 PRODUCTION_PLATFORM_READY`

---

# Phase 10 — Role Knowledge & Deterministic Assistance

## Goal

Before LLM agents, encode reusable deterministic expertise.

## Scope

- validators;
- checklists;
- decision trees;
- calculators;
- source mapping;
- role KB viewers;
- training/eval case management;
- maturity dashboard.

## Exit Gate

`WG-10 ROLE_KNOWLEDGE_BASELINE_READY`

---

# Phase 11 — Single-Model Assisted Operations

Only after Automation Activation Gate allows.

Use cases selected where L0/L1/L2 inadequate:

- candidate extraction;
- candidate requirement normalization;
- candidate conflict review;
- evidence-bound summary;
- draft review findings.

Requirements:

- frozen inputs;
- output schema;
- deterministic evidence validation;
- human review;
- security eval;
- telemetry.

## Exit Gate

`WG-11 BOUNDED_AI_ASSISTANCE_PROVEN`

---

# Phase 12 — Champion/Verifier and Model Zoo

Only after measured value of single model and explicit materiality routing.

Scope:

- champion + verifier;
- independent challenger;
- judge only when justified;
- capability-specific model registry;
- preserved dissent;
- human authority;
- cost/quality telemetry.

No autonomous lifecycle control.

## Exit Gate

`WG-12 MODEL_ZOO_GOVERNED`

---

# Phase 13 — Controlled Automation of Paper Pipeline

Final long-term goal.

Automation may:

- route review tasks;
- detect missing fields;
- execute deterministic validators;
- draft artifacts;
- update status from machine evidence;
- run tests/integrations;
- propose next actions.

Automation may not bypass human authority boundaries.

---

# Delivery strategy

Prefer thin vertical slices over layer-only projects.

Example first useful slice:

```text
Project fixture
→ S00–S12 visualization
→ Inspector
→ one source evidence viewer
→ one Requirement trace
→ one Test Oracle trace
```

Then expand breadth.

---

# Backlog mapping rule

Every implementation issue/epic must reference:

- TZ requirement IDs;
- affected station(s);
- data entities;
- tests/acceptance;
- security impact;
- migration impact where relevant.

No feature ticket “Add nice graph” without engineering contract.

---

# Definition of Ready for implementation item

An item is Ready only when:

- problem/value clear;
- requirement ID exists;
- UX behavior specified;
- canonical model impact known;
- API contract or no-API rationale known;
- auth/security impact assessed;
- acceptance tests written;
- dependencies identified.

---

# Definition of Done

- code/config committed;
- tests pass;
- acceptance proven;
- security checks completed;
- docs/spec updated if behavior changed;
- migration supplied if needed;
- audit/observability accounted;
- no unresolved critical regression;
- traceability from implementation to TZ maintained.

---

# Release cadence principle

Do not optimize for arbitrary sprint count. Optimize for validated engineering capability.

Each Workbench Gate (WG-N) should produce a usable increment and evidence package.

---

# Stop conditions

Pause implementation and return to design if:

- two teams interpret same requirement differently;
- canonical object model cannot represent a use case without UI hacks;
- authority rule is ambiguous;
- graph becomes unreadable in core user scenario;
- test oracle cannot be stated;
- selected technology forces semantics not required by FATHER;
- large complexity added without measurable benefit.

This protects the project from implementing the wrong platform very efficiently.