# Local laws and GOST intake — 2026-08-27

## Scope

Source basis: user-supplied `library_inventory.sqlite` (SHA-256 `0cb27edd99c134a0c3465b4528b5c55a30361c6db84064361db62952d1e6638f`, 2,314,240 bytes).

This pass transfers local **source identities and provenance metadata** into the canonical Security Knowledge repository. It does not claim that every local artifact is byte-verified, current in law, applicable to a specific organization, or atomized into requirements.

## Results

- Local files registered: **66** = 46 GOST-related files + 20 federal-law files.
- Unique source identities registered: **61** = 45 standards + 16 federal laws.
- GOST identities with current-status evidence from the existing Rosstandart/protect.gost.ru registry: **45/45**.
- Federal-law identities: **16**, all kept at `REVIEW_REQUIRED` for currentness/version-chain in this intake.
- Known exact local hashes available in this pass: **2 files**, both RTF variants of `ГОСТ Р 56939-2024`, and both share SHA-256 `0d9961c85319ef4bfbcc5b078dcda5fc6f356b19eb3e3e6d20e310eaf45ed843`.
- `ГОСТ Р 59548-2022`: prior evidence indicates multiple distinct SHA-256 variants; preferred artifact selection remains blocked pending identity review.
- No files on `G:` were moved, renamed, deleted, or overwritten by this GitHub-side intake.
- No full GOST text was republished into the public repository.

## Knowledge maturity

Current state is **source registration / provenance ingestion**:

`LOCAL_ARTIFACT -> SOURCE_IDENTITY -> PROVENANCE -> STATUS_GATE -> VERIFIED_SOURCE_TEXT -> ATOMIC_REQUIREMENTS -> RELATIONS -> EXPERT_REVIEW`

This pass closes the first two layers for the discovered laws and standards. It does **not** promote filename metadata into legal requirements. `.ai/regulatory-extraction-policy.yaml` requires verified text and exact anchors before requirement atomization.

## Registries created

- `security-knowledge/corpus/ru-standards/gost-local-source-registry-2026-08-27.yaml`
- `security-knowledge/corpus/ru-protected-information/federal-laws-local-source-registry-2026-08-27.yaml`
- `security-knowledge/corpus/ru-standards/README.md`

## Key guards

1. Rosstandart `CURRENT` describes standard currentness only; it does not infer legal applicability.
2. Federal-law filename date/number/title is intake identity evidence, not proof of the current consolidated wording.
3. Same-number acts remain distinct by date and title; in particular, `63-ФЗ` of 31.05.2002 and `63-ФЗ` of 06.04.2011 are separate identities.
4. Multi-format copies are variants until SHA-256/content identity proves an exact duplicate.
5. Source text, normalized requirement, interpretation, control mapping and verification mapping remain separate layers.

## Next gates

- Compute SHA-256 for all remaining local law/GOST artifacts and store exact-byte provenance.
- Resolve the `ГОСТ Р 59548-2022` variant collision.
- Verify law currentness/version chains against authoritative sources.
- Extract text and structure from verified artifacts.
- Atomize definitions/requirements with exact article/clause anchors.
- Run cross-source contradiction/applicability review before expert promotion.

## Production telemetry

No valid single-stream baseline or elapsed-time-per-document telemetry was captured for this GitHub-side intake. Therefore acceleration percentage, throughput comparison and ETA are intentionally reported as **N/A** rather than invented.
