# FATHER Knowledge Factory M1 — Аналитика и принятые решения

## Проблема

Библиотека содержит разнородные PDF/EPUB/DOCX/TXT, русские и английские источники, нормативные документы и книги. Обычный RAG по чанкам создаёт слабую трассируемость, дублирование смысла, смешивает перевод с оригиналом и плохо поддерживает противоречия, версии и разные профессиональные роли.

## Ключевое решение

Использовать evidence-first Knowledge Factory, где RAG является интерфейсом поиска, а не каноническим хранилищем истины.

Каноническая единица истины: `KNOWLEDGE_NODE` с доказательными ссылками на неизменяемые `SOURCE_FRAGMENT`.

## Почему SQLite M1

SQLite выбран как локальный canonical store для M1: транзакции, FK, индексы, воспроизводимость, переносимость и отсутствие инфраструктурной нагрузки. Логический граф хранится в `knowledge_nodes` + `knowledge_edges`; Neo4j не требуется до появления измеримой потребности. Переход PostgreSQL/pgvector возможен без смены логических ID и контрактов.

## Почему перевод отдельным слоем

Перевод не является источником. Он сохраняется отдельно с model/prompt/glossary/reviewer provenance. При споре аналитик всегда возвращается к оригиналу.

## Почему не один confidence

Один вес скрывает причины доверия. Вектор позволяет отдельно видеть авторитет источника, качество OCR/перевода, актуальность, подтверждение другими источниками, применимость и review. Роль может менять коэффициенты, но не факты.

## Почему один граф для всех ролей

Архитектор, Программист, ИБ, Юрист, Руководитель и Product используют одни знания с разными задачами. Копирование узла по ролям создаёт дрейф. Поэтому canonical node один, а `ROLE_VIEW` хранит relevance/weight profile/decision context.

## Риск: LLM consensus

Согласие моделей не считается доказательством. Модель может создавать candidate node/edge/review, но KB_READY требует evidence gate. Для противоречий сохраняются обе позиции и отдельная relation `CONTRADICTS` до экспертного разрешения.

## Риск: OCR

OCR применяется только при отсутствии/низком качестве native text. Для каждой страницы сохраняется extraction method и confidence; низкое качество блокирует автоматическое повышение знания.

## Риск: copyright/public repo

Полные книги, OCR и переводы остаются локально. В public repo допускаются код, схемы, фикстуры, glossary и безопасные metadata/контракты.

## Senior implementation principles

1. Contracts before workers.
2. Immutable evidence before inference.
3. Stable IDs before graph enrichment.
4. Idempotent ingest before parallelism.
5. Deterministic validators before LLM scoring.
6. Appendable review history; no silent overwrites.
7. Explicit migrations; no ad-hoc schema edits.
8. Golden-path fixture before bulk library processing.
9. Failure is data: every block reason is machine-readable.
10. Optimize only after telemetry.

## Definition of Done M1

M1 готов, когда короткий английский fixture и один реальный технический документ проходят полный путь до SQLite, создают узел/ребро/evidence/review/role views, проходят `foreign_key_check`, экспортируются в JSONL и воспроизводятся с теми же logical IDs.