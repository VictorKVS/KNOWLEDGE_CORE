# FATHER Library Registry

Центральный реестр внешних библиотек, справочников, корпусов и коллекций, которые могут использоваться продуктами FATHER как источники кандидатов на знания.

## Правило доверия

Запись в этом реестре не означает автоматического признания материала достоверным.

```
DISCOVERED
→ CANDIDATE
→ PRIMARY_SOURCE_CHECKED
→ VERSION_CHECKED
→ SAFETY_REVIEWED
→ LAB_TESTED
→ VERIFIED / REJECTED / DEPRECATED
```

Критически значимый материал не получает статус `VERIFIED` только на основании популярности, количества GitHub stars или утверждения автора.

## Классы источников

| Код | Класс | Начальное доверие | Применение |
|---|---|---:|---|
| S0 | официальный нормативный источник | максимальное к тексту акта | нормативные факты и редакции |
| S1 | официальный стандарт или машиночитаемый каталог | высокое | схемы, контроли, справочники |
| S2 | официальная документация продукта/проекта | высокое в пределах продукта | технические факты |
| S3 | научная публикация | после оценки исследования | гипотезы, методы, доказательства |
| S4 | признанная профессиональная методика | среднее/высокое | практики и контрольные процедуры |
| S5 | учебник или открытый курс | среднее | обучение, объяснения, задания |
| S6 | curated collection | низкое | обнаружение кандидатов |
| S7 | публикация, блог, форум | низкое | гипотеза или практический сигнал |
| S8 | dark-web / leak / anonymous material | недоверенное | только законная аналитика и corroboration |

## Направления библиотек FATHER

| Код | Направление | Приоритет | Целевые базы |
|---|---|---:|---|
| LIB-DIR-SEC | информационная безопасность | P0 | SECURITY_KB |
| LIB-DIR-REG | нормативка и Compliance as Code | P0 | SECURITY_KB, REGULATORY_KB |
| LIB-DIR-AI | AI, LLM, RAG и агенты | P0 | AI_AGENTS_KB |
| LIB-DIR-AISEC | безопасность AI/LLM | P0 | AI_SECURITY_KB |
| LIB-DIR-ARCH | архитектура систем | P0 | ARCHITECTURE_KB |
| LIB-DIR-DEV | программирование и алгоритмы | P0 | PROGRAMMING_KB |
| LIB-DIR-TEST | тестирование, eval и качество | P0 | TESTING_KB |
| LIB-DIR-DEVOPS | Linux, DevOps, Cloud и CI/CD | P0 | DEVSECOPS_KB |
| LIB-DIR-OSINT | OSINT, CTI и расследования | P0 | OSINT_KB, THREAT_KB |
| LIB-DIR-KG | графы знаний и онтологии | P0 | KNOWLEDGE_ENGINEERING_KB |
| LIB-DIR-MED | медицина и медицинские ИС | P1 | HEALTHCARE_KB |
| LIB-DIR-RISK | риск-менеджмент и безопасность | P1 | RISK_KB |
| LIB-DIR-PROC | BPMN, DMN и процессы | P1 | PROCESS_KB |
| LIB-DIR-FIN | финансы и моделирование | P1 | FINANCE_KB |
| LIB-DIR-MEDIA | текст, изображение, звук, видео | P1 | MEDIA_KB |
| LIB-DIR-EDU | педагогика и обучение | P1 | LEARNING_KB |

## Зарегистрированные библиотеки

### LIB-FATHER-SEC-0001 — The Book of Secret Knowledge

| Поле | Значение |
|---|---|
| Адрес | https://github.com/trimstray/the-book-of-secret-knowledge |
| Класс | S6 — curated collection |
| Направления | SEC, DEVOPS, OSINT, ARCH |
| Статус | `CANDIDATE_SOURCE` |
| Назначение | поиск инструментов, команд, руководств и первоисточников |
| Ограничение | не выполнять команды и не признавать советы verified без проверки |
| Дата регистрации | 2026-08-18 |

### LIB-FATHER-REG-0001 — NIST OSCAL

| Поле | Значение |
|---|---|
| Адрес | https://github.com/usnistgov/OSCAL |
| Класс | S1 — официальный машиночитаемый стандарт |
| Направления | REG, SEC, TEST, KG |
| Целевые продукты | Security Knowledge, Audit Engine, Regulatory Twin |
| Ценность | XML/JSON/YAML-модели каталогов, профилей, SSP, планов и результатов оценки, POA&M |
| Статус | `PRIORITY_INGEST` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-SEC-0002 — ComplianceAsCode Content

| Поле | Значение |
|---|---|
| Адрес | https://github.com/ComplianceAsCode/content |
| Класс | S4 — признанная профессиональная методика и corpus |
| Направления | SEC, REG, DEVOPS, TEST |
| Ценность | YAML-правила, SCAP/XCCDF/OVAL, проверки и исправления Ansible/Bash |
| Статус | `PRIORITY_RESEARCH` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-THREAT-0001 — MITRE ATT&CK STIX Data

| Поле | Значение |
|---|---|
| Адрес | https://github.com/mitre-attack/attack-stix-data |
| Класс | S1 — официальный машиночитаемый каталог |
| Направления | SEC, OSINT, KG, AISEC |
| Ценность | версионируемые STIX 2.1 коллекции Enterprise, Mobile и ICS |
| Целевые базы | THREAT_KB, OSINT_KB, SECURITY_KB |
| Статус | `PRIORITY_INGEST` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-APPSEC-0001 — OWASP Cheat Sheet Series

| Поле | Значение |
|---|---|
| Адрес | https://github.com/OWASP/CheatSheetSeries |
| Класс | S4 — профессиональная методика |
| Направления | SEC, DEV, DEVOPS, TEST |
| Ценность | практики безопасной разработки, контроли, шаблоны и антишаблоны |
| Статус | `PRIORITY_RESEARCH` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-ARCH-0001 — The System Design Primer

| Поле | Значение |
|---|---|
| Адрес | https://github.com/donnemartin/system-design-primer |
| Класс | S5/S6 — учебная и curated collection |
| Направления | ARCH, DEV, TEST |
| Ценность | масштабируемость, доступность, согласованность, базы, API и архитектурные компромиссы |
| Ограничение | решения требуют проверки применимости и первоисточников |
| Статус | `CANDIDATE_SOURCE` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-DEV-0001 — The Algorithms

| Поле | Значение |
|---|---|
| Адрес | https://github.com/TheAlgorithms |
| Класс | S5 — учебный corpus |
| Направления | DEV, TEST, EDU |
| Ценность | реализации алгоритмов на Python, Go, C, C++, Java и TypeScript |
| Ограничение | учебные реализации не считать оптимальным production-кодом |
| Статус | `CANDIDATE_TRAINING_CORPUS` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-EDU-0001 — Free Programming Books

| Поле | Значение |
|---|---|
| Адрес | https://github.com/EbookFoundation/free-programming-books |
| Класс | S6 — каталог легальных образовательных ресурсов |
| Направления | DEV, ARCH, DEVOPS, AI, EDU |
| Ценность | книги, курсы, задачи, интерактивные материалы и материалы на разных языках |
| Ограничение | полный текст загружать только при разрешающей лицензии |
| Статус | `CATALOG_SOURCE` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-DEVOPS-0001 — The Art of Command Line

| Поле | Значение |
|---|---|
| Адрес | https://github.com/jlevy/the-art-of-command-line |
| Класс | S5 — открытое практическое руководство |
| Направления | DEVOPS, SEC, EDU |
| Ценность | Bash, процессы, файлы, SSH, сети, диагностика и автоматизация |
| Ограничение | опасные команды проходят sandbox/lab test и получают rollback |
| Статус | `CANDIDATE_TRAINING_SOURCE` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-OSINT-0001 — Awesome OSINT

| Поле | Значение |
|---|---|
| Адрес | https://github.com/jivoi/awesome-osint |
| Класс | S6 — curated collection |
| Направления | OSINT, SEC, KG |
| Ценность | инструменты и источники по людям, компаниям, инфраструктуре, архивам и CTI |
| Ограничение | обязательны проверка законности, ToS, передачи данных, владельца и безопасности установки |
| Статус | `CANDIDATE_SOURCE` |
| Дата регистрации | 2026-08-19 |

### LIB-FATHER-AI-0001 — Prompt Engineering Guide

| Поле | Значение |
|---|---|
| Адрес | https://github.com/dair-ai/Prompt-Engineering-Guide |
| Класс | S5/S6 — учебная и исследовательская коллекция |
| Направления | AI, AISEC, TEST, EDU |
| Ценность | prompting, context engineering, RAG, агенты и adversarial prompting |
| Ограничение | техники привязывать к модели, версии, исходной статье и эксперименту |
| Статус | `CANDIDATE_RESEARCH_SOURCE` |
| Дата регистрации | 2026-08-19 |

## Обязательная карточка любого источника

```yaml
source_id: LIB-FATHER-*
title:
url:
publisher:
source_class: S0-S8
directions: []
target_knowledge_bases: []
license:
copyright_status:
language:
formats: []
version:
last_release:
last_checked:
maintenance_state:
acquisition_method:
authority:
known_biases: []
legal_constraints: []
security_constraints: []
ingestion_scope:
trust_status:
reviewer:
notes:
```

## Конвейер обработки

```
DISCOVER
→ REGISTER
→ LICENSE CHECK
→ SOURCE CLASSIFICATION
→ ACQUIRE METADATA
→ MALWARE/SECRET CHECK
→ EXTRACT
→ FIND PRIMARY SOURCES
→ VERSION/APPLICABILITY CHECK
→ DUPLICATE/CONFLICT CHECK
→ LAB/EVAL
→ HUMAN REVIEW
→ VERIFIED NODE
→ PERIODIC RECHECK
```

## Контур книг и статей в открытом интернете

Искать по очереди:

1. официальные сайты органов, стандартов и проектов;
2. репозитории авторов и издателей;
3. open-access научные архивы;
4. университетские репозитории;
5. каталоги легально бесплатных книг;
6. препринты и материалы конференций;
7. официальные технические блоги;
8. curated lists как навигаторы.

Для книги фиксировать ISBN/DOI, автора, издание, год, лицензию, доступность полного текста, оглавление, рецензии, актуальность и связанные первичные источники.

## Контур dark web и закрытых площадок

Разрешённое назначение:

- мониторинг упоминаний бренда и доменов;
- индикаторы компрометации;
- сообщения об уязвимостях и инцидентах;
- исследовательские отчёты;
- оценка угроз;
- corroboration по нескольким законным источникам.

Запрещённое назначение:

- поиск или загрузка пиратских книг;
- покупка и распространение утечек;
- приобретение вредоносных средств или незаконных услуг;
- получение учётных данных;
- участие в преступных сообществах;
- доступ к незаконным материалам;
- активное взаимодействие без отдельного законного основания и утверждённой процедуры.

Любой материал класса S8:

- изолируется;
- не выполняется и не открывается в основной среде;
- получает минимальное доверие;
- проверяется по независимым источникам;
- не содержит в основной базе незаконный или чувствительный контент;
- сохраняется как метаданные, хэш, индикатор и аналитический вывод;
- требует human approval и журнала оснований.

## Следующие этапы

### Этап A — открытые книги и статьи

- сформировать поисковые запросы по каждому P0-направлению;
- зарегистрировать каталоги книг, статей и конференций;
- проверить лицензии;
- выбрать по 10 приоритетных источников на направление;
- построить учебные карты и source packs.

### Этап B — официальные datasets и schemas

- OSCAL;
- ATT&CK/STIX;
- OWASP;
- ComplianceAsCode;
- CVE/CWE/CAPEC;
- SBOM: CycloneDX/SPDX;
- SARIF;
- OpenAPI;
- BPMN/DMN;
- RDF/OWL.

### Этап C — lawful dark-web intelligence

- сначала определить юридические и операционные границы;
- использовать безопасную изолированную среду;
- начать с отчётов проверенных CTI-провайдеров и публичных исследований;
- собирать только необходимые индикаторы и метаданные;
- создать процедуру проверки, хранения, удаления и эскалации.

## Неподлежащие нарушению правила

- GitHub stars не являются доказательством качества;
- книга без разрешающей лицензии не копируется в corpus;
- открытый URL не означает право массового скачивания;
- совет не становится знанием без provenance;
- исполняемый код не запускается до проверки;
- offensive content используется только законно и в лаборатории;
- личные данные и утечки не становятся публичной библиотекой;
- первичные источники выше пересказов;
- старые версии сохраняются, но помечаются;
- каждый verified-вывод должен воспроизводиться.


## Контур обучения, RL и фабрики агентов

Полный порядок поиска, извлечения, хранения, связывания, экспериментов, обучения и выпуска описан в [FATHER: конвейер знаний, обучения и фабрика агентов](./FATHER_KNOWLEDGE_ACQUISITION_AND_AGENT_FACTORY_PLAN.md).

### Дополнительные направления

| Код | Направление | Приоритет | Целевые базы/реестры |
|---|---|---:|---|
| LIB-DIR-ML | deep learning и fine-tuning | P0 | MODEL_REGISTRY, AI_AGENTS_KB |
| LIB-DIR-RL | RL, RLHF и preference optimization | P0 | EXPERIMENT_REGISTRY, MODEL_REGISTRY |
| LIB-DIR-MARL | multi-agent RL и self-play | P1 | AGENT_REGISTRY, ENVIRONMENT_REGISTRY |
| LIB-DIR-ORCH | оркестрация и durable workflows | P0 | WORKFLOW_REGISTRY |
| LIB-DIR-EVAL | eval, benchmark и воспроизводимость | P0 | EVAL_REGISTRY |
| LIB-DIR-OBS | tracing, metrics, logs и стоимость | P0 | OBSERVABILITY_KB |

### Зарегистрированные технологические семейства

| ID | Официальный источник | Назначение | Статус |
|---|---|---|---|
| LIB-FATHER-ML-0001 | https://github.com/pytorch/pytorch | базовый deep learning runtime | `CANDIDATE_CORE` |
| LIB-FATHER-ML-0002 | https://github.com/huggingface/transformers | модели и training APIs | `PRIORITY_RESEARCH` |
| LIB-FATHER-ML-0003 | https://github.com/huggingface/datasets | datasets и обработка | `PRIORITY_RESEARCH` |
| LIB-FATHER-ML-0004 | https://github.com/huggingface/peft | LoRA/QLoRA/adapters | `PRIORITY_LAB` |
| LIB-FATHER-ML-0005 | https://github.com/huggingface/accelerate | распределённый запуск обучения | `PRIORITY_RESEARCH` |
| LIB-FATHER-RL-0001 | https://github.com/huggingface/trl | SFT, reward, DPO и RL post-training | `PRIORITY_LAB` |
| LIB-FATHER-RL-0002 | https://github.com/OpenRLHF/OpenRLHF | масштабируемый RLHF | `CANDIDATE_COMPARE` |
| LIB-FATHER-RLENV-0001 | https://github.com/Farama-Foundation/Gymnasium | single-agent RL environments | `PRIORITY_LAB` |
| LIB-FATHER-MARL-0001 | https://github.com/Farama-Foundation/PettingZoo | multi-agent RL environments | `PRIORITY_LAB` |
| LIB-FATHER-RL-0003 | https://github.com/ray-project/ray | RLlib и distributed execution | `CANDIDATE_COMPARE` |
| LIB-FATHER-ORCH-0001 | https://github.com/openai/openai-agents-python | agents, tools, guardrails, handoffs | `PRIORITY_PROTOTYPE` |
| LIB-FATHER-ORCH-0002 | https://github.com/langchain-ai/langgraph | stateful agent graphs | `CANDIDATE_COMPARE` |
| LIB-FATHER-ORCH-0003 | https://github.com/microsoft/autogen | multi-agent orchestration | `CANDIDATE_COMPARE` |
| LIB-FATHER-ORCH-0004 | https://github.com/temporalio/temporal | durable workflows | `PRIORITY_ARCHITECTURE` |
| LIB-FATHER-EVAL-0001 | https://github.com/UKGovernmentBEIS/inspect_ai | agent/model evaluation | `PRIORITY_RESEARCH` |
| LIB-FATHER-EVAL-0002 | https://github.com/openai/evals | eval patterns and datasets | `PRIORITY_RESEARCH` |
| LIB-FATHER-EVAL-0003 | https://github.com/mlflow/mlflow | experiment/model registry | `PRIORITY_PROTOTYPE` |
| LIB-FATHER-OBS-0001 | https://github.com/open-telemetry | traces, metrics and logs | `PRIORITY_ARCHITECTURE` |

Правило выбора: ни одна библиотека не включается в production только по популярности. Нужны проверка лицензии, maintenance, supply chain/SBOM, sandbox-тест, benchmark на задачах FATHER, стоимость владения, совместимость и план выхода.
