# Programming Problem Families

The catalog grows by families rather than random isolated exercises. Each family should contain small learning tasks, realistic component tasks and selected production scenarios.

| Family | Junior emphasis | Middle emphasis | Senior emphasis |
|---|---|---|---|
| Search & lookup | correct lookup | index/preparation trade-offs | data placement, cache/DB boundary |
| Sorting & ordering | use ordering correctly | stability/key/cost choices | whether global ordering is needed |
| Collections | list/map/set usage | representation choice | memory, ownership, scale and boundaries |
| Strings & parsing | safe parsing | parser/API strategy | hostile input, limits, protocol contracts |
| Files & streams | correct I/O | streaming/buffering | failure, backpressure, durability |
| Errors | handle expected errors | error taxonomy/API | failure contracts across services |
| State | explicit state | state machine/model | distributed state and recovery |
| APIs | call/implement endpoint | contracts/versioning | compatibility and system boundaries |
| Databases | CRUD safely | transactions/index use | consistency, migration, operational cost |
| Concurrency | safe basic tasks | choose concurrency model | boundedness, cancellation, contention |
| Networking | client/server basics | timeout/retry/protocol | partial failure and trust boundaries |
| Caching | use cache API | invalidation/TTL | consistency and failure economics |
| Queues | FIFO processing | worker/backpressure | delivery semantics and recovery |
| Security | validate input | threat-aware implementation | abuse cases and architectural controls |
| Testing | examples/boundaries | property/integration | verification strategy and confidence |
| Performance | avoid obvious waste | profile and benchmark | capacity model and complexity budget |
| Refactoring | improve names/functions | remove coupling | simplify architecture without regression |
| Patterns | recognize common form | justify pattern | reject pattern when simpler design wins |
| Observability | useful logs | metrics/traces | diagnostic architecture and SLO support |
| Build & dependencies | build reliably | dependency hygiene | supply chain and reproducibility |

## Exercise ladder inside a family

A family should normally progress through:

1. **Mechanic** — learn the language/tool operation.
2. **Reasoning** — identify the invariant or representation.
3. **Choice** — compare implementation strategies.
4. **Elegant** — expose a smaller core idea.
5. **Production** — add contracts, errors, tests and security.
6. **Failure** — handle malformed input, resource pressure or dependency failure.
7. **System** — decide whether the component belongs here at all.

Not every exercise needs all seven stages. The mature learning object should make clear which stage it trains.

## Analyst boundary

When an exercise requires nontrivial algorithm comparison, literature review or disputed performance claims, the Programming Agent should reference an Analyst/Research decision brief instead of manufacturing an algorithmic justification.

## Target catalog shape

The long-term catalog should contain fewer duplicated toy exercises and more reusable problem families. A single strong family can generate views for Python, Go and C++, three competency levels, Elegant/Production comparison and multiple evidence depths.
