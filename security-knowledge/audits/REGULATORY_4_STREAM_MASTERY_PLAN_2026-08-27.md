# Regulatory 4-stream mastery plan — 2026-08-27

## Goal
Process the imported RU regulatory corpus end-to-end into verified Security Knowledge without inventing requirements.

Baseline import run: `security-knowledge/corpus/ru-local-regulatory-import/runs/20260827-174936/`.
Baseline telemetry: 3004 inventory rows; 108 regulatory candidates; 64 law candidates; 44 GOST candidates; 105 unique SHA-256 files; 2 exact duplicates; 1 empty file blocked; 0 missing source files.

## Governing policy
All streams MUST follow `.ai/regulatory-extraction-policy.yaml`:
- extract only from verified source text;
- preserve exact source anchors and modality;
- separate source text, normalized requirement, interpretation, control mapping, and verification mapping;
- do not invent technical controls from legal text;
- ambiguous text remains under review;
- changed source revision requires diff + impact review.

## Parallel partition
Documents are deterministically partitioned by the first hexadecimal character of SHA-256 so every unique non-empty artifact belongs to exactly one stream.

- Stream 1: SHA prefix `0-3`
- Stream 2: SHA prefix `4-7`
- Stream 3: SHA prefix `8-b`
- Stream 4: SHA prefix `c-f`

Each stream processes BOTH laws and GOST records in its shard. Full GOST binaries remain local; public GitHub stores only metadata/SHA/provenance unless redistribution rights are explicitly cleared.

## End-to-end workflow per document
1. **IDENTITY** — verify document type, number/designation, date, title, issuing authority, edition/revision and SHA-256. Filename is evidence only, never final authority.
2. **CURRENTNESS** — verify current/repealed/replaced/superseded status from authoritative official source where available. Currentness is separate from legal applicability.
3. **VERSION CHAIN** — record predecessor/successor, amendments, effective dates and supersession links.
4. **SOURCE TEXT** — verify extractable text and preserve source artifact + immutable anchor.
5. **STRUCTURE** — split into chapters/articles/clauses/annexes/tables while preserving numbering.
6. **TERMS** — extract concepts, definitions, actors, objects, scope and exceptions.
7. **ATOMIC REQUIREMENTS** — create one obligation/prohibition/permission/condition/recommendation/definition per knowledge item when practical.
8. **TRACEABILITY** — every knowledge item must point back to source SHA-256 and exact article/clause/page/section anchor.
9. **CONTRADICTIONS** — compare definitions, thresholds, duties, deadlines, scope and terminology against already processed sources. Record contradiction/overlap; do not silently reconcile.
10. **CROSS-MAPPINGS** — only after legal extraction, add implementation/control/verification mappings as separate layers.
11. **KB_READY GATE** — mature item only if source verified, anchor exact, modality preserved, applicability recorded, ambiguity/reviewer state explicit.

## Required statuses
Document: `DISCOVERED -> IDENTITY_VERIFIED -> CURRENTNESS_VERIFIED|CURRENTNESS_REVIEW -> TEXT_VERIFIED -> STRUCTURED -> EXTRACTED -> CROSS_CHECKED -> KB_READY`.

Knowledge item: `DRAFT -> SOURCE_VERIFIED -> REVIEW_REQUIRED|VERIFIED -> KB_READY`.

## Mandatory outputs per stream
- document verification ledger;
- currentness/version-chain ledger;
- structured source index;
- extracted definitions/concepts;
- atomic requirement set;
- contradiction/overlap findings;
- unresolved review queue;
- coverage statistics;
- list of documents reaching `KB_READY`.

## Acceptance gates
A stream is not complete merely because a file was parsed. Completion requires:
- 100% of shard artifacts accounted for by SHA-256;
- 0 silent identity collisions;
- 0 requirements without exact source anchor;
- 0 invented technical controls promoted as legal requirements;
- exact duplicates linked rather than re-extracted;
- empty/corrupt files blocked and reported;
- GOST currentness does not imply applicability;
- contradictions and ambiguity stay explicit;
- all unresolved items are in a review queue.

## Production telemetry
Report per stream and cumulative:
- artifacts assigned / processed / blocked / KB_READY;
- throughput per pass;
- exact duplicates and rework share;
- identity/currentness review backlog;
- contradictions found;
- remaining volume;
- speedup vs 1-stream baseline only when a measured single-stream baseline exists;
- ETA only when sufficient telemetry exists. Never invent numbers.
