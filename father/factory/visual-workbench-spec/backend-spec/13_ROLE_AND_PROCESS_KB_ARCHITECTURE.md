# FATHER Role & Process Knowledge Base Architecture

Status: `CANDIDATE_CANONICAL / ONE KB FOR ALL ROLES AND PROCESSES`

## 1. Decision

FATHER maintains a **single canonical knowledge system inside `osint_kb`** with two mandatory applicability dimensions:

```text
CANONICAL KNOWLEDGE OBJECT
        ↙            ↘
   ROLE SCOPE      PROCESS SCOPE
```

Every specialist and every material business/engineering process receives a logical knowledge section, but **not a private database/schema and not duplicated copies of knowledge**.

The canonical relationship is many-to-many:

```text
KnowledgeObject ↔ RoleKBProfile
KnowledgeObject ↔ ProcessKBProfile
RoleKBProfile   ↔ ProcessKBProfile
```

A method, definition, requirement, failure mode or case is stored once and can be applicable to many roles/processes.

---

## 2. Why this model

Bad model:

```text
security_engineer_kb.method_card_17
system_engineer_kb.method_card_17_copy
architect_kb.method_card_17_copy2
```

This creates semantic drift, duplicated truth and impossible updates.

Canonical model:

```text
knowledge.method METHOD-THREAT-MODELING-001
   ├─ applicable_to_role → security_engineer
   ├─ applicable_to_role → system_engineer
   ├─ applicable_to_role → skeptical_reviewer
   ├─ applicable_to_process → S21
   ├─ applicable_to_process → S22
   ├─ applicable_to_process → S23
   ├─ applicable_to_process → S24
   ├─ applicable_to_process → S47
   └─ applicable_to_process → S54
```

---

## 3. Role KB section contract

Every professional role has one `RoleKBProfile` with the following logical sections.

### RK-01 Role contract
- role ID/name;
- mission;
- scope of responsibility;
- authority boundaries;
- prohibited decisions/actions;
- required human authority boundaries;
- upstream/downstream collaborators.

### RK-02 Profession ontology
- domain terms;
- canonical concepts;
- synonyms/aliases;
- definitions;
- relationships;
- contested definitions.

### RK-03 Source map
- mandatory normative sources;
- standards/methodical sources;
- professional books;
- scientific sources;
- vendor/technology docs where applicable;
- source freshness/recheck policy.

### RK-04 Knowledge objects
- facts;
- requirements;
- principles;
- claims;
- constraints;
- definitions;
- decision criteria;
- trade-offs;
- anti-patterns;
- failure modes.

### RK-05 Methods & algorithms
- method cards;
- algorithms;
- formulas/calculators;
- deterministic checks;
- heuristics;
- escalation rules;
- applicability/preconditions;
- complexity/failure analysis.

### RK-06 Decision logic
- decision trees;
- policy tables;
- option-selection criteria;
- authority handoff points;
- stop/block/rework rules;
- uncertainty handling.

### RK-07 Artifact knowledge
For every artifact owned/reviewed by the role:
- purpose;
- required inputs;
- schema/fields;
- completion criteria;
- examples;
- failure examples;
- evidence expectations;
- downstream consumers.

### RK-08 Training pack
- representative cases;
- worked examples;
- solved exercises;
- historical cases;
- scenario variations.

### RK-09 Counterexample & failure pack
- common mistakes;
- plausible-but-wrong answers;
- conflicting-evidence cases;
- stale-source cases;
- missing-data cases;
- boundary cases.

### RK-10 Security/adversarial pack
Where applicable:
- malicious input;
- prompt/retrieval injection;
- forged evidence;
- authority escalation;
- poisoned source;
- sensitive-data handling;
- unsafe tool use;
- fail-closed scenarios.

### RK-11 Eval pack
- public evals;
- hidden evals;
- scoring rules;
- minimum thresholds;
- calibration cases;
- human-review criteria.

### RK-12 Maturity & telemetry
- current maturity per capability/domain;
- last certification;
- eval history;
- human acceptance/rejection rate;
- material error history;
- rework history;
- drift/security recertification state.

---

## 4. Process KB section contract

Every material business/engineering process has one `ProcessKBProfile`.

### PK-01 Process identity
- process ID;
- title;
- parent process/macro stage;
- version;
- status;
- owner.

### PK-02 Trigger & purpose
- trigger/event;
- business/engineering purpose;
- entry criteria;
- exit objective.

### PK-03 Inputs
For each input:
- canonical type;
- source/owner;
- minimum state;
- freshness rule;
- classification;
- mandatory/optional.

### PK-04 Preconditions & invariants
- upstream gates;
- required authority;
- required evidence;
- forbidden states;
- invariants that must hold.

### PK-05 Transformation steps
- ordered/parallel steps;
- deterministic operations;
- calculations;
- methods;
- algorithms;
- human tasks;
- candidate AI-assisted tasks.

### PK-06 Role/RACI/authority model
- accountable role;
- producer roles;
- reviewers;
- consulted roles;
- final authority;
- forbidden self-approval combinations.

### PK-07 Outputs
For each output:
- canonical object/artifact type;
- completion criteria;
- evidence links;
- version/baseline semantics;
- downstream consumers.

### PK-08 Local tests/oracles
- deterministic validations;
- completeness tests;
- consistency checks;
- security tests;
- quality criteria;
- acceptance oracle.

### PK-09 Exceptions/rework
- missing input;
- conflicting input;
- stale input;
- rejected output;
- test failure;
- authority missing;
- exact rework target.

### PK-10 Metrics
- throughput;
- cycle time;
- rework ratio;
- blocked time;
- quality/error rate;
- automation ratio where measured;
- human review outcomes.

### PK-11 Sources & justification
- normative basis;
- professional methods;
- scientific basis;
- internal policy basis;
- exact source locators when available.

### PK-12 Change/evolution
- process version history;
- reason for change;
- affected roles/artifacts/tests;
- migration/retraining needs.

---

## 5. Canonical role registry v1

Initial Role KB profiles are created logically for every role already defined by `FATHER_ROLE_MATRIX.yaml`:

1. `product_manager`
2. `business_owner`
3. `project_manager`
4. `knowledge_growth_analyst`
5. `business_analyst`
6. `requirements_engineer`
7. `security_engineer`
8. `system_engineer`
9. `data_owner`
10. `legal_compliance`
11. `integration_engineer`
12. `solution_architect`
13. `software_architect`
14. `api_designer`
15. `data_engineer`
16. `software_engineer`
17. `code_reviewer`
18. `devsecops_engineer`
19. `configuration_manager`
20. `qa_engineer`
21. `operations_engineer`
22. `service_owner`
23. `release_manager`
24. `change_manager`
25. `incident_manager`
26. `skeptical_reviewer`
27. `risk_owner`

Additional roles found during actual project/process inventory are added only after role-boundary review; likely candidates such as `finance_procurement`, `sre_engineer`, `ux_designer`, `data_architect`, `domain_specialist` remain separate candidate additions rather than being silently invented into the canonical matrix.

---

## 6. Canonical process registry v1

The process hierarchy starts with:

```text
Level 0: FATHER lifecycle
Level 1: A0–A16 macro stages
Level 2: S00–S59 engineering stations
Level 3: station-internal methods/algorithms/tasks
```

Every S00–S59 station receives a `ProcessKBProfile`.

Examples:
- `S01 SOURCE_ACQUISITION_REGISTRATION`
- `S04 ATOMIC_INFORMATION_EXTRACTION`
- `S11 USER_JOURNEY_BUSINESS_PROCESS`
- `S13 REGULATORY_APPLICABILITY`
- `S18 DATA_FLOW_MODEL`
- `S23 THREAT_SCENARIOS_SECURITY_RISKS`
- `S24 SECURITY_REQUIREMENTS_DRAFT`
- `S33 ARCHITECTURE_DRIVERS`
- `S38 ADR`
- `S48 TEST_SPECIFICATIONS`
- `S50 PRE_CODE_GATE`
- `S54 SYSTEM_SECURITY_PERFORMANCE_AI_TESTS`
- `S58 OPERATION_EVOLUTION`

Business processes discovered inside a project are **project/process instances or domain processes**, linked to the canonical process-method library rather than creating duplicated method knowledge.

---

## 7. Shared canonical knowledge object types

The `knowledge` domain should support at least these semantic object classes, reconciled with existing physical tables before DDL:

- `CONCEPT`
- `DEFINITION`
- `FACT`
- `CLAIM`
- `PRINCIPLE`
- `REQUIREMENT_PATTERN`
- `CONSTRAINT`
- `METHOD`
- `ALGORITHM`
- `FORMULA`
- `DECISION_CRITERION`
- `TRADEOFF`
- `PATTERN`
- `ANTI_PATTERN`
- `FAILURE_MODE`
- `CASE`
- `COUNTEREXAMPLE`
- `TEST_ORACLE`
- `EVAL_CASE`
- `SECURITY_CASE`
- `LESSON_LEARNED`

These are semantic classes, not a mandate to create one table per type.

---

## 8. Required mapping relations

Minimum canonical relations:

```text
ROLE_REQUIRES_KNOWLEDGE
ROLE_USES_METHOD
ROLE_OWNS_ARTIFACT
ROLE_REVIEWS_ARTIFACT
ROLE_PARTICIPATES_IN_PROCESS
ROLE_HAS_AUTHORITY_IN_PROCESS

PROCESS_REQUIRES_KNOWLEDGE
PROCESS_USES_METHOD
PROCESS_CONSUMES_ARTIFACT
PROCESS_PRODUCES_ARTIFACT
PROCESS_VERIFIED_BY_TEST
PROCESS_GOVERNED_BY_REQUIREMENT
PROCESS_REWORKS_TO_PROCESS

KNOWLEDGE_DERIVED_FROM_SOURCE
KNOWLEDGE_SUPERSEDES_KNOWLEDGE
KNOWLEDGE_CONFLICTS_WITH_KNOWLEDGE
KNOWLEDGE_VALIDATED_BY_CASE
```

The relation graph may be projected to `graph.*`, but canonical applicability/ownership relations remain owned by canonical domain records.

---

## 9. Database placement rule

Target semantics inside one database `osint_kb`:

```text
knowledge     canonical knowledge objects/methods/algorithms/cases
ontology      terms/definitions/entities
normative     normative requirements/applicability
review        validation/promotion/conflicts
agents        role-agent profile/runtime metadata
rag           retrieval configs/embeddings
source        provenance/source/version/span
```

Role/process KB sections are **logical profiles and mapping tables/views**, not new schemas such as:

```text
security_engineer_kb
architect_kb
qa_kb
business_analysis_kb
```

Those are prohibited because they duplicate canonical knowledge.

---

## 10. Retrieval contract

A specialist context is assembled dynamically:

```text
ROLE profile
+ current PROCESS profile
+ PROJECT scope
+ applicable NORMATIVE requirements
+ relevant canonical KNOWLEDGE
+ project EVIDENCE
+ authority/security policy
= bounded working context
```

This same retrieval contract is used by humans, UI views, reports, future RAG and future role-agents.

Example:

```text
security_engineer
+ S23 Threat Scenarios
+ healthcare project scope
+ applicable FSTEC/PDn/KII overlays
+ threat-model methods/cases
+ actual project DFD/assets/evidence
= S23 specialist workbench context
```

---

## 11. Promotion rule

Knowledge discovered during a project does not automatically enter universal Role/Process KB.

Flow:

```text
PROJECT OBSERVATION / LESSON
→ candidate knowledge
→ provenance
→ applicability scope
→ conflict check
→ domain review
→ eval/case update if needed
→ canonical promotion
→ role/process mappings
```

No LLM, parser, agent or project team may silently globalize local knowledge.

---

## 12. Versioning

RoleKBProfile and ProcessKBProfile are versioned independently from underlying knowledge objects.

A profile revision records:
- included/excluded knowledge refs;
- source baseline;
- method versions;
- decision logic versions;
- eval pack version;
- security pack version;
- change reason;
- reviewer;
- effective date.

Thus updating one method does not require copying the whole role KB.

---

## 13. Workbench representation

The visual Workbench exposes this as a living knowledge drawer.

When a user opens station `Sxx`, the right Inspector can show:

```text
PROCESS KNOWLEDGE
- purpose
- inputs/outputs
- methods/algorithms
- source basis
- tests
- failure/rework

ROLE KNOWLEDGE
- active role
- responsibilities
- allowed authority
- required competencies
- relevant methods/cases
- current maturity
```

Clicking a role switches the same station to that specialist's perspective without duplicating the underlying process or knowledge.

---

## 14. Maturity/coverage metrics

For every role and process FATHER should be able to calculate evidence-backed coverage metrics, for example:

- source coverage;
- normative coverage;
- method coverage;
- artifact-schema coverage;
- positive-case coverage;
- negative/failure-case coverage;
- security-case coverage;
- eval coverage;
- stale-source count;
- unresolved-conflict count;
- last independent review.

No invented percentage is shown when denominator/coverage model is not defined.

---

## 15. Reconciliation before DDL

Before implementing this model physically in `osint_kb`:

1. inventory existing `knowledge`, `ontology`, `normative`, `osint`, `security_*`, `public` structures;
2. identify existing role/profile/process/method/case tables;
3. map them to this logical contract;
4. classify each required structure as `KEEP / EXTEND / RENAME_VIEW / NEW`;
5. detect duplicated specialist/process knowledge;
6. define adapters/views;
7. define migration tests and rollback;
8. only then prepare DDL.

---

## 16. Acceptance gate

`ROLE_PROCESS_KB_ARCHITECTURE_V1_READY` requires:

- all canonical FATHER roles mapped to RoleKBProfile;
- all S00–S59 stations mapped to ProcessKBProfile;
- shared knowledge-object taxonomy reviewed;
- mapping relation types reviewed;
- source/provenance invariant preserved;
- no per-role/process duplicate DB introduced;
- retrieval contract accepted;
- project-to-global promotion workflow accepted;
- reconciliation against actual `osint_kb` completed before DDL.
