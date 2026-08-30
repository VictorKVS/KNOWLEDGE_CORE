# FATHER Source Processing & Crosswalk Method

Status: ACTIVE METHOD
Owner: FATHER Analyst / Architect / Legal / Security

## Purpose

FATHER must not process all documents as generic RAG text. Source types have different authority, semantics and extraction contracts.

Canonical source classes:

1. LAW / GOVERNMENT NPA
2. AGENCY ORDER / REGULATOR NPA / METHODICAL DOCUMENT
3. STANDARD (GOST / GOST R / ISO / IEC / IEEE / PNST)
4. BOOK / PROFESSIONAL EVIDENCE
5. INTERNAL EXPERIENCE / TEST / PRODUCTION OUTCOME

All sources join one graph, but authority and applicability are never flattened into one confidence score.

## Universal source identity

Every source receives:

- source_id
- source_kind
- title
- issuer / author
- number
- date_signed
- date_published
- effective_from / effective_to
- revision_id
- source_url
- source_trust_tier
- sha256
- language
- legal_status
- currentness_status
- applicability_scope
- supersedes / superseded_by
- amends / amended_by
- official_source_evidence
- processing_run_id
- trace_id

Original source remains immutable. Normalized text, OCR, translation, interpretation and knowledge are separate layers.

## A. LAW / GOVERNMENT NPA pipeline

`OFFICIAL ORIGINAL -> IDENTITY -> EFFECTIVE STATUS -> STRUCTURE -> DEFINITIONS -> SUBJECTS/OBJECTS -> CONDITIONS -> OBLIGATIONS/PROHIBITIONS/RIGHTS -> DEADLINES -> EXCEPTIONS -> SANCTIONS/CONSEQUENCES -> CROSS-REFERENCES -> AMENDMENT GRAPH -> APPLICABILITY -> ATOMIC LEGAL REQUIREMENTS -> REVIEW`

Required extraction unit:

`Article -> Part -> Clause -> Subclause -> Atomic Norm`

Atomic norm fields:

- legal_requirement_id
- actor
- modality: MUST / MUST_NOT / MAY / RIGHT / CONDITION / EXCEPTION
- action
- object
- trigger
- deadline
- jurisdiction/scope
- evidence locator
- source revision
- effective interval

Never infer an operational control from a law unless the law says it. Instead link the legal requirement to lower-level documents or to an internal control as an interpretation/implementation relation.

## B. AGENCY ORDER / REGULATOR pipeline

`ORDER -> ISSUER -> AUTHORITY BASIS -> MINJUST/REGISTRATION METADATA WHEN APPLICABLE -> SCOPE -> DEFINITIONS -> REQUIREMENTS -> PROCEDURES -> ANNEXES -> FORMS -> CONTROLS -> EVIDENCE -> HIGHER-LEVEL LEGAL BASIS -> LOWER-LEVEL METHODS/STANDARDS`

Additional fields:

- agency
- authority_basis
- registration_number/date if present
- target_system/type
- regulated_subject
- annex_id
- measure/control code if source defines it
- reporting/evidence requirement

Departmental grouping is a projection, not separate truth:

- FSTEC
- FSB
- Roskomnadzor
- Ministry of Digital Development
- Government / President
- other regulators

Relations:

- IMPLEMENTS
- DETAILS
- BASED_ON
- ISSUED_UNDER_AUTHORITY_OF
- REQUIRES
- REFERENCES
- AMENDS
- SUPERSEDES
- APPLIES_TO

## C. STANDARD pipeline

`STANDARD -> STATUS/CURRENT VERSION -> SCOPE -> NORMATIVE REFERENCES -> TERMS -> REQUIREMENTS -> RECOMMENDATIONS -> PROCESS -> ROLE -> INPUT/OUTPUT ARTIFACT -> QUALITY ATTRIBUTE -> VERIFICATION METHOD -> TESTABLE CONTROL -> FATHER MAPPING`

Requirement types:

- normative requirement
- recommendation
- definition
- process requirement
- documentation requirement
- verification requirement
- metric/quality criterion

For Russian standards, applicability is separate from technical value. National standards are generally voluntary unless legislation, contract, declaration of conformity, or another legally relevant mechanism makes the referenced requirement binding. Never convert a GOST requirement into a legal obligation without a legal applicability edge.

Relations:

- ADOPTS
- IDENTICAL_TO
- MODIFIED_FROM
- REFERENCES
- REPLACES
- IMPLEMENTS_REQUIREMENT
- VERIFIES
- TESTS
- DEFINES_ARTIFACT
- DEFINES_PROCESS

## D. BOOK pipeline

`BOOK ORIGINAL -> IDENTITY/EDITION -> TRANSLATION WHEN NEEDED -> CHAPTER/SECTION -> CLAIMS -> DEFINITIONS -> PRINCIPLES -> PATTERNS -> ANTI-PATTERNS -> DECISION RULES -> TRADE-OFFS -> METRICS -> FAILURE MODES -> EXAMPLES -> CROSS-SOURCE CORROBORATION -> ROLE TAGS -> KNOWLEDGE REVIEW`

Book knowledge is professional evidence, not law.

Knowledge types:

- CONCEPT
- DEFINITION
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

Every node retains chapter/page/source locator and edition.

## E. Crosswalk engine

Crosswalk is performed after source-specific extraction.

### Exact relation pass

Create relations only when explicitly cited or structurally clear:

- LAW -> ORDER
- ORDER -> GOST
- GOST -> ISO
- REQUIREMENT -> CONTROL
- CONTROL -> TEST
- BOOK PATTERN -> ARCHITECTURE DECISION

### Semantic candidate pass

Semantic similarity creates CANDIDATE relationships only:

- RELATED_TO
- POSSIBLE_IMPLEMENTATION_OF
- POSSIBLE_CONFLICT_WITH
- POSSIBLE_DUPLICATE_OF

Candidate relations require deterministic checks and/or analyst review before promotion.

### Contradiction pass

A contradiction candidate requires:

- same or overlapping subject/object
- compatible applicability interval
- incompatible modality/action/constraint
- source locators for both sides

Never mark a contradiction merely because wording differs.

### Gap pass

Detect gaps such as:

- binding requirement with no implementing control
- control with no legal/standard/professional rationale
- architecture component with no requirement
- security requirement with no verification evidence
- GOST verification requirement with no automated/manual test
- book pattern used in ADR with no context/trade-off record

## Authority and applicability model

Keep dimensions separate:

- AUTHORITY: legal / official-standard / regulator-method / professional / internal-experience
- CURRENTNESS: current / superseded / draft / unknown
- APPLICABILITY: applicable / not-applicable / conditional / needs-review
- EVIDENCE QUALITY: exact / indirect / inferred / unknown

Do not collapse these into one opaque score.

## Core graph

`LAW -> ORDER -> STANDARD -> REQUIREMENT -> CONTROL -> ARCHITECTURE_ELEMENT -> API -> CODE -> TEST -> TRACE -> EVIDENCE -> PRODUCT`

Parallel professional evidence:

`BOOK -> PRINCIPLE/PATTERN -> ADR -> ARCHITECTURE_ELEMENT`

Production learning:

`PRODUCT -> OUTCOME -> LESSON -> DECISION_MEMORY -> KNOWLEDGE`

## Acceptance gates

A source is not promoted to canonical knowledge unless:

1. identity and SHA are recorded;
2. exact source locator exists;
3. currentness is known or explicitly NEEDS_REVIEW;
4. source type contract passed;
5. interpretation is separated from source statement;
6. relationships preserve direction and authority;
7. trace_id links extraction/review/promotion;
8. contradictions/gaps are not silently hidden.
