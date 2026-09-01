# Security Knowledge — Codex instructions

These rules apply to everything under `security-knowledge/` and extend the repository root `AGENTS.md`.

## Workforce orchestration

For Security Knowledge production work, read `.ai/codex-local-workforce.yaml` and `.ai/task-queue/security-kb.yaml` before planning. For complex tasks, delegate independent bounded work to the project custom agents in `.codex/agents/`.

Prefer parallel subagents for read-heavy research, status checks, classification, annotation and independent review. Keep write ownership bounded: parallel agents must not edit the same shared inventory. Integrate accepted evidence before running `reconciler`, and run `qa_guard` after reconciliation. The main agent remains responsible for the final auditable decision; subagent consensus is not proof.

## Canonical acquisition gate — fail closed

A primary document may become an immutable captured source only after all required evidence is available and internally consistent:
1. exact official source route;
2. exact official bytes;
3. UTC `retrieved_at`;
4. MIME plus file-signature/magic validation where applicable;
5. exact byte length;
6. SHA-256 over the captured bytes;
7. immutable artifact reference;
8. manifest linking the artifact to source identity and acquisition evidence.

If any required element is missing, keep the source `PENDING`/`UNKNOWN` as appropriate. Never synthesize missing values. Never substitute a commercial/secondary mirror for the missing primary immutable payload.

## Source identity versus file representations

Deduplicate at two different levels and never confuse them:

- `source_identity` means the logical legal/methodological document (for example one Constitution, one federal law, one order, one edition/version of an act);
- `representation` means one physical rendition of that same source identity (for example PDF, ODT, DOCX, RTF, HTML snapshot, scan, XML, signed container, or a third-party reference copy).

Rules:
- one logical source identity may and often should retain multiple useful representations;
- PDF and ODT of the same act are not duplicate source identities and must not cause the second format to be discarded merely because the title/document identity matches;
- each physical representation gets its own `representation_id`, format/MIME, source route or local provenance, `retrieved_at`, byte length and SHA-256;
- byte-identical files are physical duplicates and may be stored once by content hash while preserving all observed filenames/locations as provenance aliases;
- byte-different representations of the same logical act must be retained separately when they have evidentiary, extraction, layout, signature, OCR or archival value;
- official and third-party copies are never merged semantically: they may point to the same `source_identity`, but each keeps its own provenance and authority class;
- a third-party PDF/ODT can be retained as `third_party_reference_copy` while the official immutable representation remains `PENDING`;
- source counters count logical documents unless a metric explicitly says `representation_count`; do not inflate document counts by counting formats;
- representation counters may separately report PDF/ODT/etc. coverage and exact-byte duplicates removed.

Preferred conceptual structure:
`source_identity -> version/edition -> representations[] -> physical_artifact_sha256`.

## Status and version chain

For normative and methodological sources, record separately:
- identity;
- legal/publication/registration status when applicable;
- current/effective status at the checked date;
- amendment/replacement/supersession chain;
- evidence for each transition.

A draft target date does not activate a replacement. A future-effective act does not become currently effective before its proven date. Recheck time-sensitive transitions against primary evidence.

## Applicability is separate from topic classification

Never infer a legal obligation from taxonomy membership. Keep an explicit applicability edge/guard.

Examples of guarded neighboring regimes include licensing, certification, KII, GosSOPKA/NCCCI, government information systems, attestation, secure development, and crypto lifecycle obligations. Import a requirement into a PDN context only when the applicability edge is proven.

For the 152-FZ technical/crypto contour in particular:
- FSB Order 378 is relevant to ISPDN when SKZI is actually used;
- licensing requirements apply only to the licensed activity they regulate;
- KII/GosSOPKA material enters the PDN branch only when an independent legal/incident applicability edge exists.

## InfoSec taxonomy layer

The Habr information-security guide at `https://habr.com/ru/articles/432466/` is a navigational taxonomy seed, not a source of law.

Classify each material with multi-label metadata:
- `primary_category`
- `secondary_categories[]`
- `taxonomy_roles[]`, using `CORE`, `CONDITIONAL`, or `REFERENCE_ONLY`
- `document_type`
- `issuer`
- `authority_level`
- `evidence_status`
- `legal_status`
- `applicability`
- `source_provenance`

One source may belong to many topical categories while retaining one canonical source identity/artifact.

Descriptions imported from the guide must be concise paraphrases, preserve provenance, and be marked `SOURCE_PARAPHRASE_DRAFT`. Do not copy long copyrighted passages. `OTHER`/`MISC` is a temporary quarantine category and requires later review.

## Intake pipeline

Use this conceptual order:
`material -> identity -> version/edition -> representation -> taxonomy -> provenance -> status/version -> applicability -> official bytes -> immutable manifest -> extraction -> norms/concepts/definitions -> graph links -> inventory reconciliation -> QA`.

## Stream 2 — PDN technical and cryptographic contour

Current priority class includes:
- PP RF 1119;
- FSTEC Order 21 and verified replacement/amendment watch;
- FSTEC Threat Assessment Methodology 2021;
- relevant FSTEC catalogs and methodologies;
- FSB Order 378;
- related current SKZI, licensing and certification acts with bounded applicability;
- NCCCI/GosSOPKA only when linked to PDN incident applicability.

Do not grow the source count with unrelated documents merely to increase coverage metrics.

## Reconciliation gate

After acquisition/classification changes, update the appropriate source inventory/master inventory and counters through existing reconciliation tooling where available. Distinguish authoritative reconciled counts from estimates or arithmetic overlays. Never hand-edit a counter to hide failed acquisition or stale graph state.
