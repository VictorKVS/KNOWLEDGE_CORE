# FATHER Knowledge Factory M1 — Техническое задание

Status: IMPLEMENTATION BASELINE
Owner: FATHER Agent Factory

## 1. Цель

Создать единый доказательный машиночитаемый слой знаний FATHER, который принимает книги, стандарты, нормативные документы и иные профессиональные источники, сохраняет оригинал и перевод раздельно, извлекает атомарные знания, связывает их в граф, хранит вектор оценок качества и предоставляет роль-специфические представления без копирования истины.

Целевые роли M1: Архитектор, Программист, ИБ, Юрист, Руководитель, Product.

## 2. Канонический алгоритм

`SOURCE -> IDENTITY -> SHA256 -> EXTRACT/OCR -> STRUCTURE -> TRANSLATE -> TRANSLATION_QA -> FRAGMENT -> KNOWLEDGE_CANDIDATE -> EVIDENCE -> NODE -> EDGE -> SCORE_VECTOR -> REVIEW -> ROLE_VIEW -> KB_READY`

Ни один следующий слой не имеет права затирать предыдущий.

## 3. Обязательные сущности

- SOURCE_DOCUMENT — файл/издание/редакция/источник;
- SOURCE_FRAGMENT — страница/раздел/блок/bbox/оригинальный текст;
- TRANSLATION_FRAGMENT — перевод конкретного фрагмента;
- KNOWLEDGE_NODE — один канонический смысловой объект;
- KNOWLEDGE_EDGE — связь двух узлов;
- EVIDENCE_LINK — доказательная связь узла/ребра с фрагментом;
- SCORE_VECTOR — независимые компоненты качества;
- REVIEW — проверка моделью/экспертом/главным аналитиком;
- ROLE_VIEW — профиль применимости одного узла для конкретной роли;
- PROCESSING_RUN — воспроизводимость прогона.

## 4. Типы знаний

`CONCEPT, DEFINITION, CLAIM, PRINCIPLE, PATTERN, ANTI_PATTERN, DECISION_RULE, TRADE_OFF, CHECKLIST, METRIC, FAILURE_MODE, TEST, EXAMPLE, REQUIREMENT`.

## 5. Типы связей

`DEFINES, SUPPORTS, CONTRADICTS, REFINES, DEPENDS_ON, PART_OF, APPLIES_TO, CAUSES, MITIGATES, IMPLEMENTS, DERIVED_FROM, EVIDENCE_FOR, SAME_AS`.

Каждое ребро имеет собственный provenance; вывод модели без доказательства не становится фактом.

## 6. Доказательность

Для любого KB_READY-узла должна восстанавливаться цепочка:

`node_id -> evidence_link -> fragment_id -> document_id -> edition/revision -> source_sha256 -> locator -> original_text`.

Для переведённых источников дополнительно:

`node -> source fragment EN -> translation fragment RU -> translator model -> reviewer -> glossary revision`.

## 7. Веса

Запрещён один непрозрачный `weight`. Хранятся отдельные компоненты: source_authority, extraction_confidence, ocr_confidence, translation_confidence, ambiguity, cross_source_support, recency/currentness, applicability, implementation_evidence, model_agreement, reviewer_confidence.

Ролевой вес вычисляется поверх компонентов и не меняет источник истины.

## 8. Review lifecycle

Допустимые решения: `APPROVE`, `REVISE`, `REJECT`, `ESCALATE`.

Для D2/D3 решений обязательны evidence package и независимый review. Для правовых и нормативных объектов точный source anchor и currentness проверяются отдельно от applicability.

## 9. 4 потока реализации

S1 — SQLite/schema/IDs/integrity/migrations.
S2 — ingest/OCR/translation/evidence/provenance.
S3 — graph/relations/contradictions/weights/role views.
S4 — review/QA/GPT/Chief Analyst/export/KB_READY gates.

Потоки интегрируются через стабильные контракты, а не через общие временные файлы.

## 10. Локальный runtime

M1 storage: SQLite + JSONL exports + optional embeddings.

Default local root: `G:\1\FATHER_KNOWLEDGE`.

Recommended layout:

- `original/`
- `extracted/`
- `translated/`
- `evidence/`
- `db/father_knowledge.db`
- `exports/jsonl/`
- `vectors/`
- `reports/`
- `runs/`

Полные книги/переводы остаются локально и не публикуются в public GitHub.

## 11. Acceptance gates

MIN: создать пустую БД, вставить один документ и восстановить provenance.
MED: пройти fixture `EN text -> translation -> node -> evidence -> review -> role view`.
MAX: пройти реальный PDF/книгу, построить связи и противоречия, экспортировать JSONL и восстановить граф без потери ID.

KB_READY запрещён при orphan evidence, пустом claim, unresolved source, failed translation QA или REJECT review.

## 12. Метрики производства

Сохранять: processed, accepted, rejected, rework, elapsed, throughput, model/runtime, error_reason. Сравнение с 1 потоком и ETA публиковать только после появления реальной baseline telemetry; значения не выдумывать.
