# FATHER Knowledge Factory — Product Document

Document ID: `FATHER-KF-PRODUCT-0001`
Package: `PACKAGE_01_FOUNDATION`
Status: DRAFT_FOR_REVIEW
Owner: FATHER Product

## 1. Product intent

FATHER Knowledge Factory converts heterogeneous professional sources into one evidence-backed, machine-readable knowledge layer that can be safely reused by multiple expert agents.

The product must preserve the chain from professional conclusion back to exact source evidence and must not duplicate semantic truth separately for every role.

Target roles for M1:
- Architect;
- Software Engineer / Programmer;
- Information Security;
- Lawyer;
- Manager;
- Product.

## 2. Problem to solve

Professional knowledge is currently scattered across books, standards, laws, technical documentation, reports and local files. A plain document library or chunk-based RAG does not provide enough control over:
- source identity and exact provenance;
- OCR and translation quality;
- versioning/currentness;
- contradictions between sources;
- one semantic concept appearing in many sources;
- reuse of the same knowledge by different professional roles;
- explainability of agent conclusions;
- repeatable review and correction;
- debugging when a wrong answer is produced.

The product must therefore create governed knowledge objects, not just searchable text chunks.

## 3. Product value

The factory should allow a user or downstream agent to answer not only `what is known?`, but also:
- where did this knowledge come from;
- what exact fragment supports it;
- was the fragment OCR-extracted or native;
- whether a translation was used and which model/reviewer produced it;
- whether other sources support or contradict it;
- how trustworthy/applicable/current it is;
- which professional roles can use it;
- who or what approved it;
- how to reproduce the processing run that created it.

## 4. Primary product outcomes

M1 is successful when the system can take one short English technical source and one real technical document and produce a traceable chain:

`SOURCE_DOCUMENT -> SOURCE_FRAGMENT -> TRANSLATION_FRAGMENT -> KNOWLEDGE_NODE -> KNOWLEDGE_EDGE -> EVIDENCE_LINK -> SCORE_VECTOR -> REVIEW -> ROLE_VIEW -> KB_READY`

Every object must remain resolvable backwards to the original source.

## 5. Core user journeys

### Journey A — English technical book
1. User selects/adds an English architecture/programming/security book.
2. Factory identifies file and calculates SHA-256.
3. Factory extracts native text or performs OCR only where needed.
4. Factory preserves page/section/block anchors.
5. Translator produces RU text without overwriting EN source.
6. Reviewer verifies translation integrity.
7. Knowledge extractor creates atomic candidate nodes.
8. Evidence links bind candidates to exact source fragments.
9. Graph builder adds relations and explicit contradictions.
10. Review gate decides APPROVE / REVISE / REJECT / ESCALATE.
11. Approved knowledge becomes available to role views.

### Journey B — Russian normative/legal source
1. Source identity and revision/currentness are established.
2. Exact article/clause/section anchors are preserved.
3. Atomic requirements/definitions are extracted separately from interpretation.
4. Applicability is assessed separately from currentness.
5. Legal/security/architect/manager role views reuse the same canonical node.

### Journey C — Debug an incorrect agent answer
1. User receives a questionable recommendation.
2. System resolves the knowledge node(s) used.
3. For each node, system shows evidence, source fragment, source SHA, translation and review history.
4. Trace ID shows processing stages, worker/model, elapsed time and failures/warnings.
5. Faulty node/translation/relation can be revised without destroying history.

## 6. Product scope — M1

Included:
- TXT/MD/HTML/DOCX/EPUB/PDF ingestion;
- native PDF extraction;
- PDF classification contract for native/scanned/mixed;
- OCR path for pages requiring OCR;
- EN->RU technical translation;
- common terminology glossary;
- translation QA/reviewer;
- source/document/fragment SHA-256 provenance;
- canonical SQLite knowledge store;
- atomic knowledge nodes;
- graph edges and explicit contradictions;
- evidence links;
- component score vectors;
- six role views;
- model/expert review lifecycle;
- KB_READY promotion gate;
- structured tracing across all stages;
- JSONL export/replay contract;
- local storage for copyrighted originals/translations.

## 7. Explicitly out of scope for M1

- autonomous legal or business authority;
- automatic resolution of source contradictions without evidence/review;
- treating model consensus as truth;
- automatic public publishing of copyrighted books/translations;
- mandatory Neo4j or distributed DB infrastructure;
- large-scale GPU cluster scheduling;
- fully autonomous bulk import before golden-path acceptance gates are green.

## 8. Canonical product rules

1. Original source is immutable evidence.
2. Translation is a separate derivative layer.
3. Interpretation is separate from source text.
4. One semantic item has one canonical knowledge identity.
5. Role views do not clone truth.
6. Every node and edge must have provenance.
7. Contradictions are preserved, not silently averaged.
8. One opaque confidence/weight is forbidden; components remain inspectable.
9. A model is a worker/reviewer, not a source of authority by itself.
10. No candidate becomes KB_READY without passing its evidence/review gates.
11. Every material processing stage emits trace events.
12. Failures are stored as machine-readable state, not hidden by retries.

## 9. Product entities visible to downstream systems

- `SOURCE_DOCUMENT`
- `SOURCE_FRAGMENT`
- `TRANSLATION_FRAGMENT`
- `KNOWLEDGE_NODE`
- `KNOWLEDGE_EDGE`
- `EVIDENCE_LINK`
- `SCORE_VECTOR`
- `REVIEW`
- `ROLE_VIEW`
- `PROCESSING_RUN`
- `TRACE_EVENT`
- `ENTITY_TRACE_LINK`

## 10. Product boundary

Public repository `KNOWLEDGE_CORE` stores:
- source code;
- schemas;
- contracts;
- policies;
- safe fixtures;
- machine-readable metadata safe for publication.

Local runtime stores:
- full copyrighted books;
- OCR/full extracted texts;
- full translations;
- runtime SQLite database;
- embeddings/vectors;
- traces/logs/reports that may contain local paths or derived working data.

Default local root: `G:\1\FATHER_KNOWLEDGE`.

## 11. Role-specific product value

### Architect
Receives principles, patterns, trade-offs, NFRs, dependencies and evidence supporting architecture decisions.

### Software Engineer
Receives implementation rules, patterns, tests, failure modes, performance/maintainability knowledge and source-backed examples.

### Information Security
Receives threats, requirements, controls, secure-development principles, compliance mappings and evidence.

### Lawyer
Receives exact normative text anchors, definitions, applicability/currentness separation, version/conflict information and interpretation as a separate layer.

### Manager
Receives risks, obligations, cost/resource implications, governance/accountability and metrics backed by traceable sources.

### Product
Receives user-value implications, constraints, prioritization evidence, trade-offs, metrics and product/technical dependencies.

## 12. Quality expectations

A product result is unacceptable when:
- source cannot be resolved;
- original and translation are mixed;
- evidence link is missing;
- OCR/translation failure is hidden;
- a knowledge node has no atomic meaning;
- a role-specific copy diverges from the canonical node;
- an edge cannot explain why it exists;
- a contradiction was silently removed;
- a review cannot be reproduced;
- tracing cannot identify where an error occurred.

## 13. M1 acceptance gates

### MIN
- SQLite DB initializes;
- schema/integrity checks pass;
- golden fixture creates all mandatory core entities;
- backwards provenance works;
- trace traversal works.

### MED
- short EN fixture is translated and reviewed locally;
- result is ingested into canonical DB;
- at least one evidence-backed knowledge node is created;
- six role views reuse the same node;
- unsupported candidate is blocked;
- full trace is available.

### MAX
- one real technical PDF/book passes classification/extraction or OCR;
- translation preserves technical meaning/code/numbers/URLs;
- multiple nodes and at least one edge are created;
- contradiction fixture remains explicit;
- review and JSONL round-trip are reproducible;
- no copyrighted full source/translation is committed publicly.

## 14. Product telemetry

Required runtime telemetry:
- items total/processed/accepted/rejected;
- rework count;
- errors by stage/reason;
- elapsed time;
- throughput;
- model/runtime profile;
- OCR/translation/reviewer outcomes;
- trace coverage.

Speed-up versus one stream, remaining volume and ETA may be reported only after real comparable telemetry exists.

## 15. Product risks

- OCR corrupts technical content;
- translator changes modality/negation/terminology;
- LLM invents unsupported knowledge or relations;
- semantic dedup merges different contexts;
- old/new editions are mixed;
- legal applicability is confused with currentness;
- graph grows faster than review capacity;
- local GPU becomes bottleneck;
- traces accidentally expose secrets/copyrighted payloads.

All risks must have deterministic checks or explicit review/escalation paths in subsequent Analytics and Architecture documents.

## 16. Product decision gate

This document defines `WHAT` and `WHY`, not implementation detail.

Before code is accepted as the next baseline, Package 01 must continue sequentially:
1. Product Document review;
2. Analyst document — requirements/use-cases/rules/data and failure analysis;
3. Architect document — components/interfaces/storage/deployment/tracing/security/ADRs;
4. Senior implementation only against approved contracts.

Next document after product review: `02_ANALYTICS.md`.
