# FATHER Paper Pipeline

Status: `PRIMARY DESIGN WORKSTREAM / AUTOMATION FEATURE DEVELOPMENT FROZEN`

This directory is the current canonical workbench for defining the complete FATHER engineering lifecycle **before** expanding LLM/Model Zoo automation.

## Read in this order

1. `FATHER_PAPER_PIPELINE_ALGORITHM.md` — human-readable end-to-end A0–A16 algorithm.
2. `ANALYSIS_FIRST_ENGINEERING_POLICY.md` — code-last policy: documentation, analysis, security, design and test intent precede material implementation.
3. `PRE_CODE_EVIDENCE_GATE.yaml` — explicit evidence gate that decides whether product-path code is allowed at all.
4. `ALGORITHM_DESIGN_STANDARD.md` — mandatory scientific/senior standard for designing every material algorithm: simplest-sufficient baseline, invariants, correctness/adequacy, complexity, failure modes, experiments and references.
5. `ALGORITHM_REVIEW_SCHEMA.yaml` — machine-readable minimum evidence for accepting an algorithm into the paper pipeline.
6. `ROLE_COMPETENCY_MATURITY_MODEL.yaml` — evidence-earned maturity levels for future role-specific AI assistants/agents.
7. `ROLE_TRAINING_CERTIFICATION_FACTORY.yaml` — source→KB→training→hidden eval→security red-team→independent review→runtime telemetry→recertification pipeline for each professional role.
8. `PROCESSING_METHOD_CATALOG.yaml` — algorithms/methods, inputs/outputs and future automation class.
9. `ARTIFACT_DEPENDENCY_MATRIX.yaml` — which data/artifacts feed each material artifact and what consumes it next.
10. `GATE_AUTHORITY_MATRIX.yaml` — minimum gate evidence and authorized final decision roles.
11. `EXCEPTION_REWORK_MODEL.yaml` — where the process returns when evidence, assumptions, tests or decisions fail.
12. `OTUS_01_31_CROSSWALK.yaml` — all 31 OTUS lessons mapped to real FATHER lifecycle stages.
13. `SOURCE_COVERAGE_STATUS.md` — what is verified in standards/books and what remains a coverage gap.
14. `PAPER_PIPELINE_REVIEW_CHECKLIST.md` — acceptance checklist and mandatory walkthrough scenarios.
15. `AUTOMATION_ACTIVATION_GATE.yaml` — explicit conditions for resuming runtime/Model Zoo expansion.

## Canonical distinction

```text
FATHER lifecycle = engineering execution order
OTUS 1–31        = method/capability curriculum
GOST/FSTEC/etc   = normative/standards layer by applicability
Books            = professional method layer after source verification
Scientific refs  = evidence/method layer, not authority replacement
Model Zoo         = future analysis/review mechanism, never the lifecycle itself
```

## Analysis-first / code-last rule

The process treats the majority of material engineering work as **pre-implementation reasoning**. The informal `~89% paper/analysis` statement is a design heuristic, not a universal measured statistic.

Preferred order:

```text
Documents / sources
→ Product analysis
→ Business analysis
→ System analysis
→ Security / Legal / Data analysis
→ Threat model
→ Requirements / NFR / acceptance
→ Architecture + full diagrams/contracts/descriptions
→ Test strategy + precise test cases/oracles
→ PRE-CODE EVIDENCE GATE
→ Implementation plan
→ CODE
→ Execute tests
→ Release / operate / learn
```

Material product-path code is not authorized until `PRE_CODE_EVIDENCE_GATE.yaml` returns `CODE_ALLOWED` or an explicitly bounded `CODE_ALLOWED_WITH_CONDITIONS` outcome through the required human authority.

Exploratory PoC/spike code is permitted only as isolated evidence-producing work; it must not silently become the implementation baseline.

## Senior-role rule

A future AI role is not considered senior/expert because of its prompt or model brand. Competence is **earned per role/task/domain** through verified sources, versioned knowledge, training/counterexample cases, hidden evals, security/adversarial suites, human-review telemetry, independent review and periodic recertification.

The target pattern is:

```text
Role contract
→ verified source map
→ versioned role KB
→ methods / decision logic
→ training cases
→ counterexamples / failure cases
→ independent eval + hidden eval
→ security/red-team suite
→ independent domain review
→ bounded runtime authority
→ telemetry / human review / incidents
→ retraining + recertification or demotion
```

No broad "senior model" status exists. Promotion is always bounded to a specific role + capability + domain, and is reversible.

## Security of the role-agents

Future senior-role agents must continuously prove both professional quality and safe behavior. Recertification is triggered by model/provider changes, prompt/tool changes, new data classes, major KB updates, new privileged tools, material incidents, drift or repeated human rejection.

Mandatory adversarial coverage includes prompt/retrieval injection, poisoned evidence, fabricated citations, authority escalation, confused-deputy behavior, tool misuse, sensitive-data routing, hidden scope expansion, unsafe autonomous approval, KB/memory poisoning, jailbreak attempts and cross-agent privilege propagation.

## Simplicity rule

The pipeline itself must remain as simple as possible. Complexity is allowed only when a simpler method cannot meet a measurable requirement or control a material risk.

```text
L0 deterministic rule
→ L1 deterministic algorithm/calculator
→ L2 statistical/bounded heuristic
→ L3 single-model assisted
→ L4 champion + verifier
→ L5 Model Zoo / multi-agent
```

Escalation upward requires evidence. A more sophisticated algorithm is not automatically a better algorithm.

## Current target

Before automation resumes, the paper pipeline must answer for every material stage:

```text
What triggers the stage?
What data must already exist?
Who owns that data?
What canonical artifacts are expected?
How are they produced or reconstructed?
Which methods are used?
Why is the selected method simpler/better than the alternatives?
What are its assumptions and invariants?
How is correctness or adequacy argued?
What are its complexity and failure modes?
How will it be falsified/tested?
Which normative/professional/scientific sources support it?
Which conflicts/UNKNOWNs are allowed?
Who reviews and who has final authority?
What evidence closes the gate?
What exact information is handed downstream?
Where does rework return?
```

## Automation policy

The existing runtime MVP is preserved and CI-tested. It is **not** authorized to expand lifecycle semantics or final authority while `AUTOMATION_ACTIVATION_GATE.yaml` is frozen.

Paper first → algorithm review → role competence review → walkthrough → review → only then automation mapping.
