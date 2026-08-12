# Russian Federal Laws — Security Knowledge Corpus

This directory is the canonical landing zone for federal-law knowledge objects used by the Security Knowledge Base.

## Ingestion rule

Each law is represented as a version-aware knowledge package rather than a single PDF:

`source metadata → structure → definitions → atomic requirements → workflows/checklists → intra/inter-document links → applicability → controls/checks/evidence`

The original uploaded binary is preserved outside this GitHub text connector until a binary-source ingestion action is available. Repository records therefore identify the source attachment and extraction state explicitly; they must not pretend that a raw immutable binary is present when it is not.

## Current corpus

| Document | Domain | Current ingestion state |
|---|---|---|
| 126-FZ — On Communications | communications / network security | REGISTERED + seed extraction |
| 187-FZ — On Security of Critical Information Infrastructure | KII / incident response / infrastructure security | REGISTERED + seed extraction |
| 98-FZ — On Commercial Secrets | confidentiality / information governance | REGISTERED + seed extraction |

152-FZ and 149-FZ are handled in the wider regulatory corpus and will be normalized into the same package layout as the corpus is consolidated.

## Package layout

Each document directory may contain:

- `document.yaml` — canonical document/source metadata;
- `README.md` — human-readable status and scope;
- `structure/` — legal structure and chunks;
- `definitions/` — statutory terms and roles;
- `requirements/` — atomic `SEC-REQ-*` candidates;
- `workflows/` — organization/specialist decision logic;
- `checklists/` — organization, specialist and auditor views;
- `links/` — typed intra/inter-document graph edges;
- `source/` — source capture metadata and, when technically possible, immutable raw source.

No requirement is promoted to `VERIFIED` solely because it was machine-extracted. Legal/source verification is a separate state transition.
