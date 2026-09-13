# FATHER — Pre-Architecture Role Handoff

Status: `CANDIDATE / MACHINE-MAPPED`

Goal: show exactly what every role must contribute before a Solution Architect may create architecture options.

## End-to-end handoff

```text
BUSINESS OWNER
   ↓ business need / authority
PRODUCT
   ↓ vision / users / value / journeys / PRD / MVP / metrics / roadmap / backlog
PROJECT + BA
   ↓ stakeholders / business process / rules / glossary / constraints / dependencies
SECURITY + LEGAL + DATA OWNER
   ↓ security intake / applicability / data classification / abuse cases / constraints
SYSTEM ENGINEERING + INTEGRATION
   ↓ context / boundary / functions / DFD / interfaces / dependencies / modes
THREAT MODEL v0
   ↓ scenarios / trust boundaries / security drivers / draft requirements
OPS / PLATFORM + FINANCE / PROCUREMENT + QA
   ↓ SLO/platform/load / budget-commercial / testability-acceptance inputs
REQUIREMENTS ENGINEER
   ↓ stakeholder/system/software/NFR/security requirements + acceptance + RTM
KGA + SKEPTICAL REVIEW
   ↓ evidence/conflicts/unknowns + independent challenge
PRE_ARCHITECTURE_PACKAGE
   ↓
SOLUTION ARCHITECT
```

## What each role contributes

| Role | Key inputs it receives | What it must establish | Canonical outputs before Architecture |
|---|---|---|---|
| Business Owner | initiative/sponsor context | real business problem, expected effect, authority | BUSINESS_NEED |
| Product Manager | business need + user/market evidence | users, value, vision, scope, product requirements, metrics, priorities | PRODUCT_VISION, TARGET_USER_SEGMENTS, VALUE_PROPOSITION, USER_JOURNEY, PRD, MVP_SCOPE, SUCCESS_METRICS, ROADMAP, BACKLOG |
| Project Manager | scope + org constraints | stakeholders, authority, schedule, dependencies, assumptions | STAKEHOLDER_REGISTER, DECISION_AUTHORITY_MAP, ASSUMPTION_LOG, PROJECT_CONSTRAINT_SNAPSHOT, DEPENDENCY_REGISTER |
| Business Analyst | Product package + stakeholder evidence | business processes, rules, exceptions, domain language | BUSINESS_PROCESS_MODEL, DOMAIN_GLOSSARY, BUSINESS_RULE_CATALOGUE, BUSINESS_REQUIREMENTS |
| Security Engineer | Product + business/data context | early security context, exposure, abuse, constraints, v0 threats | SECURITY_INTAKE, ABUSE_CASES, SECURITY_CONSTRAINTS, THREAT_MODEL_V0, SECURITY_REQUIREMENTS_DRAFT |
| Legal / Compliance | scope + data + jurisdiction | which mandatory requirements actually apply | REGULATORY_APPLICABILITY, MANDATORY_REQUIREMENT_REGISTER, LEGAL_QUESTIONS |
| Data Owner | business/data evidence + applicability | classes, sensitivity, allowed processing/sharing/retention intent | DATA_INVENTORY, DATA_CLASSIFICATION, DATA_OWNER_MATRIX, DATA_HANDLING_CONSTRAINTS |
| System Engineer | Product + Security + Data | system context/boundary/functions/flows/modes | SYSTEM_CONTEXT, SYSTEM_BOUNDARY, FUNCTION_MODEL, DATA_FLOW_MODEL, OPERATIONAL_MODES |
| Integration Engineer | system context + external systems | interfaces, protocol/auth/owner/SLA/failure dependency | INTERFACE_INVENTORY, INTEGRATION_CONSTRAINTS, EXTERNAL_SYSTEM_DEPENDENCY_MAP |
| Operations / Platform | product/system context + current runtime | SLO/SLA, support, environment limits, load/capacity, incidents | SLA_SLO_INPUTS, SUPPORT_MODEL, PLATFORM_ENVIRONMENT_CONSTRAINTS, CAPACITY_LOAD_PROFILE, INCIDENT_HISTORY |
| Finance / Procurement | scope + project/vendor context | budget envelope, buy/build, license/contract/procurement constraints | COST_BUDGET_CONSTRAINTS, COMMERCIAL_CONTRACT_CONSTRAINTS, PROCUREMENT_DEPENDENCY_REGISTER |
| QA / Verification | product metrics + candidate requirements | testability, acceptance evidence, unverifiable statements | ACCEPTANCE_CRITERIA_INPUTS, VERIFICATION_CONSTRAINTS, TESTABILITY_GAPS |
| Requirements Engineer | all above | one measurable, traceable baseline | STAKEHOLDER_REQUIREMENTS, SYSTEM_REQUIREMENTS, SOFTWARE_REQUIREMENTS, NFR_CATALOGUE, SECURITY_REQUIREMENTS, ACCEPTANCE_CRITERIA, RTM |
| Knowledge Growth Analyst | all sources/artifacts | provenance, gaps, conflicts, freshness | EVIDENCE_REGISTER, KNOWLEDGE_GAP_REGISTER, CONFLICT_REGISTER, SOURCE_FRESHNESS_REPORT |
| Skeptical Reviewer | material package + evidence | hidden assumptions, contradictory evidence, failure modes, alternatives | PRE_ARCHITECTURE_INDEPENDENT_REVIEW |

## Architect entry rule

The architect receives **facts, requirements, constraints, evidence and explicit UNKNOWNs**. The architect does not inherit authority to rewrite them.

Architecture exploration may start only after the mandatory pre-architecture package is available. A material architecture decision is forbidden while Product, Security, System Model, Threat Model v0 or Requirements Baseline is missing.

Canonical machine-readable contract: `PRE_ARCHITECTURE_PACKAGE.yaml`.
