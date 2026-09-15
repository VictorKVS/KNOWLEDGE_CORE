# PRODUCT HANDOFF TO SECURITY — FATHER Analytical Design Platform

Status: `READY_WITH_CONDITIONS`

Accountable owner: `product_manager`

Receiving role: `security_engineer`

## Handoff package

Security receives the following Product outputs as controlled inputs:

- `01_BUSINESS_NEED.md`;
- `02_PRODUCT_VISION.md`;
- `03_STAKEHOLDER_REGISTER.md`;
- `04_SCOPE_BASELINE.md`;
- `05_SUCCESS_METRICS.md`;
- `06_ASSUMPTION_UNKNOWN_LOG.md`;
- Product-stage evidence/provenance records;
- `08_PRODUCT_READY_DECISION.md`.

## Confirmed Product facts/constraints passed downstream

1. FATHER is an analytical engineering design environment, not a generic document generator.
2. Visualization and evidence analytics are first-class product capabilities.
3. Security is the first mandatory engineering discipline after Product.
4. Material decisions require traceability and accountable review.
5. FACT / CLAIM / ASSUMPTION / HYPOTHESIS / UNKNOWN must remain distinguishable.
6. Agents/models cannot self-certify material decisions or accept residual risk.
7. Existing evidence should be mapped/reused before duplicate artifacts are created.

## Conditions / unresolved inputs passed explicitly

- exact deployment topology;
- tenant/project isolation model;
- exact external user/persona set;
- external identity provider model;
- project-evidence retention rules;
- commercial/distribution model;
- final Legal/Compliance and Data Owner person assignments.

These are not blockers to start Security Intake, but they must remain visible and may become blockers for later gates.

## Required Security response

Security must return, at minimum:

- `SECURITY_INTAKE`;
- `DATA_CLASSIFICATION` with Data Owner involvement;
- `REGULATORY_APPLICABILITY` with Legal/Compliance involvement;
- `INITIAL_ABUSE_CASES`;
- `SECURITY_CONSTRAINTS`;
- `SECURITY_QUESTIONS_LOG`;
- `SECURITY_INTAKE_READY` decision.

## Boundary

Product does not tell Security which legal overlay is applicable and does not prescribe the threat model. It supplies the product context, constraints, actors, scope, success intent and unresolved questions needed for Security to perform its own accountable work.
