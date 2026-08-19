# FATHER: конвейер знаний, обучения и фабрика агентов

## 1. Назначение

Документ определяет полный производственный цикл FATHER:

```
источник → проверяемое утверждение → эксперимент → инженерный паттерн
→ навык → агент → команда агентов → продукт → обратная связь
```

Реестр источников отвечает на вопрос «откуда берём», а этот регламент — «что ищем, как забираем, куда кладём, как соединяем, проверяем, обучаем и выпускаем».

## 2. Что ищем

### 2.1 Источники знаний

1. официальные законы, редакции, стандарты, схемы и документацию;
2. систематические обзоры, метаанализы, статьи, препринты и диссертации;
3. benchmark suites, datasets, leaderboard-данные, ablation- и replication-исследования;
4. книги, курсы и учебные корпуса с законным доступом;
5. исходный код, тесты, конфигурации, модели угроз и postmortem;
6. отрицательные результаты, ограничения, известные сбои и способы отката;
7. Open Web; dark-web-сигналы — только законные индикаторы и метаданные по отдельной процедуре.

### 2.2 Что извлекаем

Для каждого метода или комбинации фиксируем:

- задачу и границы применимости;
- среду, данные, оборудование, версии и зависимости;
- алгоритм, параметры и порядок компонентов;
- baseline и альтернативы;
- метрики качества, стоимости, задержки, устойчивости и безопасности;
- положительные и отрицательные результаты;
- источник, цитату/локатор, лицензию и дату;
- воспроизводимость, артефакты, reviewer и уровень зрелости.

Формула объекта: **не «алгоритм лучший», а «алгоритм A в среде E при ограничениях C по метрике M оказался лучше B с доказательством D»**.

## 3. Куда складываем

| Слой | Содержимое | Основное хранилище |
|---|---|---|
| Source Registry | карточки, URL, лицензии, версии | Git + PostgreSQL |
| Immutable Source Vault | разрешённые оригиналы, хэши, снимки | шифруемое object storage |
| Normalized Corpus | очищенный текст, таблицы, код, chunks | object storage + PostgreSQL |
| Claim/Evidence Store | утверждения, доказательства, конфликты | PostgreSQL |
| Knowledge Graph | сущности и связи | PostgreSQL/graph layer |
| Vector Index | семантический поиск | pgvector |
| Pattern Registry | проверенные комбинации и условия | PostgreSQL + Git |
| Experiment/Eval Registry | runs, datasets, метрики, артефакты | MLflow-совместимый слой |
| Skill Registry | инструкции, tools, contracts, tests | Git |
| Agent/Model Registry | версии агентов, моделей, adapters | registry + object storage |
| Workflow Registry | DAG/state machine, роли, approvals | Git + workflow engine |
| Audit Log | кто, что, почему изменил | append-only журнал |

Открытая зона содержит только публичные схемы, документацию и разрешённые fixtures. Секреты, персональные данные, клиентские материалы, веса и закрытые наборы отделяются политиками доступа; позднее хранилища можно зашифровать без смены стабильных ID.

## 4. Как связываем в узлы

Основная цепочка:

```
SOURCE → SNAPSHOT → CHUNK → CLAIM → EVIDENCE
→ REQUIREMENT / CONTROL / METHOD
→ EXPERIMENT → RESULT → VERIFIED_PATTERN
→ SKILL → AGENT_VERSION → WORKFLOW → RUN → OUTCOME
```

Каждый узел имеет стабильный ID, версию, provenance, лицензию, уровень доверия, область применимости и дату перепроверки. Противоречия не удаляются: создаётся узел `CONFLICT` со сравнением версий, сред и доказательств.

## 5. Производственный алгоритм

```
DISCOVER
→ REGISTER
→ LEGAL/LICENSE CHECK
→ QUARANTINE + MALWARE/SECRET CHECK
→ SNAPSHOT + HASH
→ PARSE/NORMALIZE
→ EXTRACT CLAIMS, CONDITIONS, METRICS
→ LINK PRIMARY SOURCES
→ DEDUPLICATE + DETECT CONFLICTS
→ DESIGN BASELINE/EXPERIMENT
→ RUN IN SANDBOX
→ REPRODUCE
→ HUMAN/EXPERT REVIEW
→ PROMOTE OR REJECT
→ PACKAGE AS PATTERN/SKILL
→ ASSIGN TO AGENT
→ EVALUATE
→ CANARY RELEASE
→ MONITOR
→ RETRAIN, DEPRECATE OR ROLLBACK
```

Критические переходы проходят Source Gate, Data Gate, Experiment Gate, Skill Gate, Agent Gate, Release Gate и Continuous-Learning Gate.

## 6. Как комбинируем знания

Комбинация допускается, если:

1. совпадает профиль задачи и среды;
2. источники имеют provenance и совместимые лицензии;
3. есть первичный источник и желательно независимое подтверждение;
4. компоненты протестированы отдельно и вместе;
5. проверены порядок, параметры, интерфейсы и failure modes;
6. есть baseline, откат и критерий остановки;
7. перенос между отраслями маркируется как гипотеза до отдельной проверки.

Уровни зрелости:

`HYPOTHESIS → PUBLISHED → REPRODUCED → LAB_VERIFIED → MULTI_ENV_VERIFIED → PROJECT_PROVEN → PRODUCTION_PROVEN → GOLDEN_PATTERN`.

## 7. Работа при наличии нескольких баз знаний

1. Task Router классифицирует запрос, риск и требуемую экспертизу.
2. Policy Layer определяет допустимые базы, инструменты и действия.
3. Retriever выбирает claims и patterns с учётом версии и среды.
4. Applicability Filter отбрасывает несовместимые решения.
5. Planner строит минимум две альтернативы и план проверки.
6. Agent Team выполняет исследование/задачу в sandbox.
7. Verifier сверяет факты, ссылки, расчёты и результаты инструментов.
8. Red Team ищет prompt injection, утечки, reward hacking и опасные действия.
9. Human Approval применяется к нормативным, финансовым, медицинским и необратимым решениям.
10. Результат, ошибки и фактический outcome возвращаются в Experiment/Evidence Store, но не становятся обучающими данными автоматически.

## 8. Лестница обучения агентов

| Уровень | Метод | Когда применять |
|---|---|---|
| L0 | prompt + tools + policy | новая роль, быстрый MVP |
| L1 | RAG + curated examples | знания часто меняются |
| L2 | SFT/LoRA/QLoRA | стабильный формат и много качественных примеров |
| L3 | preference optimization (DPO и аналоги) | есть сравнения хороших/плохих ответов |
| L4 | RL с reward model (PPO/GRPO и аналоги) | есть надёжная автоматическая оценка |
| L5 | multi-agent RL/self-play | среда измерима, взаимодействия воспроизводимы |
| L6 | контролируемое непрерывное обучение | только с quarantine, eval, approval и rollback |

Принцип: сначала RAG, инструменты и eval; дообучение весов — после появления стабильного набора задач; RL — только после надёжной среды и reward. Иначе агент учится обходить метрику, а не решать задачу.

Reward хранится многомерно: корректность, полнота доказательств, соблюдение политики, результат задачи, безопасность tools, стоимость, latency и устойчивость. Один скрытый scalar без расшифровки запрещён.

## 9. Реестр технологических кандидатов

### Обучение и post-training

| ID | Проект | Роль | Решение |
|---|---|---|---|
| LIB-FATHER-ML-0001 | PyTorch | базовое deep learning | P0 research |
| LIB-FATHER-ML-0002 | Hugging Face Transformers | модели и training APIs | P0 research |
| LIB-FATHER-ML-0003 | Datasets | версии и обработка datasets | P0 research |
| LIB-FATHER-ML-0004 | PEFT | LoRA/QLoRA/adapters | P0 research |
| LIB-FATHER-ML-0005 | Accelerate | distributed training launcher | P0 research |
| LIB-FATHER-RL-0001 | TRL | SFT, reward, DPO, PPO/GRPO-class post-training | P0 lab |
| LIB-FATHER-RL-0002 | OpenRLHF | масштабируемый RLHF-кандидат | P1 compare |
| LIB-FATHER-RL-0003 | DeepSpeed | distributed optimization | P1 compare |
| LIB-FATHER-RL-0004 | Stable-Baselines3 | проверяемые baseline RL | P1 lab |
| LIB-FATHER-RL-0005 | CleanRL | прозрачные reference implementations | P1 research |

### Среды и многоагентное обучение

| ID | Проект | Роль | Решение |
|---|---|---|---|
| LIB-FATHER-RLENV-0001 | Gymnasium | стандарт single-agent environments | P0 lab |
| LIB-FATHER-MARL-0001 | PettingZoo | multi-agent environments | P0 lab |
| LIB-FATHER-RL-0006 | Ray RLlib | distributed RL/MARL | P0 compare |

### Оркестрация фабрики

| ID | Проект | Роль | Решение |
|---|---|---|---|
| LIB-FATHER-ORCH-0001 | OpenAI Agents SDK | agents, tools, guardrails, handoffs, tracing | P0 prototype |
| LIB-FATHER-ORCH-0002 | LangGraph | stateful agent graphs | P0 compare |
| LIB-FATHER-ORCH-0003 | Microsoft AutoGen | multi-agent patterns | P0 compare |
| LIB-FATHER-ORCH-0004 | Semantic Kernel | enterprise agent/process integration | P1 compare |
| LIB-FATHER-ORCH-0005 | Temporal | durable long-running workflows | P0 architecture |
| LIB-FATHER-ORCH-0006 | Ray Core | distributed tasks/actors | P1 scale |
| LIB-FATHER-ORCH-0007 | Haystack | retrieval/agent pipelines | P1 compare |

### Eval, наблюдаемость и воспроизводимость

| ID | Проект | Роль | Решение |
|---|---|---|---|
| LIB-FATHER-EVAL-0001 | Inspect AI | agent/model evaluation | P0 research |
| LIB-FATHER-EVAL-0002 | OpenAI Evals | eval patterns and datasets | P0 research |
| LIB-FATHER-EVAL-0003 | MLflow | runs, metrics, model registry | P0 prototype |
| LIB-FATHER-OBS-0001 | OpenTelemetry | traces, metrics, logs | P0 architecture |
| LIB-FATHER-OBS-0002 | Langfuse | LLM observability/evals | P1 compare |
| LIB-FATHER-OBS-0003 | Arize Phoenix | tracing and evaluation | P1 compare |

Все записи — кандидаты, не заранее утверждённый стек. Перед использованием: maintenance, license, security, dependency/SBOM, benchmark на наших задачах, стоимость миграции и exit plan.

## 10. Устройство фабрики агентов

Роли конвейера:

```
Source Scout → Researcher → Knowledge Engineer → Experiment Designer
→ Trainer → Agent Builder → Evaluator → Red Team
→ Human Approver → Release Manager → Monitor
```

Платформенные компоненты: Task Router, Model Gateway, Tool Registry, KB/Memory, workflow engine, event bus/queue, sandbox, secrets manager, policy engine, eval service, observability, cost manager и audit trail.

Каждый агент выпускается как пакет:

- role/instructions и границы полномочий;
- разрешённые KB, models и tools;
- input/output schema;
- golden tasks, adversarial tests и stop conditions;
- budget/timeout;
- handoff contract;
- версия, owner, risk class и rollback.

## 11. Основные угрозы

- data/knowledge poisoning и скрытые инструкции в источниках;
- supply-chain атаки библиотек и моделей;
- утечки секретов/персональных данных;
- reward hacking и Goodhart’s law;
- feedback contamination и model collapse;
- неконтролируемое самокопирование агентов;
- циклы, runaway cost и cascading failures;
- перенос паттерна в неподходящую среду.

Меры: quarantine, content disarm, allowlists, sandbox, least privilege, signed artifacts, reproducible builds, независимый verifier, лимиты, canary и быстрый rollback.

## 12. Первый практический срез

Начать не с RL, а с двух потоков и SECURITY_KB по 152-ФЗ:

- **Поток A — Regulatory Research Agent:** источник → редакция → requirement → control → evidence;
- **Поток B — Verification Agent:** независимая проверка версии, цитаты, применимости и конфликтов.

Оба потока пишут через единый schema/ID contract. Первый eval-набор: корректность источника и редакции, точность цитирования, полнота связей, отсутствие неподтверждённых требований, latency и стоимость. После стабильных golden tasks сравнить L0/L1, затем только при доказанной выгоде — PEFT/SFT; RL оставить до появления надёжного reward и достаточного числа воспроизводимых эпизодов.

## 13. Критерий готовности

Фабрика считается работоспособной, когда один и тот же входной пакет:

- воспроизводимо маршрутизируется;
- формирует проверяемые узлы с provenance;
- проходит независимый eval;
- выпускает версионированного агента/навык;
- наблюдается по качеству, риску, стоимости и latency;
- откатывается без потери истории;
- возвращает опыт в базу только после проверки.
