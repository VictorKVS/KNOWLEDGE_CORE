# FATHER Knowledge Factory M1 — 4-stream implementation plan

Goal: turn translated/OCR-extracted technical books and regulatory sources into one canonical machine-readable knowledge layer that can serve Architect, Software Engineer, Information Security, Lawyer, Manager and Product roles without duplicating truth.

Canonical pipeline:

SOURCE_DOCUMENT -> SOURCE_FRAGMENT -> TRANSLATION_FRAGMENT -> KNOWLEDGE_NODE -> KNOWLEDGE_EDGE -> EVIDENCE_LINK -> REVIEW -> SCORE -> ROLE_VIEW -> KB_READY

## Stream split

### S1 — Canonical data model and SQLite foundation
Owns: `father_knowledge.db`, schema, migrations, IDs, constraints, indexes, referential integrity, deterministic export.

Primary tables: `documents`, `fragments`, `translations`, `knowledge_nodes`, `knowledge_edges`, `evidence_links`, `reviews`, `scores`, `role_views`, `processing_runs`.

Acceptance: empty DB can be created from schema; one sample document can be inserted end-to-end; foreign-key checks pass; schema version is recorded.

### S2 — Ingest, OCR/translation provenance and evidence
Owns: mapping from PDF/EPUB/DOCX/TXT/OCR/translation outputs into canonical document/fragment records; SHA-256 provenance; page/block anchors; source-language/original/translation separation.

Acceptance: every knowledge candidate can trace back to source document SHA, page/section/block and original text; translation never replaces source text.

### S3 — Knowledge graph, relations, weights and role views
Owns: node taxonomy, edge taxonomy, score vector, graph integrity, role views for Architect / Software Engineer / Security / Lawyer / Manager / Product.

Acceptance: one node may be consumed by many roles without duplication; edge provenance is stored; weights remain component-wise, not a single opaque confidence number.

### S4 — Review, QA, GPT/analyst verification and exports
Owns: evidence packages, deterministic validators, review lifecycle, APPROVE/REVISE/REJECT/ESCALATE, JSONL export, KB_READY promotion gate and regression fixtures.

Acceptance: no node reaches KB_READY without evidence links and review gate; exports can reconstruct graph and provenance; failed checks are machine-readable.

## Integration gates

G0 schema compiles.
G1 one-document golden path works.
G2 translation provenance is lossless.
G3 graph/role views work without copied knowledge nodes.
G4 review gate blocks unsupported claims.
G5 JSONL export round-trip reproduces IDs, evidence and edges.

## Non-negotiable rules

- original source is immutable evidence;
- translation is a separate layer;
- interpretation is not source truth;
- one knowledge node may serve many roles;
- exact provenance is mandatory;
- score components are stored separately;
- unsupported claims remain UNDER_REVIEW or REJECTED;
- local copyrighted full books/translations are not published to the public repository;
- Security Knowledge canonical tree is not moved.

## Production telemetry

Record per stream: items processed, items accepted, rework count, elapsed time, throughput and failure reason. Speed-up versus a one-stream baseline is reported only after a real baseline exists. ETA is not emitted without sufficient telemetry.
