# SUCCESS METRICS — FATHER Analytical Design Platform

Status: `CANDIDATE / BASELINE_REQUIRED`

Accountable owner: `product_manager`

Review: `business_owner`

The metrics below define what Product wants to observe. They do not yet replace validated targets or SLOs.

| ID | Metric | Product intent | Current target state |
|---|---|---|---|
| SM-01 | lifecycle traceability | material decision traces to inputs, evidence, owner, artifact and review | TO_BE_BASELINED |
| SM-02 | gate explainability | every material gate has machine-readable reasons/evidence refs | 100% material gates |
| SM-03 | artifact gap visibility | missing/partial/conflicted/stale required information is visible before downstream decision | TO_BE_BASELINED |
| SM-04 | silent state collapse | FACT/CLAIM/ASSUMPTION/HYPOTHESIS/UNKNOWN are not silently collapsed | zero known violations in eval suite |
| SM-05 | visual drill-down coverage | user navigates L0 -> L1 -> L2 -> L3 where implemented | all factory stages |
| SM-06 | duplicate-document avoidance | existing evidence is mapped/reused before creating new artifact | TO_BE_BASELINED |
| SM-07 | requirement-to-verification trace | requirement can later trace to design/control/test/result | TO_BE_BASELINED |
| SM-08 | unsupported material claim visibility | unsupported material claims are visible and block/condition decisions when applicable | 100% detected material claims |
| SM-09 | conflict preservation | conflicting evidence remains explicitly conflicted until resolved | zero silent conflict resolution |
| SM-10 | role authority trace | material approval/risk acceptance identifies accountable authority | 100% material approvals |

## Baseline plan

Quantitative targets are to be baselined after:

1. one end-to-end FATHER self-pilot;
2. one real iterative software project;
3. one brownfield project with pre-existing documentation.

Until then, numbers not supported by telemetry remain `TO_BE_BASELINED`.
