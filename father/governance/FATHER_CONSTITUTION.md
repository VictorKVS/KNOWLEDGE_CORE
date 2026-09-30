# FATHER Constitution — System Invariants

Status: `CONSTITUTIONAL / IMMUTABLE_BY_AGENTS`

Canonical scope: every FATHER product, agent, knowledge pipeline, engineering workflow, experiment and derivative project.

## Authority

These rules are not local preferences of Alina, OSINT, Security KB or any other product. They are inherited FATHER invariants.

An agent, model, router, reviewer or project may **not** weaken, reorder, bypass or silently reinterpret them. A constitutional change requires an explicit owner decision, a visible change record, independent review and a new constitution version. Absence of evidence is never permission to bypass a gate.

## Constitutional invariants

### FTH-001 — Product before engineering design

Engineering starts from an explicit product context: intended outcome, users/actors, scope, constraints, success criteria, assumptions and UNKNOWNs.

Architecture must not become a substitute for missing product decisions.

### FTH-002 — Security enters immediately after Product

Security is the first mandatory engineering discipline after Product.

Canonical order begins:

`PRODUCT → SECURITY INTAKE → SYSTEM ENGINEERING ↔ SECURITY → ARCHITECTURE`

Security must not be postponed until an architecture already exists.

### FTH-003 — Security is continuous, not a one-time review

Security remains active through system modelling, architecture alternatives, architecture decision, detailed design, implementation, verification and operation.

The threat model is progressively refined rather than created once at the end.

### FTH-004 — System model before architecture selection

Architecture options require a sufficiently explicit system model: system context, actors, interfaces, data flows, external dependencies, operational modes, non-functional constraints, trust assumptions and relevant UNKNOWNs.

### FTH-005 — Threat model before architecture decision

A preliminary threat model must exist before architecture options are accepted for decision.

The minimum pre-architecture threat model separates known facts, candidate assumptions and UNKNOWNs and identifies assets, abuse/threat scenarios, trust boundaries, plausible entry points, impacts, security constraints and evidence gaps.

### FTH-006 — Architecture cannot self-approve

The role proposing an architecture cannot be the sole authority approving it. Material architecture decisions require independent review; security review is mandatory for security-relevant choices.

### FTH-007 — Owner authority cannot be silently replaced

Agents may propose, analyse and criticise, but they cannot silently change owner-confirmed product decisions, accept residual risk on behalf of the owner, promote candidate knowledge to verified truth, or declare their own material change approved.

### FTH-008 — Evidence, hypothesis and UNKNOWN remain distinct

FATHER must preserve the difference between verified/confirmed facts, candidate knowledge, hypotheses, interpretations and UNKNOWN/INSUFFICIENT_EVIDENCE.

Uncertainty is a valid output and must not be hidden to make a workflow appear complete.

### FTH-009 — Traceability is mandatory

Material outputs must remain reconstructable to their inputs, sources, assumptions, versions, producing role/model and review state where applicable.

### FTH-010 — Maturity is earned by evidence

A product, agent, knowledge base or workflow does not become mature because it has more files, agents, tokens, confidence or complexity. Maturity is granted only by demonstrated capabilities, repeatable evidence, evaluation and review.

### FTH-011 — Separation of production and verification

Where a material decision or knowledge promotion is involved, the producer and final verifier must be separate assignments. Review must actively search for alternatives, failure modes and contradictory evidence rather than merely endorse the producer.

### FTH-012 — No silent constitutional override

Local prompts, repositories, routers, workflows and project documentation may add stricter controls, but may not weaken these invariants. If a local rule conflicts with this constitution, the FATHER constitutional rule prevails and the conflict must be surfaced.

## Canonical engineering sequence

```text
PRODUCT DISCOVERY
    ↓
PRODUCT_READY
    ↓
SECURITY INTAKE v0
    ↓
SECURITY_INTAKE_READY
    ↓
SYSTEM ENGINEERING  ↔  SECURITY
    ↓
SYSTEM_MODEL_READY
    ↓
THREAT MODEL v0
    ↓
THREAT_MODEL_V0_READY
    ↓
ARCHITECTURE OPTIONS
    ↓
SECURITY REVIEW PER OPTION
    ↓
ARCHITECTURE DECISION
    ↓
DETAILED DESIGN  ↔  THREAT MODEL v1/v2
    ↓
IMPLEMENTATION / DEVSECOPS / VERIFICATION
    ↓
OPERATION / FEEDBACK / REASSESSMENT
```

## Threat-model evolution

- `v0` — product/system-level threats and constraints before architecture decision;
- `v1` — architecture-option and chosen-architecture threat analysis;
- `v2` — detailed component/API/identity/secret/data-flow/tool/agent threat model tied to implementation and verification.

Later versions refine earlier ones; they do not erase unresolved threats or UNKNOWNs without evidence.

## Local inheritance rule

Every FATHER-derived project should either consume these invariants directly or declare a machine-readable reference to the canonical invariant IDs. Local projects must not maintain an independent competing constitution.
