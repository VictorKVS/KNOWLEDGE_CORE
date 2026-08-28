# FATHER Knowledge Factory — Analytics Stage 02

Document ID: `FATHER-KF-ANALYTICS-0002`
Package: `PACKAGE_01_FOUNDATION`
Status: `DRAFT_FOR_REVIEW`
Owner: `FATHER Analyst`
Upstream: `01_PRODUCT_DOCUMENT.md`, `02_ANALYTICS_STAGE_01.md`
Next gate: `03_ARCHITECTURE`

## 1. Базовая версия оценки

| Параметр | Значение |
|---|---|
| Базовая версия | `БФТ-FATHER-KF-001 v0.1` |
| Точность оценки | Диапазон, не календарная дата |
| Плановый режим | `T&M with a cap` как модель управления R&D-объёмом |
| Пересчёт | После `corpus profiling` и PoC-телеметрии |
| Baseline | Ручной процесс, 1 поток |
| Прогноз завершения | Только после фактической телеметрии |

До profiling запрещено публиковать точный срок, бюджет или ускорение как факт.

## 2. Delivery roadmap

Проект не переходит в Production одним шагом. Каждый уровень должен купить новый тип доказательства.

| Этап | Что доказываем | Основной артефакт | Ответственные роли | Статус |
|---|---|---|---|---|
| 1. Discovery | Корпус, baseline, NFR, риски, критерии | `PROFILE-001`, `GOLDEN-SET-001`, `BASELINE-001` | Analyst + Architect | NEXT |
| 2. PoC | Технический путь `ingest -> claim -> evidence -> knowledge` | `POC-001`, `EVAL-001` | ML/Backend + Analyst | PLANNED |
| 3. MVP | Рабочий конвейер, граф, workspace, отчёт | `MVP-001` | Backend + ML + Frontend | BLOCKED_BY_POC |
| 4. Pilot | Работа в ограниченном реальном процессе | `PILOT-001` | Product + Analyst + Ops | FUTURE |
| 5. Production | ИБ, нагрузка, мониторинг, эксплуатация, SLO/DR | `PROD-GATE-001`, `PROD-001` | DevOps/SRE + QA + Security | FUTURE |

## 3. Discovery — рабочий проход

### Входы

- Product Plan / Product Document;
- несколько открытых и допустимых к обработке документов;
- golden set вопросов, фактов и ожидаемых доказательств;
- baseline ручного поиска/разбора;
- текущие FR/NFR и ограничения;
- правила допустимого использования источников.

### Действия

1. Загрузить оригиналы без изменения исходных файлов.
2. Вычислить SHA-256 и зарегистрировать source identity.
3. Выполнить corpus profiling.
4. Определить долю native PDF / scan / mixed / tables / code / images.
5. Извлечь фрагменты и claims-кандидаты.
6. Подтвердить golden facts человеком.
7. Измерить ручной baseline на тех же задачах.
8. Сравнить полноту, ошибки, evidence coverage и elapsed time.
9. Зафиксировать неизвестные и пересчитать диапазон оценки.

### Основные риски Discovery

- ложноположительные claims;
- хороший по форме ответ без доказательства;
- нерепрезентативный корпус;
- смешение исходного текста, перевода и интерпретации;
- недостаточная трассировка до источника.

## 4. Corpus profiling contract — PROFILE-001

До оценки сроков и стоимости должны быть измерены как минимум:

- количество документов;
- общий объём байт;
- число страниц;
- распределение форматов;
- доля PDF с native text;
- доля scanned PDF;
- доля mixed PDF;
- доля страниц с таблицами;
- доля страниц с кодом/формулами;
- языки;
- OCR confidence distribution;
- среднее и p95 число фрагментов на документ;
- среднее и p95 число claims-кандидатов на документ;
- доля материала, требующего ручной проверки;
- доля файлов с ошибками извлечения.

Результат PROFILE-001 является входом архитектора для sizing, pipeline topology и storage decisions.

## 5. Golden set — GOLDEN-SET-001

Golden set содержит не только вопросы и ответы, но и доказательства.

Для каждой задачи фиксируются:

- `golden_id`;
- вопрос/задача;
- ожидаемый факт/утверждение;
- допустимые варианты формулировки;
- обязательный source document;
- exact locator / page / section / block;
- ожидаемый evidence fragment;
- ожидаемые связи;
- forbidden unsupported conclusions;
- human reviewer;
- revision/date.

Проверяется не только semantic answer quality, но и `evidence correctness`.

## 6. Baseline — BASELINE-001

Baseline: один человек / один поток / ручной процесс на том же корпусе и golden set.

Измеряем:

- время поиска;
- время проверки;
- число просмотренных документов;
- полноту найденных фактов;
- ложные выводы;
- пропущенные факты;
- долю утверждений с точным evidence;
- количество повторной работы.

Автоматизированный поток сравнивается только с сопоставимым baseline.

## 7. Модель оценки срока

Для одной R&D-задачи допускается PERT-модель:

`E = (O + 4M + P) / 6`

где:

- `O` — optimistic;
- `M` — most likely;
- `P` — pessimistic.

Разброс:

`σ = (P - O) / 6`

Ориентировочный 95% коридор до появления фактической производительности:

`E ± 2σ`

PERT используется только как предварительная модель неопределённости. После PoC прогноз заменяется фактической throughput-телеметрией.

## 8. Что измерить до пересчёта

### Сначала измерить

- количество и объём документов;
- долю сканов и сложной вёрстки;
- языки и качество OCR;
- среднее число claims на документ;
- размер source fragments;
- среднюю длину перевода;
- latency/throughput локальных моделей;
- долю reviewer corrections.

### Затем рассчитать

- throughput ingestion;
- throughput OCR;
- throughput translation;
- throughput knowledge extraction;
- долю ручной верификации;
- стоимость inference на документ при внешнем inference;
- нагрузку ролей;
- rework rate;
- прогноз оставшегося объёма.

## 9. Текущий статус оценки

- Срок: `TBD_AFTER_PROFILING`;
- Бюджет: `TBD_AFTER_POC`;
- Прогноз завершения: только по телеметрии;
- Baseline: ручной процесс, 1 поток;
- Speed-up vs baseline: `N/A` до фактического сравнения;
- ETA: `N/A` до стабильного throughput и известного remaining volume.

## 10. Risk Register — RISK-REGISTER-001

P/I ниже — стартовая экспертная гипотеза и не подменяет фактические данные.

| ID | Категория | Риск | P | I | Score | Митигация |
|---|---|---|---:|---:|---:|---|
| R-01 | DATA | Сканы и сложная вёрстка снижают качество OCR | 4 | 5 | 20 | PoC на репрезентативном корпусе; manual fallback; page-level confidence |
| R-02 | QUALITY | Claim выглядит правдоподобно, но не подтверждается источником | 3 | 5 | 15 | Evidence-first gate; golden set; exact locator required |
| R-03 | SCOPE | Добавление новых источников/форматов во время MVP | 4 | 4 | 16 | Change Request; scope freeze на gate |
| R-04 | LEGAL | Источник нельзя законно хранить/перерабатывать/публиковать | 3 | 5 | 15 | Source policy; legal/use gate до импорта; local-only full content |
| R-05 | INFRA | Локальной VRAM недостаточно для выбранной модели | 3 | 3 | 9 | Benchmark на PoC; model swap; serialized GPU inference; optional external endpoint |
| R-06 | DELIVERY | Нет владельца golden set и приёмка затягивается | 3 | 4 | 12 | Назначить acceptance owner и review cadence |
| R-07 | TRACE | Потеря lineage между source, translation, node и review | 3 | 5 | Mandatory trace_id/span_id/entity_trace_links; traversal gate |
| R-08 | DATA | Нерепрезентативный Discovery corpus даёт ложный прогноз | 3 | 4 | Stratified corpus sample по форматам/языкам/качеству |
| R-09 | GRAPH | Semantic dedup ошибочно объединяет разные знания | 3 | 5 | SAME_AS only as candidate; deterministic + human/model review |
| R-10 | DELIVERY | Массовый запуск до закрытия golden path создаёт rework | 4 | 4 | Bulk processing hard-blocked until MIN/MED gates green |

## 11. Value Roadmap — VALUE-ROADMAP-001 v0.3

| Уровень | Ценность | Артефакт |
|---|---|---|
| PoC | Техническая доказуемость | `POC-001` |
| MVP | Пользовательская ценность | `MVP-001` |
| Pilot | Работа в реальном процессе | `PILOT-001` |
| Production | Управляемая эксплуатация | `PROD-001` |

## 12. Delivery Contract

| Уровень | Цель | Scope | Definition of Done | Модель работ | Артефакт |
|---|---|---|---|---|---|
| PoC | Техническая доказуемость | Репрезентативный открытый корпус; golden set; baseline | Evidence path работает на критических форматах | T&M with cap | POC-001 |
| MVP | Пользовательская ценность | Must FR; analyst workflow; audit decisions | Пользователь завершает сквозной исследовательский цикл | T&M / FP только для стабильного scope | MVP-001 |
| Pilot | Работа в реальном процессе | Ограниченная группа; operational metrics; support | Ценность и unit cost подтверждены на реальной работе | T&M with cap | PILOT-001 |
| Production | Управляемая эксплуатация | SLO; Security; DR; monitoring; runbook; owner | Quality, security and operational gates пройдены | SLA + change management | PROD-001 |

## 13. FR traceability for architecture handoff

Архитектор не получает абстрактное пожелание. Каждый FR переходит в architecture input с ID.

| Requirement | Analytics interpretation | Architecture responsibility |
|---|---|---|
| FR-001 Import source | Immutable original + identity + SHA | Ingestion + Original Store contract |
| FR-002 Extraction | Document/fragment extraction without source mutation | Document Pipeline / OCR boundary |
| FR-003 Evidence | Claim must resolve to exact fragment/source/locator | Evidence Engine + provenance store |
| FR-004 Analyst verification | APPROVE/REVISE/REJECT/ESCALATE with actor/time | Review Service / Analyst Workspace |
| FR-005 Research/knowledge graph | Verified nodes and typed relations | Graph Builder + Graph API |
| FR-006 Reproducible report | Report contains evidence chain and versions | Report Builder + evidence/graph APIs |
| FR-007 Version comparison | Detect revision changes without losing history | Version Comparator + source identity/version model |
| FR-008 Layer separation | Original / translation / interpretation are distinct | Storage/data model boundaries |
| FR-009 Tracing | Every material stage traceable | Audit/Trace subsystem |
| FR-010 KB_READY gate | Unsupported candidate cannot promote | Promotion/Review Gate |
| FR-011 Role views | Same canonical node, different projections | Role Projection service/data view |
| FR-012 Contradictions | Preserve conflicting claims/relations | Graph relation `CONTRADICTS` + review workflow |

## 14. Architecture handoff gate

Stage 02 считается готовым к передаче архитектору, когда:

1. Product scope зафиксирован.
2. FR/NFR/constraints имеют IDs.
3. PROFILE-001 contract задан.
4. GOLDEN-SET-001 contract задан.
5. BASELINE-001 contract задан.
6. Risk Register создан.
7. Delivery roadmap и PoC/MVP/Pilot/Production gates определены.
8. Нет фиктивных сроков/бюджетов.
9. FR -> architecture responsibility traceability заполнена.
10. Открытые аналитические вопросы перечислены явно.

## 15. Открытые вопросы перед архитектором

- какой реальный корпус войдёт в PROFILE-001;
- какие 3–5 документов войдут в первый golden set;
- какой документ будет первым real PDF для MAX gate;
- какие форматы M1 считаются критическими;
- какой threshold OCR confidence блокирует auto-promotion;
- какая модель фактически будет translator/reviewer после benchmark;
- нужен ли внешний inference в M1 или только local endpoint;
- какие role views обязательны для первого PoC, а какие могут быть пустыми projection profiles.

Эти вопросы не блокируют подготовку HLD, но решения по ним должны быть зафиксированы как assumptions/ADRs до production implementation.