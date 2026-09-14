# FATHER Paper Pipeline

Status: `PRIMARY DESIGN WORKSTREAM / AUTOMATION FEATURE DEVELOPMENT FROZEN`

This directory is the current canonical workbench for defining the complete FATHER engineering lifecycle **before** expanding LLM/Model Zoo automation.

## Read in this order

1. `FATHER_PAPER_PIPELINE_ALGORITHM.md` — human-readable end-to-end A0–A16 algorithm.
2. `ALGORITHM_DESIGN_STANDARD.md` — mandatory scientific/senior standard for designing every material algorithm: simplest-sufficient baseline, invariants, correctness/adequacy, complexity, failure modes, experiments and references.
3. `ALGORITHM_REVIEW_SCHEMA.yaml` — machine-readable minimum evidence for accepting an algorithm into the paper pipeline.
4. `PROCESSING_METHOD_CATALOG.yaml` — algorithms/methods, inputs/outputs and future automation class.
5. `ARTIFACT_DEPENDENCY_MATRIX.yaml` — which data/artifacts feed each material artifact and what consumes it next.
6. `GATE_AUTHORITY_MATRIX.yaml` — minimum gate evidence and authorized final decision roles.
7. `EXCEPTION_REWORK_MODEL.yaml` — where the process returns when evidence, assumptions, tests or decisions fail.
8. `OTUS_01_31_CROSSWALK.yaml` — all 31 OTUS lessons mapped to real FATHER lifecycle stages.
9. `SOURCE_COVERAGE_STATUS.md` — what is verified in standards/books and what remains a coverage gap.
10. `PAPER_PIPELINE_REVIEW_CHECKLIST.md` — acceptance checklist and mandatory walkthrough scenarios.
11. `AUTOMATION_ACTIVATION_GATE.yaml` — explicit conditions for resuming runtime/Model Zoo expansion.

## Canonical distinction

```text
FATHER lifecycle = engineering execution order
OTUS 1–31        = method/capability curriculum
GOST/FSTEC/etc   = normative/standards layer by applicability
Books            = professional method layer after source verification
Scientific refs  = evidence/method layer, not authority replacement
Model Zoo         = future analysis/review mechanism, never the lifecycle itself
```

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

Paper first → algorithm review → walkthrough → review → only then automation mapping.
