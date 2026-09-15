# Source, Evidence & File Pipeline

Status: `DRAFT_V0.1`

## 1. Purpose

Preserve original materials and provenance so every material engineering conclusion can be traced back to source or explicit authority input.

## 2. Core rule

```text
ORIGINAL BYTES / AUTHORITATIVE RECORD
        ↓ immutable identity
SOURCE VERSION
        ↓ locators
ATOMIC / STRUCTURED EXTRACTION
        ↓
EVIDENCE ITEM
        ↓
EVIDENCE LINK
        ↓
CANONICAL OBJECT FIELD / RELATION / DECISION
```

Derived text, embeddings, summaries and LLM outputs never replace original evidence.

## 3. Source classes

- uploaded file;
- repository file/commit;
- URL/web snapshot;
- API/connector snapshot;
- signed/owner-entered decision;
- normative source;
- test/CI evidence;
- operational telemetry snapshot;
- generated artifact tied to canonical baseline.

Each class defines acquisition and freshness semantics.

## 4. Register source

Registration captures:
- source ID;
- source class;
- title/name;
- owning authority;
- origin locator;
- classification;
- applicability scope;
- expected freshness/effective status;
- retention rule candidate.

## 5. Register source version

Each version captures:
- source ID;
- version ID;
- content hash where bytes available;
- byte size;
- MIME/content type;
- acquisition timestamp;
- effective/superseded metadata;
- external revision/commit ID where applicable;
- immutable storage key;
- parsing status.

## 6. File upload security

Upload pipeline:

```text
receive stream
→ size/type policy
→ temporary quarantine
→ hash
→ malware/content validation hooks
→ metadata extraction
→ classification policy
→ immutable storage
→ source version registered
```

Rejected/quarantined bytes must not become normal evidence.

## 7. Source locators

Locator identifies exact supporting region without duplicating source text.

Possible locator types:
- line range;
- page range;
- paragraph/block ID;
- JSON pointer;
- spreadsheet sheet/cell range;
- repository path + commit + lines;
- API response field path;
- timestamp/time-window;
- test case/result ID.

Locator must be resolvable against exact source version.

## 8. Evidence item

Evidence item records a bounded proposition or observation plus provenance:
- statement/observation;
- source version;
- locator;
- evidence class;
- extracted by;
- extraction method/version;
- verification state;
- confidence where probabilistic;
- timestamps/applicability.

## 9. Evidence link semantics

Evidence link expresses relationship to engineering object/field/edge:
- SUPPORTS;
- CONTRADICTS;
- QUALIFIES;
- SUPERSEDES;
- EXAMPLE_ONLY;
- OWNER_DECISION;
- TEST_EVIDENCE;
- OPERATIONAL_EVIDENCE.

Do not collapse `SUPPORTS` and `PROVES` into one vague concept.

## 10. Field-level provenance

Material object fields may have independent evidence links.
Example: Requirement title may be owner-authored while threshold and legal constraint come from separate sources.

Backend must support `GET field evidence` and show coverage gaps.

## 11. Parsing boundary

Parsing creates derived objects:
- extracted text;
- layout blocks;
- tables/figures/formulas;
- metadata;
- semantic units;
- candidate atomic items.

All derived records store:
- source version;
- parser/tool version;
- transformation version;
- exact locator where possible.

## 12. Brownfield mapping

Mapping existing document to canonical artifacts is candidate interpretation.

Flow:

```text
parsed material
→ atomic items
→ candidate artifact field mapping
→ completeness/conflict analysis
→ owner/domain review
→ canonical candidate objects
```

A file named “Architecture.docx” does not automatically satisfy architecture artifacts.

## 13. Source freshness

Freshness status:
- CURRENT;
- STALE_CANDIDATE;
- SUPERSEDED;
- EFFECTIVE_FUTURE;
- HISTORICAL;
- UNKNOWN_EFFECTIVITY.

Material decisions referencing stale/superseded source trigger policy-based review.

## 14. Normative sources

Before a normative rule becomes automatic blocker, backend must have exact trace:

`source version → clause/locator → normalized requirement → applicability → affected artifact/gate rule`.

No clause evidence = advisory only, not automatic legal blocker.

## 15. Source conflict

When two sources disagree:
- preserve both;
- classify authority/applicability/version;
- create Conflict object;
- do not overwrite lower-authority source;
- resolve by authority/owner decision with rationale;
- retain historical resolution.

## 16. Generated artifacts

Generated PDF/DOCX/report may be exported evidence package but is derived from canonical model. It stores:
- generating baseline;
- generator version;
- template version;
- source object revision set;
- checksum.

## 17. Evidence integrity checks

Deterministic tests:
- source hash still matches stored bytes;
- locator resolves;
- source version exists;
- target object/revision exists;
- evidence classification valid;
- no evidence link silently retargeted to newer source revision.

## 18. Future AI interaction

AI may propose extraction/mapping/evidence relevance, but:
- original source remains untrusted content;
- AI cannot reinterpret source text as system/tool instruction;
- every material extracted claim retains locator;
- unsupported material claims fail closed or NEEDS_REVIEW;
- source scope cannot be expanded without policy/user authorization.
