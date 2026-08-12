# Learning Objects

Learning objects are the site-ready, agent-readable presentation layer over the underlying engineering knowledge.

Each object may combine:

- a formal problem record;
- Junior / Middle / Senior views;
- Elegant / Olympiad and Production views;
- Python / Go / C++ implementations;
- tests and benchmarks;
- source and claim references;
- security considerations;
- reusable lessons for decision-memory.

The object must not duplicate authoritative evidence unnecessarily. It should reference stable IDs and implementation paths, while presenting the material in a coherent form for learning and fast agent retrieval.

## First reference object

- `LEARN-SEARCH-001` — repeated membership lookup and the trade-off between direct scan, ordered search and hash indexing.

## Design rule

The learning layer is a projection, not a second source of truth.

Underlying evidence remains in `SRC-*`, `CLM-*`, `BENCH-*`, `DM-*`, `ALG-*`, `DS-*` and implementation/test records. Learning objects assemble those pieces into a useful teaching and decision interface.
