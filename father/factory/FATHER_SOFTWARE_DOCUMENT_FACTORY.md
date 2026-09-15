# FATHER Software Document Factory

Status: `CANDIDATE / FACTORY MODEL`

Purpose: turn the FATHER Constitution, normative sources and professional knowledge into a reproducible engineering production line where every material software/system decision is supported by traceable artifacts, owners, inputs, reviews and gates.

## 1. Core idea

FATHER does not generate documents for paperwork's sake. It produces and verifies **canonical information artifacts**. One artifact may be represented as Markdown, YAML, JSON, OpenAPI, diagram, code, SARIF, SBOM, test result or a signed office document depending on purpose and legal/contractual requirements.

Canonical chain:

```text
NORMATIVE SOURCES / PROFESSIONAL SOURCES
        ↓
REQUIREMENT / PRACTICE EXTRACTION
        ↓
FATHER ARTIFACT MODEL
        ↓
PROJECT INTAKE
        ↓
EXISTING MATERIAL DISCOVERY
        ↓
ATOMIC FACT / CLAIM / REQUIREMENT EXTRACTION
        ↓
ARTIFACT MAPPING
        ↓
CONFORMANCE + GAP + CONFLICT ANALYSIS
        ↓
CREATE / COMPLETE ONLY WHAT IS MISSING
        ↓
OWNER CONFIRMATION
        ↓
INDEPENDENT REVIEW
        ↓
GATE
        ↓
NEXT STAGE
```

## 2. Factory registries

The factory is driven by machine-readable registries:

- `NORMATIVE_SOURCE_REGISTRY.yaml` — current standards, regulator orders, government resolutions and supersession state;
- `SOURCE_ARTIFACT_MAPPING.yaml` — which source affects which artifact family;
- `FATHER_LIFECYCLE_STAGES.yaml` — stages, mandatory roles, inputs, outputs and gates;
- `FATHER_ARTIFACT_REGISTRY.yaml` — canonical project artifacts and ownership;
- `FATHER_ROLE_MATRIX.yaml` — professional responsibilities and authority boundaries;
- FATHER Constitution — immutable ordering and evidence rules.

## 3. Two operating modes

### Greenfield

Little or no documentation exists. The factory creates candidate artifacts in dependency order, obtains authoritative input and moves them through owner review.

```text
MISSING → DRAFT → OWNER_REVIEW → CONFIRMED → VERIFIED
```

### Brownfield

The project already has specifications, diagrams, tickets, contracts, APIs, code and operational evidence. FATHER first extracts and maps existing knowledge before creating anything new.

```text
EXISTING SOURCES
  ↓
PARSE / EXTRACT
  ↓
ATOMIC ITEMS
  ↓
MAP TO CANONICAL ARTIFACT FIELDS
  ↓
COMPLETE / PARTIAL / CONFLICTED / GAP / STALE
```

A file name never proves artifact completeness. A single document may cover parts of several canonical artifacts.

## 4. Artifact production algorithm

For every expected artifact:

1. Resolve applicability from product scope, system type and regulatory overlays.
2. Identify accountable owner and required reviewers.
3. Resolve prerequisite artifacts and evidence.
4. Search existing project materials for relevant information.
5. Extract atomic items and classify them as `FACT / CLAIM / REQUIREMENT / CONSTRAINT / ASSUMPTION / DECISION / RISK / UNKNOWN`.
6. Preserve source, owner, date/version and applicability.
7. Map atomic items to required artifact fields.
8. Detect missing fields, stale data and contradictions.
9. Request missing authoritative input from the correct owner.
10. Draft only the unresolved canonical representation; never invent owner facts.
11. Perform owner confirmation.
12. Perform required professional and independent review.
13. Run artifact gate rules.
14. Publish artifact status and downstream outputs.
15. Record feedback when downstream evidence invalidates an assumption or decision.

## 5. Security invariant

The factory follows the constitutional sequence:

```text
PRODUCT
  ↓
SECURITY INTAKE
  ↓
SYSTEM ENGINEERING ↔ SECURITY
  ↓
THREAT MODEL v0
  ↓
REQUIREMENTS BASELINE
  ↓
ARCHITECTURE OPTIONS
  ↓
SECURITY REVIEW + INDEPENDENT REVIEW
  ↓
ARCHITECTURE DECISION
```

Security is not an audit attached at the end. Security constraints and threat knowledge become inputs to system requirements and architecture.

## 6. Information state model

Every artifact or material field must have an explicit state:

- `EXPECTED` — required but not yet requested;
- `REQUESTED` — requested from owner;
- `RECEIVED` — source received, not yet verified;
- `PARTIAL` — incomplete or ambiguous;
- `CONFLICTED` — incompatible evidence exists;
- `GAP` — missing;
- `DRAFT` — candidate representation exists;
- `OWNER_REVIEW` — awaiting authoritative confirmation;
- `CONFIRMED` — owner accepted project meaning;
- `VERIFIED` — applicable review/evidence gate passed;
- `STALE` — validity/freshness no longer sufficient;
- `REJECTED` — invalidated;
- `NOT_APPLICABLE` — applicability explicitly assessed and rejected.

`UNKNOWN` remains valid inside an artifact. A complete-looking document does not justify closing an unknown.

## 7. Gate principle

A gate is evidence-based, not document-count-based.

Example `SYSTEM_MODEL_READY` does not mean that a file named `system-model.docx` exists. It means required system context, boundary, flows, interfaces, dependencies, operational modes, assumptions and security-relevant views are sufficiently complete for the next decision, with unresolved gaps explicitly bounded.

## 8. Regulatory overlays

Core lifecycle artifacts apply broadly. Regulatory overlays add or tighten requirements only when applicable.

Examples:

- personal data → PP RF 1119 + FSTEC 21; FSB 378 when cryptographic protection is in scope;
- state information systems → current FSTEC 117 requirements;
- KII → PP RF 127, and for significant objects FSTEC 235/239;
- secure software development → GOST R 56939-2024 and related secure-development standards.

The factory must never blindly apply every overlay to every project.

## 9. Knowledge Growth Analyst

The Knowledge Growth Analyst operates the knowledge-production layer of the factory:

```text
profession model
→ source map
→ admitted sources
→ atomic knowledge
→ concepts/relations/conflicts
→ decision logic
→ artifact knowledge
→ examples/failure modes
→ evals
→ retrieval
→ maturity evidence
```

The analyst may build candidate professional KBs for every FATHER role but cannot independently certify domain truth. Domain specialist and skeptical review remain separate assignments.

## 10. Relation to Architect Intake Playbook

The existing `ARCHITECT_PROJECT_INTAKE_PLAYBOOK.md` remains valuable as a candidate architecture-intake inventory. The factory lifts that model one level upward:

- artifacts are no longer architect-owned by default;
- Security enters before System Engineering and Architecture;
- each information family receives a canonical professional owner;
- architecture only consumes gates and artifacts created/confirmed upstream;
- architect-created reconstructions remain candidate until owner confirmation.

The 31-item architect intake inventory will be mapped into this registry rather than discarded.

## 11. Current status and next build steps

Current branch establishes the first factory skeleton. It is **not yet a claim of exhaustive legal or standards coverage**.

Next iterations:

1. ingest full texts of core standards and regulator documents;
2. break each source into atomic normative requirements;
3. create exact `source → clause → requirement → artifact field → role → gate` links;
4. import the existing 31 architect intake inputs into canonical artifact mappings;
5. add federal-law and sector overlays;
6. define artifact schemas and validators;
7. define gate evaluators;
8. build project intake/conformance engine;
9. test first on WILD_IDEAS/Alina as a greenfield/brownfield hybrid case;
10. independently review before any factory rule is promoted to verified doctrine.
