# FATHER Knowledge Factory — Senior Engineering Standard

## Engineering level

Все изменения ядра выполняются как production-grade senior implementation: контракт, аналитика, дизайн, код, тесты, наблюдаемость, миграция и rollback рассматриваются до массового прогона данных.

## Mandatory workflow

`TASK -> REQUIREMENTS -> ANALYSIS -> CONTRACTS -> DESIGN -> IMPLEMENTATION -> UNIT TEST -> INTEGRATION TEST -> GOLDEN FIXTURE -> REGRESSION -> TELEMETRY -> REVIEW -> PROMOTION`.

Нельзя перескакивать напрямую от идеи к bulk processing.

## Coding rules

- Python 3.12 baseline; type hints for public functions.
- Standard library first for core storage path; optional heavy dependencies isolated behind adapters.
- SQLite connections enable `PRAGMA foreign_keys=ON`.
- Transactions around logical ingest/review units.
- No catch-all exception swallowing; failure reason is persisted or raised with context.
- No hard-coded model truth; model/endpoint/profile are runtime configuration.
- No rowid as public identity.
- No mutable source evidence after admission.
- All timestamps ISO-8601 UTC/offset-aware.
- JSON/JSONL output UTF-8 and deterministic field contracts.
- File system paths are runtime configuration; public metadata must not leak private absolute paths unless explicitly local-only.

## Idempotency

Repeated ingest of the same `source_sha256` must not create another canonical document unless edition/revision identity is explicitly different. Repeated fragment/translation imports use stable uniqueness keys. Resume after crash must be safe.

## Concurrency

Four logical streams do not mean four heavy GPU models. Storage writers serialize short SQLite transactions; expensive OCR/LLM work happens outside DB locks. Workers submit immutable results to the persistence layer.

## Security and integrity

- Parameterized SQL only.
- Validate enums and state transitions.
- Never execute code extracted from books.
- Treat PDF/OCR/LLM content as untrusted data.
- Reject unexpected path traversal in generated artifacts.
- SHA-256 verifies copied/extracted identity where applicable.

## Review boundaries

LLM output is candidate data. Deterministic QA and evidence presence are hard gates. GPT/Chief Analyst review is recorded with model/profile/input revision. Human authority may override a model verdict only through a new review record, never by editing history.

## Testing pyramid

MIN: schema compile, CRUD, FK/unique/state constraints.
MED: end-to-end fixture from EN source to reviewed node and role views.
MAX: real PDF/native text + OCR fallback + translation + contradiction + JSONL round-trip + recovery after interrupted run.

## Performance

Measure before optimization. Required telemetry: queue wait, extraction time, translation time, review time, DB write time, chunks/items processed, accepted/rework/error counts, model tokens/sec where available. Speed-up vs one stream is calculated only from measured comparable runs.

## Change control

Schema changes require numbered migration and compatibility note. Protected canonical trees are not moved during cleanup. A breaking contract change requires version bump and fixture update.

## Definition of senior-ready PR

A PR is senior-ready when it explains why, not only what; lists invariants and failure modes; has acceptance gates; contains executable verification; preserves provenance; and can be rolled back without corrupting admitted knowledge.