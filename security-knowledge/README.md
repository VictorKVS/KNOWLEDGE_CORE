# SECURITY KNOWLEDGE BASE

## Evidence-driven regulatory, audit and security architecture knowledge graph

Security Knowledge Base is the regulatory and assurance layer of `KNOWLEDGE_CORE`.

Its first objective is deliberately narrow: **build a trustworthy document corpus first**. Laws, decrees, government resolutions, regulator orders, standards and official methodologies are ingested with version history and provenance before the project attempts to automate audit or architecture decisions.

The long-term objective is broader: given an organization and its systems, produce a complete, explainable and evidence-linked view of applicable security obligations, controls, verification steps, gaps, risks, alternatives, implementation cost, target architecture and development roadmap.

> The system must not merely answer *what should be done*. It must be able to show **why**, **under which source and version**, **for whom it applies**, **what alternatives exist**, **how the result can be verified**, and **what changes when the source changes**.

---

## 1. Development order

The project develops in layers. Later layers must not weaken the provenance of earlier ones.

### Phase 1 — Document Knowledge Base — CURRENT PRIORITY

Collect and normalize primary sources:

- federal laws;
- presidential decrees and strategic documents;
- Government of the Russian Federation resolutions;
- FSTEC orders, requirements, methodologies and official materials;
- FSB orders and requirements;
- Roskomnadzor acts, requirements and official explanations;
- other regulators when applicability requires them;
- GOST and GOST R standards;
- ISO/IEC and other international standards;
- international treaties and conventions;
- sector regulation;
- official technical security catalogues and registries.

Every document is stored with its history. A new edition **does not overwrite** the old edition.

### Phase 2 — Requirement and relationship graph

Extract atomic requirements, definitions, exceptions, roles, deadlines, algorithms and evidence expectations. Build intra-document and inter-document relationships.

### Phase 3 — Applicability

Determine which sources and atomic requirements apply to a particular organization, information system, data set, jurisdiction, sector and security status.

### Phase 4 — Assurance and audit

Map requirements to controls, checks and evidence. Produce organizational and specialist checklists, identify gaps and calculate bounded risks.

### Phase 5 — Approved solutions and registries

Link requirements and controls to verified security products, software, hardware, certificates, licences and approved configurations from authoritative FSTEC/FSB and other applicable registries.

### Phase 6 — Security architecture

Generate evidence-backed implementation alternatives and compare compatibility, assurance, residual risk, implementation effort and total cost of ownership.

### Phase 7 — Security development programme

Convert gaps and architecture decisions into priorities, remediation work, owners, dependencies, budget, milestones, retest and measurable actual effect.

### Phase 8 — Continuous update engine

Watch authoritative sources, detect new documents and revisions, build diffs, determine impact radius and propose graph/weight updates for review.

---

## 2. What is stored for every document

A document is not merely a PDF and not merely a RAG chunk collection. It is a versioned knowledge object.

### 2.1 Immutable source

For every source/version store:

- stable `SEC-SRC-*` ID;
- exact title;
- document type;
- issuer/regulator;
- jurisdiction;
- number and date;
- publication date;
- effective-from/effective-to dates;
- revision/version;
- legal/current status;
- official source URL/reference;
- acquisition timestamp;
- immutable raw capture when legally and technically possible;
- SHA-256/fingerprint;
- provenance and verification state;
- predecessor/successor versions.

### 2.2 Normalized representation

Keep a normalized machine-readable copy separately from the immutable original. Normalization must never silently change normative meaning.

### 2.3 Structural tree

Preserve the legal/document address:

`document → section → chapter → article → part → clause → subclause → paragraph → appendix/table/note`

A requirement must always be traceable back to its exact source location.

### 2.4 Chunks

Maintain separate chunk purposes where useful:

- structural chunks;
- semantic chunks;
- retrieval/RAG chunks;
- atomic requirement chunks;
- definition chunks;
- table/appendix/note chunks.

Chunking must preserve source offsets/anchors and cross-references.

### 2.5 Definitions and terminology

Extract:

- terms;
- definitions;
- abbreviations;
- roles;
- regulated entities;
- protected objects;
- references to definitions in other documents.

The graph must distinguish `defined_in`, `used_in`, `redefined_by`, `narrowed_by` and `extended_by`.

### 2.6 Footnotes, appendices, tables and diagrams

They are first-class evidence objects. They must remain linked to the provisions they qualify.

---

## 3. Atomic knowledge extracted from a document

Each independently satisfiable or violable normative statement becomes an atomic `SEC-REQ-*` candidate.

For each requirement record at least:

- normative text anchor;
- normalized meaning;
- type: obligation / prohibition / permission / condition / exception / recommendation / responsibility / reporting / deadline / procedure;
- subject: who must act;
- object: what is regulated/protected;
- action;
- conditions;
- exceptions;
- trigger;
- deadline/periodicity;
- expected result;
- required evidence;
- interpretation and interpretation confidence;
- applicability rule references;
- provenance.

Source text, extracted requirement, interpretation and implementation control are separate layers. An implementation choice must never be presented as if it were literal statutory text.

---

## 4. Logic inside a document

The database stores the operational logic hidden in prose.

### Organization algorithm

`Determine applicability → appoint responsibility → classify/categorize → create required documentation → implement measures → verify → preserve evidence → monitor → reassess`

### Security specialist algorithm

For every applicable requirement answer:

1. What must I request?
2. What must I inspect?
3. What decision must I make?
4. What evidence is sufficient?
5. What artifact/document must be created or updated?
6. Who approves it?
7. What technical control implements it?
8. How is that control tested?
9. What happens if it fails?
10. When must it be reviewed again?

### Role-specific flows

Where applicable derive workflows for:

- executive management;
- security function;
- system owner;
- IT/operations;
- developer/DevSecOps;
- SOC/incident response;
- HR;
- legal/privacy;
- administrator;
- contractor/vendor.

### Checklists

Maintain separate checklists for:

- the organization;
- security specialist;
- auditor;
- system owner;
- technical verification/pentest where authorized and applicable.

Checklist states should distinguish `PASS`, `PARTIAL`, `FAIL`, `NOT_APPLICABLE`, `UNKNOWN` and `NOT_VERIFIED`.

---

## 5. Graph relationships

Relationships are typed. A generic hyperlink is insufficient.

Important edge types include:

- `defines`;
- `refers_to`;
- `implements`;
- `details`;
- `extends`;
- `restricts`;
- `exception_to`;
- `depends_on`;
- `amends`;
- `supersedes`;
- `conflicts_with`;
- `evidence_for`;
- `satisfied_by`;
- `verified_by`;
- `mitigates`;
- `affects`;
- `applicable_if`;
- `derived_from`.

Both intra-document and inter-document edges are required.

Example:

`152-FZ → Government resolution → FSTEC requirement → SEC-REQ → SEC-CTRL → SEC-CHECK → EVIDENCE`

---

## 6. Weights are properties, not truth

The graph must not collapse legal and technical reasoning into one opaque score.

Maintain independent dimensions such as:

- legal authority;
- mandatoryness;
- applicability;
- asset criticality;
- business impact;
- technical impact;
- threat relevance;
- exposure;
- control effectiveness;
- evidence quality;
- source confidence;
- interpretation confidence;
- freshness;
- implementation complexity;
- cost confidence.

Every calculated score must retain its input dimensions and provenance. `UNKNOWN` must never silently become zero.

Weights and ranking algorithms may evolve without rewriting the underlying source facts.

---

## 7. Applicability engine

The future organization profile must describe facts, not guesses:

- jurisdiction;
- sector;
- ownership/governance type;
- operator/controller/processor roles;
- personal data and special categories;
- ISPDn status;
- GIS status;
- KII subject/object/significance status;
- cryptographic protection use;
- cloud/external processing;
- remote access;
- software development;
- contractors;
- cross-border processing;
- sites and infrastructure;
- other sector-specific facts.

Each applicability decision returns:

`APPLIES / DOES_NOT_APPLY / CONDITIONAL / UNKNOWN`

plus the facts and source rules that caused the decision.

---

## 8. Evidence and audit model

The target traceability chain is:

`SOURCE → CHUNK → SEC-REQ → SEC-CTRL → SEC-CHECK → EVIDENCE → FINDING → RISK → PRIORITY → REMEDIATION → RETEST → CLOSURE`

Evidence may include, depending on the requirement:

- approved orders/policies/regulations;
- contracts and acts;
- configuration exports;
- logs;
- screenshots only where appropriate;
- test protocols;
- SIEM/SOC records;
- asset/inventory records;
- certification/attestation evidence;
- technical measurements;
- signed approvals;
- other reproducible artifacts.

`implemented != verified` and `scanner clean != compliant`.

---

## 9. Approved products, software, licences and hardware — PLANNED DEVELOPMENT TRACK

This is registered as a major development direction after the primary document corpus is established.

Create entities such as:

- `SEC-PRODUCT-*`;
- `SEC-SOFTWARE-*`;
- `SEC-HARDWARE-*`;
- `SEC-SOLUTION-*`;
- `SEC-CERT-*`;
- `SEC-LICENSE-*`;
- `SEC-CONFIG-*`;
- `SEC-VENDOR-*`.

For security products preserve:

- exact product and version;
- manufacturer;
- functional class;
- certificate/registry identifier;
- issuing authority;
- validity dates;
- trust/security class or certified properties;
- certified configuration;
- restrictions and conditions of use;
- supported platforms;
- dependencies;
- compatibility;
- licence model;
- lifecycle/EOL information;
- authoritative registry/source;
- historical status changes.

A product is never marked "approved" merely because a vendor claims compliance. Approval/certification assertions require authoritative evidence.

The desired chain is:

`SEC-REQ → required property → SEC-CTRL → solution class → alternative products/configurations → certificate/licence evidence → compatibility → cost → architecture option`

The system must preserve alternatives instead of recommending a vendor by habit.

---

## 10. Cost and implementation economics — PLANNED DEVELOPMENT TRACK

Cost belongs to architecture and roadmap reasoning, not to the normative truth layer.

Model at least:

- acquisition;
- licences/subscriptions;
- hardware;
- implementation;
- integration;
- migration;
- certification/attestation;
- personnel;
- training;
- support;
- maintenance;
- infrastructure;
- operational overhead;
- renewal;
- change/downtime risk;
- 3/5-year TCO where meaningful.

Cost values must have date, currency, source and confidence. Unknown cost remains unknown.

---

## 11. Security Architecture Engine — REGISTERED DEVELOPMENT DIRECTION

Once requirements, inventory and solution registries are sufficiently mature, the system should compare architecture alternatives rather than emit one unexplained answer.

Example classes:

- minimum compliant architecture;
- balanced architecture;
- target/high-assurance architecture;
- compensating-control option where legally and technically acceptable.

Compare alternatives across:

- requirement coverage;
- security assurance;
- compatibility;
- residual risk;
- operational complexity;
- migration risk;
- implementation time;
- capital/operating cost;
- TCO;
- evidence quality.

Every important choice should produce a decision record explaining selected and rejected alternatives.

---

## 12. Organization inventory / Current State — REGISTERED DEVELOPMENT DIRECTION

Architecture and audit require facts about the actual organization. Planned entity families include:

`SEC-ORG`, `SEC-SYSTEM`, `SEC-ASSET`, `SEC-DATA`, `SEC-DATAFLOW`, `SEC-NETWORK`, `SEC-SOFTWARE`, `SEC-HARDWARE`, `SEC-SOLUTION`, `SEC-CERTIFICATE`, `SEC-LICENSE`, `SEC-CONTRACT`, `SEC-PERSON`, `SEC-ROLE`, `SEC-PROCESS`, `SEC-VENDOR`, `SEC-SITE`.

This layer becomes the factual `CURRENT STATE` against which requirements are assessed.

---

## 13. Audit and development roadmap — REGISTERED DEVELOPMENT DIRECTION

For an organization the target output is not a list of document names. It is a traceable programme:

`Organization → Applicability → Applicable requirements → Current State → Controls → Evidence → Gaps → Findings → Risks → Alternatives → Cost → Decision → Target Architecture → Roadmap → Implementation → Retest → Monitoring`

The audit should be able to generate:

- executive summary;
- scope and assumptions;
- regulatory applicability;
- current architecture/inventory;
- requirement coverage;
- control/evidence coverage;
- findings;
- risks;
- alternatives;
- estimated cost;
- target architecture;
- prioritized remediation/development plan;
- retest and acceptance criteria.

---

## 14. Regulatory Update Engine — REGISTERED DEVELOPMENT DIRECTION

The database must eventually maintain itself under controlled review.

Pipeline:

`AUTHORITATIVE SOURCE → WATCH → CAPTURE → FINGERPRINT → VERSION DIFF → IMPACT ANALYSIS → PROPOSED GRAPH UPDATE → REVIEW → VERIFIED UPDATE → RECOMPUTE APPLICABILITY/COVERAGE/RISK/ROADMAP`

The impact radius can include:

- definitions;
- chunks;
- requirements;
- applicability rules;
- controls;
- checks;
- products/certificates;
- organization profiles;
- findings;
- risks;
- architecture decisions;
- roadmap items.

No legally significant change is silently promoted to verified truth without review.

---

## 15. Time-aware knowledge

The graph must answer both:

- "What is applicable now?"
- "What was applicable on a specified historical date?"

Therefore source versions, interpretations, certificates, licences, applicability decisions and organization assessments require temporal validity.

---

## 16. Conflicts, uncertainty and interpretation

Do not force false certainty.

Maintain explicit objects/states for:

- conflicts between sources;
- ambiguous interpretation;
- missing evidence;
- unresolved applicability;
- superseded interpretation;
- regulator clarification;
- judicial/enforcement practice where relevant.

A conflict is a review task, not permission for an agent to silently choose the convenient source.

---

## 17. Provenance rule

Every important answer must support forward and reverse traceability.

Forward:

`ORIGINAL → STRUCTURE → CHUNK → REQUIREMENT → CONTROL → CHECK → EVIDENCE → DECISION`

Reverse:

`DECISION → EVIDENCE → CHECK → CONTROL → REQUIREMENT → CHUNK → EXACT SOURCE VERSION`

If the chain breaks, confidence must decrease and the missing link must remain visible.

---

## 18. Development registry

| Track | Status | Priority | Dependency |
|---|---|---:|---|
| Primary document corpus | **ACTIVE** | P0 | none |
| Version history and immutable provenance | **ACTIVE** | P0 | document corpus |
| Structural parsing and chunking | ACTIVE/BUILDING | P0 | source ingestion |
| Definitions and atomic requirements | ACTIVE/BUILDING | P0 | verified sources |
| Intra/inter-document graph | ACTIVE/BUILDING | P0 | requirements |
| Applicability engine | BUILDING | P1 | requirements + organization facts |
| Controls/checks/evidence graph | BUILDING | P1 | requirements |
| Coverage/risk/priority/roadmap | BUILDING | P1 | controls + evidence |
| FSTEC/FSB approved solution and certificate registry | **REGISTERED** | P1 | source registry |
| Software/hardware/licence inventory | **REGISTERED** | P1 | solution registry + Current State |
| Organization Current State inventory | **REGISTERED** | P1 | organization model |
| Security Audit Engine | **REGISTERED** | P1 | applicability + Current State + evidence |
| Cost/TCO model | **REGISTERED** | P2 | alternatives + market/source data |
| Security Architecture Engine | **REGISTERED** | P2 | audit + products + costs |
| Development programme / target roadmap | **REGISTERED** | P2 | risks + architecture decisions |
| Regulatory Update Engine | **REGISTERED** | P1 | stable source/version model |
| Automatic impact and weight recalculation | **REGISTERED** | P1 | update engine + graph |

**Current execution rule:** do not let future architecture features distract from Phase 1. Build the document base first, but preserve the schemas and IDs needed by later phases.

---

## 19. Definition of success for the first usable release

Given a real organization profile, the system can produce a defensible list of applicable security requirements where every item exposes:

1. exact source and version;
2. exact source location;
3. why it applies;
4. atomic requirement;
5. responsible role;
6. required organizational action;
7. required evidence;
8. mapped controls/checks when available;
9. unresolved uncertainty;
10. links to related documents.

Only after this is dependable do product selection, cost optimization and target architecture become trusted automation rather than attractive guesses.

---

## 20. Guiding principle

**Facts first. Relationships second. Weights third. Decisions last.**

The knowledge base may evolve its scoring, ranking and architecture algorithms many times. It must never lose the original evidence that allows those algorithms to be challenged and rebuilt.
