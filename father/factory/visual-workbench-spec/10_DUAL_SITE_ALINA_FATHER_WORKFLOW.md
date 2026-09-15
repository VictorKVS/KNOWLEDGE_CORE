# ALINA + FATHER — Dual-Site Engineering Workflow

Status: `CANDIDATE_CANONICAL / UX + INFORMATION ARCHITECTURE`

## 1. Decision

FATHER uses two different user-facing workspaces over one canonical operational state in PostgreSQL `osint_kb`.

```text
                     osint_kb
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
   ALINA Knowledge Site          FATHER Design Site
   knowledge factory             engineering workbench
   role/process KB               project lifecycle S00-S59
   sources/methods/evals         artifacts/decisions/tests
```

They are not two products with duplicated knowledge. They are two projections over the same canonical IDs, source/evidence records, role/process profiles, reviews and audit history.

## 2. Responsibility split

### ALINA site answers

- What must this specialist know?
- Which sources justify the knowledge?
- Which methods/algorithms are approved or candidate?
- What training and counterexamples exist?
- What does this role usually produce?
- Which Sxx processes use this knowledge?
- What is missing/stale/conflicted?
- What is the current capability maturity?
- Which tests/evals/security tests certify the capability?

### FATHER site answers

- What project are we designing?
- Which Sxx station are we in?
- What entered this station?
- Which role owns the work?
- Which knowledge/method package is needed now?
- Which artifacts must be produced?
- Which sources/evidence support them?
- Who reviews/approves them?
- What passes to the next station?
- What is blocked/stale/conflicted/rework-required?

ALINA grows specialists and process knowledge. FATHER applies that knowledge to a concrete project.

## 3. Common canonical IDs

Both sites must use the same IDs for:

```text
ROLE_ID
PROCESS_ID / Sxx
KNOWLEDGE_OBJECT_ID
METHOD_ID
ALGORITHM_ID
SOURCE_ID
CAPTURE_ID
SOURCE_SPAN_ID
REQUIREMENT_ID
RISK_ID
ARTIFACT_ID
TEST_ID
GATE_ID
DECISION_ID
BASELINE_ID
PROJECT_ID
```

The UI may render friendly titles, but navigation and trace use canonical IDs.

## 4. ALINA information architecture

Top-level navigation:

```text
ALINA
├── Knowledge Factory
├── Roles
├── Processes
├── Methods & Algorithms
├── Sources
├── Cases / Counterexamples
├── Evals & Certification
├── Security Training
├── Gaps / Conflicts / Stale
├── Promotion Review
└── Factory Telemetry
```

### 4.1 Role page

Opening `security_engineer`, for example, shows:

```text
HEADER
role name / maturity / last certification / coverage warnings

TABS
Overview
Mission & Authority
Knowledge Map
Methods & Algorithms
Artifacts
Processes Sxx
Sources
Training Cases
Counterexamples
Security Cases
Eval / Hidden Eval
Errors & Rework
Versions
```

Each Method Card can be opened to:

```text
purpose
preconditions
inputs
steps
invariants
outputs
complexity/cost
failure modes
alternatives
source evidence
roles using it
processes using it
artifacts produced
public evals
hidden eval status
security eval status
version history
```

### 4.2 Process page

Opening `S23 Threat Scenarios & Security Risks` shows:

```text
purpose
trigger
inputs
preconditions
responsible roles
review/authority
required knowledge
methods/algorithms
output artifacts
test oracles
failure/rework paths
source basis
training examples
production lessons
version history
```

### 4.3 Source page

Source Inspector shows:

```text
source identity
version/effective status
origin/authority class
hash/capture history
license/use restrictions
parsed structure
atomic knowledge derived
methods/requirements derived
roles/processes using it
conflicts/supersession
reviews
```

### 4.4 Factory queue

ALINA work queue shows candidate knowledge flowing through:

```text
RECEIVED
→ REGISTERED
→ EXTRACTED
→ STRUCTURED
→ KNOWLEDGE_CANDIDATE
→ CONFLICT_CHECK
→ DOMAIN_REVIEW
→ EVAL_UPDATE
→ PROMOTION_REVIEW
→ CANONICAL
```

No direct LLM-to-canonical button exists.

## 5. FATHER information architecture

Top-level navigation:

```text
FATHER DESIGN
├── Projects
├── Lifecycle Canvas
├── Artifacts
├── Requirements
├── Security
├── Architecture
├── Data
├── Tests
├── Decisions / Gates
├── Trace / Impact
├── Reviews
└── History / Baselines
```

Main canvas is the S00-S59 engineering conveyor.

### 5.1 Station node

Each visible node displays compactly:

```text
Sxx + title
owner role
state
input readiness
artifact completion
review/gate state
blocker count
```

Color/state conveys readiness, not subjective quality score.

### 5.2 Single click

Single click opens right Inspector while keeping canvas visible.

Tabs:

```text
Overview
Inputs
Outputs
Evidence
Methods
Role Knowledge
Requirements/Risks
Tests
Review/Gate
History
Impact
```

`Methods` and `Role Knowledge` are live projections from ALINA canonical knowledge, not copied project text.

### 5.3 Double click

Double click drills into station internals:

```text
inputs
  ↓
normalization / checks
  ↓
method steps
  ↓
calculations / bounded AI assistance
  ↓
artifact construction
  ↓
local tests
  ↓
review
  ↓
outputs
```

Breadcrumb preserves canvas position and context.

### 5.4 Artifact page

Opening an artifact shows:

```text
canonical structured content
rendered document/diagram
source/evidence lineage
method/algorithm lineage
requirements/risks covered
owner/reviewer
open UNKNOWN/CONFLICT
version/baseline
upstream/downstream
verification/test evidence
history
```

## 6. Cross-site navigation

Cross-links are mandatory.

From FATHER station:

```text
Open role in ALINA
Open process KB in ALINA
Open method card in ALINA
Open source in ALINA
```

From ALINA role/method/process:

```text
Show active FATHER projects using this
Show project artifacts created with this
Show production errors/rework linked to this method
Show incidents/lessons candidates
```

A new browser view may be used, but IDs and exact version/context must be preserved in the link.

## 7. Specialist working context

When a specialist opens a FATHER station, runtime context is assembled as:

```text
ROLE KB PROFILE
+ PROCESS KB PROFILE
+ PROJECT BASELINE
+ current INPUT ARTIFACTS
+ applicable NORMATIVE requirements
+ PROJECT EVIDENCE
+ active METHOD versions
+ AUTHORITY/SECURITY policy
+ OPEN UNKNOWN/CONFLICT
= WORK PACKAGE
```

The UI must show what was included and why. Hidden context assembly is forbidden for material decisions.

## 8. Document creation interaction

The project designer should not face an empty document editor by default.

For each required artifact FATHER shows:

```text
Required by station: Sxx
Owner: role
Reviewers: roles
Required inputs: refs
Required sections/fields
Applicable methods
Applicable normative basis
Examples/counterexamples from ALINA
Local tests/oracles
Downstream consumers
```

The specialist fills or generates a draft only inside this contract.

Material fields have inline provenance indicators.

Example field state:

```text
System boundary: APPROVED
source refs: SRC-14, SRC-19
method: METHOD-SYSTEM-CONTEXT-001 v3
owner: system_engineer
review: solution_architect PASS
last changed: baseline B-07
```

## 9. Handoff interaction

When an artifact is sent downstream, FATHER opens a Handoff Sheet rather than silently changing state.

It shows:

```text
FROM role/station
TO role/station
artifacts included
baseline/source snapshot
open conditions
UNKNOWNs
conflicts
required downstream acceptance
impact if rejected
```

Receiver chooses only authorized actions:

```text
ACCEPT
ACCEPT_WITH_CONDITIONS
REQUEST_REWORK
REQUEST_MORE_EVIDENCE
REJECT
```

The decision becomes a review/audit event.

## 10. Learning loop back to ALINA

Production/project evidence flows back as candidate learning, never direct canonical knowledge.

```text
project artifact/test/rework/incident
        ↓
LESSON CANDIDATE
        ↓
ALINA Factory
        ↓
source/provenance + applicability
        ↓
method/case/counterexample candidate
        ↓
domain review + eval update
        ↓
canonical promotion
        ↓
role/process KB new version
```

Thus FATHER improves ALINA and ALINA improves future FATHER projects.

## 11. Permissions

ALINA permissions and FATHER permissions are separate views over shared authority policy.

Examples:

- Knowledge Growth Analyst may propose a Method Card but not approve a legal interpretation.
- Security Engineer may review security method applicability but not accept business residual risk.
- Solution Architect may draft ADR but cannot self-close architecture authority gate.
- Software Engineer may read approved design package but cannot silently change requirements baseline.

Cross-site links never escalate permissions.

## 12. Search

Global search should understand typed objects.

Examples:

```text
role:security_engineer method:threat-modeling
process:S23 status:stale
source:187-FZ used_by:S13
artifact:ADR project:OSINT status:approved
requirement:SEC-* unverified
```

Search results show source/type/status/version, not just text snippets.

## 13. Visual trace modes in FATHER

The same project can be viewed through perspectives:

```text
Lifecycle
Role handoff
Evidence
Requirements
Security
Architecture
Data
Verification
Compliance
Cost
Operations
```

Example Role Handoff view:

```text
Business Owner
   ↓ BUSINESS_NEED
Business Analyst
   ↓ BUSINESS_PROCESS_MODEL
System Engineer
   ↓ SYSTEM_CONTEXT / DFD
Security Engineer
   ↓ THREAT_MODEL / SEC REQ
Requirements Engineer
   ↓ REQUIREMENTS BASELINE
Solution Architect
   ↓ ADR / TARGET ARCHITECTURE
QA Engineer
   ↓ TEST ORACLES
Software Engineer
```

Example Evidence view:

```text
SOURCE SPAN
→ REQUIREMENT
→ THREAT/RISK
→ ADR
→ CONTROL
→ TEST
→ RELEASE EVIDENCE
```

## 14. Dashboards

### ALINA dashboard
Only evidence-backed metrics:

- role KB coverage by defined denominator;
- process KB coverage;
- stale source count;
- unresolved conflicts;
- methods awaiting review;
- eval/security-eval state;
- role maturity by capability;
- recent production lessons awaiting promotion.

### FATHER dashboard

- project stage/station state;
- blocked/rework stations;
- artifact readiness;
- unclosed UNKNOWN/CONFLICT;
- review/gate queue;
- requirement-to-test coverage;
- stale impact after source/baseline change;
- release readiness.

No invented percentages without defined denominator.

## 15. Codex implementation boundary

Codex must not implement ALINA and FATHER as separate truth stores.

Before UI implementation it must provide:

1. shared canonical ID contract;
2. ALINA read/write use-case list;
3. FATHER read/write use-case list;
4. cross-site navigation contract;
5. permission/authority matrix;
6. artifact/handoff state machine;
7. API boundary and audit events;
8. reconciliation to existing `osint_kb`;
9. design gaps where current paper contracts are insufficient.

Only after paper/design acceptance may implementation proceed for material behavior.

## 16. Acceptance

`DUAL_SITE_ALINA_FATHER_V1_READY` requires:

- both sites use the same canonical IDs;
- no duplicate knowledge or project truth store;
- every FATHER station can resolve Role KB + Process KB context;
- every ALINA method can show projects/processes/roles using it;
- every artifact has traceable method/source/owner/test lineage;
- handoffs are explicit and audited;
- project lessons enter ALINA only as candidates;
- cross-site permissions do not escalate authority;
- design-gap behavior exists before Codex fills undefined material decisions.
