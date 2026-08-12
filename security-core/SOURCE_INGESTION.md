# Security Source Ingestion Order

Security Core is populated from authoritative material outward. Pentest checklists and vulnerability catalogs are mapped later; they do not define the legal or regulatory truth.

## Phase 1 — Canonical documents

Each law, decree, regulator order, official methodology, mandatory standard when applicable, and official technical security document is stored as a versioned source record.

Minimum metadata:

- jurisdiction and issuing authority;
- exact document identifier and title;
- official publication/source location;
- publication and effective dates;
- revision/version;
- current/superseded/withdrawn state;
- scope and applicability conditions;
- verification date.

Do not paraphrase away legal qualifiers. The canonical text is evidence; summaries are derived views.

## Phase 2 — Atomic nodes

Source text is decomposed into atomic records:

- definitions;
- obligations;
- prohibitions;
- permissions;
- recommendations;
- applicability conditions;
- required organizational or technical measures.

Every node keeps a back-reference to the exact source and relevant provision/section.

## Phase 3 — Security graph

Atomic requirements are connected to:

`system/data/process/actor → threat/weakness → control → configuration → verification evidence`.

Each non-obvious mapping records its rationale and confidence.

## Phase 4 — External catalogs

Only after the normative and technical graph exists do we map external security catalogs and Top-N lists. Catalog version/date is mandatory. A catalog mapping may enrich a node but cannot silently redefine the source requirement.

## Phase 5 — Pentest knowledge

Pentest checks are derived from a controlled chain:

`authorization & scope → asset → requirement/threat/weakness → test objective → safe method → evidence → finding → remediation`.

A pentest rule must describe prerequisites, allowed scope, stop conditions, expected evidence and limitations. Tool output alone is never equivalent to compliance evidence.

## Phase 6 — Feedback

Verified findings and remediations become outcome evidence. They may strengthen or weaken claims, but promotion follows the normal Knowledge Core promotion policy.

## Separation of views

The same graph can later drive different interfaces:

- compliance/audit view;
- architect view;
- secure configuration view;
- blue-team detection view;
- authorized pentest view;
- developer secure-coding view;
- learning view.

These are views over the same evidence graph, not independent copies of security truth.
