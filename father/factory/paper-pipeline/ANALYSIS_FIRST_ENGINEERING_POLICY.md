# FATHER — Analysis-First Engineering Policy

Status: `CANDIDATE / GOVERNING ENGINEERING PRINCIPLE`

## 1. Core rule

FATHER treats software/system engineering as an **analysis-first, code-last** discipline.

The statement that "roughly 89% of the work is analytical/paper work" is recorded as a **design heuristic**, not as a measured universal statistic. Its practical meaning is:

> A material implementation should begin only after the problem, requirements, system model, security model, architecture, detailed design, test intent and acceptance evidence are sufficiently defined to make coding a bounded execution task rather than exploratory guessing.

## 2. Required order

```text
Source / Business Need
→ Product documents
→ Business analysis
→ System analysis
→ Security / Legal / Data analysis
→ Threat model
→ Requirements / NFR / acceptance baseline
→ Feasibility / estimate / risk / TCO / PoC evidence
→ Architecture options / trade-offs / decision
→ Detailed design / interfaces / data / deployment / observability
→ Test strategy + test specifications + acceptance/security/performance/AI-quality cases
→ Implementation plan
→ Code / configuration / IaC / model assets
→ Test execution
→ Release / operation / feedback
```

The process is iterative, but iteration does not authorize skipping upstream reasoning. If implementation exposes a wrong assumption, the smallest affected upstream stage is reopened.

## 3. Code-entry gate

`CODE_ALLOWED` requires, where applicable:

- approved or explicitly bounded product scope;
- system boundary and responsibilities;
- classified data and applicable regulatory constraints;
- threat model and security requirements;
- functional and non-functional requirements;
- acceptance criteria;
- chosen architecture and material ADRs;
- component/interface/data contracts;
- deployment, IAM, secrets and observability intent;
- test strategy;
- executable or otherwise precise test descriptions for critical requirements;
- traceability from requirement/risk to control/test;
- named owner for unresolved residual risk/UNKNOWN;
- implementation rollback/disable strategy for material changes.

`No CODE_ALLOWED → no product-path implementation.`

## 4. Tests are designed before implementation

For material behavior, tests are not written only after code appears.

Preferred chain:

```text
Requirement / Risk
→ Observable acceptance condition
→ Test oracle / expected outcome
→ Test case / security case / performance case / AI eval case
→ Implementation
→ Execution evidence
```

The test package may include:

- unit-test contracts;
- integration scenarios;
- system scenarios;
- API/schema tests;
- security negative tests;
- SAST/SCA/secret-scan expectations;
- DAST/pentest scenarios;
- performance/load/capacity scenarios;
- failure/recovery/rollback tests;
- GenAI/RAG golden-set and adversarial cases;
- acceptance scenarios;
- data quality/lineage checks.

A test is valid only if it proves or falsifies a requirement/assumption/control. Passing existing code is not by itself evidence that the correct requirement was tested.

## 5. Documentation is executable reasoning

A document is not valuable because it exists. It is valuable when it captures one of:

- authoritative input;
- explicit decision;
- contract;
- model;
- risk/threat;
- test oracle;
- evidence;
- traceability;
- operation/feedback.

Therefore FATHER minimizes decorative documentation and maximizes **decision-bearing information artifacts**.

## 6. Senior-role principle

Every material stage is performed by a role-specific expert profile, not by a generic assistant.

Examples:

- Product / Business Owner;
- Business Analyst;
- System Engineer;
- Security Engineer;
- Requirements Engineer;
- Solution Architect;
- Data/Integration Architect;
- QA / Verification Engineer;
- DevSecOps Engineer;
- Operations/SRE;
- Risk Owner;
- Legal/Compliance;
- Skeptical Reviewer.

For future AI-assisted execution, each role profile must have its own competence model, source corpus, methods, evals and authority boundary.

## 7. Capability is earned, not declared

A role-agent is never called "senior" merely because a prompt says so.

Maturity must be supported by evidence such as:

- versioned professional knowledge base;
- verified normative source coverage;
- solved training cases;
- negative/counterexample cases;
- benchmark/evaluation results;
- security/adversarial tests;
- human-review acceptance/rejection statistics;
- error taxonomy;
- rework rate;
- calibration records;
- independent review;
- evidence traceability.

No measurable competence evidence → no claim of senior capability.

## 8. Continuous training and evaluation

Role competence is maintained through a loop:

```text
new source / standard / book / incident / defect
→ source verification
→ atomic knowledge extraction
→ conflict/supersession analysis
→ role KB update candidate
→ training cases
→ eval / red-team cases
→ independent review
→ promotion
→ runtime telemetry
→ failures/rework
→ new training cases
```

The purpose is not to maximize model complexity. It is to improve reliability of role decisions.

## 9. Security testing is continuous

Security testing applies both to the engineered system and to future AI role-agents.

Agent/model security evaluation should cover, where applicable:

- prompt/retrieval injection;
- poisoned evidence;
- authority escalation;
- confused-deputy behavior;
- tool misuse;
- sensitive-data routing;
- fabricated sources/citations;
- hidden scope expansion;
- unsafe autonomous approval;
- memory/knowledge poisoning;
- jailbreak/adversarial instruction following;
- refusal/fail-closed correctness;
- cross-agent privilege propagation.

A model that performs well on ordinary cases but fails authority/security cases is not production-ready for that role.

## 10. Simplicity remains mandatory

Deep analysis does not justify process bloat.

Preferred order:

```text
simple deterministic rule
→ deterministic algorithm/calculator
→ statistical or bounded heuristic
→ single specialist model
→ champion + verifier
→ Model Zoo
```

Escalate only when the simpler level fails a stated requirement, risk threshold or measured quality target.

## 11. Scientific discipline

Every material algorithm/decision must state:

1. problem;
2. inputs and provenance;
3. assumptions;
4. outputs;
5. invariants/constraints;
6. simplest baseline;
7. alternatives;
8. evaluation criteria set before comparison;
9. evidence and references;
10. correctness/adequacy argument;
11. uncertainty and limitations;
12. failure modes;
13. falsification tests;
14. security implications;
15. revisit triggers.

This policy is implemented together with `ALGORITHM_DESIGN_STANDARD.md` and the A0–A16 paper pipeline.
