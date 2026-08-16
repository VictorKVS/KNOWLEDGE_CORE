# Evidence-Driven Knowledge Base Construction Methodology (EDKBCM)

**Document ID:** KBRE-METHOD-0001  
**Version:** 1.1  
**Status:** RESEARCH_BASELINE / LIVING_METHOD  
**Flagships:** Security / Programmer / Architecture  
**Purpose:** define a reusable, measurable and continuously improving method for constructing evidence-driven knowledge bases across domains while increasing construction speed and reuse without reducing quality, provenance or auditability, and while minimizing total cost.

## 1. Governing objective

Optimize simultaneously: quality, speed, cost and reuse. Faster but less trustworthy is a failed experiment. The primary optimization metric is `verified_reusable_knowledge_units / (human_hours + machine_cost)` subject to mandatory proof, regression and red-team gates.

## 2. Scientific and engineering foundations

This methodology is a synthesis and does not claim invention of the underlying disciplines.

- Knowledge Graph / Ontology Engineering: typed entities, relations, stable identifiers, ontologies and graph reasoning.
- W3C PROV-O: provenance entities, activities, agents and derivation. Source: https://www.w3.org/TR/prov-o/
- W3C SHACL: declarative graph constraints and validation reports. Source: https://www.w3.org/TR/shacl/
- FAIR principles: Findable, Accessible, Interoperable, Reusable knowledge and workflows. Source: Wilkinson et al., Scientific Data 3, 160018 (2016), https://doi.org/10.1038/sdata.2016.18
- Rules as Code: machine-consumable rules alongside human prose. Source: OECD, Mohun & Roberts, Cracking the code (2020), https://www.oecd.org/en/publications/cracking-the-code_3afe6ba5-en.html
- Akoma Ntoso / LegalDocumentML: structured legislative and judicial documents. Source: https://www.oasis-open.org/standard/akn-v1-0/
- LegalRuleML: formal legal rule representation; candidate for benchmarked adoption rather than automatic complexity.
- Software engineering / CI/CD: deterministic regression, release gates, change-impact analysis.
- Measurement science / continuous improvement: every build pass is an experiment with recorded input, method, output, defects, cost and result.

## 3. Canonical construction pipeline

`SCOPE → SOURCE INVENTORY → ACQUISITION → PROVENANCE → STRUCTURE → ATOMIZATION → ONTOLOGY BINDING → APPLICABILITY → TEMPORAL ROUTING → DECISION LOGIC → ROLE/ACTION/DEADLINE → EVIDENCE OF EXECUTION → CONSEQUENCE → REGRESSION → RED TEAM → RELEASE → TELEMETRY → METHOD IMPROVEMENT`

Every stage has fail-closed states. Missing evidence remains UNKNOWN/PENDING/NOT_PROVEN rather than being filled by plausible invention.

## 4. MVP-first maturity

M0 Scope → M1 Registered sources → M2 Evidence-bearing atomic knowledge → M3 Executable applicability → M4 Operational compilation → M5 Regression-safe system → M6 Expert-ready domain MVP → M7 Portable factory asset.

## 5. Mandatory evidence states

At minimum: PRIMARY_IMMUTABLE, PRIMARY_DYNAMIC_SNAPSHOT, PRIMARY_WEB_VERIFIED, AUTHORITATIVE_SECONDARY, DISCOVERY_ONLY, PENDING, CONFLICT, NOT_PROVEN, NOT_APPLICABLE, SUPERSEDED, REJECTED. Truth status and provenance tier remain separate.

## 6. Mandatory telemetry

Count exactly from repositories, never from memory: sources by state/tier; claims; requirements; applicability and temporal rules; roles; deadlines; evidence nodes; consequences; relations; VERIFIED/PENDING/conflicts; red-team findings; regression and CI pass rates; human/machine time; review/rework; cost; reuse; coverage; freshness; provenance closure.

Core efficiency metrics include `verified_records_per_hour`, `review_minutes_per_verified_record`, `cost_per_verified_record`, `cost_per_closed_decision_path`, `rework_ratio`, `provenance_acquisition_success_rate`, `reuse_ratio`, `schema_change_rate`, `defect_escape_rate` and `time_to_proof_floor`.

## 7. Quality-adjusted optimization

A method version is promoted only if it introduces no unresolved Critical/High defect, does not weaken provenance or regression gates, does not materially reduce decision/applicability coverage, and measurably improves at least one of speed, cost, review load, rework, acquisition success or reuse. Results should be reproducible in repeated passes or another flagship/domain.

## 8. Method experiments

Benchmark source-first, inventory-first, ontology-first, clause-first, graph-first, schema-guided extraction, retrieval-assisted atomization, validator-first, red-team-first and hybrid pipelines. Record method version, slice complexity, time, machine cost, output, provenance tier, defects, rework and regression result.

## 9. Golden assets

Repeatedly successful source-acquisition recipes, authority rules, ontology fragments, extraction schemas, provenance templates, applicability/temporal patterns, evidence contracts, validators, regression fixtures, red-team checklists, document templates and clone playbooks become versioned Golden Assets with tested domains, benchmark result and deprecation rule.

## 10. Three-flagship research system

The factory must not learn universal rules from Security alone. The first validation triangle is intentionally heterogeneous.

### Flagship F01 — Security
Research chain: `SOURCE → CLAIM → REQUIREMENT → APPLICABILITY → THREAT/RISK → CONTROL → ROLE → DEADLINE → EVIDENCE → LIABILITY/CONSEQUENCE → CASE → FEEDBACK`.

Primary research questions: provenance, normative authority, temporal routing, applicability, evidence closure, legal consequences, dynamic registers, auditability and fail-closed decisions.

### Flagship F02 — Programmer
Research chain: `SOURCE/BOOK/DOC → KNOWLEDGE CLAIM → PATTERN → TASK → IMPLEMENTATION → TEST → BENCHMARK → DEFECT → FIX → LESSON → GOLDEN SOLUTION`.

Required measurements include task throughput, first-pass test rate, defect density, rework, benchmark delta, solution reuse, human correction, time/cost to demonstrated skill, and transfer of learned patterns to new tasks. Each educational implementation should preserve why a solution was selected, alternatives considered, tests, failures and measured result when the learning mode is enabled.

### Flagship F03 — Architecture
Research chain: `REQUIREMENT → CONSTRAINT → NFR → OPTIONS → TRADE-OFF → ADR → ARCHITECTURE → THREAT/RISK → COST → TEST/REVIEW → OPERATIONAL OUTCOME → LESSON`.

Required measurements include time-to-decision, ADR reversal rate, decision reuse, architecture defect escape, NFR satisfaction, predicted-versus-actual cost, change impact, implementation friction and operational outcome.

### Cross-flagship feedback loop

`ARCHITECT DECISION → PROGRAMMER IMPLEMENTATION → SECURITY REVIEW → TEST/OPERATION OUTCOME → KBRE TELEMETRY → PATTERN WEIGHT UPDATE → NEXT DECISION`.

A pattern must preserve context, applicability and outcome; raw popularity is never proof of quality.

## 11. Method promotion ladder

A useful method discovered in one flagship becomes `CANDIDATE`. After successful independent use in two materially different flagships it becomes `CROSS_DOMAIN_CANDIDATE`. After successful validation across all three initial flagships, without degradation of quality gates, it may become `GOLDEN_CORE_METHOD`. Promotion requires recorded metrics and method version; intuition is insufficient.

A method may remain `DOMAIN_GOLDEN` when excellent in one domain but not portable. This prevents Security-specific, coding-specific or architecture-specific practices from being misclassified as universal.

## 12. Pattern outcome statistics and weights

Reusable patterns receive immutable IDs such as `PAT-SEC-*`, `PAT-DEV-*`, `PAT-ARCH-*`. For every use record context, selected alternative, success/failure, defects, rework, human intervention, cost, performance/NFR/security outcomes and evidence quality.

Weights are derived from evidence, not manually declared prestige. Any score must expose sample size, domains, recency, uncertainty and metric definition. A pattern with 2 successes must not outrank a mature pattern merely because its raw success rate is 100%.

Research future calibration using confidence intervals/Bayesian or other statistically justified models; do not present an uncalibrated scalar as truth.

## 13. Cost-minimization strategy

Avoid rediscovery; validate deterministically before expert review; route humans to ambiguous/high-impact cases; cache immutable sources and parsed structures; rebuild incrementally; reuse stable schemas/validators; measure rework; benchmark model/tool tiers by task complexity; preserve failed acquisition and negative findings; never optimize token/compute cost by silently lowering proof quality.

## 14. Research-to-method binding contract

Every research result from Security, Programmer, Architecture or later flagships must be classified as `OBSERVATION`, `HYPOTHESIS`, `EXPERIMENT`, `RESULT`, `CANDIDATE_METHOD`, `GOLDEN_ASSET`, `ANTI_PATTERN` or `REJECTED_METHOD`.

Every promoted methodology change must reference the experiments/results that justified it. Every experiment must record the methodology version it tested. This creates a bidirectional trace:

`METHOD VERSION ↔ EXPERIMENTS ↔ FLAGSHIP RUNS ↔ METRICS ↔ DECISION TO PROMOTE/REJECT`.

Research must not disappear into chat, prose reports or undocumented implementation choices.

## 15. Benchmark report per flagship

Each flagship publishes frozen scope, exact source/input counts, exact node/relation/output counts, quality/coverage, human and machine effort, total/unit costs, defects/rework, reused versus new assets, method versions tested, A/B results, red-team findings, operational outcomes and lessons transferred to EDKBCM.

## 16. Research questions

Study source ordering; ontology-first versus source-first; automation limits; mandatory human-review tiers; validator portability; optimal claim granularity; confidence/freshness/corroboration calibration; RDF/OWL/SHACL versus YAML/property graphs; LegalRuleML cost-benefit; acquisition/cache strategy; domain complexity versus review load; cost learning curve from flagship 1 to N; whether programmer and architect evidence structures generalize to engineering/scientific domains; and which cross-flagship patterns predict real operational success.

## 17. Change policy

This is a living research method. PATCH = clarification; MINOR = compatible metric/stage/validator/process improvement; MAJOR = changed proof-floor, ontology/evidence semantics or lifecycle. Historical benchmarks retain the method version used and are never silently recalculated.

## 18. Current success criterion

The goal is not maximum document count. It is **faster + cheaper + equally or more trustworthy + reproducible + portable knowledge construction**.

The factory is learning only when later flagship runs demonstrate measurable reduction in quality-adjusted time/cost while retaining or improving proof, coverage, regression and red-team results.
