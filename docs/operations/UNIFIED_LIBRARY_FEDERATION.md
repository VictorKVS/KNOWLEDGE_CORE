# Unified Library Federation

## Goal

Create one auditable logical catalog over all KNOWLEDGE_CORE/FATHER/local libraries without destructively merging source directories.

The federation does **not** mean copying every file into one ordinary folder. It means that every observed item is mapped through a common identity model:

`collection -> document_identity -> version/edition -> representation -> physical_artifact(SHA-256) -> location_aliases[]`

This preserves source provenance, versions and useful file formats while removing only exact byte duplicates at the physical-artifact layer.

## Mandatory inputs

Read before work:

- `AGENTS.md`
- `REPOSITORY_STRUCTURE_PROTECTION.yaml`
- `security-knowledge/AGENTS.md` when Security Knowledge is involved
- `.ai/library-unification.yaml`
- `.ai/task-queue/unified-library.yaml`
- `.ai/evidence-policy.yaml`
- `.ai/agent-collaboration-policy.yaml`

## Libraries to federate

Codex must discover and register all actually accessible collections, including:

- repository `security-knowledge/`;
- repository `security-corpora/` and other legacy/candidate collections when present;
- repository FATHER knowledge/library stage outputs;
- local regulatory import checkout `G:\1\KNOWLEDGE_CORE_IMPORT_20260827-162116`;
- local FATHER library stage outputs such as `G:\1\FATHER_LIBRARY_STAGE6_LEGAL` and `G:\1\FATHER_LIBRARY_STAGE7` when they exist;
- the user's Downloads staging area for newly downloaded PDF/ODT/etc.;
- existing library inventories/manifests;
- additional known user library roots on available data drives, but only when explicitly discovered and registered.

Do not claim a drive/folder was inspected if it was inaccessible.

## Non-destructive rule

Source libraries are inputs, not disposable staging areas.

Do not:

- delete originals;
- move originals;
- rename originals;
- rewrite files in source collections;
- clean up user directories;
- convert the source library into the canonical layout in place.

Instead, record paths as `location_alias` entries and create content-addressed artifacts only where policy permits.

## Identity and deduplication

### Logical document

One law/book/standard/order/methodology/work = one logical `document_identity`, even if it occurs in many libraries.

### Version or edition

Keep different legal revisions, publication states, book editions, releases or materially different states separate.

Never collapse by title/number alone.

### Representation

Keep useful byte-distinct forms separately:

- PDF
- ODT
- DOC/DOCX
- RTF
- HTML
- XML
- scan/image package
- signed container
- other material representations

PDF + ODT of one version = one logical version, two representations.

### Exact duplicate

Only byte-identical payloads with the same SHA-256 can share one physical artifact.

When several copies have the same SHA-256, preserve every observed library membership, path and filename as provenance aliases.

## Authority and provenance

Authority is attached to each representation, not inferred from document identity.

Examples:

- official primary publication;
- regulator copy;
- official card without downloadable bytes;
- third-party reference copy;
- local reference copy;
- unknown.

An official document card plus a local Garant PDF does not turn the Garant PDF into official immutable evidence. Both can map to the same logical identity while keeping separate authority/provenance.

## Canonical ownership

The federation is a catalog/identity merge, not a protected-directory migration.

- Security/regulatory knowledge keeps canonical logical ownership under `security-knowledge/`.
- Other professional domains keep canonical logical ownership under `professional-knowledge/`.
- FATHER library stages remain pipeline/staging/derived collections and link into canonical identities.
- `security-corpora/` and legacy roots remain source collections until an explicit migration record authorizes structural movement.

This respects `REPOSITORY_STRUCTURE_PROTECTION.yaml`.

## Public Git versus local blobs

Use Git as the metadata/control plane.

For large or copyright-sensitive material, keep the physical original in the local content-addressed blob store and keep metadata, hashes, provenance and canonical identity links in Git.

Do not publish full books or restricted/copyright-sensitive standards to public Git without confirmed rights. Keep their metadata/hash/provenance instead.

## Execution order

Run the queue in `.ai/task-queue/unified-library.yaml`:

1. register all collections;
2. inventory accessible files non-destructively;
3. hash and exact-byte deduplicate;
4. resolve logical identities;
5. resolve versions/editions;
6. preserve all byte-distinct representations;
7. route into canonical knowledge domains/taxonomies;
8. enforce storage/publication rights;
9. reconcile a single logical catalog;
10. independent QA.

Read-heavy discovery/classification can run in parallel. Shared catalog/inventory writes are single-owner through `reconciler`.

## Codex master prompt

Use this prompt from the repository root:

> Read AGENTS.md, REPOSITORY_STRUCTURE_PROTECTION.yaml, security-knowledge/AGENTS.md, .ai/library-unification.yaml and .ai/task-queue/unified-library.yaml. Federate every actually accessible KNOWLEDGE_CORE, Security Knowledge, security-corpora, FATHER stage, local import, Downloads and registered user-library collection into one non-destructive logical catalog. Do not move/delete/rename originals. Deduplicate physical bytes only by SHA-256 while preserving every location alias. Keep one document_identity across libraries, keep distinct versions/editions, and retain byte-distinct PDF/ODT/etc. representations. Respect public-Git rights boundaries for books and standards. Security canonical ownership remains security-knowledge; non-Security professional ownership remains professional-knowledge. Use parallel read-heavy lanes where independent, but only reconciler may write shared master catalog/counters. Fail closed on uncertain identity/version/provenance. After reconciliation run qa_guard and report reproducible counts and unresolved conflicts.

## Per-pass report

After each pass report only measured values:

- collections registered;
- files observed;
- unique SHA-256 artifacts;
- exact duplicate copies;
- logical documents;
- versions/editions;
- representations total and by format;
- canonical links created;
- unresolved identities;
- version conflicts;
- unreadable/failed files;
- rights/publication blockers;
- protected-path changes (must normally be zero);
- validators run.

Production speed, rework, remaining volume and ETA must be reported only when sufficient telemetry exists.
