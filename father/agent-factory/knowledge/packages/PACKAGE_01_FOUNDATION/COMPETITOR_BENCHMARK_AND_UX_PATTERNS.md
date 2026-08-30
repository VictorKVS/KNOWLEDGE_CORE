# FATHER Knowledge Factory — Competitor Benchmark & UX Patterns

Document ID: `FATHER-KF-BENCH-0001`
Status: `ARCHITECTURE_INPUT`
Owner: `FATHER Product + Architect`
Scope: investigation UX, knowledge graph, lineage, evidence, observability, case workflow, source-grounded AI.

## 1. Benchmark objective

Do not clone a competitor. Reuse proven interaction and architecture patterns where they strengthen FATHER's canonical flow:

`SOURCE -> EXTRACT/OCR -> TRANSLATE -> EVIDENCE -> KNOWLEDGE -> GRAPH -> REVIEW -> ROLE VIEW -> PRODUCT`

Every adopted pattern must preserve FATHER rules: evidence-first, immutable source, API-first, trace-first, one canonical node with multiple role projections, and no model-as-authority shortcut.

## 2. Maltego — adopt the investigation ergonomics

Strong patterns:
- graph-first investigation workspace;
- entity palette and type-aware actions;
- context actions / transforms launched from selected entities;
- multiple layouts (hierarchical, organic, circular, orthogonal);
- graph/table/map switching;
- transform history and visible derivation of new entities;
- cases, collaboration, bookmarks and result export;
- custom data sources through transform/API concepts.

Adopt in FATHER:
- right-click / context-action model for node operations;
- `Expand`, `Find evidence`, `Show source`, `Compare versions`, `Find contradictions`, `Build product`, `Open trace` actions;
- multiple graph layouts;
- graph + table + detail-panel simultaneous view;
- visible operation history tied to trace spans;
- analyst workspaces/cases.

Do not copy:
- OSINT-specific entity ontology as the canonical FATHER ontology;
- transform results as automatically trusted knowledge.

## 3. OpenCTI — adopt structured graph governance

Strong patterns:
- explicit entity and relationship types;
- STIX-style typed graph semantics;
- investigations/workspaces as a temporary analytical surface over the shared knowledge base;
- ability to pivot from any entity/relationship;
- direct vs inferred relationships visually distinguishable;
- graph findings can be converted into durable report/container artifacts;
- tables and graph are alternate lenses over the same knowledge.

Adopt in FATHER:
- distinguish `DIRECT_EVIDENCE` vs `INFERRED` edges visually;
- temporary investigation workspace separate from canonical KB;
- pivot/expand/rollback operations;
- investigation -> durable product conversion;
- typed relationship registry with schema/version;
- report/container concept for packaging selected nodes/evidence into a product.

Do not copy:
- threat-intelligence-specific STIX schema as the universal data model; FATHER keeps its broader professional ontology.

## 4. Palantir Foundry/Ontology — adopt lineage and productization

Strong patterns:
- ontology as a semantic/operational layer rather than raw data catalog;
- data lineage from sources into operational objects/workflows;
- workflow lineage showing upstream/downstream dependencies;
- decision lineage: which data/version/application supported a decision;
- graph-backed observability integrating metrics, tracing, logs and execution history;
- object + action model connects knowledge to operational workflows/products;
- branch-aware exploration and impact analysis.

Adopt in FATHER:
- dedicated `Lineage` mode independent of investigation graph;
- upstream/downstream impact view for every DOC/FRG/TRN/KN/EDGE/PRODUCT;
- `decision/product lineage`: which approved nodes, evidence and revisions created an ADR/checklist/report/recommendation;
- trace timeline embedded directly in graph node detail;
- dependency impact analysis before changing/deprecating a node;
- branch/revision comparison for knowledge changes.

FATHER differentiation:
- Palantir lineage is an inspiration for dependency/decision traceability; FATHER additionally preserves exact source fragment, OCR/translation provenance and evidence sufficiency for each knowledge node.

## 5. Neo4j Bloom — adopt perspectives and exploration UX

Strong patterns:
- graph scene as central canvas;
- business `Perspectives` over the same graph;
- perspectives control visible entity categories, relations, properties, labels, icons and styles;
- natural-language/search-first graph exploration;
- card list/details next to the graph;
- share/export scene.

Adopt in FATHER:
- `Role Perspective` becomes a first-class UI mode: Architect, Developer, Security, Lawyer, Manager, Product;
- same graph, different visibility/relevance/style — never cloned truth;
- search-first query box for graph patterns and natural-language questions;
- selected-node card list / detail drawer;
- saved scenes/views for recurring investigations.

## 6. Linkurious — adopt case workflow and analyst operations

Strong patterns:
- unified case list;
- assignment, status, comments, mentions and activity history;
- alert/query -> case -> investigation graph workflow;
- property panel and configurable filters;
- graph visualization used as the investigative work surface;
- webhooks/API for integration with external case-management and dashboards;
- current product direction includes natural-language graph querying / AI copilot features.

Adopt in FATHER:
- unified `Work Queue` with status/owner/priority/review state;
- case lifecycle: `NEW -> IN_PROGRESS -> REVIEW_REQUIRED -> VERIFIED -> PRODUCTIZED/CLOSED`;
- comments/decision notes as append-only history;
- webhook/event API for product generation and downstream systems;
- saved filters and analyst-specific views;
- alerts for contradiction, stale source, failed evidence, broken lineage and review backlog.

## 7. Graphistry — adopt scale-oriented visual investigation patterns

Strong patterns:
- visual investigation over many heterogeneous sources;
- GPU-accelerated large graph visualization;
- clustering, timebars, filters, search and summaries;
- reusable investigation templates;
- APIs and embedding into custom applications.

Adopt in FATHER later:
- progressive graph loading;
- clustering/aggregation for large node counts;
- investigation templates for repeatable analyst workflows;
- timebar for source/revision/event chronology;
- keep graph renderer replaceable behind an API/data contract so a GPU renderer can be introduced only after measured scale demands it.

## 8. NotebookLM — adopt source-grounded communication

Strong patterns:
- source-centric notebook/workspace;
- grounded answers with inline citations;
- source transformation into briefings, guides, mind maps and other consumable outputs.

Adopt in FATHER:
- every generated narrative/product paragraph can expose evidence citations;
- source panel always available beside generated output;
- one-click transformation of verified knowledge into `brief`, `ADR evidence pack`, `checklist`, `risk memo`, `architecture rationale`, `legal note`, `study guide`;
- generated product is a view over approved evidence-backed nodes, not a new untraceable truth layer.

## 9. Target FATHER visual workspace

### Main modes

1. `INVESTIGATE` — Maltego/OpenCTI style graph exploration.
2. `LINEAGE` — Palantir style source -> processing -> knowledge -> product lineage.
3. `PERSPECTIVE` — Neo4j Bloom style role lens over the same graph.
4. `CASES` — Linkurious style work queue, review assignment and lifecycle.
5. `SOURCE` — source/evidence/translation inspection.
6. `PRODUCTS` — verified knowledge transformed into reports, ADRs, checklists and recommendations.
7. `TRACE` — distributed trace/span timeline for debugging and audit.

### Main screen composition

- top status/KPI strip;
- left filter/entity/action panel;
- central graph canvas;
- optional lower timeline / pipeline panel;
- right evidence/property/trace drawer;
- graph/table toggle or split view;
- persistent breadcrumbs `Product -> Node -> Evidence -> Fragment -> Source`.

## 10. Visual semantics

Recommended semantic categories (exact colors belong to UI design tokens, not architecture):
- SOURCE / DOCUMENT;
- DERIVED TEXT / TRANSLATION;
- KNOWLEDGE;
- REVIEW_REQUIRED;
- CONTRADICTION / RISK;
- ROLE / PERSPECTIVE;
- PRODUCT / ARTIFACT;
- TRACE / PROCESS.

Relationship rendering must visually distinguish:
- evidence-backed direct relation;
- inferred/candidate relation;
- contradiction;
- superseded/version relation;
- processing/lineage relation;
- product-consumption relation.

## 11. API requirements for the visual workspace

The UI must use governed APIs/events, not bypass contracts for material writes.

Minimum read APIs:
- graph neighborhood;
- node/edge detail;
- evidence chain;
- source/fragment detail;
- role perspective;
- contradiction list;
- case/work queue;
- product lineage;
- trace timeline;
- metrics/status.

Minimum action APIs:
- expand graph;
- request enrichment/extraction/review;
- approve/revise/reject/escalate;
- create relationship candidate;
- create contradiction;
- create/save investigation scene;
- convert selection to product;
- export report/graph;
- re-run failed stage with preserved trace parentage.

Every material API request propagates `request_id`, `trace_id`, contract version and relevant entity IDs.

## 12. What gives FATHER a distinct position

FATHER should not compete by having the prettiest graph alone.

Its distinctive product loop is:

`INFORMATION -> EVIDENCE -> GOVERNED KNOWLEDGE -> ROLE DECISION -> PRODUCT -> OUTCOME -> LESSON`

The differentiator is that a user can click from a finished product back through every decision/node/translation/OCR fragment to the exact original source and also see the execution trace that produced it.

## 13. Implementation priority

### V0 — immediate
- graph + table + detail drawer;
- node/edge typed rendering;
- source/evidence panel;
- trace timeline;
- role perspective selector;
- product lineage breadcrumb;
- API-first data access.

### V1
- saved investigations/scenes;
- work queue/cases;
- comments/review history;
- contradiction alerts;
- transform/action menu;
- natural-language graph search.

### V2 after telemetry
- clustering/large graph aggregation;
- timeline analytics;
- collaborative live investigation;
- GPU graph renderer if needed;
- webhooks/external case integration;
- AI copilot over the current graph/selection with evidence-only grounding.

## 14. Anti-patterns

Do not:
- clone a competitor UI pixel-for-pixel;
- create microservices solely to imitate enterprise products;
- make the visual graph the source of truth;
- let inferred edges look identical to verified evidence-backed edges;
- hide lineage behind admin-only screens;
- let AI-generated summaries lose source citations;
- overload the default scene with the full graph; progressive expansion is mandatory.
