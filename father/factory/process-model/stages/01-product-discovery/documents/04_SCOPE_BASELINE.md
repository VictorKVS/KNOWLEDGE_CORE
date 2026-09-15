# SCOPE BASELINE — FATHER Analytical Design Platform

Status: `OWNER_CONFIRMED_WITH_OPEN_BOUNDARIES`

Accountable owner: `product_manager`

Review: `business_owner`, `project_manager`

## In scope — current factory MVP

- lifecycle/process model from Product to Retirement;
- normative/source registry and applicability overlays;
- artifact registry and machine-readable schemas;
- role/authority model;
- evidence/provenance graph;
- stage/gate engine;
- visual navigation from L0 lifecycle to L1/L2/L3 detail;
- brownfield document intake, mapping and gap/conflict analysis;
- professional-agent support with independent review controls;
- metrics for completeness, conflicts, UNKNOWNs, evidence and maturity;
- trace from source/normative requirement to artifact/decision/test evidence;
- Product, Security Intake, System Engineering and Threat Model v0 as first validated production stages.

## Out of scope for the current MVP

- autonomous acceptance of residual risk;
- autonomous legal/compliance declaration;
- autonomous owner approval of material decisions;
- unrestricted multi-agent swarm;
- replacing original source documents with LLM summaries;
- hiding uncertainty to make a gate pass;
- selecting a universal architecture before project-specific evidence exists.

## Open boundaries

| Boundary | State | Why it remains open |
|---|---|---|
| exact UI technology | UNKNOWN | architecture/design decision comes later |
| deployment topology | UNKNOWN | Security/System/Architecture evidence required |
| external integration catalogue | PARTIAL | depends on first target deployment/project |
| commercial packaging | UNKNOWN | not required for current engineering pilot |
| tenant model | UNKNOWN | required before multi-project production design |
| external identity/IAM provider | UNKNOWN | design choice deferred |

## Change control

Any material scope change must record:

`change -> owner -> reason -> affected artifacts -> affected gates -> security/system impact -> review state`.
