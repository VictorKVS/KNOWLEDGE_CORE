# Техническое задание
# FATHER Visual Engineering Workbench

**Версия:** `DRAFT_V0.1`  
**Статус:** `CANDIDATE / FOR REVIEW / IMPLEMENTATION NOT YET AUTHORIZED`  
**Класс продукта:** визуальная инженерная среда проектирования, анализа, верификации и сопровождения software/AI-систем  
**Основной принцип:** `analysis-first / code-last / evidence-driven / human-authority-bound`

---

# 1. Назначение документа

Настоящее ТЗ определяет требования к FATHER Visual Engineering Workbench — интерактивной системе, в которой проектировщик должен видеть весь жизненный цикл системы как **живой инженерный чертёж**, а не как набор разрозненных документов, таблиц и страниц.

FATHER должен стать для системного/solution/security/AI-архитектора тем же классом рабочего инструмента, которым CAD/BIM является для архитектора здания:

- виден объект проектирования целиком;
- видны входы, выходы, связи и зависимости;
- каждый крупный блок можно раскрыть;
- каждое инженерное решение связано с доказательствами;
- изменение одного элемента показывает downstream impact;
- требования связаны с архитектурой;
- угрозы связаны с security controls;
- controls связаны с tests;
- tests связаны с evidence;
- архитектура связана с реализацией и эксплуатацией;
- ни одна модель/LLM не получает полномочия, которых нет у соответствующей роли.

Цель ТЗ — описать продукт достаточно строго, чтобы по нему можно было:

1. сформировать архитектурные решения;
2. декомпозировать реализацию на backlog;
3. построить data/API contracts;
4. подготовить UI/UX design system;
5. разработать тесты **до** продуктового кода;
6. реализовать MVP без скрытого изменения смысла;
7. в дальнейшем безопасно подключить LLM/Model Zoo только к явно разрешённым точкам.

---

# 2. Источники требований

## 2.1 Канонические источники FATHER

Система должна быть визуальной проекцией над следующими каноническими моделями, а не отдельной истиной:

- `FATHER_PAPER_PIPELINE_ALGORITHM.md`;
- `FATHER_PAPER_PIPELINE.yaml`;
- `FATHER_ARTIFACT_REGISTRY.yaml`;
- `FATHER_ROLE_MATRIX.yaml`;
- `ARTIFACT_DEPENDENCY_MATRIX.yaml`;
- `GATE_AUTHORITY_MATRIX.yaml`;
- `EXCEPTION_REWORK_MODEL.yaml`;
- `PROCESSING_METHOD_CATALOG.yaml`;
- `ALGORITHM_DESIGN_STANDARD.md`;
- `ANALYSIS_FIRST_ENGINEERING_POLICY.md`;
- `PRE_CODE_EVIDENCE_GATE.yaml`;
- `ROLE_COMPETENCY_MATURITY_MODEL.yaml`;
- `NORMATIVE_SOURCE_REGISTRY.yaml`;
- `SOURCE_ARTIFACT_MAPPING.yaml`.

## 2.2 Профессиональные источники и UX-паттерны

В качестве UX/interaction reference используются проверенные идеи следующих классов инструментов:

- Ardoq — data-driven architecture repository, components/relationships, multi-view modeling;
- KNIME — workflow nodes, components/metanodes, typed ports, execution state;
- Node-RED — palette/workspace/sidebar/navigation/subflows;
- BPMN/bpmn-js — user tasks, gateways, human approvals, process rendering/editing;
- Structurizr/C4 — one model / many architecture views;
- React Flow — web canvas, custom nodes, handles, nested flows;
- CAD/BIM tools — zoom hierarchy, object inspector, layers/perspectives, selection/context preservation.

Конкурентный UX не является нормативной истиной. Заимствуется только подход, который улучшает читаемость, трассируемость и управляемость FATHER.

---

# 3. Продуктовое видение

## 3.1 Краткое определение

FATHER Visual Engineering Workbench — это интерактивная визуальная среда, которая отображает инженерный проект как типизированный граф:

```text
SOURCE / NEED
   ↓
FACTS / REQUIREMENTS / CONSTRAINTS
   ↓
ENGINEERING TRANSFORMATIONS
   ↓
MODELS / DECISIONS / CONTRACTS
   ↓
TEST ORACLES / TESTS / EVIDENCE
   ↓
IMPLEMENTATION / RELEASE / OPERATION
   ↓
FEEDBACK / CHANGE / EVOLUTION
```

## 3.2 Основная метафора

Каждая рабочая станция должна выглядеть как инженерный black box:

```text
INPUT PORTS  →  ENGINEERING STATION  →  OUTPUT PORTS
                       │
                       ▼
                 OPEN INTERNALS
                       │
                       ▼
      checks → algorithms → evidence → review → tests
```

## 3.3 Ключевой результат для пользователя

Проектировщик должен за секунды отвечать на вопросы:

- что сейчас проектируется;
- на какой стадии находится проект;
- что блокирует следующий шаг;
- откуда взялось конкретное требование;
- кто его владелец;
- какие документы/источники его подтверждают;
- какой риск/угроза породили security requirement;
- каким контролем закрывается требование;
- каким тестом доказано выполнение;
- какое решение было принято и почему;
- что изменится, если поменять этот элемент;
- какие downstream-артефакты станут stale;
- где остались UNKNOWN/CONFLICTED;
- кто имеет полномочия подтвердить gate;
- можно ли уже писать product-path код;
- чем production отличается от текущего проекта/PoC.

---

# 4. Принципы продукта

## PR-001 — One canonical model

Один инженерный объект существует один раз и может быть показан во множестве представлений. Нельзя создавать независимую копию Requirement только потому, что он отображается в Security View и Architecture View.

## PR-002 — UI is projection

UI не является самостоятельным источником инженерной истины. Любое изменение должно сериализоваться в каноническую модель.

## PR-003 — Simplicity first

Сначала используется минимальный достаточный механизм. Не вводить message broker, graph DB, workflow engine, agent swarm или vector store до появления доказанной необходимости.

## PR-004 — Analysis first / code last

Основная неопределённость должна быть снята до реализации. Код продуктового пути разрешается только после `PRE_CODE_EVIDENCE_GATE`.

## PR-005 — Evidence before confidence

`confidence` модели, человека или reviewer не заменяет evidence.

## PR-006 — Unknown is valid state

`UNKNOWN` является допустимым инженерным состоянием. UI не должен вынуждать пользователя заполнять неизвестное выдуманным значением.

## PR-007 — Human authority is explicit

Gate, legal applicability, residual risk, product scope, production release и другие полномочия закрываются только уполномоченной ролью.

## PR-008 — Trace everything material

Материальные decisions должны иметь обратную и прямую трассировку.

## PR-009 — Views do not duplicate truth

Lifecycle/Security/Data/Cost/Compliance/Architecture views — фильтры и проекции одного графа.

## PR-010 — Change invalidates downstream deliberately

При изменении upstream объекта система обязана вычислить impact и явно перевести зависимые объекты в `STALE/PARTIAL/BLOCKED`, а не скрыто считать их актуальными.

---

# 5. Границы продукта

## 5.1 В scope

Система должна поддерживать:

- проекты greenfield/brownfield/hybrid;
- проектный intake;
- source/evidence registry;
- pipeline A0–A16;
- детальные станции S00–S59;
- canonical artifacts;
- live graph canvas;
- typed ports/edges;
- inspector;
- drill-down black boxes;
- multiple perspectives;
- architecture views;
- requirement/security/test traceability;
- approvals/gates;
- role/authority model;
- history/version/diff;
- impact analysis;
- test design before code;
- evidence/status dashboards;
- import/export;
- Git-friendly representation;
- audit;
- future AI-assistance integration points;
- read-only/projector mode;
- manual-first execution of paper pipeline;
- controlled future automation.

## 5.2 Не входит в первый MVP

- полноценный low-code application builder;
- IDE замена VS Code/JetBrains;
- собственная СУБД;
- собственный BPMN engine;
- собственный graph database;
- автономный AI project manager;
- автоматическое legal decision-making;
- автоматическое принятие residual risk;
- автоматический production release;
- автоматическая генерация продукта «по одному prompt»;
- realtime collaborative whiteboard уровня Figma как обязательное требование MVP;
- замена специализированных CASE/CAD/CI/CD/security tools.

---

# 6. Целевые пользователи

## U-01 Project/Product Owner

Нужен обзор value/scope/gates/risks/progress и точки принятия решений.

## U-02 Business Analyst

Нужны business need, processes, journeys, glossary, requirements, gaps/conflicts.

## U-03 System Engineer

Нужны context, boundary, functions, data flows, interfaces, dependencies, operating modes.

## U-04 Security Engineer

Нужен путь `asset/interest → consequence → source → boundary → threat scenario → requirement → control → test → residual risk`.

## U-05 Requirements Engineer

Нужны requirement baselines, NFR, acceptance criteria, RTM, change impact.

## U-06 Solution/Software Architect

Нужны drivers, C4, options, trade-offs, ADR, components, contracts, deployment, sizing.

## U-07 QA / Verification Engineer

Нужны oracles, test design, coverage, requirement-to-test mapping, evidence.

## U-08 DevSecOps / Platform

Нужны build/dependency/SBOM/config/security scan/release/deployment contracts.

## U-09 Operations/SRE

Нужны observability, SLO, capacity, incident, DR, runbooks, feedback.

## U-10 Legal/Compliance/Data Owner/Risk Owner

Нужны authority-bound views, applicability, classification, obligations, decisions and approval forms.

## U-11 Reviewer / CTO / Skeptical Reviewer

Нужны alternatives, conflicts, hidden assumptions, evidence strength, diff, decision packet.

## U-12 Future AI role-agent

Получает только явно разрешённые inputs, методы, evidence и authority boundary. Визуально показывается как помощник внутри операции, а не владелец жизненного цикла.

---

# 7. Уровни визуального масштаба

## Z0 — Lifecycle map

Показывает A0–A16 и основные gates.

Цель: руководитель/архитектор за 10–20 секунд понимает состояние всего проекта.

Обязательная информация на macro-node:

- stage ID/name;
- completion state;
- blocking count;
- unresolved P0/P1;
- owner;
- exit gate;
- % artifact readiness (информационный показатель, не автоматический gate);
- last material change;
- downstream impact when stale.

## Z1 — Detailed station conveyor

Показывает S00–S59.

Каждая station должна быть ограниченной инженерной трансформацией:

```text
known inputs
→ bounded operation
→ explicit outputs
→ local readiness criterion
```

## Z2 — Station internals

Показывает внутреннюю структуру выбранной station:

- deterministic checks;
- input validation;
- source lookup;
- data mapping;
- algorithm/method;
- candidate output;
- conflict/gap checks;
- human/role review;
- tests;
- output publication.

В будущем здесь отображается AI-assistance, если она разрешена.

---

# 8. Основной экран

## UX-FR-001 — Three-column engineering layout

Desktop layout по умолчанию:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Project | Stage | Gate | Perspective | Search | History | Compare | Help    │
├──────────────┬─────────────────────────────────────┬─────────────────────────┤
│ PALETTE      │               CANVAS                │ INSPECTOR               │
│              │                                     │                         │
│ Sources      │                                     │ selected object         │
│ Product      │      INPUT → NODE → OUTPUT          │ overview                │
│ System       │                    │                │ inputs/outputs          │
│ Security     │                    ▼                │ evidence                │
│ Requirements │              [subgraph]             │ algorithm               │
│ Architecture │                                     │ refs/tests/gates        │
│ Testing      │                                     │ people/history          │
│ Delivery     │                                     │                         │
├──────────────┴─────────────────────────────────────┴─────────────────────────┤
│ Timeline | blockers | UNKNOWN | conflicts | stale | audit | scenario flow    │
└──────────────────────────────────────────────────────────────────────────────┘
```

## UX-FR-002 — Canvas must dominate

Canvas должен занимать большую часть экрана. Детали не должны постоянно уводить пользователя на отдельные страницы.

## UX-FR-003 — Inspector drawer

Обычный single click открывает/обновляет правый inspector без потери viewport.

## UX-FR-004 — Breadcrumb context

При drill-down пользователь всегда видит:

```text
Project > Macro Stage > Station > Internal Node
```

Возврат обязан восстанавливать zoom/pan/selection.

---

# 9. Взаимодействие с узлами

## UX-FR-010 Hover

Показывает краткую карточку:

- name/id;
- state;
- owner;
- main input/output count;
- blocker count;
- last change;
- gate effect.

Не должен открывать тяжёлую панель.

## UX-FR-011 Single click

Выбирает объект и открывает Inspector.

## UX-FR-012 Double click

Если node composite — провалиться внутрь.

Если atomic — открыть focused detail mode.

## UX-FR-013 Right click

Context menu зависит от role/authority и state. Возможные действия:

- Open;
- Trace upstream;
- Trace downstream;
- Show impact;
- Compare versions;
- Request owner input;
- Mark NOT_APPLICABLE;
- Create review task;
- Propose change;
- Run deterministic validation;
- Open test/evidence;
- Copy stable link;
- Export selected subgraph.

Запрещённые полномочия не должны показываться как обычное доступное действие.

## UX-FR-014 Edge click

Edge — самостоятельный engineering relationship. Inspector показывает:

- relation type;
- source/target;
- cardinality/contract if applicable;
- payload/port types;
- evidence;
- created by;
- version;
- validation rules;
- impact on deletion/change.

---

# 10. Node contract

Каждый node обязан иметь:

```text
nodeId
nodeType
name
stageId
stationId
purpose
inputPorts[]
outputPorts[]
ownerRole
reviewerRoles[]
authorityRule
methodRefs[]
algorithmRef
normativeRefs[]
professionalRefs[]
scientificRefs[]
evidenceRefs[]
testRefs[]
gateRefs[]
status
unknowns[]
conflicts[]
version
lastMaterialChange
downstreamConsumers[]
```

## FR-NODE-001 Stable identity

Node ID не должен меняться при простом переименовании display name.

## FR-NODE-002 Typed boundary

Любой composite node имеет явный boundary contract: inputs/outputs доступны снаружи, internals могут меняться без изменения boundary только при сохранении совместимости.

## FR-NODE-003 No invisible business logic

Если результат node зависит от правила/алгоритма, ссылка на него должна быть видима из Inspector.

## FR-NODE-004 Status is derived

UI status должен вычисляться из canonical state, а не храниться только как CSS/color.

---

# 11. Port type system

Минимальные типы портов:

- `SOURCE_EVIDENCE`;
- `SOURCE_VERSION`;
- `FACT`;
- `CLAIM`;
- `OWNER_INPUT`;
- `BUSINESS_NEED`;
- `SCOPE`;
- `REQUIREMENT`;
- `NFR`;
- `ACCEPTANCE_CRITERION`;
- `DATA_OBJECT`;
- `DATA_CLASSIFICATION`;
- `SYSTEM_CONTEXT`;
- `FUNCTION_MODEL`;
- `INTERFACE_CONTRACT`;
- `THREAT_SCENARIO`;
- `RISK`;
- `SECURITY_REQUIREMENT`;
- `ARCHITECTURE_DRIVER`;
- `ARCHITECTURE_OPTION`;
- `DECISION`;
- `ADR`;
- `COMPONENT_CONTRACT`;
- `API_CONTRACT`;
- `TEST_ORACLE`;
- `TEST_CASE`;
- `TEST_EVIDENCE`;
- `BUILD_EVIDENCE`;
- `RELEASE_EVIDENCE`;
- `SLO`;
- `COST`;
- `INCIDENT`;
- `FEEDBACK`;
- `AUTHORITY_DECISION`.

## FR-PORT-001 Type validation

Несовместимое соединение должно отклоняться до сохранения.

## FR-PORT-002 Mapping adapter

Явное преобразование типа допускается только через station/adapter, чтобы transformation не была невидимой.

## FR-PORT-003 Directionality

Каждый port имеет `input/output` и допустимые relation types.

## FR-PORT-004 Required/optional

Port должен знать обязательность для локального readiness.

---

# 12. Edge/relation model

Базовые relation types:

- `DERIVED_FROM`;
- `SUPPORTS`;
- `CONTRADICTS`;
- `REFINES`;
- `SUPERSEDES`;
- `REQUIRES`;
- `SATISFIES`;
- `IMPLEMENTS`;
- `MITIGATES`;
- `VERIFIED_BY`;
- `VALIDATED_BY`;
- `DEPENDS_ON`;
- `BLOCKS`;
- `OWNED_BY`;
- `REVIEWED_BY`;
- `APPROVED_BY`;
- `PRODUCES`;
- `CONSUMES`;
- `AFFECTS`;
- `TRIGGERS_REWORK`;
- `APPLIES_TO`;
- `EXEMPTS`;
- `CONFLICTS_WITH`.

Relation type обязан иметь semantics и допустимые endpoint classes.

---

# 13. Status model

Единый status vocabulary:

```text
EXPECTED
REQUESTED
RECEIVED
PARTIAL
CONFLICTED
GAP
DRAFT
OWNER_REVIEW
CONFIRMED
VERIFIED
STALE
BLOCKED
REJECTED
NOT_APPLICABLE
RETIRED
```

## FR-STATE-001 No hidden promotion

Переход `DRAFT → VERIFIED` без обязательных промежуточных authority/review evidence запрещён.

## FR-STATE-002 Stale propagation

Изменение material upstream объекта запускает impact analysis.

## FR-STATE-003 Conflict is visible

`CONFLICTED` нельзя автоматически преобразовать в `CONFIRMED` на основании majority vote моделей.

---

# 14. Inspector

Обязательные tabs:

1. `Overview`;
2. `Inputs / Outputs`;
3. `Evidence`;
4. `Fields`;
5. `Algorithm / Method`;
6. `Requirements / Risks`;
7. `Tests`;
8. `Gate / Authority`;
9. `People / Roles`;
10. `History / Diff`;
11. `Downstream Impact`;
12. `AI Assistance` — только при наличии разрешённой AI-функции.

## UX-FR-020 Overview

Показывает purpose, state, owner, current version, readiness summary, blockers.

## UX-FR-021 Evidence

Каждая материальная field/value должна позволять перейти к source locator.

## UX-FR-022 Algorithm

Показывает:

- problem;
- selected method;
- simplest baseline;
- assumptions;
- invariants;
- alternatives;
- correctness/adequacy evidence;
- failure modes;
- tests;
- references.

## UX-FR-023 History

Показывает semantic diff, а не только textual diff, где это возможно.

---

# 15. Perspectives / layers

Одна модель должна поддерживать следующие projections:

## P-01 Lifecycle

A0–A16 / S00–S59 / gates.

## P-02 Business

`need → user/process → requirement → value metric`.

## P-03 System

`actor/system → function → data flow → interface → dependency`.

## P-04 Security

`protected interest/asset → consequence → threat source → trust boundary → scenario → security requirement → control → test → residual risk`.

## P-05 Data

`source → classification → owner → transformation → lineage → store/index → use → retention/disposition`.

## P-06 Architecture

`driver → option → trade-off → ADR → component → interface/deployment`.

## P-07 Verification

`requirement/risk → oracle → test → result → defect → evidence`.

## P-08 Compliance

`normative source → clause → requirement → artifact field → control → evidence`.

## P-09 Operations

`component → telemetry → SLO → alert → incident/problem → feedback`.

## P-10 Cost

`decision/component/workload → resource → unit cost → TCO → actual spend`.

## P-11 Responsibility

`artifact/decision → owner → reviewers → authority`.

---

# 16. Dynamic Flow / scenario playback

## FR-FLOW-001 Scenario flow

Пользователь может создать/выбрать сценарий и пошагово проиграть путь по существующему графу.

Примеры:

- new requirement;
- security incident;
- failed performance test;
- source superseded;
- architecture option rejected;
- production rollback;
- data class changed;
- API contract change;
- model/provider change.

## FR-FLOW-002 Step mode

На каждом шаге подсвечиваются active nodes/edges и textual explanation.

## FR-FLOW-003 Impact mode

Показывает потенциально stale/blocked downstream nodes до применения change.

## FR-FLOW-004 No mutation during simulation by default

Simulation не меняет canonical project, пока пользователь явно не создаст Change Request.

---

# 17. Source and evidence management

## FR-SRC-001 Source registry

Каждый source имеет:

- stable ID;
- type;
- origin;
- owner/authority;
- version/date;
- hash where applicable;
- status/effective state;
- locator;
- classification;
- freshness policy;
- supersession relation.

## FR-SRC-002 Original preservation

Исходный source snapshot сохраняется отдельно от derived text/chunks/annotations.

## FR-SRC-003 Evidence locator

Любая extracted claim/requirement должна иметь resolvable locator.

## FR-SRC-004 Side-by-side evidence viewer

Пользователь должен видеть artifact field рядом с source fragment/document page.

## FR-SRC-005 Brownfield mapping

Перед созданием нового artifact система должна позволять искать существующие источники и показывать coverage.

---

# 18. Requirements management

## FR-REQ-001 Requirement object

Requirement является first-class entity, не строкой в Word.

Поля минимум:

- ID;
- statement;
- type;
- source;
- owner;
- rationale;
- priority;
- applicability;
- acceptance criterion;
- verification method;
- linked risk/threat;
- linked architecture element;
- linked test;
- status/version.

## FR-REQ-002 Bidirectional trace

Из requirement доступны upstream source и downstream decision/component/test.

## FR-REQ-003 Quality checks

Должны быть deterministic validators на ambiguity patterns, missing actor/action/condition/measure where applicable, duplicate/conflict candidates.

## FR-REQ-004 Baseline

Baseline является versioned set, а не просто статусом отдельных requirements.

---

# 19. Security engineering

## SEC-FR-001 Security as continuous perspective

Security включается с A2 и не является финальным audit-only этапом.

## SEC-FR-002 Threat graph

Поддержать canonical threat chain:

```text
asset/protected interest
→ negative consequence
→ threat source
→ trust boundary/entry point
→ scenario
→ security driver
→ requirement
→ architecture control
→ test
→ verification evidence
→ residual risk
```

## SEC-FR-003 Authority

Risk acceptance может оформить только назначенный Risk Owner.

## SEC-FR-004 Security test predesign

Security requirements должны иметь planned verification до product implementation.

## SEC-FR-005 AI security

Для будущих AI-assistance функций отображать data policy, provider eligibility, tool permissions, prompt/version and security eval state.

---

# 20. Architecture modeling

## FR-ARCH-001 One architecture model, many views

C4 Context/Container/Component/Dynamic/Deployment должны строиться из одного underlying model.

## FR-ARCH-002 Driver trace

Любой material architecture option должен ссылаться на drivers/NFR/risks.

## FR-ARCH-003 Alternatives mandatory

Для material decision должна существовать хотя бы одна реально рассмотренная альтернатива либо явное обоснование single feasible option.

## FR-ARCH-004 ADR integration

ADR связан с affected elements и evidence.

## FR-ARCH-005 Architecture health

Production feedback может инициировать architecture health review и reopen A7/A8/A9.

---

# 21. Testing and verification

## FR-TEST-001 Test oracle before code

Critical requirement должен иметь observable condition и oracle до `CODE_ALLOWED`.

## FR-TEST-002 Test as object

Test Case / Test Suite / Test Run / Test Evidence — отдельные сущности.

## FR-TEST-003 Coverage views

Показывать:

- requirements without tests;
- security controls without tests;
- tests without requirement/risk rationale;
- failed tests and impacted gates;
- stale test evidence.

## FR-TEST-004 GenAI eval

Для AI components поддержать versioned eval dataset, metric definitions, model/config identity, run evidence, adversarial/security cases.

---

# 22. Gate and approval model

## FR-GATE-001 Gate entity

Gate содержит:

- required evidence rules;
- owner/final authority;
- reviewers;
- blockers;
- allowed outcomes;
- decision record;
- timestamp/version.

## FR-GATE-002 Allowed outcomes

Минимум:

- PASS;
- CONDITIONAL_PASS;
- REWORK;
- BLOCKED;
- NOT_APPLICABLE where meaningful.

## FR-GATE-003 Human form

Authority decision выполняется через явную форму с evidence/rationale.

## FR-GATE-004 No UI-color approval

Зелёный node не является gate approval.

---

# 23. Search and navigation

## FR-SEARCH-001 Global search

Поиск по ID/name/text/type/source/owner/tag/status.

## FR-SEARCH-002 Command palette

Keyboard-first navigation:

- open node;
- jump station;
- change perspective;
- trace upstream/downstream;
- open source;
- compare versions.

## FR-SEARCH-003 Deep link

Любой material object имеет stable URL.

## FR-SEARCH-004 Graph neighborhood

Команда “focus neighborhood” показывает N-hop context без дублирования данных.

---

# 24. History, versioning and diff

## FR-VERSION-001 Immutable revision identity

Material revisions имеют immutable version/revision IDs.

## FR-VERSION-002 Semantic diff

Для structured object показывать:

- field changed;
- relation added/removed;
- owner/status change;
- evidence changed;
- test/gate impact.

## FR-VERSION-003 Baseline tagging

Project может фиксировать named baselines: requirements, architecture, release, production.

## FR-VERSION-004 Time travel read-only

Пользователь может открыть состояние проекта на выбранную baseline/time point.

---

# 25. Collaboration and review

## FR-COLLAB-001 Review tasks

Можно назначить review по node/subgraph/artifact/decision.

## FR-COLLAB-002 Comment with object anchor

Комментарий привязывается к object/field/relation/version.

## FR-COLLAB-003 Decision resolution

Комментарий не равен authority decision.

## FR-COLLAB-004 Presence optional

Realtime cursors/presence являются P2; асинхронная review-модель является P0/P1.

---

# 26. Import/export

## FR-IO-001 Import

В MVP предусмотреть ingestion/import для:

- Markdown;
- YAML/JSON;
- OpenAPI;
- CSV/XLSX structured mapping;
- Git repository metadata;
- file/document references;
- C4/Structurizr where feasible.

## FR-IO-002 Export

- Markdown/YAML/JSON canonical pack;
- static HTML/project report;
- Mermaid/PlantUML/Structurizr views;
- CSV matrix export;
- later DOCX/PDF Architecture Pack.

## FR-IO-003 Round-trip safety

Export/import не должен терять stable IDs и material relations.

---

# 27. Future AI assistance

AI не является обязательным для базового Workbench.

## AI-FR-001 Visible invocation point

AI работает только внутри конкретной operation/station.

## AI-FR-002 Frozen context

Каждый AI run хранит input snapshot refs, model/provider/version, prompt version, tool permissions, output and review result.

## AI-FR-003 Role capability

Модель выбирается по capability/task/domain maturity, а не по бренду.

## AI-FR-004 Human review

Candidate outputs остаются candidate до required review.

## AI-FR-005 Model Zoo

Zoo допускается только для mapped material decisions после paper-pipeline activation gate.

## AI-FR-006 Security

Prompt injection, retrieval poisoning, fabricated refs, authority escalation, data routing и tool misuse должны иметь security eval coverage.

---

# 28. Reference technical architecture

Это **исходный рекомендуемый baseline**, а не уже утверждённый ADR.

## 28.1 Frontend

- TypeScript;
- React;
- React Flow / XYFlow для graph canvas;
- собственный FATHER node/edge/port layer;
- component library/design tokens;
- state management с локальным cache + server truth;
- web workers для тяжёлых graph computations при необходимости.

## 28.2 Backend

- Python;
- FastAPI как reference HTTP/API boundary;
- application/service layer без UI-зависимости;
- deterministic validation engine;
- traceability/impact service;
- import/export service;
- future AI gateway behind interface.

## 28.3 Persistence

Принцип простоты:

- PostgreSQL — primary structured project store;
- JSONB допустим для extensible typed payloads, но core IDs/relations/statuses должны быть queryable;
- object storage/file layer для immutable source snapshots/large artifacts;
- relational adjacency/edge tables — сначала;
- отдельный graph DB только после доказанного query/performance need;
- PostgreSQL full-text/search сначала;
- отдельный search engine только после benchmark need;
- outbox/event table сначала;
- Kafka/another broker только после durable async/scale requirement.

## 28.4 Architecture views

- internal canonical model;
- Structurizr DSL/export adapter для C4;
- bpmn-js optional view для workflow/human approvals;
- Mermaid/PlantUML export for documentation.

---

# 29. Logical service boundaries

Минимальные bounded modules:

1. Project Service;
2. Source/Evidence Service;
3. Artifact Service;
4. Graph/Trace Service;
5. Requirement Service;
6. Security/Risk Service;
7. Architecture Service;
8. Test/Verification Service;
9. Gate/Authority Service;
10. Version/Diff Service;
11. Import/Export Service;
12. Search Service;
13. Audit Service;
14. AI Assistance Gateway — future/feature-gated.

В MVP это **не обязательно 14 микросервисов**. Допускается modular monolith с этими logical boundaries.

---

# 30. Non-functional requirements

Все численные значения ниже — `INITIAL DESIGN TARGET / TO BE BASELINED` и должны пройти benchmark до утверждения Production NFR.

## NFR-PERF-001 Canvas responsiveness

Цель MVP: интерактивное pan/zoom/select без заметной задержки на типовом Z1-представлении. Benchmark profile должен включать не менее 500 одновременно видимых nodes/edges aggregate order >1000 elements.

## NFR-PERF-002 Large project

Архитектура данных не должна ограничивать проект несколькими сотнями объектов. Initial target: десятки тысяч canonical objects на проект при использовании фильтров/virtualization.

## NFR-PERF-003 Inspector open

Cached object inspector target: perceived response <300 ms; server fetch target p95 <1 s в типовой локальной/корпоративной среде — provisional.

## NFR-SEARCH-001 Search

Target p95 <2 s для initial representative corpus. Подтверждается benchmark.

## NFR-AVAIL-001 Recoverability

Для self-hosted deployment должны существовать backup/restore procedure и verified restore test before Production.

## NFR-SEC-001 Least privilege

Все write/approve действия проходят server-side authorization.

## NFR-SEC-002 Auditability

Материальные изменения, approvals, risk acceptance, baseline promotion и AI runs имеют audit trail.

## NFR-SEC-003 Secure defaults

External AI/provider use disabled for data classes without explicit approval.

## NFR-USABILITY-001 Progressive disclosure

Начальный экран не показывает всю сложность Z2. Детали открываются по demand.

## NFR-USABILITY-002 Keyboard support

Основные navigation/actions доступны с клавиатуры.

## NFR-A11Y-001 Accessibility

UI проектируется с учетом WCAG 2.2 AA where feasible; status нельзя кодировать только цветом.

## NFR-I18N-001 Localization

Модель хранит identifiers отдельно от локализованного display text. RU primary, EN support planned.

## NFR-MAINT-001 Model migrations

Schema/version migrations должны быть явными, тестируемыми и reversible/backup-safe.

## NFR-OBS-001 Observability

Backend/critical frontend operations имеют structured logs, request/trace correlation, errors and performance telemetry.

---

# 31. Authorization model

Начальный подход:

- RBAC по role;
- ABAC/conditions по project, data class, object type, authority assignment;
- distinct permissions: view/edit/review/approve/accept-risk/admin/export-sensitive;
- authority action требует current assignment, а не просто generic role membership.

Примеры:

- Security Engineer может создавать Security Risk, но не принимать residual risk без Risk Owner authority;
- Architect может создавать ADR candidate, но не self-approve material architecture;
- AI может draft/review, но не получает human authority;
- Project Owner может принять scope, но не автоматически legal applicability.

---

# 32. Audit

Audit event минимум:

```text
eventId
projectId
actorId / actorType
roleContext
action
objectRef
objectVersionBefore
afterVersionRef
reason/rationale
source/evidence refs where material
timestamp
client/session correlation
AI run ref if applicable
```

Audit trail append-only at application semantics level.

---

# 33. Error and exception UX

Ошибки должны быть engineering-readable.

Запрещено:

- `Something went wrong` без correlation/context;
- потеря unsaved structured edit без предупреждения;
- молчаливое игнорирование invalid relation;
- automatic conflict overwrite.

Для blocked station UI показывает:

- что именно отсутствует;
- кто owner;
- какой upstream object нужен;
- почему это blocker;
- какое действие доступно;
- какой downstream impact.

---

# 34. Greenfield mode

При новом проекте система:

1. создаёт project shell;
2. показывает Z0;
3. активирует S00 Intake;
4. предлагает minimal required input;
5. последовательно раскрывает stations по dependency readiness;
6. не создаёт декоративные документы заранее;
7. показывает expected artifacts as empty contracts, а не заполненные шаблоны.

---

# 35. Brownfield mode

При существующем проекте приоритет другой:

```text
existing materials
→ ingest/map
→ coverage
→ conflicts/stale
→ missing fields
→ only then create new artifacts
```

UI должен показывать процент/состояние coverage **по полям/обязательным сведениям**, а не по наличию файлов.

---

# 36. Project dashboard

Dashboard не заменяет canvas.

Минимальные widgets:

- current gate;
- blockers;
- unresolved UNKNOWN/CONFLICTED;
- stale impact;
- decisions awaiting authority;
- test coverage gaps;
- security residual risks;
- source freshness warnings;
- recent material changes;
- upcoming review tasks.

---

# 37. Design system requirements

## UX-DS-001 Status colors + icons

Каждый статус имеет цвет + shape/icon/text.

## UX-DS-002 Node anatomy consistent

Node layout одинаков на всех stages, различается content/icon/category, а не фундаментальная структура.

## UX-DS-003 Density modes

- Compact — large graphs;
- Standard;
- Review — more metadata visible.

## UX-DS-004 Dark/light

Поддержка dark/light должна быть предусмотрена design tokens, но не блокировать MVP.

---

# 38. Undo/redo and transactions

## FR-EDIT-001 Local editing session

Structured edits выполняются в draft transaction.

## FR-EDIT-002 Validation before commit

Перед сохранением server validates schema, types, authorization, relation constraints.

## FR-EDIT-003 Undo

UI undo для локального draft; committed revision отменяется через new compensating revision, не history deletion.

---

# 39. Notifications

Только material notifications:

- owner input requested;
- review assigned;
- gate decision required;
- source superseded;
- upstream change made my object stale;
- test/security evidence failed;
- risk acceptance expiring/review required.

Не строить шумный social feed.

---

# 40. Plugin/extension boundary

Будущие adapters могут подключать:

- GitHub/GitLab;
- Jira/issue trackers;
- CI systems;
- scanners;
- document stores;
- SIEM/observability;
- model providers;
- regulatory repositories;
- Structurizr;
- BPMN engines.

Plugin не может обходить canonical authority/audit rules.

---

# 41. Acceptance of visual concept

Visual MVP принимается, если пользователь может вручную выполнить сценарий:

```text
create/open project
→ see Z0
→ enter S00
→ attach source
→ map evidence to an artifact field
→ see missing input
→ assign owner request
→ navigate to requirement
→ trace to architecture decision
→ trace to test oracle
→ open a black box
→ see algorithm + evidence
→ change upstream input
→ see downstream stale impact
→ open Security perspective
→ open Compliance perspective
→ compare two revisions
→ perform human gate decision
→ return to same canvas context
```

---

# 42. Quality gates for implementation

## WG-0 Specification Ready

- master TZ reviewed;
- station catalogue reviewed;
- data model reviewed;
- UX interaction reviewed;
- security authority reviewed;
- acceptance tests drafted.

## WG-1 Read-only Prototype

- project graph load;
- Z0/Z1;
- inspector;
- perspectives;
- stable links;
- no write authority.

## WG-2 Structured Editing

- typed nodes/edges;
- draft/validation;
- versioning;
- audit.

## WG-3 Evidence & Traceability

- source viewer;
- artifact mapping;
- upstream/downstream trace;
- impact/stale.

## WG-4 Gates/Reviews/Tests

- review tasks;
- authority forms;
- test/oracle model;
- gate evidence.

## WG-5 Production-grade Workbench

- security hardening;
- performance;
- backup/restore;
- observability;
- accessibility;
- migration;
- integration adapters.

## WG-6 AI Assistance

Только после отдельного activation decision.

---

# 43. Forbidden implementation shortcuts

Запрещено:

1. хранить canonical project только в frontend state;
2. использовать diagram JSON как единственный engineering source of truth;
3. делать status только визуальным цветом;
4. хранить approvals как comments;
5. смешивать role и authority;
6. создавать independent copies одного requirement для разных views;
7. делать AI-generated evidence;
8. считать file presence = artifact completeness;
9. скрывать UNKNOWN;
10. автоматически принимать модельное majority vote как decision;
11. вводить микросервисы без NFR/операционного основания;
12. вводить Kafka/graph DB/vector DB без benchmark/use case;
13. писать product code до прохождения соответствующего pre-code gate;
14. делать UI-only поля, которые нельзя экспортировать/версионировать;
15. терять history при edit/delete.

---

# 44. Definition of Done для любого feature

Feature не `DONE`, пока нет:

- requirement ID;
- UX behavior where applicable;
- data model impact;
- authorization impact;
- audit impact;
- error behavior;
- tests;
- documentation;
- migration/backward compatibility assessment;
- security review for material features;
- trace to this TZ.

---

# 45. Итоговое определение продукта

FATHER Visual Engineering Workbench должен стать не «сайтом с блок-схемой» и не «LLM-обёрткой», а инженерной средой, где визуально соединены:

```text
source
→ fact
→ requirement
→ system model
→ threat/risk
→ decision
→ architecture
→ contract
→ test oracle
→ test
→ evidence
→ implementation
→ release
→ operation
→ feedback
```

Сложность скрывается прогрессивно, но не исчезает: любой black box раскрываем, любой material output объясним, любой material decision трассируем, любой gate имеет authority и evidence.

Это является базовым контрактом для всех приложений данного ТЗ и будущей реализации.