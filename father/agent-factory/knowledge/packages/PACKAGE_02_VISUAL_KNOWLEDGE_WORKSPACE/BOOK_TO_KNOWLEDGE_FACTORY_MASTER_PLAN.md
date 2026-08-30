# FATHER Book → Knowledge Factory — Master Plan

Status: DESIGN BASELINE
Owner: Senior PM + System Analyst + Knowledge Architect
Scope: all authorized professional books used by FATHER

## 1. Mission

Books are not a passive archive and are not dumped into one generic RAG index. They are source material for a controlled knowledge factory that produces traceable, reusable engineering knowledge for product development.

Canonical flow:

`BOOK ORIGINAL -> IDENTITY/SHA256 -> RIGHTS/USE POLICY -> EXTRACT/OCR -> STRUCTURE -> TRANSLATE -> TRANSLATION QA -> ATOMIC KNOWLEDGE -> EVIDENCE -> CROSS-SOURCE CHECK -> REVIEW -> CANONICAL KNOWLEDGE GRAPH -> ROLE/PROJECT VIEWS -> DEVELOPMENT USE -> OUTCOME -> LESSON`

The original, translation, interpretation and canonical knowledge are separate layers.

## 2. Copyright and locality boundary

- Source books and full translations remain local unless publication rights explicitly permit otherwise.
- Public GitHub stores code, schemas, metadata, safe fixtures, hashes, manifests, extracted knowledge records and short evidence locators; it does not store unauthorized full copyrighted text.
- Each source has `rights_status`, `use_scope`, `storage_scope`, `publication_scope` and `review_status`.
- A book may be processed for private/local research and internal knowledge extraction without that implying permission to republish its full text or translation.

## 3. Book lifecycle

### B0 REGISTERED
Record identity, title, authors, edition, language, ISBN if available, local path, SHA256, domain candidates, priority and rights state.

### B1 PROFILED
Determine file type, page count, native/scanned/mixed layout, tables, code, formulas, figures, languages and expected OCR complexity.

### B2 EXTRACTED
Build immutable source fragments with precise locators: page, chapter, section, paragraph/block, bbox where available, ordinal and fragment SHA.

### B3 TRANSLATED
For non-Russian sources, create a separate RU derivative layer with translator model, prompt/profile, glossary version, reviewer, QA outcome and exact source-fragment link.

### B4 KNOWLEDGE_CANDIDATES
Extract atomic objects without silently changing the author's meaning:
- CONCEPT
- DEFINITION
- CLAIM
- PRINCIPLE
- PATTERN
- ANTI_PATTERN
- DECISION_RULE
- TRADE_OFF
- CHECKLIST
- METRIC
- FAILURE_MODE
- TEST
- EXAMPLE
- REQUIREMENT
- LESSON

### B5 EVIDENCE_LINKED
Each candidate resolves to source fragment(s), book/document identity, edition, locator and source SHA. Translation may support readability but source evidence remains authoritative for what the author actually wrote.

### B6 CROSS_SOURCE_CHECKED
Compare with other books, standards, official docs, experiments and production evidence. Preserve agreement, refinement and contradiction instead of flattening them.

Allowed relations include:
`DEFINES, SUPPORTS, CONTRADICTS, REFINES, DEPENDS_ON, PART_OF, APPLIES_TO, CAUSES, MITIGATES, IMPLEMENTS, DERIVED_FROM, EVIDENCE_FOR, SAME_AS`.

### B7 REVIEWED
Review verdicts: `APPROVE / REVISE / REJECT / ESCALATE`.

Model agreement is not evidence. Critical architecture/security/legal decisions require stronger evidence and independent review.

### B8 KB_READY
Only approved, evidence-linked knowledge may become canonical knowledge.

### B9 ROUTED
One canonical node is projected into multiple role and project views; knowledge is not copied into six inconsistent databases.

### B10 USED_IN_DEVELOPMENT
Knowledge is connected to actual project artifacts: requirement, ADR, C4 element, API, schema, component, test, security control, runbook, product decision or code change.

### B11 OUTCOME_CAPTURED
Production/test outcome returns to Decision Memory and may strengthen, weaken, refine or supersede the prior knowledge/application rule.

## 4. Routing dimensions

Routing is many-to-many across four dimensions.

### 4.1 Professional domain
- PRODUCT_DISCOVERY
- REQUIREMENTS_ANALYSIS
- DOMAIN_MODEL_DDD
- UX_INFORMATION_ARCHITECTURE
- GRAPH_VISUALIZATION
- SOFTWARE_ARCHITECTURE
- C4_ARCHITECTURE_AS_CODE
- API_INTEGRATION
- DATA_ARCHITECTURE
- KNOWLEDGE_GRAPHS
- MICROSERVICES_DISTRIBUTED
- SOFTWARE_ENGINEERING
- AI_LLM_RAG
- OBSERVABILITY_RELIABILITY
- SECURITY_DEVSECOPS
- TEAM_EVOLUTION
- FINOPS
- CLOUD_PLATFORM

### 4.2 Role view
- PRODUCT
- ANALYST
- ARCHITECT
- SOFTWARE_ENGINEER
- AI_ML_ENGINEER
- SECURITY
- SRE_DEVOPS
- LAWYER
- MANAGER
- CHIEF_ANALYST

### 4.3 Project lifecycle
- DISCOVERY
- REQUIREMENTS
- DOMAIN
- UX
- HLD
- LLD
- API_CONTRACTS
- IMPLEMENTATION
- VERIFICATION
- RELEASE
- OPERATIONS
- EVOLUTION

### 4.4 Evidence maturity
- CANDIDATE
- BOOK_SUPPORTED
- MULTI_SOURCE_SUPPORTED
- STANDARD_OR_OFFICIAL_SUPPORTED
- EXPERIMENTALLY_VERIFIED
- PRODUCTION_VERIFIED

A book can therefore contribute the same canonical principle to `ARCHITECT + HLD`, `SOFTWARE_ENGINEER + IMPLEMENTATION`, and `SRE + OPERATIONS` through different role projections without duplicating the semantic node.

## 5. Knowledge object contract

Minimum canonical record:

- `knowledge_id`
- `type`
- `canonical_statement`
- `conditions`
- `constraints`
- `applicability`
- `non_applicability`
- `trade_offs`
- `failure_modes`
- `related_nodes`
- `evidence_ids`
- `source_authority`
- `cross_source_support`
- `ambiguity`
- `review_state`
- `roles[]`
- `domains[]`
- `lifecycle_stages[]`
- `maturity`
- `created_by_run_id`
- `trace_id`
- `revision`

Evidence record:

`knowledge_id -> evidence_id -> fragment_id -> book_id -> edition -> source_sha256 -> page/chapter/section/block -> original_text locator -> translation_id(optional)`

## 6. How books become development rules

A book is useful only when its knowledge can affect engineering work.

Example:

`Simon Brown / C4`
→ PRINCIPLE: architecture diagrams should reflect the real software structure
→ DECISION_RULE: every C4 component must resolve to a real implementation boundary or explicit planned boundary
→ FATHER requirement: `ARCH-VIS-*`
→ architecture editor validation
→ API entity contract
→ regression test
→ project ADR / implementation linkage.

Another example:

`Observability Engineering`
→ PRINCIPLE: debugging distributed behavior requires high-cardinality event context
→ FATHER rule: every material cross-service call propagates trace context
→ OpenTelemetry contract
→ API headers/event metadata
→ trace completeness test
→ UI Trace view.

## 7. Processing priority

Do not translate the entire library blindly in filename order.

Priority score is derived from:
1. current project stage;
2. canonical/GOLD source status;
3. uniqueness of knowledge;
4. cross-role value;
5. unresolved architecture question coverage;
6. language gap;
7. extraction cost;
8. rights/use eligibility.

Recommended queue order for the current product:
1. requirements/product books;
2. DDD/domain modeling;
3. C4/software architecture;
4. API design/integration;
5. data/knowledge graphs;
6. software engineering/continuous delivery;
7. observability/reliability;
8. security;
9. AI/RAG;
10. team/evolution/FinOps.

## 8. Translation policy

Translation exists to make knowledge usable in Russian, not to replace the original.

- original EN fragment is immutable evidence;
- RU translation is derivative and versioned;
- technical identifiers/code/API/schema terms remain exact;
- glossary is shared across books and versioned;
- reviewer and deterministic QA are required;
- ambiguous terms are flagged, not guessed;
- translation corrections create revisions instead of overwriting provenance.

## 9. Book-to-KB router

The router receives reviewed knowledge candidates and assigns:
- canonical domain(s);
- role views;
- project lifecycle views;
- topic tags;
- related project entities;
- contradiction candidates;
- potential product outputs.

The router never creates a second truth copy. It creates projections/links.

## 10. Development integration

Every major project artifact should be able to query and record knowledge lineage.

Target chain:
`REQ -> DOMAIN NODE -> ADR -> C4 -> API -> CODE/SCHEMA -> TEST -> TRACE -> OUTCOME`

Each artifact may link `applied_knowledge_ids[]` and `rejected_alternative_knowledge_ids[]`.

This allows FATHER to answer:
- Why was this architecture selected?
- Which book/standard/experiment supported it?
- What alternatives were rejected and why?
- Which production outcomes confirmed or challenged the decision?

## 11. Visual workspace requirements

The website/Figma workspace must show:
- book/source inventory;
- processing state per book;
- page/chapter structure;
- translation state;
- extracted knowledge nodes;
- evidence chains;
- agreement/contradiction graph;
- role/project routing;
- downstream products/ADRs/APIs/tests/code;
- full lineage back to source;
- trace timeline of processing stages.

Core visual story:
`INFORMATION -> EVIDENCE -> KNOWLEDGE -> DECISION -> PRODUCT -> OUTCOME`.

## 12. API-first and trace-first

Every material processing boundary exposes a versioned contract, even if initially implemented inside a modular monolith.

Candidate APIs/events:
- Library Registry API
- Source Profile API
- Extraction API
- Translation API
- Translation QA API
- Knowledge Candidate API
- Evidence API
- Knowledge Graph API
- Review API
- Routing/Role View API
- Development Artifact Link API
- Trace API

Every call/event propagates `trace_id`; cross-stage entity links retain `book_id`, `fragment_id`, `translation_id`, `knowledge_id`, `review_id`, and downstream artifact IDs.

## 13. Microservice policy

Do not split into microservices merely because the pipeline has many stages.

Default: modular monolith + explicit contracts.

Extract a service only when at least one measured reason exists:
- independent scaling;
- GPU/CPU/runtime isolation;
- failure isolation;
- independent deployment cadence;
- security/trust boundary;
- separate data ownership;
- external integration boundary.

Likely future candidates: OCR worker, Translation inference worker, Embedding worker, Graph API, Trace/Observability ingest. Decision requires ADR and measured evidence.

## 14. Acceptance gates

### MIN
One authorized EN technical book:
`original -> SHA -> extract -> translate -> QA -> 10+ atomic knowledge candidates -> evidence -> review -> canonical node -> role view -> one development artifact link`, all under trace.

### MED
Three books from different domains, shared glossary, cross-source SAME_AS/REFINES/CONTRADICTS candidates, six role views, graph UI data contract and stable IDs.

### MAX
Representative real library batch with native/scanned/mixed PDFs, controlled OCR fallback, book priority queue, round-trip export/replay, contradiction review, development artifact lineage and measured throughput/rework.

## 15. Metrics

Collect factual telemetry only:
- books registered/profiled/extracted/translated/reviewed;
- pages and fragments processed;
- translation QA pass/rework rate;
- knowledge candidates / accepted / rejected;
- evidence coverage;
- orphan rate;
- contradiction candidates;
- human review share;
- throughput by stage;
- elapsed and queue wait;
- failure reason;
- downstream development use count.

Speed-up vs one stream, remaining volume and ETA are reported only after a real one-stream baseline and stable measurements.

## 16. Immediate execution order

1. Freeze book metadata + rights schema.
2. Import existing library inventory into Book Registry without moving originals.
3. Classify GOLD/SILVER/CANDIDATE and domain/stage priority.
4. Run a GOLD architecture/API book through MIN path.
5. Validate translation and evidence trace.
6. Extract atomic knowledge and route to canonical graph.
7. Link at least one extracted principle to a real FATHER requirement/ADR/API/test.
8. Expose the chain in Visual Knowledge Workspace.
9. Only then scale queue processing.

## 17. Definition of success

Success is not “all books translated”. Success is that authorized books become a maintained, evidence-backed engineering memory that directly improves FATHER development while every material recommendation remains traceable to its source and actual outcome.
