# S2 — Ingest, OCR/translation provenance and evidence

Mission: connect book/document ingestion outputs to canonical knowledge storage without losing source identity.

Deliverables:
- document ingest adapter for PDF/EPUB/DOCX/TXT/MD/HTML;
- OCR/native-text source classification;
- fragment records with page/section/block anchors and bbox where available;
- original/source text and translated text stored separately;
- SHA-256 for document and fragment payloads;
- translation provenance: model, prompt/profile, glossary revision, reviewer, timestamp;
- evidence package builder for later review;
- failure states for empty/corrupt/unreadable material.

Acceptance gate: any extracted or translated fragment can be traced back to exact source document, source SHA-256 and page/section/block; no translation overwrites original evidence.