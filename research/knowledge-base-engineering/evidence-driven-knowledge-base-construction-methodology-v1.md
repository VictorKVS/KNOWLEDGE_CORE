# Evidence-Driven Knowledge Base Construction Methodology (EDKBCM)

**Document ID:** KBRE-METHOD-0001  
**Version:** 1.0  
**Status:** RESEARCH_BASELINE / LIVING_METHOD  
**Flagship domain:** Russian Security Knowledge Core  
**Purpose:** define a reusable, measurable and continuously improving method for constructing evidence-driven knowledge bases across domains while increasing construction speed and reuse without reducing quality, provenance or auditability, and while minimizing total cost.

## 1. Governing objective

The method optimizes three objectives simultaneously:

1. **Quality must not decrease.** No speed or cost improvement is accepted if provenance quality, correctness, applicability coverage, temporal correctness, regression coverage, evidence closure or red-team performance deteriorates beyond an explicitly approved tolerance.
2. **Construction speed should increase.** Each flagship domain must produce empirical lessons, reusable schemas, acquisition recipes, extraction patterns, validators and workflows that reduce time-to-proof-floor for later domains.
3. **Total cost should decrease.** Human review, source acquisition, extraction, modeling, rework and compute/tool costs must be measured so the factory can optimize cost per verified reusable knowledge unit rather than merely document count.

Primary optimization metric:

`verified_reusable_knowledge_units / (human_hours + machine_cost)`

subject to mandatory quality gates.

## 2. Scientific and engineering foundations

This methodology is a synthesis. It does not claim invention of the underlying disciplines.

### 2.1 Knowledge graph and ontology engineering
Use typed entities, relations, stable identifiers and domain ontologies rather than isolated documents or flat checklists. Domain extensions must not silently redefine universal concepts.

### 2.2 W3C PROV-O — provenance
Adopt the provenance principle that knowledge should retain traceable relations between entities, activities and agents. In this methodology every important claim should be traceable to acquisition, extraction, transformation and review events.

Source: W3C Recommendation, **PROV-O: The PROV Ontology** — https://www.w3.org/TR/prov-o/

Adopted concepts: provenance graph, derivation, activity, agent, source lineage.  
Local extension: immutable artifact hashes, reviewer state, acquisition failures, legal/version applicability and claim-level proof binding.

### 2.3 W3C SHACL — graph validation
Use declarative constraints where appropriate to validate graph structure and required evidence. A VERIFIED node should fail validation when mandatory provenance, applicability, temporal or evidence properties are missing.

Source: W3C Recommendation, **Shapes Constraint Language (SHACL)** — https://www.w3.org/TR/shacl/

Adopted concepts: shapes graph, validation, conformance report.  
Local extension: CI quality gates, fail-closed decision validation, domain regression fixtures and release blocking.

### 2.4 FAIR principles
Knowledge assets, workflows and research artifacts should become increasingly Findable, Accessible under appropriate permissions, Interoperable and Reusable. Reusability applies not only to final data but to algorithms, tools and workflows used to produce it.

Source: Wilkinson et al., **The FAIR Guiding Principles for scientific data management and stewardship**, Scientific Data 3, 160018 (2016), DOI 10.1038/sdata.2016.18 — https://doi.org/10.1038/sdata.2016.18

Adopted concepts: persistent identity, rich metadata, interoperability, provenance and reuse.  
Local extension: cross-domain reuse telemetry and knowledge-factory asset promotion.

### 2.5 Rules as Code
Where a domain contains rules, obligations or decision logic, represent them in machine-consumable form in addition to human-readable explanation. Do not treat prose interpretation as the final machine representation.

Source: OECD, Mohun & Roberts, **Cracking the code: Rulemaking for humans and machines**, OECD Working Papers on Public Governance No. 42 (2020), DOI 10.1787/3afe6ba5-en — https://www.oecd.org/en/publications/cracking-the-code_3afe6ba5-en.html

Adopted concept: rules should be capable of consistent machine consumption.  
Local extension: evidence-gated applicability, deadlines, roles, consequences, regression testing and red-team review.

### 2.6 Akoma Ntoso / LegalDocumentML
For legal and regulatory domains, preserve document structure, metadata, identity and cross-reference semantics rather than flattening legislation into untraceable text fragments.

Source: OASIS, **Akoma Ntoso Version 1.0** — https://www.oasis-open.org/standard/akn-v1-0/

Adopted concepts: structured machine-readable legislative/judicial documents, common metadata and linking model.  
Local extension: source-version graph, effective-date routing and clause-to-claim evidence binding.

### 2.7 LegalRuleML and related formal rule representation
Research formal representations of legal norms and deontic/rule semantics for future executable legal layers. Adoption into production requires separate benchmarking against simpler domain-specific rule models; complexity alone is not a reason to adopt it.

Reference family: OASIS LegalRuleML / legal rule representation standards.

### 2.8 Software engineering, CI/CD and regression testing
Treat a knowledge base as an executable engineered system. Schema, rules, mappings and decisions require deterministic positive/negative regression tests, change-impact analysis and release gates.

### 2.9 Measurement and continuous improvement
Treat each construction pass as an experiment. Methods are promoted because measured evidence shows better quality-adjusted throughput, lower rework and lower cost—not because they appear elegant.

## 3. Canonical construction pipeline

`SCOPE → SOURCE INVENTORY → ACQUISITION → PROVENANCE → STRUCTURE → ATOMIZATION → ONTOLOGY BINDING → APPLICABILITY → TEMPORAL ROUTING → DECISION LOGIC → ROLE/ACTION/DEADLINE → EVIDENCE OF EXECUTION → CONSEQUENCE → REGRESSION → RED TEAM → RELEASE → TELEMETRY → METHOD IMPROVEMENT`

Every stage has a fail-closed state. Missing evidence must remain UNKNOWN/PENDING/NOT_PROVEN rather than being filled by plausible invention.

## 4. MVP-first maturity model

### M0 — Scope
Freeze domain boundaries, P0 source families, users and decisions the base must support.

### M1 — Registered source universe
Create source inventory, authority hierarchy, versions and acquisition status.

### M2 — Evidence-bearing atomic knowledge
Extract atomic claims/requirements with locators, quotations or equivalent proof, provenance tier and temporal state.

### M3 — Executable applicability
Build classification, applicability and decision paths. Unknown facts fail closed.

### M4 — Operational compilation
Connect decisions to roles, actions, deadlines, evidence, workflows and consequences.

### M5 — Regression-safe knowledge system
Add positive/negative boundary fixtures, deterministic validators, CI gates, conflict handling and change-impact tests.

### M6 — Expert-ready domain MVP
No unresolved Critical/High findings inside frozen scope; proof-floor and red-team gates pass.

### M7 — Portable factory asset
Clone into a materially different domain and prove measured reuse and lower quality-adjusted construction cost.

## 5. Mandatory evidence states

At minimum distinguish:

- PRIMARY_IMMUTABLE
- PRIMARY_DYNAMIC_SNAPSHOT
- PRIMARY_WEB_VERIFIED
- AUTHORITATIVE_SECONDARY
- DISCOVERY_ONLY
- PENDING
- CONFLICT
- NOT_PROVEN
- NOT_APPLICABLE
- SUPERSEDED
- REJECTED

Truth status and provenance tier must remain separate dimensions.

## 6. Mandatory telemetry

Every build pass must emit machine-countable metrics.

### Inventory
`discovered_sources`, `registered_sources`, `primary_sources`, `authoritative_secondary_sources`, `pending_sources`, `rejected_sources`, `superseded_sources`, `immutable_hash_pinned_sources`.

### Knowledge output
`atomic_claims`, `requirements`, `applicability_rules`, `temporal_rules`, `roles`, `deadlines`, `evidence_nodes`, `consequence_rules`, `relations`.

### Quality
`verified_records`, `pending_records`, `conflicts`, `red_team_findings`, `defect_escape_rate`, `regression_pass_rate`, `primary_provenance_rate`, `evidence_closure_rate`, `stale_fact_rate`.

### Speed
`time_to_first_verified`, `time_to_family_proof_floor`, `verified_records_per_hour`, `requirements_per_hour`, `relations_per_hour`, `review_minutes_per_verified_record`.

### Cost
`human_hours`, `machine_processing_cost`, `tool_cost`, `acquisition_cost`, `review_cost`, `rework_cost`, `cost_per_verified_record`, `cost_per_closed_decision_path`.

### Reuse
`reused_schema_objects`, `reused_ontology_terms`, `reused_validators`, `reused_workflows`, `reused_acquisition_recipes`, `reuse_ratio`, `schema_change_rate`.

## 7. Quality-adjusted optimization rule

A new method version may be promoted only if:

1. no new unresolved Critical/High defect is introduced;
2. proof/provenance requirements are not weakened;
3. regression pass rate is not degraded;
4. decision-path/applicability coverage is not materially reduced;
5. at least one target efficiency metric improves: elapsed time, human review load, rework, acquisition success, cost per verified record, or reuse ratio;
6. the result is reproducible in repeated passes or a second domain.

Therefore **faster but less trustworthy is a failed experiment**.

## 8. Method A/B experiments

Candidate strategies include:

- source-first;
- inventory-first;
- ontology-first;
- clause-first;
- graph-first;
- schema-guided extraction;
- retrieval-assisted atomization;
- validator-first;
- red-team-first;
- hybrid pipelines.

Each experiment records method version, domain slice, source complexity, human time, machine cost, output count, provenance tier, defects, rework and regression result.

Preferred method = Pareto-superior or demonstrably better quality-adjusted throughput across repeated experiments.

## 9. Golden assets

Promote repeatedly successful artifacts into a versioned factory library:

- source acquisition recipes;
- source authority/precedence rules;
- universal ontology fragments;
- domain ontology templates;
- extraction schemas/prompts;
- provenance templates;
- applicability patterns;
- temporal-routing patterns;
- evidence contracts;
- validators;
- regression fixtures;
- red-team checklists;
- document-generation templates;
- clone playbooks.

Every golden asset needs an ID, version, provenance of creation, domains tested, benchmark result and deprecation rule.

## 10. Cost-minimization strategy

Optimize total lifecycle cost, not cheapest extraction step.

Priority order:

1. avoid rediscovery through reusable source inventories and acquisition recipes;
2. automate deterministic validation before expensive expert review;
3. send humans ambiguous/high-impact records rather than every record;
4. cache immutable source artifacts and parsed structures;
5. incrementally rebuild only affected graph regions after source changes;
6. reuse stable ontology/schema/validators across domains;
7. measure rework because cheap low-quality extraction that causes later rework is not cheap;
8. select model/tool tier according to task complexity and benchmarked error rate;
9. preserve negative findings and failed acquisition paths so future agents do not repeat them.

## 11. Flagship learning protocol

Security Knowledge Core is Flagship Domain 01. Its purpose is both useful security knowledge and training the construction methodology.

After every material Security build pass:

1. capture telemetry;
2. record defects and rework;
3. identify reusable pattern or anti-pattern;
4. compare with current method baseline;
5. propose method change;
6. test the change on a bounded slice;
7. promote only after quality gates;
8. update this methodology version and changelog.

Future flagships (electronics, robotics, medicine, agriculture, etc.) must repeat the protocol and report cross-domain reuse.

## 12. Research questions

- What source ordering minimizes time-to-proof-floor?
- When does ontology-first outperform source-first?
- What percentage of atomization can be automated without increasing defect escape?
- Which evidence tiers require mandatory human review?
- Which validators generalize across domains?
- What is the optimal granularity of an atomic claim?
- How should confidence, freshness and corroboration be calibrated separately?
- When should RDF/OWL/SHACL replace or coexist with YAML/property-graph representations?
- Can LegalRuleML materially improve correctness enough to justify its complexity?
- What acquisition/cache strategy minimizes cost for dynamic sources?
- What is the relationship between domain complexity and human-review minutes?
- How quickly does cost per verified node fall from flagship 1 to flagship N?

## 13. Required benchmark report per flagship

Each flagship must eventually publish:

- frozen scope;
- exact source counts by state;
- exact knowledge-node/relation counts;
- quality and coverage metrics;
- human and machine effort;
- total and unit costs;
- defects/rework;
- reusable versus new assets;
- method versions tested;
- A/B results;
- red-team findings;
- lessons transferred to the factory method.

## 14. Change policy

This is a living research method. Version changes require a recorded reason and expected measurable effect.

- PATCH: wording/clarification with no method behavior change.
- MINOR: new metric, stage, validator class or compatible process improvement.
- MAJOR: changed proof-floor, ontology contract, evidence semantics or construction lifecycle.

No historical benchmark may be silently recalculated under a new methodology version. Preserve the method version used for each experiment.

## 15. Current success criterion

The long-term target is not maximum document count. It is:

**faster + cheaper + equally or more trustworthy + reproducible + portable knowledge construction.**

The factory is considered to be learning only when later domains demonstrate measurable reduction in quality-adjusted time/cost while retaining or improving proof, coverage and red-team results.
