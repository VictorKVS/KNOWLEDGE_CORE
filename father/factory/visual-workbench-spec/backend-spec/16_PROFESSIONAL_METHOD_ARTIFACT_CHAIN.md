# FATHER Professional Method & Artifact Handoff Chain

Status: `CANDIDATE_CANONICAL / PAPER DESIGN AUTHORITY`

## 1. Purpose

This document defines how every FATHER professional role works as part of one engineering conveyor:

```text
ROLE
→ receives typed inputs
→ applies approved methods/algorithms
→ produces canonical artifacts
→ passes local tests/oracles
→ receives review/authority decision
→ hands versioned outputs to downstream roles/processes
→ writes trace/audit/state to osint_kb
```

The goal is to make the lifecycle visible, reproducible, reviewable and suitable for later automation without allowing automation to invent missing engineering decisions.

This document complements:

- `01_STATION_CATALOG_S00_S59.md`
- `13_ROLE_AND_PROCESS_KB_ARCHITECTURE.md`
- `14_ROLE_PROCESS_KB_REGISTRY.yaml`
- FATHER Paper Pipeline and Algorithm Design Standard.

## 2. Core invariant

A specialist does not start from a blank prompt and does not hand off free-form text.

Every material handoff uses:

```text
INPUT PACKAGE
  ├─ canonical IDs
  ├─ source/evidence refs
  ├─ baseline/version
  ├─ classification
  ├─ assumptions/UNKNOWNs
  └─ upstream gate state
       ↓
SPECIALIST METHOD
       ↓
ARTIFACT PACKAGE
  ├─ artifact ID/type
  ├─ structured content
  ├─ diagrams/models where applicable
  ├─ evidence and rationale
  ├─ open issues/conflicts
  ├─ test/oracle results
  ├─ owner/reviewer
  └─ version/baseline
       ↓
DOWNSTREAM HANDOFF
```

No downstream role should have to reconstruct why a field exists.

## 3. Source hierarchy for professional methods

ALINA builds each Role KB from a layered source model. All layers remain traceable.

### L1 — Mandatory authority
- laws and binding regulations;
- regulator acts/orders;
- contracts/internal mandatory policies;
- applicable GOST/ISO/IEC/IEEE standards where adopted or chosen as project baseline.

### L2 — Primary professional method sources
- standards bodies;
- official technology specifications;
- primary vendor documentation where technology-specific;
- recognized method owners.

### L3 — Scientific/professional evidence
- peer-reviewed research;
- systematic reviews;
- reproducible benchmarks;
- recognized professional bodies and consensus guidance.

### L4 — Books and educational practice
- professional architecture/security/data/software engineering books;
- OTUS lessons and exercises;
- worked examples.

### L5 — Internal production evidence
- project incidents;
- accepted/rejected decisions;
- test failures;
- rework history;
- measured telemetry;
- lessons learned.

A lower layer cannot silently override a higher-authority mandatory rule.

## 4. Artifact format contract

Every material engineering artifact is represented as a canonical information object even when exported as Markdown/PDF/DOCX/YAML/JSON/diagram.

Minimum metadata:

```text
artifact_id
artifact_type
project_id
station_id
owner_role
reviewer_roles
status
version
baseline_id
created_at
updated_at
source_refs[]
input_artifact_refs[]
requirement_refs[]
risk_refs[]
method_refs[]
algorithm_refs[]
assumptions[]
unknowns[]
conflicts[]
test_refs[]
decision_refs[]
downstream_refs[]
classification
```

Preferred representations:

- Markdown: narrative and rationale;
- YAML/JSON: machine-readable contracts/registries;
- Mermaid/C4/BPMN/DFD/ERD: diagrams from canonical model;
- OpenAPI/AsyncAPI/JSON Schema/SQL logical model: technical contracts;
- PDF/DOCX: reviewed/export/submission projection only;
- database records: operational canonical state.

## 5. Professional role chain

The canonical v1 role set contains 27 roles. Candidate additions are reviewed separately.

### R01 Product Manager

**Primary stations:** S08-S12, consulted S25-S29, S33-S38, S55, S58.

**Knowledge ALINA must build:** product discovery, value proposition, user outcomes, scope management, product metrics, product risk, experiment framing.

**Method families:** problem-vs-solution framing; JTBD/value proposition where useful; stakeholder interview synthesis; journey mapping; scope IN/OUT; KPI baseline/target; hypothesis/experiment framing.

**Consumes:** source register, business request, stakeholder evidence, market/domain evidence, existing product artifacts.

**Produces/owns:** BUSINESS_NEED, PRODUCT_VISION, VALUE_PROPOSITION, SCOPE_BASELINE, TARGET_USERS, USER_JOURNEYS, SUCCESS_METRICS, product assumptions.

**Formats:** structured artifact + narrative rationale + journey/process diagrams.

**Review/handoff:** Business Owner confirms value/scope; BA/System/Security/Requirements consume approved product baseline.

### R02 Business Owner

**Primary stations:** S08-S12, S30-S32, S36-S39, S55-S57.

**Knowledge:** business objectives, authority model, financial/risk ownership, acceptance and residual-risk authority boundaries.

**Methods:** business case; benefit/cost reasoning; decision criteria; risk acceptance; stage-gate approval.

**Produces/owns:** material business decisions, scope/value approval, business acceptance, funding/prioritization decisions.

**Formats:** Decision Record with evidence, alternatives, consequences, owner authority and revisit trigger.

**Handoff:** authorizes Product/Architecture/Acceptance decisions; cannot replace domain/security/legal authority where those are mandatory.

### R03 Project Manager

**Primary stations:** S00-S12, S29-S32, S49-S59.

**Knowledge:** lifecycle planning, WBS, dependencies, RAID, change control, milestone/gate tracking.

**Methods:** WBS; dependency network; PERT/range estimation where justified; RAID; critical path reasoning; change control.

**Produces:** PROJECT_SHELL, stakeholder/authority coordination, DELIVERY_WBS, plan/baseline, milestone/gate register, status/issue logs.

**Formats:** YAML/JSON plan + human-readable roadmap/status report.

**Handoff:** coordinates all roles; cannot self-approve domain artifacts.

### R04 Knowledge Growth Analyst

**Primary stations:** S01-S07, cross-cutting all Sxx, S58.

**Knowledge:** source acquisition, provenance, source authority, extraction, knowledge engineering, ontology, conflict/freshness detection, promotion workflow.

**Methods:** source registry; SHA/version identity; provenance chain; atomic extraction; source authority scoring policy; conflict/supersession analysis; ontology mapping; evidence sufficiency checks.

**Produces:** SOURCE_REGISTER, SOURCE_VERSION, SOURCE_SPAN, atomic knowledge candidates, GAP/CONFLICT/STALE registers, KB coverage reports.

**Formats:** canonical DB records + YAML/JSON registries + trace report.

**Handoff:** supplies bounded evidence packages to all specialist roles; no auto-promotion to canonical without review.

### R05 Business Analyst

**Primary stations:** S08-S12, S16-S20, S25-S29.

**Knowledge:** business process analysis, stakeholder needs, business rules, use/journey scenarios.

**Methods:** BPMN, SIPOC, IDEF0 as applicable; 5W/5Whys where appropriate; stakeholder mapping; business rule catalogue; process decomposition.

**Produces:** BUSINESS_PROCESS_MODEL, USER_JOURNEYS, BUSINESS_RULE_CATALOGUE, business requirements/candidate acceptance conditions.

**Formats:** BPMN/IDEF0 + structured rule catalogue + narrative.

**Handoff:** Requirements Engineer/System Engineer consume; Product/Business Owner review business meaning.

### R06 Requirements Engineer

**Primary stations:** S24-S29, supports S33-S38, S48-S55.

**Knowledge:** requirement quality, atomicity, verifiability, NFR/quality scenarios, traceability, baseline/change management.

**Methods:** requirement normalization; duplicate/conflict detection; shall-style normative wording where appropriate; quality attribute scenarios; traceability matrix; acceptance-oracle derivation.

**Produces:** BUSINESS/STakeholder/SYSTEM/SOFTWARE/SECURITY requirements baseline, NFR catalogue, acceptance criteria, RTM.

**Formats:** YAML/JSON requirement objects + Markdown export + trace graph.

**Handoff:** Architecture, QA, Security, Software Engineering; changes trigger impact analysis.

### R07 Security Engineer

**Primary stations:** S13-S15, S18, S21-S24, S28, S36, S39, S43, S47-S58.

**Knowledge:** secure-by-design, threat modeling, applicable FSTEC/FSB/industry requirements, abuse cases, control design, security verification.

**Methods:** asset/protected-interest analysis; trust-boundary analysis; threat source/scenario modeling; attack/abuse trees where useful; risk analysis; threat→requirement→control→test mapping; secure design review.

**Produces:** SECURITY_INTAKE, abuse cases, threat model, security requirements, security architecture review, residual security risk, security test requirements.

**Formats:** structured threat/risk registers + DFD/security overlays + trace graph.

**Handoff:** Requirements, Architecture, DevSecOps, QA, Risk Owner. Security cannot accept business risk on behalf of Risk Owner.

### R08 System Engineer

**Primary stations:** S16-S20, S25-S29, S33-S47, S55.

**Knowledge:** system boundary/context, functions, interfaces, modes/states, requirements allocation, system decomposition.

**Methods:** C4 Context where useful; functional decomposition; DFD; state/mode analysis; interface inventory; dependency mapping; system trade-off reasoning.

**Produces:** SYSTEM_CONTEXT, SYSTEM_BOUNDARY, FUNCTION_MODEL, DATA_FLOW_MODEL, INTERFACE_INVENTORY, OPERATIONAL_MODES, system requirements allocation.

**Formats:** canonical model + diagrams + structured contracts.

**Handoff:** Security/Architecture/Requirements/Integration/Data/QA.

### R09 Data Owner

**Primary stations:** S13-S14, S18, S25-S29, S39, S42, S55-S59.

**Knowledge:** data ownership, classification, permitted use, retention, quality/accountability, lifecycle.

**Methods:** data inventory; classification; ownership matrix; retention/usage rules; data quality acceptance.

**Produces:** DATA_INVENTORY, DATA_CLASSIFICATION, ownership/retention decisions, data acceptance decisions.

**Formats:** structured data catalogue + policy decisions.

**Handoff:** Data Engineer, Security, Legal, Architect, Operations.

### R10 Legal / Compliance

**Primary stations:** S13, S24-S29, S36-S39, S55-S59.

**Knowledge:** jurisdiction, applicability, mandatory obligations, contract constraints, regulator interpretations, version/effective-date logic.

**Methods:** applicability decision trees; legal source/version validation; clause→requirement mapping; exception/exemption analysis; obligation/prohibition/permission classification.

**Produces:** REGULATORY_APPLICABILITY, compliance constraints, clause-level requirements, compliance review findings.

**Formats:** normative register with exact source locator/version/effective date + rationale.

**Handoff:** Requirements/Security/Architecture/Data Owner/Business Owner.

### R11 Integration Engineer

**Primary stations:** S19, S40-S44, S53-S55.

**Knowledge:** integration patterns, protocol contracts, reliability, idempotency, error handling, external dependency behavior.

**Methods:** interface inventory; sync/async trade-off; contract-first design; sequence diagrams; retry/idempotency/backpressure/error taxonomy.

**Produces:** integration contracts, sequence/dynamic views, interface NFRs, integration test inputs.

**Formats:** OpenAPI/AsyncAPI/event schemas + sequence diagrams + dependency contract.

**Handoff:** API Designer, Software Architect, Data Engineer, DevSecOps, QA.

### R12 Solution Architect

**Primary stations:** S33-S39, S40-S47, supports S25-S32.

**Knowledge:** architecture drivers, quality attributes, patterns, trade-offs, cost/security/operability, architecture governance.

**Methods:** simplest-feasible baseline; architecture characteristics; C4; ADR; ATAM-like scenario review; weighted matrix only when weights justified; option/trade-off analysis.

**Produces:** ARCHITECTURE_DRIVER_SET, OPTION_SET, architecture views, trade-off records, target architecture, ADRs.

**Formats:** model + C4 views + ADR + decision packet.

**Handoff:** Software Architect, Security, Data, Integration, QA, Business/System decision authority. Cannot self-approve architecture.

### R13 Software Architect

**Primary stations:** S38-S48, S52-S55.

**Knowledge:** component boundaries, runtime decomposition, patterns, resilience, maintainability, technology constraints.

**Methods:** component decomposition; dependency rules; sequence/state design; pattern/anti-pattern analysis; architecture fitness checks.

**Produces:** COMPONENT_MODEL, software architecture rules, technical ADRs, implementation constraints.

**Formats:** component views + structured constraints + ADR.

**Handoff:** API/Data/Software Engineer/Code Reviewer/QA/DevSecOps.

### R14 API Designer

**Primary stations:** S19, S41, S48, S53-S55.

**Knowledge:** API semantics, versioning, errors, auth context, idempotency, compatibility.

**Methods:** contract-first; resource/event modeling; compatibility checks; error model; pagination/idempotency/security considerations.

**Produces:** API/EVENT contracts and API acceptance rules.

**Formats:** OpenAPI/AsyncAPI/JSON Schema + examples.

**Handoff:** Software Engineer, Integration Engineer, QA, Security.

### R15 Data Engineer

**Primary stations:** S18, S42, S44-S46, S53-S58.

**Knowledge:** logical/physical data models, pipelines, lineage, quality, storage, batch/stream trade-offs, retention.

**Methods:** ER/data modeling; lineage; pipeline design; partition/index strategy; quality rules; batch/stream choice based on requirements.

**Produces:** DATA_MODEL, PIPELINE_MODEL, LINEAGE, data quality tests, storage/sizing inputs.

**Formats:** ERD/schema contracts + pipeline diagrams + SQL/logical model.

**Handoff:** Software Architect, DevSecOps, QA, Operations, Data Owner.

### R16 Software Engineer

**Primary stations:** S49-S54.

**Knowledge:** implementation patterns, language/framework standards, secure coding, testability, observability requirements.

**Methods:** implementation plan decomposition; TDD where appropriate; code standards; deterministic tests; defensive programming.

**Consumes:** approved S50 package only for production path.

**Produces:** CODE, unit tests, implementation evidence, technical notes.

**Formats:** source code + tests + build metadata.

**Handoff:** Code Reviewer, DevSecOps, QA. Cannot reinterpret material requirements without change request.

### R17 Code Reviewer

**Primary stations:** S51-S54.

**Knowledge:** coding standards, architectural constraints, security rules, maintainability and test quality.

**Methods:** diff review; checklist; static evidence review; architecture constraint verification; test adequacy review.

**Produces:** REVIEW_RECORD, findings, approval/rework decision.

**Handoff:** Engineer/DevSecOps/QA; no self-review of material own code.

### R18 DevSecOps Engineer

**Primary stations:** S43-S57.

**Knowledge:** CI/CD, IaC, secrets, build provenance, SAST/SCA/DAST, containers, deployment safety, rollback.

**Methods:** pipeline-as-code; supply-chain checks; SBOM; secrets scanning; IaC validation; immutable build identity; staged rollout.

**Produces:** CI/CD design, build manifest, SBOM, security scan evidence, deployment/rollback automation, release evidence.

**Formats:** pipeline/IaC code + manifests + reports.

**Handoff:** Security, QA, Release, Operations.

### R19 Configuration Manager

**Primary stations:** S28, S38-S57.

**Knowledge:** baselines, versioning, change/configuration identification, environment/config drift.

**Methods:** baseline control; version manifest; configuration item register; change traceability.

**Produces:** BASELINE_MANIFEST, CONFIGURATION_REGISTER, version/release trace.

**Handoff:** all implementation/release roles.

### R20 QA Engineer

**Primary stations:** S27-S29, S48, S53-S55, S57.

**Knowledge:** test design, oracle design, coverage, negative/boundary testing, defect taxonomy, acceptance evidence.

**Methods:** requirements-based testing; equivalence/boundary; state/decision table; integration/system/performance/security/AI test planning; trace-based coverage.

**Produces:** TEST_STRATEGY, TEST_SPECIFICATIONS, test cases/oracles, defect records, verification reports.

**Formats:** structured test catalog + executable tests where applicable + evidence reports.

**Handoff:** Engineer, Security, Business/System Owner, Release.

### R21 Operations Engineer

**Primary stations:** S20, S44-S46, S56-S59.

**Knowledge:** runtime operation, observability, SLO, incident response, capacity, backup/recovery.

**Methods:** SLI/SLO; runbook design; capacity analysis; backup/restore drills; failure/recovery scenarios.

**Produces:** RUNBOOKS, monitoring model, operational acceptance evidence, capacity and recovery records.

**Handoff:** Service Owner, Incident/Change/Release, Architecture evolution.

### R22 Service Owner

**Primary stations:** S45-S59.

**Knowledge:** service accountability, SLO/SLA, operational risk, release readiness, lifecycle economics.

**Methods:** readiness gate; SLO governance; risk/cost/service-quality balancing.

**Produces:** operational acceptance, service decisions, production authority decisions.

**Handoff:** Operations, Release, Change, Business Owner.

### R23 Release Manager

**Primary stations:** S55-S57.

**Knowledge:** release packaging, dependency/readiness gates, deployment sequencing, rollback.

**Methods:** release checklist; deployment gate; rollback criteria; release evidence packaging.

**Produces:** RELEASE_MANIFEST, release decision record, deployment window/rollback plan.

**Handoff:** Operations/Service Owner/Change Manager.

### R24 Change Manager

**Primary stations:** S56-S58.

**Knowledge:** change risk, impact analysis, approvals, rollback and communication.

**Methods:** change classification; impact graph; authority routing; rollback readiness.

**Produces:** CHANGE_RECORD, approval/rejection, impact and rollback record.

**Handoff:** Release/Operations/Service Owner and affected design roles.

### R25 Incident Manager

**Primary stations:** S58 plus rework links to any affected station.

**Knowledge:** incident classification, containment, evidence preservation, RCA, corrective/preventive action.

**Methods:** incident command; timeline reconstruction; causal analysis; 5Whys/fault-tree where appropriate; lessons-learned promotion.

**Produces:** INCIDENT_RECORD, timeline, RCA, corrective actions, lessons candidate.

**Handoff:** Change/Operations/Security/Architecture/Knowledge Growth Analyst.

### R26 Skeptical Reviewer

**Primary stations:** cross-cutting material gates, especially S12, S24, S28, S32, S37-S39, S48-S50, S55-S57.

**Knowledge:** challenge methods, counterexamples, failure modes, evidence-quality assessment.

**Methods:** adversarial review; red-team reasoning; assumption challenge; counterexample search; ATAM-like scenarios; consistency checks.

**Produces:** INDEPENDENT_REVIEW_RECORD, unresolved objections, rework requests.

**Handoff:** relevant owner/final authority. Reviewer must be sufficiently independent from producer.

### R27 Risk Owner

**Primary stations:** S23-S24, S30-S32, S36-S39, S55-S58.

**Knowledge:** risk ownership, treatment/acceptance/transfer/avoidance, residual risk, authority.

**Methods:** risk decision framework; evidence review; treatment comparison; residual-risk acceptance.

**Produces:** RISK_DECISION, acceptance conditions, review date/triggers.

**Handoff:** Business/Service/Security/Architecture governance.

## 6. Candidate roles requiring explicit review

These are not silently promoted to canonical roles:

- Finance / Procurement;
- SRE Engineer;
- UX Designer / UX Researcher;
- Data Architect;
- Domain Specialist / Subject Matter Expert.

They become canonical only after boundary analysis shows responsibilities cannot be safely represented by existing roles.

## 7. Document production chain

The preferred lifecycle chain is:

```text
S00-S07  evidence foundation
  ↓
S08-S12  product/business baseline
  ↓
S13-S15  legal/data/security intake
  ↓
S16-S20  system model
  ↓
S21-S24  threat/security model v0
  ↓
S25-S29  requirements/NFR/acceptance/trace
  ↓
S30-S32  feasibility/risk/TCO/PoC
  ↓
S33-S39  architecture options/challenge/decision
  ↓
S40-S47  detailed design
  ↓
S48      complete test specifications/oracles
  ↓
S49      implementation plan
  ↓
S50      PRE-CODE EVIDENCE GATE
  ↓
S51-S52  implementation/build/supply-chain checks
  ↓
S53-S55  integration/system/security/performance/AI verification
  ↓
S56-S57  release/production readiness
  ↓
S58      operation/evolution
  ↓
S59      retirement
```

## 8. Handoff semantics

A handoff can have these states:

```text
DRAFT
READY_FOR_REVIEW
REWORK_REQUIRED
CONDITIONAL_PASS
APPROVED_BASELINE
STALE
SUPERSEDED
REJECTED
```

A downstream station may consume only states explicitly allowed by its Process KB profile.

Every handoff records:

```text
handoff_id
from_role
from_station
to_role
to_station
artifact_refs[]
source_snapshot_id
baseline_id
conditions[]
open_unknowns[]
conflicts[]
review_state
accepted_by
accepted_at
```

## 9. Fixation in osint_kb

The physical DB remains `osint_kb`. Logical placement is reconciled before DDL.

Target semantics:

```text
source       original/capture/span/provenance/version
normative    clauses/requirements/applicability
knowledge    concepts/methods/algorithms/cases/oracles
ontology     canonical terms/entities/definitions
review       review decisions/conflicts/promotions
agents       role profiles/prompt/model runtime metadata
rag          retrieval profiles/embeddings/index metadata
security     classification/access/security review
weights      versioned decision weights/calibrations
audit        append-only activity/snapshot manifests
graph        derived projections only
git_export   sanitized explicitly allowed projection
```

Artifact/project-state records must use canonical IDs and not create a second truth store.

## 10. Method maturity

ALINA must not mark a role method as production-ready merely because it exists in a book or prompt.

Method lifecycle:

```text
SOURCE_CANDIDATE
→ SOURCE_VERIFIED
→ METHOD_EXTRACTED
→ METHOD_REVIEWED
→ TRAINING_CASES_READY
→ EVAL_READY
→ SECURITY_EVAL_READY where applicable
→ ROLE_CAPABILITY_CANDIDATE
→ ROLE_CAPABILITY_VERIFIED
→ MONITORED
```

Each role capability has independent maturity by domain/process.

## 11. Acceptance

`PROFESSIONAL_CHAIN_V1_READY` requires:

- all 27 roles have Role KB profiles;
- every S00-S59 station has accountable/reviewer/authority mapping;
- every material artifact has owner, minimum schema, tests and downstream consumer;
- handoff states and acceptance semantics agreed;
- methods have source/evidence lineage;
- role/process duplication is prevented;
- project knowledge promotion remains review-gated;
- physical mapping against real `osint_kb` is completed before DDL;
- ALINA and FATHER UIs use the same canonical IDs.
