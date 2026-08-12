# Test Evidence Registry

`TEST-*` records turn executable tests into traceable evidence objects.

A source file containing tests is not automatically evidence for every claim. A `TEST-*` record states exactly what the suite verifies, what it does **not** prove, where each language implementation lives, which CI workflow executes it, and which claims/decisions may rely on it.

## Traceability

```text
code/tests
   ↓ registered as
TEST-*
   ↓ supports
CLM-* / ADR-*
   ↓ contributes to
DM-* / Learning Object / Explain Decision
```

The knowledge quality gate indexes `TEST-*` alongside `SRC-*`, `CLM-*`, `BENCH-*`, `EXP-*`, `ADR-*` and `DM-*`. Mature records fail validation when they point to a resolvable evidence ID that does not exist.

## Evidence limits

Passing tests demonstrate the behavior covered by the registered cases in the tested environment. They do not establish universal correctness, performance, security, distributed-system guarantees, or properties explicitly listed under `contract.does_not_prove`.

## Current registered suites

- `TEST-QUEUE-001` — bounded queue and explicit capacity pressure.
- `TEST-TRANSACTION-001` — in-memory all-or-nothing teaching model.
- `TEST-DBTX-001` — database transaction boundary teaching object.
- `TEST-MSG-001` — duplicate message suppression by stable message identity.
