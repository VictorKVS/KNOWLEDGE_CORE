# FATHER Professional Evidence Doctrine

Status: ACTIVE
Purpose: common evidence-first decision doctrine for every professional domain consumed by FATHER.

## Core principle
FATHER must not justify material professional decisions with phrases such as "this is common practice", "the architect preferred it", "the model thinks so", or "this is usually done" when the decision materially affects cost, safety, legality, reliability, quality, performance, maintainability, security or business outcome.

A professional recommendation is a governed derivation:

`CONTEXT → REQUIREMENTS → CONSTRAINTS → CRITERIA/METRICS → OPTIONS → EVIDENCE → ESTIMATES/CALCULATIONS → TRADE-OFF → DECISION → IMPLEMENTATION → VERIFICATION → OUTCOME → LESSON`

The decision must be explainable after the fact and reproducible from the evidence available at the time.

## Security is the first reference implementation
`SEC-PROD-0001 Security Knowledge Base` is the first mature evidence-first domain. Its source/locator/provenance discipline is the reference pattern, but the semantic layers differ by profession.

Examples of authoritative or useful evidence by domain include:
- law, regulation and regulator guidance;
- standards and normative methodologies;
- contracts and explicit business requirements;
- official vendor/product documentation and lifecycle/support data;
- engineering handbooks and accepted professional methodologies;
- peer-reviewed research and reproducible experiments;
- benchmark and measurement data;
- incident/failure/near-miss history;
- internal architecture decisions and measured operating history;
- cost/resource/availability data with freshness and provenance;
- code/project standards and toolchain-enforced conventions.

Secondary articles, community practice and model-generated explanations may support discovery or interpretation but do not silently become primary authority.

## Decision materiality
Evidence depth is proportional to consequence, irreversibility, uncertainty and cost of error.

### D0 — Local/conventional
Examples: local variable name, formatting choice, non-material refactor.
Evidence expectation: project coding standard, linter/formatter, local convention or explicit team rule. No external research is required unless the choice has wider consequences.

### D1 — Implementation
Examples: library/API use, data structure, retry policy in a bounded component, test technique.
Evidence expectation: official documentation, compatibility/version constraints, project standards, tests/benchmarks where material, known failure modes.

### D2 — Architecture/product
Examples: database choice, service boundary, consistency model, cloud topology, metric family, buy-vs-build, reliability-vs-latency trade-off.
Evidence expectation: explicit requirements and constraints, multiple viable options where available, measurable criteria, cost/resource estimate, risk/failure analysis, authoritative technical sources, assumptions, rejected-option rationale, verification plan.

### D3 — Regulated/safety/critical
Examples: legal compliance, security control selection, safety envelope, cryptography, industrial/medical/financial critical decisions.
Evidence expectation: admitted primary/normative sources with exact locators, applicability determination, calculations/measurements where relevant, independent qualified review, explicit residual risk and no silent override by convenience or cost.

A low-level choice is promoted to a higher materiality class when it can materially affect a higher-level property.

## Universal decision questions
Every material professional decision should be able to answer:
1. What problem or decision question was being solved?
2. Which business goals and acceptance criteria matter?
3. Which mandatory requirements apply and why?
4. Which constraints apply: law, budget, time, people, infrastructure, vendor support, interoperability, performance, safety, security, data, energy, supply chain, maintainability?
5. Which facts are verified and which are assumptions?
6. Which alternatives were considered?
7. Why were alternatives rejected?
8. Which metrics/criteria were used and why are those metrics appropriate?
9. What calculations, measurements, benchmarks or historical evidence support the comparison?
10. What trade-offs were accepted?
11. What uncertainty remains?
12. What would make this decision invalid or require review?
13. How will implementation be verified against the decision intent?
14. What happened after implementation and what lesson should return to the knowledge base?

## Professional examples
### Architect
A valid architecture decision is not "microservices are best practice". It derives candidate architectures from requirements and constraints, estimates cost/reliability/performance/operational burden, checks vendor and lifecycle constraints, exposes trade-offs, and records why one option dominates or why several remain viable.

### Analyst
A metric, label, threshold or segmentation must record what decision it supports, definition and unit, data lineage, assumptions, known bias/limitations, alternative metrics considered and why the selected metric is appropriate for the business/technical question.

### Software engineer
A material implementation decision should reference relevant language/platform/library contracts, project coding/architecture standards, compatibility/security/performance constraints and executable tests. A local naming decision may be justified by the project style guide rather than external literature; an algorithm or concurrency model requires stronger evidence.

### Reliability/operations engineer
Reliability, latency, recovery and availability targets must be tied to business impact, workload, failure model, dependency behavior, measured history and recovery capability rather than chosen as arbitrary round numbers.

### Finance/economics
Cost models must state source dates, units, uncertainty, scenario assumptions, capex/opex boundaries and sensitivity. A precise-looking number without provenance is not stronger evidence.

## Source hierarchy is domain-specific
Every domain must define its source taxonomy and precedence rules. There is no universal ordering that makes a vendor guide equivalent to a law, a benchmark equivalent to a contract, or a research paper equivalent to observed production behavior.

Conflicting sources are preserved and assessed; they are not silently averaged or overwritten.

## Requirement explosion and synthesis
A project may have hundreds or thousands of requirements. The system should not expose them to a decision maker as an unstructured list. It must support:
- atomic requirements;
- applicability;
- deduplication and relation mapping;
- hard constraints vs preferences;
- business priority;
- conflicts/tensions;
- grouped controls/capabilities;
- candidate solution generation;
- option elimination by hard gates;
- scored/quantitative comparison only where the scoring model is itself justified;
- human/independent review for material residual ambiguity.

The correct outcome may be one feasible option, several Pareto-valid alternatives, a request for missing evidence, or `NO-GO`.

## Anti-patterns
Forbidden as sole justification for material decisions:
- "best practice" without an identified source/context;
- "industry standard" without naming the standard or evidence;
- "everyone uses it";
- "the LLM recommended it";
- "the architect/programmer wanted it";
- vendor marketing treated as independent evidence;
- a weighted score whose weights have no rationale;
- a benchmark outside the relevant workload/context;
- precision beyond the quality of the underlying data;
- copying a prior decision without checking current applicability and freshness.

## Relationship to FATHER
Knowledge is not authority. Evidence supports a recommendation; the governed organization decides within its authority model.

FATHER should eventually consume a `PROFESSIONAL_DECISION_RECORD` for material choices so that RUN/trace/replay can preserve not only which knowledge objects were used, but also the derivation from requirements and alternatives to the chosen decision.

## Long-term objective
Every professional role becomes an evidence-backed expert system with a domain-specific corpus and a shared decision semantics. Security is first; software engineering, architecture, analysis, DevOps/SRE, AI/ML, data, networking, finance, legal, construction, electrical, safety, physical security, healthcare, research and future manufacturing domains follow the same principle without copying Security-specific semantics blindly.
