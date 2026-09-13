# Stage 01 — Product Document Pack

Status: `CANDIDATE_PRODUCT_PACK / PILOT_FILLED`

Purpose: the canonical information package produced by Product before Security Intake. These are **information artifacts**, not a requirement that every organization create separate Word files.

## Normative positioning

FATHER uses the current standards as a baseline and keeps exact clause-level mapping separate until full-text ingestion/review:

- `ГОСТ Р 57193-2025` — system life-cycle process baseline;
- `ГОСТ Р 58609-2019 / ISO/IEC/IEEE 15289:2017` — life-cycle information items; information items may be combined or split for project/organizational needs;
- `ГОСТ Р 59793-2021` — creation stages for automated systems; Product Pack supplies the early information needed for formation of requirements and concept work;
- `ГОСТ 34.602-2020` — technical assignment for an automated system; Product supplies upstream product/business inputs but **does not own the complete ТЗ**.

No document below claims clause-level compliance until `source -> clause -> requirement -> artifact field` mapping is reviewed.

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
