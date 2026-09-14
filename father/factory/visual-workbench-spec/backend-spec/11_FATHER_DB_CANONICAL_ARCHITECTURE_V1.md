# FATHER DB Canonical Architecture v1

Status: `CANDIDATE_CANONICAL / ONE DATABASE FOR ALL FATHER DIVISIONS`

## 1. Core decision

FATHER uses **one physical PostgreSQL database** for the operational canonical state:

```text
PostgreSQL database: osint_kb
```

Do not create parallel knowledge databases such as:

- `father_db`;
- `alina_db`;
- a second `knowledge_factory` database;
- per-agent vector databases;
- a full duplicate `kf.*` mirror of already canonical domain objects.

Any proposal to introduce a second operational source-of-truth database requires a separate material ADR with migration, consistency, authority and failure analysis.

## 2. Logical schema target

Target logical structure inside `osint_kb`:

```text
osint_kb
│
├── staging          incoming corpora, import, quarantine
├── source           Source / Capture / provenance / versions
├── normative        NPA / standards / requirements / applicability / versions
├── knowledge        concepts / claims / ideas / methods / algorithms
├── ontology         terms / definitions / canonical entities
├── osint            cases / observations / claims / hypotheses / entities
├── graph            derived canonical graph projection
├── review           decisions / validation / conflicts / approvals
├── weights          append-only weight versions
├── agents           FATHER/ALINA/OSINT/Security profiles / prompts / runs
├── rag              retrieval configs / embedding metadata / vector refs
├── security         classification / access / security review
├── audit            append-only event log / snapshot manifests
└── git_export       explicitly allowed reviewed/sanitized projection
```

This is a **target logical model**, not an instruction to create all schemas immediately.

## 3. Existing schemas are reconciled, not duplicated

Known existing schemas such as:

```text
normative
knowledge
ontology
osint
public
security_core
security_advanced
```

must be inventoried and mapped using one of four actions:

- `KEEP` — already canonical enough; preserve as-is;
- `EXTEND` — add missing columns/tables/constraints/indexes;
- `RENAME_VIEW` — preserve physical table but expose canonical naming through view/adapter;
- `NEW` — create only when no canonical equivalent exists.

No destructive migration is allowed before reconciliation and migration acceptance.

## 4. Earlier isolated kf.* concept is superseded by reconciliation

Earlier concept:

```text
existing schemas
+ kf.source
+ kf.knowledge_object
+ kf.graph_node
...
```

is refined into:

```text
existing osint_kb domain schemas = canonical operational model
+ only missing governance/infrastructure tables
```

Example anti-duplication rule:

```text
osint.claims
AND
kf.knowledge_object(type='claim')
```

must not both become canonical sources of truth.

Instead:

```text
osint.claims
    ↓ canonical adapter / object API
knowledge object projection
```

## 5. Mandatory design elements retained from the kf concept

The following ideas remain mandatory across the unified database:

- `Source / Capture` versioning;
- `SourceSpan` / precise locators;
- stable canonical IDs;
- `origin_class`;
- classification;
- `git_export_allowed`;
- universal `ReviewDecision`;
- append-only `WeightVersion`;
- append-only `AuditEvent`;
- append-only/versioned `SnapshotManifest`;
- object/source provenance;
- graph as projection rather than independent truth;
- PostgreSQL + pgvector as shared embedding layer;
- Git-safe reviewed/sanitized projection.

## 6. Universal provenance invariant

Every material knowledge object must be able to resolve through:

```text
Source
  → Capture / SourceVersion
  → SourceSpan / locator
  → Object / Claim / Requirement / Method / Algorithm
```

If a material object cannot resolve to evidence, it must explicitly carry a valid non-evidence state such as:

- `OWNER_DECISION`;
- `ASSUMPTION`;
- `UNKNOWN`;
- `HYPOTHESIS`;
- `DERIVED_CALCULATION` with resolvable inputs.

No LLM/parser output may silently skip this provenance boundary.

## 7. Graph is a projection

`graph.*` stores a query-optimized projection of canonical objects and relations.

It must not become an independent authoring source.

Canonical direction:

```text
canonical domain object/relation
        ↓
projection/rebuild
        ↓
graph
```

If graph is lost, it must be rebuildable from canonical state.

## 8. Shared vector layer

Use shared PostgreSQL/pgvector infrastructure where vector search is justified.

Do not create one separate vector database per FATHER division or agent.

Embedding records must retain at least:

- object/source reference;
- chunk/span reference;
- embedding model ID/version;
- transform/chunker version;
- dimensions;
- created_at;
- index generation/version;
- classification/data-policy constraints.

Vector index is derivative/rebuildable, not evidence truth.

## 9. Weight versioning

Weights are append-only/versioned.

Never overwrite only a `final_weight` field without history.

Each weight revision should preserve:

- `weight_id` / logical subject;
- version;
- previous version reference;
- method/formula version;
- factors/features;
- evidence refs;
- reason for change;
- actor/agent;
- timestamp;
- review/approval state.

## 10. Universal review and audit

`review` and `audit` are common infrastructure for all divisions.

Do not create separate incompatible review/audit systems for ALINA, OSINT, Security, Architecture, etc.

Review records must preserve:

- target canonical ID + revision;
- reviewer/authority;
- decision;
- findings;
- rationale;
- evidence snapshot;
- conditions;
- supersession/reopen state.

Audit is append-only and independent of ordinary application logs.

## 11. FATHER divisions share one canonical state

Logical picture:

```text
                 FATHER
          orchestration / governance
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      ALINA       OSINT      Security
    Analysis/TI   cases       knowledge
        │           │           │
        └───────────┼───────────┘
                    ▼
                 osint_kb
                    │
          CANONICAL OPERATIONAL STATE
```

FATHER divisions use shared canonical IDs and role-scoped APIs/views.

No division owns a private copy of canonical knowledge.

## 12. KNOWLEDGE_CORE role

The repositories and database have different responsibilities:

```text
KNOWLEDGE_CORE
= source corpus references + Git provenance + reproducible definitions/specs/artifacts

PostgreSQL / osint_kb
= operational canonical state

Git
= DDL + policies + manifests + reviewed/sanitized public projection

protected/local/object storage
= originals + protected files + full backups
```

`KNOWLEDGE_CORE` is not a competing operational database.

## 13. Unified data/knowledge lifecycle

All divisions use one lifecycle:

```text
D0 RECEIVE
↓
D1 REGISTER / SHA / PROVENANCE
↓
STAGING
↓
IDENTITY RESOLUTION
↓
SOURCE / CAPTURE
↓
D4 STRUCTURE
↓
D5–D7 IDEA / CLAIM / KNOWLEDGE
↓
D8 METHOD / ALGORITHM
↓
D9 SCENARIOS
↓
D10 CONDITIONS
↓
D11 VALIDATION
↓
D12 CANONICAL PROPOSAL
↓
D13 REVIEW
↓
CANONICAL DB
↓
GRAPH / RAG PROJECTIONS
↓
GIT-SAFE SNAPSHOT
```

Detailed state names may evolve, but no direct bypass from ingest/parser/model output into canonical truth is allowed.

## 14. Canonical invariants

1. One physical operational PostgreSQL database: `osint_kb`.
2. One canonical source of truth per semantic object.
3. Existing schemas are reconciled before new ones are created.
4. Staging is isolated from canonical state.
5. Provenance resolves `Source → Capture/Version → Span → Object`.
6. Graph is a derivative projection.
7. Weights are append-only/versioned.
8. Review and audit are universal infrastructure.
9. FATHER, ALINA, OSINT and Security use shared canonical IDs.
10. pgvector is shared; per-agent vector silos are prohibited by default.
11. Git export is explicit allow-list/reviewed projection only.
12. No automatic LLM/parser promotion into canonical state.
13. Existing tables are not deleted before reconciliation/migration acceptance.
14. Any duplicate canonical representation must be resolved through `KEEP / EXTEND / RENAME_VIEW / NEW`.
15. A second operational database requires a material ADR.

## 15. Workbench integration

The Visual Engineering Workbench backend must consume this architecture directly.

The Workbench must not introduce a separate persistence universe for requirements, threats, ADRs, tests or evidence if canonical equivalents already exist in `osint_kb`.

Workbench domain APIs may expose normalized objects/adapters over existing tables.

Example:

```text
existing osint/normative/knowledge row(s)
        ↓
canonical adapter / application API
        ↓
Workbench object model
        ↓
views / graph / trace / impact
```

## 16. Migration strategy before DDL

Before creating or altering schemas:

1. inventory actual `osint_kb` schemas/tables/views/extensions/indexes;
2. identify canonical semantic owner for every existing table;
3. map each target v1 object to existing physical structures;
4. classify `KEEP / EXTEND / RENAME_VIEW / NEW`;
5. identify duplicates/conflicts;
6. design compatibility views/adapters;
7. define migration/reconciliation tests;
8. define rollback;
9. approve migration plan;
10. only then write DDL.

## 17. Exit criterion

`FATHER_DB_CANONICAL_ARCHITECTURE_V1_READY` means:

- all current schemas/tables are inventoried;
- every target domain family has a canonical owner;
- duplicate truth sources are identified;
- `KEEP / EXTEND / RENAME_VIEW / NEW` matrix is reviewed;
- provenance/review/audit/weights/graph/RAG invariants are accepted;
- Workbench backend design references `osint_kb` only;
- migration tests and rollback are specified;
- no destructive DDL has been executed yet.
