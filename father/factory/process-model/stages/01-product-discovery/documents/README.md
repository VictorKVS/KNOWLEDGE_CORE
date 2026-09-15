# Stage 01 — Product Document Pack

Status: `CANDIDATE_PRODUCT_PACK / PILOT_FILLED / CLAUSE_TRACEABILITY_ACTIVE`

Purpose: the canonical information package produced by Product before Security Intake. These are **information artifacts**, not a requirement that every organization create separate Word files.

## Normative positioning

FATHER now maintains two normative layers for every artifact:

1. standard/source level — which GOST/order/methodology governs the information;
2. clause level — exact clause/subclause, applicability, responsible role, artifact field and validation method.

Current Product clause mappings are stored in `PRODUCT_GOST_CROSSWALK.yaml` and follow the common `father/factory/CLAUSE_TRACEABILITY_SCHEMA.yaml` contract.

Verified Product-stage clause families currently include:

- `ГОСТ Р 57193-2025`: `6.4.1.2`, `6.4.1.3`, `6.4.2.1`, `6.4.2.2`, `6.4.2.3`;
- `ГОСТ Р 59793-2021`: `4.1`, stages `1.1–1.3`, `2.1–2.5`, plus tailoring rule `4.2`;
- `ГОСТ 34.602-2020`: `4.1`, `4.2`, `4.3`, `4.4`, `4.4.1`, `4.4.2`, `4.5` as downstream ТЗ bindings;
- `ГОСТ Р 58609-2019 / ISO/IEC/IEEE 15289:2017`: information-item model confirmed at scope/section level; exact subclause binding remains `SECTION_VERIFIED_SUBCLAUSE_PENDING` until full-text ingestion.

A clause is never invented. If the source text/number has not been verified, the mapping stays `CLAUSE_NOT_VERIFIED` or `SECTION_VERIFIED_SUBCLAUSE_PENDING`.

## Product-owned / Product-coordinated artifacts

| Order | Artifact | Accountable owner | Review | Main downstream consumer |
|---|---|---|---|---|
| 01 | `BUSINESS_NEED.md` | Business Owner | Product Manager | Security / System / Requirements |
| 02 | `PRODUCT_VISION.md` | Product Manager | Business Owner | Security / System |
| 03 | `STAKEHOLDER_REGISTER.md` | Project Manager | Product Manager | Security / System / Governance |
| 04 | `SCOPE_BASELINE.md` | Product Manager | Business Owner + PM | Security / System |
| 05 | `SUCCESS_METRICS.md` | Product Manager | Business Owner | Requirements / Validation |
| 06 | `ASSUMPTION_UNKNOWN_LOG.md` | Project Manager | Skeptical Reviewer | all downstream roles |
| 07 | `PRODUCT_HANDOFF_TO_SECURITY.md` | Product Manager | Security Engineer | Security Intake |
| 08 | `PRODUCT_READY_DECISION.md` | Product Manager | Business Owner + Skeptical Reviewer | Gate engine |

## Traceability model

```text
DOCUMENT
  ↓
SECTION / FIELD
  ↓
SOURCE (GOST / order / FATHER Constitution)
  ↓
CLAUSE / SUBCLAUSE
  ↓
REQUIREMENT SUMMARY
  ↓
APPLICABILITY CONDITION
  ↓
LIFECYCLE STAGE
  ↓
ACCOUNTABLE ROLE
  ↓
VALIDATION METHOD
  ↓
GATE / DOWNSTREAM CONSUMER
```

This is the format the future FATHER UI should render as a drill-down panel next to each document field.

## Product boundary

Product is accountable for **why / for whom / what outcome / what scope / who decides / how success is recognized**.

Product must **not** silently author:

- legal applicability conclusions;
- data protection classification on behalf of the Data Owner/Security/Legal roles;
- system architecture;
- threat model;
- complete system/software requirements baseline;
- residual-risk acceptance.

## Handoff rule

```text
BUSINESS_NEED
PRODUCT_VISION
STAKEHOLDER_REGISTER
SCOPE_BASELINE
SUCCESS_METRICS
ASSUMPTION_UNKNOWN_LOG
PRODUCT_READY_DECISION
        ↓
PRODUCT_HANDOFF_TO_SECURITY
        ↓
SECURITY_INTAKE
```

A missing artifact is not auto-generated as fact. It becomes `GAP`, `UNKNOWN`, or a `DRAFT` that must be confirmed by its information owner.
