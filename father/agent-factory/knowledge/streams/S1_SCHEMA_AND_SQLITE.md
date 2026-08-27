# S1 — Schema and SQLite foundation

Mission: build the canonical machine-readable storage for FATHER Knowledge Factory M1.

Deliverables:
- `schema.sql` with tables: documents, fragments, translations, knowledge_nodes, knowledge_edges, evidence_links, reviews, scores, role_views, processing_runs;
- stable ID conventions;
- schema_version metadata;
- foreign keys, uniqueness and indexes;
- bootstrap/init script;
- golden fixture with one source -> fragment -> translation -> node -> edge -> evidence -> review -> score -> role view;
- integrity test and deterministic JSONL export contract.

Constraints:
- do not duplicate one fact per role;
- do not store copyrighted full books in the public repository;
- preserve SHA-256 provenance fields;
- keep review and score histories appendable.

Acceptance gate: fresh SQLite DB builds cleanly and golden fixture passes foreign-key/integrity checks.