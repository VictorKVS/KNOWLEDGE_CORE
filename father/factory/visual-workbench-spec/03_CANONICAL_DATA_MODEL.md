# FATHER Visual Engineering Workbench — Canonical Data Model

Status: `DRAFT_V0.1`

## 1. Purpose

This document defines the canonical engineering object model used by the Workbench. The canvas, inspector, perspectives, exports and future AI workers are projections over this model.

Core principle:

```text
semantic engineering object ≠ visual node instance
```

A Requirement exists once. It may appear in multiple views. A visual node stores display/layout metadata that points to the canonical Requirement ID.

---

# 2. Entity families

## 2.1 Project / baseline

- PROJECT
- PROJECT_BASELINE
- PROJECT_STAGE_STATE
- STATION_STATE
- CHANGE_REQUEST

## 2.2 Source / evidence

- SOURCE
- SOURCE_VERSION
- SOURCE_LOCATOR
- EVIDENCE_ITEM
- EVIDENCE_LINK

## 2.3 Knowledge / analysis

- ATOMIC_ITEM
- TERM
- ENTITY
- ASSUMPTION
- UNKNOWN_ITEM
- CONFLICT

## 2.4 Product / business

- BUSINESS_NEED
- PRODUCT_VISION
- STAKEHOLDER
- SCOPE_ITEM
- USER_JOURNEY
- BUSINESS_PROCESS
- SUCCESS_METRIC

## 2.5 System engineering

- SYSTEM
- SYSTEM_BOUNDARY
- ACTOR
- FUNCTION
- DATA_FLOW
- INTERFACE
- DEPENDENCY
- OPERATIONAL_MODE

## 2.6 Security / risk

- PROTECTED_INTEREST
- ASSET
- NEGATIVE_CONSEQUENCE
- THREAT_SOURCE
- TRUST_BOUNDARY
- ENTRY_POINT
- THREAT_SCENARIO
- SECURITY_REQUIREMENT
- SECURITY_CONTROL
- RISK
- RISK_ACCEPTANCE

## 2.7 Requirements

- REQUIREMENT
- NFR_SCENARIO
- ACCEPTANCE_CRITERION
- REQUIREMENT_BASELINE

## 2.8 Architecture / design

- ARCHITECTURE_DRIVER
- ARCHITECTURE_OPTION
- ARCHITECTURE_VIEW
- TRADEOFF_RECORD
- ADR
- COMPONENT
- API_CONTRACT
- EVENT_CONTRACT
- DATA_MODEL_OBJECT
- DEPLOYMENT_NODE
- IAM_RULE
- SECRET_RULE
- OBSERVABILITY_SIGNAL
- SLO
- SIZING_ASSUMPTION

## 2.9 Verification

- TEST_ORACLE
- TEST_CASE
- TEST_SUITE
- TEST_RUN
- TEST_RESULT
- DEFECT
- VULNERABILITY
- VERIFICATION_REPORT
- VALIDATION_REPORT

## 2.10 Delivery / operation

- BUILD_ARTIFACT
- DEPENDENCY_RECORD
- SBOM_RECORD
- CONFIGURATION_BASELINE
- RELEASE
- DEPLOYMENT_RECORD
- RUNBOOK
- INCIDENT
- PROBLEM
- CAPACITY_RECORD
- COST_RECORD
- FEEDBACK_ITEM
- RETIREMENT_RECORD

## 2.11 Governance

- ROLE
- PERSON_OR_TEAM
- ASSIGNMENT
- REVIEW_TASK
- APPROVAL_DECISION
- GATE
- GATE_DECISION
- AUDIT_EVENT
- ALGORITHM_SPEC
- METHOD_REF
- SOURCE_REF

---

# 3. Common object envelope

Every material entity must support a common envelope:

```yaml
id: stable-id
object_type: REQUIREMENT
project_id: project-id
version_id: immutable-revision-id
schema_version: object-schema-version
status: DRAFT
name: human title
summary: optional concise description
owner_ref: assignment-or-role
reviewer_refs: []
created_at: timestamp
created_by: actor
updated_at: timestamp
updated_by: actor
source_refs: []
evidence_refs: []
assumptions: []
unknown_refs: []
conflict_refs: []
tags: []
classification: INTERNAL
baseline_refs: []
custom_fields: {}
```

## DM-001 Stable ID

`id` identifies logical object across revisions.

## DM-002 Immutable revision

`version_id` identifies exact revision and never changes.

## DM-003 Schema version

Object schema migrations must be explicit.

## DM-004 Soft lifecycle, not silent delete

Material objects are retired/rejected/superseded rather than hard-deleted from engineering history.

---

# 4. Relationship model

Relationship is first-class:

```yaml
id: edge-id
project_id: p1
version_id: edge-revision
source_ref: REQ-014
target_ref: ADR-003
relation_type: DRIVES
status: VERIFIED
source_port_type: REQUIREMENT
target_port_type: ARCHITECTURE_DRIVER
evidence_refs: []
rationale: ...
created_by: ...
```

## DM-REL-001 Typed relation

Relation type must have schema defining valid source/target classes.

## DM-REL-002 Relation evidence

Material semantic relation may require evidence/rationale.

## DM-REL-003 Versioned relation

Edge changes are versioned separately where necessary.

---

# 5. Visual projection model

Visual representation must not pollute semantic object.

```yaml
view_id: view-security-01
object_ref: REQ-014
layout:
  x: 1220
  y: 480
  width: 240
  height: 110
collapsed: false
visual_overrides:
  pin: false
```

View data can be deleted/rebuilt without deleting engineering object.

---

# 6. View definition

```yaml
id: view-architecture-main
project_id: p1
name: Architecture
perspective: ARCHITECTURE
root_ref: SYSTEM-001
filters: {}
layout_strategy: manual-with-autolayout
saved_selection: []
```

Views may include query/filter definition rather than explicit duplicated object sets.

---

# 7. Source model

## SOURCE

Represents logical source.

Fields:

- id;
- source_type;
- authority_class;
- owner;
- title;
- origin;
- canonical_locator;
- effective_status;
- classification;
- freshness_policy.

## SOURCE_VERSION

- source_id;
- version_id;
- external_version/date;
- acquired_at;
- content_hash;
- media_type;
- storage_ref;
- effective_from/to;
- supersedes/superseded_by.

## SOURCE_LOCATOR

Supports:

- line range;
- page;
- paragraph;
- section/clause;
- JSON pointer;
- code file+line;
- URL fragment;
- commit/path;
- external stable identifier.

---

# 8. Evidence model

Evidence is not just attachment.

```yaml
id: EVID-123
source_version_ref: SRCV-9
locator_ref: LOC-88
claim_scope: field:REQ-014.statement
support_type: SUPPORTS
strength: DIRECT
review_status: VERIFIED
```

Support types:

- SUPPORTS;
- CONTRADICTS;
- QUALIFIES;
- SUPERSEDES;
- CONTEXT_ONLY.

Strength labels are descriptive and policy-bound, not mathematical truth unless a metric is defined.

---

# 9. Atomic information model

ATOMIC_ITEM types:

- FACT;
- CLAIM;
- REQUIREMENT_CANDIDATE;
- CONSTRAINT;
- ASSUMPTION;
- DECISION;
- RISK;
- UNKNOWN.

Fields include exact source span and modality/qualifiers.

Atomic items may map to one or more artifact fields.

---

# 10. Requirement model

```yaml
id: REQ-014
requirement_type: SYSTEM
statement: ...
rationale: ...
priority: MUST
owner_ref: ...
source_refs: [...]
acceptance_refs: [AC-014]
verification_method: TEST
risk_refs: [...]
architecture_refs: [...]
status: VERIFIED
```

NFR uses structured scenario extension:

```yaml
stimulus:
environment:
artifact:
response:
measure:
```

---

# 11. Threat / risk model

THREAT_SCENARIO:

```yaml
id: THR-021
protected_interest_refs: []
negative_consequence_refs: []
threat_source_refs: []
entry_point_refs: []
trust_boundary_refs: []
preconditions: []
scenario_steps: []
resulting_impact: []
evidence_refs: []
security_requirement_refs: []
control_refs: []
test_refs: []
```

RISK is separate from THREAT.

RISK_ACCEPTANCE requires explicit authority assignment and expiry/review trigger.

---

# 12. Architecture decision model

ADR:

- status;
- context;
- decision;
- drivers;
- considered options;
- rejected alternatives;
- consequences;
- risks;
- evidence;
- rollback/replacement path;
- revisit triggers;
- reviewer;
- final authority decision.

ADR revision history preserved; supersession creates relation rather than overwriting history.

---

# 13. Test model

## TEST_ORACLE

Defines expected observable condition independent of implementation.

## TEST_CASE

Links:

- requirement/risk/control;
- oracle;
- preconditions;
- steps/input;
- expected result;
- evidence required;
- test class.

## TEST_RUN

Captures exact implementation baseline/environment/config.

## TEST_RESULT

- PASS/FAIL/ERROR/SKIPPED;
- measured values;
- evidence refs;
- defects created;
- timestamp/tool/operator.

---

# 14. Gate model

```yaml
id: GATE-ARCH-READY
required_conditions:
  - rule: all_material_drivers_traced
  - rule: independent_review_present
  - rule: residual_risk_has_owner
authorized_role: SYSTEM_DECISION_OWNER
reviewer_roles: [SECURITY_ENGINEER, SKEPTICAL_REVIEWER]
```

GATE_DECISION:

- gate version;
- decision;
- actor/authority assignment;
- rationale;
- conditions;
- evidence snapshot refs;
- timestamp.

Gate decision is immutable record; reopening creates new cycle/version.

---

# 15. Assignment / authority model

ROLE defines capability/organizational role.

PERSON_OR_TEAM identifies human/team.

ASSIGNMENT binds:

```text
person/team + role + project/scope + effective period + authority flags
```

This prevents assumption that anyone with generic role globally can approve every object.

---

# 16. Review model

REVIEW_TASK fields:

- target object/version;
- review type;
- assignee;
- due/status;
- checklist;
- findings;
- outcome;
- linked comments;
- independence constraint.

Review outcome does not mutate target to VERIFIED unless gate/policy says so.

---

# 17. Conflict model

CONFLICT:

- conflicting refs;
- conflict type;
- severity/materiality;
- detected by;
- evidence;
- responsible owner;
- resolution status;
- resolution rationale.

Types:

- source contradiction;
- requirement conflict;
- definition conflict;
- version conflict;
- scope conflict;
- authority conflict;
- implementation mismatch;
- test/evidence conflict.

---

# 18. Unknown model

UNKNOWN_ITEM fields:

- question;
- why material;
- owner;
- affected objects;
- due trigger;
- blocking/nonblocking;
- resolution evidence.

Unknown can be bounded and nonblocking by explicit policy/authority.

---

# 19. Change request model

CHANGE_REQUEST captures proposed material mutation before commit to baseline.

Fields:

- trigger;
- proposed changes;
- affected objects;
- impact preview;
- required rework stations;
- risk/cost/time;
- reviewers;
- decision;
- execution refs.

---

# 20. Baseline model

PROJECT_BASELINE is named immutable set of exact object/relation revisions.

Types:

- PRODUCT_BASELINE;
- REQUIREMENTS_BASELINE;
- ARCHITECTURE_BASELINE;
- IMPLEMENTATION_BASELINE;
- RELEASE_BASELINE;
- PRODUCTION_BASELINE.

Baseline must be reconstructable.

---

# 21. Station state model

STATION_STATE references S00–S59 and project.

Fields:

- availability;
- state;
- unmet inputs;
- current outputs;
- blocker refs;
- owner assignment;
- local readiness result;
- review refs;
- gate refs;
- last evaluated at.

Station status derives from data/rules; not manually colored.

---

# 22. Algorithm specification object

ALGORITHM_SPEC aligns with `ALGORITHM_DESIGN_STANDARD.md`.

Fields:

- problem;
- input contract;
- output contract;
- assumptions;
- invariants;
- simplest baseline;
- alternatives;
- selection criteria;
- correctness/adequacy argument;
- complexity;
- failure modes;
- falsification tests;
- security implications;
- references;
- review status.

---

# 23. AI run record — future

AI_RUN_RECORD:

- station/object scope;
- role capability;
- model/provider/version;
- prompt/system contract version;
- frozen input refs;
- tool permissions;
- data classification;
- output refs;
- evidence refs claimed;
- deterministic validation results;
- human review result;
- duration/cost;
- security flags.

Model output itself is never source evidence.

---

# 24. Audit event model

Audit event is immutable application event for material actions.

Minimum fields defined in Master TZ.

Audit and engineering event streams may be stored separately but linked.

---

# 25. Query patterns the model must support

The data model is acceptable only if it efficiently supports queries such as:

1. show all requirements without test;
2. show all security controls without evidence;
3. trace this release defect to source requirement;
4. show everything stale because source X superseded;
5. show decisions relying on UNKNOWN Y;
6. show all objects approved by person/role during period;
7. show all external dependencies handling confidential data;
8. show test failures affecting Production Ready gate;
9. show architecture elements implementing NFR latency;
10. show clause→requirement→control→test→evidence chain;
11. show all accepted residual risks expiring this quarter;
12. show all AI runs touching restricted data;
13. reconstruct architecture baseline vN;
14. compute impact of changing API contract version;
15. render Security perspective neighborhood.

---

# 26. Persistence guidance

Initial relational implementation should prefer normalized core tables for IDs/statuses/relations and use JSONB for extensible payload only where schema evolution benefits outweigh strict columns.

Do not store the entire model as one opaque JSON document.

Do not require graph DB in MVP. Edge table + indexed traversal/cache is baseline; graph DB requires benchmark justification.

---

# 27. Deletion policy

Hard delete allowed only for:

- uncommitted local drafts;
- obvious duplicate imports before baseline/review under policy;
- non-material layout/view objects.

Material confirmed/verified/approved engineering data uses reject/retire/supersede.

---

# 28. Data classification propagation

Objects derived from sensitive sources inherit classification unless an explicit declassification/transformation policy exists.

AI/provider eligibility uses the effective classification of frozen input snapshot.

---

# 29. Integrity invariants

1. every revision belongs to logical object;
2. every material field with evidence-required policy has evidence or explicit UNKNOWN;
3. final authority decision resolves to valid assignment;
4. VERIFIED state cannot exist if mandatory gate evidence absent;
5. relation endpoints exist in same project or explicit external namespace;
6. baseline references immutable revisions;
7. source locator references exact source version;
8. test result references exact test + implementation/environment baseline;
9. risk acceptance references exact risk revision and authority;
10. UI projection cannot create semantic orphan object silently.

These invariants become automated validators before write/promotion.