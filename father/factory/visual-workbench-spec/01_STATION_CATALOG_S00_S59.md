# FATHER Visual Workbench — Station Catalog S00–S59

Status: `DRAFT_V0.1 / CANDIDATE STATION MODEL`

## 1. Назначение

Этот каталог раскладывает макроцикл A0–A16 на 60 визуальных engineering stations. Каждая станция должна быть достаточно маленькой, чтобы проектировщик понимал:

```text
что вошло
→ что мы делаем
→ каким методом
→ кто отвечает
→ что вышло
→ чем проверили
→ можно ли идти дальше
```

Станция — не обязательно отдельный документ и не обязательно отдельный runtime worker. Это **единица инженерной трансформации** и визуальная единица Workbench.

Общий node pattern:

```text
[typed inputs] → [Sxx station] → [typed outputs]
                       ↓
                 local readiness
```

---

# A0 — Source & Project Intake

## S00 — Project Shell & Mode Classification

**Цель:** создать проектный контекст и определить `GREENFIELD / BROWNFIELD / HYBRID`.

**Входы:** business request, sponsor context, existing project references.  
**Методы:** deterministic intake checklist, mode classification.  
**Выходы:** PROJECT_ID, PROJECT_MODE, initial owner assignments, project metadata.  
**Owner:** Project Manager.  
**Ready:** project has stable ID, accountable sponsor/owner and selected mode.  
**UI:** стартовый узел; double-click открывает Project Inspector.

## S01 — Source Acquisition & Registration

**Цель:** зарегистрировать все исходные материалы до анализа.

**Входы:** files, URLs, repositories, contracts, TZ, policies, emails/notes where admitted.  
**Методы:** source registry, acquisition record.  
**Выходы:** PROJECT_SOURCE_REGISTER entries.  
**Owner:** Knowledge Growth Analyst / Project Manager.  
**Ready:** каждый принятый source имеет origin/type/owner/locator.

## S02 — Source Identity, Version, Hash & Classification

**Цель:** зафиксировать идентичность и версию evidence.

**Методы:** SHA-256/content identity where applicable, metadata extraction, source-classification rules.  
**Выходы:** SOURCE_VERSION_REGISTER, effective/stale/superseded status, data class.  
**Ready:** material source cannot silently change without new revision.

## S03 — Parse / Extract / Segment

**Цель:** получить машиночитаемое представление без потери provenance.

**Методы:** native parser first, OCR fallback, layout segmentation, source-locator preservation.  
**Выходы:** aligned text/blocks/pages/chunks with stable source refs.  
**Ready:** original source remains recoverable; derived content links back to locator.

## S04 — Atomic Information Extraction

**Цель:** разбить material на минимальные смысловые элементы.

**Классы:** FACT, CLAIM, REQUIREMENT, CONSTRAINT, ASSUMPTION, DECISION, RISK, UNKNOWN.  
**Методы:** deterministic patterns + bounded semantic assistance later.  
**Выходы:** atomic items with evidence refs.  
**Ready:** material items do not lose source context/qualifiers.

## S05 — Terminology / Entity Normalization

**Цель:** выявить термины, aliases, entities и конфликтующие смыслы.

**Методы:** exact matching, normalized matching, glossary candidate mapping, sense separation.  
**Выходы:** DOMAIN_GLOSSARY candidates, entity map, unresolved terminology conflicts.  
**Ready:** same word with different senses is not forcibly merged.

## S06 — Existing Artifact Coverage Mapping

**Цель:** сопоставить существующие материалы каноническим artifact fields.

**Методы:** artifact-field mapping, source→field graph.  
**Выходы:** EXISTING_ARTIFACT_COVERAGE_MAP.  
**Ready:** file presence is not treated as completeness.

## S07 — Initial Gap / Conflict / Freshness Analysis

**Цель:** определить, что известно, что отсутствует, что конфликтует и что устарело.

**Методы:** completeness rules, conflict/supersession check, freshness policy.  
**Выходы:** INITIAL_GAP_REGISTER, CONFLICT register, stale flags.  
**Ready:** blockers visible before Product stage.

---

# A1 — Product Discovery

## S08 — Business Need

**Цель:** отделить реальную проблему/возможность от заранее выбранного решения.

**Входы:** sponsor evidence, pain/loss/opportunity, strategic context.  
**Методы:** problem-vs-solution test, 5W framing, evidence challenge.  
**Выходы:** BUSINESS_NEED.  
**Owner:** Business Owner.  
**Ready:** need stated independently from technology.

## S09 — Stakeholders & Decision Authority

**Цель:** определить участников, owners и полномочия.

**Методы:** stakeholder mapping, RACI-like responsibility model, authority separation.  
**Выходы:** STAKEHOLDER_REGISTER, AUTHORITY_MAP.  
**Ready:** material domains have accountable owner/reviewer/final authority.

## S10 — Product Vision, Value & Scope

**Цель:** определить кому, какую ценность и в каких границах создаём.

**Методы:** value proposition, IN/OUT scope, boundary challenge.  
**Выходы:** PRODUCT_VISION, VALUE_PROPOSITION, SCOPE_BASELINE.  
**Ready:** explicit exclusions exist.

## S11 — Users, Journeys & Business Processes

**Цель:** описать работу пользователя и business process до system design.

**Методы:** journey mapping, BPMN/SIPOC/IDEF0 as applicable.  
**Выходы:** TARGET_USERS, USER_JOURNEYS, BUSINESS_PROCESS_MODEL.  
**Ready:** happy/alternate/failure paths identified for material flows.

## S12 — Success Metrics, Assumptions & Product Gate

**Цель:** определить измеряемый outcome и зафиксировать неизвестное.

**Методы:** KPI baseline/target logic, assumption register, owner confirmation.  
**Выходы:** SUCCESS_METRICS, ASSUMPTION_LOG, PRODUCT_READY_DECISION.  
**Ready:** Product Ready gate may close or return to S08–S11.

---

# A2 — Security / Legal / Data Intake

## S13 — Regulatory / Contractual Applicability

**Цель:** определить применимые обязательные правила.

**Входы:** scope, organization/system type, data categories, jurisdiction, contracts/policies.  
**Методы:** applicability decision tree, current-version check, authority review.  
**Выходы:** REGULATORY_APPLICABILITY.  
**Owner:** Legal/Compliance with Security.  
**Ready:** UNKNOWN applicability remains explicit blocker where material.

## S14 — Data Inventory, Ownership & Classification

**Цель:** понять какие данные существуют и что с ними допустимо.

**Методы:** data inventory, classification policy, owner mapping, retention/use constraints.  
**Выходы:** DATA_INVENTORY, DATA_CLASSIFICATION.  
**Owner:** Data Owner.  
**Ready:** material data flows can inherit classification.

## S15 — Security Intake & Initial Abuse Cases

**Цель:** сформировать ранние security constraints до system architecture.

**Методы:** abuse-case brainstorming, trust assumptions, secure-by-design intake.  
**Выходы:** SECURITY_INTAKE, INITIAL_ABUSE_CASES, SECURITY_CONSTRAINTS.  
**Ready:** security questions visible for System Engineering.

---

# A3 — Business + System Engineering

## S16 — System Context & Boundary

**Цель:** определить систему в окружающей среде.

**Методы:** context modeling, C4 Context, scope/system boundary rules.  
**Выходы:** SYSTEM_CONTEXT, SYSTEM_BOUNDARY.  
**Ready:** external actors/systems and ownership boundary visible.

## S17 — Functions, Business Rules & Responsibilities

**Цель:** описать что система должна делать без выбора implementation technology.

**Методы:** functional decomposition, rule catalogue, responsibility allocation.  
**Выходы:** FUNCTION_MODEL, BUSINESS_RULE_CATALOGUE.  
**Ready:** function set supports later requirements.

## S18 — Data Flow Model

**Цель:** показать что, откуда, куда и в каком trust context перемещается.

**Методы:** DFD, source/sink/store/process model, classification propagation.  
**Выходы:** DATA_FLOW_MODEL.  
**Ready:** material flows have origin/destination/data class.

## S19 — Interfaces & External Dependencies

**Цель:** инвентаризировать integration boundaries.

**Методы:** interface inventory, dependency classification, ownership/SLA capture.  
**Выходы:** INTERFACE_INVENTORY, EXTERNAL_DEPENDENCY_REGISTER.  
**Ready:** unknown external dependencies identified.

## S20 — Operational Modes & System Assumptions

**Цель:** зафиксировать normal/degraded/maintenance/offline/emergency modes.

**Методы:** mode/state analysis, assumption capture.  
**Выходы:** OPERATIONAL_MODES, SYSTEM_ASSUMPTION_LOG.  
**Ready:** system model supports threat/NFR reasoning.

---

# A4 — Threat Model v0

## S21 — Protected Interests, Assets & Negative Consequences

**Цель:** понять что именно защищается и что считается ущербом.

**Методы:** asset/protected-interest inventory, consequence analysis.  
**Выходы:** ASSET/PROTECTED_INTEREST register, NEGATIVE_CONSEQUENCES.  
**Ready:** security model anchored in impact, not tool lists.

## S22 — Threat Sources, Trust Boundaries & Entry Points

**Цель:** определить кто/что может инициировать threat и через какие границы.

**Методы:** FSTEC-aligned threat source analysis where applicable, trust-boundary modeling.  
**Выходы:** TRUST_BOUNDARY_REGISTER, THREAT_SOURCE_REGISTER, ENTRY_POINTS.  
**Ready:** every material boundary considered.

## S23 — Threat Scenarios & Security Risks

**Цель:** построить реалистичные attack/abuse scenarios.

**Методы:** scenario chaining, precondition→action→consequence, likelihood/evidence-bounded risk analysis.  
**Выходы:** THREAT_SCENARIO_REGISTER, SECURITY_RISK_REGISTER.  
**Ready:** scenarios are traceable to assets/boundaries/sources.

## S24 — Security Requirements Draft

**Цель:** преобразовать material threat/risk into candidate requirements.

**Методы:** threat→security-driver→requirement mapping.  
**Выходы:** SECURITY_REQUIREMENTS_DRAFT.  
**Ready:** requirement rationale points back to threat/risk/normative source.

---

# A5 — Requirements / NFR / Acceptance

## S25 — Requirements Intake & Normalization

**Цель:** объединить business/stakeholder/system/software/security requirements.

**Методы:** normalization, duplicate/conflict detection, atomicity and verifiability checks.  
**Выходы:** BUSINESS_REQUIREMENTS, STAKEHOLDER_REQUIREMENTS, SYSTEM_REQUIREMENTS, SOFTWARE_REQUIREMENTS, SECURITY_REQUIREMENTS.  
**Ready:** each material requirement has owner/source/rationale.

## S26 — NFR / Quality Attribute Scenarios

**Цель:** сделать quality requirements измеримыми.

**Методы:** stimulus→environment→artifact→response→measure scenario.  
**Выходы:** NFR_CATALOGUE, QUALITY_ATTRIBUTE_SCENARIOS.  
**Ready:** no material NFR remains adjective-only where measure is possible.

## S27 — Acceptance Criteria & Test Oracles

**Цель:** определить как отличить выполненное требование от невыполненного до кода.

**Методы:** Given/When/Then where useful, measurable oracle definition, negative case design.  
**Выходы:** ACCEPTANCE_CRITERIA, TEST_ORACLE candidates.  
**Ready:** critical requirements have observable expected outcomes.

## S28 — Traceability Matrix & Requirements Baseline

**Цель:** собрать versioned baseline.

**Методы:** source→requirement→risk→verification links, completeness validation.  
**Выходы:** REQUIREMENTS_TRACEABILITY_MATRIX, REQUIREMENTS_BASELINE.  
**Ready:** baseline versioned; unresolved gaps bounded/owned.

---

# A6 — Delivery Feasibility

## S29 — WBS & Estimate v0

**Цель:** понять структуру работ и диапазон усилий до detailed architecture.

**Методы:** WBS decomposition, analogous/bottom-up/range estimate, PERT where justified.  
**Выходы:** DELIVERY_WBS_V0, ESTIMATION_REGISTER_V0.  
**Ready:** assumptions and uncertainty visible.

## S30 — Project Risk & TCO Model

**Цель:** сравнить delivery risk/cost exposure.

**Методы:** risk matrix/Monte Carlo later if justified, TCO scenarios, cost-driver model.  
**Выходы:** PROJECT_RISK_REGISTER, TCO_MODEL_V0.  
**Ready:** no invented precise number without input basis.

## S31 — PoC Hypotheses & Experiment Plan

**Цель:** определить что действительно надо проверить экспериментом.

**Методы:** hypothesis→setup→metric→success/failure threshold→decision impact.  
**Выходы:** POC_PLAN.  
**Ready:** PoC is bounded and cannot silently become production code.

## S32 — PoC Evidence & Feasibility Gate

**Цель:** собрать experimental evidence и решить, можно ли проектировать дальше.

**Выходы:** POC_REPORT(s), DELIVERY_FEASIBILITY_DECISION.  
**Ready:** evidence affects requirements/options/estimate explicitly.

---

# A7 — Architecture Drivers & Options

## S33 — Architecture Drivers

**Цель:** выделить малый набор факторов, реально определяющих архитектуру.

**Методы:** requirements/NFR/risk/context synthesis, Richards/Ford characteristic discovery.  
**Выходы:** ARCHITECTURE_DRIVER_SET.  
**Ready:** each driver has evidence/trace.

## S34 — Architecture Option Generation

**Цель:** создать несколько feasible solution concepts.

**Методы:** pattern catalogue, constraints, simplest-feasible baseline, option generation.  
**Выходы:** ARCHITECTURE_OPTION_SET.  
**Ready:** options differ materially; decorative alternatives rejected.

## S35 — Architecture Views

**Цель:** визуализировать options consistently.

**Методы:** C4 Context/Container; Component where beneficial; data/deployment/security overlays.  
**Выходы:** ARCHITECTURE_VIEWS.  
**Ready:** views derive from one model.

## S36 — Trade-off & Security Review

**Цель:** сравнить варианты по заранее заданным criteria.

**Методы:** weighted matrix only when weights justified, qualitative trade-off records, security review, cost/ops review.  
**Выходы:** OPTION_TRADEOFF_MATRIX, OPTION_SECURITY_REVIEW.  
**Ready:** benefits/costs/risks/unknowns explicit.

---

# A8 — Architecture Verification & Decision

## S37 — CTO / Independent Challenge

**Цель:** независимо попытаться опровергнуть preferred option.

**Методы:** skeptical review, ATAM-like scenarios, failure modes, alternative challenge.  
**Выходы:** INDEPENDENT_REVIEW_RECORD, open questions.  
**Ready:** material objections resolved or preserved.

## S38 — ADR & Target Architecture

**Цель:** зафиксировать решение, контекст, alternatives, consequences.

**Методы:** ADR lifecycle.  
**Выходы:** ARCHITECTURE_DECISION_RECORDS, TARGET_ARCHITECTURE.  
**Ready:** final authority approves; architect cannot self-certify material decision.

## S39 — Residual Risk & Decision Evidence

**Цель:** зафиксировать что остаётся неустранённым и почему решение допустимо.

**Выходы:** RESIDUAL_RISK_REGISTER, DECISION_EVIDENCE_REGISTER.  
**Ready:** Risk Owner handles residual risk acceptance.

---

# A9 — Detailed Design

## S40 — Component Decomposition

**Цель:** разложить target architecture до bounded components/responsibilities.

**Методы:** C4 Component, cohesion/coupling analysis, responsibility allocation.  
**Выходы:** COMPONENT_DESIGN.  
**Ready:** components have homes/boundaries/contracts.

## S41 — API / Event / Integration Contracts

**Цель:** описать внешние и внутренние interfaces before implementation.

**Методы:** OpenAPI/AsyncAPI/schema design, compatibility rules, timeout/retry/idempotency semantics.  
**Выходы:** API_CONTRACTS, EVENT_SCHEMAS, INTEGRATION_CONTRACTS.  
**Ready:** contracts versioned and testable.

## S42 — Data Model, Pipeline & Lineage

**Цель:** описать data entities, transformations, stores and lineage.

**Методы:** conceptual/logical model, ETL/ELT/stream design, lineage graph, retention/classification propagation.  
**Выходы:** DATA_MODEL, DATA_PIPELINE_DESIGN, LINEAGE_MODEL.  
**Ready:** source→derived object trace exists.

## S43 — IAM & Secrets Design

**Цель:** определить identities, privileges, trust and secret lifecycle.

**Методы:** least privilege, role/attribute access model, secrets lifecycle.  
**Выходы:** IAM_MODEL, SECRETS_MODEL.  
**Ready:** privileged actions have explicit authority.

## S44 — Deployment Topology

**Цель:** описать runtime/deployment units, zones, networks and dependencies.

**Методы:** deployment view, environment separation, infrastructure boundary model.  
**Выходы:** DEPLOYMENT_DESIGN.  
**Ready:** deployment is traceable to architecture/NFR/security.

## S45 — Observability & SLO Design

**Цель:** заранее определить как увидим здоровье/деградацию.

**Методы:** signals, SLIs/SLOs, logging/metrics/tracing/event model.  
**Выходы:** OBSERVABILITY_DESIGN, SLO_DRAFT.  
**Ready:** critical NFRs have observable signals.

## S46 — Sizing / Capacity / HA-DR Design

**Цель:** рассчитать resource envelope and recovery strategy.

**Методы:** workload model, queueing/bottleneck reasoning, capacity margins, RTO/RPO, failure-domain analysis.  
**Выходы:** SIZING_MODEL, HA_DR_DESIGN.  
**Ready:** numbers have stated assumptions and test plan.

## S47 — Threat Model v1/v2 & Security Control Design

**Цель:** обновить threat model по реальной architecture/design.

**Методы:** trust-boundary refinement, control mapping, attack-path review.  
**Выходы:** THREAT_MODEL_V1_V2, SECURITY_CONTROL_PROFILE.  
**Ready:** material threats have control/test intent or accepted risk owner.

## S48 — Test Strategy & Detailed Test Specifications

**Цель:** закончить verification design before implementation.

**Методы:** test pyramid by requirement/risk, negative/security/performance/AI eval design.  
**Выходы:** TEST_STRATEGY, TEST_SPECIFICATIONS, SECURITY_TEST_PLAN, PERFORMANCE_TEST_PLAN, AI_EVAL_PLAN.  
**Ready:** critical paths have oracles and planned evidence.

---

# A10 — Implementation Plan

## S49 — Implementation / IaC / CI-CD / MLOps Plan

**Цель:** превратить design в контролируемый delivery plan.

**Методы:** WBS refinement, build pipeline design, IaC design, MLOps lifecycle where applicable.  
**Выходы:** IMPLEMENTATION_PLAN, IaC_PLAN, CI_CD_DESIGN, MLOPS_DESIGN, CONFIGURATION_IDENTIFICATION_PLAN.  
**Ready:** work packages trace to design/tests.

## S50 — Pre-Code Evidence Gate

**Цель:** формально решить, достаточно ли анализа для product-path implementation.

**Проверяет:** scope, system model, security, requirements/NFR, architecture, contracts, data/IAM/deployment, test oracles/specs, traceability, owner of residual UNKNOWN/risk.  
**Выход:** CODE_ALLOWED / REWORK / CONDITIONAL EXCEPTION.  
**Authority:** project/architecture governance per policy.  
**UI:** ярко выраженный gate node; models cannot approve.

---

# A11 — Implementation Baseline

## S51 — Source Code / Configuration / Model Assets

**Цель:** реализовать approved design.

**Входы:** CODE_ALLOWED + implementation plan.  
**Выходы:** SOURCE_CODE, configuration, migration/model assets.  
**Ready:** changes trace to work item/design requirement.

## S52 — Build / Dependencies / SBOM / Configuration Baseline

**Цель:** получить reproducible build and supply-chain identity.

**Методы:** dependency lock, SBOM, build manifest, config baseline.  
**Выходы:** BUILD_MANIFEST, DEPENDENCY_LOCK, SBOM, CONFIGURATION_BASELINE.  
**Ready:** artifact reproducible/identifiable.

## S53 — Code Review + Unit + SAST/SCA/Secrets

**Цель:** провести implementation-level verification before system tests.

**Выходы:** CODE_REVIEW_RECORDS, UNIT_TEST_RESULTS, SAST_RESULTS, SCA_RESULTS, SECRET_SCAN_RESULTS.  
**Ready:** material blockers resolved/accepted by proper authority.

---

# A12 — Verification / Validation

## S54 — Integration / System / Security / Performance / AI Test Execution

**Цель:** выполнить заранее спроектированные suites against baseline.

**Выходы:** INTEGRATION_TEST_RESULTS, SYSTEM_TEST_RESULTS, SECURITY_TEST_RESULTS, DAST/PENTEST evidence, PERFORMANCE_TEST_RESULTS, GENAI_EVAL_REPORT.  
**Ready:** test evidence version matches implementation baseline.

## S55 — Defect/Vulnerability Triage + Verification/Validation Reports

**Цель:** классифицировать failures, определить rework stage и сформировать release-candidate evidence.

**Методы:** root-cause routing, severity/prioritization, requirement coverage review.  
**Выходы:** DEFECT_REGISTER, VULNERABILITY_REGISTER, VERIFICATION_REPORT, VALIDATION_REPORT, ACCEPTANCE_TEST_RESULTS.  
**Ready:** RELEASE_CANDIDATE_READY or explicit return upstream.

---

# A13 — Release / Deployment

## S56 — Release / Migration / Rollback / Change Package

**Цель:** подготовить воспроизводимый controlled release.

**Выходы:** RELEASE_MANIFEST, RELEASE_NOTES, DEPLOYMENT_PLAN, MIGRATION_PLAN, ROLLBACK_PLAN, CHANGE_RECORD.  
**Ready:** rollback path and dependencies explicit.

## S57 — Operational Readiness & Deployment Evidence

**Цель:** доказать readiness и зафиксировать фактическое развертывание.

**Выходы:** OPERATIONAL_READINESS_REVIEW, DEPLOYMENT_EVIDENCE, monitoring/runbook baseline.  
**Ready:** PRODUCTION_READY requires human authority.

---

# A14–A15 — Operation & Evolution

## S58 — Operation / Incidents / Cost / Drift / Evolution

**Цель:** замкнуть цикл фактическими production data.

**Входы:** telemetry, SLO, incidents, vulnerabilities, cost, AI quality/drift, user/business feedback.  
**Методы:** SLO error-budget reasoning, incident/problem analysis, FinOps, drift/quality monitoring, architecture health review, technology radar.  
**Выходы:** RUNBOOKS, SLO/SLA actuals, INCIDENT_RECORDS, PROBLEM_RECORDS, CAPACITY_REPORTS, SECURITY_MONITORING_REPORTS, COST_REPORTS, AI_QUALITY_DRIFT_REPORTS, ARCHITECTURE_HEALTH_REVIEW, TECHNOLOGY_RADAR, CHANGE_REQUESTS.  
**Ready:** change routes to smallest required upstream station.

---

# A16 — Retirement

## S59 — Controlled Retirement

**Цель:** безопасно завершить lifecycle системы/версии/provider integration.

**Методы:** dependency closure, data disposition, access revocation, archive/knowledge capture, retirement verification.  
**Выходы:** RETIREMENT_PLAN, DATA_DISPOSITION_PLAN, ACCESS_REVOCATION_RECORD, ARCHIVE_PACKAGE, DEPENDENCY_DECOMMISSION_RECORD, RETIREMENT_VERIFICATION_REPORT, LESSONS_LEARNED.  
**Ready:** RETIRED_VERIFIED.

---

# 2. Визуальное правило станции

Каждая Sxx-station на canvas обязана показывать в compact mode:

```text
Sxx  Name
[status icon] [owner]
IN n   OUT n
! blockers n
```

Expanded card добавляет:

- local ready rule;
- unresolved UNKNOWN/conflicts;
- tests/evidence count;
- last material change;
- downstream stale count.

Double-click открывает Z2 internals.

---

# 3. Station categories

Для palette/filters станции классифицируются:

- SOURCE;
- PRODUCT;
- BUSINESS_ANALYSIS;
- SECURITY_LEGAL_DATA;
- SYSTEM_ENGINEERING;
- THREAT_MODELING;
- REQUIREMENTS;
- FEASIBILITY;
- ARCHITECTURE;
- DETAILED_DESIGN;
- TEST_DESIGN;
- DELIVERY_PLAN;
- IMPLEMENTATION;
- VERIFICATION;
- RELEASE;
- OPERATIONS;
- EVOLUTION;
- RETIREMENT.

---

# 4. Station execution semantics

В manual-first режиме station не “выполняется” автоматически. Она имеет lifecycle:

```text
LOCKED
→ AVAILABLE
→ IN_PROGRESS
→ OWNER_REVIEW
→ REVIEW
→ READY
→ VERIFIED/GATE_PASSED
```

Дополнительные состояния:

`BLOCKED`, `CONFLICTED`, `STALE`, `NOT_APPLICABLE`, `REWORK`.

Station становится `AVAILABLE`, когда выполнены минимальные input conditions.

Station может быть открыта раньше для просмотра, но UI обязан показывать unmet prerequisites.

---

# 5. Automation mapping rule

Будущая automation привязывается **внутрь station**, а не заменяет station.

Например S25 Requirements Normalization может со временем иметь:

```text
L0 schema checks
→ L1 deterministic ambiguity rules
→ L2 similarity duplicate candidates
→ L3 specialist LLM draft
→ human requirements engineer review
```

Но внешний station contract `inputs → outputs → owner → ready rule` остаётся стабильным.

---

# 6. Change/rework rule

Если downstream test/operation выявляет дефект, система не возвращает весь проект в S00. Impact engine ищет минимальную upstream cause-set.

Пример:

```text
S54 performance FAIL
  ├─ wrong NFR → S26/S28
  ├─ wrong estimate/workload → S29/S30/S46
  ├─ architecture bottleneck → S33–S39
  ├─ detailed design → S40–S48
  └─ implementation defect → S51–S53
```

Это правило является обязательным для визуального сценария rework.