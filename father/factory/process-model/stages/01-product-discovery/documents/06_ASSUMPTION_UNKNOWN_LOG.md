# ASSUMPTION / UNKNOWN LOG — FATHER Analytical Design Platform

Status: `OPEN`

Accountable owner: `project_manager`

Review: `skeptical_reviewer`

## Assumptions

| ID | Statement | Owner | Validation trigger | Downstream impact |
|---|---|---|---|---|
| A-01 | A canonical artifact/evidence model can support multiple delivery methodologies without forcing waterfall | Product Manager | apply to iterative and brownfield projects | process model |
| A-02 | BPMN + IDEF0 + DMN + RACI + graph navigation will be sufficiently understandable for engineering users | Product Manager | usability review on working L0-L3 prototype | visualization architecture |
| A-03 | Professional KBs can support roles while independent review prevents self-certification | Knowledge Growth Analyst | role evals + independent domain review | agent architecture |
| A-04 | Existing project evidence can often be mapped into canonical artifacts without duplicating documents | Product Manager | brownfield pilot | document intake architecture |

## UNKNOWNs

| ID | Unknown | Owner to resolve | Impact | Required by |
|---|---|---|---|---|
| U-01 | exact first external user/persona set | Product Manager | UX/prioritization | before external product validation |
| U-02 | first production deployment topology | System/Architecture/Security | trust boundaries/security controls | before architecture decision |
| U-03 | commercial/noncommercial distribution model | Business Owner/Product | legal/product constraints | before commercialization |
| U-04 | tenant/project isolation model | Product + System + Security | confidentiality/authorization | before multi-project architecture |
| U-05 | external identity provider model | System/Security | IAM/authorization | before detailed design |
| U-06 | exact retention requirements for project evidence | Data Owner/Legal/Security | storage/deletion/audit | before data design |

## Conflict log

No material Product-stage conflicts are currently recorded. This field must remain explicit; `none recorded` is not equivalent to `conflicts impossible`.

## Rule

An assumption/UNKNOWN may be closed only by evidence or accountable owner decision. A model-generated answer alone does not close it.
