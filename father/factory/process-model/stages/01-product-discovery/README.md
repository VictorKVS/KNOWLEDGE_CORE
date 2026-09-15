# Stage 01 — Product Discovery

Status: `CANDIDATE_PROCESS`

Goal: turn an initial initiative into an evidence-backed product context that Security can consume immediately after Product.

## L2 process map

```mermaid
flowchart LR
    A([Initiative / Sponsor Context]) --> B[PD-01 Register initiative and provenance]
    B --> C[PD-02 Define Business Need]
    C --> D[PD-03 Define Product Vision]
    D --> E[PD-04 Stakeholders + Decision Authority]
    E --> F[PD-05 Scope Baseline]
    F --> G[PD-06 Success Metrics]
    G --> H[PD-07 Assumptions / UNKNOWN / Conflicts]
    H --> I{PD-08 PRODUCT_READY gate}
    I -->|PASS| J([Security Intake])
    I -->|CONDITIONAL_PASS| J
    I -->|BLOCKED| K[Close blocking gaps]
    K --> C
    I -->|INSUFFICIENT_EVIDENCE| L[Acquire evidence]
    L --> B
```

## Role swimlanes

```mermaid
flowchart TB
  subgraph BO[Business Owner / Sponsor]
    BO1[Problem / opportunity]
    BO2[Confirm need, authority, outcomes]
  end
  subgraph PM[Product Manager]
    PM1[Product Vision]
    PM2[Scope Baseline]
    PM3[Success Metrics]
    PM4[Readiness review]
  end
  subgraph BA[Business Analyst]
    BA1[Clarify actors, need, boundaries]
  end
  subgraph PJ[Project Manager]
    PJ1[Stakeholder Register]
    PJ2[Assumption / UNKNOWN Log]
  end
  subgraph KG[Knowledge Growth Analyst]
    KG1[Evidence structure / provenance / gaps]
  end
  subgraph SR[Skeptical Reviewer]
    SR1[Challenge assumptions and hidden conflicts]
  end
  subgraph SEC[Security Engineer]
    SEC1([Receives PRODUCT_READY package])
  end

  BO1 --> BA1 --> PM1 --> PJ1 --> PM2 --> PM3 --> PJ2 --> PM4
  KG1 -. evidence governance .-> PM1
  KG1 -. evidence governance .-> PJ2
  BO2 --> PM4
  SR1 --> PM4
  PM4 --> SEC1
```

## IDEF0 / ICOM passport

| ICOM | Product Discovery |
|---|---|
| **Input** | business need claim, sponsor context, initiative request, existing evidence |
| **Control** | FATHER Constitution; product governance; source/provenance policy; project constraints |
| **Mechanism** | Business Owner, Product Manager, BA, PM, Knowledge Growth Analyst, Skeptical Reviewer |
| **Output** | BUSINESS_NEED, PRODUCT_VISION, SUCCESS_METRICS, STAKEHOLDER_REGISTER, SCOPE_BASELINE, ASSUMPTION_LOG, evidence register, gate decision |

## Evidence analytics

The stage is not considered complete because six files exist. Evidence quality is evaluated continuously.

```text
Statement
   ↓ classify
FACT / CLAIM / REQUIREMENT / CONSTRAINT / ASSUMPTION / PREFERENCE / HYPOTHESIS / UNKNOWN
   ↓
Source + owner + version/date
   ↓
Verification state
UNSUPPORTED / SOURCED / OWNER_CONFIRMED / CONFLICTED / REJECTED / STALE
   ↓
Affected artifact + downstream impact
   ↓
PRODUCT_READY decision
```

### Dashboard signals

| Indicator | Why it matters |
|---|---|
| Material claims total | denominator for evidence quality |
| Sourced / owner-confirmed ratio | shows how much product context has support |
| Unsupported claims | exposes invented or unverified assumptions |
| Open conflicts | prevents silent reconciliation |
| Material UNKNOWNs | shows uncertainty that may affect Security/System work |
| Artifacts with named owner | prevents orphan decisions |
| Gate blockers | shows exactly why Product cannot hand off yet |

**Important:** no numeric percentage automatically opens the gate. Metrics are diagnostic evidence, not a substitute for the decision table and professional review.

## Canonical outputs and ownership

| Artifact | Owner | Review | Next consumer |
|---|---|---|---|
| BUSINESS_NEED | Business Owner | Product Manager | Security, Requirements, System Engineering |
| PRODUCT_VISION | Product Manager | Business Owner | Security, System Engineering |
| SUCCESS_METRICS | Product Manager | Business Owner | Requirements, Validation |
| STAKEHOLDER_REGISTER | Project Manager | Product Manager | Security, System Engineering, Governance |
| SCOPE_BASELINE | Product Manager | Business Owner + PM | Security, System Engineering |
| ASSUMPTION_LOG | Project Manager | Skeptical Reviewer | all downstream roles |
| INITIATIVE_EVIDENCE_REGISTER | Product Manager / KGA governance | relevant information owners | gate + downstream evidence trace |
| PRODUCT_READY_DECISION | Product Manager | Business Owner + Skeptical Reviewer | Security Intake |

## Gate logic

`PRODUCT_READY` has four outcomes:

- `PASS` — all mandatory product context is sufficiently evidenced;
- `CONDITIONAL_PASS` — non-critical gaps remain but have explicit owners/conditions;
- `BLOCKED` — a hard blocker exists;
- `INSUFFICIENT_EVIDENCE` — evidence is not enough to determine readiness.

Hard blockers include missing decision authority, absent scope boundary, a technology request with no validated business problem, hidden material conflict, or UNKNOWN silently promoted to fact.

## Handoff to Security

Security receives the complete product package, not a verbal summary:

```text
BUSINESS_NEED
PRODUCT_VISION
SUCCESS_METRICS
STAKEHOLDER_REGISTER
SCOPE_BASELINE
ASSUMPTION_LOG
INITIATIVE_EVIDENCE_REGISTER
PRODUCT_READY_DECISION
        ↓
SECURITY_INTAKE
```

The next stage may begin only under the gate conditions in `PRODUCT_READY_DECISION_TABLE.yaml`.

## Machine-readable contracts

- `PRODUCT_DISCOVERY_PROCESS.yaml` — operations, roles, inputs/outputs and handoff;
- `PRODUCT_DISCOVERY_EVIDENCE_SCHEMA.yaml` — evidence records and analytics;
- `PRODUCT_READY_DECISION_TABLE.yaml` — DMN-like gate contract.
