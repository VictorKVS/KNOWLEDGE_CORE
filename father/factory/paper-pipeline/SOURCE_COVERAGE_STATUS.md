# FATHER Paper Pipeline — Source Coverage Status

Status: `EXPLICIT COVERAGE / NO EXHAUSTIVE CLAIM`

Этот файл отделяет **полноту алгоритма** от **полноты нормативной и книжной базы**. Бумажный lifecycle может быть закончен структурно, даже если не все источники ещё разобраны до пункта/страницы. Автоматизация blocker-правил при этом запрещена до exact evidence mapping.

## 1. Нормативный слой — зарегистрирован

Текущий `NORMATIVE_SOURCE_REGISTRY.yaml` содержит:

- ГОСТ Р 57193-2025 — процессы жизненного цикла систем;
- ГОСТ Р 58609-2019 — информационные элементы/документация жизненного цикла;
- ГОСТ Р ИСО/МЭК 12207-2010 — жизненный цикл программных средств;
- ГОСТ Р 57100-2025 — описание архитектуры;
- ГОСТ Р 57101-2016 — управление проектом;
- ГОСТ Р 59793-2021 — стадии создания автоматизированных систем;
- ГОСТ 34.201-2020 — виды/комплектность/обозначение документов АС;
- ГОСТ Р 59795-2021 — содержание документов АС;
- ГОСТ 34.602-2020 — ТЗ на создание АС;
- ГОСТ Р 59792-2021 — виды испытаний АС;
- ГОСТ Р 56939-2024 — безопасная разработка ПО;
- ГОСТ Р 71207-2024 — статический анализ ПО;
- Методика оценки угроз ФСТЭК России 2021;
- применимые overlays: ФСТЭК 117, ФСТЭК 21, ПП РФ 1119, ФСБ 378, ПП РФ 127, ФСТЭК 235, ФСТЭК 239.

## 2. Что по нормативам ещё НЕ считается закрытым

- федеральный законовый слой `149-ФЗ / 152-ФЗ / 187-ФЗ` должен быть добавлен/нормализован в общий реестр;
- sector overlays (включая healthcare и иные регулируемые отрасли) должны быть расширены по конкретному проекту;
- каждый норматив, используемый как автоматический blocker, должен пройти full-text ingestion;
- требуется atomic decomposition `source → clause → applicability condition → normative requirement → artifact field → owner → gate`;
- conflicts/supersession должны храниться как данные, а не решаться из памяти;
- exact clause numbers не считаются доказанными только из названия стандарта/приказа.

Следовательно: **paper pipeline использует нормативные семейства и области применения сейчас; автоматическое юридически значимое решение по пунктам — позже, после evidence review.**

## 3. Книжный слой — SOURCE_VERIFIED / PROMOTED CANDIDATE

### Mark Richards, Neal Ford — «Фундаментальный подход к программной архитектуре»

Проверенные и уже нанесённые идеи:

- architecture characteristics как явные drivers;
- решения как trade-offs, а не «лучшая технология вообще»;
- ADR и сохранение истории решения;
- architecture risk review / risk storm;
- continuous architecture analysis/reassessment.

Состояние: source-verified идеи находятся в `BOOK_IDEA_INTAKE.yaml` и используются как method layer, не как normative authority.

### Simon Brown — C4 model

Источник в пользовательской библиотеке проверен. Используемые идеи:

- иерархия Context → Container → Component → Code;
- System Context показывает систему в окружающем мире, пользователей и внешнюю среду;
- Container показывает high-level shape, распределение ответственности, major technology choices и взаимодействия;
- Context и Container рассматриваются как базовые views; Component/Code создаются тогда, когда польза оправдывает стоимость поддержки.

Состояние: source verified; подлежит фиксации в `BOOK_IDEA_INTAKE.yaml` как professional method source.

## 4. Книжный слой — PENDING / NOT PROMOTED

`Software Architecture: The Hard Parts` имеет зарегистрированный pilot, но публичный канонический pipeline фиксирует `AWAITING_SOURCE_BYTES`; B1+ не закрыты. Поэтому идеи из него **не используются как verified FATHER rules** до прохождения book pipeline.

Другие backlog sources пока также не являются правилами FATHER только по названию:

- Documenting Software Architectures;
- Clean Architecture;
- The Software Architect Elevator;
- Software Systems Architecture;
- Building Evolutionary Architectures, 2e;
- Just Enough Software Architecture;
- Team Topologies;
- Building Secure & Reliable Systems.

## 5. Правило применения источника

```text
Normative source
  → applicability + current status
  → exact evidence/clause when material
  → requirement/control/gate

Professional source
  → source verification
  → paraphrased method/idea
  → applicability
  → conflicts/alternatives
  → independent review
  → method catalogue / candidate rule
```

Профессиональный источник никогда не отменяет закон, обязательный договорный constraint или authoritative owner fact.
