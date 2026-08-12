# FSTEK requirement atomization

This directory converts regulator documents into machine-readable, traceable and auditable requirements.

Pipeline:

`SOURCE -> EXTRACT -> ATOMIZE -> LINK -> REVIEW -> VERIFIED -> CHECKLIST`

## Core rule

The source document remains authoritative. Structured records are an index and reasoning layer, not a replacement for the regulatory text.

Each atomic requirement must retain:

- canonical source document ID;
- exact source locator;
- obligated subject;
- action/obligation;
- protected object/process;
- applicability conditions;
- expected implementation evidence;
- links to amendments and related acts;
- verification status.

## Verification barrier

`VERIFIED` is allowed only when the requirement is supported directly by the ingested source and has a source locator. Items inferred from document relationships, summaries, or general security practice remain `DRAFT` or `EXTRACTED`.

## Output use

Verified requirements can feed:

1. compliance checklists;
2. gap analysis;
3. architecture requirements;
4. technical specifications;
5. evidence collection;
6. control matrices;
7. knowledge graph / RAG retrieval;
8. future compliance agents.
