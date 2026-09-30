# Architect Project Intake Playbook

- **Knowledge domain:** `SOFTWARE_ENGINEERING`
- **Knowledge space:** `KB-SOFTWARE-ENGINEERING`
- **Status:** `CANDIDATE_PRACTICE`
- **Purpose:** practical intake procedure for an architect entering a project before material architecture decisions are made
- **Cross-domain rule:** this playbook may request and structure inputs owned by Product, Business Analysis, Security, Operations, Procurement, Finance or Project Management, but it does **not** grant Software Engineering authority to invent or silently override those domains' facts
- **Promotion state:** not expert-ready; requires independent review and evidence admission before promotion to verified professional doctrine

## 1. Core principle

An architect does not wait for an “ideal specification”. The architect must determine which inputs are required to make defensible decisions, inspect what exists, identify gaps, obtain missing information from the correct owner and create working drafts when necessary.

A draft created by the architect is **not a fact merely because it is written down**. Missing information follows this controlled path:

```text
EXPECTED INPUT
   ↓
PRESENT? ── yes ──> VERIFY SOURCE / VERSION / OWNER / QUALITY
   │
   no
   ↓
GAP
   ↓
IDENTIFY INFORMATION OWNER
   ↓
REQUEST / INTERVIEW / WORKSHOP / OBSERVATION / REVERSE ENGINEERING
   ↓
ARCHITECT DRAFTS STRUCTURED ARTIFACT WHEN NEEDED
   ↓
OWNER REVIEW
   ↓
CONFIRMED / REJECTED / STILL UNKNOWN
```

**Invariant:** `ASSUMPTION != REQUIREMENT != FACT != DECISION`.

## 2. Intake states

Every expected input should have an explicit state:

| State | Meaning |
|---|---|
| `EXPECTED` | Required for the project context but not yet requested |
| `REQUESTED` | Requested from an identified owner |
| `RECEIVED` | Material received but not yet quality-checked |
| `VERIFIED` | Source, version, owner and applicability checked |
| `PARTIAL` | Exists but is incomplete, stale or ambiguous |
| `CONFLICTED` | Materially conflicts with another source |
| `GAP` | Missing and architecture impact is known or suspected |
| `DRAFTED_BY_ARCHITECT` | Working reconstruction prepared by the architect |
| `OWNER_REVIEW` | Awaiting validation from the authoritative owner |
| `CONFIRMED` | Accepted by the information owner for project use |
| `REJECTED` | Owner or evidence invalidated the draft/input |
| `NOT_APPLICABLE` | Explicitly assessed as irrelevant to the project |

Unknown is a valid state. It is not replaced with a convenient guess.

## 3. What should arrive on the architect's desk

The table below is an **ideal intake inventory**. Not every project needs every artifact as a separate document; several may be combined. The architect cares about the information, ownership, freshness and evidence, not paperwork for its own sake.

### A. Why the product exists

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-01` | Product Vision | Product Owner / Sponsor | approved vision, strategy memo, workshop | goal, target users, horizon and boundaries are explicit | run vision workshop; draft one-page vision for owner review | defines problem boundary and evolution direction |
| `IN-02` | Business Need / Problem Statement | Sponsor / Business Owner | interview, business brief, metrics | describes problem/opportunity, not a predetermined technology | rewrite technology request into measurable need and validate | prevents solution-first architecture |
| `IN-03` | Business Case | Sponsor / Finance / Product | investment memo, cost/benefit model | benefits, costs, risks, assumptions and time horizon visible | request economics; create provisional model with assumptions | constrains cost, buy/build and rollout decisions |
| `IN-04` | Success Metrics / Outcomes | Product / Business Owner | OKR/KPI set, service metrics | measurable baseline and target exist | define candidate measures and get owner agreement | gives architecture measurable business outcomes |

### B. Who matters and who can decide

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-05` | Stakeholder Register | Sponsor / PM / BA | org map, interviews, RACI | decision rights and affected groups are explicit | build stakeholder map; validate with sponsor | determines concerns, review participants and escalation path |
| `IN-06` | Sponsor / Decision Authority | Governance / Sponsor | charter, steering model | final business decision authority is named | explicitly ask who can accept scope/cost/risk changes | prevents approval ambiguity |
| `IN-07` | SME Map | Business / Operations | interviews, team lists | domain and system experts are named by topic | discover SMEs during workshops and system walkthroughs | identifies authoritative sources for domain facts |
| `IN-08` | End-user / Operator groups | Product / Operations | personas, roster, field observation | real users separated from management assumptions | interview/observe representative users | exposes workflow, usability and operational constraints |

### C. What is being built

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-09` | Scope / Out of Scope | Sponsor / Product / PM | scope statement, charter, backlog | boundaries and exclusions are explicit | facilitate scope workshop and create baseline draft | bounds solution and estimate |
| `IN-10` | Business Requirements | Business Owner / BA | BRD/BFT, backlog, interviews | trace to business need and owner | elicit and structure requirements | establishes required outcomes |
| `IN-11` | Stakeholder Requirements | BA / Stakeholders | interviews, journeys, use cases | each requirement has source/owner | conduct elicitation and record source | translates stakeholder needs into solution expectations |
| `IN-12` | Functional Requirements | Product / BA / Domain SMEs | use cases, stories, specification | testable behavior and exceptions included | derive candidate capabilities; validate | shapes component responsibilities and interfaces |
| `IN-13` | NFR / Quality Attributes | Business + Operations + Security + Architecture | SLOs, policy, workshops | measurable latency, availability, security, scalability etc. | run quality-attribute workshop; mark unknown thresholds | architecture-driving constraints and trade-offs |
| `IN-14` | Acceptance Criteria | Product / QA / Business | backlog, contract, test plan | objectively testable and tied to requirement | draft with QA/product, then approve | defines completion and evidence gates |
| `IN-15` | Assumptions | All contributors; architect maintains log | meetings, estimates, design sessions | owner and validation trigger recorded | create assumption log immediately | prevents guesses from becoming hidden design facts |
| `IN-16` | Constraints | Business / Security / Operations / Procurement | policy, budget, platform standards, contract | hard vs negotiable separated | discover through interviews and source review | prunes architecture option space |

### D. How the business and current system work

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-17` | Business Processes / Journeys | Process Owner / BA | BPMN, SOP, observation | happy path + exceptions + handoffs covered | model AS-IS process from interviews/observation | exposes system boundaries and integration points |
| `IN-18` | Domain Model / Glossary | Domain SMEs / BA | glossary, conceptual model, regulations | terms have unambiguous meaning and ownership | build working glossary during discovery | prevents semantic mismatch in APIs/data/models |
| `IN-19` | AS-IS Architecture | Current system owners / Architecture | C4, network/app diagrams, CMDB | version/date/environment and owners known | reverse engineer from repos, runtime, configs and interviews | establishes migration constraints and dependencies |
| `IN-20` | Integration Inventory | System owners / Integration team | OpenAPI, async specs, interface catalog | protocol, owner, auth, SLA and data contract known | inventory traffic/configs and interview owners | drives interface and failure-mode design |
| `IN-21` | Data Inventory / Data Model | Data Owners / DBA / Analytics | ERD, schemas, catalog, samples | owner, classification, lineage, quality and retention known | profile schemas/samples with permission; draft data map | drives storage, privacy, migration and RAG/ML feasibility |

### E. Security, compliance and trust

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-22` | Data Classification / Privacy rules | Security / Legal / Data Owner | policy, data catalog, regulation mapping | classes and handling rules tied to actual data | request security/legal review; do not infer legal permission | establishes trust boundaries and processing restrictions |
| `IN-23` | IAM / Identity model | IAM / Security / Platform | IdP docs, role matrix, auth flows | identities, roles, authN/authZ and lifecycle covered | model current identity flow and validate with IAM owner | drives access-control architecture |
| `IN-24` | Security / Compliance Requirements | Security / Compliance | security baseline, threat model, control catalog | mandatory vs advisory controls separated | initiate security requirements workshop | constrains components, hosting, logging and integrations |

### F. Operability, load and platform reality

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-25` | SLA / SLO / Support Model | Service Owner / Operations | service catalog, SLA, on-call/runbook | availability, latency, support hours and escalation measurable | derive candidate SLOs from business impact; owner approval required | drives redundancy, observability and failure budgets |
| `IN-26` | Load / Capacity Profile | Product / Operations / Analytics | traffic metrics, forecasts, seasonality | averages + peaks + concurrency + growth + payload sizes | instrument current system or create bounded scenarios | drives sizing and scaling choices |
| `IN-27` | Platform / Environment Constraints | Platform / DevOps / Cloud / Infrastructure | landing-zone rules, clusters, network zones, supported services | version, quota, region and lifecycle explicit | run platform discovery and record unknowns | limits deployable topology and technologies |
| `IN-28` | Incident / Problem History | Operations / SRE / Support | incident DB, postmortems, tickets | recurring failure modes and impact visible | interview operations and sample recent incidents | provides empirical failure evidence |

### G. Delivery, commercial and prior decisions

| ID | Expected input | Information owner | Typical acquisition | Quality check | If missing | Architecture use |
|---|---|---|---|---|---|---|
| `IN-29` | Roadmap / Team / Schedule / Budget | PM / Product / Finance / Engineering managers | delivery plan, staffing, budget | skills, deadlines, dependency dates and cost envelope explicit | build constraint snapshot and escalate unknown commitments | determines feasible architecture and sequencing |
| `IN-30` | Commercial / Contract model | Procurement / Legal / Sponsor | RFP/SOW/FP/T&M/T&M-cap terms | scope-change, acceptance, liability and dependencies understood | request contract summary; architect flags technical ambiguity, not legal conclusions | changes uncertainty allocation and documentation depth |
| `IN-31` | Existing ADRs + PoC/Benchmarks + decision history | Architecture / Engineering / Product | ADR log, experiments, benchmarks | context, date, environment, limitations and supersession known | recover history from Git/PRs/interviews; mark confidence | prevents repeating failed decisions and supports trade-offs |

## 4. Mandatory architect-owned working artifacts

These are not necessarily authoritative business documents. They are the architect's controlled working surfaces used to make gaps visible and decisions auditable.

| Artifact | Purpose |
|---|---|
| `INTAKE_REGISTER` | inventory of expected/received inputs, owners, versions and states |
| `QUESTIONS_LOG` | unresolved questions, owner, due date, architecture impact |
| `ASSUMPTION_LOG` | explicit assumptions with validation trigger and expiry/review condition |
| `CONSTRAINT_REGISTER` | hard/soft constraints, source and negotiability |
| `RISK_REGISTER` | architecture-relevant risks with probability/impact/owner/response |
| `STAKEHOLDER_MAP` | stakeholders, concerns, decision rights and review role |
| `SCOPE_BASELINE` | current in/out boundary and approved change history |
| `NFR_CATALOGUE` | measurable quality attributes and source/owner |
| `AS_IS_MAP` | current systems, dependencies and trust boundaries |
| `DECISION_BACKLOG` | architecture-significant choices that need ADR or evidence |
| `EVIDENCE_REGISTER` | sources, measurements, experiments and limitations used by decisions |

## 5. Minimum gate before material architecture decisions

A material design decision should not be presented as “the architecture” while all of the following remain unknown without explicit risk acceptance:

1. business problem / outcome;
2. decision authority and affected stakeholders;
3. scope boundary;
4. architecture-driving requirements and NFRs;
5. hard constraints;
6. current-system dependencies when modifying an existing landscape;
7. security/data handling constraints relevant to the decision;
8. workload or bounded load assumptions when performance/cost matters;
9. delivery and commercial constraints that materially affect feasibility;
10. unresolved gaps and assumptions.

If one is missing, the architect may continue **exploration**, PoC, option analysis or reverse engineering, but the gap must remain visible in the decision record.

## 6. Intake interview pattern

For every incoming statement, classify before designing:

```text
Who said it?
What type is it?
  FACT / CLAIM / REQUIREMENT / CONSTRAINT / ASSUMPTION / PREFERENCE / PROPOSED_SOLUTION / RISK / GAP
What evidence supports it?
Who owns confirmation?
Is it current for this project/version/environment?
What architecture decision changes if it is false?
```

Example:

> “We need Kubernetes, 10,000 users, and it must be ready in two months.”

Do not store this as one requirement.

```text
“Kubernetes”
→ proposed solution / possible platform constraint
→ ask which requirement it is intended to satisfy

“10,000 users”
→ capacity claim
→ clarify registered vs active vs concurrent, workload shape and peak window

“two months”
→ schedule constraint
→ identify authority, mandatory scope and consequences of missing the date
```

## 7. Cross-domain ownership boundaries

This playbook lives in Software Engineering because it governs **architecture intake and decision readiness**, but many inputs are not owned by Software Engineering.

| Input family | Likely canonical owner domain | Software Engineering role |
|---|---|---|
| Product vision, value, priority | `PRODUCT_PROJECT` | consume, challenge ambiguity, trace to decisions |
| Business/stakeholder requirements | `BUSINESS_ANALYSIS` | consume, verify architecture relevance, derive design questions |
| Procurement/RFP/contract semantics | `PROCUREMENT_VENDOR` + Legal | consume technical constraints; do not invent legal interpretation |
| Security/compliance truth | `SECURITY` / `LEGAL_COMPLIANCE` | map controls to architecture and escalate conflicts |
| Platform operations | `DEVOPS_SRE` / `CLOUD_ARCHITECTURE` | consume operational constraints and test feasibility |
| Cost/budget authority | `FINANCE_ACCOUNTING` / Sponsor | model TCO/options; do not redefine approved budget |

Until those planned domains are materialized in `professional-knowledge/`, their inputs remain explicit cross-domain dependencies rather than silently absorbed Software Engineering facts.

## 8. Evidence and provenance policy

This playbook follows the repository's evidence-first rules:

- project-specific requirements and constraints outrank generic preferences;
- source identity, owner, version/date and applicability should be recorded when material;
- conflicting sources remain conflicted until resolved or escalated;
- model-generated explanations are discovery candidates, not verified truth;
- benchmarks do not generalize beyond their workload/environment without evidence;
- missing product/business/legal authority is not substituted by an architect's opinion.

Relevant repository contracts:

- `father/domain-knowledge/PROFESSIONAL_EVIDENCE_DOCTRINE.md`
- `professional-knowledge/software-engineering/DOMAIN.yaml`
- `professional-knowledge/software-engineering/SOURCE_POLICY.yaml`
- `father/domain-knowledge/professional-decision-schema.yaml`

## 9. Current provenance of this candidate playbook

This candidate was created from the active OTUS AI Architect learning project and then adapted to the governance model of `KNOWLEDGE_CORE`.

Project source:

- `VictorKVS/OTUS-`
- lesson 1: “Пресейл, контракты и работа с требованиями: закладываем фундамент проекта”
- project artifact: `1. Пресейл, контракты и работа с требованиями закладываем фундамент проекта/ARCHITECT_INTAKE_PACK.md`

The OTUS lesson explicitly covers presales, initial requirement analysis, hidden requirements, business context, RFP analysis, Fixed Price / Time & Materials / T&M with cap, Change Management and project uncertainty. The expanded intake inventory in this document is a **derived practice model**, not a claim that all 31 artifacts are explicitly required by the lesson or by a single external standard.

## 10. Promotion requirements

Before promoting this candidate beyond practice guidance:

1. map each normative-looking statement to admitted sources or project requirements;
2. independently review the 31-input inventory for overreach and missing categories;
3. test the playbook against at least:
   - greenfield product discovery;
   - brownfield/legacy modernization;
   - regulated/security-sensitive project;
   - procurement-led RFP project;
   - small MVP where excessive intake would be wasteful;
4. record negative cases where a listed artifact is intentionally unnecessary;
5. ensure the playbook does not turn “ideal input pack” into mandatory bureaucracy;
6. preserve cross-domain authority boundaries.

## 11. Practical definition of done for intake

Intake is sufficient when the architect can answer, with source/owner confidence:

- **Why** are we changing the system?
- **Who** owns outcomes and decisions?
- **What** is in and out of scope?
- **Which requirements and quality attributes drive architecture?**
- **Which constraints are hard, negotiable or still assumed?**
- **What does the current system/data/integration landscape actually look like?**
- **What security, operational and workload realities constrain options?**
- **What delivery/commercial boundaries affect feasibility?**
- **What is still unknown?**
- **Which architecture decisions now have enough evidence to enter ADR analysis?**

The goal is not to collect every document. The goal is to make architecture decisions from explicit, owned and testable context rather than hidden assumptions.
