# FATHER — канонический бумажный конвейер проектирования и воплощения

Status: `CANDIDATE / FULL END-TO-END ALGORITHM / AUTOMATION FROZEN UNTIL REVIEW`

## 0. Назначение

Этот документ задаёт **полный инженерный алгоритм FATHER от исходной бизнес-потребности до эксплуатации, эволюции и вывода системы из эксплуатации**.

Главное правило: сначала строится законченный бумажный конвейер — какие данные нужны, какие канонические информационные артефакты появляются, кто ими владеет, какие методы обработки применяются, какие источники дают основание и какой gate разрешает следующий шаг. Только после утверждения этого алгоритма автоматизация и Model Zoo получают право исполнять его.

FATHER не считает документом только Word/PDF. Артефакт — канонический информационный объект, который может быть Markdown/YAML/JSON/OpenAPI/диаграммой/SBOM/SARIF/test evidence/office document.

---

## 1. Источники и их приоритет

### 1.1 Классы входной информации

1. **Обязательные внешние требования** — применимые законы, постановления, приказы регуляторов и иные обязательные нормы.
2. **Обязательные проектные требования** — договор, ТЗ, owner decisions, корпоративные политики, обязательные SLA/ограничения.
3. **Стандарты и методические документы** — ГОСТ/ISO/IEC/методики; применяются по области действия и/или когда сделаны обязательными договором/политикой.
4. **Фактические данные проекта** — существующие документы, код, API, схемы, конфигурация, telemetry, incidents, test evidence.
5. **Профессиональные источники** — книги, OTUS, статьи, паттерны. Они дают методы и варианты, но не могут отменять нормативные/owner requirements.

### 1.2 Правило конфликта

`обязательная норма → обязательное проектное требование → подтверждённый факт проекта → применимый стандарт/методика → профессиональная рекомендация`.

Если конфликт нельзя разрешить по authority/applicability, он остаётся `CONFLICTED` и блокирует зависимый gate.

### 1.3 Book knowledge

Идея из книги проходит:

`DISCOVERED → SOURCE_VERIFIED → MAPPED → IMPLEMENTED_CANDIDATE → INDEPENDENT_REVIEW → PROMOTED`.

Книги не становятся системным правилом напрямую. Сейчас source-verified идеи Richards/Ford используются для architecture characteristics, trade-offs, ADR, risk review и continuous architecture analysis. C4 используется как метод представления Context/Container/Component views. Остальные книги проходят отдельный intake до promotion.

---

# 2. Сквозной алгоритм

```text
A0 SOURCE & PROJECT INTAKE
 ↓
A1 PRODUCT DISCOVERY
 ↓
A2 SECURITY / LEGAL / DATA INTAKE
 ↓
A3 BUSINESS + SYSTEM ENGINEERING
 ↓
A4 THREAT MODEL v0
 ↓
A5 REQUIREMENTS + NFR + ACCEPTANCE BASELINE
 ↓
A6 DELIVERY FEASIBILITY / ESTIMATE / RISK / TCO / POC PLAN
 ↓
A7 ARCHITECTURE DRIVERS + OPTIONS
 ↓
A8 ARCHITECTURE VERIFICATION + DECISION / ADR
 ↓
A9 DETAILED DESIGN
 ↓
A10 IMPLEMENTATION PLAN + BUILD / CI / MLOPS PLAN
 ↓
A11 IMPLEMENTATION BASELINE
 ↓
A12 VERIFICATION / VALIDATION / SECURITY / GENAI QUALITY
 ↓
A13 RELEASE / MIGRATION / ROLLBACK / PRODUCTION READINESS
 ↓
A14 OPERATION / OBSERVABILITY / SLO / INCIDENTS / FINOPS
 ↓
A15 EVOLUTION / SCALE / RADAR / GOVERNANCE / API PRODUCT
 ↓
A16 RETIREMENT
```

Каждый шаг работает по общей формуле:

```text
INPUT SNAPSHOT
→ applicability
→ source/evidence extraction
→ normalize/classify
→ map to artifact fields
→ gap/conflict/staleness analysis
→ owner input
→ draft
→ domain review
→ independent review where material
→ gate
→ immutable/versioned handoff
```

---

# A0. Source & Project Intake

## Входы
- sponsor/business request;
- RFP/contract/TZ/current documentation;
- source code, repositories, interfaces and deployments for brownfield;
- normative source registry;
- approved professional-source registry.

## Обработка
1. определить `greenfield / brownfield / hybrid`;
2. зафиксировать immutable source snapshot/version/hash;
3. определить source class, owner/authority, date/freshness;
4. извлечь atomic items: `FACT / CLAIM / REQUIREMENT / CONSTRAINT / ASSUMPTION / DECISION / RISK / UNKNOWN`;
5. выполнить terminology/entity normalization без потери original wording;
6. выявить дубли, версии, supersession и конфликты;
7. сопоставить существующие материалы будущим canonical artifacts.

## Артефакты
- PROJECT_SOURCE_REGISTER;
- SOURCE_VERSION_REGISTER;
- PROJECT_INTAKE_INVENTORY;
- EXISTING_ARTIFACT_COVERAGE_MAP;
- INITIAL_GAP_REGISTER;
- TERMINOLOGY_CANDIDATES;
- EVIDENCE_REGISTER.

## Алгоритмы/методы
- checksum/version identity;
- semantic segmentation;
- exact + normalized terminology matching;
- document-to-artifact field mapping;
- freshness/supersession analysis;
- provenance graph creation.

## Gate
`PROJECT_INTAKE_READY`

---

# A1. Product Discovery

## Входы
- business need/sponsor context;
- current pain/loss/opportunity evidence;
- stakeholder information;
- contractual context.

## Обработка
1. отделить проблему от заранее выбранного решения;
2. определить target users/buyers/operators;
3. сформировать value proposition и product boundary;
4. построить happy/alternate/failure user journeys;
5. определить IN/OUT scope;
6. определить KPI/outcome и baseline gap;
7. завести assumptions/UNKNOWN;
8. определить decision authority.

## Артефакты
- BUSINESS_NEED;
- PRODUCT_VISION;
- TARGET_USERS / USER_JOURNEYS;
- VALUE_PROPOSITION;
- SUCCESS_METRICS;
- STAKEHOLDER_REGISTER;
- SCOPE_BASELINE;
- ASSUMPTION_LOG;
- PRODUCT_READY_DECISION.

## Методы
- stakeholder interview/workshop;
- problem-vs-solution check;
- journey mapping;
- scope decomposition;
- KPI baseline/target logic;
- assumption register.

## Норматив/методические основания
- ГОСТ Р 57193-2025 lifecycle/stakeholder processes;
- ГОСТ Р 57101-2016 project controls;
- ГОСТ Р 58609-2019 information-item discipline.

## OTUS
Lessons 1–3 / Gate G1.

## Gate
`PRODUCT_READY`

---

# A2. Security / Legal / Data Intake

## Входы
- Product package;
- system/product scope;
- stakeholder roles;
- intended data/source/provider classes;
- normative registry.

## Обработка
1. определить юрисдикцию/sector/system type;
2. проверить applicability обязательных overlays;
3. инвентаризировать data categories and owners;
4. выполнить preliminary classification/sensitivity;
5. определить trust assumptions и abuse cases;
6. определить external-processing restrictions;
7. сформировать ранние security/legal/data constraints;
8. unresolved legal questions направить Legal/Data Owner, не закрывать технически.

## Артефакты
- SECURITY_INTAKE;
- REGULATORY_APPLICABILITY;
- DATA_INVENTORY;
- DATA_CLASSIFICATION;
- INITIAL_ABUSE_CASES;
- SECURITY_CONSTRAINTS;
- SECURITY_QUESTIONS_LOG.

## Методы
- applicability decision tree;
- data inventory/classification;
- trust-boundary pre-analysis;
- abuse-case elicitation;
- authority matrix.

## Normative overlays
- ФСТЭК 117 when applicable;
- ПП РФ 1119 + ФСТЭК 21 for ISPDn;
- ФСБ 378 if crypto/ISPDn applies;
- ПП РФ 127 + ФСТЭК 235/239 for applicable KII cases;
- ГОСТ Р 56939-2024 secure development baseline.

## Gate
`SECURITY_INTAKE_READY`

---

# A3. Business + System Engineering

## Входы
- Product Ready package;
- Security/Data constraints;
- existing AS-IS systems/interfaces/data.

## Обработка
### Business/domain
- process modeling;
- business rules;
- glossary/domain concepts;
- use cases/operator journeys.

### System
1. identify system-of-interest and boundary;
2. actors/external systems;
3. decompose logical functions without technology choice;
4. build data flows and trust-boundary candidates;
5. inventory interfaces/dependencies;
6. define operational modes and environment assumptions.

## Артефакты
- BUSINESS_PROCESS_MODEL;
- BUSINESS_RULE_CATALOGUE;
- DOMAIN_GLOSSARY;
- SYSTEM_CONTEXT;
- SYSTEM_BOUNDARY;
- FUNCTION_MODEL;
- DATA_FLOW_MODEL;
- INTERFACE_INVENTORY;
- EXTERNAL_DEPENDENCY_REGISTER;
- OPERATIONAL_MODES;
- SYSTEM_ASSUMPTION_LOG.

## Методы
- BPMN/SIPOC/IDEF0 where useful;
- functional decomposition;
- context diagram;
- DFD;
- interface/dependency inventory;
- brownfield reverse mapping from API/config/code when authorized.

## Normative/book basis
- ГОСТ Р 57193-2025 system lifecycle;
- ГОСТ Р 59793-2021 creation stages;
- Simon Brown C4: System Context is mandatory context view; Container follows after context for high-level responsibility/technology shape.

## Gate
`SYSTEM_MODEL_READY`

---

# A4. Threat Model v0

## Входы
- System Context/Boundary;
- DFD;
- interfaces/dependencies;
- data classification;
- abuse/security constraints.

## Обработка
1. protected interests/assets/data/processes;
2. negative consequences;
3. threat-source candidates;
4. entry points and trust boundaries;
5. attacker capabilities/assumptions;
6. threat scenarios/chains;
7. map scenario → security driver → draft requirement;
8. initial likelihood/impact/risk only where basis exists.

## Артефакты
- THREAT_MODEL_V0;
- THREAT_SCENARIO_REGISTER;
- TRUST_BOUNDARY_REGISTER;
- SECURITY_REQUIREMENTS_DRAFT;
- SECURITY_RISK_REGISTER.

## Методы
- ФСТЭК threat assessment methodology;
- threat trees / attack paths;
- misuse/abuse cases;
- asset → consequence → threat source → scenario → driver trace.

## Gate
`THREAT_MODEL_V0_READY`

---

# A5. Requirements + NFR + Acceptance Baseline

## Входы
- Product Vision/Scope;
- business/system model;
- threat model/security draft requirements;
- applicable normative requirements;
- operational constraints.

## Обработка
1. classify requirements: business / stakeholder / system / software / security / quality;
2. remove ambiguity and solution leakage unless it is a real constraint;
3. normalize terminology;
4. detect duplicates/conflicts/orphans;
5. derive measurable NFR scenarios;
6. define verification method for each material requirement;
7. define acceptance criteria;
8. build bidirectional traceability.

## Артефакты
- BUSINESS_REQUIREMENTS;
- STAKEHOLDER_REQUIREMENTS;
- SYSTEM_REQUIREMENTS;
- SOFTWARE_REQUIREMENTS;
- NFR_CATALOGUE;
- SECURITY_REQUIREMENTS;
- ACCEPTANCE_CRITERIA;
- REQUIREMENTS_TRACEABILITY_MATRIX;
- requirement assumptions/conflicts.

## Algorithms
- atomic requirement extraction;
- ambiguity/modality scan;
- duplicate similarity + semantic conflict analysis;
- NFR quality-attribute scenario: stimulus → environment → response → measure;
- requirement ↔ source ↔ owner ↔ test mapping.

## Normative basis
- ГОСТ 34.602-2020 for AS technical assignment structure where applicable;
- ГОСТ Р 58609-2019 information items;
- ГОСТ Р 57193-2025 requirements processes;
- ГОСТ Р 56939-2024 security requirements.

## Gate
`REQUIREMENTS_BASELINE_READY`

---

# A6. Delivery Feasibility / Estimate / Risk / TCO / PoC Plan

## Входы
- Requirements/NFR baseline;
- known constraints/dependencies;
- procurement/finance/operations inputs;
- unresolved technical uncertainty.

## Обработка
1. WBS by capabilities/work packages;
2. Estimate v0: analogous/parametric/PERT/bottom-up/hybrid;
3. explicitly record assumptions/ranges, never fake precision;
4. project risk matrix and dependencies;
5. initial TCO scenarios;
6. define PoC hypotheses for high uncertainty;
7. define GO/PIVOT/STOP evidence gates;
8. change-control model.

## Артефакты
- DELIVERY_WBS_V0;
- ESTIMATION_REGISTER_V0;
- ESTIMATION_ASSUMPTION_LOG;
- PROJECT_RISK_REGISTER;
- TCO_MODEL_V0;
- CHANGE_MANAGEMENT_MODEL;
- POC_PLAN / POC_GATE_CRITERIA;
- DELIVERY_FEASIBILITY_DECISION.

## OTUS
Lessons 2–3; later refined by 16–17 and 28.

## Gate
`DELIVERY_FEASIBILITY_READY`

---

# A7. Architecture Drivers + Options

## Entry condition
Architecture starts only after Product/Security/System/Threat/Requirements gates and sufficient feasibility evidence.

## Входы
- system model;
- requirements/NFR;
- threat/security requirements;
- cost/operability constraints;
- PoC evidence where required.

## Обработка
1. derive explicit + implicit architecture characteristics;
2. keep only materially differentiating drivers;
3. build Quality Attribute Scenarios;
4. generate **multiple** architecture options;
5. represent with C4 Context/Container and other required viewpoints;
6. assess data/integration/security/deployment impacts;
7. perform trade-off analysis;
8. risk storm / failure-mode review;
9. mark assumptions and required experiments.

## Артефакты
- ARCHITECTURE_DRIVER_SET;
- QUALITY_ATTRIBUTE_SCENARIOS;
- ARCHITECTURE_OPTION_SET;
- ARCHITECTURE_VIEWS;
- OPTION_TRADEOFF_MATRIX;
- OPTION_SECURITY_REVIEW;
- ARCHITECTURE_RISK_REGISTER;
- OPTION_POC_REQUIREMENTS.

## Methods/books
- Richards/Ford: architecture characteristics as first-class drivers; trade-offs, not universal best technology; collaborative risk analysis;
- C4: Context + Container always expected; Component only when it adds decision value;
- OTUS 4–7, 11–17, 21–27 are pattern/tool inputs **invoked conditionally**, not mandatory technologies.

## Gate
`ARCHITECTURE_OPTIONS_READY`

---

# A8. Architecture Verification + Decision

## Входы
- option set;
- trade-off/security/risk evidence;
- PoC/benchmark results;
- feasibility/TCO;
- owner constraints.

## Обработка
1. independent challenge: hidden assumptions, missing alternatives, failure modes;
2. ATAM/quality-scenario reasoning where useful;
3. CTO challenge for material decisions;
4. evidence completeness check;
5. residual-risk identification;
6. decision + rejected alternatives;
7. rollback/replacement path;
8. revisit triggers.

## Артефакты
- ARCHITECTURE_DECISION_RECORDS;
- TARGET_ARCHITECTURE;
- DECISION_EVIDENCE_REGISTER;
- RESIDUAL_RISK_REGISTER;
- independent review record;
- supersession links.

## Book basis
- Richards/Ford ADR lifecycle: status/context/decision/consequences/history;
- significant decision is immutable; replacement supersedes.

## OTUS
8–10, CTO Challenge and architecture governance.

## Gate
`ARCHITECTURE_DECISION_READY`

---

# A9. Detailed Design

## Входы
- Target Architecture + ADRs;
- requirements/security requirements;
- data/integration constraints.

## Обработка
1. C3/component decomposition;
2. sequence/state models for critical scenarios;
3. API/event/data contracts and compatibility/version policy;
4. data model + lineage;
5. IAM/authorization matrix;
6. secrets/key model;
7. deployment topology;
8. observability design;
9. threat model v1/v2 against actual components/flows;
10. test strategy;
11. sizing model and capacity assumptions;
12. HA/DR requirements/design if NFRs require them;
13. tenancy/cloud/privacy patterns only if applicable.

## Артефакты
- COMPONENT_DESIGN;
- API_CONTRACTS / EVENT_SCHEMAS;
- DATA_MODEL / DATA_PIPELINE_DESIGN;
- IAM_MODEL;
- SECRETS_MODEL;
- DEPLOYMENT_DESIGN;
- OBSERVABILITY_DESIGN;
- SIZING_MODEL;
- HA_DR_DESIGN where applicable;
- THREAT_MODEL_V1_V2;
- TEST_STRATEGY.

## OTUS pattern catalogue
- 5 LLD;
- 11 integration;
- 12 data;
- 14 security;
- 15 observability;
- 16–17 sizing/inference;
- 21 HA/DR;
- 22 Serverless/K8s;
- 23 EDA;
- 24 high-load/low-latency;
- 25 hybrid/multicloud;
- 26 multi-tenancy;
- 27 privacy-preserving.

## Gate
`DESIGN_READY_FOR_IMPLEMENTATION`

---

# A10. Implementation Plan + Build/CI/MLOps Plan

## Входы
- detailed design;
- test/security strategy;
- deployment/sizing;
- configuration model.

## Обработка
1. map components/contracts to work items;
2. Definition of Ready;
3. dependency/supply-chain plan;
4. IaC/environment plan;
5. CI/CD stages and promotion gates;
6. model/data/prompt/index versioning and MLOps lifecycle when AI is in scope;
7. rollout/rollback strategy;
8. migration rehearsals where needed.

## Артефакты
- IMPLEMENTATION_PLAN;
- DELIVERY_BACKLOG;
- IaC_PLAN;
- CI_CD_DESIGN;
- MLOPS_DESIGN / MODEL_REGISTRY_POLICY;
- CONFIGURATION_IDENTIFICATION_PLAN;
- RELEASE_STRATEGY;
- MIGRATION_TEST_PLAN.

## OTUS
18 IaC/CI-CD, 19 MLOps, 20 deployment strategy.

## Gate
`IMPLEMENTATION_PLAN_READY`

---

# A11. Implementation Baseline

## Inputs
approved design + implementation plan.

## Обработка
- secure coding;
- code review;
- unit/component tests;
- build reproducibility;
- dependency pinning/SBOM;
- SAST/SCA/secrets scans;
- configuration/version baselining;
- model/prompt/data/index manifest generation for AI components.

## Артефакты
- SOURCE_CODE;
- BUILD_MANIFEST;
- DEPENDENCY_LOCK;
- SBOM;
- CONFIGURATION_BASELINE;
- CODE_REVIEW_RECORDS;
- UNIT_TEST_RESULTS;
- SAST/SCA/SECRET_SCAN results;
- AI_COMPONENT_MANIFESTS.

## Normative basis
- ГОСТ Р ИСО/МЭК 12207-2010;
- ГОСТ Р 56939-2024;
- ГОСТ Р 71207-2024 for static analysis process.

## Gate
`IMPLEMENTATION_BASELINE_READY`

---

# A12. Verification / Validation / Security / GenAI Quality

## Входы
- implementation baseline;
- RTM;
- test strategy;
- threat/security requirements;
- Golden/Eval datasets for AI.

## Обработка
1. integration/system tests;
2. security/DAST/adversarial tests;
3. performance/load/reliability tests;
4. acceptance/validation;
5. requirements coverage/orphan checks;
6. GenAI: retrieval metrics, Faithfulness/groundedness, Answer Relevancy, citation/provenance, refusal/safety;
7. compare model candidates on same dataset/context;
8. test repeatability/flakiness;
9. defect/vulnerability triage;
10. release-candidate gate.

## Артефакты
- INTEGRATION_TEST_RESULTS;
- SYSTEM_TEST_RESULTS;
- SECURITY_TEST_RESULTS;
- DAST_RESULTS;
- PERFORMANCE_TEST_RESULTS;
- GENAI_EVAL_REPORT;
- ACCEPTANCE_TEST_RESULTS;
- DEFECT_REGISTER;
- VULNERABILITY_REGISTER;
- VERIFICATION_REPORT;
- VALIDATION_REPORT.

## Normative/OTUS
- ГОСТ Р 59792-2021 tests of automated systems;
- ГОСТ Р 56939-2024 security verification;
- OTUS 13 quality + 14 security + 15 observability evidence + 16/17 load/sizing validation.

## Gate
`RELEASE_CANDIDATE_READY`

---

# A13. Release / Migration / Rollback / Production Readiness

## Входы
- release candidate;
- verified deployment/IaC;
- migration/rollback evidence;
- operational/security readiness.

## Обработка
1. immutable release composition;
2. config/secrets/environment validation;
3. migration rehearsal;
4. canary/blue-green/rolling strategy by risk;
5. rollback rehearsal;
6. operational readiness review;
7. unresolved-risk owner decisions;
8. deployment evidence.

## Артефакты
- RELEASE_MANIFEST;
- RELEASE_NOTES;
- DEPLOYMENT_PLAN;
- MIGRATION_PLAN;
- ROLLBACK_PLAN;
- CHANGE_RECORD;
- DEPLOYMENT_EVIDENCE;
- OPERATIONAL_READINESS_REVIEW.

## OTUS
18–20.

## Gate
`PRODUCTION_READY`

---

# A14. Operation / Observability / SLO / Incidents / FinOps

## Inputs
Production baseline + SLO/SLA + observability design.

## Обработка
- logs/metrics/traces/model telemetry;
- SLI/SLO/error budget;
- security monitoring;
- incident/problem management;
- drift/quality/cost monitoring for AI;
- capacity and FinOps reports;
- vulnerability/dependency lifecycle;
- feedback to requirements/risk/architecture.

## Артефакты
- RUNBOOKS;
- SLO_SLA;
- MONITORING_BASELINE;
- INCIDENT_RECORDS;
- PROBLEM_RECORDS;
- VULNERABILITY_MANAGEMENT_RECORDS;
- CAPACITY_REPORTS;
- SECURITY_MONITORING_REPORTS;
- AI_QUALITY_DRIFT_REPORTS;
- COST_REPORTS;
- FEEDBACK_BACKLOG.

## OTUS
15 observability, 21 HA/DR operational verification, 28 FinOps.

## Gate
`OPERATION_CONTROLLED`

---

# A15. Evolution / Scale / Radar / Governance / API Product

This is a feedback loop, not a one-time final phase.

## Triggers
- SLO breach / incident;
- business change;
- cost anomaly;
- new regulation;
- technology lifecycle/EOL;
- model/data drift;
- new tenant/region/load;
- API consumer needs.

## Processing
1. classify trigger as requirement/risk/debt/opportunity/incident;
2. technology radar: adopt/trial/assess/hold with evidence;
3. architecture health review;
4. evolutionary fitness functions;
5. FinOps trade-offs;
6. Ethical AI/Governance assessment where AI decisions affect people/processes;
7. API as product: consumers, contract/version/SLO/deprecation, economics;
8. determine smallest lifecycle stage to reopen;
9. create new ADR/change package rather than silently rewrite history.

## Artifacts
- ARCHITECTURE_HEALTH_REVIEW;
- TECHNOLOGY_RADAR;
- TECH_DEBT_REGISTER;
- CHANGE_REQUESTS;
- FINOPS_DECISION_RECORDS;
- AI_GOVERNANCE / MODEL_CARD where applicable;
- API_PRODUCT_MODEL / API_LIFECYCLE_POLICY;
- updated ROADMAP / FEEDBACK_BACKLOG.

## OTUS
22–31, especially 28 FinOps, 29 radar/evolution, 30 Ethical AI/Governance, 31 API as product.

---

# A16. Retirement

## Inputs
retirement decision + current inventory/dependencies/data obligations.

## Processing
- data disposition/archive;
- access/key/secrets revocation;
- integration shutdown;
- dependency/provider termination;
- compliance/retention confirmation;
- consumer migration/deprecation completion;
- final verification and lessons learned.

## Artifacts
- RETIREMENT_PLAN;
- DATA_DISPOSITION_PLAN;
- ACCESS_REVOCATION_RECORD;
- ARCHIVE_PACKAGE;
- DEPENDENCY_DECOMMISSION_RECORD;
- RETIREMENT_VERIFICATION_REPORT;
- LESSONS_LEARNED.

## Gate
`RETIRED_VERIFIED`

---

# 3. Where Model Zoo will eventually operate

Model Zoo is **not a stage**. It is a review/analysis mechanism invoked inside the paper pipeline only when the artifact/decision is material.

Possible future invocation points after paper approval:

- A0: conflict/definition/source challenge — advisory;
- A1: problem/scope challenge — advisory;
- A2: security/legal/data gap challenge — Legal/Data final authority remains human;
- A4: threat scenario challenge;
- A5: requirement ambiguity/conflict/testability challenge;
- A6: estimate/risk assumption challenge;
- A7: option generation and trade-off challenge;
- A8: full Champion + blind Challengers + Evidence Verifier + Independent Judge;
- A9: detailed-design consistency/security challenge;
- A12: model/eval comparison and independent quality judge;
- A15: technology-radar and architecture-health challenge.

Never delegated to Zoo as final authority:
- legal applicability;
- data-owner classification/allowed use;
- business scope/value authority;
- residual-risk acceptance;
- final production/release authority.

---

# 4. OTUS is a method catalogue, not the execution clock

OTUS 1–31 remains the learning/capability crosswalk. Some later lessons supply methods that FATHER must invoke earlier when requirements trigger them.

Examples:
- Lesson 21 HA/DR belongs in NFR/Architecture/Detailed Design, not only after deployment.
- Lesson 24 High-load/Low-latency affects A5/A7/A9 sizing and design.
- Lesson 27 Privacy-Preserving affects A2/A7/A9 before implementation when required.
- Lesson 28 FinOps starts at feasibility/TCO and continues in operation.
- Lesson 30 Ethical AI/Governance can add requirements before architecture, not only at course end.
- Lesson 31 API as Product begins when external API consumers appear and continues through operation/deprecation.

---

# 5. Standard/book separation

## Normative layer
The current source registry covers core lifecycle/documentation/requirements/architecture/tests/secure-development plus selected state-system/PDn/KII overlays. Exact clause-level rules are not yet claimed until full-text ingestion and verification.

## Professional-method layer
Books/course methods are candidates that help **how** to analyze/design/review; they never override **what must be true** from applicable law/contract/owner requirements.

Verified current book contributions:
- Richards/Ford: architecture characteristics, trade-offs, ADR, architecture-risk review, continuous architecture analysis;
- Simon Brown C4: hierarchical Context → Container → Component representation, with Context/Container expected and deeper diagrams only when useful.

Software Architecture: The Hard Parts remains a book-pipeline candidate until source bytes/evidence are formally promoted.

---

# 6. Activation rule for automation

No runtime worker, Model Zoo or automatic gate may become the source of lifecycle truth before:

1. this paper pipeline is reviewed;
2. artifact schemas are complete enough;
3. source/applicability precedence is approved;
4. gate rules are explicit;
5. authority boundaries are explicit;
6. representative greenfield and brownfield walkthroughs pass;
7. conflicts/UNKNOWN/rework loops are tested on paper.

Only after that do we map each paper operation to deterministic logic, single-LLM worker, Model Zoo panel or human task.