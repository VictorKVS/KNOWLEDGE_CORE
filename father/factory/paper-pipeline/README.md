# FATHER Paper Pipeline

Status: `PRIMARY DESIGN WORKSTREAM / AUTOMATION FEATURE DEVELOPMENT FROZEN`

This directory is the current canonical workbench for defining the complete FATHER engineering lifecycle **before** expanding LLM/Model Zoo automation.

## Read in this order

1. `FATHER_PAPER_PIPELINE_ALGORITHM.md` — human-readable end-to-end A0–A16 algorithm.
2. `PROCESSING_METHOD_CATALOG.yaml` — algorithms/methods, inputs/outputs and future automation class.
3. `ARTIFACT_DEPENDENCY_MATRIX.yaml` — which data/artifacts feed each material artifact and what consumes it next.
4. `OTUS_01_31_CROSSWALK.yaml` — all 31 OTUS lessons mapped to real FATHER lifecycle stages.
5. `SOURCE_COVERAGE_STATUS.md` — what is verified in standards/books and what remains a coverage gap.
6. `PAPER_PIPELINE_REVIEW_CHECKLIST.md` — acceptance checklist and mandatory walkthrough scenarios.
7. `AUTOMATION_ACTIVATION_GATE.yaml` — explicit conditions for resuming runtime/Model Zoo expansion.

## Canonical distinction

```text
FATHER lifecycle = engineering execution order
OTUS 1–31        = method/capability curriculum
GOST/FSTEC/etc   = normative/standards layer by applicability
Books            = professional method layer after source verification
Model Zoo         = future analysis/review mechanism, never the lifecycle itself
```

## Current target

Before automation resumes, the paper pipeline must answer for every material stage:

```text
What triggers the stage?
What data must already exist?
Who owns that data?
What canonical artifacts are expected?
How are they produced or reconstructed?
Which methods are used?
Which normative/professional sources support those methods?
Which conflicts/UNKNOWNs are allowed?
Who reviews and who has final authority?
What evidence closes the gate?
What exact information is handed downstream?
Where does rework return?
```

## Automation policy

The existing runtime MVP is preserved and CI-tested. It is **not** authorized to expand lifecycle semantics or final authority while `AUTOMATION_ACTIVATION_GATE.yaml` is frozen.

Paper first → walkthrough → review → only then automation mapping.
