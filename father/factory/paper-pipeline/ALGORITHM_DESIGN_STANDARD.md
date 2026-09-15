# FATHER — стандарт проектирования алгоритмов

Status: `CANDIDATE / MANDATORY METHOD STANDARD FOR PAPER PIPELINE REVIEW`

## 1. Главный принцип

FATHER выбирает **самый простой алгоритм, который доказуемо удовлетворяет требованиям**.

```text
простое решение
    ↓
проходит correctness / evidence / risk / performance / operability criteria?
    ├─ ДА → оставить простое
    └─ НЕТ → добавить только ту сложность, которая закрывает конкретный дефект
```

Сложность не является достоинством сама по себе. Любая дополнительная ветвь, модель, очередь, агент, БД, эвристика или LLM должна иметь явное основание.

## 2. Научный подход

Каждый материальный алгоритм проектируется как проверяемая гипотеза, а не как мнение автора.

Минимальный цикл:

```text
PROBLEM
→ FORMAL INPUTS / OUTPUTS
→ ASSUMPTIONS
→ INVARIANTS
→ CANDIDATE METHODS
→ SELECTION CRITERIA
→ PROPOSED ALGORITHM
→ CORRECTNESS ARGUMENT
→ COMPLEXITY / COST
→ FAILURE MODES
→ TEST / EXPERIMENT DESIGN
→ EVIDENCE
→ REVIEW
→ ACCEPT / REWORK / REJECT
```

Для алгоритмов, где строгого математического доказательства корректности дать нельзя, используется **argument of adequacy**: явные условия применимости, контрпримеры, тестовый набор, сравнительный baseline, измеряемые критерии и независимый review.

## 3. Обязательная карточка алгоритма

Для каждого алгоритма фиксируются следующие поля.

### A. Problem statement

- какую задачу решаем;
- почему задача вообще существует;
- какой upstream requirement / risk / gate её породил;
- что считается успехом;
- что не входит в scope.

### B. Inputs

Для каждого входа:

- имя и тип;
- источник;
- owner/authority;
- версия/freshness;
- допустимые состояния (`VERIFIED`, `CONFIRMED`, `PARTIAL`, `UNKNOWN`, ...);
- preconditions;
- trust/security classification.

### C. Outputs

Для каждого выхода:

- структура;
- семантика;
- downstream consumer;
- postconditions;
- provenance/traceability requirements;
- допустимое состояние результата.

### D. Assumptions

Каждое предположение получает ID и способ проверки.

Нельзя скрывать assumption внутри текста алгоритма.

### E. Invariants

Инвариант — свойство, которое должно оставаться истинным на всём допустимом пути исполнения.

Примеры:

- source provenance не теряется;
- UNKNOWN не превращается в FACT;
- владелец данных не заменяется моделью;
- сумма процентов остаётся 100%;
- один и тот же immutable input snapshot даёт воспроизводимый deterministic result;
- security classification не понижается неявно.

### F. Candidate algorithms

До выбора рассматривается минимум:

1. простейший baseline;
2. один практически реалистичный альтернативный вариант;
3. при материальном решении — вариант «не делать / отложить».

Если альтернатив реально нет, это должно быть обосновано.

### G. Selection criteria

Критерии задаются **до выбора варианта**.

Типовые критерии:

- correctness;
- completeness;
- precision/recall/error rate;
- latency / throughput;
- computational complexity;
- memory/storage cost;
- human review cost;
- explainability;
- reversibility;
- security/privacy impact;
- maintainability;
- operational complexity;
- deterministic reproducibility;
- total cost.

Вес критерия не придумывается после получения желаемого результата.

### H. Algorithm

Алгоритм описывается одним из способов:

- строгий pseudocode;
- state machine;
- decision table;
- DAG;
- formula / optimization problem;
- graph traversal;
- deterministic ruleset;
- bounded heuristic;
- model-assisted procedure.

Для LLM/agent procedure отдельно указывается deterministic envelope: что именно модель **не имеет права** решать.

### I. Correctness argument

Нужно ответить минимум на четыре вопроса:

1. Почему каждый шаг допустим?
2. Почему результат соответствует postconditions?
3. Какие инварианты сохраняются?
4. При каких входах корректность больше не гарантируется?

Для формализуемых алгоритмов по возможности используются:

- induction;
- invariant proof;
- contradiction;
- exhaustive case analysis;
- graph/property proof;
- bound proof.

Для эмпирических/AI-алгоритмов:

- reference/golden set;
- baseline comparison;
- confidence interval where applicable;
- error taxonomy;
- blind/challenger review where material;
- reproducible experiment configuration.

### J. Complexity

Фиксируется только там, где это имеет смысл.

Минимум:

- time complexity;
- space complexity;
- I/O or network complexity;
- number of human decisions;
- number of model calls;
- worst/expected case distinction.

Для workflow-алгоритмов организационная сложность не менее важна вычислительной.

### K. Failure modes

Для каждого существенного failure mode:

- trigger;
- detectability;
- consequence;
- containment;
- fallback;
- rework target;
- whether gate must fail closed.

### L. Experiment / test design

До внедрения определяется, как алгоритм будет опровергаться.

Обязательные группы тестов по применимости:

- nominal;
- boundary;
- empty/missing input;
- contradictory input;
- stale input;
- adversarial/malicious input;
- high-load/worst-case;
- regression;
- counterexample cases.

### M. Evidence and references

Каждое существенное правило помечается происхождением:

- `NORMATIVE` — закон/приказ/ГОСТ/ISO и применимость;
- `PROJECT_EVIDENCE` — факты конкретного проекта;
- `BOOK_VERIFIED` — проверенная профессиональная книга;
- `COURSE_METHOD` — OTUS/курс как методический источник;
- `SCIENTIFIC` — статья/исследование/формальный метод;
- `ENGINEERING_HYPOTHESIS` — наша гипотеза, требующая проверки.

Приоритет authority остаётся проектным: обязательные нормы и owner requirements не заменяются книгой или статьёй.

## 4. Простота как формальный критерий

При прочих равных выбирается вариант с меньшей суммарной сложностью:

```text
C_total = C_compute + C_state + C_dependencies + C_operations + C_review + C_change
```

Это не денежная формула, а decision model. Конкретные веса вводятся только если есть измеримые основания.

Правило:

```text
если Quality(A) >= required_gate
и Risk(A) <= allowed_risk
и Cost(A) <= constraints,
то более сложный B не принимается без отдельного доказанного преимущества.
```

## 5. Лестница усложнения

FATHER должен двигаться снизу вверх:

```text
L0 deterministic rule
→ L1 deterministic algorithm / calculator
→ L2 statistical/heuristic method
→ L3 single-model assisted
→ L4 champion + verifier
→ L5 Model Zoo / multi-agent
```

Переход на следующий уровень допускается только если нижний уровень не закрывает измеримое требование.

Пример:

- exact ID lookup → не нужен LLM;
- формула PERT → не нужен Zoo;
- проверка SHA-256 → только deterministic;
- классификация неоднозначного требования → возможно single LLM + reviewer;
- материальный архитектурный trade-off с конфликтующими evidence → Zoo может быть оправдан.

## 6. Где нужны математические методы

По типам задач:

| Задача | Предпочтительный метод |
|---|---|
| идентичность/целостность | hash / exact equality / deterministic checks |
| зависимости | DAG / graph traversal / topological order |
| применимость правил | decision tables / predicate logic |
| требования и traceability | graph relations + consistency constraints |
| оценка сроков | Bottom-Up / PERT / ranges |
| риск | likelihood × impact only when scales defined; otherwise ordinal matrix |
| sizing | queueing/load/capacity formulas + measured coefficients |
| выбор варианта | explicit multi-criteria trade-off, sensitivity analysis |
| поиск | lexical/vector/hybrid only after benchmark |
| AI quality | golden set + statistical metrics + error analysis |
| изменение baseline | dependency impact graph |

## 7. Алгоритм не должен маскировать неопределённость

Допустимые результаты:

- `PASS`;
- `PASS_WITH_CONDITIONS`;
- `INSUFFICIENT_EVIDENCE`;
- `CONFLICTED`;
- `UNKNOWN`;
- `NOT_APPLICABLE`;
- `REWORK`;
- `REJECT`.

`UNKNOWN` — валидный научный результат. Принудительное заполнение пустоты догадкой запрещено.

## 8. Критерий готовности алгоритма

Алгоритм готов к включению в бумажный конвейер только если:

- problem/inputs/outputs определены;
- owner и final authority определены;
- assumptions и invariants явны;
- простейший baseline рассмотрен;
- минимум одна реалистичная альтернатива рассмотрена для материального решения;
- критерии выбора заданы до результата;
- correctness/adequacy аргументирован;
- failure modes и rework path определены;
- test/experiment plan существует;
- source/evidence references присутствуют;
- неавтоматизируемые полномочия явно отделены;
- complexity оправдана.

## 9. Основания текущего стандарта

Нормативно-процессный слой FATHER опирается на реестры:

- `NORMATIVE_SOURCE_REGISTRY.yaml`;
- `SOURCE_ARTIFACT_MAPPING.yaml`;
- `FATHER_LIFECYCLE_STAGES.yaml`;
- `FATHER_ROLE_MATRIX.yaml`.

Профессиональные методы сейчас source-verified для:

- Richards/Ford: architecture characteristics, trade-offs, ADR, risk review, continuous architecture analysis;
- Simon Brown C4: Context / Container / Component views и выбор нужной глубины документации.

OTUS 1–31 используется как каталог методов и capability, но не как обязательный порядок жизненного цикла.

## 10. Научная дисциплина FATHER

Для каждого улучшения действует правило:

```text
observe
→ formulate hypothesis
→ define falsifiable criterion
→ compare against baseline
→ measure
→ review errors
→ accept / reject / refine
→ preserve evidence
```

Без критерия опровержения это не инженерная гипотеза, а предпочтение.
